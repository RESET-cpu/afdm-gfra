"""Check the authorized terminology changes and the explicit phase formula."""
import difflib
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
import re
import sys
import unicodedata

from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PAPER = ROOT / 'paper/C-STMP'
read = lambda p: p.read_text(encoding='utf-8')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
baseline = json.loads(read(HERE / 'BASELINE.json'))

changes = [
    ('During each transmission block, active devices share the same pilot\nresources to transmit their signals to the satellite.',
     'During each transmission block, active devices share the same resources\nfor pilot transmission to the satellite.'),
    ('After receiver compensation for the common delay $\\tau_c$, the',
     'After delay compensation for $\\tau_c$ at the satellite receiver, the'),
    ('We assume that the path gains, delays, Doppler shifts, and arrival\nangles remain approximately constant within a transmission block.',
     'We assume that the path gains, delays, Doppler shifts, and angles of\narrival remain approximately constant within a transmission block.'),
    ('\\subsection{Multi-Frame AFDM Transmission}', '\\subsection{Transmission Scheme}'),
    ('Let $\\mathbf P\\in\\mathbb C^{Q\\times KN}$ denote a known pilot matrix\nat the satellite receiver, with entries',
     'The pilot symbols are known at the satellite receiver.\nLet $\\mathbf P\\in\\mathbb C^{Q\\times KN}$ denote the pilot matrix,\nwith entries'),
    ('$\\mathbf P\\mathbf P^{\\mathsf H}=KE_p\\I_Q$, where each device has\nthe same pilot energy $E_p=\\|\\mathbf p_{qk}\\|^2$ in each frame',
     '$\\mathbf P\\mathbf P^{\\mathsf H}=KE_p\\I_Q$, where\n$\\|\\mathbf p_{qk}\\|^2=E_p$ for all $k$ and $q$'),
    ('Here $T_{\\rm frame}=(N+N_{\\rm CPP})T_s$ is the time duration of\nan AFDM frame with CPP.',
     'Each AFDM frame spans a duration of $T_{\\rm frame}=(N+N_{\\rm CPP})T_s$.'),
    ('$t=0,\\ldots,N-1$, while $\\varphi_n(\\xi)$ satisfies the CPP relation',
     '$t=0,\\ldots,N-1$, while $\\varphi_n(\\xi)$ satisfies'),
    ('where $n$ and $r$ represent the transmitted and received symbol\npositions, respectively, and $m$ is the antenna index.',
     'where $n$ and $r$ correspond to the transmitted and received\nsymbols, respectively, and $m=0,\\ldots,M-1$.'),
    (' \\beta_k=\\operatorname{wrap}(2\\pi\\nu_kT_{\\rm frame}),',
     ' \\beta_k=2\\pi\\!\\left(\\nu_kT_{\\rm frame}\n -\\left\\lfloor\\nu_kT_{\\rm frame}+\\frac12\\right\\rfloor\\right),'),
    ('where $\\operatorname{wrap}(\\cdot)$ maps an angle to $[-\\pi,\\pi)$.\nAfter separating the phase evolution across frames, $H_k$ remains\napproximately constant over $Q$ consecutive frames.',
     'where $\\beta_k\\in[-\\pi,\\pi)$.\nThe phase rotation $e^{jq\\beta_k}$ accumulates across multiple frames,\nwhile $H_k$ remains approximately constant over $Q$ consecutive frames.'),
    ('The pilot symbols including the inter-frame phase rotation are given by',
     'The pilot symbols including the phase rotation are given by'),
]

chapter_path = 'sections/02_system_model.tex'
appendix_path = 'sections/appendix_parameter_estimation.tex'
before = read(HERE / 'before' / chapter_path)
after = read(PAPER / chapter_path)
expected = before
for old, new in changes:
    assert expected.count(old) == 1, old
    expected = expected.replace(old, new)
assert expected == after, 'Unexpected change in Chapter II'

old_app = read(HERE / 'before' / appendix_path)
new_app = read(PAPER / appendix_path)
app_old = 'as a refinement start. Finally set\n$\\widehat\\beta_k=\\operatorname{wrap}(2\\pi\\widehat\\nu_kT_{\\rm frame})$'
app_new = 'as a refinement start. Finally, compute $\\widehat\\beta_k$ from\n\\eqref{eq:twc-frame-channel} with $\\nu_k=\\widehat\\nu_k$'
assert old_app.count(app_old) == 1
assert old_app.replace(app_old, app_new) == new_app

equations = lambda t: re.findall(r'\\begin\{equation\}.*?\\end\{equation\}', t, re.S)
old_eqs, new_eqs = equations(before), equations(after)
assert len(old_eqs) == len(new_eqs) == 15
equation_checks = {}
for old, new in zip(old_eqs, new_eqs):
    label = re.search(r'\\label\{([^}]+)\}', old).group(1)
    target = old.replace(*changes[9]) if label == 'eq:twc-frame-channel' else old
    equation_checks[label] = target == new
assert all(equation_checks.values())
assert equations(old_app) == equations(new_app)
assert re.findall(r'\\\[.*?\\\]', before, re.S) == re.findall(r'\\\[.*?\\\]', after, re.S)
assert re.findall(r'\\label\{[^}]*\}', before) == re.findall(r'\\label\{[^}]*\}', after)

