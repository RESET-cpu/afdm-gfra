"""Compare this compression with its saved baseline; no receiver experiments."""
from pathlib import Path
import difflib
import hashlib
import json
import re

CHECKS = Path(__file__).resolve().parent
PAPER = CHECKS.parents[1]
BEFORE = PAPER / "history/before_compression_20261022"


def read(path):
    return path.read_text(encoding="utf-8-sig")


def strip_comments(text):
    return re.sub(r"(?<!\\)%[^\n]*", "", text)


def active_source(root):
    seen = set()

    def expand(path):
        if path in seen:
            return ""
        seen.add(path)
        return re.sub(
            r"\\input\{([^}]+)\}",
            lambda m: expand(root / (m.group(1) + ".tex")),
            strip_comments(read(path)),
        )

    return expand(root / "main.tex")


def normalize_math(text):
    text = re.sub(r"\\label\{[^}]+\}", "", strip_comments(text))
    return re.sub(r"\s+", "", text)


def displays(text):
    pattern = r"\\begin\{(equation\*?|align\*?|gather\*?)\}(.*?)\\end\{\1\}"
    result = {}
    for match in re.finditer(pattern, text, re.S):
        for label in re.findall(r"\\label\{([^}]+)\}", match.group(2)):
            result[label] = normalize_math(match.group(2))
    return result


def prose(text):
    text = strip_comments(text)
    for environment in (r"figure\*?", "table", r"equation\*?", r"align\*?"):
        text = re.sub(
            r"\\begin\{" + environment + r"\}.*?\\end\{" + environment + r"\}",
            " ", text, flags=re.S,
        )
    text = re.sub(r"\\\[.*?\\\]|\$.*?\$", " ", text, flags=re.S)
    text = re.sub(r"\\(?:cite|eqref|ref|label|input)(?:\[[^\]]*\])?\{[^}]*\}", " ", text)
    text = re.sub(r"\\(?:sub)*section\{([^}]+)\}", r"\n\n## \1\n\n", text)
    text = re.sub(r"\\[A-Za-z]+(?:\[[^\]]*\])?", " ", text)
    text = text.replace("{", "").replace("}", "").replace("~", " ")
    return "\n\n".join(" ".join(p.split()) for p in text.split("\n\n") if p.strip())


old = active_source(BEFORE)
new = active_source(PAPER)
old_eq, new_eq = displays(old), displays(new)
removed = sorted(set(old_eq) - set(new_eq))
expected_removed = {
    "eq:activity-generation", "eq:continuous-basis", "eq:working-prior",
    "eq:twc-score-matching", "eq:twc-initialization", "eq:twc-final-output",
}
changed = sorted(k for k in set(old_eq) & set(new_eq) if old_eq[k] != new_eq[k])
assert set(removed) == expected_removed, removed
assert changed == ["eq:twc-factor-definitions"], changed
assert not set(new_eq) - set(old_eq)
old_unnumbered = [normalize_math(x) for x in re.findall(r"\\\[(.*?)\\\]", old, re.S)]
new_unnumbered = [normalize_math(x) for x in re.findall(r"\\\[(.*?)\\\]", new, re.S)]
assert old_unnumbered == new_unnumbered

# The activity factor was moved from its display to adjacent prose.
assert normalize_math(r"f_{\alpha,k}(\alpha_k)=\rho^{\alpha_k}(1-\rho)^{1-\alpha_k}") in normalize_math(new)
for formula in (
    r"\rho=p/[1-(1-p)^K]",
    r"[\mathbf B_d]_{tn}=\varphi_n(t-d)",
    r"\mathbf M_1=\mathbf0", r"w_1=w_{\rm ref}=\rho P_H",
    r"\widehat H_k^{\rm out}=s\widehat H_{k,L}",
    r"\widehat X_k^{\rm out}=s p_{kL}\widehat H_{k,L}",
    r"\widehat\alpha_k=\mathbf1\{p_{kL}\geq1/2\}",
):
    assert normalize_math(formula) in normalize_math(new), formula

