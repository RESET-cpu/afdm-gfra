"""Scoped, read-only validation of the prose streamlining sources.

Writes only STATIC_VALIDATION.json next to this script. Does not compile,
execute algorithms, inspect experimental values, or modify canonical files.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
PAPER = HERE.parent.parent
BEFORE = HERE / "before"
CHAPTERS = [
    "02_system_model.tex",
    "03_bayesian_receiver_design.tex",
    "04_generative_priors.tex",
    "05_overall_algorithm.tex",
    "06_simulation_results.tex",
]
IMPLEMENTATION = "appendix_implementation.tex"
checks: list[dict] = []


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def uncomment(text: str) -> str:
    # The manuscript uses ordinary TeX comments, not verbatim environments.
    return re.sub(r"(?<!\\)%[^\n]*", "", text)


def compact(text: str) -> str:
    return re.sub(r"\s+", "", uncomment(text))


def check(name: str, passed: bool, **details) -> None:
    checks.append({"check": name, "status": "PASS" if passed else "FAIL", **details})


def active_graph(root: Path) -> dict[str, str]:
    files: dict[str, str] = {}

    def visit(rel: str) -> None:
        if rel in files:
            raise ValueError(f"Repeated source input: {rel}")
        text = uncomment(read(root / rel))
        files[rel] = text
        for name in re.findall(r"\\(?:input|include)\{([^}]+)\}", text):
            target = name if name.endswith(".tex") else name + ".tex"
            visit(target)

    visit("main.tex")
    return files


def display_blocks(text: str, rel: str) -> list[dict]:
    # Capture top-level numbered displays and unnumbered \[...\] displays.
    pattern = re.compile(
        r"\\begin\{(?P<env>equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}"
        r".*?\\end\{(?P=env)\}|\\\[.*?\\\]",
        re.S,
    )
    blocks = []
    for match in pattern.finditer(uncomment(text)):
        body = match.group(0)
        labels = re.findall(r"\\label\{([^}]+)\}", body)
        blocks.append({
            "path": rel,
            "environment": match.group("env") or "bracket-display",
            "labels": labels,
            "normalized": compact(body),
        })
    return blocks


baseline = json.loads(read(HERE / "baseline.json"))
old_files = active_graph(BEFORE)
new_files = active_graph(PAPER)
old_scope = {f"sections/{name}": old_files[f"sections/{name}"] for name in CHAPTERS}
new_scope = {f"sections/{name}": new_files[f"sections/{name}"] for name in CHAPTERS}
new_scope[f"sections/{IMPLEMENTATION}"] = new_files[f"sections/{IMPLEMENTATION}"]

old_blocks = [block for path, text in old_scope.items() for block in display_blocks(text, path)]
new_blocks = [block for path, text in new_scope.items() for block in display_blocks(text, path)]
old_counts = Counter(block["normalized"] for block in old_blocks)
new_counts = Counter(block["normalized"] for block in new_blocks)
check(
    "All original II-VI displayed mathematics preserved in II-VI plus D",
    old_counts == new_counts,
    original_total=len(old_blocks), current_total=len(new_blocks),
    original_numbered_environments=sum(block["environment"] != "bracket-display" for block in old_blocks),
    current_numbered_environments=sum(block["environment"] != "bracket-display" for block in new_blocks),
    removed_or_changed=sum((old_counts - new_counts).values()),
    added_or_changed=sum((new_counts - old_counts).values()),
)

equation_preservation = []
for original in old_blocks:
    matches = [item for item in new_blocks if item["normalized"] == original["normalized"]]
    equation_preservation.append({
        "labels": original["labels"], "old_path": original["path"],
        "current_paths": [item["path"] for item in matches],
        "status": "PASS" if matches else "FAIL",
    })

def labels_in(files: dict[str, str]) -> dict[str, list[str]]:
    result = defaultdict(list)
    for path, text in files.items():
        for label in re.findall(r"\\label\{([^}]+)\}", text):
            result[label].append(path)
    return dict(result)

old_labels = labels_in(old_files)
new_labels = labels_in(new_files)
missing_labels = sorted(set(old_labels) - set(new_labels))
duplicates = {key: value for key, value in new_labels.items() if len(value) != 1}
check("All original active manuscript labels retained", not missing_labels,
      original_label_count=len(old_labels), current_label_count=len(new_labels), missing=missing_labels)
check("All active manuscript labels are unique", not duplicates, duplicates=duplicates)

refs = []
for path, text in new_files.items():
    for match in re.finditer(r"\\(?:eqref|ref|autoref|cref|Cref)\*?\{([^}]+)\}", text):
        for label in match.group(1).split(","):
            refs.append({"path": path, "label": label.strip()})
unresolved = [item for item in refs if item["label"] not in new_labels]
check("All active cross-references have source labels", not unresolved,
      reference_count=len(refs), unresolved=unresolved)

bib_keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", read(PAPER / "references.bib")))
cites = []
for path, text in new_files.items():
    for match in re.finditer(r"\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}", text):
        cites.extend({"path": path, "key": key.strip()} for key in match.group(1).split(","))
missing_cites = [item for item in cites if item["key"] not in bib_keys]
check("All active citation keys exist", not missing_cites,
      citation_occurrences=len(cites), missing=missing_cites)

protected = []
mutable = {f"sections/{name}" for name in CHAPTERS} | {"main.tex", "main.pdf"}
for entry in baseline:
    if entry["path"] not in mutable:
        actual = digest(PAPER / entry["path"])
        protected.append({"path": entry["path"], "baseline_sha256": entry["sha256"],
                          "current_sha256": actual, "unchanged": actual == entry["sha256"]})
check("Protected baseline assets unchanged byte-for-byte", all(item["unchanged"] for item in protected),
      protected_count=len(protected), changed=[item["path"] for item in protected if not item["unchanged"]])
required_protected = {"sections/01_introduction.tex", "references.bib",
                      "sections/appendix_parameter_estimation.tex",
                      "sections/appendix_afdm_channel_model.tex",
                      "sections/appendix_evaluation_protocol.tex"}
figures = [item["path"] for item in protected if item["path"].startswith("figures/")]
check("Requested I, A-B-C, references and seven figures are covered",
      required_protected <= {item["path"] for item in protected} and len(figures) == 7,
      figure_paths=figures)

main = new_files["main.tex"]
appendix_inputs = re.findall(r"\\input\{(sections/appendix_[^}]+)\}", main)
check("Implementation appendix is active Appendix D",
      appendix_inputs == ["sections/appendix_parameter_estimation",
                          "sections/appendix_afdm_channel_model",
                          "sections/appendix_evaluation_protocol",
                          "sections/appendix_implementation"],
      appendix_order=appendix_inputs)

ch2 = new_scope["sections/02_system_model.tex"]
ch3 = new_scope["sections/03_bayesian_receiver_design.tex"]
ch4 = new_scope["sections/04_generative_priors.tex"]
ch5 = new_scope["sections/05_overall_algorithm.tex"]
app = new_scope[f"sections/{IMPLEMENTATION}"]

check("SVD and stopping equation labels migrated exactly once to D",
      all(new_labels.get(label) == [f"sections/{IMPLEMENTATION}"]
          for label in ["eq:linear-fraction", "eq:variance-stopping"]))
check("Algorithm 1 does not span main and appendix equation numbers",
      r"\eqref{eq:linear-mean}--\eqref{eq:linear-fraction}" not in ch5
      and r"\eqref{eq:linear-mean}--\eqref{eq:linear-extrinsic}" in ch5
      and r"SVD implementation in Appendix~\ref{app:implementation}" in ch5)
check("Chapter II keeps path waveform and frame timing interfaces",
      all(compact(item) in compact(ch2) for item in [
          "$g$ of the transmission block", "$n$th AFDM basis waveform with its CPP",
          "corresponds to $g=N_{\\rm CPP}$", "$g_q=N_{\\rm CPP}+q(N+N_{\\rm CPP})$.",
          r"\label{eq:working-posterior}", r"\label{eq:targets}"]))
check("Chapter III keeps GPJD variance bridge and site acceptance",
      all(compact(item) in compact(ch3) for item in [
          r"$v=\kappa\bar v$", r"$\bar v$ is the damped linear variance",
          "lies within the training range and $0<\\tau<v$", "Otherwise, the previous site is retained."]))
check("Chapter IV preserves complete fixed-covariance derivative evaluation",
      all(compact(item) in compact(ch4) for item in [
          "Both perturbed evaluations hold $C$ fixed", "including its skip and",
          "preconditioning terms."]))
check("Chapter IV retains classifier sampling and optimum qualifications",
      all(compact(item) in compact(ch4) for item in [
          "$v$ follows the same sampling law for both classes.",
          "The channel network remains fixed during classifier training",
          "At the population optimum over unrestricted logits",
          "The trained classifier approximates this ideal logit."]))
check("Algorithm 1 preserves current network input even when site is retained",
      all(compact(item) in compact(ch5) for item in [
          r"and $z_\phi(R_k,v,F_k)$", r"if $\tau<v$, and otherwise retain them.",
          r"Obtain $p_k$ by \eqref{eq:activity-probability}."]))
check("Algorithm 1 preserves current variance while computing next ratio",
      all(compact(item) in compact(ch5) for item in [
          r"$v^{(i)}=\kappa^{(i)}\bar v^{(i)}$ fixed throughout the current",
          r"Compute $\kappa^{(i+1)}$", r"using $v^{(i)}$",
          r"new-message weight $\eta\in(0,1]$"]))
check("Algorithm 1 preserves out-of-range fallback and first-iteration initialization",
      all(compact(item) in compact(ch5) for item in [
          "Otherwise, retain the sites and obtain $p_k$ from",
          r"\eqref{eq:gaussian-evidence}",
          r"$\bar v^{(1)}=v_{\rm L}^{(1)}$", "The first input and feedback messages are used without damping."]))
check("Appendix D retains SVD equivalent extrinsic mean",
      all(compact(item) in compact(app) for item in [
          r"$\widehat{\mathbf A}=\mathbf U\diag(s_i)\mathbf V^{\mathsf H}$",
          r"+(\mathbf X_{\rm L}-\mathbf X^{\rm pri})/f_{\rm L}$"]))
check("Appendix D retains derivative and classifier input settings",
      all(compact(item) in compact(app) for item in [
          r"$\sqrt{2/(1+v)}$", r"normalized by $Dv$", "sign-preserving",
          r"$L_z=1$", r"$\delta=10^{-2}$", "one random sign vector per terminal reused",
          r"$\tau_{\min}=10^{-4}$"]))
check("Appendix D retains stopping state, acceptance and both window criteria",
      all(compact(item) in compact(app) for item in [
          "The site check requires accepted updates with stable precision",
          r"$w_k^{(0)}=\rho$", "This history is used only for stopping.",
          r"each hold for $L_s$ consecutive iterations", r"unchanged for $L_d$ consecutive",
          r"$I_{\max}$"]))

bindings = [{"path": path, "sha256": digest(PAPER / path)} for path in new_files]
report = {
    "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "scope": "Static preservation and independent method-flow review of II-VI plus implementation appendix D",
    "not_in_scope": ["PDF compilation/layout", "recomputing experimental statistics", "new theory or algorithm validation"],
    "check_count": len(checks),
    "failed_check_count": sum(item["status"] == "FAIL" for item in checks),
    "checks": checks,
    "equation_preservation": equation_preservation,
    "protected_assets": protected,
    "source_bindings": bindings,
    "independent_read_review": {
        "status": "PASS",
        "chapters_read": ["II", "III", "IV", "V", "Appendix B", "Appendix D"],
        "method": "Compared actual before/after II-V source diffs and read the resulting chapters and implementation appendix together.",
        "findings": [
            "The weighted-denoising to score-matching argument in IV loses only an intermediate algebraic expansion; the score definition, target, covariance weighting and population qualifications remain.",
            "Mean, fixed-covariance derivative, pooled variance, activity classifier, retained-site conditional moments, extrinsic feedback and next-iteration variance ratio remain connected by formulas and Algorithm 1.",
            "Classifier-current-output and next-iteration variance behavior are explicit in Algorithm 1 after duplicate prose is removed.",
            "SVD implementation, finite-difference settings, classifier features and stopping details are restored in Appendix D with their original definitions.",
            "The complexity formulas and pass-count definitions remain unchanged; removed specializations and subordinate arithmetic remarks do not alter the stated bound.",
            "No required correction or newly strengthened empirical/theoretical claim was found in this scoped edit review."
        ],
    },
}
(HERE / "STATIC_VALIDATION.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": report["status"], "checks": len(checks),
                  "failed": [item for item in checks if item["status"] != "PASS"],
                  "displayed_math_before": len(old_blocks), "displayed_math_after": len(new_blocks),
                  "protected_assets": len(protected)}, ensure_ascii=False, indent=2))
raise SystemExit(0 if report["status"] == "PASS" else 1)
