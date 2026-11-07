from pathlib import Path
import hashlib, json, shutil, sys
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
PAPER=ROOT/'paper/C-STMP'
cfg=ROOT/'src/configs/plots/manuscript.json'
paths=[cfg,ROOT/'FINAL.json',ROOT/'MAINLINE.json',PAPER/'main.tex',PAPER/'main_full.tex',
       PAPER/'main.pdf',PAPER/'main_full.pdf',PAPER/'references.bib',
       *PAPER.joinpath('sections').glob('*.tex'),*PAPER.joinpath('figures').glob('*.pdf')]
hashes={}
for p in paths:
    rel=p.relative_to(ROOT); dest=OUT/'before'/rel
    assert not dest.exists(),dest
    dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,dest)
    hashes[rel.as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'BEFORE_HASHES.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
raw=cfg.read_bytes()
assert raw.count(b'#ff6699')==9
cfg.write_bytes(raw.replace(b'#ff6699',b'#ff00ff'))

sys.path.insert(0,str(ROOT/'src/evaluation/plots'))
from manuscript.vector import fitz
source=ROOT/'reference/literature/shen2025.pdf'
counts={}
with fitz.open(source) as doc:
    for number in [13,14]:
        counts[number]=sum(d.get('color')==(1.,0.,1.) for d in doc[number-1].get_drawings())
        assert counts[number]>0
info={'title':'LEO Satellite-Enabled Random Access With Large Differential Delay and Doppler Shift',
      'path':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
      'pdf_pages_one_based':[13,14],'figures':[6,7,8,9],
      'series':'On-grid ConvSBL-GAMP+MP','rgb':[1,0,1],'hex':'#ff00ff',
      'method':'Exact vector stroke color, checked against rendered page 13',
      'matching_strokes_by_page':counts}
(OUT/'SHEN_SOURCE.json').write_text(json.dumps(info,indent=2),encoding='utf-8')

def prepend(p,text):
    s=p.read_text(encoding='utf-8');title,rest=s.split('\n',1)
    p.write_text(title+'\n\n'+text+'\n'+rest,encoding='utf-8')
prepend(PAPER/'figures/README.md',
        '2026-11-05 最新配色：按作者要求，STMP 改用 Shen 图 6–9 的亮粉色 **#ff00ff**，GP-MP/GP-MP-EP 保持红色；七幅实验图和两版 PDF 同步。出处见[取色记录](../checks/stmp_shen_pink_20261105/SHEN_SOURCE.json)。')
p=ROOT/'src/evaluation/plots/manuscript/README.md'
s=p.read_text(encoding='utf-8').replace('STMP 基线统一使用Xu 图 9–11 所用的粉色 `#ff6699`',
                                      'STMP 基线统一使用 Shen 图 6–9 所用的亮粉色 `#ff00ff`（2026-11-05 作者最新要求）')
p.write_text(s,encoding='utf-8')
with (PAPER/'docs/REVIEW_DECISIONS.md').open('a',encoding='utf-8') as f:
    f.write('\n\n## 2026-11-05：STMP 改用 Shen 原图亮粉色\n\n作者主动要求 STMP 换更亮的粉色并指定 Shen 原图。本次从本地 shen2025.pdf 第 13–14 页图 6–9 的 On-grid ConvSBL-GAMP+MP 矢量曲线读取 RGB(1,0,1)，采用 #ff00ff，覆盖此前 Xu #ff6699 及更早偏红配色决定。七幅实验图、双面板内外配置共九处颜色同步；GP-MP/GP-MP-EP 名称、红色和全部数据保持。没有修改正文文字、实验或模型绑定。证据见 [SHEN_SOURCE.json](../checks/stmp_shen_pink_20261105/SHEN_SOURCE.json) 和本轮 VALIDATION.json。\n')
(OUT/'README.md').write_text('# STMP 使用 Shen 原图亮粉色\n\n作者要求更亮的粉色并参考 Shen，采用原图矢量颜色 #ff00ff。七幅实验图和两版论文 PDF 同步；原来的圆圈、虚线、其他曲线颜色及数据保持。\n\nSHEN_SOURCE.json 保存来源页码、图号和哈希；BEFORE_HASHES.json 与 before/ 保存改前文件；PLOT_VALIDATION.json 保存曲线和绘图检查；VALIDATION.json 保存颜色、文本、数据和编译核验。\n',encoding='utf-8')
print('STMP color: #ff6699 -> #ff00ff (9 settings).')
