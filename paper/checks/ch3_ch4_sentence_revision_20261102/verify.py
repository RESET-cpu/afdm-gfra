from pathlib import Path
import collections
import difflib
import hashlib
import json
import re
from pypdf import PdfReader

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
norm = lambda text: re.sub(r'\s+', '', text)
baseline = json.loads((RUN / 'BASELINE.json').read_text(encoding='utf-8-sig'))
targets = ['sections/03_bayesian_receiver_design.tex', 'sections/04_generative_priors.tex']
allowed = set(targets + ['main.pdf', 'README.md', 'docs/TERMINOLOGY.md'])
protected = {name: sha(ROOT / name) == value for name, value in baseline.items() if name not in allowed}
assert all(protected.values()), [p for p, same in protected.items() if not same]

result = {'protected_files_unchanged': protected, 'chapters': {}}
diffs = []
prose = []
for name in targets:
    old = (RUN / 'before' / name).read_text(encoding='utf-8')
    new = (ROOT / name).read_text(encoding='utf-8')
    environments = lambda s: re.findall(r'\\begin\{(equation|align|figure)\}(.*?)\\end\{\1\}', s, re.S)
    old_blocks, new_blocks = environments(old), environments(new)
    assert old_blocks == new_blocks, f'Math/figure changed: {name}'
    headings = lambda s: re.findall(r'\\(?:section|subsection|subsubsection|label)\{[^}]+\}', s)
    assert headings(old) == headings(new), f'Heading or label changed: {name}'
    cites = lambda s: re.findall(r'\\cite\w*(?:\[[^\]]*\])*\{[^}]+\}', s)
    # Source citations may be repositioned with their claims, but none may disappear.
    assert collections.Counter(cites(old)) == collections.Counter(cites(new)), f'Citation set changed: {name}'
    result['chapters'][name] = {'preserved_equation_labels': re.findall(r'\\label\{(eq:[^}]+)\}', new), 'math_and_figure_blocks_identical': True, 'headings_identical': True, 'citations_preserved': True}
    diffs.append(''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile='before/' + name, tofile=name)))
    plain = re.sub(r'\\begin\{(equation|align|figure)\}.*?\\end\{\1\}', '\n\n', new, flags=re.S)
    plain = re.sub(r'\$[^$]*\$', '', plain)
    plain = re.sub(r'\\(?:label|eqref|ref)\{[^}]*\}', '', plain)
    plain = re.sub(r'\\cite(?:\[[^\]]*\])*\{[^}]*\}', '', plain)
    prose.append(plain)
    assert not re.search(r'MFLE|GPJD|second-order\s+network|replac.{0,40}network', new, re.I)

def expand(path):
    src = re.sub(r'(?<!\\)%[^\n]*', '', path.read_text(encoding='utf-8'))
    def include(match):
        p = ROOT / match.group(1)
        return expand(p if p.suffix else p.with_suffix('.tex'))
    return re.sub(r'\\input\{([^}]+)\}', include, src)

active = expand(ROOT / 'main.tex')
labels = re.findall(r'\\label\{([^}]+)\}', active)
refs = re.findall(r'\\(?:eqref|ref|autoref)\{([^}]+)\}', active)
duplicates = [k for k, count in collections.Counter(labels).items() if count > 1]
missing_refs = sorted(set(refs) - set(labels))
bib_keys = set(re.findall(r'@\w+\s*\{\s*([^,]+)', (ROOT / 'references.bib').read_text(encoding='utf-8')))
cites = set()
for group in re.findall(r'\\cite\w*(?:\[[^\]]*\])*\{([^}]+)\}', active):
    cites.update(k.strip() for k in group.split(','))
assert not duplicates and not missing_refs and not (cites - bib_keys)
result.update({'duplicate_labels': duplicates, 'missing_references': missing_refs, 'missing_citations': sorted(cites - bib_keys)})

pdf = PdfReader(RUN / 'build/main.pdf')
log = (RUN / 'build/main.log').read_text(encoding='utf-8', errors='replace')
assert 'Overfull' not in log
assert not re.search(r'(?:Reference|Citation).*undefined|There were undefined references', log)
result.update({'pages': len(pdf.pages), 'overfull_boxes': False, 'build_pdf_sha256': sha(RUN / 'build/main.pdf'), 'current_pdf_sha256': sha(ROOT / 'main.pdf'), 'published_pdf_matches_build': sha(ROOT / 'main.pdf') == sha(RUN / 'build/main.pdf'), 'algorithm_or_experiment_changes': False})
(RUN / 'CHANGES.diff').write_text('\n'.join(diffs), encoding='utf-8')
(RUN / 'draft.md').write_text('\n\n'.join(prose), encoding='utf-8')
(RUN / 'VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'equation_count': sum(len(x['preserved_equation_labels']) for x in result['chapters'].values()), 'protected_files': len(protected), 'pages': len(pdf.pages), 'references_valid': True, 'published_pdf_matches_build': result['published_pdf_matches_build']}))
