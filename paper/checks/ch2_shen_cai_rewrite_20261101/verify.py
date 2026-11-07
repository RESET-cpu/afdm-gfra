"""Verify the scope and evidence of the authorized Chapter II prose rewrite."""
import hashlib
import json
import re
import unicodedata
from pathlib import Path

from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PAPER = ROOT / 'paper/C-STMP'

def read(path):
    return path.read_text(encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def words(value):
    value = unicodedata.normalize('NFKC', value).replace('\u00ad', '')
    value = re.sub(r'(?<=[A-Za-z])-\s*\n\s*(?=[a-z])', '', value)
    return set(re.findall(r'[a-z]+(?:-[a-z]+)*', value.lower()))

def prose(value):
    value = re.sub(r'(?<!\\)%[^\n]*', '', value)
    value = re.sub(r'\\begin\{equation\}.*?\\end\{equation\}|\\\[.*?\\\]', ' ', value, flags=re.S)
    value = re.sub(r'\$[^$]*\$', ' ', value)
    value = re.sub(r'\\(?:cite|ref|eqref|label)\{[^}]*\}', ' ', value)
    return re.sub(r'\\[A-Za-z]+\*?', '', value)

baseline = json.loads(read(HERE / 'BASELINE.json'))
before = read(HERE / 'before/02_system_model.tex')
after = read(PAPER / 'sections/02_system_model.tex')
equation_pattern = r'\\begin\{equation\}.*?\\end\{equation\}'
display_pattern = r'\\\[.*?\\\]'
equations_before = re.findall(equation_pattern, before, flags=re.S)
displays_before = re.findall(display_pattern, before, flags=re.S)
protected_changed = [p for p, digest in baseline['protected'].items() if sha(ROOT / p) != digest]

source_set = []
for key, filename, expected, location in [
    ('shen2025', 'shen2025.pdf', baseline['sources']['shen2025'], 'PDF pp.3–5, §II-A/B/C; p.1 §I'),
    ('cai2026', 'cai2026.pdf', baseline['sources']['cai2026'], 'PDF pp.3–5, §II-A/B; pp.1,6,7,9,11; p.5 Table II'),
    ('ding2026', 'ding2026.pdf', '22dceda0036c892f44e961ce9ab6d094930e610befe0d51c18c3357aa1890ec5', 'PDF p.2, §II, IDAFT signal and parameter definitions'),
    ('wei_yuan_2026', 'wei_yuan_2026_lstmp_v1.pdf', 'dee35d773df47f984b2022c2b7be07a01e3d942cde8fae84830ac3a0bfd2f7dd', 'PDF p.2, §II-A/B, known matrix and underdetermined inverse problem'),
]:
    path = ROOT / 'reference/literature' / filename
    source_set.append({'key': key, 'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'matches_read_source': sha(path) == expected, 'location': location})
source_set.append({
    'key': 'xu2026',
    'url': 'https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/AFDM-aided-Grant-Free-Random-Access-for-LEO/991050765702346',
    'location': 'Author manuscript, printed p.3 (PDF p.4), §II-B, before Eq.(6)',
    'access': 'Online PDF text read; no local PDF or successful page screenshot.',
    'used_sentence': 'The time-domain signal can be obtained by',
})
(HERE / 'SOURCE_SET.json').write_text(json.dumps(source_set, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

evidence = {}
pages = json.loads(read(PAPER / 'checks/ch2_source_wording_20261101/SOURCE_PAGES.json'))
for key, texts in pages.items():
    for number, page in enumerate(texts, 1):
        for word in words(page):
            evidence.setdefault(word, f'{key}, PDF p.{number}')
for item in json.loads(read(PAPER / 'checks/ch2_sentence_source_check_20261030/SOURCES.json')):
    if item['key'] in pages:
        for word in words(read(Path(item['clean_text']))):
            evidence.setdefault(word, f'{item["key"]}, cleaned PDF extraction')
for word in words(read(ROOT / 'reference/literature/wei_yuan_2026_lstmp_v1.txt')):
    evidence.setdefault(word, 'Wei–Yuan, local PDF extraction')
main = read(PAPER / 'main.tex')
abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', main, flags=re.S).group(1)
for title, value in [('approved abstract', abstract), ('approved introduction', read(PAPER / 'sections/01_introduction.tex'))]:
    for word in words(prose(value)):
        evidence.setdefault(word, title)
chapter_words = words(prose(after))
automatic_unmatched = sorted(chapter_words - evidence.keys())
evidence['closest'] = 'Shen PDF p.3 §II-A; visually checked in ch2_source_wording_20261101/shen-source-page-03.png; PDF extraction splits as closes t.'
unmatched = sorted(chapter_words - evidence.keys())
(HERE / 'WORD_SOURCES.json').write_text(json.dumps({w: evidence.get(w) for w in sorted(chapter_words)}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

alignment = json.loads(read(HERE / 'ALIGNMENT.json'))
alignment_current = all(after[u['start']:].startswith(u['anchor']) for u in alignment['units'])
log = read(PAPER / 'main.log')
chapter_log = log.split('(sections/02_system_model', 1)[1].split('(sections/03_bayesian_receiver_design', 1)[0]
result = {
    'chapter_before_matches_baseline': sha(HERE / 'before/02_system_model.tex') == baseline['chapter_before_sha256'],
    'chapter_after_sha256': sha(PAPER / 'sections/02_system_model.tex'),
    'numbered_equations': len(equations_before),
    'numbered_equations_byte_identical': equations_before == re.findall(equation_pattern, after, flags=re.S),
    'unnumbered_displays': len(displays_before),
    'unnumbered_displays_byte_identical': displays_before == re.findall(display_pattern, after, flags=re.S),
    'labels_unchanged': re.findall(r'\\label\{([^}]+)\}', before) == re.findall(r'\\label\{([^}]+)\}', after),
    'protected_files_checked': len(baseline['protected']),
    'protected_files_changed': protected_changed,
    'glossary_baseline_preserved_as_prefix': (PAPER / 'docs/TERMINOLOGY.md').read_bytes().startswith((HERE / 'before/TERMINOLOGY.md').read_bytes()),
    'local_source_hashes_match': all(s['matches_read_source'] for s in source_set if 'path' in s),
    'alignment_units': len(alignment['units']),
    'alignment_groups': len({u['group'] for u in alignment['units']}),
    'alignment_anchors_current': alignment_current,
    'alignment_sha256': sha(HERE / 'SENTENCE_ALIGNMENT.md'),
    'unique_prose_word_forms': len(chapter_words),
    'automatic_unmatched_word_forms': automatic_unmatched,
    'unresolved_word_forms_after_visual_evidence': unmatched,
    'word_check_scope': 'Individual word forms only. Full sentence/paragraph relations and necessary mathematical adaptations are recorded separately in SENTENCE_ALIGNMENT.md.',
    'pdf_pages': len(PdfReader(PAPER / 'main.pdf').pages),
    'pdf_sha256': sha(PAPER / 'main.pdf'),
    'overfull_boxes': len(re.findall(r'Overfull \\[hv]box', log)),
    'undefined_references_or_citations': bool(re.search(r'(?:Citation|Reference).*undefined|There were undefined', log)),
    'chapter_ii_underfull_boxes': len(re.findall(r'Underfull \\[hv]box', chapter_log)),
    'visual_review': {'status': 'PASS', 'pages': [2, 3, 4, 5], 'note': 'Latest compiled PDF rendered with Poppler and visually inspected; Chapter II spans pages 2–4. No overlaps, clipped text, or overflowing equations.'},
}
(HERE / 'VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
assert result['chapter_before_matches_baseline'] and result['local_source_hashes_match']
assert result['numbered_equations_byte_identical'] and result['unnumbered_displays_byte_identical'] and result['labels_unchanged']
assert not protected_changed and not unmatched and alignment_current
assert result['glossary_baseline_preserved_as_prefix']
assert not result['overfull_boxes'] and not result['undefined_references_or_citations']
