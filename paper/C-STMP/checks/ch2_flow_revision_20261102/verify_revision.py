from pathlib import Path
from collections import Counter
import difflib
import hashlib
import json
import re
import sys
import unicodedata
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')
paper = Path(__file__).resolve().parents[2]
run = Path(__file__).resolve().parent
before = (run/'before/sections/02_system_model.tex').read_text(encoding='utf-8')
after = (paper/'sections/02_system_model.tex').read_text(encoding='utf-8')
baseline = json.loads((run/'BASELINE.json').read_text(encoding='utf-8'))
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
changes = [p for p, h in baseline.items() if digest(paper/p) != h]
allowed = {'sections/02_system_model.tex', 'docs/TERMINOLOGY.md', 'main.pdf'}

def numbered(text):
    result = {}
    for block in re.findall(r'\\begin\{equation\}[\s\S]*?\\end\{equation\}', text):
        label = re.search(r'\\label\{([^}]+)\}', block).group(1)
        result[label] = block
    return result

def unnumbered(text):
    return Counter(re.findall(r'\\\[[\s\S]*?\\\]', text))

diff = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
    fromfile='before/02_system_model.tex', tofile='after/02_system_model.tex'))
(run/'CHANGES.diff').write_text(diff, encoding='utf-8')

# Word matches are bounded vocabulary evidence, not sentence-provenance proof.
def words(text):
    return set(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", unicodedata.normalize('NFKC', text).lower()))
source_dir = paper/'checks/ch2_paragraph_review_20261102/sources'
corpus = {p.stem: words(p.read_text(encoding='utf-8')) for p in source_dir.glob('*.reading.txt')
          if p.name != 'cai_v2.reading.txt'}
corpus['accepted_abstract_introduction'] = words(
    (paper/'main.tex').read_text(encoding='utf-8') + (paper/'sections/01_introduction.tex').read_text(encoding='utf-8'))
new_words = {w: [key for key, vocabulary in corpus.items() if w in vocabulary]
             for w in sorted(words(after)-words(before))}
(run/'NEW_WORDS.json').write_text(json.dumps(new_words, ensure_ascii=False, indent=2), encoding='utf-8')

# Include the unchanged introduction so first-use acronym checks have body context.
reading = (paper/'sections/01_introduction.tex').read_text(encoding='utf-8')+'\n\n'+after
reading = re.sub(r'\\begin\{equation\}[\s\S]*?\\end\{equation\}|\\\[[\s\S]*?\\\]|\$[^$]*\$', ' ', reading)
reading = re.sub(r'\\(?:cite|label|ref|eqref)\{[^}]*\}', '', reading)
reading = re.sub(r'\\(?:section|subsection|subsubsection)\{([^}]*)\}', r'\n\n\1\n\n', reading)
reading = re.sub(r'\\(?:begin|end)\{[^}]*\}(?:\[[^]]*\])?', '', reading)
reading = re.sub(r'\\item', '', reading)
reading = re.sub(r'(?<!\n)\n(?!\n)', ' ', reading)
(run/'draft.md').write_text(reading, encoding='utf-8')

pdf = PdfReader(paper/'main.pdf')
pdf_pages = [p.extract_text() or '' for p in pdf.pages]
normalize = lambda s: re.sub(r'[\s\-–—]', '', unicodedata.normalize('NFKC', s))
pdf_text = normalize('\n'.join(pdf_pages))
phrases = [
    'In the proposed scheme, each active device transmits pilot symbols over',
    'AFDM modulation and demodulation are performed independently for each',
    'To account for fractional delays, we define the transmit waveform',
    'frames provide more observations without increasing the number of',
    'We use the distribution of the training channels as the channel prior',
]
log = (paper/'main.log').read_text(encoding='utf-8', errors='replace')
result = {
    'numbered_equations': len(numbered(after)),
    'numbered_equation_content_and_order_unchanged': numbered(before)==numbered(after) and list(numbered(before))==list(numbered(after)),
    'unnumbered_displays': sum(unnumbered(after).values()),
    'unnumbered_display_content_unchanged': unnumbered(before)==unnumbered(after),
    'formula_movement': 'A definition moved before the unnumbered activity definition; equation numbers and contents unchanged.',
    'all_labels_unchanged': re.findall(r'\\label\{[^}]+\}', before)==re.findall(r'\\label\{[^}]+\}', after),
    'changed_files_in_baseline': changes,
    'unexpected_protected_changes': sorted(set(changes)-allowed),
    'abstract_and_introduction_unchanged': all(p not in changes for p in ['main.tex','sections/00_abstract_zh.md','sections/01_introduction.tex']),
    'terminology_previous_entries_preserved': (paper/'docs/TERMINOLOGY.md').read_text(encoding='utf-8').startswith((run/'before/docs/TERMINOLOGY.md').read_text(encoding='utf-8')),
    'new_words_without_verified_corpus_match': [w for w, hits in new_words.items() if not hits],
    'pdf_pages': len(pdf.pages),
    'revised_phrases_present_in_pdf': {p: normalize(p) in pdf_text for p in phrases},
    'compile': 'success' if 'Output written on main.xdv' in log else 'not_confirmed',
    'compile_command': 'tectonic --only-cached --keep-logs --keep-intermediates main.tex; successful exit recorded by caller',
    'overfull_boxes': bool(re.search(r'Overfull \\[hv]box', log)),
    'undefined_references_or_citations': bool(re.search(r'(?:Reference|Citation).+undefined|There were undefined references', log)),
    'source_sha256': digest(paper/'sections/02_system_model.tex'),
    'pdf_sha256': digest(paper/'main.pdf'),
}
previous = run/'VALIDATION.json'
if previous.exists():
    old = json.loads(previous.read_text(encoding='utf-8'))
    if old.get('pdf_sha256') == result['pdf_sha256'] and 'visual_review' in old:
        result['visual_review'] = old['visual_review']
(run/'VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
assert result['numbered_equation_content_and_order_unchanged']
assert result['unnumbered_display_content_unchanged'] and result['all_labels_unchanged']
assert not result['unexpected_protected_changes']
assert result['terminology_previous_entries_preserved']
assert not result['new_words_without_verified_corpus_match']
assert all(result['revised_phrases_present_in_pdf'].values())
assert not result['overfull_boxes'] and not result['undefined_references_or_citations']
assert result['compile']=='success'
