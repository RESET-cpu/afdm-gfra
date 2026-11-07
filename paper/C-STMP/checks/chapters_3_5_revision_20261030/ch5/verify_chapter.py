"""Assemble the reviewed Chapter V and perform text-level preservation checks."""
from pathlib import Path
from collections import Counter
import difflib
import hashlib
import json
import re

here = Path(__file__).resolve().parent
paper = here.parents[2]
parts = [here / name for name in (
    '00_chapter_opening.tex', 'a_overall_algorithm.tex', 'b_complexity.tex')]
reviewed = '\n\n'.join(p.read_text(encoding='utf-8').strip() for p in parts) + '\n'
target = here / 'chapter_reviewed.tex'
target.write_text(reviewed, encoding='utf-8')
before = (here / '05_overall_algorithm.before.tex').read_text(encoding='utf-8')

def equations(text):
    found = {}
    for m in re.finditer(r'\\begin\{equation\}(.*?)\\end\{equation\}', text, re.S):
        labels = re.findall(r'\\label\{([^}]+)\}', m.group(1))
        for label in labels:
            found[label] = re.sub(r'\s+', '', m.group(0))
    return found

old_eq, new_eq = equations(before), equations(reviewed)
equation_comparison = {key: old_eq[key] == new_eq.get(key) for key in old_eq}
all_tex = []
main = (paper / 'main.tex').read_text(encoding='utf-8')
# Read only active input statements; this check is not a TeX parser or compiler.
for rel in re.findall(r'^\\input\{([^}]+)\}', main, re.M):
    path = paper / (rel + '.tex')
    all_tex.append(reviewed if path.name == '05_overall_algorithm.tex'
                   else path.read_text(encoding='utf-8'))
combined = main + '\n' + '\n'.join(all_tex)
labels = re.findall(r'\\label\{([^}]+)\}', combined)
refs = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', reviewed)
bib = (paper / 'references.bib').read_text(encoding='utf-8')
bibkeys = set(re.findall(r'@\w+\s*\{\s*([^,\s]+)', bib))
citekeys = set()
for group in re.findall(r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}', reviewed):
    citekeys.update(k.strip() for k in group.split(','))
baseline = json.loads((here / 'baseline.json').read_text(encoding='utf-8'))
workspace = paper.parents[1]
protected = {}
for relative, expected in baseline['sources'].items():
    if relative.startswith('src/') or relative.endswith('06_simulation_results.tex'):
        actual = hashlib.sha256((workspace / relative).read_bytes()).hexdigest()
        protected[relative] = actual == expected
result = {
    'scope': 'Chapter-lead text and source preservation checks; root owns compilation and rendering',
    'subsections': re.findall(r'\\subsection\{([^}]+)\}', reviewed),
    'extra_subsubsections': bool(re.search(r'\\subsubsection', reviewed)),
    'equation_count_before': len(old_eq),
    'equation_count_after': len(new_eq),
    'equations_unchanged_ignoring_whitespace': equation_comparison,
    'added_equation_labels': sorted(set(new_eq) - set(old_eq)),
    'compatibility_labels': {x: labels.count(x) for x in (
        'sec:overall', 'sec:schedule', 'sec:frontend', 'sec:damping')},
    'duplicate_labels_in_combined_manuscript': sorted(x for x, n in Counter(labels).items() if n > 1),
    'unresolved_refs_in_chapter': sorted(set(refs) - set(labels)),
    'missing_citation_keys': sorted(citekeys - bibkeys),
    'old_MP_abbreviation_in_chapter': bool(re.search(r'\bMP\b', reviewed)),
    'protected_code_and_VI_unchanged': protected,
    'reviewed_draft_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
    'initial_draft_records_present': all((here / x).exists() for x in (
        'a_overall_algorithm.initial.tex', 'a_sources.initial.md',
        'b_complexity.initial.tex', 'b_sources.initial.md')),
    'compile_run': False,
    'experiment_or_training_run': False,
    'complexity_convention': 'Standard dense operations; products of three matrices evaluated pairwise. Unchanged NumPy optimize=False whitening einsum adds an implementation-level O(M^4) cost; recorded separately.',
}
checks = [
    result['subsections'] == ['Overall Algorithm', 'Computational Complexity Analysis'],
    not result['extra_subsubsections'], len(old_eq) == len(new_eq) == 6,
    all(equation_comparison.values()), not result['added_equation_labels'],
    all(n == 1 for n in result['compatibility_labels'].values()),
    not result['duplicate_labels_in_combined_manuscript'],
    not result['unresolved_refs_in_chapter'], not result['missing_citation_keys'],
    not result['old_MP_abbreviation_in_chapter'], all(protected.values()),
    result['initial_draft_records_present'],
]
result['text_checks_pass'] = all(checks)
(here / 'verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
(here / 'chapter5.diff').write_text(''.join(difflib.unified_diff(
    before.splitlines(True), reviewed.splitlines(True),
    fromfile='05_overall_algorithm.before.tex', tofile='chapter_reviewed.tex')), encoding='utf-8')
print(json.dumps(result, indent=2))
if not result['text_checks_pass']:
    raise SystemExit('Chapter V text verification failed')
