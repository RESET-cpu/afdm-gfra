"""Compare the saved manuscript with the notation revision and render the PDF."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import sys

RUN = Path(__file__).resolve().parent
PAPER = RUN.parents[1]
sys.path.append(str(Path.home() / '.cache/codex-pymupdf'))
import pymupdf as fitz
from PIL import Image, ImageDraw
import numpy as np

def read(path):
    return path.read_text(encoding='utf-8').replace('\r\n', '\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def normalize(text, name):
    text = text.replace(r'\mathrm j', 'j')
    if name.startswith(('04_', '05_', '06_')):
        text = text.replace(r'\mathbf C', 'C')
        text = text.replace(r'\mathbf R_{\rm a}', r'R_{\rm a}')
        text = text.replace(r'\mathbf R_{\rm c}', r'R_{\rm c}')
    text = text.replace(r'\delta_{\rm FD}', r'\delta')
    text = text.replace(r'(\tau^{\rm post})^{-1}', r'\tau^{-1}')
    text = text.replace(r'\tau^{\rm post}', r'\tau')
    text = text.replace(r'\zeta_{\rm hist}', r'\zeta')
    if name == '05_overall_algorithm.tex':
        text = text.replace(r'\sum_{a=1}^{Q}', r'\sum_i').replace('s_a^2', 's_i^2')
    if name == '06_simulation_results.tex':
        text = text.replace(r'\mathbf R_{\rm corr}', 'R')
        text = text.replace(r'\mathbf Z_{\rm tr}', 'G')
        text = text.replace(r'\xi_{\rm corr}', r'\xi')
        text = text.replace(r'\sum_{e\in\mathcal T}', r'\sum_{i\in\mathcal T}')
        for token in ('X', 'H', r'\alpha'):
            text = text.replace(token+'_{ek}', token+'_{ik}')
    if name == 'appendix_parameter_estimation.tex':
        text = text.replace(r'\mathbf h_k^{\rm p}', r'\mathbf h_k')
        text = text.replace(r'\mathbf h_j^{\rm p}', r'\mathbf h_j')
        text = text.replace(r'\frac{1}{N_{\rm s}}', r'\frac1L')
        text = text.replace(r'N_{\rm s}', 'L')
    if name == 'appendix_afdm_channel_model.tex':
        text = text.replace(r'N_{\rm pre}', 'G')
    return re.sub(r'\s+', '', text)

def displays(text):
    return re.findall(r'\\begin\{equation\*?\}.*?\\end\{equation\*?\}|\\\[.*?\\\]', text, re.S)

manifest = json.loads(read(RUN / 'BEFORE.json'))
active = [p for p in manifest if p.endswith('.tex')]
label_before, label_after, display_count = [], [], 0
display_changes, mismatches, changes = [], [], []
for rel in active:
    old, new = read(RUN / 'before' / rel), read(PAPER / rel)
    label_before += re.findall(r'\\label\{([^}]+)\}', old)
    label_after += re.findall(r'\\label\{([^}]+)\}', new)
    a, b = displays(old), displays(new)
    if len(a) != len(b):
        mismatches.append({'file': rel, 'before_count': len(a), 'after_count': len(b)})
    for index, (x, y) in enumerate(zip(a, b), 1):
        display_count += 1
        label = re.findall(r'\\label\{([^}]+)\}', x)
        if x != y:
            display_changes.append({'file': rel, 'index': index, 'label': label})
        if normalize(x, Path(rel).name) != normalize(y, Path(rel).name):
            mismatches.append({'file': rel, 'index': index, 'label': label, 'before': x, 'after': y})
    if old != new:
        changes.extend(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile=rel+' (before)', tofile=rel))
(RUN / 'CHANGES.diff').write_text(''.join(changes), encoding='utf-8')

protected = [rel for rel in manifest if (rel.startswith('figures/') and not rel.startswith('figures/learned_receiver') and not rel.endswith('README.md')) or rel in ['references.bib', 'sections/01_introduction.tex', 'sections/appendix_evaluation_protocol.tex']]
protected_hashes = {rel: sha(PAPER/rel) == manifest[rel] for rel in protected}
sim_rel = 'sections/06_simulation_results.tex'
sim_old, sim_new = read(RUN/'before'/sim_rel), read(PAPER/sim_rel)
simulation_numbers_unchanged = re.findall(r'\d+', sim_old) == re.findall(r'\d+', sim_new)
result_start = r'\subsection{Effect of Density Ratio Estimation}'
results_prose_unchanged = sim_old.split(result_start, 1)[1] == sim_new.split(result_start, 1)[1]
frontend = read(PAPER/'sections/appendix_parameter_estimation.tex')
source_text = '\n'.join(read(PAPER/rel) for rel in active)
residual_checks = {
    'no_old_training_power_name': r'P_{\rm tr}' not in source_text,
    'no_plain_finite_difference_step': not re.search(r'\\delta(?![A-Za-z_])', read(PAPER/'sections/04_generative_priors.tex')),
    'no_old_noise_sample_denominator': r'\frac1L' not in frontend,
    'frontend_h_has_p_superscript': not re.search(r'\\mathbf h_[kj](?!\^\{\\rm p\})', frontend),
    'no_accidentally_bold_complex_field': r'\mathbb \mathbf C' not in source_text,
}

# A small deterministic check connects the explicitly defined index order to
# the existing tensor/Kronecker layout; it does not run inference or training.
m, n = 2, 3
h = np.arange(m*n*n).reshape(m,n,n) + 1j*np.arange(m*n*n, 0, -1).reshape(m,n,n)
index_ok = all(h.reshape(-1)[a*n*n+r*n+c] == h[a,r,c] for a in range(m) for r in range(n) for c in range(n))
za = np.array([[1, 2j], [3+1j, 2]], dtype=complex)
zc = np.array([[1, 2j], [3, 1j], [1+1j, 2]], dtype=complex)
ra, rc = za@za.conj().T, zc@zc.conj().T
c = np.kron(np.kron(ra, np.eye(n)), rc)
direct = np.einsum('ab,brs,cs->arc', ra, h, rc)
kronecker_error = float(np.max(np.abs(c@h.reshape(-1)-direct.reshape(-1))))
sigma = .5*np.block([[c.real, -c.imag], [c.imag, c.real]])
packed = np.r_[h.reshape(-1).real, h.reshape(-1).imag]
projected = c@h.reshape(-1)
real_embedding_error = float(np.max(np.abs(2*sigma@packed-np.r_[projected.real, projected.imag])))

doc = fitz.open(PAPER/'main.pdf')
preview = RUN/'preview'
preview.mkdir(exist_ok=True)
locations = {}
for i, page in enumerate(doc, 1):
    page.get_pixmap(dpi=110, alpha=False).save(preview/f'page-{i:02d}.png')
    text = page.get_text()
    for term in ['SUMMARY OF NOTATIONS', 'Learning Channel', 'Noise Variance Estimation', 'PHASE AND NOISE ESTIMATION', 'Algorithm 1', 'Common conditional', 'CHIRP']:
        if term.lower() in text.lower():
            locations.setdefault(term, []).append(i)
for start in range(1, len(doc)+1, 6):
    sheet = Image.new('RGB', (3*480, 2*650), 'white')
    draw = ImageDraw.Draw(sheet)
    for j, number in enumerate(range(start, min(start+6, len(doc)+1))):
        picture = Image.open(preview/f'page-{number:02d}.png')
        picture.thumbnail((470, 620))
        x, y = (j%3)*480, (j//3)*650
        sheet.paste(picture, (x, y+24))
        draw.text((x+8,y+5), f'Page {number}', fill='black')
    sheet.save(preview/f'contact-{start:02d}.png')

log = read(PAPER/'main.log')
validation = {
    'scope': 'active manuscript I-VI and appendices A-C, receiver figure labels only',
    'display_count': display_count,
    'changed_displays': display_changes,
    'display_mismatches_after_declared_inverse_renaming': mismatches,
    'removed_labels': sorted(set(label_before)-set(label_after)),
    'added_labels': sorted(set(label_after)-set(label_before)),
    'duplicate_labels': sorted({x for x in label_after if label_after.count(x)>1}),
    'protected_files_unchanged': protected_hashes,
    'simulation_numeric_tokens_unchanged': simulation_numbers_unchanged,
    'experimental_results_prose_from_VI_C_unchanged': results_prose_unchanged,
    'residual_checks': residual_checks,
    'vector_index_order_ok': index_ok,
    'kronecker_action_max_error': kronecker_error,
    'real_embedding_max_error': real_embedding_error,
    'pdf_pages': len(doc),
    'pdf_sha256': sha(PAPER/'main.pdf'),
    'overfull_count': log.count('Overfull'),
    'undefined_reference_or_citation': bool(re.search(r'(?:Reference|Citation).*undefined|There were undefined', log)),
    'page_locations': locations,
    'visual_review': 'pending',
    'final_source_sha256': {rel:sha(PAPER/rel) for rel in manifest},
}
(RUN/'VALIDATION.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in validation.items() if k not in ['changed_displays','final_source_sha256','protected_files_unchanged']}, ensure_ascii=False, indent=2))
print('Protected files unchanged:', all(protected_hashes.values()), f'({len(protected_hashes)} files)')
