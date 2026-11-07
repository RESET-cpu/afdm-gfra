from pathlib import Path
import hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
PAPER=ROOT/'paper/C-STMP'
cfg=ROOT/'src/configs/plots/manuscript.json'
paths=[cfg,ROOT/'FINAL.json',ROOT/'MAINLINE.json',PAPER/'main.tex',PAPER/'main_full.tex',
       PAPER/'main.pdf',PAPER/'main_full.pdf',PAPER/'references.bib',
       *PAPER.joinpath('sections').glob('*.tex'),*PAPER.joinpath('figures').glob('*.pdf')]
hashes={}
for p in paths:
    rel=p.relative_to(ROOT);dest=OUT/'before'/rel
    assert not dest.exists(),dest
    dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    hashes[rel.as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'BEFORE_HASHES.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
raw=cfg.read_bytes()
assert raw.count(b'#0066cc')==8
cfg.write_bytes(raw.replace(b'#0066cc',b'#0000ff'))

sys.path.insert(0,str(ROOT/'src/evaluation/plots'))
from manuscript.vector import fitz
source=ROOT/'reference/literature/shen2025.pdf'
with fitz.open(source) as doc:
    strokes=sum(d.get('color')==(0.,0.,1.) for d in doc[12].get_drawings())
    assert strokes>0
info={'path':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
      'pdf_page_one_based':13,'figures':[6,7],
      'series':'On-grid / Off-grid MRF-MP-GAMP-CNN','rgb':[0,0,1],'hex':'#0000ff',
      'matching_strokes':strokes,'method':'Exact vector stroke color; original rendered page checked in preceding color revision.'}
(OUT/'SHEN_SOURCE.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
def prepend(p,text):
    s=p.read_text(encoding='utf-8');title,rest=s.split('\n',1)
    p.write_text(title+'\n\n'+text+'\n'+rest,encoding='utf-8')
prepend(PAPER/'figures/README.md',
    '2026-11-05 最新蓝色：Off-grid SBL 改用 Shen 图 6–7 的亮蓝色 **#0000ff**，六幅相关图和两版 PDF 同步。STMP 亮粉色与其他样式保持。出处见[取色记录](../checks/offgrid_shen_blue_20261105/SHEN_SOURCE.json)。')
p=ROOT/'src/evaluation/plots/manuscript/README.md'
s=p.read_text(encoding='utf-8')
needle='### 算法配色约定（2026-11-04 作者确认）\n'
assert needle in s
s=s.replace(needle,needle+'\n- Off-grid SBL 使用 Shen 图 6–7 的亮蓝色 `#0000ff`（2026-11-05 作者要求），保留方块标记和虚线。\n',1)
p.write_text(s,encoding='utf-8')
with (PAPER/'docs/REVIEW_DECISIONS.md').open('a',encoding='utf-8') as f:
    f.write('\n\n## 2026-11-05：蓝色改用 Shen 原图亮蓝色\n\n作者要求蓝色也换成 Shen 的亮蓝色。直接从 shen2025.pdf 第13页图6–7矢量曲线读取 RGB(0,0,1)，将 Off-grid SBL 从 #0066cc 改为 #0000ff。六幅相关图及双面板内外配置共八处同步；原数据、图例名称、标记、线型、STMP 粉色、正文与冻结资产保持，两版 PDF 同步。来源及核验见 [本轮记录](../checks/offgrid_shen_blue_20261105/README.md)。\n')
(OUT/'README.md').write_text('# Off-grid SBL 使用 Shen 原图亮蓝色\n\n按作者要求，将六幅图中 Off-grid SBL 的 #0066cc 改为 Shen 原图矢量色 #0000ff，双面板内外配置同步，其他颜色和样式保持。数据、正文及冻结模型保持。\n\nSHEN_SOURCE.json 保存取色来源；BEFORE_HASHES.json 与 before/ 保存改前版本；PLOT_VALIDATION.json 保存曲线检查；VALIDATION.json 保存编译、文本与颜色核验。\n',encoding='utf-8')
print('Off-grid SBL: #0066cc -> #0000ff (8 settings).')