labels = re.findall(r"\\label\{([^}]+)\}", new)
refs = re.findall(r"\\(?:eqref|ref)\{([^}]+)\}", new)
assert len(labels) == len(set(labels)), "Duplicate labels"
assert not set(refs) - set(labels), set(refs) - set(labels)
bibkeys = set(re.findall(r"@\w+\{([^,\s]+)", read(PAPER / "references.bib")))
citations = {key.strip() for group in re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}", new) for key in group.split(",")}
assert not citations - bibkeys
assert read(PAPER / "sections/01_introduction.tex").count(r"\item") == 3

unchanged = ["main.tex", "references.bib", "sections/00_abstract_zh.md",
             "sections/appendix_parameter_estimation.tex", "sections/06_simulation_results.tex",
             "sections/07_conclusion.tex", "figures/posterior_factor_graph.tex"]
for relative in unchanged:
    assert (PAPER / relative).read_bytes() == (BEFORE / relative).read_bytes(), relative
tikz = r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}"
assert re.findall(tikz, old, re.S) == re.findall(tikz, new, re.S)
table = r"\\begin\{tabular\}.*?\\end\{tabular\}"
assert re.findall(table, read(BEFORE / "sections/04_receiver_training.tex"), re.S) == re.findall(table, read(PAPER / "sections/04_receiver_training.tex"), re.S)

sections = [f"sections/{s}" for s in ["01_introduction.tex", "02_system_model.tex", "03_bayesian_receiver_design.tex", "04_receiver_training.tex", "05_unfolded_algorithm.tex"]]
counts = {}
diff = []
for relative in sections + ["sections/01_introduction_zh.md"]:
    before, after = read(BEFORE / relative), read(PAPER / relative)
    diff.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile="before/" + relative, tofile="after/" + relative))
    if relative.endswith(".tex"):
        counts[relative] = {
            "before": len(re.findall(r"\b[A-Za-z]+(?:[-'][A-Za-z]+)*\b", prose(before))),
            "after": len(re.findall(r"\b[A-Za-z]+(?:[-'][A-Za-z]+)*\b", prose(after))),
        }
(CHECKS / "revision.diff").write_text("".join(diff), encoding="utf8")
abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", new, re.S).group(1)
plain = "# Abstract\n\n" + prose(abstract) + "\n\n# Main Text\n\n" + "\n\n".join(prose(read(PAPER / x)) for x in sections)
(CHECKS / "prose_for_acronym_check.md").write_text(plain + "\n", encoding="utf8")

summary = {
    "scope": "Source-preservation and editorial compression checks; no experiment or receiver-performance result",
    "status": "PASS",
    "numbered_equation_labels_before": len(old_eq),
    "numbered_equation_labels_after": len(new_eq),
    "unchanged_numbered_equation_labels": len(set(old_eq) & set(new_eq)) - len(changed),
    "removed_display_labels_accounted_for": removed,
    "display_with_definition_moved_inline": changed,
    "unnumbered_displays_unchanged": len(old_unnumbered),
    "missing_references": [], "duplicate_labels": [], "citation_keys_resolved": len(citations),
    "contribution_count": 3, "diagram_geometry_unchanged": True,
    "network_configuration_table_unchanged": True,
    "unchanged_files": unchanged,
    "abstract_status": "unchanged; not regenerated",
    "prose_word_counts_exclude_math_floats_and_commands": counts,
    "source_sha256": {x: hashlib.sha256((PAPER / x).read_bytes()).hexdigest() for x in sections + unchanged + ["sections/01_introduction_zh.md"]},
}
(CHECKS / "source_validation.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
print(json.dumps({k: v for k, v in summary.items() if k not in {"source_sha256", "unchanged_files"}}, ensure_ascii=False, indent=2))
