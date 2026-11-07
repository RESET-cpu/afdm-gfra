"""Apply the author's STMP / GP-MP / GP-MP-C naming decision; no inference."""
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PAPER = ROOT / 'paper/C-STMP'
records = {}


def read(path):
    return path.read_text(encoding='utf-8-sig')


def save(path, value):
    relative = path.relative_to(ROOT)
    if path.exists():
        backup = HERE / 'before' / relative
        if backup.exists():
            raise RuntimeError(f'Backup already exists: {relative}')
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup)
        records[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    path.write_text(value, encoding='utf-8', newline='\n')


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f'Expected exactly one occurrence: {old}')
    return text.replace(old, new, 1)


# Preserve the current reading copies and all seven experiment figures.
for path in [PAPER/'main.pdf', PAPER/'main_full.pdf', *PAPER.joinpath('figures').glob('*.pdf')]:
    backup = HERE / 'before' / path.relative_to(ROOT)
    backup.parent.mkdir(parents=True, exist_ok=True)
    if backup.exists():
        raise RuntimeError(f'Backup already exists: {path}')
    shutil.copy2(path, backup)
    records[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()


# Existing GP-MP results belong to the three-network STMP adaptation.
for name in ['01_introduction.tex', '06_simulation_results.tex',
             '07_conclusion.tex', 'appendix_evaluation_protocol.tex']:
    path = PAPER/'sections'/name
    old = read(path)
    new = re.sub(r'\bGP-MP\b(?!-)', 'STMP', old)
    if name == '01_introduction.tex':
        new = replace_once(new,
            'generative-prior message-passing (STMP) reference across the evaluated',
            'STMP baseline adapted to AFDM across the evaluated')
        new = replace_once(new,
            'detection and channel estimation performance compared with the white-noise-trained\n',
            'detection and channel estimation performance compared with the\n')
        new = replace_once(new,
            'errors and the white Gaussian noise used for training. This mismatch can\n',
            'errors and the white Gaussian noise used for training. Related limitations\n'
            'of the AWGN approximation under finite-dimensional, structured spatial\n'
            'compression are discussed in \\cite[Sec.~I]{wei2026lstmp}. This mismatch can\n')
    elif name == '06_simulation_results.tex':
        new = replace_once(new,
            '\\item \\textbf{STMP:} This AFDM adaptation of STMP \\cite{cai2026}\n'
            'uses a white-noise-trained first-order\n'
            'score network, a learned second-order score network, and a classifier\n'
            'for density ratio estimation.',
            '\\item \\textbf{STMP:} We adapt STMP \\cite{cai2026} to the multi-frame\n'
            'AFDM model, retaining its white-noise-trained first- and second-order\n'
            'score networks for conditional mean and variance estimation. We replace\n'
            'its Gaussian-message-based activity-probability update with a learned\n'
            'density-ratio estimator trained using the corresponding first-order network.')
        new = replace_once(new,
            '\\caption{Channel denoising under AWGN with known variance.\n'
            'AWGN and colored refer to the training noise.}',
            '\\caption{Channel denoising under AWGN with known variance.}')
        new = replace_once(new,
            'The denoiser trained with colored noise has lower NMSE at low SNR,\n'
            'whereas the white-noise-trained denoiser is more accurate at high SNR.',
            'The GP-MP-C denoiser has lower NMSE at low SNR,\n'
            'whereas the STMP denoiser is more accurate at high SNR.')
    elif name == '07_conclusion.tex':
        new = replace_once(new, 'over the white-noise-trained baseline,',
                           'over the adapted STMP baseline,')
    else:
        new = replace_once(new,
            'STMP follows the STMP framework \\cite{cai2026} adapted to the AFDM\n'
            'model, with learned activity probabilities replacing the analytical activity\n'
            'update.',
            'The STMP baseline adapts \\cite{cai2026} to the AFDM model, replacing\n'
            'the Gaussian-message-based activity-probability update with learned\n'
            'density-ratio estimation.')
    if new != old:
        save(path, new)

path = PAPER/'sections/05_overall_algorithm.tex'
save(path, replace_once(read(path),
    'We denote the proposed receiver by GP-MP-C, where C indicates\n'
    'training with colored Gaussian noise.',
    'We denote the proposed generative-prior message-passing receiver by GP-MP-C,\n'
    'where C indicates training with colored Gaussian noise. The corresponding\n'
    'AWGN-trained variant is denoted by GP-MP. It retains the same denoiser\n'
    'architecture, variance estimator, classifier training procedure, and receiver\n'
    'settings, with the classifier retrained using its own denoiser.'))

path = PAPER/'references.bib'
save(path, read(path) + '\n' + r'''@misc{wei2026lstmp,
  author = {Yiming Wei and Xiaojun Yuan},
  title = {Learned Score-Based Turbo Message Passing for Channel Recovery From Spatially Compressed Measurements},
  howpublished = {arXiv:2610.17785},
  year = {2026},
  source_url = {https://arxiv.org/abs/2610.17785v1},
}
''')

path = ROOT/'src/configs/plots/manuscript.json'
text = read(path)
assert text.count('"STMP": "GP-MP"') == 8
text = text.replace('"STMP": "GP-MP"', '"STMP": "STMP"')
text = replace_once(text, '"pretrained_colored_first": "Denoiser (colored)"',
                    '"pretrained_colored_first": "GP-MP-C"')
text = replace_once(text, '"proposed": "Denoiser (AWGN)"', '"proposed": "STMP"')
save(path, text)

path = PAPER/'README.md'
text = read(path)
start = text.index('当前稿件主算法展示名为')
end = text.index('\n', start)
text = text[:start] + ('当前稿件主算法展示名为 **GP-MP-C**；现有三网络 AFDM 适配基线统一称为 '
    '**STMP**，其中活动概率更新已替换为学习密度比估计。**GP-MP** 专指与当前方法同结构、同接收机设置的'
    '白噪声训练消融版本，须重新训练其配套分类器；该版本尚无正式评估曲线。估计相位版本仍为 '
    '**GP-MP-C-EP**。目录、算法内部标识和已保存实验数据保持。见'
    '[最新命名与消融记录](checks/stmp_baseline_white_ablation_20261104/README.md)。') + text[end:]
save(path, text)

path = PAPER/'figures/README.md'
text = replace_once(read(path),
    '本文方法与白噪声基线分别展示为 GP-MP-C、GP-MP。',
    '本文方法与现有三网络基线分别展示为 GP-MP-C、STMP。GP-MP 留给同结构白噪声训练消融，尚未加入曲线。')
save(path, text)

decision = ('**2026-11-04 作者确认 STMP 基线与 GP-MP 白噪声消融的命名：** '
    '现有三网络 GP-MP 统一改称 STMP，正文明确它是 Cai STMP 的 AFDM 适配版本，'
    '活动概率计算改为学习密度比估计。当前有色方法继续称 GP-MP-C；GP-MP 专指保持当前去噪网络结构、'
    '预条件、导数方差、分类器训练流程和接收机设置，仅将一阶训练扰动改为白高斯噪声的消融版本。'
    '分类器使用各自冻结的一阶网络重新训练，方差依各自一阶网络计算，这种联动属于训练干预的后续影响，'
    '不当作独立新增变量。Cai 的 AWGN 接口、本文有限维 AFDM 结构化观测，以及 Wei–Yuan '
    'L-STMP 引言（PDF p.1, Sec. I）对结构化压缩下 AWGN 条件的讨论共同构成动机；'
    '动机不代替有色训练收益的配对验证。STMP 与 GP-MP-C 是整体方法比较，GP-MP 与 GP-MP-C '
    '用于训练噪声消融。白噪声训练仍按已授权的“相位完成核验并退出 → 一阶 200 轮 → 分类器 100 轮”顺序，'
    '未取消或改变预算。本次不启动训练、不加入未完成的消融曲线。见'
    '[实施记录](../checks/stmp_baseline_white_ablation_20261104/README.md)。\n\n')
path = PAPER/'docs/REVIEW_DECISIONS.md'
text = read(path)
first_break = text.index('\n\n') + 2
save(path, text[:first_break]+decision+text[first_break:])

term = ('**2026-11-04 最新命名（作者确认）：** 现有三网络 AFDM 对照称 **STMP**，'
    '保留 Cai 的白噪声一、二阶网络与消息传递，并以学习密度比估计替换其活动概率公式；'
    '原文为 Cai §III-B, PDF p.7, 式(28)–(31)。**GP-MP-C** 为当前有色方法；'
    '**GP-MP** 为保持当前架构及接收机设置的白噪声训练消融，分类器随各自去噪器重新训练。'
    'GP-MP/GP-MP-C 是作者指定标签，不是文献既有方法名。历史同名记录按当时版本理解。'
    'Wei–Yuan *Learned Score-Based Turbo Message Passing for Channel Recovery From Spatially Compressed Measurements*, '
    'arXiv:2610.17785v1, Sec. I, PDF p.1 讨论有限维结构化压缩下的 AWGN 模型局限，'
    '只支撑失配动机，不提供本文 AFDM 有色训练的效果保证。'
    '原文、实现与比较边界见[本轮依据](../checks/stmp_baseline_white_ablation_20261104/README.md)。\n\n')
path = PAPER/'docs/TERMINOLOGY.md'
text = read(path)
save(path, text.replace('\n\n', '\n\n'+term, 1))
for method in ['STMP','DU']:
    path = ROOT/f'paper/{method}/docs/TERMINOLOGY.md'
    text = read(path)
    note = ('**2026-11-04 共用名称同步：** C-STMP 稿件中，旧三网络 GP-MP 对照改称 STMP '
        '（AFDM 适配并使用学习密度比活动估计），GP-MP 留给当前方法的同结构白噪声训练消融，'
        'GP-MP-C 仍为有色方法。内部算法 ID、该稿历史结果和冻结资产不变。'
        '出处与定义见 [C-STMP 术语最新记录](../../C-STMP/docs/TERMINOLOGY.md)。\n\n')
    save(path, text.replace('\n\n','\n\n'+note,1))

path = PAPER/'docs/README.md'
text = read(path)
note = ('2026-11-04 最新[STMP 基线与 GP-MP 白噪声消融命名](../checks/stmp_baseline_white_ablation_20261104/README.md)：'
        '旧 GP-MP 三网络对照改称 STMP；GP-MP 留给与 GP-MP-C 同结构、同接收机设置的白噪声训练消融。'
        '当前图不含尚未完成的新消融。以下记录按历史时点理解。\n\n')
save(path,text.replace('\n\n','\n\n'+note,1))

path = ROOT/'result/channel_denoising/data/white_preconditioned_matched_20261104/TRAINING_PLAN.json'
plan = json.loads(read(path))
plan['display_names'] = {'baseline_three_network': 'STMP', 'matched_white_ablation': 'GP-MP',
                         'colored_receiver': 'GP-MP-C',
                         'decision_date': '2026-11-04',
                         'internal_ids_and_scientific_settings_unchanged': True}
plan['interpretation']['required_comparison'] = (
    'GP-MP (matched white) versus GP-MP-C (colored): same evaluation inputs and C=vI queries, '
    'architecture, variance-estimation rule, classifier-training procedure and receiver settings. '
    'Independent denoising isolates the training intervention. Recomputed derivative variance and '
    'matched classifier training are downstream effects of the denoiser intervention.')
plan['interpretation']['null_gain'] = (
    'No observed GP-MP-C advantage over matched white GP-MP does not assign all STMP-to-GP-MP-C '
    'gains to neural architecture. STMP differs in denoiser parameterization, variance-estimation '
    'method, damping and query-variance update. The main SNR comparison shares basic minimum/'
    'maximum iterations and tolerance, while GP-MP-C additionally checks the variance-update residual. '
    'Account for paired uncertainty and retain unfavorable results.')
save(path, json.dumps(plan,ensure_ascii=False,indent=2)+'\n')

(HERE/'before_hashes.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
print(f'Updated {len(records)} tracked source/output snapshots; no experiment was launched.')
