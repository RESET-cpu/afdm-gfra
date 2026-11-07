#!/usr/bin/env python3
"""One GNN-ASPL for mixed SNR/grid conditions; project training adaptation.

--development runs 128 real training and 32 held-out cases, all 29 phases.
Full mode defaults to 10001 cases and preserves the same architecture/order.
The per-SNR recipe is available through train_gnn.py per-snr.
Resume at saved epoch boundaries with --resume OUTPUT/training_state.pt.
"""
from collections import OrderedDict
from dataclasses import asdict
from pathlib import Path
import argparse
import hashlib
import json
import resource
import shutil
import sys
import time


import numpy as np
import torch

from project import ROOT, source_files
from system.dictionary import AFDMGrid, physical_atoms
from . import common
from .common import physical_row_support
from algorithm.baseline.gnn import (
    CHECKPOINT_SCHEMA,
    METHOD,
    INTEGER_GRID,
    GNNASPLSettings,
    coefficient_nmse,
    make_gnn_aspl_network,
    project_channel_coefficients,
)
from utils import sha256, state_sha, write_json


TRAINING_MODE = "mixed_snr_grid"
STATE_SCHEMA = "ding-gnn-aspl-mixed-epoch-state-v1"
SAMPLER_VERSION = "seed6261008_snr_grid_k_q_p_v1"
SAMPLER_SALT = 6261008


def parser():
    p = argparse.ArgumentParser(prog="train_gnn.py mixed", description=__doc__)
    p.add_argument("--output", type=Path)
    p.add_argument("--resume", type=Path)
    modes = p.add_mutually_exclusive_group()
    modes.add_argument("--development", action="store_true")
    modes.add_argument(
        "--smoke", action="store_true", help="tiny test fixture, never a performance model"
    )
    p.add_argument("--train-samples", type=int)
    p.add_argument("--validation-samples", type=int)
    p.add_argument("--snr-range", type=float, nargs=2, default=[-10.0, 10.0])
    p.add_argument("--on-grid-probability", type=float, default=0.5)
    p.add_argument("--user-counts", type=int, nargs="+", default=[40])
    p.add_argument("--frame-counts", type=int, nargs="+", default=[16])
    p.add_argument("--activity-probabilities", type=float, nargs="+", default=[0.1])
    p.add_argument("--m-z", type=int, default=4)
    p.add_argument("--m-y", type=int, default=4)
    p.add_argument("--scale", type=float, default=0.2647966452702405)
    p.add_argument("--batch-size", type=int, default=128)
    p.add_argument("--microbatch-size", type=int, default=4)
    p.add_argument("--threads", type=int, default=2)
    p.add_argument("--tensor-cache-mib", type=int, default=2048)
    p.add_argument("--backend", choices=("cpu", "mps_real"), default="cpu")
    p.add_argument("--cache-mode", choices=("dense", "compact"), default="dense")
    p.add_argument("--adaptive-final-joint", action="store_true")
    p.add_argument("--max-final-joint-epochs", type=int, default=20)
    p.add_argument("--final-joint-add-epochs", type=int, default=5)
    p.add_argument("--final-joint-relative-improvement", type=float, default=0.01)
    p.add_argument("--gnn-epochs", type=int)
    p.add_argument("--damping-epochs", type=int)
    p.add_argument("--joint-epochs", type=int)
    p.add_argument("--learning-rate", type=float, default=5e-3)
    p.add_argument("--train-seed-base", type=int, default=171000000)
    p.add_argument("--validation-seed-base", type=int, default=181000000)
    p.add_argument("--model-seed", type=int, default=6100817)
    p.add_argument(
        "--stop-after-epoch",
        type=int,
        help="development interruption at absolute completed epoch count",
    )
    return p


