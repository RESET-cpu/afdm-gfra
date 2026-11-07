"""Read-only manuscript checks for the abstract and Sections I-V review."""
from pathlib import Path
import hashlib
import json
import re
from collections import Counter

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / 'paper/C-STMP'
OUT = Path(__file__).resolve().parent

def read(path):
    return path.read_text(encoding='utf-8-sig')

def clean(text):
    return re.sub(r'(?<!\\)%[^\n]*', '', text)

main = read(PAPER / 'main.tex')
abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', main, re.S).group(1)
notation = main[main.index(r'\noindent\textit{Notation:}'):main.index(r'\input{sections/02_system_model}')]
sections = [PAPER / 'sections' / name for name in (
    '01_introduction.tex', '02_system_model.tex', '03_bayesian_receiver_design.tex',
    '04_generative_priors.tex', '05_overall_algorithm.tex')]
scope = [(PAPER / 'main.tex', abstract, 48), (PAPER / 'main.tex', notation, 84)]
scope += [(p, read(p), 1) for p in sections]

all_sources = [(PAPER / 'main.tex', main)] + [
    (p, read(p)) for p in sorted((PAPER / 'sections').glob('*.tex'))
    if p.name != 'appendix_second_order_training.tex'
]
all_text = '\n'.join(clean(t) for _, t in all_sources)
labels = re.findall(r'\\label\{([^}]+)\}', all_text)
scope_text = '\n'.join(clean(t) for _, t, _ in scope)
refs = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', scope_text)
citations = []
for group in re.findall(r'\\cite(?:\[[^\]]*\])*\{([^}]+)\}', scope_text):
    citations += [k.strip() for k in group.split(',')]
bib_keys = set(re.findall(r'@\w+\{([^,]+),', read(PAPER / 'references.bib')))
aux = read(PAPER / 'main.aux')
equations = {k: num for k, num in re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}', aux) if k.startswith('eq:')}
scope_equations = [equations[k] for k in re.findall(r'\\label\{(eq:[^}]+)\}', scope_text)]

reviewer_terms = [
    'innovative', 'pioneering', 'revolutionary paradigm', 'transformative framework',
    'superior', 'surpass', 'excel', 'remarkable', 'unprecedented', 'achieves SOTA',
    'breakthrough performance', 'general-purpose', 'is capable of', 'notably', 'yet',
    'yielding', 'at its essence', 'encompass', 'differentiate', 'reveal', 'underscore',
    'exhibit superior capability', 'exceed', 'pave the way for', 'highlight the potential of',
    'profound challenges', 'stems from', 'rigid', 'impede'
]
humanizer_patterns = {
    'staged_contrast': r'\b(?:not just|not only|not merely|rather than|this is not|this isn.t)\b',
    'staged_opening': r'\b(?:let.s dive|let.s explore|at its core|the real question|to be clear)\b',
    'inflation': r'\b(?:pivotal|crucial|groundbreaking|revolutionary|unprecedented|delve|tapestry)\b',
    'stacked_hedges': r'\b(?:could potentially|might arguably|may possibly)\b',
    'draft_residue': r'\b(?:I hope this helps|great question|let me know|would you like)\b',
}
hits = []
for p, t, start in scope:
    t = clean(t)
    # Normalize line wrapping while preserving source-line attribution.
    chunks = t.splitlines(keepends=True)
    joined = ' '.join(x.rstrip('\r\n') for x in chunks)
    offsets = []
    pos = 0
    for j, chunk in enumerate(chunks):
        offsets.append((pos, start + j))
        pos += len(chunk.rstrip('\r\n')) + 1
    checks = [('reviewer_word', term, re.escape(term)) for term in reviewer_terms]
    checks += [('humanizer_structure', key, pattern) for key, pattern in humanizer_patterns.items()]
    checks += [('sentence_dash', 'em_dash', r'—|---')]
    for kind, term, pattern in checks:
        for match in re.finditer(pattern, joined, re.I):
            line = max((ln for offset, ln in offsets if offset <= match.start()), default=start)
            hits.append({'kind': kind, 'term': term, 'path': p.relative_to(ROOT).as_posix(),
                         'line': line, 'context': joined[max(0, match.start()-70):match.end()+80]})

pdfs = {}
for name in ('main.pdf', 'main_full.pdf'):
    reader = PdfReader(PAPER / name)
    pdfs[name] = {'pages': len(reader.pages)}
    if name == 'main.pdf':
        text = '\n'.join(page.extract_text() or '' for page in reader.pages[:8])
        (OUT / 'pages_1_to_8.txt').write_text(text, encoding='utf-8')
        pdfs[name]['reviewed_pages'] = list(range(1, 9))
        pdfs[name]['page_8_scope'] = 'Section V-C only; Section VI is outside this review.'
        pdfs[name]['current_name_visible'] = 'GP-MP-C' in text
        pdfs[name]['old_ccd_name_visible'] = 'GP-MP-CCD' in text

figures = {}
for name in ('system_multiframe.pdf', 'factor_graph.pdf', 'learned_receiver.pdf'):
    reader = PdfReader(PAPER / 'figures' / name)
    figures[name] = {'pages': len(reader.pages), 'embedded_images': sum(len(page.images) for page in reader.pages)}

logs = {}
for name in ('main.log', 'main_full.log'):
    logs[name] = [line for line in read(PAPER / name).splitlines()
                  if re.search(r'undefined|multiply defined|Overfull|Underfull|PDF inclusion|PDF version', line, re.I)]

before = json.loads(read(OUT / 'BEFORE_HASHES.json'))
changed = []
for item in before:
    path = Path(item['Path'])
    if hashlib.sha256(path.read_bytes()).hexdigest().upper() != item['Hash']:
        changed.append(str(path))

result = {
    'date': '2026-11-04',
    'skills': ['pre-submission-reviewer', 'humanizer'],
    'scope': 'English abstract, Notation, Sections I-V, Figures 1-3, Algorithm 1',
    'sources': [p.relative_to(ROOT).as_posix() for p, _, _ in scope],
    'abstract_words_whitespace': len(abstract.split()),
    'undefined_reference_labels': sorted(set(refs)-set(labels)),
    'undefined_citation_keys': sorted(set(citations)-bib_keys),
    'duplicate_labels': [k for k, count in Counter(labels).items() if count > 1],
    'scope_equation_numbers': scope_equations,
    'scope_equations_contiguous_1_to_40': scope_equations == [str(n) for n in range(1, 41)],
    'bibliography_item_count': len(re.findall(r'\\bibitem(?:\[[^\]]*\])?\{', read(PAPER / 'main.bbl'))),
    'mechanical_scan_hits': hits,
    'scan_interpretation': 'Candidate matching only; substantive humanizer review also read every paragraph.',
    'pdfs': pdfs, 'figures': figures, 'existing_compile_log_messages': logs,
    'protected_asset_count': len(before), 'changed_protected_assets': changed,
    'new_compilation': False, 'new_receiver_experiments_or_training': False,
    'formula_review': 'Read current formulas and source-provenance records; no rerun of historical algebra tests.',
}
(OUT / 'CHECKS.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
