"""Check this figure/manuscript revision against its saved inputs and backups."""
from pathlib import Path
import hashlib
import json
import re
import sys

from PIL import Image, ImageDraw
sys.path.append(str(Path.home()/'.cache/codex-pymupdf'))
import pymupdf as fitz

CHECK = Path(__file__).resolve().parent
ROOT = CHECK.parents[3]

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

before = read(CHECK/'BEFORE_HASHES.json')
cfg = read(ROOT/'src/configs/plots/manuscript.json')
oldcfg = read(CHECK/'before/src/configs/plots/manuscript.json')
assert all(c == oldcfg['figures'][n] for n, c in cfg['figures'].items()
           if n != 'snr_comparison')
assert sum(c.get('point_count', 0) for c in cfg['figures'].values()) == 559
for name, digest in before.items():
    if name.startswith('paper/C-STMP/figures/') and name.endswith('.pdf') and not name.endswith('snr_comparison.pdf'):
        assert sha(ROOT/name) == digest, name
for name, digest in read(CHECK/'DATA_VALIDATION.json')['source_hashes'].items():
    assert sha(ROOT/name) == digest, name

oldplot = read(ROOT/'paper/C-STMP/checks/algorithm_name_cgp_mp_20261104/PLOT_VALIDATION.json')['figures']['snr_comparison']['curves']
newplot = read(CHECK/'PLOT_VALIDATION.json')['figures']['snr_comparison']
kept = [c for c in newplot['curves'] if c['method'] != 'C_STMP_phase_frontend_marginal_20261104']
assert kept == oldplot
assert newplot['point_count'] == 84 and newplot['pdf_images'] == 0
old = (CHECK/'before/paper/C-STMP/sections/05_overall_algorithm.tex').read_text(encoding='utf-8')
new = (ROOT/'paper/C-STMP/sections/05_overall_algorithm.tex').read_text(encoding='utf-8')
formula = lambda text: re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}', text, re.S)
assert formula(old) == formula(new)
assert len(formula(new)) == 7
sections = '\n'.join(p.read_text(encoding='utf-8') for p in (ROOT/'paper/C-STMP/sections').glob('*.tex'))
assert 'app:phase-refinement' not in sections

pages = {}
for stem, folder in [('main', 'build_main'), ('main_full', 'build_full')]:
    log = (CHECK/folder/(stem+'.log')).read_text(encoding='utf-8', errors='replace')
    bad = re.findall(r'^.*(?:Overfull|undefined|Missing character|Error).*$', log, re.M)
    assert not bad, bad
    changed, thumbs = [], []
    with fitz.open(CHECK/folder/(stem+'.pdf')) as doc, fitz.open(CHECK/'before/paper/C-STMP'/(stem+'.pdf')) as olddoc:
        assert len(doc) == (13 if stem == 'main' else 15)
        for i, page in enumerate(doc):
            if i >= len(olddoc) or page.get_pixmap(dpi=90).samples != olddoc[i].get_pixmap(dpi=90).samples:
                changed.append(i+1)
                dest = CHECK/'preview'/f'{stem}_{i+1:02}.png'
                page.get_pixmap(dpi=150).save(dest)
                im = Image.open(dest).convert('RGB')
                im.thumbnail((340,445))
                tile = Image.new('RGB',(360,480),'#ddd')
                tile.paste(im,((360-im.width)//2,25))
                ImageDraw.Draw(tile).text((10,5),f'{stem} page {i+1}',fill='black')
                thumbs.append(tile)
        text = '\n'.join(page.get_text() for page in doc)
        assert 'CGP-MP-EP' in text and '0.30–0.61' in text and 'Gaussian marginal-likelihood' in text
        assert all(i > 6 for i in changed)
        pages[stem] = {'pages':len(doc), 'changed_pages':changed,
                      'first_six_pages_pixel_identical_90dpi':True,
                      'references':len(re.findall(r'\\bibitem',(CHECK/folder/(stem+'.bbl')).read_text(encoding='utf-8'))),
                      'sha256':sha(CHECK/folder/(stem+'.pdf'))}
    sheet = Image.new('RGB',(1440,480*((len(thumbs)+3)//4)),'#ddd')
    for i, tile in enumerate(thumbs):
        sheet.paste(tile,((i%4)*360,(i//4)*480))
    sheet.save(CHECK/'preview'/f'{stem}_contact.png')

report = {'status':'PASS', 'original_72_snr_points_exactly_unchanged':True,
          'new_snr_points':12, 'other_nine_figure_pdf_hashes_unchanged':True,
          'other_nine_figure_configurations_unchanged':True,
          'chapter_v_numbered_equations_unchanged':True,
          'seven_experiment_points':559, 'snr_vector_pdf_embedded_images':0,
          'pilot_regression':read(CHECK/'PILOT_REGRESSION.json')['comparison'],
          'source_hashes_rechecked':True, 'pdfs':pages,
          'inference_started':False, 'training_started':False,
          'known_limitations':'Retrospective paired comparison; no inferential test or claim of activity-error equivalence.'}
(CHECK/'FINAL_VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(CHECK/'PDF_PAGE_CHECK.json').write_text(json.dumps(pages,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
