"""Scoped structural/equation checks; semantic review is recorded separately."""
from pathlib import Path
import collections
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / 'paper/C-STMP'
RUN = Path(__file__).resolve().parent
CHAPTERS = ['03_bayesian_receiver_design', '04_generative_priors', '05_overall_algorithm']

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def equation_map(text):
    result = {}
    for match in re.finditer(r'\\begin\{(equation\*?|align\*?)\}(.*?)\\end\{\1\}', text, re.S):
        body = match.group(2)
        labels = re.findall(r'\\label\{([^}]+)\}', body)
        body = re.sub(r'\\label\{[^}]+\}', '', body)
        body = re.sub(r'%[^\n]*', '', body)
        body = re.sub(r'\s+', '', body)
        for label in labels:
            result[label] = body
    return result

baseline_eq = {}
current_eq = {}
for name in CHAPTERS:
    baseline_eq.update(equation_map((RUN/'baseline'/f'{name}.tex').read_text(encoding='utf-8')))
    current_eq.update(equation_map((PAPER/'sections'/f'{name}.tex').read_text(encoding='utf-8')))

main = (PAPER/'main.tex').read_text(encoding='utf-8')
active_main = re.sub(r'(?m)%.*$', '', main)
included = re.findall(r'\\input\{([^}]+)\}', active_main)
source = main + '\n' + '\n'.join((PAPER/(f+'.tex')).read_text(encoding='utf-8') for f in included)
source = re.sub(r'(?m)%.*$', '', source)
labels = re.findall(r'\\label\{([^}]+)\}', source)
refs = re.findall(r'\\(?:eqref|ref|autoref)\{([^}]+)\}', source)
cites = []
for value in re.findall(r'\\cite\w*(?:\[[^\]]*\]){0,2}\{([^}]+)\}', source):
    cites.extend(x.strip() for x in value.split(','))
bibkeys = set(re.findall(r'@\w+\s*\{\s*([^,]+),', (PAPER/'references.bib').read_text(encoding='utf-8')))
baseline = json.loads((RUN/'run_baseline.json').read_text(encoding='utf-8'))['hashes']
allowed = {f'paper/C-STMP/sections/{n}.tex' for n in CHAPTERS} | {'paper/C-STMP/docs/TERMINOLOGY.md'}
unexpected = [p for p,h in baseline.items() if p not in allowed and digest(ROOT/p) != h]
report = {
    'scope': 'structural checks and equation-text preservation, not a proof of semantic correctness',
    'baseline_equation_labels': len(baseline_eq),
    'current_equation_labels': len(current_eq),
    'equations_unchanged_ignoring_whitespace': sorted(k for k in baseline_eq if current_eq.get(k) == baseline_eq[k]),
    'equations_changed': sorted(k for k in baseline_eq if k in current_eq and current_eq[k] != baseline_eq[k]),
    'equations_missing': sorted(set(baseline_eq)-set(current_eq)),
    'equations_added': sorted(set(current_eq)-set(baseline_eq)),
    'missing_references': sorted(set(refs)-set(labels)),
    'duplicate_labels': sorted(k for k,v in collections.Counter(labels).items() if v > 1),
    'missing_citations': sorted(set(cites)-bibkeys),
    'unexpected_protected_changes': unexpected,
    'subsection_structure': {n: re.findall(r'\\subsection\{([^}]+)\}', (PAPER/'sections'/f'{n}.tex').read_text(encoding='utf-8')) for n in CHAPTERS},
    'final_chapter_hashes': {n:digest(PAPER/'sections'/f'{n}.tex') for n in CHAPTERS},
}
(RUN/'structural_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
