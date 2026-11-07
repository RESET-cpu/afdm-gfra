"""Recompute VI claims from saved data and verify retained disclosures.

No training, inference, compilation, or PDF inspection is performed.
Select the staged candidate or applied canonical source explicitly.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[3]
PAPER = ROOT / "paper/C-STMP"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--source", choices=["staged", "canonical"], required=True)
parser.add_argument("--output", default="NUMERICAL_VERIFICATION.json")
args = parser.parse_args()
checks = []

def read(path):
    return path.read_text(encoding="utf-8")

def load(path):
    return json.loads(read(path))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check(name, passed, **evidence):
    checks.append({"name": name, "passed": bool(passed), **evidence})

def close(name, actual, expected, tolerance=0.005):
    check(name, abs(actual - expected) < tolerance,
          actual=actual, reported=expected, tolerance=tolerance)

baseline = {entry["path"]: entry for entry in load(RUN / "baseline.json")}
source = (RUN / "staged/06_simulation_results.tex" if args.source == "staged"
          else PAPER / "sections/06_simulation_results.tex")
implementation_source = (RUN / "staged/appendix_implementation.tex" if args.source == "staged"
                         else PAPER / "sections/appendix_implementation.tex")
appendix_source = PAPER / "sections/appendix_evaluation_protocol.tex"
before_path = RUN / "before/sections/06_simulation_results.tex"
before = read(before_path)
current = read(source)
appendix = read(appendix_source)
implementation = read(implementation_source)
compact = re.sub(r"\s+", " ", current)
app_compact = re.sub(r"\s+", " ", appendix)
implementation_compact = re.sub(r"\s+", " ", implementation)
check("before_vi_matches_this_revision_baseline",
      sha(before_path) == baseline["sections/06_simulation_results.tex"]["sha256"])

# Only Appendix C and the seven figure files are protected here. Other
# chapters are being intentionally streamlined and are outside this script.
protected = ["sections/appendix_evaluation_protocol.tex"] + sorted(
    path for path in baseline if path.startswith("figures/"))
check("protected_inventory", len(protected) == 8, paths=protected)
for rel in protected:
    actual = sha(PAPER / rel)
    check("unchanged:" + rel, actual == baseline[rel]["sha256"], sha256=actual)

equation_pattern = r"\\begin\{equation\}.*?\\end\{equation\}"
old_equations = re.findall(equation_pattern, before, re.S)
new_equations = re.findall(equation_pattern, current, re.S)
check("five_numbered_equations_unchanged", len(old_equations) == 5
      and old_equations == new_equations, count=len(old_equations))
for name, pattern in [
    ("parameter_table", r"\\begin\{table\}.*?\\end\{table\}"),
    ("figure_commands", r"\\includegraphics(?:\[[^\]]*\])?\{[^}]+\}"),
    ("labels", r"\\label\{[^}]+\}"),
    ("citations", r"\\cite(?:\[[^\]]*\])?\{[^}]+\}"),
]:
    a, b = re.findall(pattern, before, re.S), re.findall(pattern, current, re.S)
    check(name + "_unchanged", a == b, before_count=len(a), after_count=len(b))
check("appendix_c_included", "\\input{sections/appendix_evaluation_protocol}"
      in read(PAPER / "main.tex"))
check("implementation_label_available", "\\label{app:implementation}" in implementation)
if args.source == "canonical":
    check("appendix_d_included", "\\input{sections/appendix_implementation}"
          in read(PAPER / "main.tex"))

paths = {
    "convergence": "result/snr_comparison/figures/convergence_current_paper_20261026/PLOT_DATA.json",
    "snr": "result/snr_comparison/figures/full_grid_final_20261026/PLOT_DATA.json",
    "pilot": "result/pilot_frames/figures/full_grid_final_20261026/PLOT_DATA.json",
    "users": "result/user_count/figures/redraw_beta01_500_20261028/PLOT_DATA.json",
    "activity": "result/activity_probability/figures/stmp_c_stmp_500_20261026/PLOT_DATA.json",
    "cross": "result/cross_channel/figures/full_500_paper_20261028/PLOT_DATA.json",
    "denoising": "result/channel_denoising/figures/narrow_paper_20261026/PLOT_DATA.json",
}
data = {key: load(ROOT / path) for key, path in paths.items()}


def row(dataset, method, **conditions):
    candidates = [r for r in data[dataset]["rows"] if r["method"] == method
                  and all(r.get(k, r.get("parameters", {}).get(k)) == v
                          for k, v in conditions.items())]
    if len(candidates) != 1:
        raise ValueError((dataset, method, conditions, len(candidates)))
    return candidates[0]


def nmse(dataset, method, **conditions):
    return row(dataset, method, **conditions)["nmse_db"]


def gap(dataset, competitor, **conditions):
    return (nmse(dataset, competitor, **conditions)
            - nmse(dataset, "C_STMP", **conditions))


close("denoising_colored_at_0", nmse("denoising", "pretrained_colored_first", snr_db=0), -17.98)
close("denoising_gaussian_at_0", nmse("denoising", "gaussian", snr_db=0), -2.98)
close("denoising_colored_gain_at_minus10",
      nmse("denoising", "proposed", snr_db=-10)
      - nmse("denoising", "pretrained_colored_first", snr_db=-10), 2.11)
check("denoising_awgn_better_at_high_snr", all(
    nmse("denoising", "proposed", snr_db=x)
    < nmse("denoising", "pretrained_colored_first", snr_db=x)
    for x in [10, 20, 30]))
for method, end, value in [("C_STMP", 60, -13.85), ("STMP", 85, -11.79)]:
    close("convergence_final_" + method,
          nmse("convergence", method, iteration=end), value)
    check("convergence_initial_increase_" + method,
          nmse("convergence", method, iteration=2)
          > nmse("convergence", method, iteration=1))
distance = (nmse("convergence", "C_STMP", iteration=30)
            - nmse("convergence", "C_STMP", iteration=60))
check("approximately_30_iterations_near_final", 0 <= distance < 0.1,
      distance_to_final_db=distance,
      note="0.1 dB is a descriptive proximity check, not a stopping criterion.")
for x, target in [(-4, 1.87), (6, 0.41)]:
    close(f"snr_gain_over_stmp_{x}", gap("snr", "STMP", snr_db=x), target)
check("snr_gap_over_offgrid_widens",
      gap("snr", "offgrid_sbl", snr_db=-4) < gap("snr", "offgrid_sbl", snr_db=6),
      endpoint_gaps=[gap("snr", "offgrid_sbl", snr_db=x) for x in [-4, 6]])
a, b = row("snr", "C_STMP", snr_db=0), row("snr", "STMP", snr_db=0)
close("snr_aer_relative_reduction_percent", 100 * (1 - a["aer"] / b["aer"]), 47, 0.5)
check("aer_improvement_mainly_fewer_misses",
      (a["misses"], a["false_alarms"], b["misses"], b["false_alarms"])
      == (42, 1, 81, 0),
      proposed=[a["misses"], a["false_alarms"]], stmp=[b["misses"], b["false_alarms"]])
a, o = row("snr", "C_STMP", snr_db=-4), row("snr", "offgrid_sbl", snr_db=-4)
check("minus4_aer_nmse_rankings_differ", o["aer"] < a["aer"] and o["nmse_db"] > a["nmse_db"])
for q, value in [(16, 1.57), (48, 0.51)]:
    close(f"pilot_gain_over_stmp_{q}", gap("pilot", "STMP", frames=q), value)
pilot_targets = {}
for method, expected in [("C_STMP", 24), ("STMP", 32)]:
    q = min(r["frames"] for r in data["pilot"]["rows"]
            if r["method"] == method and r["nmse_db"] <= -14)
    pilot_targets[method] = q
    check("pilot_first_grid_point_below_minus14_" + method, q == expected, frames=q)
close("pilot_frame_reduction_percent", 100 * (1 - pilot_targets["C_STMP"] / pilot_targets["STMP"]), 25)
check("pilot_aer_equal_at_48", row("pilot", "C_STMP", frames=48)["aer"]
      == row("pilot", "STMP", frames=48)["aer"] == 0.0001)
for method, expected in [("C_STMP", 2), ("STMP", 462)]:
    r = row("pilot", method, frames=8)
    check("pilot_q8_cap_count_" + method,
          r["stopping_reasons"].get("MAX_ITERATIONS", 0) == expected,
          cap_count=r["stopping_reasons"].get("MAX_ITERATIONS", 0))
check("pilot_all_q16_or_more_converged", all(
    r["convergence_rate"] == 1 for r in data["pilot"]["rows"]
    if r["method"] in ["C_STMP", "STMP"] and r["frames"] >= 16))
for method, expected in [("C_STMP", 80), ("STMP", 40)]:
    k = max(r["users"] for r in data["users"]["rows"]
            if r["method"] == method and r["nmse_db"] <= -10)
    check("largest_tested_k_at_minus10_" + method, k == expected, users=k)
close("user100_gain_over_offgrid", gap("users", "offgrid_sbl", users=100), 2.53)
for p, value in [(0.05, 1.07), (0.25, 2.25)]:
    close(f"activity_gain_over_stmp_{p}", gap("activity", "STMP", activity_probability=p), value)
close("activity025_gain_over_offgrid", gap("activity", "offgrid_sbl", activity_probability=0.25), 2.15)
check("activity025_offgrid_better_than_stmp", nmse("activity", "offgrid_sbl", activity_probability=.25)
      < nmse("activity", "STMP", activity_probability=.25))
cross_gaps = [gap("cross", "STMP", channel_model=c, snr_db=0) for c in "DABC"]
close("cross_zero_min_gain", min(cross_gaps), 1.02)
close("cross_zero_max_gain", max(cross_gaps), 1.60)
for c, value in [("A", .39), ("B", .58)]:
    close("cross_stmp_gain_at_6_" + c, -gap("cross", "STMP", channel_model=c, snr_db=6), value)
check("cross_b_at4_nearly_equal", abs(gap("cross", "STMP", channel_model="B", snr_db=4)) < .01,
      gap_db=gap("cross", "STMP", channel_model="B", snr_db=4))
check("cross_d_c_proposed_always_better", all(gap("cross", "STMP", channel_model=c, snr_db=s) > 0
      for c in "DC" for s in [-4, -2, 0, 2, 4, 6]))
check("cross_all_sparse_methods_worse", all(gap("cross", m, channel_model=c, snr_db=s) > 0
      for m in ["offgrid_sbl", "gnn", "gamp", "somp"] for c in "DABC" for s in [-4, -2, 0, 2, 4, 6]))
check("cross_without_retraining", data["cross"]["training_runs"] == 0, training_runs=data["cross"]["training_runs"])

claimed_tokens = [
    "$-17.98$~dB", "$-2.98$~dB", "$2.11$~dB", "approximately $30$ iterations",
    "$-13.85$ and $-11.79$~dB", "$1.87$~dB at $-4$~dB to $0.41$~dB at $6$~dB",
    "$47\\%$", "$1.57$~dB at $Q=16$ to $0.51$~dB at $Q=48$",
    "$24$ frames", "$32$ with STMP", "$25\\%$ reduction", "$462$ of $500$",
    "$80$ and $40$ for GP-CCD-MP-DRE and STMP", "$2.53$~dB advantage",
    "$1.07$~dB at $p=0.05$ to $2.25$~dB at $p=0.25$", "$2.15$~dB advantage",
    "$1.02$ to $1.60$~dB", "$0.39$ and $0.58$~dB",
]
check("verified_representative_values_are_current_text",
      all(token in compact for token in claimed_tokens),
      missing_tokens=[token for token in claimed_tokens if token not in compact])

# Retained disclosure: check specific statements, not just the existence of an appendix.
disclosures = {
    "development_overlap": ["Development and baseline-threshold selection overlap the evaluation scenes", "reused without refitting"],
    "snr_selection": ["SNR range was narrowed after interim inspection", "$8$ and $10$~dB results remain archived"],
    "diagnostic_reuse": ["$12$-input diagnostic", "All $12$ diagnostic inputs are included"],
    "original_stmp_failures": ["$498$, $479$, and $500$", "those outputs remain archived"],
    "current_stmp_failures": ["$3$ and $14$", "These $17$ outputs are retained"],
    "selected_single_scene_replacement": ["only scene~372", "this selected replacement is used in the reported panel", "Other $K=80$ scenes retain weight $0.4$"],
    "full_k100_adjustment": ["from $0.4$ to $0.2$ for all $K=100$ scenes after preliminary inspection"],
    "retrospective_not_independent": ["retrospective parameter development, rather than independent validation"],
    "all_finite_retained": ["All finite outputs enter the reported metrics", "All finite nonconverged outputs remain in both NMSE and AER"],
    "activity_counts": ["All $2{,}500$", "one scene at each of $p=0.20$ and $0.25$"],
    "cross_counts_and_reuse": ["all $12{,}000$", "profile-D outputs are reused", "after matching inputs and configurations"],
    "cross_scope": ["without retraining", "does not introduce a full time-varying Doppler-spectrum model"],
}
for name, snippets in disclosures.items():
    check("disclosure:" + name, all(s in app_compact for s in snippets), required_text=snippets)
check("nonempty_activity_condition_retained", "conditioned on at least one active terminal" in compact
      and "$\\rho=p/[1-(1-p)^K]$" in compact)
check("main_protocol_points_to_appendix", "Appendix~\\ref{app:evaluation-protocol}" in compact)
check("all_user_cap_counts_match_appendix", [row("users", "STMP", users=k)["stopping_reasons"].get("MAX_ITERATIONS", 0)
      for k in [20, 40, 60, 80, 100]] == [0, 0, 0, 3, 14])
check("activity_cap_counts_match_appendix", [row("activity", "STMP", activity_probability=p)["stopping_reasons"].get("MAX_ITERATIONS", 0)
      for p in [.05, .1, .15, .2, .25]] == [0, 0, 0, 1, 1])
check("activity_proposed_all_converged", all(r["convergence_rate"] == 1 for r in data["activity"]["rows"] if r["method"] == "C_STMP"))
check("cross_learned_receivers_all_converged", all(r["convergence_rate"] == 1 for r in data["cross"]["rows"] if r["method"] in ["STMP", "C_STMP"]))

# This is a fresh file-hash comparison, not a copied status from the earlier audit.
data_baseline_path = PAPER / "checks/experiment_analysis_20261030/baseline.json"
data_baseline = load(data_baseline_path)
data_bindings = {}
for key, rel in paths.items():
    actual = sha(ROOT / rel)
    check("frozen_data_unchanged:" + key, actual == data_baseline[rel]["sha256"],
          path=rel, sha256=actual)
    data_bindings[key] = {"path": rel, "sha256": actual}

main_disclosures = {
    "retrospective_design": ["These are retrospective comparisons:",
        "baseline threshold development overlaps evaluation scenes",
        "damping settings selected after preliminary evaluation"],
    "finite_outputs": ["All finite outputs, including those reaching the iteration limit, enter the reported metrics"],
    "native_minimum": ["imposed minimum of $60$ iterations, compared with $85$ for STMP"],
    "q8_context": ["$462$ of $500$ runs reaching the iteration limit, compared with two",
        "pilot-saving comparison above uses $Q\\geq16$"],
    "pilot_energy_and_grid": ["at fixed per-frame pilot energy", "on the evaluated grid"],
    "snr_counterexample": ["off-grid SBL has slightly lower AER but substantially higher NMSE"],
    "denoising_counterexample": ["white-noise training performs better at high SNR", "genie retains a substantial advantage"],
    "cross_counterexample": ["STMP is better by $0.39$ and $0.58$~dB on A and B"],
    "candidate_grid_scope": ["largest tested candidate populations", "evaluated configuration accommodates"],
}
for name, snippets in main_disclosures.items():
    check("main_text:" + name, all(s in compact for s in snippets),
          missing=[s for s in snippets if s not in compact])
check("finite_outputs_statement_consolidated", compact.count("All finite outputs") == 1)
check("protocol_reference_consolidated", compact.count("ref{app:evaluation-protocol}") == 2)
check("implementation_reference_resolves", "ref{app:implementation}" in compact
      and "\\label{app:implementation}" in implementation)
implementation_tokens = [
    "$s=0.2647966453$", "epoch $200$", "epoch $90$",
    "$L_z=1$", "$\\delta=10^{-2}$", "one random sign vector per terminal reused",
    "$\\tau_{\\min}=10^{-4}$", "$I_{\\min}=60$", "$I_{\\max}=600$",
    "activity-change, site-parameter, and activity-history tolerances are $10^{-3}$, $0.1$, and $10^{-3}$",
    "$\\zeta=0.2$", "$L_s=5$", "$L_d=10$",
]
check("moved_vi_implementation_parameters_retained",
      all(s in implementation_compact for s in implementation_tokens),
      missing=[s for s in implementation_tokens if s not in implementation_compact])
training_tokens = ["$50{,}000$ and $5{,}000$", "two sets use disjoint scenes",
                   "batch size of $64$", "Training lasts $200$ epochs",
                   "minimum fixed-noise validation loss", "$100$ epochs",
                   "checkpoint selected by validation"]
check("training_budget_and_selection_retained", all(s in compact for s in training_tokens),
      missing=[s for s in training_tokens if s not in compact])

inspected_sources = [source, appendix_source, implementation_source]
report = {
    "status": "PASS" if all(c["passed"] for c in checks) else "FAIL",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "source_mode": args.source,
    "scope": "Fresh recomputation of representative Chapter VI numerical claims from seven saved plot datasets; source-preservation checks for VI equations/table/figures/citations, unchanged Appendix C and seven figure files, text checks of retained disclosures and moved VI implementation constants. No other-chapter audit, experiments, training, PDF compilation or visual inspection.",
    "checks_count": len(checks), "checks": checks,
    "current_baseline": {"path": str((RUN / "baseline.json").relative_to(ROOT)).replace("\\", "/"),
                         "sha256": sha(RUN / "baseline.json"), "protected_paths_checked": protected},
    "historical_data_hash_source": {"path": str(data_baseline_path.relative_to(ROOT)).replace("\\", "/"),
                                    "sha256": sha(data_baseline_path),
                                    "use": "Only the seven saved dataset hashes are reused; every comparison and numerical check is executed in this run."},
    "data_sources": data_bindings,
    "inspected_prose_sha256": {
        str(p.relative_to(ROOT)).replace("\\", "/"): sha(p) for p in inspected_sources
    },
    "manual_review": "No manual PASS is generated by this script. Narrative causal-scope review is provided separately by the reviewing agent.",
    "training_started": False, "inference_started": False,
    "canonical_files_written": False, "final_pdf_hash_bound": False,
}
output = RUN / args.output
if output.resolve().parent != RUN:
    raise ValueError("Output must remain directly in this revision directory")
output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"status": report["status"], "source_mode": args.source,
                  "checks": len(checks), "report": str(output),
                  "failures": [c["name"] for c in checks if not c["passed"]]}, ensure_ascii=False))
raise SystemExit(0 if report["status"] == "PASS" else 1)
