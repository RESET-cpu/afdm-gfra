from pathlib import Path
import hashlib
import json
import re
import sys
sys.path.append(str(Path.home() / '.cache/codex-pymupdf'))
import pymupdf as fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
CHECK = Path(__file__).resolve().parent
BEFORE = CHECK / 'before'
RENDER = CHECK / 'render'
RENDER.mkdir(exist_ok=True)
load = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
hash_file = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def diff(a, b, prefix=''):
    if a == b:
        return []
    if isinstance(a, dict) and isinstance(b, dict):
        assert a.keys() == b.keys()
        return [change for k in a for change in diff(a[k], b[k], prefix + '/' + k)]
    if isinstance(a, list) and isinstance(b, list):
        assert len(a) == len(b)
        return [change for i in range(len(a)) for change in diff(a[i], b[i], prefix + '/' + str(i))]
    return [[prefix, a, b]]

changes = diff(load(BEFORE / 'src/configs/plots/manuscript.json'), load(ROOT / 'src/configs/plots/manuscript.json'))
assert len(changes) == 9
assert all('/labels/' in p and a == 'GP-MP-C' and b == 'CGP-MP' for p, a, b in changes)
plot = load(CHECK / 'PLOT_VALIDATION.json')
previous = load(ROOT / 'paper/C-STMP/checks/stmp_xu_pink_20261104/PLOT_VALIDATION.json')
assert plot['status'] == 'PASS' and not plot['inference_started'] and not plot['training_started']
points = 0
figure_colors = {}
for name, fig in plot['figures'].items():
    assert fig['curves'] == previous['figures'][name]['curves']
    points += fig['point_count']
    doc = fitz.open(ROOT / f'paper/C-STMP/figures/{name}.pdf')
    assert 'CGP-MP' in doc[0].get_text() and 'GP-MP-C' not in doc[0].get_text()
    assert not doc[0].get_images()
    colors = [d['color'] for d in doc[0].get_drawings() if d['color']]
    count = lambda target: sum(max(abs(a-b) for a,b in zip(c,target)) < 1e-5 for c in colors)
    figure_colors[name] = {'xu_pink_strokes': count((1, .4, .6)), 'red_strokes': count((1, 0, 0))}
    assert all(v > 0 for v in figure_colors[name].values())
assert points == 547

hashes = load(CHECK / 'before_hashes.json')
tex_count = 0
protected_count = 0
for rel, sha in hashes.items():
    if rel.endswith('.tex'):
        before = (BEFORE / rel).read_bytes()
        after = (ROOT / rel).read_bytes()
        assert after == re.sub(rb'GP-MP-C(?![A-Za-z0-9])', b'CGP-MP', before), rel
        tex_count += 1
    elif rel.endswith('.bib') or rel in ['FINAL.json', 'MAINLINE.json'] or any(rel.endswith('/' + f + '.pdf') for f in ['system_multiframe', 'factor_graph', 'learned_receiver']):
        assert hash_file(ROOT / rel) == sha, rel
        protected_count += 1

plan_rel = 'result/channel_denoising/data/white_preconditioned_matched_20261104/TRAINING_PLAN.json'
plan_changes = diff(load(BEFORE / plan_rel), load(ROOT / plan_rel))
assert len(plan_changes) == 3
assert all(p.startswith('/interpretation/') or p == '/display_names/colored_receiver' for p, a, b in plan_changes)
assert all(b == a.replace('GP-MP-C', 'CGP-MP') for p, a, b in plan_changes)

pdfs = {}
all_tiles = []
for name, folder, expected_pages in [('main', 'build_main', 13), ('main_full', 'build_full', 15)]:
    old = fitz.open(BEFORE / f'paper/C-STMP/{name}.pdf')
    path = CHECK / folder / f'{name}.pdf'
    new = fitz.open(path)
    assert len(new) == expected_pages == len(old)
    text = '\n'.join(p.get_text() for p in new)
    assert 'CGP-MP' in text
    assert not re.search(r'GP-MP-C(?:CD)?', text)
    assert re.search(r'\[44\]', text)
    log = (CHECK / folder / f'{name}.log').read_text(errors='replace')
    assert not re.search(r'Overfull|undefined references|undefined citations|Missing character:', log, re.I)
    bbl = (CHECK / folder / f'{name}.bbl').read_text(errors='replace')
    assert bbl.count('\\bibitem') == 44
    changed_pages = []
    for i, page in enumerate(new):
        pix = page.get_pixmap(dpi=100)
        oldpix = old[i].get_pixmap(dpi=100)
        if pix.samples != oldpix.samples:
            changed_pages.append(i+1)
            full = page.get_pixmap(dpi=150)
            full.save(RENDER / f'{name}_p{i+1}.png')
            thumb = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
            thumb.thumbnail((490, 650))
            tile = Image.new('RGB', (510, 690), 'white')
            tile.paste(thumb, ((510-thumb.width)//2, 28))
            ImageDraw.Draw(tile).text((12, 8), f'{name} page {i+1}', fill='black')
            all_tiles.append(tile)
    pdfs[name] = {'pages': len(new), 'references': 44, 'changed_render_pages': changed_pages, 'sha256': hash_file(path)}

for batch_idx, start in enumerate(range(0, len(all_tiles), 6), 1):
    tiles = all_tiles[start:start+6]
    contact = Image.new('RGB', (510*3, 690*((len(tiles)+2)//3)), '#dddddd')
    for i,tile in enumerate(tiles):
        contact.paste(tile, (510*(i%3), 690*(i//3)))
    contact.save(RENDER / f'contact_{batch_idx}.png')

report = {'status': 'PASS', 'configuration_changes': changes, 'curves_unchanged': True,
    'plot_points': points, 'preserved_color_strokes': figure_colors,
    'tex_files_verified_exact_name_replacement': tex_count, 'protected_files_unchanged': protected_count,
    'training_plan_display_only_changes': plan_changes, 'pdfs': pdfs,
    'visual_review': 'PENDING'}
(CHECK / 'VALIDATION.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps({'status': 'PASS', 'points': points, 'pdfs': pdfs, 'contact_sheets': (len(all_tiles)+5)//6}, ensure_ascii=False))
