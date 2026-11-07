"""Full-bank, resumable second-score and activity training.

The final shared first must be completed before either stage starts. Existing
selected weights are read only. Every trained checkpoint binds that final first
and the same full-geometry prior. See docs/THEORY.md and docs/TRAINING.md for the objectives.
"""
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
import json
import math
import os
import time

from workspace import ROOT

import numpy as np
from scipy.special import logit
import torch
from torch.nn import functional as functional

from networks.score import load_direct_checkpoint
from receiver.stmp.activity import Config
from receiver.stmp.activity import EvidenceNetwork
from receiver.stmp.activity import SCHEMA
from receiver.stmp.activity import FEATURE_DEFINITION_FROZEN
from training.organized.scores.direct_objectives import direct_second_loss
from training.organized.scores.checkpoints import save_direct_checkpoint
from training.organized.scores.device import capture_device_rng
from training.organized.scores.device import restore_device_rng
from fileio import sha256


from training.organized.stmp.common import source_hashes


def resolve(path):
    return Path(path) if Path(path).is_absolute() else ROOT / path


def relative(path):
    path = Path(path).resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def atomic_torch(path, value):
    path = Path(path)
    temporary = path.with_suffix(".tmp")
    torch.save(value, temporary)
    temporary.replace(path)


def cpu_state(model):
    return {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}


def draw_queries(channels, rng, scale, noise_support, *, paired=False):
    """Online queries from physical H; both classes use the identical v law.

    Paired means one active and one zero query at each independently drawn v.
    Their noise draws are independent. Packing retains complex norm exactly in
    real arithmetic; each real noise coordinate has variance v/2.
    """
    channels = np.asarray(channels)
    if channels.ndim != 4 or not np.isfinite(channels).all() or not np.isfinite(scale) or scale <= 0:
        raise ValueError("Finite full physical channel samples and positive scale required")
    clean = np.stack((channels.real, channels.imag), axis=1).astype(np.float32)/scale
    lower, upper = noise_support
    variance = np.exp(rng.uniform(np.log(lower), np.log(upper), len(clean))).astype(np.float32)
    factor = np.sqrt(variance[:, None, None, None, None]/2)
    positive = clean + factor*rng.standard_normal(clean.shape).astype(np.float32)
    if not paired:
        return dict(clean=clean, observation=positive, variance=variance)
    negative = factor*rng.standard_normal(clean.shape).astype(np.float32)
    return dict(clean=clean, positive=positive, negative=negative, variance=variance)


def complete_mean(first, observation, variance, device):
    """Match inference float32 score and float64 Tweedie readout, then cast features.

    No input clipping, power rescaling, projection, or extra score query.
    """
    with torch.inference_mode():
        r = torch.as_tensor(observation, dtype=torch.float32, device=device)
        v = torch.as_tensor(variance, dtype=torch.float32, device=device)
        score = first(r, v).cpu().numpy()
    mean = observation.astype(np.float64)+.5*variance.astype(np.float64)[:, None, None, None, None]*score.astype(np.float64)
    return mean.astype(np.float32), score


def activity_metrics(logits, variances):
    positive, negative = np.asarray(logits, float)
    n = len(variances)
    bce = float((np.logaddexp(0, -positive).sum()+np.logaddexp(0, negative).sum())/(2*n))
    deployments = {}
    for rho in (.01, .05, .1, .2, .3):
        threshold = -logit(rho)
        errors = rho*np.count_nonzero(positive < threshold)+(1-rho)*np.count_nonzero(negative >= threshold)
        deployments[str(rho)] = dict(aer=float(errors/n), activity_prior=rho)
    bands = {}
    groups = np.floor(-10*np.log10(variances)/5).astype(int)*5
    for group in np.unique(groups):
        mask = groups == group
        count = int(mask.sum())
        loss = (np.logaddexp(0, -positive[mask]).sum()+np.logaddexp(0, negative[mask]).sum())/(2*count)
        rho = .1
        error = rho*np.count_nonzero(positive[mask] < -logit(rho))+(1-rho)*np.count_nonzero(negative[mask] >= -logit(rho))
        bands[f"snr_{group}_to_{group+5}_db"] = dict(pairs=count, bce=float(loss), aer_at_rho_0_1=float(error/count))
    return dict(loss=bce, bce=bce, pairs=n, examples=2*n, deployments=deployments, bands=bands,
                logit_minimum=float(np.min(logits)), logit_maximum=float(np.max(logits)))


