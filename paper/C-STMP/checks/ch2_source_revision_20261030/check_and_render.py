from pathlib import Path
import hashlib
import json
import re
import subprocess
from pypdf import PdfReader

out = Path(__file__).resolve().parent
repo = out.parents[3]
paper = repo / 'paper/C-STMP'
manifest = json.loads((out / 'REVISION_MANIFEST.json').read_text(encoding='utf-8'))
report = json.loads((out / 'APPLY_REPORT.json').read_text(encoding='utf-8'))
audit = json.loads((out.parent / 'ch2_sentence_source_check_20261030/FINAL_AUDIT.json').read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(paper / 'sections/02_system_model.tex') == report['source_after_sha256']
before = (out / 'before.tex').read_text(encoding='utf-8')
after = (paper / 'sections/02_system_model.tex').read_text(encoding='utf-8')
equations = lambda text: [re.sub(r'\s+', '', block) for block in re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}', text, re.S)]
assert equations(before) == equations(after) and len(equations(after)) == 14
assert re.findall(r'\\label\{([^}]+)\}', before) == re.findall(r'\\label\{([^}]+)\}', after)
concurrent = json.loads((out / 'CONCURRENT_CHANGES.json').read_text(encoding='utf-8'))
for name, digest in manifest['protected_files'].items():
    expected = concurrent['observed_sha256'].get(name, digest)
    assert sha(repo / name) == expected, 'New concurrent modification: ' + name

rows = []
for paragraph in audit['paragraphs']:
    for old in paragraph['sentences']:
        matching = [op for op in report['operations'] if old['id'] in op['old_ids']]
        new = old['draft_tex']
        for op in matching:
            assert op['old'] in new, old['id']
            new = new.replace(op['old'], op['new'], 1)
        if matching:
            action = 'REVISED'
        elif old['id'] == 'P12.S03':
            action = 'RETAINED_FORMULA_EXPLANATION'
        else:
            action = 'RETAINED'
        rows.append({'old_id': old['id'], 'old_category': old['category'], 'action': action,
                     'new_tex': new, 'source_refs': [r for op in matching for r in op['source_refs']] or old['source_refs'],
                     'reasons': [op['change_reason'] for op in matching]})
assert len(rows) == 54
supported = [r for r in rows if r['old_category'] == 'SUPPORTED_PARAPHRASE']
assert len(supported) == 21
assert all(r['action'] == 'REVISED' or r['old_id'] == 'P12.S03' for r in supported)
assert 'working posterior' not in (paper / 'sections/02_system_model.tex').read_text(encoding='utf-8').lower()
(out / 'SENTENCE_DISPOSITION.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

log = (paper / 'main.log').read_text(encoding='utf-8', errors='replace')
bad = re.findall(r'^.*(?:undefined references|Reference .* undefined|Citation .* undefined|multiply[- ]defined|Overfull \\[hv]box|Missing character|^! ).*$', log, re.M | re.I)
assert not bad, bad
reader = PdfReader(paper / 'main.pdf')
page_text = [p.extract_text() or '' for p in reader.pages]
(out / 'compiled_pdf_text.txt').write_text('\n\n'.join(f'===== PAGE {i+1} =====\n{text}' for i,text in enumerate(page_text)), encoding='utf-8')
assert 'working posterior' not in '\n'.join(page_text).lower()
assert 'joint posterior distribution' in '\n'.join(page_text).lower()
pages = [2, 3, 4, 5, len(page_text)]
previews = out / 'previews'
previews.mkdir(exist_ok=True)
for n in pages:
    subprocess.run(['pdftoppm', '-f', str(n), '-l', str(n), '-scale-to', '1800', '-png', '-singlefile',
                    str(paper / 'main.pdf'), str(previews / f'page-{n:02d}')], check=True, capture_output=True)
checks = {'old_sentences_accounted_for': len(rows), 'supported_paraphrases_revised': 20,
          'formula_explanation_retained': 'P12.S03', 'working_posterior_replaced': True,
          'numbered_equations_unchanged': 14,
          'protected_file_hashes_match_except_documented_concurrent_changes': True,
          'concurrent_changes_preserved': concurrent,
          'pdf_pages': len(reader.pages), 'blocking_latex_diagnostics': bad,
          'rendered_pages': pages, 'pdf_sha256': sha(paper / 'main.pdf'),
          'source_sha256': sha(paper / 'sections/02_system_model.tex'), 'visual_review': 'pending'}
(out / 'VALIDATION.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(checks, ensure_ascii=False))