# Exact rational checks include every half-integer boundary and near-boundary points.
# If r = x-floor(x+1/2), then -1/2 <= r < 1/2 and x-r is an integer.
# This proves beta=2*pi*r is the same representative and preserves exp(j*q*beta).
xs = {Fraction(i, 113) for i in range(-10000, 10001)}
xs |= {Fraction(i, 2) + offset for i in range(-300, 301)
       for offset in (Fraction(0), Fraction(1, 10**12), Fraction(-1, 10**12))}
for x in xs:
    r = x - math.floor(x + Fraction(1, 2))
    assert Fraction(-1, 2) <= r < Fraction(1, 2)
    assert (x - r).denominator == 1
    for q in (0, 1, 7, 31):
        assert (q * (x - r)).denominator == 1

def norm(t):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', t))

source_text = PAPER / 'checks/full_terminology_audit_20261030/source_text'
source_checks = [
    ('resources for pilot transmission', 'cai2026', 1),
    ('delay compensation', 'li2023', 4),
    ('angles-of-arrival', 'li2023', 4),
    ('Transmission Scheme', 'shen2025', 4),
    ('pilot matrix', 'cai2026', 4),
    ('known at the receiver', 'wei2026', 2),
    ('Each AFDM frame spans a duration', 'huang2026', 2),
    ('transmitted symbols', 'bemani2022', 10),
    ('received symbols', 'bemani2022', 10),
    ('phase rotation', 'shen2025', 5),
    ('accumulates across multiple frames', 'shen2025', 5),
]
evidence = []
for phrase, key, page in source_checks:
    source = norm(json.loads(read(source_text / (key + '.json')))[page - 1])
    pattern = '[\\s\\-]*'.join(map(re.escape, re.sub(r'[\s-]', '', phrase)))
    match = re.search(pattern, source, re.I)
    assert match, (phrase, key, page)
    evidence.append(dict(phrase=phrase, source=key, pdf_page=page,
                         context=source[max(0, match.start()-80):match.end()+210]))

flat = norm(after)
removed = ['pilot resources', 'arrival angles', 'Multi-Frame AFDM Transmission',
           'receiver compensation', 'known pilot matrix', 'pilot energy',
           'time duration of an AFDM frame with CPP', 'CPP relation',
           'transmitted and received symbol positions', 'antenna index',
           'wrap', 'phase evolution across frames', 'inter-frame phase rotation']
assert not [p for p in removed if p in flat]
assert 'wrap' not in new_app
protected_changed = [p for p, h in baseline['protected'].items() if sha(ROOT / p) != h]
assert not protected_changed
cite_pattern = r'\\cite(?:\[[^\]]*\])*\{[^}]*\}'
assert re.findall(cite_pattern, before) == re.findall(cite_pattern, after)
assert re.findall(cite_pattern, old_app) == re.findall(cite_pattern, new_app)
# The saved .bbl predates an already-present citation in unchanged main.tex.
# Check this discrepancy explicitly rather than asserting byte identity for a cache.
old_scope = json.loads(read(PAPER / 'checks/ch2_all_names_20261101/SEARCH_SCOPE.json'))
old_keys = set(old_scope['keys_in_current_pdf_references'])
new_keys = set(re.findall(r'\\bibitem\{([^}]+)\}', read(PAPER / 'main.bbl')))
assert new_keys - old_keys == {'neeser1993'} and not old_keys - new_keys
assert r'\cite{neeser1993}' in read(PAPER / 'main.tex')
log = read(PAPER / 'main.log')
ch_log = log.split('(sections/02_system_model', 1)[1].split('(sections/03_bayesian_receiver_design', 1)[0]
assert not re.search(r'(?:Over|Under)full', ch_log)
assert not re.search(r'(?:Reference|Citation).*undefined|There were undefined references|Overfull', log)

diff = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='before/'+chapter_path, tofile='after/'+chapter_path))
diff += ''.join(difflib.unified_diff(old_app.splitlines(True), new_app.splitlines(True), fromfile='before/'+appendix_path, tofile='after/'+appendix_path))
(HERE / 'CHANGES.diff').write_text(diff, encoding='utf-8')
(HERE / 'SOURCE_EVIDENCE.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
result = dict(exact_authorized_chapter_replacements=len(changes), exact_appendix_replacement=True,
              numbered_equations=15, numbered_equation_checks=equation_checks,
              phase_definition='Equivalent explicit floor formula; no model change',
              exact_rational_phase_cases=len(xs), unnumbered_displays_unchanged=True,
              appendix_numbered_equations_unchanged=True, labels_unchanged=True,
              forbidden_old_names_absent=True, direct_source_checks=len(evidence),
              protected_files_checked=len(baseline['protected']), protected_files_changed=protected_changed,
              bibliography_source_and_citation_commands_unchanged=True,
              compiled_bbl_changed=sha(PAPER/'main.bbl') != baseline['bbl_before_sha256'],
              compiled_bbl_note='Rebuild adds neeser1993 already cited in unchanged main.tex:80; stale pre-build .bbl omitted it. No citation was added to manuscript source.',
              pdf_pages=len(PdfReader(PAPER/'main.pdf').pages),
              chapter_layout_warnings=False, undefined_references=False, overfull_anywhere=False,
              chapter_after_sha256=sha(PAPER/chapter_path), appendix_after_sha256=sha(PAPER/appendix_path),
              pdf_sha256=sha(PAPER/'main.pdf'))
(HERE / 'VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
