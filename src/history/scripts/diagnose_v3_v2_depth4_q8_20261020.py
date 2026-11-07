"""CPU-only diagnosis on previously revealed paired scenes; no optimization."""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "2"

import hashlib
import importlib
import itertools
import json
from pathlib import Path
import shutil
import sys
import time
import traceback
import numpy as np

ROOT = Path(r"C:\Users\25911\Desktop\afdm-gfra")
PREVIOUS = ROOT / "results/v3_vs_v2_depth4_paired20_cpu_20261020"
OUT = ROOT / "results/v3_v2_depth4_q8_diagnosis_20261020"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                   encoding="utf-8")
    tmp.replace(path)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def physical(tensor, scale):
    a = tensor.detach().numpy().astype(np.float64)
    return (a[:, 0] + 1j * a[:, 1]) * scale


def main():
    if OUT.exists():
        raise FileExistsError("A diagnosis already exists; preserve it: " + str(OUT))
    previous_plan = read(PREVIOUS / "PLAN.json")
    if read(PREVIOUS / "AUDIT.json")["status"] != "PASSED":
        raise ValueError("Unverified paired reference")
    OUT.mkdir()
    (OUT / "source").mkdir()
    shutil.copy2(__file__, OUT / "source" / Path(__file__).name)
    lock = OUT / "RUNNING.lock"
    lock.write_text(str(os.getpid()), encoding="ascii")
    try:
        run(previous_plan)
    except BaseException as error:
        write(OUT / f"FAILURE_{time.time_ns()}.json",
              dict(error=repr(error), traceback=traceback.format_exc()))
        raise
    finally:
        lock.unlink(missing_ok=True)


