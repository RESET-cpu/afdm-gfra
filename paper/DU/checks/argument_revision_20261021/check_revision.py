"""Check the manuscript revision without loading data or training a receiver."""
from pathlib import Path
import hashlib
import json
import re
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BEFORE = ROOT / "history/before_argument_revision_20261021"
section_names = ["02_system_model", "03_bayesian_receiver_design",
                 "04_receiver_training", "05_unfolded_algorithm"]

def read(path):
    return path.read_text(encoding="utf-8-sig")

def equations(text):
    result = {}
    for match in re.finditer(r"\\begin\{(equation|align|gather)\}(.*?)\\end\{\1\}", text, re.S):
        block = re.sub(r"\s+", "", match.group(0))
        for label in re.findall(r"\\label\{([^}]+)\}", match.group(0)):
            result[label] = block
    return result

counts, preserved, added = {}, [], []
for name in section_names:
    old = equations(read(BEFORE / "sections" / (name + ".tex")))
    new = equations(read(ROOT / "sections" / (name + ".tex")))
    assert all(label in new and new[label] == block for label, block in old.items()), name
    preserved.extend(old)
    added.extend(sorted(new.keys() - old.keys()))
    counts[name] = len(new)
assert added == ["eq:twc-frame-channel"], added
assert (BEFORE / "references.bib").read_bytes() == (ROOT / "references.bib").read_bytes()
old_main, main = read(BEFORE / "main.tex"), read(ROOT / "main.tex")
abstract_pattern = r"\\begin\{abstract\}.*?\\end\{abstract\}"
assert re.search(abstract_pattern, old_main, re.S).group() == re.search(abstract_pattern, main, re.S).group()

# Check the new frame relation against the continuous-delay path construction.
rng = np.random.default_rng(20261021)
N, prefix, c1, c2, ts = 16, 33, 3 / 32, np.sqrt(2) / 7, 1 / 240000
t = np.arange(N)
F = np.exp(-2j*np.pi*(c2*t[:, None]**2 + t[:, None]*t/N + c1*t**2))/np.sqrt(N)
delay = np.array([.37, 17.8, 31.2])
gains = rng.normal(size=3) + 1j*rng.normal(size=3)
frame_errors = []
for nu in [-37000., -121.2, 0., 40800.]:
    beta = (2*np.pi*nu*(N+prefix)*ts + np.pi) % (2*np.pi) - np.pi
    def channel(frame):
        result = np.zeros((N, N), complex)
        phase = np.exp(2j*np.pi*nu*ts*(prefix + frame*(N+prefix) + t))
        for d, gain in zip(delay, gains):
            w = (t-d) % N
            zeta = np.floor(2*c1*w[:, None] + t/N)
            B = np.exp(2j*np.pi*(c2*t**2 + c1*(t[:, None]-d)**2
                        + w[:, None]*t/N - zeta*w[:, None]))/np.sqrt(N)
            result += gain * (F @ (phase[:, None]*B))
        return result
    reference = channel(0)
    for frame in [0, 1, 3, 11]:
        frame_errors.append(float(np.linalg.norm(channel(frame)-np.exp(1j*frame*beta)*reference)
                                  / np.linalg.norm(reference)))
assert max(frame_errors) < 1e-11

counts["appendix_parameter_estimation"] = len(equations(read(ROOT / "sections/appendix_parameter_estimation.tex")))
report = {
    "status": "PASS", "preserved_numbered_equations_II_V": len(preserved),
    "added_equations": added, "equation_counts": counts,
    "total_numbered_equations": sum(counts.values()),
    "frame_relation_max_relative_error": max(frame_errors),
    "abstract_unchanged": True, "bibliography_unchanged": True,
    "training_or_performance_experiments_run": False,
    "source_sha256": {name: hashlib.sha256((ROOT / "sections" / (name + ".tex")).read_bytes()).hexdigest()
                      for name in section_names},
}
(HERE / "revision_validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

# Save a prose-only body for the advisory acronym checker. Math and floats
# are excluded; this report is not a check of the abstract or figure labels.
inputs = re.findall(r"\\input\{([^}]+)\}", re.sub(r"(?<!\\)%.*", "", main))
body = "\n\n".join(read(ROOT / (item + ".tex")) for item in inputs)
body = re.sub(r"(?<!\\)%.*", "", body)
for env in ["figure", "table", "equation", "align", "gather"]:
    body = re.sub(r"\\begin\{" + env + r"\*?\}.*?\\end\{" + env + r"\*?\}", "", body, flags=re.S)
body = re.sub(r"\\\[.*?\\\]", "", body, flags=re.S)
body = re.sub(r"\$[^$]*\$", "", body, flags=re.S)
body = re.sub(r"\\(?:label|eqref|ref|cite)\{[^}]*\}", "", body)
body = re.sub(r"\\(?:section|subsection|subsubsection)\{([^}]+)\}", r"\n# \1\n", body)
body = re.sub(r"\\(?:textit|textbf|emph|noindent)\b", "", body)
body = body.replace("~", " ").replace("{", "").replace("}", "")
(HERE / "body_for_acronym_check.txt").write_text(body, encoding="utf-8")
print(json.dumps(report, indent=2))
