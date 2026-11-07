from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path('src').resolve()))
sys.path.append(str(Path.home()/'.cache/codex-pymupdf'))
import pymupdf as fitz
from utils import read_json,write_json,sha256
root=Path.cwd(); check=root/'paper/C-STMP/checks/white_denoising_adopted_20261107'
for p,h in read_json(check/'BEFORE.json')['protected'].items(): assert sha256(root/p)==h,p
with fitz.open(root/'paper/C-STMP/main.pdf') as a,fitz.open(root/'paper/C-STMP/main_full.pdf') as b:
    for n in [6,7]: assert a[n].get_pixmap(dpi=140).samples==b[n].get_pixmap(dpi=140).samples
assert read_json(check/'RENDER.json')['status']=='PASS'
assert read_json(check/'DATA_VERIFICATION.json')['status']=='PASS'
validation=dict(status='PASS',protected_assets_unchanged=len(read_json(check/'BEFORE.json')['protected']),
    baseline_rows_unchanged=48,figure_layout_and_styles_preserved=True,
    visual_inspection=dict(figures=[3,4],manuscript_pages=[7,8,10],both_versions_inspected=True,
                           pages_7_8_pixel_identical=True,page_10_note='Full version includes existing appendix pointers; independently inspected.',
                           outcome='Readable labels and legends; no clipping, overlap or broken equations.'),
    compilation=read_json(check/'PDF_CHECK.json'),
    render_sha256=sha256(check/'RENDER.json'),data_sha256=sha256(check/'DATA_VERIFICATION.json'))
write_json(check/'VALIDATION.json',validation)
result=root/'result/channel_denoising/data/white_mainline_500_20261107'
write_json(result/'ADOPTION.json',dict(status='PASS',adopted_unix=time.time(),
    completion_sha256=sha256(result/'COMPLETION.json'),summary_sha256=sha256(result/'SUMMARY.json'),
    check=str(check/'VALIDATION.json'),check_sha256=sha256(check/'VALIDATION.json'),
    figures=[3,4],source=str(root/'result/channel_denoising/figures/white_mainline_500_20261107/PLOT_DATA.json'),
    coordinator_exited=True,old_data_unchanged=True,next_stage='pilot_frames'))
print('PASS: denoising adoption and both manuscript versions')
