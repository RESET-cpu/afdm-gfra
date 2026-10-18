"""Prespecified full-user score AMP comparison; truth is evaluator-only.

Preparation and summary stages are CPU-only. Receiver execution is sequential
and explicitly dispatched by the parent task. Test generation requires freeze.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from afdm_jadcedd.experiment.generate import generate_case
from afdm_jadcedd.experiment.evaluation.metrics import score_arrays
from afdm_jadcedd.system.observation import ReceiverInput, array_sha256, load_input
from afdm_jadcedd.utils import sha256, write_json

DEST = ROOT / "results/joint_amp_20261015"
RUN = DEST / "comparison_v1"
SNRS = [-4, 0, 6]
METHODS = ("joint_amp", "proposed", "diffusion_amp")
SPLITS = {"solver_validation": (2026101528100000, 4), "test": (2026101528300000, 8)}
SCALE = .2647966452702405
BOOTSTRAP_SEED = 2026101528400000
PROTOCOL = Path(__file__).with_name("PROTOCOL.md")


def read(path):
    return json.loads(Path(path).read_text())


def plain(value):
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [plain(v) for v in value]
    if isinstance(value, np.ndarray):
        return plain(value.tolist())
    if isinstance(value, np.generic):
        return plain(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, Path):
        return str(value)
    return value


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, plain(value))


def frozen_json(path, value):
    value = plain(value)
    if Path(path).exists():
        if read(path) != value:
            raise ValueError(f"Frozen record differs; retain existing attempt: {path}")
    else:
        save(path, value)


def digest(value):
    return hashlib.sha256(json.dumps(plain(value), sort_keys=True).encode()).hexdigest()


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT))


def identity_audit():
    paths = sorted({*ROOT.glob("data/proposed/**/train_identities.npy"),
                    *ROOT.glob("data/proposed/**/validation_identities.npy")})
    if not paths:
        raise FileNotFoundError("Training/validation bank identities are required")
    scenes, records = set(), []
    for path in paths:
        ids = np.load(path, allow_pickle=False)
        if ids.ndim != 2 or ids.shape[1] < 1:
            raise ValueError(f"Unsupported identity layout: {path}")
        values = set(ids[:, 0].tolist())
        scenes.update(values)
        records.append(dict(path=relative(path), sha256=sha256(path), samples=len(ids),
                            unique_scenes=len(values)))
    split_seeds = {name: list(range(base, base + count)) for name, (base, count) in SPLITS.items()}
    overlap = {name: sorted(scenes.intersection(seeds)) for name, seeds in split_seeds.items()}
    if any(overlap.values()):
        raise ValueError(f"Scene leakage from existing data banks: {overlap}")
    if set(split_seeds["solver_validation"]) & set(split_seeds["test"]):
        raise AssertionError("Development/test scene overlap")
    # Written at initial development preparation; this audit itself makes no draws.
    return dict(status="PASS", bank_identity_files=records, split_seeds=split_seeds,
                overlap=overlap, test_generated=False,
                calibration_used=False, reserved_calibration_seed_base=2026101528200000)


def generator_assets():
    paths = [ROOT / "src/afdm_jadcedd/experiment/generate.py",
             *sorted((ROOT / "src/afdm_jadcedd/system").rglob("*.py"))]
    return {relative(p): sha256(p) for p in paths}


def verify_freeze():
    path = RUN / "TEST_FREEZE.json"
    if not path.exists():
        raise RuntimeError("Freeze checkpoint, configurations and code before opening test")
    record = read(path)
    changed = [name for name, expected in record["assets"].items()
               if not (ROOT / name).is_file() or sha256(ROOT / name) != expected]
    if changed:
        raise ValueError(f"Frozen test assets changed: {changed}")
    return record


def prepare(split):
    if split == "test":
        freeze = verify_freeze()
        frozen_json(RUN / "TEST_OPENED.json", dict(freeze_sha256=sha256(RUN / "TEST_FREEZE.json"),
                                                   independent_test_seeds=freeze["test_seeds"]))
    audit = identity_audit()
    audit["generator_assets"] = generator_assets()
    frozen_json(RUN / "IDENTITY_AUDIT.json", audit)
    base, count = SPLITS[split]
    cases, pair_checks = [], []
    for scene in range(count):
        reference = None
        for snr in SNRS:
            folder = RUN / "data" / split / f"scene{scene:02d}" / f"snr{snr:+d}"
            meta_path = folder / "CASE.json"
            if not meta_path.exists():
                if (folder / "input.npz").exists() or (folder / "truth.npz").exists():
                    raise RuntimeError(f"Partial data generation retained; inspect {folder}")
                inputs, truth, meta = generate_case(base + scene, snr, SCALE)
                folder.mkdir(parents=True, exist_ok=True)
                public = {key: inputs[key] for key in ReceiverInput.__dataclass_fields__}
                np.savez_compressed(folder / "input.npz", **public)
                np.savez_compressed(folder / "truth.npz", **truth)
                meta.update(input_sha256=sha256(folder / "input.npz"),
                            truth_sha256=sha256(folder / "truth.npz"),
                            channel_array_sha256=array_sha256(truth["channel"]),
                            operator_array_sha256=array_sha256(public["operator"]),
                            activity_array_sha256=array_sha256(truth["activity"]),
                            training_scene_overlap=False,
                            identity_audit_sha256=sha256(RUN / "IDENTITY_AUDIT.json"))
                save(meta_path, meta)
            meta = read(meta_path)
            if meta["seed"] != base + scene or meta["snr_db"] != snr:
                raise ValueError("Saved case identity differs")
            for name in ("input", "truth"):
                if meta[f"{name}_sha256"] != sha256(folder / f"{name}.npz"):
                    raise ValueError(f"Saved {name} changed: {folder}")
            public = load_input(folder / "input.npz")
            if public.observation.shape != (16, 16, 16) or public.operator.shape != (16, 40, 16):
                raise ValueError("Unexpected public scene dimensions")
            keys = ("channel_array_sha256", "operator_array_sha256", "activity_array_sha256",
                    "standardized_noise_sha256")
            paired = {key: meta[key] for key in keys}
            if reference is None:
                reference = paired
            if paired != reference:
                raise ValueError("Cross-SNR physical scene or standardized noise mismatch")
            cases.append(dict(scene=scene, seed=base + scene, snr_db=snr, folder=folder))
        pair_checks.append(dict(scene=scene, seed=base + scene, status="PASS", hashes=reference))
    frozen_json(RUN / "data" / split / "DATA_AUDIT.json", dict(
        status="PASS", split=split, physical_scenes=count, input_cases=len(cases), snr_db=SNRS,
        receiver_input_fields=list(ReceiverInput.__dataclass_fields__),
        cross_snr_pairing=pair_checks, identity_audit_sha256=sha256(RUN / "IDENTITY_AUDIT.json"),
        input_hashes={relative(c["folder"] / "input.npz"): sha256(c["folder"] / "input.npz") for c in cases}))
    return cases


def method_sources(method):
    folder = ROOT / "src/afdm_jadcedd/algorithm" / method
    paths = sorted(folder.glob("*.py"))
    if not paths or not (folder / "receiver.py").exists():
        raise FileNotFoundError(f"Receiver implementation not ready: {method}")
    common = [ROOT / "src/afdm_jadcedd/system/observation.py",
              ROOT / "src/afdm_jadcedd/project.py", ROOT / "src/afdm_jadcedd/utils.py"]
    if method in ("joint_amp", "diffusion_amp"):
        common.append(ROOT / "src/afdm_jadcedd/algorithm/ldamp/representation.py")
    return {relative(p): sha256(p) for p in paths + common}


def model_assets(config):
    paths = []
    for key in ("checkpoint_path", "first_checkpoint", "second_checkpoint", "evidence_checkpoint", "prior_definition"):
        if key in config:
            paths.append(ROOT / config[key])
    if config.get("readout"):
        paths.append(ROOT / config["readout"]["path"])
    return {relative(p): sha256(p) for p in paths}


def binding(method, config, device):
    return dict(method=method, configuration=config, device=device,
                sources=method_sources(method), models=model_assets(config))


def build_receiver(method, config, device):
    if method == "joint_amp":
        from afdm_jadcedd.algorithm.joint_amp.receiver import JointAMPReceiver
        return JointAMPReceiver(config, device=device)
    if method == "diffusion_amp":
        from afdm_jadcedd.algorithm.diffusion_amp.receiver import DiffusionAMPReceiver
        return DiffusionAMPReceiver(config, device=device)
    from afdm_jadcedd.algorithm.proposed.receiver import Receiver
    return Receiver(config, device=device)


def run_cases(receiver, cases, method, label, split, config, device):
    run_binding = binding(method, config, device)
    frozen_json(RUN / split / label / "BINDING.json", run_binding)
    records = []
    for case in cases:
        folder = RUN / split / label / f"scene{case['scene']:02d}" / f"snr{case['snr_db']:+d}"
        folder.mkdir(parents=True, exist_ok=True)
        output = folder / "estimate.npz"
        record_path = output.with_suffix(".json")
        evaluator_path = folder / "EVALUATOR.json"
        input_path = case["folder"] / "input.npz"
        # Inference and observer never open truth. Retained states are scored later.
        snapshots, observed_rows = [], []
        if record_path.exists():
            record = read(record_path)
            if record.get("input_sha256") != sha256(input_path):
                raise ValueError("Cached receiver input differs")
            if hasattr(receiver, "signature") and record.get("inference_sha256") not in (None, receiver.signature):
                raise ValueError("Cached native receiver signature differs")
            native_config = record.get("configuration")
            if native_config is not None and any(native_config.get(key) != value for key, value in config.items()):
                raise ValueError("Cached native receiver configuration differs")
            if output.exists() and record.get("output_sha256") != sha256(output):
                raise ValueError("Cached receiver output differs")
            evaluator = read(evaluator_path) if evaluator_path.exists() else dict(
                wall_seconds=None, recovered_native_record=True,
                binding_sha256=digest(run_binding), input_sha256=sha256(input_path))
            if evaluator.get("binding_sha256") != digest(run_binding):
                raise ValueError("Cached inference binding differs")
        else:
            if output.exists():
                raise RuntimeError(f"Partial native output retained: {output}")
            def observer(row, state, *unused):
                observed_rows.append(plain(dict(row)))
                if isinstance(state, np.ndarray):
                    estimate = np.array(state, copy=True)
                elif hasattr(state, "mean"):
                    estimate = np.array(state.mean * config["scale"], copy=True)
                else:
                    return
                snapshots.append((row.get("iteration", len(observed_rows)), estimate))
            started = time.monotonic()
            try:
                record = receiver.run(input_path, output, observer=observer)
            except Exception as exc:
                if record_path.exists():
                    record = read(record_path)
                else:
                    record = dict(status="FAILED", error=repr(exc), input_sha256=sha256(input_path))
                    save(record_path, record)
            evaluator = dict(wall_seconds=time.monotonic() - started,
                             binding_sha256=digest(run_binding), input_sha256=sha256(input_path),
                             truth_loaded_during_receiver_run=False,
                             observer="copies receiver rows and estimates; offline scoring after run")
            save(evaluator_path, evaluator)
            trace = observed_rows or record.get("trace", [])
            save(folder / "TRACE.json", dict(rows=trace, source="native receiver/observer", truth_used=False))
        if not (folder / "TRACE.json").exists():
            save(folder / "TRACE.json", dict(rows=record.get("trace", []), source="recovered native record", truth_used=False))
        with np.load(case["folder"] / "truth.npz", allow_pickle=False) as data:
            truth = {key: data[key] for key in data.files}
        if snapshots:
            energy = float(np.sum(abs(truth["channel"]) ** 2))
            diagnostic = [dict(iteration=i, full_error=float(np.sum(abs(h - truth["channel"]) ** 2)),
                               signal_energy=energy,
                               nmse_db=float(10 * np.log10(max(np.sum(abs(h - truth["channel"]) ** 2) / energy, np.finfo(float).tiny))))
                          for i, h in snapshots]
            save(folder / "ITERATION_METRICS.json", dict(truth_used_only_after_inference=True, rows=diagnostic))
        row = {key: case[key] for key in ("scene", "seed", "snr_db")}
        row.update(method=method, label=label, status=record.get("status", "FAILED"),
                   output=relative(output), native_record=relative(record_path),
                   seconds=record.get("seconds"), wall_seconds=evaluator.get("wall_seconds"),
                   iterations=record.get("iterations"), probability_query_iteration=record.get("probability_query_iteration"))
        for key in ("denoiser_calls", "directional_derivative_evaluations", "network_batches",
                    "first_score_calls", "second_score_calls", "classifier_calls"):
            row[key] = record.get(key)
        if row["status"] == "COMPLETE":
            if not output.exists():
                raise ValueError("COMPLETE receiver has no native output")
            with np.load(output, allow_pickle=False) as data:
                arrays = {key: data[key] for key in data.files}
            if "activity_decision" not in arrays:
                if "probabilities" not in arrays:
                    raise ValueError("Activity decision unavailable; never insert placeholder decisions")
                arrays["activity_decision"] = arrays["probabilities"] >= config.get("decision_threshold", .5)
            if not np.isfinite(arrays["estimate"]).all():
                raise ValueError("Nonfinite COMPLETE estimate")
            if "probabilities" in arrays:
                probability = arrays["probabilities"]
                if (probability.shape != truth["activity"].shape or not np.isfinite(probability).all()
                        or np.any(probability < 0) or np.any(probability > 1)):
                    raise ValueError("Invalid native activity probabilities")
            row["metrics"] = score_arrays(arrays, truth)
            if "probabilities" in arrays:
                probability_error = arrays["probabilities"].astype(float) - truth["activity"].astype(float)
                row["metrics"].update(brier_sum=float(np.sum(probability_error ** 2)),
                                      brier_user_count=int(probability_error.size))
            else:
                row["metrics"].update(brier_sum=None, brier_user_count=None)
            activity = dict(probabilities=arrays.get("probabilities"),
                            activity_score=arrays.get("activity_score"),
                            activity_decision=arrays["activity_decision"],
                            probability_query_iteration=record.get("probability_query_iteration"),
                            channel_regated=False,
                            interpretation="last accepted query probability; channel may be history-damped"
                            if method == "joint_amp" else "native frozen receiver activity rule")
            save(folder / "ACTIVITY.json", activity)
        else:
            row["failure"] = record.get("failure", record.get("error", "Native failure"))
        save(folder / "METRICS.json", row)
        records.append(row)
        save(RUN / split / f"{label}_ROWS.json", records)
        print(json.dumps({key: row.get(key) for key in ("method", "label", "scene", "snr_db", "status", "seconds")}), flush=True)
    return records


def aggregate(rows, expected):
    complete = [row for row in rows if row["status"] == "COMPLETE"]
    result = dict(expected_cases=expected, attempted=len(rows), complete=len(complete),
                  failed=len(rows) - len(complete), pending=expected - len(rows), nmse_db=None)
    if len(rows) != expected or len(complete) != expected or expected == 0:
        result["status"] = "INCOMPLETE" if len(rows) < expected else "FAILED"
        return result
    keys = ("full_error", "active_error", "inactive_error", "signal_energy", "active", "inactive", "misses", "false_alarms")
    sums = {key: sum(row["metrics"][key] for row in rows) for key in keys}
    result.update(sums, status="COMPLETE")
    ratio_db = lambda numerator: float(10 * np.log10(max(numerator / sums["signal_energy"], np.finfo(float).tiny)))
    result.update(nmse_db=ratio_db(sums["full_error"]), active_nmse_db=ratio_db(sums["active_error"]),
                  inactive_error_over_signal=sums["inactive_error"] / sums["signal_energy"],
                  miss_rate=sums["misses"] / sums["active"] if sums["active"] else None,
                  false_alarm_rate=sums["false_alarms"] / sums["inactive"] if sums["inactive"] else None,
                  activity_error_rate=(sums["misses"] + sums["false_alarms"]) / (sums["active"] + sums["inactive"]))
    if all(row["metrics"].get("brier_sum") is not None
           and row["metrics"].get("brier_user_count", 0) > 0 for row in rows):
        brier_sum = sum(row["metrics"]["brier_sum"] for row in rows)
        brier_count = sum(row["metrics"]["brier_user_count"] for row in rows)
        result.update(brier_sum=brier_sum, brier_user_count=brier_count,
                      brier_score=brier_sum / brier_count)
    else:
        result.update(brier_sum=None, brier_user_count=None, brier_score=None)
    for key in ("seconds", "wall_seconds", "iterations", "denoiser_calls", "directional_derivative_evaluations",
                "network_batches", "first_score_calls", "second_score_calls", "classifier_calls"):
        values = [row.get(key) for row in rows]
        result[f"mean_{key}"] = float(np.mean(values)) if all(v is not None for v in values) else None
    return result


def base_config(checkpoint):
    checkpoint = Path(checkpoint).resolve()
    return dict(schema="afdm-joint-score-amp-v1", checkpoint_path=relative(checkpoint),
                checkpoint_sha256=sha256(checkpoint), scale=SCALE, batch_size=40,
                solver=dict(iterations=12, probes=16, damping=.5, divergence_seed=202610152703),
                decision_threshold=.5)


def validate(config, device, smoke=False):
    cases = prepare("solver_validation")
    frozen_json(RUN / "BASE_CONFIG.json", config)
    frozen_json(RUN / "VALIDATION_MODEL.json", dict(models=model_assets(config), sources=method_sources("joint_amp")))
    candidates = []
    for beta in ((.5,) if smoke else (.5, 1.)):
        candidate = deepcopy(config)
        candidate["solver"]["damping"] = beta
        label = f"beta_{beta:g}"
        split = "smoke" if smoke else "solver_validation"
        frozen_json(RUN / split / f"{label}_CONFIG.json", candidate)
        receiver = build_receiver("joint_amp", candidate, device)
        rows = run_cases(receiver, cases[:1] if smoke else cases, "joint_amp", label, split, candidate, device)
        del receiver
        candidates.append(dict(label=label, configuration=candidate, metrics=aggregate(rows, 1 if smoke else len(cases))))
    if smoke:
        save(RUN / "smoke" / "SUMMARY.json", dict(candidates=candidates, used_only_development_scene=True))
        return
    eligible = [item for item in candidates if item["metrics"]["status"] == "COMPLETE"]
    selection = dict(status="COMPLETE" if eligible else "FAILED", candidates=candidates,
                     criterion="Zero failures on all 12 validation inputs, then minimum pooled full-channel NMSE; ties beta=1",
                     activity_threshold=.5, calibration_used=False)
    if not eligible:
        frozen_json(RUN / "solver_validation" / "SELECTION.json", selection)
        raise RuntimeError("No eligible validation candidate; retain all failures and do not open test")
    chosen = min(eligible, key=lambda item: (item["metrics"]["nmse_db"], -item["configuration"]["solver"]["damping"]))
    selection["chosen"] = chosen["label"]
    frozen_json(RUN / "solver_validation" / "SELECTION.json", selection)
    frozen_json(RUN / "CHOSEN_CONFIG.json", chosen["configuration"])


def freeze_test():
    selection = read(RUN / "solver_validation" / "SELECTION.json")
    if selection.get("status") != "COMPLETE":
        raise RuntimeError("Successful prespecified solver selection required")
    config = read(RUN / "CHOSEN_CONFIG.json")
    current = dict(models=model_assets(config), sources=method_sources("joint_amp"))
    if current != read(RUN / "VALIDATION_MODEL.json"):
        raise ValueError("Model/code changed since solver validation")
    if config.get("decision_threshold") != .5 or config["solver"]["probes"] != 16:
        raise ValueError("Prespecified activity threshold and probes required")
    frozen_json(RUN / "FROZEN_CONFIG.json", config)
    configs = {"joint_amp": config}
    for method in ("proposed", "diffusion_amp"):
        configs[method] = read(ROOT / "configs" / f"{method}.json")
    frozen_json(RUN / "BASELINE_CONFIGS.json", {key: value for key, value in configs.items() if key != "joint_amp"})
    assets = generator_assets()
    for method, configuration in configs.items():
        assets.update(method_sources(method))
        assets.update(model_assets(configuration))
    for path in [Path(__file__), Path(__file__).with_name("report.py"), PROTOCOL,
                 RUN / "FROZEN_CONFIG.json", RUN / "BASELINE_CONFIGS.json",
                 RUN / "IDENTITY_AUDIT.json", RUN / "solver_validation/SELECTION.json",
                 ROOT / "configs/proposed.json", ROOT / "configs/diffusion_amp.json",
                 ROOT / "src/afdm_jadcedd/experiment/evaluation/metrics.py"]:
        assets[relative(path)] = sha256(path)
    base, count = SPLITS["test"]
    frozen_json(RUN / "TEST_FREEZE.json", dict(schema="joint-score-amp-test-freeze-v1", assets=assets,
        test_seeds=list(range(base, base + count)), snr_db=SNRS,
        activity_threshold=.5, calibration_used=False, methods=list(METHODS),
        criterion=selection["criterion"], selected=selection["chosen"], test_results_seen=False))
    verify_freeze()


def paired_intervals(by_method):
    n = SPLITS["test"][1]
    if any(aggregate(rows, n * len(SNRS))["status"] != "COMPLETE" for rows in by_method.values()):
        return dict(status="UNAVAILABLE", reason="All three complete paired sets are required")
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draws = rng.integers(0, n, size=(5000, n))
    differences = {}
    for baseline in ("proposed", "diffusion_amp"):
        entries = []
        for label, snrs in [("all", SNRS)] + [(str(snr), [snr]) for snr in SNRS]:
            statistics = {}
            for method in ("joint_amp", baseline):
                groups = [[r for r in by_method[method] if r["scene"] == scene and r["snr_db"] in snrs] for scene in range(n)]
                error = np.array([sum(r["metrics"]["full_error"] for r in group) for group in groups])
                energy = np.array([sum(r["metrics"]["signal_energy"] for r in group) for group in groups])
                mistakes = np.array([sum(r["metrics"]["misses"] + r["metrics"]["false_alarms"] for r in group) for group in groups])
                users = np.array([sum(r["metrics"]["active"] + r["metrics"]["inactive"] for r in group) for group in groups])
                stats = dict(nmse_db=(10 * np.log10(error.sum() / energy.sum()),
                                    10 * np.log10(error[draws].sum(1) / energy[draws].sum(1))),
                             activity_error_rate=(mistakes.sum() / users.sum(), mistakes[draws].sum(1) / users[draws].sum(1)))
                if all(r.get("seconds") is not None for group in groups for r in group):
                    seconds = np.array([np.mean([r["seconds"] for r in group]) for group in groups])
                    stats["mean_seconds"] = (seconds.mean(), seconds[draws].mean(1))
                statistics[method] = stats
            entry = dict(snr=label, new_minus_baseline={})
            for metric in statistics["joint_amp"].keys() & statistics[baseline].keys():
                new, old = statistics["joint_amp"][metric], statistics[baseline][metric]
                entry["new_minus_baseline"][metric] = dict(value=float(new[0] - old[0]),
                    percentile_95=np.quantile(new[1] - old[1], [.025, .975]).tolist())
            entries.append(entry)
        differences[baseline] = entries
    return dict(status="COMPLETE", resampling_unit="physical scene; all SNRs and methods kept together",
                physical_scenes=n, replicates=5000, seed=BOOTSTRAP_SEED, differences=differences,
                scope="Preliminary evidence from eight scenes and one newly trained checkpoint")


def summarize():
    by_method = {}
    for method in METHODS:
        path = RUN / "test" / f"{method}_ROWS.json"
        rows = read(path) if path.exists() else []
        identities = [(row["scene"], row["snr_db"]) for row in rows]
        if len(identities) != len(set(identities)):
            raise ValueError("Repeated test input in summary")
        expected = {(scene, snr) for scene in range(SPLITS["test"][1]) for snr in SNRS}
        if not set(identities).issubset(expected):
            raise ValueError("Unregistered test input in summary")
        by_method[method] = rows
    methods = {method: dict(overall=aggregate(rows, 24),
                            by_snr={str(snr): aggregate([row for row in rows if row["snr_db"] == snr], 8) for snr in SNRS})
               for method, rows in by_method.items()}
    all_complete = all(value["overall"]["status"] == "COMPLETE" for value in methods.values())
    summary = dict(schema="full-user-joint-score-amp-comparison-v1",
                   status="COMPLETE" if all_complete else "INCOMPLETE", methods=methods,
                   snr_db=SNRS, independent_physical_scenes=8, expected_inputs_per_method=24,
                   uncertainty=paired_intervals(by_method),
                   freeze_sha256=sha256(RUN / "TEST_FREEZE.json") if (RUN / "TEST_FREEZE.json").exists() else None,
                   complete_set_scores_require_all_inputs=True)
    save(RUN / "SUMMARY.json", summary)
    return summary


def evaluate(device, methods):
    verify_freeze()
    config = read(RUN / "FROZEN_CONFIG.json")
    configs = {"joint_amp": config, **read(RUN / "BASELINE_CONFIGS.json")}
    cases = prepare("test")
    import torch
    for method in methods:
        verify_freeze()
        receiver = build_receiver(method, configs[method], device)
        run_cases(receiver, cases, method, method, "test", configs[method], device)
        del receiver
        if device == "mps" and torch.backends.mps.is_available():
            torch.mps.empty_cache()
        summarize()
    return summarize()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True,
                        choices=("prepare-validation", "smoke", "validate", "freeze", "evaluate", "summarize"))
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--device", choices=("cpu", "mps"), default="mps")
    parser.add_argument("--methods", nargs="+", choices=METHODS, default=list(METHODS))
    args = parser.parse_args()
    if args.stage == "prepare-validation":
        cases = prepare("solver_validation")
        print(json.dumps(dict(status="COMPLETE", stage=args.stage, input_cases=len(cases), test_generated=False)))
    elif args.stage == "freeze":
        freeze_test()
    elif args.stage == "summarize":
        print(json.dumps(summarize(), ensure_ascii=False))
    else:
        import torch
        from threadpoolctl import threadpool_limits
        torch.set_num_threads(1)
        with threadpool_limits(limits=1):
            if args.stage in ("smoke", "validate"):
                if args.checkpoint is None:
                    parser.error("--checkpoint is required for smoke/validate")
                validate(base_config(args.checkpoint), args.device, smoke=args.stage == "smoke")
            elif args.stage == "evaluate":
                evaluate(args.device, args.methods)
    print("COMPLETED", args.stage, flush=True)


if __name__ == "__main__":
    main()
