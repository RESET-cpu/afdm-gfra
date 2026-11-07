"""Validate manuscript identities and saved evidence; no receiver/training runs."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import numpy as np
from pypdf import PdfReader

RUN = Path(__file__).resolve().parent
PAPER = RUN.parents[1]
ROOT = PAPER.parents[1]

def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def text(p):
    return Path(p).read_text(encoding='utf-8-sig')

protected = json.loads(text(RUN / 'protected_files_before.json'))
for item in protected:
    assert digest(item['Path']).upper() == item['Hash'], item['Path']

changes = []
old_math_count = 0
math_re = r'\\begin\{(equation\*?|align\*?|gather\*?)\}[\s\S]*?\\end\{\1\}'
for before in sorted((RUN / 'before').rglob('*')):
    if not before.is_file():
        continue
    relative = before.relative_to(RUN / 'before')
    old, new = text(before), text(PAPER / relative)
    changes.extend(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
        fromfile='before/' + relative.as_posix(), tofile=relative.as_posix()))
    if before.suffix == '.tex':
        for match in re.finditer(math_re, old):
            assert match.group() in new, (relative, match.group()[:70])
            old_math_count += 1

ch6 = text(PAPER / 'sections/06_simulation_results.tex')
old6 = text(RUN / 'before/sections/06_simulation_results.tex')
for env in ('table', 'figure'):
    pattern = rf'\\begin\{{{env}\}}[\s\S]*?\\end\{{{env}\}}'
    assert re.findall(pattern, ch6) == re.findall(pattern, old6), env
assert ch6.count('\\includegraphics') == 7

# Execute only the established read-only numeric assertions, stopping before
# its historical snapshots, layout assumptions, or report-writing code.
previous = PAPER / 'checks/ch6_revision_20261103/validate_revision.py'
numeric_source = text(previous).split('# Actual 500-scene stopping statistics')[0]
numeric_source = numeric_source.replace('import pymupdf as fitz', '')
namespace = {'__file__': str(previous), '__name__': 'numeric_evidence_recheck'}
exec(compile(numeric_source, str(previous), 'exec'), namespace)

summary_path = ROOT / ('result/snr_comparison/data/c_stmp_ablation_1000_20261028/'
                      'phase_only_20261029/GAUSSIAN_RETAINED_SUMMARY.json')
summary = json.loads(text(summary_path))
assert summary['paired_conditions'] == 354 * 6 == 2124
for record in (summary['paired_known'], summary['paired']['gaussian_evidence']):
    assert abs((record['misses'] + record['false_alarms']) / (2124 * 40)
               - record['aer']) < 1e-14
assert summary['paired']['gaussian_evidence']['nonconverged'] == 724

# Deterministic linear algebra checks of the newly written derivations.
rng = np.random.default_rng(20261103)
N, L, M, G, QO = 16, 7, 16, 336, 3
def dft(n):
    ix = np.arange(n)
    return np.exp(-2j*np.pi*np.outer(ix, ix)/n) / np.sqrt(n)
FN, FL = dft(N), dft(L)
X = rng.normal(size=(N, L)) + 1j*rng.normal(size=(N, L))
direct = FN.conj().T @ (FN @ X @ FL.conj().T)
reduced = X @ FL.conj().T
cancellation_error = np.linalg.norm(direct-reduced) / np.linalg.norm(reduced)
assert cancellation_error < 5e-13

c1, c2 = 7/32, 1/320
ix = np.arange(N)
lambda1 = np.diag(np.exp(-2j*np.pi*c1*ix**2))
lambda2 = np.diag(np.exp(-2j*np.pi*c2*ix**2))
A = lambda2 @ FN @ lambda1
explicit = np.exp(-2j*np.pi*(c2*ix[:,None]**2 +
                ix[:,None]*ix[None,:]/N + c1*ix[None,:]**2)) / np.sqrt(N)
idaft_error = np.linalg.norm(A-explicit) / np.linalg.norm(explicit)
assert idaft_error < 5e-13

Ts = 1/(N*30000)
Tframe = (N+G)*Ts
nu = 17345.67
b = np.arange(L)
Pi = np.exp(-2j*np.pi*(b-L*Tframe*nu)[:,None]*np.arange(L)/L).sum(axis=1)/np.sqrt(L)
position = np.exp(2j*np.pi*nu*ix*Ts)
a = np.exp(1j*rng.normal(size=M))
gains = rng.normal(size=4) + 1j*rng.normal(size=4)
delays = np.array([3,19,45,100]) % N
full = np.zeros((M,L,N,N), dtype=complex)
h = np.zeros(N, dtype=complex)
for gain, delay in zip(gains, delays):
    full[:,:,delay,:] += (gain * a[:,None,None] * Pi[None,:,None]
                         * position[None,None,:] / np.sqrt(L))
    h[delay] += gain
factored = (a[:,None,None,None] * Pi[None,:,None,None] *
            h[None,None,:,None] * position[None,None,None,:] / np.sqrt(L))
factor_error = np.linalg.norm(full-factored) / np.linalg.norm(full)
assert factor_error < 5e-13
assert L*QO*(N+G) == QO*L*(N+G)
assert M*N*N == 4096 and M*L*N*N == 28672

included = re.findall(r'^\\input\{([^}]+)\}', text(PAPER / 'main.tex'), re.M)
manuscript = text(PAPER / 'main.tex') + '\n'.join(text(PAPER / (p+'.tex')) for p in included)
bib = text(PAPER / 'references.bib')
keys = set(re.findall(r'@\w+\s*\{\s*([^,]+),', bib))
citations = set()
for match in re.finditer(r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}', manuscript):
    citations.update(k.strip() for k in match[1].split(','))
assert citations <= keys, citations-keys
labels = re.findall(r'\\label\{([^}]+)\}', manuscript)
assert len(labels) == len(set(labels)), 'duplicate labels'
refs = set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', manuscript))
assert refs <= set(labels), refs-set(labels)
log = text(PAPER / 'main.log')
assert not re.search(r'undefined references|Citation .+ undefined|Reference .+ undefined|multiply defined|Overfull', log, re.I)

pdf = PdfReader(PAPER / 'main.pdf')
for page in pdf.pages:
    assert float(page.mediabox.width) == 612 and float(page.mediabox.height) == 792
    assert len(page.extract_text().strip()) > 100
aux = text(PAPER / 'main.aux')
aux = re.sub(r'\\mbox\s*\{([^{}]+)\}', r'\1', aux)
locations = {}
for label in ('sec:afdm-otfs-comparison','tab:afdm-otfs-representation','sec:complexity',
              'sec:receiver-settings','tab:activity-evidence','app:afdm-model',
              'app:otfs-comparison','app:modulation-comparison','app:receiver-configurations'):
    match = re.search(r'\\newlabel\{'+re.escape(label)+r'\}\{\{([^}]+)\}\{([^}]+)\}', aux)
    assert match, label
    locations[label] = {'number':match[1], 'page':int(match[2])}

(RUN / 'CHANGES.diff').write_text(''.join(changes), encoding='utf-8')
result = {
    'status':'PASS', 'existing_equation_blocks_preserved':old_math_count,
    'protected_files_unchanged':len(protected), 'experimental_tables_and_figures_unchanged':True,
    'saved_numeric_claims_checked':len(namespace['checks']),
    'otfs_transform_relative_error':float(cancellation_error),
    'idaft_factorization_relative_error':float(idaft_error),
    'common_doppler_factorization_relative_error':float(factor_error),
    'pages':len(pdf.pages), 'labels':locations, 'undefined_references':False,
    'overfull_boxes':False, 'abstract_regenerated':False,
    'new_receiver_runs':0, 'training_runs':0,
    'evidence_summary_sha256':digest(summary_path),
    'numeric_checker_sha256':digest(previous), 'pdf_sha256':digest(PAPER / 'main.pdf'),
    'visual_inspection':'Recorded separately in REVISION_NOTES.md; not certified by this script.',
}
(RUN / 'VALIDATION.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
