from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys

sys.path.append('C:/Users/25911/.cache/codex-pymupdf')
import pymupdf
from PIL import Image, ImageDraw

RUN = Path(__file__).resolve().parent
PAPER = RUN.parents[1]
RENDER = RUN / 'render'
RENDER.mkdir(exist_ok=True)
POPPLER = Path('C:/Users/25911/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

source_hashes = json.loads((RUN / 'SOURCE_HASHES.json').read_text(encoding='utf-8-sig'))
result = {'source_files_unchanged': all(sha(PAPER / p).upper() == h for p, h in source_hashes.items()), 'versions': {}}
for name in ['main', 'main_full']:
    path = PAPER / f'{name}.pdf'
    doc = pymupdf.open(path)
    text = '\n\f\n'.join(p.get_text() for p in doc)
    (RUN / f'{name}_text.txt').write_text(text, encoding='utf-8')
    log = (PAPER / f'{name}.log').read_text(encoding='utf-8', errors='replace')
    shutil.copy2(PAPER / f'{name}.log', RUN / f'{name}.log')
    version = {
        'pages': len(doc), 'sha256': sha(path),
        'undefined_references': bool(re.search(r'undefined references|(?:Citation|Reference) .+ undefined', log, re.I)),
        'overfull_boxes': 'Overfull' in log,
        'underfull_boxes': len(re.findall('Underfull', log)),
        'missing_characters': 'Missing character' in log,
        'reference_count': len(re.findall(r'\\bibitem', (PAPER / f'{name}.bbl').read_text(encoding='utf-8'))),
        'contains_new_paragraph_wording': all(s in re.sub(r'\s+', ' ', text) for s in ['iterates between linear estimation and joint denoising', 'We retain the same symbols for the normalized quantities']),
        'appendix_c_present': 'RECEIVERCONFIGURATIONSANDEVALUATIONPROTOCOL' in re.sub(r'\s+', '', text).upper(),
    }
    assert not any(version[k] for k in ['undefined_references', 'overfull_boxes', 'missing_characters'])
    assert version['contains_new_paragraph_wording']
    assert version['appendix_c_present'] == (name == 'main_full')
    result['versions'][name] = version
    if '--skip-render' not in sys.argv:
        subprocess.run([str(POPPLER), '-r', '90', '-png', str(path), str(RENDER / name)], check=True, capture_output=True)
    pages = sorted(RENDER.glob(f'{name}-*.png'))
    assert len(pages) == len(doc)
    for start in range(0, len(pages), 8):
        selected = pages[start:start+8]
        sheet = Image.new('RGB', (1440, 1020), '#e6e6e6')
        draw = ImageDraw.Draw(sheet)
        for j, page in enumerate(selected):
            im = Image.open(page).convert('RGB')
            im.thumbnail((345, 480))
            x, y = (j % 4) * 360, (j // 4) * 510
            sheet.paste(im, (x + (360-im.width)//2, y+25))
            draw.text((x+12, y+7), page.stem, fill='black')
        sheet.save(RENDER / f'overview-{name}-{start//8+1}.png')
assert result['source_files_unchanged']
(RUN / 'VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
