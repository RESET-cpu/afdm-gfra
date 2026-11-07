"""Reanalyse saved five/seven-layer evidence without receiver inference or training."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RUN = Path(r"D:\afdm-gfra-cpu\runs\lstmp_refinenet_depth7_20261020")
PARENT = RUN.parent / "lstmp_refinenet_50000_epoch6_20261020"
PAIRED = ROOT / "results/lstmp_depth7_reuse_previous20_20261020"
OUT = ROOT / "results/lstmp_depth7_design_review_20261020"
SCALE = 0.2647966452702405
BOOTSTRAPS = 3000


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                    encoding="utf-8")


def db(value):
    return 10 * math.log10(value) if value > 0 else None


def summary(rows, layer=None):
    metrics = rows if layer is None else [r["layer_metrics"][layer] for r in rows]
    fields = ("error_energy", "truth_energy", "active_error_energy",
              "inactive_error_energy", "misses", "false_alarms", "active", "inactive")
    s = {key: sum(row[key] for row in metrics) for key in fields}
    users = s["active"] + s["inactive"]
    s.update(scenes=len(rows), users=users,
             pooled_nmse_db=db(s["error_energy"] / s["truth_energy"]),
             active_effective_nmse_db=db(s["active_error_energy"] / s["truth_energy"]),
             mean_scene_nmse_db=db(float(np.mean([r["nmse"] for r in metrics]))),
             aer=(s["misses"] + s["false_alarms"]) / users,
             missed_detection_rate=s["misses"] / s["active"],
             false_alarm_rate=s["false_alarms"] / s["inactive"],
             balanced_error_rate=.5 * (s["misses"] / s["active"] +
                                      s["false_alarms"] / s["inactive"]),
             mean_scene_bce=float(np.mean([r["activity_bce"] for r in metrics])),
             pooled_bce=sum(r["users"] * m["activity_bce"]
                            for r, m in zip(rows, metrics)) / users)
    return s


def key(row, snr=True):
    c = row["condition"]
    result = (c["users"], c["frames"], c["activity_probability"])
    return result + (row["snr"],) if snr else result


def quantiles(values):
    a = np.asarray(values, dtype=float)
    return dict(zip(("min", "p10", "median", "p90", "max"),
                    np.quantile(a, [0, .1, .5, .9, 1]).tolist()))


def diagnostics(rows):
    records = []
    for layer in range(len(rows[0]["diagnostics"])):
        ds = [r["diagnostics"][layer] for r in rows]
        realized = [r["layer_metrics"][layer]["error_energy"] /
                    r["layer_metrics"][layer]["complex_coefficients"] / SCALE**2
                    for r in rows]
        records.append(dict(
            layer=layer + 1,
            feedback_used_by_later_layer=layer + 1 < len(rows[0]["diagnostics"]),
            negative_raw_residual_scenes=sum(d["raw_residual_variance"] < 0 for d in ds),
            feedback_ratio_over_09=sum(d["feedback_ratio"] > .9 for d in ds),
            damped_scenes=sum(d["damping"] < 1 for d in ds),
            query_outside_pretraining=sum(d["out_of_pretraining_support"] for d in ds),
            query_variance=quantiles([d["query_variance"] for d in ds]),
            query_mse_over_variance=quantiles(
                [d["query_mse"] / d["query_variance"] for d in ds]),
            active_query_mse_over_variance=quantiles(
                [d["query_active_mse"] / d["query_variance"] for d in ds]),
            inactive_query_mse_over_variance=quantiles(
                [d["query_inactive_mse"] / d["query_variance"] for d in ds]),
            feedback_over_realized_effective_mse=quantiles(
                [d["feedback_variance"] / mse for d, mse in zip(ds, realized)]),
        ))
    return records


def decomposition(value):
    rows = value["rows"]
    depth = len(rows[0]["layer_metrics"])
    weights = np.array([.8 / (depth - 1)] * (depth - 1) + [1.]) / 1.8
    nmse = np.array([[m["nmse"] for m in row["layer_metrics"]] for row in rows])
    bce = np.array([[m["activity_bce"] for m in row["layer_metrics"]] for row in rows])
    weighted_nmse, weighted_bce = nmse @ weights, bce @ weights
    error = float(np.max(np.abs(weighted_nmse + .1 * weighted_bce -
                                [r["loss"] for r in rows])))
    assert error < 1e-6, error
    return dict(weighted_nmse=float(weighted_nmse.mean()),
                weighted_bce=float(weighted_bce.mean()),
                weighted_bce_contribution=float(.1 * weighted_bce.mean()),
                reconstructed_loss=float((weighted_nmse + .1 * weighted_bce).mean()),
                reconstruction_max_error=error)


def compare(a, b):
    sa, sb = summary(a), summary(b)
    fields = ("pooled_nmse_db", "aer", "missed_detection_rate", "false_alarm_rate",
              "balanced_error_rate", "misses", "false_alarms", "error_energy",
              "active_error_energy", "inactive_error_energy", "mean_scene_bce", "pooled_bce")
    return dict(after_minus_before={f: sb[f] - sa[f] for f in fields},
                scenes_nmse_improved=sum(y["nmse"] < x["nmse"] for x, y in zip(a, b)),
                scenes_nmse_worsened=sum(y["nmse"] > x["nmse"] for x, y in zip(a, b)),
                active_error_relative_change=sb["active_error_energy"] /
                    sa["active_error_energy"] - 1,
                inactive_error_relative_change=sb["inactive_error_energy"] /
                    sa["inactive_error_energy"] - 1)


def bootstrap(a, b):
    rng = np.random.default_rng(20261020123)
    groups = {}
    for i, r in enumerate(a):
        groups.setdefault(key(r), []).append(i)
    indices = np.concatenate(
        [rng.choice(ids, size=(BOOTSTRAPS, len(ids))) for ids in groups.values()], axis=1)

    def statistics(rows):
        total = lambda f: np.array([r[f] for r in rows])[indices].sum(axis=1)
        active, inactive = total("active"), total("inactive")
        miss, false = total("misses"), total("false_alarms")
        return dict(pooled_nmse_db=10 * np.log10(total("error_energy") / total("truth_energy")),
                    aer=(miss + false) / (active + inactive),
                    missed_detection_rate=miss / active, false_alarm_rate=false / inactive)
    aa, bb = statistics(a), statistics(b)
    return {k: np.quantile(bb[k] - aa[k], [.025, .975]).tolist() for k in aa}


def csv_write(path, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    paths = {"five_selected": PARENT / "checkpoints/depth_5/best_validation.json"}
    for depth in (6, 7):
        for epoch in range(3):
            paths[f"depth{depth}_epoch{epoch}"] = (
                RUN / f"checkpoints/depth_{depth}/validation_epoch_{epoch}.json")
    inputs = {k: dict(path=str(p), sha256=digest(p)) for k, p in paths.items()}
    values = {k: read(p) for k, p in paths.items()}
    first = values["five_selected"]["rows"]
    identity = lambda r: (r["seed"], r["snr"], key(r),
                          r["frontend"]["observation_sha256"],
                          r["frontend"]["operator_sha256"], r["truth_energy"],
                          r["active"], r["inactive"])
    for v in values.values():
        assert len(v["rows"]) == 1200
        assert [identity(r) for r in v["rows"]] == [identity(r) for r in first]
        s = summary(v["rows"])
        for field in ("pooled_nmse_db", "aer", "misses", "false_alarms", "error_energy"):
            assert math.isclose(s[field], v["summary"][field], rel_tol=1e-12, abs_tol=1e-10)

    all_summaries = {name: summary(v["rows"]) | dict(loss=v["summary"]["loss"])
                     for name, v in values.items()}
    layer_rows, condition_rows, profile_rows = [], [], []
    grouped_diagnostics = {}
    for name, v in values.items():
        rows = v["rows"]
        for layer in range(len(rows[0]["layer_metrics"])):
            layer_rows.append(dict(stage=name, layer=layer + 1) | summary(rows, layer))
        for use_snr, target in ((True, condition_rows), (False, profile_rows)):
            groups = {}
            for r in rows:
                groups.setdefault(key(r, use_snr), []).append(r)
            for c, group in sorted(groups.items()):
                condition = dict(users_condition=c[0], frames=c[1], activity_probability=c[2])
                if use_snr:
                    condition["snr_db"] = c[3]
                target.append(dict(stage=name) | condition | summary(group))
        if name in ("five_selected", "depth7_epoch1", "depth7_epoch2"):
            grouped_diagnostics[name] = {"all": diagnostics(rows)}
            for c in sorted({key(r, False) for r in rows}):
                group = [r for r in rows if key(r, False) == c]
                grouped_diagnostics[name][str(c)] = diagnostics(group)

    pairs = [("five_selected", "depth7_epoch1"),
             ("depth6_epoch1", "depth7_epoch1"),
             ("depth6_epoch1", "depth6_epoch2"),
             ("depth7_epoch0", "depth7_epoch1"),
             ("depth7_epoch1", "depth7_epoch2")]
    comparisons = {}
    for before, after in pairs:
        a, b = values[before]["rows"], values[after]["rows"]
        item = compare(a, b)
        item["stratified_scene_bootstrap_95_percentile"] = bootstrap(a, b)
        item["nmse_improved_conditions"] = sum(
            summary([r for r in b if key(r) == c])["pooled_nmse_db"] <
            summary([r for r in a if key(r) == c])["pooled_nmse_db"]
            for c in {key(r) for r in a})
        comparisons[f"{after}_vs_{before}"] = item

    prefix_checks = {}
    for before, after, layers in (("five_selected", "depth7_epoch1", 5),
                                 ("five_selected", "depth6_epoch0", 5),
                                 ("depth6_epoch0", "depth6_epoch1", 5),
                                 ("depth6_epoch1", "depth7_epoch0", 6),
                                 ("depth7_epoch0", "depth7_epoch1", 6),
                                 ("depth6_epoch1", "depth7_epoch1", 6)):
        a, b = values[before]["rows"], values[after]["rows"]
        fields = ("error_energy", "activity_bce", "misses", "false_alarms")
        prefix_checks[f"{after}_vs_{before}"] = {
            f: max(abs(x["layer_metrics"][l][f] - y["layer_metrics"][l][f])
                   for x, y in zip(a, b) for l in range(layers)) for f in fields}

    sampled_gradients = {}
    for line in (RUN / "stdout_20261020_090048.log").open(encoding="utf-8"):
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if row.get("stage") != "PROGRESSIVE_RECEIVER_TRAINING":
            continue
        k = f"depth{row['depth']}_epoch{row['epoch']}"
        sampled_gradients.setdefault(k, []).append(row["gradient_norm"])
    gradient_stats = {k: dict(samples=len(v), preclip_quantiles=quantiles(v),
                              fraction_over_clip=float(np.mean(np.asarray(v) > 1)))
                      for k, v in sampled_gradients.items()}

    plan = read(PAIRED / "PLAN.json")
    assert math.isclose(SCALE, plan["scale"], rel_tol=1e-14)
    audit = read(PAIRED / "RESULT_AUDIT.json")
    assert digest(PAIRED / "PLAN.json") == audit["plan_sha256"]
    assert digest(PAIRED / "SUMMARY.json") == audit["summary_sha256"]
    assert digest(PAIRED / "per_scene.csv") == audit["per_scene_csv_sha256"]
    source = RUN / "source_code/experiments/lstmp_candidate_20261019"
    source_hashes = {str(p): digest(p) for p in (
        RUN / "MANIFEST.json", source / "extension.py", source / "receiver_base.py",
        source / "message_damping.py", RUN / "stdout_20261020_090048.log",
        RUN / "checkpoints/depth_6/COMPLETE.json",
        RUN / "checkpoints/depth_7/COMPLETE.json")}
    checks = {str(p): digest(p) == inputs[k]["sha256"] for k, p in paths.items()}
    assert all(checks.values())

    additional = {}
    for name in ("five_selected", "depth7_epoch1", "depth7_epoch2"):
        rows = values[name]["rows"]
        hard = summary([r for r in rows if r["condition"]["users"] == 100])
        total = all_summaries[name]
        outside = {}
        for r in rows:
            d = r["diagnostics"][-1]
            if d["out_of_pretraining_support"]:
                k = str(key(r) + ("low" if d["query_variance"] < 1e-3 else "high",))
                outside[k] = outside.get(k, 0) + 1
        q8 = []
        for snr in sorted({r["snr"] for r in rows}):
            group = [r for r in rows if r["condition"]["users"] == 100
                     and r["condition"]["frames"] == 8 and r["snr"] == snr]
            q8.append(dict(snr_db=snr, summary=summary(group),
                           negative_raw_residual_by_layer=[
                               sum(r["diagnostics"][i]["raw_residual_variance"] < 0
                                   for r in group)
                               for i in range(len(rows[0]["diagnostics"]))]))
        additional[name] = dict(
            k100_fraction_of_detection_errors=(hard["misses"] + hard["false_alarms"]) /
                (total["misses"] + total["false_alarms"]),
            k100_fraction_of_misses=hard["misses"] / total["misses"],
            final_query_outside_pretraining_by_condition=outside,
            k100_q8_by_snr=q8)
    delta = comparisons["depth7_epoch1_vs_five_selected"]["after_minus_before"]
    additional["five_to_seven_inactive_share_of_error_reduction"] = (
        delta["inactive_error_energy"] / delta["error_energy"])

    report = dict(
        schema="depth7-design-review-v1", inputs=inputs, source_hashes=source_hashes,
        summaries=all_summaries, comparisons=comparisons,
        loss_decomposition={k: decomposition(v) for k, v in values.items()},
        preserved_prefix_metric_max_abs=prefix_checks,
        sampled_training_gradients=gradient_stats, diagnostics=grouped_diagnostics,
        additional_diagnostics=additional,
        paired20=dict(condition=plan["condition"], summary=read(PAIRED / "SUMMARY.json"),
                      audit_status=audit["status"], source_audit_sha256=digest(PAIRED / "RESULT_AUDIT.json")),
        source_files_unchanged=checks,
        scope=dict(receiver_forwards=0, optimizer_updates=0, checkpoint_loads=0,
                   validation_scenes=1200, bootstrap_resamples=BOOTSTRAPS,
                   uncertainty="Descriptive stratified scene bootstrap on checkpoint-selection validation; not new test or training-seed uncertainty.",
                   active_error="Error of p*mu on truly active users, not error of conditional mean mu.",
                   variance_ratios="Realized scalar errors from truth used only for diagnosis; not exact posterior covariance or evidence a variance network is necessary.",
                   training_gradient="Sampled total preclip norms; no loss-specific or parameter-group gradients stored."))
    OUT.mkdir(parents=True, exist_ok=True)
    save(OUT / "ANALYSIS.json", report)
    csv_write(OUT / "stage_summary.csv", [dict(stage=k) | v for k, v in all_summaries.items()])
    csv_write(OUT / "condition_summary.csv", condition_rows)
    csv_write(OUT / "profile_summary.csv", profile_rows)
    csv_write(OUT / "layer_summary.csv", layer_rows)
    save(OUT / "PROVENANCE.json", dict(script=str(Path(__file__).resolve()),
                                     script_sha256=digest(Path(__file__)),
                                     output=str(OUT), inputs=inputs))
    print(json.dumps(dict(output=str(OUT), summaries=all_summaries,
                          comparisons=comparisons, prefix_checks=prefix_checks,
                          gradients=gradient_stats), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
