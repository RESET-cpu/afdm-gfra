from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[4]
CHECK = Path(__file__).resolve().parent
BEFORE = CHECK / 'before'
assert not BEFORE.exists(), 'Do not repeat the edit over the preserved snapshot.'

direct = [
    'README.md', 'paper/C-STMP/README.md',
    'src/configs/plots/manuscript.json',
    'src/evaluation/plots/manuscript/README.md',
    'result/channel_denoising/data/white_preconditioned_matched_20261104/TRAINING_PLAN.json',
]
docs = [
    'paper/C-STMP/figures/README.md', 'paper/C-STMP/docs/README.md',
    'paper/C-STMP/docs/REVIEW_DECISIONS.md',
    *[f'paper/{name}/docs/TERMINOLOGY.md' for name in ('STMP', 'C-STMP', 'DU')],
]
tex = sorted((ROOT / 'paper/C-STMP').glob('*.tex')) + sorted((ROOT / 'paper/C-STMP/sections').glob('*.tex'))
protected = [ROOT / 'paper/C-STMP/references.bib', ROOT / 'FINAL.json', ROOT / 'MAINLINE.json']
outputs = list((ROOT / 'paper/C-STMP/figures').glob('*.pdf')) + [ROOT / 'paper/C-STMP/main.pdf', ROOT / 'paper/C-STMP/main_full.pdf']
paths = [ROOT / p for p in direct + docs] + tex + protected + outputs
hashes = {}
for path in paths:
    rel = path.relative_to(ROOT)
    dest = BEFORE / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)
    hashes[rel.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
(CHECK / 'before_hashes.json').write_text(json.dumps(hashes, indent=2), encoding='utf-8')

def replace_bytes(path, before, after):
    raw = path.read_bytes()
    path.write_bytes(raw.replace(before.encode('utf-8'), after.encode('utf-8')))

def prepend_after_title(path, text):
    raw = path.read_bytes()
    newline = b'\r\n' if b'\r\n' in raw else b'\n'
    title, body = raw.split(newline, 1)
    path.write_bytes(title + newline * 2 + text.encode('utf-8') + newline + body)

for path in [ROOT / p for p in direct] + tex:
    raw = path.read_bytes()
    if path == ROOT / 'paper/C-STMP/README.md':
        current, history = raw.split('## 最近修订依据'.encode('utf-8'), 1)
        raw = re.sub(rb'GP-MP-C(?![A-Za-z0-9])', b'CGP-MP', current) + '## 最近修订依据'.encode('utf-8') + history
    else:
        raw = re.sub(rb'GP-MP-C(?![A-Za-z0-9])', b'CGP-MP', raw)
    path.write_bytes(raw)

# Keep dated historical records intact; new entries supersede their display names.
review = ROOT / 'paper/C-STMP/docs/REVIEW_DECISIONS.md'
replace_bytes(review, '# GP-MP-C 预审问题、讨论决定与剩余事项', '# CGP-MP 预审问题、讨论决定与剩余事项')
prepend_after_title(review,
    '**2026-11-04 最新命名（作者要求减少连字符）：** 当前方法由 GP-MP-C 简化为 **CGP-MP**；C 仍指有色高斯噪声训练，GP 和 MP 的含义保持。估计相位版本相应称 **CGP-MP-EP**，同结构白噪声消融仍为 **GP-MP**，现有三网络适配基线仍为 **STMP**。这是作者指定的算法展示名，不是新增文献术语。正文、算法标题、七幅实验图例、当前说明及训练计划的展示名称已同步；STMP 保留 Xu 粉色 `#ff6699`，本文方法保留红色。内部标识、模型绑定、训练配置及已有数据不变，既定训练顺序和条件性论述方案继续有效。下文旧名称按记录时点理解。见[实施核验](../checks/algorithm_name_cgp_mp_20261104/README.md)。')

for name in ('STMP', 'C-STMP', 'DU'):
    path = ROOT / f'paper/{name}/docs/TERMINOLOGY.md'
    link = '../checks/algorithm_name_cgp_mp_20261104/README.md' if name == 'C-STMP' else '../../C-STMP/checks/algorithm_name_cgp_mp_20261104/README.md'
    prepend_after_title(path,
        '**2026-11-04 最新名称简化（作者确认）：** **CGP-MP** 替代 GP-MP-C，C 表示 colored Gaussian noise training，GP/MP 对应 generative-prior/message passing。此名称是本文作者指定标签，未声称为已有文献的算法名；只是调整字母位置并减少一个连字符，原术语出处和方法含义沿用下文记录。估计相位版为 **CGP-MP-EP**；**GP-MP** 保留给当前结构的白噪声训练消融；**STMP** 为含学习密度比活动更新的三网络适配基线。历史名称按日期理解。见[同步记录](' + link + ')。')

prepend_after_title(ROOT / 'paper/C-STMP/docs/README.md',
    '2026-11-04 最新[算法名称简化](../checks/algorithm_name_cgp_mp_20261104/README.md)：当前方法统一称 **CGP-MP**，估计相位版为 **CGP-MP-EP**；GP-MP 白噪声消融及 STMP 基线名称保持。下面的旧名称保留为历史记录。')

figdoc = ROOT / 'paper/C-STMP/figures/README.md'
# Only update the current palette paragraph and current figure-description paragraph.
raw = figdoc.read_bytes()
parts = raw.split(b'\r\n\r\n' if b'\r\n' in raw else b'\n\n')
for i, part in enumerate(parts):
    if part.startswith('2026-11-04 最新配色'.encode()) or part.startswith('实验图沿用'.encode()):
        parts[i] = part.replace(b'GP-MP-C', b'CGP-MP')
separator = b'\r\n\r\n' if b'\r\n' in raw else b'\n\n'
figdoc.write_bytes(separator.join(parts))
prepend_after_title(figdoc,
    '2026-11-04 最新名称：七幅实验图中的 **GP-MP-C** 已统一改为 **CGP-MP**，两版论文已同步。Xu 粉色、其他样式和全部 547 个数据点保持，见[名称核验](../checks/algorithm_name_cgp_mp_20261104/README.md)。')

paper_readme = ROOT / 'paper/C-STMP/README.md'
replace_bytes(paper_readme,
    '见[最新命名与消融记录](checks/stmp_baseline_white_ablation_20261104/README.md)。',
    '见[最新名称简化](checks/algorithm_name_cgp_mp_20261104/README.md)及[基线与消融定义](checks/stmp_baseline_white_ablation_20261104/README.md)。')
prepend_after_title(paper_readme,
    '2026-11-04 作者确认将 GP-MP-C 简化为 **CGP-MP**；正文、图例和两版 PDF 已同步，C 仍表示有色高斯噪声训练。[本轮核验](checks/algorithm_name_cgp_mp_20261104/README.md)。')

changed = [rel for rel, sha in hashes.items() if hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() != sha]
(CHECK / 'SOURCE_CHANGES.json').write_text(json.dumps(changed, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'modified_source_files': len(changed), 'files': changed}, ensure_ascii=False))
