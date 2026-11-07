"""Check this authorized wording revision against its saved baseline and sources."""
import difflib
import hashlib
import json
import re
import unicodedata
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PAPER = ROOT / 'paper/C-STMP'
baseline = json.loads((HERE / 'BASELINE.json').read_text(encoding='utf-8'))
before = (HERE / 'before/02_system_model.tex').read_text(encoding='utf-8')
after = (PAPER / 'sections/02_system_model.tex').read_text(encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def norm(text):
    text = unicodedata.normalize('NFKC', text).replace('\u00ad', '')
    text = re.sub(r'(?<=[A-Za-z])-\s*\n\s*(?=[a-z])', '', text)
    return re.sub(r'\s+', ' ', text).lower()

def words(text):
    return set(re.findall(r"[a-z]+(?:-[a-z]+)*", norm(text)))

def prose(tex):
    tex = re.sub(r'(?<!\\)%[^\n]*', '', tex)
    tex = re.sub(r'\\begin\{equation\}.*?\\end\{equation\}', ' ', tex, flags=re.S)
    tex = re.sub(r'\\\[.*?\\\]', ' ', tex, flags=re.S)
    tex = re.sub(r'\$[^$]*\$', ' ', tex)
    tex = re.sub(r'\\(?:cite|ref|eqref|label)\{[^}]*\}', ' ', tex)
    return re.sub(r'\\[A-Za-z]+\*?', '', tex)

sources = json.loads((PAPER / 'checks/ch2_sentence_source_check_20261030/SOURCES.json').read_text(encoding='utf-8'))
pages = json.loads((HERE / 'SOURCE_PAGES.json').read_text(encoding='utf-8'))
evidence = {}
source_hashes = {}
for source in sources:
    key = source['key']
    if key not in pages:
        continue
    source_hashes[key] = sha(Path(source['pdf'])) == source['sha256']
    for number, page in enumerate(pages[key], 1):
        for word in words(page):
            evidence.setdefault(word, f'{key}, PDF p.{number}')
    for word in words(Path(source['clean_text']).read_text(encoding='utf-8')):
        evidence.setdefault(word, f'{key}, cleaned PDF extraction')

main = (PAPER / 'main.tex').read_text(encoding='utf-8')
abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', main, flags=re.S).group(1)
intro = (PAPER / 'sections/01_introduction.tex').read_text(encoding='utf-8')
for title, tex in [('current abstract', abstract), ('current introduction', intro)]:
    for word in words(prose(tex)):
        evidence.setdefault(word, title)

chapter_words = words(prose(after))
automatic_unmatched = sorted(chapter_words - evidence.keys())
manual = {'closest': 'Shen, PDF p.3, section II-A; visually checked shen-source-page-03.png; extracted as closes t.'}
for word, location in manual.items():
    evidence.setdefault(word, location)
unresolved = sorted(chapter_words - evidence.keys())
(HERE / 'WORD_SOURCES.json').write_text(json.dumps({word: evidence.get(word) for word in sorted(chapter_words)}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def displays(tex, pattern):
    return [re.sub(r'\s+', '', match) for match in re.findall(pattern, tex, flags=re.S)]

equations = r'\\begin\{equation\}(.*?)\\end\{equation\}'
unnumbered = r'\\\[(.*?)\\\]'
old_phrases = ['path count', 'beam footprint', 'subtracts', 'unit-gain path', 'path matrix', 'AFDM basis waveform', 'integer useful samples', 'useful interval', 'normalized time', 'training prior', 'retains dependence', 'up to phase rotation', 'maintains its activity state', 'throughout a transmission block', 'posterior factorizes as', 'chirp periodicity']
remaining = [phrase for phrase in old_phrases if phrase.lower() in norm(after)]
protected_changed = [name for name, digest in baseline['protected'].items() if sha(ROOT / name) != digest]
log = (PAPER / 'main.log').read_text(encoding='utf-8', errors='replace')
pdf = PdfReader(PAPER / 'main.pdf')
result = {
    'chapter_before_matches_saved_baseline': sha(HERE / 'before/02_system_model.tex') == baseline['chapter_before_sha256'],
    'chapter_after_sha256': sha(PAPER / 'sections/02_system_model.tex'),
    'numbered_equations': len(displays(before, equations)),
    'numbered_equations_unchanged': displays(before, equations) == displays(after, equations),
    'unnumbered_displays': len(displays(before, unnumbered)),
    'unnumbered_displays_unchanged': displays(before, unnumbered) == displays(after, unnumbered),
    'labels_unchanged': re.findall(r'\\label\{([^}]+)\}', before) == re.findall(r'\\label\{([^}]+)\}', after),
    'inline_math_note': 'Equivalent descriptions added: xi T_s; t=0,...,N-1; path gain 1; delay d T_s; t_c=(g+t)T_s; integer d. Prior argument H_k and independence variables made explicit.',
    'protected_files_checked': len(baseline['protected']),
    'protected_files_changed': protected_changed,
    'source_hashes_match': source_hashes,
    'unique_prose_word_forms': len(chapter_words),
    'automatic_unmatched_word_forms': automatic_unmatched,
    'manual_pdf_matches': manual,
    'unresolved_word_forms': unresolved,
    'superseded_phrases_remaining': remaining,
    'pdf_pages': len(pdf.pages),
    'pdf_sha256': sha(PAPER / 'main.pdf'),
    'overfull_boxes': len(re.findall(r'Overfull \\[hv]box', log)),
    'undefined_citations_or_references': bool(re.search(r'(?:Citation|Reference).*undefined|There were undefined', log)),
    'visual_review': 'pending',
}
(HERE / 'VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(HERE / 'CHANGES.diff').write_text(''.join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True), fromfile='before/02_system_model.tex', tofile='sections/02_system_model.tex')), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
assert not protected_changed and not unresolved and not remaining
assert result['numbered_equations_unchanged'] and result['unnumbered_displays_unchanged'] and result['labels_unchanged']
assert all(source_hashes.values()) and not result['undefined_citations_or_references']
