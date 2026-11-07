"""Check the scientific content and intended presentation changes against this revision's snapshot."""
from collections import Counter
from pathlib import Path
import difflib
import hashlib
import json
import re
import sys
from pypdf import PdfReader

RUN = Path(__file__).resolve().parent
PAPER = RUN.parents[1]
ROOT = PAPER.parents[1]
sys.path.insert(0, r"C:/Users/25911/.codex/skills/academic-research-suite/ars/scripts")
from pdf_read_preflight import run_preflight
baseline = json.loads((RUN / "BASELINE.json").read_text(encoding="utf-8"))

def read(p):
    return p.read_text(encoding="utf-8")

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def uncomment(t):
    return re.sub(r"(?<!\\)%[^\n]*", "", t)

def math(t):
    pattern = r"(?<!\\)\$.*?(?<!\\)\$|\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}.*?\\end\{\1\}"
    # A TeX line break immediately before $ is not an escaped dollar sign.
    prepared = uncomment(t).replace(r"\\", "\x01\x01")
    return [re.sub(r"\s+", "", m.group().replace("\x01\x01", r"\\")) for m in re.finditer(pattern, prepared, re.S)]

def cites(t):
    return Counter(k.strip() for group in re.findall(r"\\cite(?:\[[^\]]*\])*\{([^}]+)\}", uncomment(t)) for k in group.split(","))

def refs(t):
    return Counter(re.findall(r"\\(?:eqref|ref)\{([^}]+)\}", uncomment(t)))

def numbers(t):
    t = re.sub(r"\\cite(?:\[[^\]]*\])*\{[^}]+\}", "", uncomment(t))
    return re.findall(r"\d+", t)

active = ["main.tex"] + [p + ".tex" for p in baseline["active_inputs"]]
diffs, checks, old_join, new_join = [], {}, "", ""
for rel in active:
    old, new = read(RUN / "before" / rel), read(PAPER / rel)
    assert math(old) == math(new), (rel, "math changed")
    assert numbers(old) == numbers(new), (rel, "numerical tokens changed")
    assert re.findall(r"\\label\{([^}]+)\}", old) == re.findall(r"\\label\{([^}]+)\}", new)
    checks[rel] = {"math_spans_preserved": len(math(old)), "labels_preserved": True}
    old_join += old + "\n"
    new_join += new + "\n"
    diffs.append("".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile="before/"+rel, tofile=rel)))

old_cites, new_cites = cites(old_join), cites(new_join)
assert new_cites == old_cites + Counter({"neeser1993": 1})
assert refs(new_join) == refs(old_join) + Counter({"eq:first-loss": 1})
bib = read(PAPER / "references.bib")
assert bib.startswith(read(RUN / "before/references.bib"))
keys = re.findall(r"@\w+\s*\{\s*([^,\s]+)", bib)
assert len(keys) == len(set(keys))
assert set(new_cites).issubset(keys)
for acronym in ("MIMO", "GNN-ASPL", "NTN-TDL-D", "MSE"):
    assert len(re.findall(r"\b"+re.escape(acronym)+r"\b", old_join)) == len(re.findall(r"\b"+re.escape(acronym)+r"\b", new_join))
old_abs = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", old_join, re.S).group(1)
new_abs = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", new_join, re.S).group(1)
assert old_abs == new_abs
assert sha(PAPER / "sections/00_abstract_zh.md") == baseline["files"]["sections/00_abstract_zh.md"]

# Internal labels and filenames remain stable; they are not visible terminology.
visible = re.sub(r"\\(?:label|ref|eqref|input|includegraphics)(?:\[[^\]]*\])?\{[^}]*\}", "", uncomment(new_join))
for term in ("training queries", "query covariance", "covariance-weighted loss", "balanced binary cross-entropy",
             "frequency wrapping", "first-order network", "mean network", "channel network", "mean-network",
             "maximum channel delay spread", "Residual-delay support", "AFDM block length", "sub-carrier", "pre-compens"):
    assert term not in visible, term
assert not re.search(r"\b(?:terminal|terminals|user|users)\b", visible, re.I)
assert "first- and second-order score networks" in visible
for rel, expected in baseline["protected"].items():
    assert sha(ROOT / rel) == expected, (rel, "protected file changed")
unchanged_figures = []
for name in ("channel_denoising", "convergence", "snr_comparison", "pilot_frames"):
    rel = "figures/" + name + ".pdf"
    assert sha(PAPER / rel) == baseline["files"][rel]
    unchanged_figures.append(name)

pdf = PdfReader(PAPER / "main.pdf")
pages = [p.extract_text() for p in pdf.pages]
assert len(pages) == 15
plot_labels = {"user_count": ["Number of candidate devices"],
               "activity_probability": ["Nominal activity probability"],
               "cross_channel": ["NTN-TDL-"+p for p in "DABC"]}
for name, labels in plot_labels.items():
    text = "\n".join(p.extract_text() for p in PdfReader(PAPER / "figures" / (name + ".pdf")).pages)
    for label in labels:
        assert label in text, (name, label)
assert "Neeser" in "\n".join(pages) and "Proper complex random processes" in "\n".join(pages)
log_file = PAPER / "main.log"
if not log_file.exists():
    log_file = RUN / "main.log"
log = read(log_file)
for pattern in (r"Overfull", r"LaTeX Error", r"Citation .* undefined", r"Reference .* undefined", r"Missing character", r"multiply defined"):
    assert not re.search(pattern, log), pattern
preflights = []
for p in [PAPER / "main.pdf", RUN / "sources/neeser1993.pdf"] + [PAPER / "figures" / (n + ".pdf") for n in plot_labels]:
    result = run_preflight(p)
    assert result["verdict"] == "PASS", result
    preflights.append(result)

old_bib = read(RUN / "before/references.bib")
diffs.append("".join(difflib.unified_diff(old_bib.splitlines(True), bib.splitlines(True), fromfile="before/references.bib", tofile="references.bib")))
(RUN / "MANUSCRIPT.diff").write_text("\n".join(diffs), encoding="utf-8")
report = {"status": "PASS", "active_source_checks": checks,
          "math_spans_preserved_total": sum(c["math_spans_preserved"] for c in checks.values()),
          "citation_keys_before": len(old_cites), "citation_keys_after": len(new_cites), "new_citation": "neeser1993",
          "existing_citation_occurrences_preserved": True, "added_equation_reference": "eq:first-loss",
          "acronym_expansions_added": False, "abstracts_unchanged": True,
          "protected_file_count": len(baseline["protected"]), "other_four_figures_unchanged": unchanged_figures,
          "pdf_page_count": len(pages), "pdf_sha256": sha(PAPER / "main.pdf"),
          "preflights": preflights, "latex_serious_warnings": [],
          "underfull_hbox_count": len(re.findall(r"Underfull \\hbox", log)),
          "visual_review": "Recorded separately after inspection of rendered pages"}
(RUN / "VERIFICATION.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps({k: report[k] for k in ("status", "math_spans_preserved_total", "citation_keys_after", "protected_file_count", "pdf_page_count")}))