def canonical_sha(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def condition_spec(a):
    return dict(
        sampler_version=SAMPLER_VERSION,
        sampler_salt=SAMPLER_SALT,
        snr_distribution="continuous uniform",
        snr_range=a.snr_range,
        on_grid_probability=a.on_grid_probability,
        user_counts=a.user_counts,
        frame_counts=a.frame_counts,
        activity_probabilities=a.activity_probabilities,
        m_z=a.m_z,
        m_y=a.m_y,
        scale=a.scale,
        require_active_user=True,
        dictionary=INTEGER_GRID,
    )


def descriptor(seed, a):
    rng = np.random.default_rng(np.random.SeedSequence([int(seed), SAMPLER_SALT]))
    return dict(
        seed=int(seed),
        snr_db=float(rng.uniform(*a.snr_range)),
        grid_mode="on_grid" if rng.random() < a.on_grid_probability else "off_grid",
        users=int(rng.choice(a.user_counts)),
        frames=int(rng.choice(a.frame_counts)),
        activity_probability=float(rng.choice(a.activity_probabilities)),
        m_z=a.m_z,
        m_y=a.m_y,
    )


def case_arguments(seed, a):
    return argparse.Namespace(**dict(descriptor(seed, a), scale=a.scale))


def training_row(seed, a, atoms, coordinates, *, compact=False):
    context = case_arguments(seed, a)
    public, truth, metadata = common.case(seed, context)
    grid = AFDMGrid.from_operator(public["operator"], **INTEGER_GRID)
    z = common.coefficient_label(truth["channel"], atoms, context)
    design = grid.design * grid.norms[None, :]
    reconstruction = np.einsum(
        "kgm,grn->kmrn", z.reshape(context.users, len(atoms), -1), atoms, optimize=True
    )
    slab_energy = slab_coordinates = active_rows = 0
    activity = np.asarray(truth["activity"], bool)
    active = z.reshape(context.users, len(atoms), -1)[activity]
    if context.grid_mode == "on_grid":
        clean = np.einsum("qkn,kmrn->qmr", public["operator"], truth["channel"], optimize=False)
        if not np.allclose(design @ z, grid.stack(clean), rtol=1e-10, atol=1e-10):
            raise ValueError(
                "on_grid clean observation differs from the exact physical dictionary label"
            )
        support = physical_row_support(truth, metadata, coordinates)
        # A fixed roundoff check, not a support threshold; support was set above.
        if np.max(abs(z[~support]), initial=0.0) > 1e-10 * max(1.0, np.max(abs(z))):
            raise ValueError("on_grid projection has signal outside its physical path support")
        occupied = z[support]
        slab_energy, slab_coordinates = float(np.sum(abs(occupied) ** 2)), occupied.size
        active_rows = int(support.sum())
    row = dict(
        design=np.asarray(design, np.complex64),
        observation=np.asarray(grid.stack(public["observation"]), np.complex64),
        target=np.asarray(z, np.complex64),
        noise=np.asarray(public["noise_variance"], np.float32),
        descriptor=descriptor(seed, a),
        slab_energy=slab_energy,
        slab_coordinates=slab_coordinates,
        active_rows=active_rows,
        active_users=int(activity.sum()),
        legacy_user_energy=float(np.sum(abs(active) ** 2)),
        legacy_user_coordinates=active.size,
        channel_energy=float(np.sum(abs(truth["channel"]) ** 2)),
        projection_residual_energy=float(np.sum(abs(truth["channel"] - reconstruction) ** 2)),
    )
    if compact:
        target = row.pop("target").reshape(context.users, len(atoms), -1)
        if np.count_nonzero(target[~activity]):
            raise ValueError("compact label requires exactly zero inactive-user blocks")
        row.pop("design")
        row.update(
            operator=np.asarray(public["operator"], np.complex64),
            active_user_indices=np.flatnonzero(activity),
            active_target=np.ascontiguousarray(target[activity]),
        )
    return row


class TensorCache:
    def __init__(self, a, atoms, coordinates):
        self.arguments, self.atoms, self.coordinates = a, atoms, coordinates
        self.compact = getattr(a, "cache_mode", "dense") == "compact"
        self.key_sha = canonical_sha(dict(conditions=condition_spec(a), compact=self.compact))
        self.limit_bytes = a.tensor_cache_mib * 2**20
        self.rows = OrderedDict()
        self.bytes = self.peak_bytes = self.hits = self.misses = self.evictions = 0

    def row(self, seed):
        key = (int(seed), self.key_sha)
        if key in self.rows:
            self.hits += 1
            self.rows.move_to_end(key)
            return self.rows[key]
        self.misses += 1
        row = training_row(seed, self.arguments, self.atoms, self.coordinates, compact=self.compact)
        size = sum(value.nbytes for value in row.values() if isinstance(value, np.ndarray))
        if size <= self.limit_bytes:
            while self.rows and self.bytes + size > self.limit_bytes:
                _, old = self.rows.popitem(last=False)
                self.bytes -= sum(
                    value.nbytes for value in old.values() if isinstance(value, np.ndarray)
                )
                self.evictions += 1
            self.rows[key] = row
            self.bytes += size
            self.peak_bytes = max(self.peak_bytes, self.bytes)
        return row

    def statistics(self):
        return dict(
            limit_bytes=self.limit_bytes,
            tensor_bytes=self.bytes,
            peak_tensor_bytes=self.peak_bytes,
            entries=len(self.rows),
            hits=self.hits,
            misses=self.misses,
            evictions=self.evictions,
            condition_spec_sha256=self.key_sha,
            cache_tensors_persisted=False,
        )


def fit_gamma(seeds, cache):
    energy = coordinates = rows = on_cases = on_users = 0
    legacy_energy = legacy_coordinates = 0
    for index, seed in enumerate(seeds):
        row = cache.row(seed)
        if (index + 1) % 512 == 0:
            print(
                json.dumps(
                    dict(
                        stage="training_slab_fit",
                        generated_training_cases=index + 1,
                        planned_training_cases=len(seeds),
                        cache=cache.statistics(),
                    )
                ),
                flush=True,
            )
        if row["descriptor"]["grid_mode"] != "on_grid":
            continue
        energy += row["slab_energy"]
        coordinates += row["slab_coordinates"]
        rows += row["active_rows"]
        on_users += row["active_users"]
        on_cases += 1
        legacy_energy += row["legacy_user_energy"]
        legacy_coordinates += row["legacy_user_coordinates"]
    if not on_cases or not coordinates or not np.isfinite(energy) or energy <= 0:
        raise ValueError("positive slab fit requires occupied rows in the on_grid training branch")
    gamma = energy / coordinates
    return dict(
        physical_variance=gamma,
        label_scope="on_grid training cases only; exact physical occupied rows",
        conditioning="lambda_n=1; physical active-user path coordinates with collisions merged",
        support_definition="on_grid active users and declared path (folded delay,Doppler), no magnitude threshold",
        assumed_slab_mean=0.0,
        estimator="sum |Z_nm|^2 / occupied row-antenna coordinate count",
        pooling="scalar shared across rows, users, antennas",
        fitted_energy=energy,
        coordinate_count=coordinates,
        occupied_row_count=rows,
        active_user_count=on_users,
        on_grid_training_cases=on_cases,
        training_cases=len(seeds),
        off_grid_cases_excluded=len(seeds) - on_cases,
        legacy_active_user_all_grid_mean=legacy_energy / legacy_coordinates,
        legacy_active_user_all_grid_coordinate_count=legacy_coordinates,
        conditional_to_legacy_ratio=gamma / (legacy_energy / legacy_coordinates),
        project_fit_not_author_value=True,
        frozen_during_training_and_inference=True,
        calibration_or_validation_or_test_truth_used=False,
    )


def micro_groups(seeds, a):
    groups = OrderedDict()
    for seed in seeds:
        d = descriptor(seed, a)
        groups.setdefault((d["users"], d["frames"], d["m_z"], d["m_y"]), []).append(seed)
    for group in groups.values():
        for offset in range(0, len(group), a.microbatch_size):
            yield group[offset : offset + a.microbatch_size]


def restored_target(row):
    if "target" in row:
        return row["target"]
    d = row["descriptor"]
    target = np.zeros((d["users"], 80, d["m_z"] * d["m_y"]), np.complex64)
    target[row["active_user_indices"]] = row["active_target"]
    return target.reshape(d["users"] * 80, -1)


def load_batch(seeds, cache):
    rows = [cache.row(seed) for seed in seeds]
    field = "operator" if cache.compact else "design"
    return (
        torch.as_tensor(np.stack([r[field] for r in rows])),
        torch.as_tensor(np.stack([r["observation"] for r in rows])),
        torch.as_tensor(np.stack([r["noise"] for r in rows])),
        torch.as_tensor(np.stack([restored_target(r) for r in rows])),
        rows,
    )


def model_result(model, inputs, y, noise, users, layers, cache):
    if not cache.compact:
        return model(inputs, y, noise, users, layers=layers)
    if hasattr(model, "forward_operator"):
        return model.forward_operator(inputs, y, noise, users, layers=layers)
    atoms = torch.as_tensor(np.array(cache.atoms), dtype=inputs.dtype)
    b, q, k, n = inputs.shape
    design = torch.einsum("bqkn,grn->bqrkg", inputs, atoms).reshape(b, q * n, k * len(atoms))
    return model(design, y, noise, users, layers=layers)


def evaluate(model, seeds, cache, layers):
    model.eval()
    measurements = []
    with torch.no_grad():
        for group in micro_groups(seeds, cache.arguments):
            design, y, noise, target, rows = load_batch(group, cache)
            estimate = model_result(
                model, design, y, noise, rows[0]["descriptor"]["users"], layers, cache
            )["mean"]
            error = torch.abs(estimate - target).square().sum((-2, -1)).double().numpy()
            denominator = torch.abs(target).square().sum((-2, -1)).double().numpy()
            for row, e, denominator in zip(rows, error, denominator):
                d = row["descriptor"]
                measurements.append(
                    dict(
                        seed=d["seed"],
                        snr_db=d["snr_db"],
                        grid_mode=d["grid_mode"],
                        users=d["users"],
                        frames=d["frames"],
                        activity_probability=d["activity_probability"],
                        coefficient_nmse=float(e / denominator),
                        channel_nmse=float(
                            (16 * e + row["projection_residual_energy"]) / row["channel_energy"]
                        ),
                    )
                )
    model.train()
    groups = {}
    for measurement in measurements:
        center = min(
            (-10.0, -6.0, -2.0, 2.0, 6.0, 10.0), key=lambda x: abs(x - measurement["snr_db"])
        )
        for key in (
            measurement["grid_mode"],
            f"snr_nearest_{center:g}",
            f"users_{measurement['users']}",
            f"frames_{measurement['frames']}",
            f"activity_probability_{measurement['activity_probability']:g}",
        ):
            groups.setdefault(key, []).append(measurement)
    grouped = {
        key: dict(
            count=len(values),
            coefficient_nmse=float(np.mean([v["coefficient_nmse"] for v in values])),
            channel_nmse=float(np.mean([v["channel_nmse"] for v in values])),
        )
        for key, values in groups.items()
    }
    return dict(
        samples=len(measurements),
        coefficient_nmse=float(np.mean([v["coefficient_nmse"] for v in measurements])),
        channel_nmse=float(np.mean([v["channel_nmse"] for v in measurements])),
        groups=grouped,
        channel_metric="orthogonal dictionary identity N||Zhat-Zprojection||²+||H-Hprojection||²; training cast complex64",
        per_case=measurements,
    )


def train_epoch(model, optimizer, seeds, cache, layers, phase, epoch):
    a = cache.arguments
    rng = np.random.default_rng(
        np.random.SeedSequence(
            [a.model_seed, layers, {"gnn": 0, "damping": 1, "joint": 2}[phase], epoch]
        )
    )
    shuffled = np.asarray(seeds)[rng.permutation(len(seeds))].tolist()
    total = steps = 0
    forward_seconds = backward_seconds = optimizer_seconds = 0.0
    for offset in range(0, len(shuffled), a.batch_size):
        batch = shuffled[offset : offset + a.batch_size]
        optimizer.zero_grad(set_to_none=True)
        for group in micro_groups(batch, a):
            design, y, noise, target, rows = load_batch(group, cache)
            started = time.perf_counter()
            estimate = model_result(
                model, design, y, noise, rows[0]["descriptor"]["users"], layers, cache
            )["mean"]
            loss = coefficient_nmse(estimate, target)
            forward_seconds += time.perf_counter() - started
            if not torch.isfinite(loss):
                raise FloatingPointError("nonfinite mixed training loss")
            started = time.perf_counter()
            (loss * (len(group) / len(batch))).backward()
            backward_seconds += time.perf_counter() - started
            total += len(group) * float(loss.detach())
        if not all(
            p.grad is None or torch.isfinite(p.grad).all()
            for group in optimizer.param_groups
            for p in group["params"]
        ):
            raise FloatingPointError("nonfinite mixed training gradient")
        started = time.perf_counter()
        optimizer.step()
        optimizer_seconds += time.perf_counter() - started
        steps += 1
    return dict(
        coefficient_nmse=total / len(seeds),
        optimizer_steps=steps,
        forward_seconds=forward_seconds,
        backward_seconds=backward_seconds,
        optimizer_seconds=optimizer_seconds,
    )


def final_joint_extension(history, budget, a):
    eligible = [r for r in history if r["layer"] == 10 and r["phase"] == "joint"]
    if len(eligible) < 4:
        raise ValueError("four final-joint validation epochs required for the fixed extension rule")
    previous = float(np.mean([r["validation"]["coefficient_nmse"] for r in eligible[-4:-2]]))
    recent = float(np.mean([r["validation"]["coefficient_nmse"] for r in eligible[-2:]]))
    improvement = (previous - recent) / previous
    extend = improvement > a.final_joint_relative_improvement and budget < a.max_final_joint_epochs
    decision = dict(
        previous_two_mean=previous,
        recent_two_mean=recent,
        relative_improvement=improvement,
        extended=bool(extend),
        at_maximum=budget >= a.max_final_joint_epochs,
    )
    return (
        min(a.max_final_joint_epochs, budget + a.final_joint_add_epochs) if extend else budget
    ), decision


def source_identity():
    source = common.source_identity(__file__)
    source["training_mode"] = TRAINING_MODE
    return source


def recipe_identity(a):
    recipe = {
        key: value
        for key, value in vars(a).items()
        if key not in ("output", "resume", "stop_after_epoch", "tensor_cache_mib")
    }
    recipe.update(
        training_mode=TRAINING_MODE,
        preliminary=a.development,
        condition_spec=condition_spec(a),
        architecture=asdict(GNNASPLSettings()),
        dictionary=INTEGER_GRID,
        optimizer="Adam",
        optimizer_reset_each_phase=True,
        gamma_fit="on_grid training physical occupied rows; mu0; pooled scalar second moment",
        selection="minimum held-out sample-average coefficient NMSE among layer10 joint epochs",
    )
    return recipe, canonical_sha(recipe)


def resolve_arguments(argv=None):
    p = parser()
    tokens = sys.argv[1:] if argv is None else list(argv)
    a = p.parse_args(tokens)
    saved = None
    if a.resume is not None:
        saved = torch.load(a.resume, map_location="cpu", weights_only=True)
        if saved.get("schema") != STATE_SCHEMA or saved.get("method") != METHOD:
            raise ValueError("mixed epoch training-state required")
        mentioned = {token.split("=", 1)[0] for token in tokens}
        for action in p._actions:
            if action.dest in ("resume", "stop_after_epoch", "tensor_cache_mib", "help"):
                continue
            if any(option in mentioned for option in action.option_strings):
                value = getattr(a, action.dest)
                recorded = saved["arguments"][action.dest]
                equal = (
                    (Path(value).resolve() == Path(recorded).resolve())
                    if action.dest == "output"
                    else value == recorded
                )
                if not equal:
                    raise ValueError(
                        f"resume cannot change recorded training argument {action.dest}"
                    )
        cache_override = (
            a.tensor_cache_mib
            if "--tensor-cache-mib" in mentioned
            else saved["arguments"]["tensor_cache_mib"]
        )
        a = argparse.Namespace(
            **saved["arguments"], resume=a.resume, stop_after_epoch=a.stop_after_epoch
        )
        a.output = Path(a.output)
        a.tensor_cache_mib = cache_override
    else:
        if a.output is None:
            raise ValueError("--output is required for a new mixed run")
        a.output = a.output.resolve()
        a.train_samples = (
            a.train_samples if a.train_samples is not None else 128 if a.development else 10001
        )
        a.validation_samples = (
            a.validation_samples
            if a.validation_samples is not None
            else 32 if a.development else 128
        )
        defaults = (1, 1, 1) if a.smoke else (2, 2, 3) if a.development else (3, 3, 5)
        for key, value in zip(("gnn_epochs", "damping_epochs", "joint_epochs"), defaults):
            if getattr(a, key) is None:
                setattr(a, key, value)
        if a.smoke:
            a.train_samples, a.validation_samples, a.batch_size, a.microbatch_size = 8, 4, 4, 2
            a.user_counts, a.frame_counts, a.m_z, a.m_y = [2], [2], 1, 2
    return a, saved


def save_state(
    a,
    model,
    source,
    recipe,
    recipe_sha,
    dataset,
    gamma,
    initial_sha,
    history,
    phase_index,
    next_epoch,
    optimizer,
    best,
    resume_count,
    elapsed,
    cache,
    final_joint_epochs,
):
    arguments = {
        key: value for key, value in vars(a).items() if key not in ("resume", "stop_after_epoch")
    }
    arguments["output"] = str(a.output)
    state = dict(
        schema=STATE_SCHEMA,
        method=METHOD,
        arguments=arguments,
        source=source,
        recipe=recipe,
        training_recipe_sha256=recipe_sha,
        dataset=dataset,
        gamma_fit=gamma,
        initial_state_sha256=initial_sha,
        state_dict=model.state_dict(),
        model_state_sha256=state_sha(model),
        history=history,
        phase_index=phase_index,
        next_epoch=next_epoch,
        optimizer_state=None if optimizer is None else optimizer.state_dict(),
        best=best,
        resume_count=resume_count,
        elapsed_seconds=elapsed,
        torch_rng_state=torch.get_rng_state(),
    )
    state["final_joint_epochs"] = final_joint_epochs
    path = a.output / "training_state.pt"
    temporary = path.with_suffix(".pt.tmp")
    torch.save(state, temporary)
    temporary.replace(path)
    write_json(a.output / "HISTORY.json", history)
    progress = dict(
        status="MIXED_CHECKPOINTED",
        completed_training_phases=phase_index,
        completed_epochs=len(history),
        next_epoch=next_epoch,
        resume_count=resume_count,
        seconds=elapsed,
        training_state_sha256=sha256(path),
        model_state_sha256=state["model_state_sha256"],
        cache=cache.statistics(),
        peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        training_completed=False,
    )
    write_json(a.output / "PROGRESS.json", progress)
    return progress


def main(argv=None):
    a, resumed = resolve_arguments(argv)
    if (
        min(
            a.train_samples,
            a.validation_samples,
            a.batch_size,
            a.microbatch_size,
            a.threads,
            a.m_z,
            a.m_y,
            a.gnn_epochs,
            a.damping_epochs,
            a.joint_epochs,
        )
        < 1
    ):
        raise ValueError("positive counts/epochs/threads required")
    max_cache = 3072 if getattr(a, "cache_mode", "dense") == "compact" else 2048
    if a.microbatch_size > a.batch_size or not 0 <= a.tensor_cache_mib <= max_cache:
        raise ValueError(
            "microbatch<=batch and bounded cache: dense<=2048MiB, compact<=3072MiB required"
        )
    if getattr(a, "adaptive_final_joint", False) and (
        a.joint_epochs < 5
        or a.max_final_joint_epochs < a.joint_epochs
        or a.final_joint_add_epochs < 1
        or not 0 < a.final_joint_relative_improvement < 1
    ):
        raise ValueError(
            "adaptive final joint requires >=5 initial epochs, valid extension and improvement rule"
        )
    if (
        not np.isfinite(a.snr_range).all()
        or a.snr_range[0] >= a.snr_range[1]
        or not 0 < a.on_grid_probability < 1
        or min(a.user_counts) < 2
        or min(a.frame_counts) < 1
        or max(a.frame_counts) > 32
        or any(not 0 < p < 1 for p in a.activity_probabilities)
        or not np.isfinite(a.scale)
        or a.scale <= 0
        or not np.isfinite(a.learning_rate)
        or a.learning_rate <= 0
    ):
        raise ValueError("valid mixed conditions and learning rate required")
    if not a.smoke and (
        a.batch_size != 128
        or (not 128 <= a.train_samples <= 10000 if a.development else a.train_samples <= 10000)
    ):
        raise ValueError(
            "development needs >=128 real samples; full needs >10000; effective batch128 required"
        )
    train_seeds = list(range(a.train_seed_base, a.train_seed_base + a.train_samples))
    validation_seeds = list(
        range(a.validation_seed_base, a.validation_seed_base + a.validation_samples)
    )
    if min(train_seeds + validation_seeds) < 0 or set(train_seeds) & set(validation_seeds):
        raise ValueError("disjoint nonnegative seed sets required")
    source = source_identity()
    recipe, recipe_sha = recipe_identity(a)
    assignments = dict(
        train=[descriptor(seed, a) for seed in train_seeds],
        validation=[descriptor(seed, a) for seed in validation_seeds],
    )
    dataset = dict(
        condition_spec=condition_spec(a),
        assignments=assignments,
        assignment_sha256=canonical_sha(assignments),
        seed_sets_disjoint=True,
    )
    if resumed is None:
        if a.output.exists():
            raise ValueError("fresh training output required")
        a.output.mkdir(parents=True)
        write_json(
            a.output / "PLAN.json",
            dict(
                source=source,
                recipe=recipe,
                training_recipe_sha256=recipe_sha,
                dataset=dataset,
                status=(
                    "SMOKE_ONLY"
                    if a.smoke
                    else "DEVELOPMENT_TRAINING" if a.development else "FULL_TRAINING"
                ),
                paper_per_snr_adaptation=True,
                formal_qualification=False,
                selection=recipe["selection"],
            ),
        )
        snapshot = a.output / "source_snapshot"
        manifest = {}
        for path in source_files():
            relative = path.relative_to(ROOT)
            dest = snapshot / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            manifest[str(relative)] = sha256(path)
        write_json(snapshot / "MANIFEST.json", manifest)
    else:
        if resumed["source"] != source:
            raise ValueError("resume source/runtime identity differs")
        if resumed["recipe"] != recipe or resumed["training_recipe_sha256"] != recipe_sha:
            raise ValueError("resume recipe identity differs")
        if resumed["dataset"] != dataset:
            raise ValueError("resume dataset assignment identity differs")
        plan = json.loads((a.output / "PLAN.json").read_text())
        if (
            plan["source"] != source
            or plan["dataset"] != dataset
            or plan["training_recipe_sha256"] != recipe_sha
        ):
            raise ValueError("resume plan identity differs")
        if a.stop_after_epoch is not None and a.stop_after_epoch <= len(resumed["history"]):
            raise ValueError("stop-after-epoch must follow completed history")
    torch.set_num_threads(a.threads)
    torch.manual_seed(a.model_seed)
    np.random.seed(a.model_seed)
    start = time.perf_counter()
    prior_seconds = 0.0 if resumed is None else resumed["elapsed_seconds"]
    try:
        atoms, coordinates, _ = physical_atoms(**INTEGER_GRID)
        project_channel_coefficients(np.zeros((1, 1, 16, 16)), atoms)
        cache = TensorCache(a, atoms, coordinates)
        gamma = fit_gamma(train_seeds, cache) if resumed is None else resumed["gamma_fit"]
        model = make_gnn_aspl_network(
            gamma["physical_variance"], backend=getattr(a, "backend", "cpu")
        )
        initial_sha = state_sha(model) if resumed is None else resumed["initial_state_sha256"]
        history = [] if resumed is None else resumed["history"]
        phase_index = 0 if resumed is None else resumed["phase_index"]
        next_epoch = 0 if resumed is None else resumed["next_epoch"]
        resume_count = 0 if resumed is None else resumed["resume_count"] + 1
        best = None if resumed is None else resumed["best"]
        final_joint_epochs = a.joint_epochs if resumed is None else resumed["final_joint_epochs"]
        if resumed is None:
            write_json(a.output / "GAMMA_FIT.json", gamma)
            write_json(
                a.output / "INITIAL_VALIDATION.json", evaluate(model, validation_seeds, cache, 10)
            )
        else:
            model.load_state_dict(resumed["state_dict"], strict=True)
            if state_sha(model) != resumed["model_state_sha256"]:
                raise ValueError("resume state hash differs")
            torch.set_rng_state(resumed["torch_rng_state"])
        tasks = [task for task in common.phase_schedule(10) if task["phase"] != "validation"]
        if not 0 <= phase_index <= len(tasks):
            raise ValueError("invalid phase boundary")
        if resumed is None:
            save_state(
                a,
                model,
                source,
                recipe,
                recipe_sha,
                dataset,
                gamma,
                initial_sha,
                history,
                0,
                0,
                None,
                best,
                0,
                time.perf_counter() - start,
                cache,
                final_joint_epochs,
            )
        for index in range(phase_index, len(tasks)):
            layer, phase = tasks[index]["layer"], tasks[index]["phase"]
            selected = model.phase_parameters(layer, phase)
            optimizer = torch.optim.Adam(selected, lr=a.learning_rate)
            if resumed is not None and index == phase_index and next_epoch:
                if resumed["optimizer_state"] is None:
                    raise ValueError("within-phase epoch resume needs Adam state")
                optimizer.load_state_dict(resumed["optimizer_state"])
            epoch = next_epoch if index == phase_index else 0
            while epoch < (
                final_joint_epochs
                if layer == 10 and phase == "joint"
                else getattr(a, phase + "_epochs")
            ):
                started = time.perf_counter()
                training = train_epoch(model, optimizer, train_seeds, cache, layer, phase, epoch)
                training_seconds = time.perf_counter() - started
                started = time.perf_counter()
                validation = evaluate(model, validation_seeds, cache, layer)
                record = dict(
                    layer=layer,
                    phase=phase,
                    epoch=epoch + 1,
                    training=training,
                    validation=validation,
                    training_seconds=training_seconds,
                    validation_seconds=time.perf_counter() - started,
                    training_samples_per_second=len(train_seeds) / training_seconds,
                )
                history.append(record)
                if (
                    layer == 10
                    and phase == "joint"
                    and (
                        best is None
                        or validation["coefficient_nmse"] < best["validation_coefficient_nmse"]
                    )
                ):
                    best = dict(
                        layer=layer,
                        phase=phase,
                        epoch=epoch + 1,
                        validation_coefficient_nmse=validation["coefficient_nmse"],
                        state_dict={
                            key: value.detach().clone() for key, value in model.state_dict().items()
                        },
                        model_state_sha256=state_sha(model),
                    )
                if (
                    a.adaptive_final_joint
                    and layer == 10
                    and phase == "joint"
                    and epoch + 1 == final_joint_epochs
                ):
                    final_joint_epochs, record["extension_decision"] = final_joint_extension(
                        history, final_joint_epochs, a
                    )
                phase_finished = epoch + 1 == (
                    final_joint_epochs
                    if layer == 10 and phase == "joint"
                    else getattr(a, phase + "_epochs")
                )
                progress = save_state(
                    a,
                    model,
                    source,
                    recipe,
                    recipe_sha,
                    dataset,
                    gamma,
                    initial_sha,
                    history,
                    index + 1 if phase_finished else index,
                    0 if phase_finished else epoch + 1,
                    None if phase_finished else optimizer,
                    best,
                    resume_count,
                    prior_seconds + time.perf_counter() - start,
                    cache,
                    final_joint_epochs,
                )
                print(
                    json.dumps(
                        dict(
                            layer=layer,
                            phase=phase,
                            epoch=epoch + 1,
                            train_nmse=training["coefficient_nmse"],
                            validation_nmse=validation["coefficient_nmse"],
                            channel_nmse=validation["channel_nmse"],
                            training_seconds=training_seconds,
                            completed_epochs=len(history),
                            completed_phases=progress["completed_training_phases"],
                        )
                    ),
                    flush=True,
                )
                if len(history) == a.stop_after_epoch:
                    return progress
                epoch += 1
            next_epoch = 0
        if source_identity() != source:
            raise ValueError("source changed during training")
        if best is None:
            raise ValueError("completed layer10 joint validation required for selection")
        last_state_sha = state_sha(model)
        model.load_state_dict(best["state_dict"], strict=True)
        selected_validation = evaluate(model, validation_seeds, cache, 10)
        if state_sha(model) != best["model_state_sha256"]:
            raise ValueError("selected model state identity differs")
        training = dict(
            status=(
                "SMOKE_ONLY"
                if a.smoke
                else "PRELIMINARY_TRAINED" if a.development else "TRAINED_UNQUALIFIED"
            ),
            training_completed=True,
            training_mode=TRAINING_MODE,
            separate_model_per_snr=False,
            shared_model_across_snr_and_grid=True,
            snr_range=a.snr_range,
            on_grid_probability=a.on_grid_probability,
            backend=getattr(a, "backend", "cpu"),
            cache_mode=getattr(a, "cache_mode", "dense"),
            final_joint_epochs=final_joint_epochs,
            training_samples=len(train_seeds),
            validation_samples=len(validation_seeds),
            train_seeds=train_seeds,
            validation_seeds=validation_seeds,
            effective_batch_size=a.batch_size,
            microbatch_size=a.microbatch_size,
            epochs=dict(gnn=a.gnn_epochs, damping=a.damping_epochs, joint=a.joint_epochs),
            completed_training_phases=29,
            completed_epochs=len(history),
            initial_learning_rate=a.learning_rate,
            initial_state_sha256=initial_sha,
            final_state_sha256=state_sha(model),
            last_training_state_sha256=last_state_sha,
            selection={key: value for key, value in best.items() if key != "state_dict"},
            selected_validation=selected_validation,
            dataset_assignment_sha256=dataset["assignment_sha256"],
            training_recipe_sha256=recipe_sha,
            resume_count=resume_count,
            seconds=prior_seconds + time.perf_counter() - start,
            peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            training_budget_scope=(
                "bounded smoke only"
                if a.smoke
                else (
                    "128+ real development training"
                    if a.development
                    else ">10000 independent mixed training cases; multiple phase epochs"
                )
            ),
            formal_qualification=False,
            threshold_calibrated=False,
            cache=cache.statistics(),
        )
        checkpoint = a.output / "checkpoint.pt"
        torch.save(
            dict(
                schema=CHECKPOINT_SCHEMA,
                method=METHOD,
                architecture=asdict(model.settings),
                dictionary=INTEGER_GRID,
                state_dict=model.state_dict(),
                gamma_fit=gamma,
                training=training,
                source=source,
                training_recipe=recipe,
                training_recipe_sha256=recipe_sha,
                dataset=dataset,
            ),
            checkpoint,
        )
        training.update(checkpoint_path=str(checkpoint), checkpoint_sha256=sha256(checkpoint))
        write_json(a.output / "STATUS.json", training)
        print(
            json.dumps(
                dict(
                    status=training["status"],
                    checkpoint=str(checkpoint),
                    seconds=training["seconds"],
                    selected_epoch=best["epoch"],
                    validation_nmse=selected_validation["coefficient_nmse"],
                )
            ),
            flush=True,
        )
        return training
    except BaseException as exc:
        write_json(
            a.output / "FAILURE.json",
            dict(
                status="FAILED",
                exception=type(exc).__name__,
                message=str(exc),
                seconds=prior_seconds + time.perf_counter() - start,
            ),
        )
        raise


if __name__ == "__main__":
    main()
