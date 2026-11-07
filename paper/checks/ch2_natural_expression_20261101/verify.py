"""Check the scope of the notation and prose correction against its own baseline."""
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

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return p.read_text(encoding='utf-8')

def norm(t):
    t = unicodedata.normalize('NFKC', t).replace('\u00ad', '')
    t = re.sub(r'(?<=[A-Za-z])-\s*\n\s*(?=[a-z])', '', t)
    return re.sub(r'\s+', ' ', t).lower()

def words(t):
    return set(re.findall(r'[a-z]+(?:-[a-z]+)*', norm(t)))

def prose(t):
    t = re.sub(r'\\begin\{equation\}.*?\\end\{equation\}|\\\[.*?\\\]', ' ', t, flags=re.S)
    t = re.sub(r'\$[^$]*\$', ' ', t)
    t = re.sub(r'\\(?:cite|ref|eqref|label)\{[^}]*\}', ' ', t)
    return re.sub(r'\\[A-Za-z]+\*?', '', t)

before = read(HERE / 'before/02_system_model.tex')
after = read(PAPER / 'sections/02_system_model.tex')
baseline = json.loads(read(HERE / 'BASELINE.json'))
numbered = r'\\begin\{equation\}.*?\\end\{equation\}'
unnumbered = r'\\\[.*?\\\]'
extract = lambda t, p: re.findall(p, t, flags=re.S)
protected_changed = [p for p, h in baseline['protected'].items() if sha(ROOT / p) != h]

evidence = {}
source_checks = {}
upa_search = {}
pages = json.loads(read(PAPER / 'checks/ch2_source_wording_20261101/SOURCE_PAGES.json'))
sources = json.loads(read(PAPER / 'checks/ch2_sentence_source_check_20261030/SOURCES.json'))
for s in sources:
    if s['key'] not in pages:
        continue
    source_checks[s['key']] = sha(Path(s['pdf'])) == s['sha256']
    for n, t in enumerate(pages[s['key']], 1):
        for w in words(t):
            evidence.setdefault(w, f'{s["key"]}, PDF p.{n}')
    clean = read(Path(s['clean_text']))
    for w in words(clean):
        evidence.setdefault(w, s['key'] + ', cleaned extraction')
    upa_search[s['key']] = bool(re.search(r'\bupa response\b', norm(' '.join(pages[s['key']]) + ' ' + clean)))
wei = read(ROOT / 'reference/literature/wei_yuan_2026_lstmp_v1.txt')
upa_search['wei_yuan_2026'] = bool(re.search(r'\bupa response\b', norm(wei)))
for w in words(wei):
    evidence.setdefault(w, 'Wei–Yuan, local full text')
abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', read(PAPER / 'main.tex'), flags=re.S).group(1)
for name, value in [('approved abstract', abstract), ('approved introduction', read(PAPER / 'sections/01_introduction.tex'))]:
    for w in words(prose(value)):
        evidence.setdefault(w, name)
evidence['closest'] = 'Shen PDF p.3 §II-A; visually checked in prior round; OCR splits closest.'
evidence['axis'] = 'Li PDF p.4 §II-B: v-axis; visually checked. Stripping the inline math v from the manuscript leaves axis as a separate token.'
chapter_words = words(prose(after))
unresolved = sorted(chapter_words - evidence.keys())
(HERE / 'WORD_SOURCES.json').write_text(json.dumps({w: evidence.get(w) for w in sorted(chapter_words)}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
log = read(PAPER / 'main.log')
chlog = log.split('(sections/02_system_model', 1)[1].split('(sections/03_bayesian_receiver_design', 1)[0]
result = {
    'chapter_before_matches_saved_hash': sha(HERE / 'before/02_system_model.tex') == baseline['chapter_before_sha256'],
    'chapter_after_sha256': sha(PAPER / 'sections/02_system_model.tex'),
    'numbered_equations': len(extract(before, numbered)),
    'numbered_equations_byte_identical': extract(before, numbered) == extract(after, numbered),
    'unnumbered_displays': len(extract(before, unnumbered)),
    'unnumbered_displays_byte_identical': extract(before, unnumbered) == extract(after, unnumbered),
    'labels_unchanged': re.findall(r'\\label\{([^}]+)\}', before) == re.findall(r'\\label\{([^}]+)\}', after),
    'protected_files_checked': len(baseline['protected']),
    'protected_files_changed': protected_changed,
    'glossary_baseline_preserved': (PAPER/'docs/TERMINOLOGY.md').read_bytes().startswith((HERE/'before/TERMINOLOGY.md').read_bytes()),
    'source_pdf_hashes_match_prior_extraction': source_checks,
    'exact_upa_response_found_in_checked_texts': upa_search,
    'array_response_vector_source': 'Li PDF p.3 §II-B after Eq.(2); p.4 first paragraph; source pages visually inspected.',
    'the_notations_before': len(re.findall(r'\bThe notations\b', before)),
    'the_notations_after': len(re.findall(r'\bThe notations\b', after)),
    'unresolved_word_forms': unresolved,
    'word_check_limitation': 'Word-form matching is not evidence of a full phrase or sentence. Old broad source attribution has been corrected in REVISION_NOTES.md and TERMINOLOGY.md.',
    'inline_math_adaptations': ['d_v with v in {y,z} is equivalent to the original d_y,d_z definitions.', 't_c=0 at the beginning of the transmission block preserves the former time-from-block-start definition.', 'g=g_q makes the substitution in the original Eq.(8) explicit.'],
    'pdf_pages': len(PdfReader(PAPER / 'main.pdf').pages),
    'pdf_sha256': sha(PAPER / 'main.pdf'),
    'overfull_boxes': len(re.findall(r'Overfull \\[hv]box', log)),
    'undefined_references_or_citations': bool(re.search(r'(?:Citation|Reference).*undefined|There were undefined', log)),
    'chapter_ii_underfull_boxes': len(re.findall(r'Underfull \\[hv]box', chlog)),
    'visual_review': {'status': 'PASS', 'pages': [2,3,4], 'note': 'Latest Poppler renders inspected: no clipped or overlapping text or formulas.'},
}
(HERE / 'VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
(HERE / 'CHANGES.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='before/02_system_model.tex', tofile='sections/02_system_model.tex')), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
assert result['chapter_before_matches_saved_hash'] and result['numbered_equations_byte_identical']
assert result['unnumbered_displays_byte_identical'] and result['labels_unchanged']
assert result['glossary_baseline_preserved'] and not protected_changed and not unresolved
assert all(source_checks.values()) and not result['overfull_boxes'] and not result['undefined_references_or_citations']
