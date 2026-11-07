from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PAPER = ROOT/'paper/C-STMP'
config_path = ROOT/'src/configs/plots/manuscript.json'
files = [config_path, PAPER/'main.tex', PAPER/'main_full.tex', PAPER/'main.pdf', PAPER/'main_full.pdf',
         ROOT/'FINAL.json', ROOT/'MAINLINE.json', *PAPER.joinpath('sections').glob('*.tex'),
         *PAPER.joinpath('figures').glob('*.pdf')]
hashes = {}
for p in files:
    rel = p.relative_to(ROOT)
    dest = OUT/'before'/rel
    assert not dest.exists(), dest
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(p,dest)
    hashes[rel.as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'BEFORE_HASHES.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')

# Display labels only; leave result keys, input paths, hashes and all styles intact.
raw = config_path.read_bytes()
config_path.write_bytes(raw.replace(b'CGP-MP',b'GP-MP'))
for p in [PAPER/'main.tex', *PAPER.joinpath('sections').glob('*.tex')]:
    raw=p.read_bytes()
    if b'CGP-MP' in raw:
        p.write_bytes(raw.replace(b'CGP-MP',b'GP-MP'))

# Remove the previous round's name-transition explanations.
p=PAPER/'sections/05_overall_algorithm.tex'
t=p.read_text(encoding='utf-8')
t=t.replace('pair with a common magnitude scale from the GP-MP implementation\nidentified in Section~\\ref{sec:compared-receivers}.',
            'pair with a common magnitude scale.')
p.write_text(t,encoding='utf-8')
p=PAPER/'sections/06_simulation_results.tex'
t=p.read_text(encoding='utf-8')
t=t.replace('The results in this section use an implementation of GP-MP trained with\ncolored Gaussian perturbations, denoted by GP-MP. Its training settings\nare specified below; receiver evaluation retains the scalar noise model\nin \\eqref{eq:pseudo-awgn}.\n\n','')
t=t.replace('\\item \\textbf{GP-MP:} The GP-MP implementation trained with colored\nGaussian noise; EP denotes estimated phases.',
            '\\item \\textbf{GP-MP:} The proposed receiver; EP denotes estimated phases.')
p.write_text(t,encoding='utf-8')
p=PAPER/'sections/appendix_evaluation_protocol.tex'
t=p.read_text(encoding='utf-8').replace('The GP-MP implementation of GP-MP uses','GP-MP uses')
p.write_text(t,encoding='utf-8')

def prepend(p, text):
    t=p.read_text(encoding='utf-8')
    title,rest=t.split('\n',1)
    p.write_text(title+'\n\n'+text+'\n'+rest,encoding='utf-8')

for method in ['C-STMP','STMP','DU']:
    prepend(ROOT/f'paper/{method}/docs/TERMINOLOGY.md',
        '**2026-11-05 最新展示名称（作者要求）：** 论文方法统一使用已有作者标签 **GP-MP**，估计相位版本为 **GP-MP-EP**；STMP 基线保持。GP/MP 沿用 generative-prior/message passing，未新增文献术语。名称不再编码训练噪声颜色；数据、权重与历史标识按原记录溯源。此次先统一图例及正文名称，实验完成后另行替换数据。')
prepend(PAPER/'figures/README.md',
        '2026-11-05：七幅实验图统一使用 **GP-MP**，估计相位版使用 **GP-MP-EP**。现有数据与样式保持，见[核验记录](../checks/gp_mp_legends_20261105/VALIDATION.json)。以下带日期名称属于历史记录。')
prepend(PAPER/'README.md',
        '2026-11-05：图例及正文方法名称统一为 **GP-MP**，估计相位版为 **GP-MP-EP**；两版 PDF 同步。最新名称覆盖以下历史状态说明。')
with (PAPER/'docs/REVIEW_DECISIONS.md').open('a',encoding='utf-8') as f:
    f.write('\n\n## 2026-11-05：按作者要求先统一 GP-MP 图例\n\n作者要求先把图例改为 GP-MP，后续实验完成后替换数据，不添加额外说明。本次统一七幅实验图及正文名称，估计相位版保留 EP 后缀；删除上一轮新增的名称过渡说明。只改变展示标签，原始数据、559 个绘图点、训练事实与数值保持，数据实际来源仍由绘图配置的原路径和 SHA-256 记录。未启动实验、未改模型绑定。\n')
(OUT/'README.md').write_text('# GP-MP 图例统一\n\n按作者要求，将 CGP-MP / CGP-MP-EP 展示为 GP-MP / GP-MP-EP，正文同名引用同步，删除名称过渡说明；保留数据、样式、真实训练设置和来源哈希。后续实验完成后另行替换数据。\n\n`before/` 为修改前备份；`PLOT_VALIDATION.json` 保存逐曲线数据及绘图检查；`VALIDATION.json` 保存标签、配置、编译及版面检查。\n',encoding='utf-8')
print('Display labels updated.')
