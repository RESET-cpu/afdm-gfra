"""Verify this language-only revision against the immediately preceding chapter."""
import difflib
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PAPER = ROOT / 'paper/C-STMP'
read = lambda p: p.read_text(encoding='utf-8')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = read(HERE / 'before/sections/02_system_model.tex')
after = read(PAPER / 'sections/02_system_model.tex')
baseline = json.loads(read(HERE / 'BASELINE.json'))

changes = [
    ('The time instant $t_{\\rm c}=0$ corresponds to the beginning of\nthe transmission block.',
     'We set $t_{\\rm c}=0$ at the beginning of the transmission block.'),
    ('The directional cosines $\\mu_{z,k}$ and $\\mu_{y,k}$ are along the\nz-axis and y-axis, respectively.',
     'Here $\\mu_{z,k}$ and $\\mu_{y,k}$ are the directional cosines along\nthe z-axis and y-axis, respectively.'),
    ('Assume that a total of $Q$ AFDM frames are allocated for pilot\ntransmission.',
     'Assume that $Q$ AFDM frames are allocated for pilot transmission.'),
    ('For path gain $1$, delay $dT_s$, and Doppler shift $\\nu$,',
     'For a path with gain $1$, delay $dT_s$, and Doppler shift $\\nu$,'),
    ('We model the entire $H_k$ using $q_{\\rm tr}(H_k)$, the channel\nprior for training, rather than factorizing it element-wise.',
     'We model the entire $H_k$ using the channel prior $q_{\\rm tr}(H_k)$\nfor training, rather than factorizing this prior element-wise.'),
    ('The variables $H_k$ and $\\alpha_k$ are independent for different\nvalues of $k$, and $H_k$ is independent of $\\alpha_k$.',
     'We assume that $H_k$ and $\\alpha_k$ are independent for different\nvalues of $k$, and that $H_k$ is independent of $\\alpha_k$.'),
]
punctuation = {
    'eq:upa': ('/\\lambda}.', '/\\lambda},'),
    'eq:continuous-waveform': ('\\zeta_n(w_\\xi)w_\\xi]}.', '\\zeta_n(w_\\xi)w_\\xi]},'),
    'eq:path-operator-system': ('\\varphi_n(t-d).', '\\varphi_n(t-d),'),
}
expected = before
for old, new in changes + list(punctuation.values()):
    assert expected.count(old) == 1, old
    expected = expected.replace(old, new)

numbered_pattern = r'\\begin\{equation\}.*?\\end\{equation\}'
unnumbered_pattern = r'\\\[.*?\\\]'
extract = lambda t, p: re.findall(p, t, flags=re.S)
old_equations = extract(before, numbered_pattern)
new_equations = extract(after, numbered_pattern)
equation_checks = {}
for old, new in zip(old_equations, new_equations):
    label = re.search(r'\\label\{([^}]+)\}', old).group(1)
    if label in punctuation:
        old_p, new_p = punctuation[label]
        equation_checks[label] = old.replace(old_p, new_p) == new
    else:
        equation_checks[label] = old == new

def words(text):
    text = unicodedata.normalize('NFKC', text).replace('\u00ad', '')
    text = re.sub(r'(?<=[A-Za-z])-\s*\n\s*(?=[a-z])', '', text)
    return set(re.findall(r'[a-z]+(?:-[a-z]+)*', text.lower()))

def prose(text):
    text = re.sub(numbered_pattern + '|' + unnumbered_pattern, ' ', text, flags=re.S)
    text = re.sub(r'\$[^$]*\$', ' ', text)
    text = re.sub(r'\\(?:cite|ref|eqref|label)\{[^}]*\}', ' ', text)
    return re.sub(r'\\[A-Za-z]+\*?', '', text)

new_words = words(prose(after)) - words(prose(before))
pages = json.loads(read(PAPER / 'checks/ch2_source_wording_20261101/SOURCE_PAGES.json'))
word_sources = {}
for key, source_pages in pages.items():
    for page, text in enumerate(source_pages, 1):
        for word in new_words & words(text):
            word_sources.setdefault(word, f'{key}, PDF p.{page}')

log = read(PAPER / 'main.log')
chapter_log = log.split('(sections/02_system_model', 1)[1].split('(sections/03_bayesian_receiver_design', 1)[0]
result = {
    'chapter_before_matches_baseline': sha(HERE / 'before/sections/02_system_model.tex') == baseline['chapter_before_sha256'],
    'chapter_after_sha256': sha(PAPER / 'sections/02_system_model.tex'),
    'exactly_six_prose_changes_and_three_punctuation_changes': expected == after,
    'numbered_equations_before_after': [len(old_equations), len(new_equations)],
    'equation_checks_with_only_three_allowed_punctuation_changes': equation_checks,
    'unnumbered_displays_before_after': [len(extract(before, unnumbered_pattern)), len(extract(after, unnumbered_pattern))],
    'unnumbered_displays_unchanged': extract(before, unnumbered_pattern) == extract(after, unnumbered_pattern),
    'labels_unchanged': re.findall(r'\\label\{[^}]+\}', before) == re.findall(r'\\label\{[^}]+\}', after),
    'protected_files_checked': len(baseline['protected']),
    'protected_files_changed': [p for p, h in baseline['protected'].items() if sha(ROOT/p) != h],
    'glossary_baseline_preserved': (PAPER/'docs/TERMINOLOGY.md').read_bytes().startswith((HERE/'before/docs/TERMINOLOGY.md').read_bytes()),
    'new_prose_words': sorted(new_words),
    'new_word_sources_only_not_full_sentence_provenance': word_sources,
    'unmatched_new_words': sorted(new_words-word_sources.keys()),
    'pdf_pages': len(PdfReader(PAPER/'main.pdf').pages),
    'pdf_sha256': sha(PAPER/'main.pdf'),
    'chapter_overfull_or_underfull': bool(re.search(r'(?:Over|Under)full', chapter_log)),
    'undefined_references': bool(re.search(r'(?:Reference|Citation).*undefined|There were undefined references', log)),
    'overfull_anywhere': 'Overfull' in log,
}
(HERE/'CHANGES.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='before/02_system_model.tex', tofile='after/02_system_model.tex')), encoding='utf-8')
(HERE/'VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
assert result['exactly_six_prose_changes_and_three_punctuation_changes']
assert all(equation_checks.values()) and len(new_equations) == 15
assert result['unnumbered_displays_unchanged'] and result['labels_unchanged']
assert not result['protected_files_changed'] and result['glossary_baseline_preserved']
assert not result['unmatched_new_words']
assert not result['undefined_references'] and not result['overfull_anywhere']
print(json.dumps(result, ensure_ascii=False, indent=2))
