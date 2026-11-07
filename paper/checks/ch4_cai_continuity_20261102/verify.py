from pathlib import Path
import collections
import difflib
import hashlib
import json
import re
import numpy as np
from pypdf import PdfReader

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = (RUN / 'before/sections/04_generative_priors.tex').read_text(encoding='utf-8')
after = (ROOT / 'sections/04_generative_priors.tex').read_text(encoding='utf-8')

def equations(text):
    result = {}
    for block in re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}', text, re.S):
        label = re.search(r'\\label\{([^}]+)\}', block).group(1)
        result[label] = re.sub(r'\s+', '', block)
    return result

old_eq, new_eq = equations(before), equations(after)
assert len(old_eq) == 9
assert all(new_eq.get(k) == v for k, v in old_eq.items())
added = sorted(set(new_eq) - set(old_eq))
assert added == sorted(['eq:tweedie-covariance', 'eq:score-matching-objective', 'eq:denoising-score-objective'])

baseline = json.loads((RUN / 'BASELINE.json').read_text(encoding='utf-8-sig'))
allowed = {'main.pdf', 'README.md', 'docs/TERMINOLOGY.md', 'sections/04_generative_priors.tex'}
protected = {p: sha(ROOT / p) == value for p, value in baseline.items() if p not in allowed}
assert all(protected.values())

def expand(path):
    src = re.sub(r'(?<!\\)%[^\n]*', '', path.read_text(encoding='utf-8'))
    def include(match):
        child = ROOT / match.group(1)
        return expand(child if child.suffix else child.with_suffix('.tex'))
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
missing_cites = sorted(cites - bib_keys)
assert not duplicates and not missing_refs and not missing_cites
assert not re.search(r'MFLE|GPJD|STMP|second-order\s+network|replac.{0,40}network|without training an additional network', after, re.I)

# Deterministic identities with noncommuting covariance matrices.
rng = np.random.default_rng(20261102)
n = 8
D = n // 2
factor_k, factor_s = rng.normal(size=(n, n)), rng.normal(size=(n, n))
K = factor_k @ factor_k.T + 1.3 * np.eye(n)
Sigma = factor_s @ factor_s.T + 0.7 * np.eye(n)
Sinv, Tinv = np.linalg.inv(Sigma), np.linalg.inv(K + Sigma)
P = np.linalg.inv(np.linalg.inv(K) + Sinv)
J = K @ Tinv
cov_error = max(np.linalg.norm(P - J @ Sigma), np.linalg.norm(P - (Sigma - Sigma @ Tinv @ Sigma))) / np.linalg.norm(P)
u, h, f = rng.normal(size=(3, n))
score = Sinv @ (f - u)
dsm_residual = score + Sinv @ (u - h)
mean_loss = (f - h) @ Sinv @ (f - h) / n
dsm_loss = dsm_residual @ Sigma @ dsm_residual / n
reparam_error = abs(mean_loss - dsm_loss) / max(1., abs(mean_loss))
constant = np.trace(Sigma @ (Sinv - Tinv)) / n
constant_errors = []
for B in [np.zeros((n, n)), -Tinv, rng.normal(size=(n, n))]:
    A = B + Tinv
    l_sm = np.trace(Sigma @ A @ (K + Sigma) @ A.T) / n
    G = B + Sinv
    l_dsm = np.trace(Sigma @ (B @ K @ B.T + G @ Sigma @ G.T)) / n
    constant_errors.append(float(abs(l_dsm - l_sm - constant)))
assert cov_error < 1e-12 and reparam_error < 1e-12 and max(constant_errors) < 1e-10

pdf = PdfReader(RUN / 'build/main.pdf')
assert len(pdf.pages) == 14
for i in range(4, 9):
    (RUN / f'preview/page-{i + 1:02d}.txt').write_text(pdf.pages[i].extract_text(), encoding='utf-8')
log = (RUN / 'build/main.log').read_text(encoding='utf-8', errors='replace')
assert 'Overfull' not in log
assert not re.search(r'(?:Reference|Citation).*undefined|There were undefined references', log)

prose = re.sub(r'\\begin\{equation\}.*?\\end\{equation\}', '', after, flags=re.S)
prose = re.sub(r'\$[^$]*\$', '', prose)
prose = re.sub(r'\\(?:label|eqref|ref)\{[^}]*\}', '', prose)
prose = re.sub(r'\\cite(?:\[[^\]]*\])*\{[^}]*\}', '', prose)
(RUN / 'chapter4_prose.txt').write_text(prose, encoding='utf-8')
(RUN / 'CHANGES.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='before/sections/04_generative_priors.tex', tofile='sections/04_generative_priors.tex')), encoding='utf-8')

result = {
    'original_equations_preserved': sorted(old_eq),
    'added_equations': added,
    'protected_files_unchanged': protected,
    'duplicate_labels': duplicates,
    'missing_references': missing_refs,
    'missing_citations': missing_cites,
    'replacement_narrative_absent_in_chapter4': True,
    'deterministic_formula_checks': {
        'covariance_relative_error': float(cov_error),
        'mean_parameterization_relative_error': float(reparam_error),
        'sm_dsm_constant_absolute_errors': constant_errors,
        'covariances_commutator_norm': float(np.linalg.norm(K @ Sigma - Sigma @ K)),
    },
    'pages': len(pdf.pages),
    'chapter4_pages': [5, 6, 7],
    'visually_reviewed_pages': [5, 6, 7, 8, 9],
    'visual_review': 'No clipping, overlap, or missing text. Page 9 has larger vertical spacing around the training covariance formula; experiment source is unchanged.',
    'overfull_boxes': False,
    'chapter4_layout_warnings': False,
    'remaining_layout_warnings': 'Underfull boxes in simulation results, appendix, and bibliography; no undefined references or citations.',
    'build_pdf_sha256': sha(RUN / 'build/main.pdf'),
    'current_pdf_sha256': sha(ROOT / 'main.pdf'),
    'published_pdf_matches_build': sha(ROOT / 'main.pdf') == sha(RUN / 'build/main.pdf'),
    'training_or_performance_experiments_run': False,
    'abstract_regenerated': False,
}
(RUN / 'VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: result[k] for k in ['added_equations', 'pages', 'deterministic_formula_checks', 'published_pdf_matches_build']}, ensure_ascii=False))
print(f'Preserved {len(old_eq)} equations and {len(protected)} protected files; labels and citations valid.')