class Trainer:
    def __init__(self, config, prior, stage, *, device):
        self.config, self.prior, self.stage, self.device = config, prior, stage, device
        self.settings = config[stage]
        self.output = resolve(config["output"]) / stage
        self.output.mkdir(parents=True, exist_ok=True)
        self.stop = False
        self.first_path = resolve(config["first_checkpoint"])
        self.first_hash = sha256(self.first_path)
        self.prior_hash = sha256(resolve(config["prior_definition"]))
        self.first, first_blob = load_direct_checkpoint(self.first_path, device)
        self.first.eval().requires_grad_(False)
        if first_blob["order"] != 1 or first_blob["global_complex_rms"] != prior["global_complex_rms"]:
            raise ValueError("Final first and new prior coordinates differ")
        if tuple(prior["noise_support"]) != (.001, 100.) or prior["shape"] != [16, 16, 16]:
            raise ValueError("Selected complete-score architecture/support required")
        with np.load(resolve(config["moments_file"]), allow_pickle=False) as archive:
            self.prior_mean = archive["prior_mean"].copy()
            self.prior_second_moment = float(archive["prior_second_moment"])
        self.data = {}
        for split in ("train", "validation"):
            path = resolve(config["data_files"][split])
            if sha256(path) != prior["sample_files_sha256"][split]:
                raise ValueError("Prior bank changed: " + split)
            bank = np.load(path, mmap_mode="r", allow_pickle=False)
            expected = (prior[split+"_samples"], *prior["shape"])
            if bank.shape != expected or bank.dtype != np.complex64:
                raise ValueError("Complete physical prior bank shape/dtype differs")
            self.data[split] = bank
        if sha256(resolve(config["moments_file"])) != prior["moments_sha256"]:
            raise ValueError("Prior moment artifact changed")
        self.second_path = resolve(config["second_checkpoint"])
        self.second_hash = sha256(self.second_path) if stage == "activity" else None
        self.specification = dict(schema="full-geometry-route12-training-specification-v1", stage=stage,
            configuration=config, first_sha256=self.first_hash, second_sha256=self.second_hash,
            prior_definition_sha256=self.prior_hash, device=device,
            source_sha256=source_hashes())
        specification_path = self.output/"specification.json"
        if specification_path.exists():
            if json.loads(specification_path.read_text()) != self.specification:
                raise ValueError("Existing training specification differs; previous artifacts preserved")
        else:
            atomic_json(specification_path, self.specification)
        self.specification_hash = sha256(specification_path)

    def request_stop(self, *_):
        self.stop = True

    def status(self, status, **values):
        row = dict(status=status, pid=os.getpid(), stage=self.stage, updated_unix=time.time(), **values)
        atomic_json(self.output/"status.json", row)
        print(json.dumps(row, ensure_ascii=False), flush=True)

    def selected_path(self):
        return self.output/("second_best.pt" if self.stage == "second" else "evidence_best.pt")

    def model(self):
        initial = resolve(self.settings["initial_checkpoint"])
        if sha256(initial) != self.settings["initial_checkpoint_sha256"]:
            raise ValueError("Warm-start checkpoint changed")
        if self.stage == "second":
            model, blob = load_direct_checkpoint(initial, self.device)
            if blob["order"] != 2 or model.config != self.first.config:
                raise ValueError("Warm-start second architecture differs from final first")
        else:
            blob = torch.load(initial, map_location="cpu", weights_only=False)
            if blob["schema"] != SCHEMA or not blob["config"]["use_score_mean"]:
                raise ValueError("Complete-observation and score-mean activity warm start required")
            model = EvidenceNetwork(Config(**blob["config"]))
            model.load_state_dict(blob["state_dict"])
            model = model.to(self.device)
        return model

    def validation_cache(self):
        rng = np.random.default_rng(self.settings["validation_seed"])
        cache = draw_queries(self.data["validation"], rng, self.prior["global_complex_rms"],
                             self.prior["noise_support"], paired=self.stage == "activity")
        observations = (cache["observation"],) if self.stage == "second" else (cache["positive"], cache["negative"])
        means, scores = [], []
        for class_index, observation in enumerate(observations):
            mean_parts, score_parts = [], []
            for start in range(0, len(observation), self.settings["microbatch_size"]):
                stop = start+self.settings["microbatch_size"]
                mean, score = complete_mean(self.first, observation[start:stop], cache["variance"][start:stop], self.device)
                mean_parts.append(mean)
                if self.stage == "second":
                    score_parts.append(score)
                if start % 320 == 0:
                    self.status("PREPARING_FIXED_VALIDATION", class_index=class_index,
                                samples=min(stop, len(observation)), validation_samples=len(observation))
            means.append(np.concatenate(mean_parts))
            if score_parts:
                scores.append(np.concatenate(score_parts))
        cache["means"] = means
        if scores:
            cache["scores"] = scores[0]
        return cache

    def validation(self, model, cache):
        model.eval()
        losses, logits, raw_traces, risks = [], [], [], []
        total = 0.
        size = len(cache["variance"])
        with torch.inference_mode():
            for start in range(0, size, self.settings["microbatch_size"]):
                stop = min(start+self.settings["microbatch_size"], size)
                v = cache["variance"][start:stop]
                if self.stage == "second":
                    r = torch.as_tensor(cache["observation"][start:stop], device=self.device)
                    h = torch.as_tensor(cache["clean"][start:stop], device=self.device)
                    vv = torch.as_tensor(v, device=self.device)
                    s1 = torch.as_tensor(cache["scores"][start:stop], device=self.device)
                    s2 = model(r, vv)
                    loss = direct_second_loss(s2, s1, r, h, vv[:, None, None, None])
                    total += float(loss.cpu())*(stop-start)
                    s2_array = s2.cpu().numpy().astype(float)
                    raw = v.astype(float)*(1+.5*v.astype(float)*s2_array.mean(axis=(1, 2, 3, 4)))
                    estimate = cache["means"][0][start:stop].astype(float)
                    clean = cache["clean"][start:stop].astype(float)
                    error = (estimate-clean).reshape(stop-start, -1)
                    risk = np.sum(error**2, axis=1)/np.prod(self.prior["shape"])
                    raw_traces.append(raw); risks.append(risk)
                else:
                    r = np.concatenate((cache["positive"][start:stop], cache["negative"][start:stop]))
                    f = np.concatenate((cache["means"][0][start:stop], cache["means"][1][start:stop]))
                    x = torch.as_tensor(r, device=self.device)
                    vv = torch.as_tensor(np.tile(v, 2), device=self.device)
                    ff = torch.as_tensor(f, device=self.device)
                    b = model(x, vv, ff).cpu().numpy().astype(float)
                    logits.append(np.stack((b[:stop-start], b[stop-start:])))
        if self.stage == "activity":
            all_logits = np.concatenate(logits, axis=1)
            if not np.isfinite(all_logits).all():
                raise FloatingPointError("Nonfinite activity validation logits")
            return activity_metrics(all_logits, cache["variance"])
        raw, risk = np.concatenate(raw_traces), np.concatenate(risks)
        if not all(np.isfinite(value).all() for value in (raw, risk)):
            raise FloatingPointError("Nonfinite second validation readout")
        bands = {}
        groups = np.floor(-10*np.log10(cache["variance"])/5).astype(int)*5
        for group in np.unique(groups):
            mask = groups == group
            reported = float(raw[mask].sum())
            bands[f"snr_{group}_to_{group+5}_db"] = dict(samples=int(mask.sum()),
                mean_risk=float(risk[mask].mean()), mean_raw_readout=float(raw[mask].mean()),
                error_to_reported=float(risk[mask].sum()/reported) if reported > 0 else None,
                raw_nonpositive_traces=int(np.count_nonzero(raw[mask] <= 0)))
        return dict(loss=total/size, samples=size, mean_risk=float(risk.mean()),
                    mean_raw_readout=float(raw.mean()), raw_nonpositive_traces=int(np.count_nonzero(raw <= 0)),
                    raw_minimum=float(raw.min()), raw_maximum=float(raw.max()), bands=bands)

    def save_selected(self, model, epoch, steps, measured, *, destination=None):
        path = self.selected_path() if destination is None else destination
        metadata = dict(epoch=epoch, optimizer_steps=steps, validation=measured,
            first_sha256=self.first_hash, prior_definition_sha256=self.prior_hash,
            initialization_sha256=self.settings["initial_checkpoint_sha256"],
            specification_sha256=self.specification_hash, objective=self.settings["objective"],
            target="Complete frozen first conditional squared risk; no rank-one projection" if self.stage == "second" else "Same-prior active versus zero density ratio",
            completion_evidence="External complete.json required", receiver_performance_verified=False)
        if self.stage == "second":
            save_direct_checkpoint(path, model, scale=self.prior["global_complex_rms"], metadata=metadata)
        else:
            atomic_torch(path, dict(schema=SCHEMA, config=asdict(model.config), state_dict=cpu_state(model),
                scale=self.prior["global_complex_rms"], prior_definition=self.prior,
                prior_mean=self.prior_mean, prior_second_moment=self.prior_second_moment,
                training_class_prior=.5, noise_support=self.prior["noise_support"],
                first_sha256=self.first_hash, second_sha256=self.second_hash,
                feature_definition=FEATURE_DEFINITION_FROZEN, metadata=metadata,
                selected_epoch=epoch, optimizer_steps=steps, validation=measured,
                objective=self.settings["objective"], risk_output_unused=True,
                receiver_performance_verified=False))

    def train(self):
        completed = self.output/"complete.json"
        if completed.exists():
            record = json.loads(completed.read_text())
            if record["specification_sha256"] != self.specification_hash or record["weight_sha256"] != sha256(self.selected_path()):
                raise ValueError("Completed training identity changed")
            self.status("ALREADY_COMPLETED", **{key:record[key] for key in ("epochs", "selected_epoch", "optimizer_steps", "stopping_reason")})
            return record
        torch.manual_seed(self.settings["seed"])
        if self.device == "mps":
            torch.mps.manual_seed(self.settings["seed"])
        rng = np.random.default_rng(self.settings["seed"])
        model = self.model()
        ema = deepcopy(model).eval().requires_grad_(False)
        optimizer = torch.optim.Adam(model.parameters(), lr=self.settings["learning_rate"])
        epoch, cursor, indices, steps = 1, 0, None, 0
        best, meaningful_best, last_improvement = math.inf, math.inf, 0
        selected_epoch, history, loss_sum, seen = 0, [], 0., 0
        last = self.output/"last.pt"
        if last.exists():
            state = torch.load(last, map_location="cpu", weights_only=False)
            if state["specification_sha256"] != self.specification_hash:
                raise ValueError("Resume training specification changed")
            model.load_state_dict(state["model"]); ema.load_state_dict(state["ema"])
            optimizer.load_state_dict(state["optimizer"])
            for row in optimizer.state.values():
                for key, value in row.items():
                    if torch.is_tensor(value) and key != "step":
                        row[key] = value.to(self.device)
            rng.bit_generator.state = state["rng"]
            torch.set_rng_state(state["torch_rng"])
            restore_device_rng(self.device, state)
            epoch, cursor, indices, steps = state["epoch"], state["cursor"], state["indices"], state["steps"]
            best, meaningful_best, last_improvement = state["best"], state["meaningful_best"], state["last_improvement"]
            selected_epoch, history, loss_sum, seen = state["selected_epoch"], state["history"], state["loss_sum"], state["seen"]
        self.status("PREPARING_VALIDATION", parameters=sum(p.numel() for p in model.parameters()),
                    first_sha256=self.first_hash, resume=last.exists())
        cache = self.validation_cache()
        last_saved = time.time()

        def save_resume():
            nonlocal last_saved
            atomic_torch(last, dict(schema="full-geometry-route12-resume-v1",
                specification_sha256=self.specification_hash, stage=self.stage,
                model=cpu_state(model), ema=cpu_state(ema), optimizer=optimizer.state_dict(),
                rng=rng.bit_generator.state, torch_rng=torch.get_rng_state(),
                **capture_device_rng(self.device),
                epoch=epoch, cursor=cursor, indices=indices, steps=steps, best=best,
                meaningful_best=meaningful_best, last_improvement=last_improvement,
                selected_epoch=selected_epoch, history=history, loss_sum=loss_sum, seen=seen))
            last_saved = time.time()

        if not last.exists():
            baseline = self.validation(ema, cache)
            best = meaningful_best = baseline["loss"]
            history.append(dict(epoch=0, optimizer_steps=0, validation=baseline))
            atomic_json(self.output/"baseline.json", baseline)
            self.save_selected(ema, 0, 0, baseline)
            save_resume()
        execution = self.config.get("cuda_execution", {}).get(self.stage, {})
        graph = None
        if execution.get("cuda_graph"):
            if torch.device(self.device).type != "cuda":
                raise ValueError("Auxiliary CUDA graph requires a CUDA device")
            from training.organized.scores.cuda_graph_auxiliary import AuxiliaryGraph
            from training.organized.scores.cuda_graph_auxiliary import query_parts
            graph = AuxiliaryGraph(model, self.first, self.stage, self.settings["batch_size"])
        stopping_reason = "MAXIMUM_TRAINING_BUDGET"
        started = time.time()
        while epoch <= self.settings["maximum_epochs"]:
            epoch_started = time.time()
            rate = self.settings["minimum_learning_rate"]+.5*(self.settings["learning_rate"]-self.settings["minimum_learning_rate"])*(1+math.cos(math.pi*(epoch-1)/max(self.settings["maximum_epochs"]-1, 1)))
            for group in optimizer.param_groups:
                group["lr"] = rate
            model.train()
            if indices is None:
                indices = rng.permutation(len(self.data["train"]))
            while cursor < len(indices):
                if self.stop or (self.output/"pause.request").exists():
                    save_resume()
                    self.status("PAUSED", epoch=epoch, samples=cursor, optimizer_steps=steps, resumable=True)
                    return None
                chosen = indices[cursor:cursor+self.settings["batch_size"]]
                optimizer.zero_grad(set_to_none=True)
                if graph is not None:
                    parts = query_parts(self.data["train"], chosen, rng, self.prior, self.settings, self.stage)
                    for value, count in graph.backward(parts):
                        loss_sum += value*count
                        seen += count
                for offset in (() if graph is not None else range(0, len(chosen), self.settings["microbatch_size"])):
                    micro = chosen[offset:offset+self.settings["microbatch_size"]]
                    batch = draw_queries(self.data["train"][micro], rng, self.prior["global_complex_rms"],
                                         self.prior["noise_support"], paired=self.stage == "activity")
                    if self.stage == "second":
                        r = torch.as_tensor(batch["observation"], device=self.device)
                        h = torch.as_tensor(batch["clean"], device=self.device)
                        vv = torch.as_tensor(batch["variance"], device=self.device)
                        with torch.no_grad():
                            s1 = self.first(r, vv)
                        loss = direct_second_loss(model(r, vv), s1, r, h, vv[:, None, None, None])
                    else:
                        observation = np.concatenate((batch["positive"], batch["negative"]))
                        variance = np.tile(batch["variance"], 2)
                        mean, _ = complete_mean(self.first, observation, variance, self.device)
                        r = torch.as_tensor(observation, device=self.device)
                        vv = torch.as_tensor(variance, device=self.device)
                        ff = torch.as_tensor(mean, device=self.device)
                        labels = torch.cat((torch.ones(len(micro), device=self.device), torch.zeros(len(micro), device=self.device)))
                        loss = functional.binary_cross_entropy_with_logits(model(r, vv, ff), labels)
                    value = float(loss.detach().cpu())
                    if not np.isfinite(value):
                        raise FloatingPointError("Nonfinite training objective; saved state preserved")
                    (loss*len(micro)/len(chosen)).backward()
                    loss_sum += value*len(micro); seen += len(micro)
                if any(p.grad is not None for p in self.first.parameters()):
                    raise AssertionError("Auxiliary training updated the frozen first")
                gradient = torch.nn.utils.clip_grad_norm_(model.parameters(), self.settings["gradient_clip"], error_if_nonfinite=True)
                optimizer.step(); cursor += len(chosen); steps += 1
                with torch.no_grad():
                    if execution.get("foreach_ema"):
                        torch._foreach_lerp_(list(ema.parameters()), list(model.parameters()), 1-self.settings["ema_decay"])
                    else:
                        for target, source in zip(ema.parameters(), model.parameters()):
                            target.lerp_(source, 1-self.settings["ema_decay"])
                if time.time()-last_saved >= self.settings["checkpoint_seconds"]:
                    save_resume()
                if steps % 10 == 0:
                    self.status("TRAINING", epoch=epoch, samples=cursor, train_samples=len(indices),
                        optimizer_steps=steps, loss=loss_sum/seen, learning_rate=rate,
                        gradient_norm_before_clip=float(gradient.cpu()), elapsed_epoch_seconds=time.time()-epoch_started)
            if sha256(self.first_path) != self.first_hash:
                raise ValueError("Final frozen first changed during training")
            measured = self.validation(ema, cache)
            row = dict(epoch=epoch, optimizer_steps=steps, train_loss=loss_sum/seen,
                       learning_rate=rate, validation=measured, elapsed_epoch_seconds=time.time()-epoch_started)
            history.append(row)
            atomic_json(self.output/"history.json", history)
            if measured["loss"] < best:
                best, selected_epoch = measured["loss"], epoch
                self.save_selected(ema, epoch, steps, measured)
            if measured["loss"] < meaningful_best*(1-self.settings["meaningful_relative_improvement"]):
                meaningful_best, last_improvement = measured["loss"], epoch
            plateau = epoch >= self.settings["minimum_epochs"] and epoch-last_improvement >= self.settings["validation_patience"]
            self.status("EPOCH_COMPLETE", epoch=epoch, optimizer_steps=steps,
                        validation=measured, selected_epoch=selected_epoch,
                        epochs_since_meaningful_improvement=epoch-last_improvement,
                        elapsed_invocation_seconds=time.time()-started)
            if plateau:
                stopping_reason = "VALIDATION_PLATEAU"
            epoch += 1; cursor = 0; indices = None; loss_sum = 0.; seen = 0
            save_resume()
            if plateau:
                break
        last_measured = history[-1]["validation"]
        final_name = "second_final.pt" if self.stage == "second" else "evidence_final.pt"
        self.save_selected(ema, epoch-1, steps, last_measured, destination=self.output/final_name)
        selected = torch.load(self.selected_path(), map_location="cpu", weights_only=False)
        selected_validation = selected["metadata"]["validation"] if self.stage == "second" else selected["validation"]
        record = dict(schema="full-geometry-route12-completed-training-v1", status="COMPLETED", stage=self.stage,
            stopping_reason=stopping_reason, epochs=epoch-1, optimizer_steps=steps, selected_epoch=selected_epoch,
            validation=selected_validation, validation_plateau=stopping_reason == "VALIDATION_PLATEAU",
            train_samples=len(self.data["train"]), validation_samples=len(self.data["validation"]),
            specification_sha256=self.specification_hash, prior_definition_sha256=self.prior_hash,
            weight_sha256=sha256(self.selected_path()), first_sha256=self.first_hash,
            initialization_sha256=self.settings["initial_checkpoint_sha256"],
            samples_processed=(epoch-1)*len(self.data["train"]), receiver_performance_verified=False)
        if self.stage == "activity":
            record["second_sha256"] = self.second_hash
        atomic_json(completed, record)
        self.status("COMPLETED", **{key:record[key] for key in ("epochs", "optimizer_steps", "selected_epoch", "stopping_reason")})
        return record


def first_record(config):
    record_path = resolve(config["first_training_record"])
    specification_path = resolve(config["first_training_specification"])
    record = json.loads(record_path.read_text())
    specification = json.loads(specification_path.read_text())
    if (record["status"] != "COMPLETED" or record["optimizer_steps"] < 1
            or record["weight_sha256"] != sha256(resolve(config["first_checkpoint"]))
            or record["specification_sha256"] != sha256(specification_path)
            or specification["prior_definition_sha256"] != sha256(resolve(config["prior_definition"]))):
        raise ValueError("Completed final first with the identical prior required")
    bank = specification["configuration"]["bank"]
    prior = json.loads(resolve(config["prior_definition"]).read_text())
    if (prior["schema"] != "physical-training-prior-v1" or bank["train_samples"] != prior["train_samples"]
            or bank["validation_samples"] != prior["validation_samples"]
            or record["epochs"] < specification["configuration"]["first"]["minimum_epochs"]):
        raise ValueError("Completed full-prior first training with declared minimum length required")
    return record