def run(previous_plan):
    models_bound = previous_plan["models"]
    scale = previous_plan["scale"]
    input_cases = previous_plan["cases"]
    hashes = {}
    for model in models_bound.values():
        hashes.update(model["hashes"])
    for case in input_cases:
        hashes.update({str(Path(case["folder"]) / f): h for f, h in case["files"].items()})
    hashes[str(PREVIOUS / "PLAN.json")] = sha(PREVIOUS / "PLAN.json")
    hashes[str(PREVIOUS / "AUDIT.json")] = sha(PREVIOUS / "AUDIT.json")
    for path, digest in hashes.items():
        if sha(path) != digest:
            raise ValueError("Frozen asset changed: " + path)
    shared = {}
    for filename in ("receiver_base.py", "message_damping.py", "backbone.py", "data.py"):
        values = {name: sha(Path(b["run"]) / "source_code/experiments/lstmp_candidate_20261019" / filename)
                  for name, b in models_bound.items()}
        if values["v2"] != values["v3"]:
            raise ValueError("Unequal shared source: " + filename)
        shared[filename] = values
    configs = {name: read(b["config"]) for name, b in models_bound.items()}
    for field in ("normalized_training_second_moment", "complex_variance_support"):
        assert configs["v2"][field] == configs["v3"][field], field
    for field in ("microbatch", "variance_soft_floor_temperature_ratio", "maximum_feedback_variance_ratio"):
        assert configs["v2"]["receiver"][field] == configs["v3"]["receiver"][field], field

    plan = dict(
        created_unix=time.time(), device="cpu", cpu_threads=2, previous_comparison=str(PREVIOUS),
        target=dict(group="k40_q8", index=5, seed=202610200800006, user_zero_based=27),
        fixed_queries="All four layers of both baseline trajectories on the target case.",
        paired_trajectories="All ten already revealed K40/Q8 scenes; no newly generated scenes.",
        replacements="All 2x2x2 combinations: score+alpha, activity head, gamma+beta. "
                     "Additional single-component and single-layer replacements use the new model as base.",
        labels_policy="Truth used for scoring and explicitly marked output-only oracle diagnostics. "
                      "No truth supplied to any closed-loop receiver or hybrid.",
        interpretation="Post-hoc mechanism diagnosis, not independent performance confirmation. "
                       "Hybrid networks were never trained together; interactions preclude a unique causal share.",
        weight_updates=False, threshold=.5, frozen_hashes=hashes, shared_source_hashes=shared,
        source_sha256=sha(OUT / "source" / Path(__file__).name))
    write(OUT / "PLAN.json", plan)

    import psutil
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    os.environ["AFDM_LSTMP_ROOT"] = str(ROOT)
    os.environ["AFDM_LSTMP_CONFIG"] = models_bound["v3"]["config"]
    sys.path.insert(0, str(Path(models_bound["v3"]["run"]) / "source_code"))
    import torch
    from threadpoolctl import threadpool_limits
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    threadpool_limits(2)
    from experiments.lstmp_candidate_20261019 import common, data
    from experiments.lstmp_candidate_20261019.message_damping import damp_gaussian
    receiver = importlib.import_module("experiments.lstmp_execution_v3_20261020.receiver")
    assert common.OUT.resolve() == Path(models_bound["v3"]["run"]).resolve()
    models = {}
    for name, bound in models_bound.items():
        saved = torch.load(bound["checkpoint"], map_location="cpu", weights_only=False, mmap=True)
        assert saved["depth"] == 4 and saved["epoch"] == 3
        model = receiver.Receiver()
        for _ in range(4):
            model.add_layer(None)
        model.load_state_dict(saved["state"], strict=True)
        model.eval()
        model.use_checkpoint = False
        model.graphs_enabled = False
        models[name] = model
        del saved
    assert all(next(m.parameters()).device.type == "cpu" for m in models.values())
    calibration = {name: [
        {key: float(torch.exp(getattr(layer, "c_" + key)).detach()) for key in ("gamma", "alpha", "beta")}
        for layer in model.layers] for name, model in models.items()}
    write(OUT / "CALIBRATION.json", calibration)
    statistics = {name: {k: v for k, v in read(Path(b["run"]) / "protocol/TRAINING_STATISTICS.json").items()
                         if isinstance(v, (float, int, str, bool))}
                  for name, b in models_bound.items()}
    write(OUT / "TRAINING_STATISTICS.json", statistics)

    def status(stage, **extra):
        row = dict(stage=stage, pid=os.getpid(), updated_unix=time.time(), **extra)
        write(OUT / "STATUS.json", row)
        print(json.dumps(row), flush=True)

    def load_case(case):
        with np.load(Path(case["folder"]) / "input.npz", allow_pickle=False) as f:
            public, _ = data.prepare_public(
                dict(y=f["observation"], a=f["operator"], noise=f["noise_variance"], rho=f["activity_prior"]),
                scale, "cpu", phase_mode="known", noise_mode="known")
        with np.load(Path(case["folder"]) / "truth.npz", allow_pickle=False) as f:
            truth, active = f["channel"].copy(), f["activity"].astype(bool)
        return public, truth, active

    def summarize(r, v, mu, probabilities, estimate, truth, active, **extras):
        true_energy = np.abs(truth).reshape(len(truth), -1) ** 2
        energies = true_energy.sum(1)
        arrays = {name: physical(x, scale) for name, x in
                  (("query", r), ("conditional", mu), ("estimate", estimate))}
        errors = {name: (np.abs(a - truth) ** 2).reshape(len(truth), -1).sum(1)
                  for name, a in arrays.items()}
        p = probabilities.numpy().astype(np.float64)
        decision = p >= .5
        count_coefficients = truth[0].size
        error = errors["estimate"].sum()
        row = dict(
            nmse_db=float(10 * np.log10(error / energies.sum())), error_energy=float(error),
            conditional_active_nmse_db=float(10 * np.log10(errors["conditional"][active].sum()/energies.sum())),
            misses=int(np.sum(active & ~decision)), false_alarms=int(np.sum(~active & decision)),
            query_variance=float(v),
            empirical_query_complex_mse=float(errors["query"].mean() / (count_coefficients * scale**2)),
            empirical_active_query_complex_mse=float(errors["query"][active].mean() / (count_coefficients * scale**2)),
            users=[dict(user=int(u), active=bool(active[u]), true_energy=float(energies[u]),
                        probability=float(p[u]),
                        **{name + "_error_energy": float(err[u]) for name, err in errors.items()})
                   for u in range(len(truth))], **extras)
        return row

    def selected_versions(s, a, m, override=None):
        rows = [dict(score=s, alpha=s, activity=a, gamma=m, beta=m) for _ in range(4)]
        for layer, fields in (override or {}).items():
            rows[layer].update(fields)
        return rows

    def forward(public, truth, active, versions, *, replace_message=None):
        y, a, rho = public["y"], public["a"], public["rho"]
        prior = y.new_zeros(public["channel_shape"])
        reference = y.new_tensor(rho * common.CONFIG["normalized_training_second_moment"])
        variance = reference
        trace, states = [], []
        for i, selection in enumerate(versions):
            layers = {key: models[name].layers[i] for key, name in selection.items()}
            r, v, av = receiver.base.linear_query(public, prior, variance, layers["gamma"].c_gamma)
            nv = v.expand(len(r))
            score = models[selection["score"]].score_call(layers["score"].score, r, nv)
            mu = r + torch.exp(layers["alpha"].c_alpha) * v / 2 * score
            logits = layers["activity"].activity(r, nv, mu, rho)
            probability = torch.sigmoid(logits)
            estimate = probability[:, None, None, None, None] * mu
            residual = y - a @ data.pack(estimate)
            frames, columns = y.shape[0] // 2, y.shape[1]
            raw = (residual.square().sum() - frames * columns * public["noise"]) / (
                columns * a.square().sum() / 2)
            post_v, ratio = receiver.base.feedback_variance(raw, v, layers["beta"].c_beta,
                                                           order="after_positive")
            proposed_mean = (estimate - ratio * r) / (1 - ratio)
            proposed_variance = post_v / (1 - ratio)
            next_prior, next_var, damping = damp_gaussian(
                prior, variance, proposed_mean, proposed_variance, reference)
            if replace_message and i in replace_message:
                for component, tensor in replace_message[i].items():
                    if component == "prior":
                        next_prior = tensor
                    elif component == "variance":
                        next_var = tensor
                    else:
                        raise ValueError(component)
            trace.append(summarize(r, v, mu, probability, estimate, truth, active,
                layer=i+1, raw_residual_variance=float(raw), feedback_variance=float(post_v),
                feedback_ratio=float(ratio), next_variance=float(next_var),
                damping=float(damping), linear_variance=float(av), versions=selection))
            states.append(dict(query=r, variance=v, conditional=mu, probabilities=probability,
                               estimate=estimate, score=score, prior=next_prior, next_variance=next_var))
            prior, variance = next_prior, next_var
        return trace, states

    def final_compact(trace):
        last = trace[-1]
        return {key: last[key] for key in ("nmse_db", "error_energy", "conditional_active_nmse_db",
                                          "misses", "false_alarms")} | {"target_user": last["users"][27]}

    parity = []
    baseline_summary = []
    with torch.no_grad():
        # Final-output arithmetic uses existing predictions, including all 20 scenes.
        output_swaps = []
        for case in input_cases:
            with np.load(Path(case["folder"]) / "truth.npz", allow_pickle=False) as f:
                truth, active = f["channel"], f["activity"].astype(bool)
            preds = {}
            for name in models:
                stem = PREVIOUS / name / case["group"] / f'{case["index"]:03d}'
                assert sha(stem.with_suffix(".npz")) == read(stem.with_suffix(".json"))["prediction_sha256"]
                with np.load(stem.with_suffix(".npz"), allow_pickle=False) as f:
                    preds[name] = {key: f[key] for key in f.files}
            row = dict(group=case["group"], index=case["index"], variants={})
            energy = float((abs(truth)**2).sum())
            for mu_name, p_name in itertools.product(models, repeat=2):
                x = preds[mu_name]["conditional"] * preds[p_name]["probabilities"][:, None, None, None]
                err = (abs(x-truth)**2).reshape(len(truth), -1).sum(1)
                row["variants"][f"mu_{mu_name}_p_{p_name}"] = dict(
                    nmse_db=float(10*np.log10(err.sum()/energy)),
                    error_energy=float(err.sum()), user_error_energy=err.tolist())
            for name in models:
                x = preds[name]["conditional"] * active[:, None, None, None]
                err = (abs(x-truth)**2).reshape(len(truth), -1).sum(1)
                row["variants"]["oracle_final_mask_"+name] = dict(
                    nmse_db=float(10*np.log10(err.sum()/energy)),
                    error_energy=float(err.sum()), user_error_energy=err.tolist(),
                    oracle=True, message_feedback_modified=False)
            output_swaps.append(row)
        write(OUT / "OUTPUT_SWAPS.json", output_swaps)

        target = {}
        for case in [c for c in input_cases if c["group"] == "k40_q8"]:
            public, truth, active = load_case(case)
            for name, model in models.items():
                status("BASELINE_TRACE", method=name, case=case["index"])
                trace, states = forward(public, truth, active, selected_versions(name, name, name))
                native, _ = model(public)
                last = states[-1]
                checks = {}
                for key in ("estimate", "conditional"):
                    checks[key+"_native_max_abs"] = float(abs(last[key] - native[-1][key]).max())
                checks["probabilities_native_max_abs"] = float(
                    abs(last["probabilities"] - torch.sigmoid(native[-1]["logits"])).max())
                with np.load(PREVIOUS / name / case["group"] / f'{case["index"]:03d}.npz', allow_pickle=False) as old:
                    checks["estimate_saved_max_abs"] = float(abs(physical(last["estimate"], scale)-old["estimate"]).max())
                    checks["conditional_saved_max_abs"] = float(abs(physical(last["conditional"], scale)-old["conditional"]).max())
                    checks["probabilities_saved_max_abs"] = float(abs(last["probabilities"].numpy()-old["probabilities"]).max())
                if max(checks.values()) > 2e-6:
                    raise ValueError("Baseline parity failed: " + str(checks))
                parity.append(dict(method=name, index=case["index"], **checks))
                write(OUT / "traces" / f'{name}_{case["index"]:03d}.json', trace)
                baseline_summary.append(dict(method=name, index=case["index"],
                                             seed=case["seed"], **final_compact(trace)))
                if case["index"] == 5:
                    target[name] = (trace, states)
            del native
        write(OUT / "BASELINE_SUMMARY.json", baseline_summary)
        write(OUT / "PARITY.json", parity)
        case = next(c for c in input_cases if c["group"] == "k40_q8" and c["index"] == 5)
        public, truth, active = load_case(case)

        # Feed both learned denoisers and both heads exactly the same r and v.
        fixed_queries = []
        for source, (_, states) in target.items():
            for i, state in enumerate(states):
                status("FIXED_QUERY", source=source, layer=i+1)
                r, v = state["query"], state["variance"]
                nv = v.expand(len(r))
                scores = {name: model.score_call(model.layers[i].score, r, nv)
                          for name, model in models.items()}
                for sn, an, hn in itertools.product(models, repeat=3):
                    mu = r + torch.exp(models[an].layers[i].c_alpha) * v / 2 * scores[sn]
                    prob = torch.sigmoid(models[hn].layers[i].activity(r, nv, mu, public["rho"]))
                    trace = summarize(r, v, mu, prob, prob[:, None, None, None, None]*mu, truth, active,
                                      query_source=source, layer=i+1, score=sn, alpha=an, activity=hn)
                    fixed_queries.append(trace)
        write(OUT / "FIXED_QUERY.json", fixed_queries)

        hybrids = []
        for sn, hn, mn in itertools.product(models, repeat=3):
            key = f"score_{sn}_activity_{hn}_messages_{mn}"
            status("CLOSED_LOOP_REPLACEMENT", variant=key)
            trace, _ = forward(public, truth, active, selected_versions(sn, hn, mn))
            write(OUT / "hybrids" / (key+".json"), trace)
            hybrids.append(dict(variant=key, score=sn, activity=hn, messages=mn, **final_compact(trace)))
        write(OUT / "HYBRIDS.json", hybrids)

        singles = []
        for component in ("score", "alpha", "activity", "gamma", "beta"):
            for indices in ([0, 1, 2, 3], [0], [1], [2], [3]):
                key = component + "_old_layers_" + "_".join(str(i+1) for i in indices)
                status("SINGLE_COMPONENT_REPLACEMENT", variant=key)
                versions = selected_versions("v3", "v3", "v3",
                    {i: {component: "v2"} for i in indices})
                trace, _ = forward(public, truth, active, versions)
                write(OUT / "singles" / (key+".json"), trace)
                singles.append(dict(variant=key, component=component,
                                    layers=[i+1 for i in indices], **final_compact(trace)))
        write(OUT / "SINGLES.json", singles)

        message_replays = []
        for i in range(3):
            for components in (("prior",), ("variance",), ("prior", "variance")):
                key = f"old_message_after_layer_{i+1}_" + "_".join(components)
                status("MESSAGE_REPLAY", variant=key)
                replacement = {i: {k: target["v2"][1][i]["next_variance" if k == "variance" else "prior"]
                                   for k in components}}
                trace, _ = forward(public, truth, active, selected_versions("v3", "v3", "v3"),
                                   replace_message=replacement)
                write(OUT / "message_replays" / (key+".json"), trace)
                message_replays.append(dict(variant=key, layer=i+1,
                                           components=components, **final_compact(trace)))
        write(OUT / "MESSAGE_REPLAYS.json", message_replays)

    for path, digest in hashes.items():
        if sha(path) != digest:
            raise ValueError("Frozen asset changed during diagnosis: " + path)
    write(OUT / "AUDIT.json", dict(
        status="PASSED", gpu_used=False, training_modified=False, weight_updates=False,
        baseline_scenes_replayed_per_method=10, baseline_native_and_previous_parity_verified=True,
        maximum_parity_absolute_difference=max(max(v for k, v in row.items() if k not in ("method", "index"))
                                               for row in parity),
        all_frozen_assets_verified=True, fixed_query_combinations=len(fixed_queries),
        closed_loop_combinations=len(hybrids), single_component_replacements=len(singles),
        message_replays=len(message_replays), output_arithmetic_scenes=len(output_swaps),
        plan_sha256=sha(OUT / "PLAN.json")))
    write(OUT / "COMPLETE.json", dict(status="COMPLETE", completed_unix=time.time(),
                                     audit_sha256=sha(OUT / "AUDIT.json")))
    status("COMPLETE", output=str(OUT))


if __name__ == "__main__":
    main()
