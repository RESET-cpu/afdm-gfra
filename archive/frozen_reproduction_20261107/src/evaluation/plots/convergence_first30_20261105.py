"""Plot NMSE for the first 30 paired scenes and 150 saved iterations."""
from pathlib import Path
import csv
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'src'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

from utils import read_json, write_json, sha256
from evaluation.convergence_20261105.run import checked, load_case, case_name
from evaluation.convergence_20261105.metrics import aggregate
from evaluation.plots import style

SOURCE = ROOT / 'result/snr_comparison/data/convergence_50x300_20261105'
OUTPUT = ROOT / 'result/snr_comparison/figures/convergence_first30_300_20261105'
SCENES = list(range(30))
DISPLAY_ITERATIONS = 150
STYLE_KEYS = {
    'GP-MP': 'C_STMP',
    'STMP': 'STMP',
    'Off-grid SBL (7)': 'offgrid_sbl',
}


def main():
    plan_hash = read_json(SOURCE / 'PLAN_HASH.json')['sha256']
    checked(SOURCE / 'PLAN.json', plan_hash)
    plan = read_json(SOURCE / 'PLAN.json')
    assert plan['scene_ids'][:30] == SCENES and plan['iterations'] == 300
    assert set(STYLE_KEYS).issubset(plan['methods'])
    for name in ('run.py', 'metrics.py'):
        path = ROOT / 'src/evaluation/convergence_20261105' / name
        checked(path, plan['assets'][str(path.resolve())])

    curves, paired, evidence = {}, {}, {}
    for method in STYLE_KEYS:
        traces = {}
        for scene in SCENES:
            trace = load_case(SOURCE, plan, method, scene)
            if scene in paired:
                np.testing.assert_array_equal(trace['truth_activity'], paired[scene][0])
                np.testing.assert_equal(trace['signal_energy'], paired[scene][1])
            else:
                paired[scene] = (trace['truth_activity'], trace['signal_energy'])
            traces[scene] = trace
            relative = Path('cases') / case_name(method, scene) / 'RESULT.json'
            evidence[relative.as_posix()] = sha256(SOURCE / relative)
        curves[method] = aggregate(traces, SCENES, plan['iterations'])

    OUTPUT.mkdir(parents=True, exist_ok=True)
    serial = {m: {k: v.tolist() if isinstance(v, np.ndarray) else v
                  for k, v in data.items()} for m, data in curves.items()}
    write_json(OUTPUT / 'PLOT_DATA.json', {
        'scope': 'Author-adopted first 30 paired scenes; original 50-scene experiment stopped',
        'scene_ids': SCENES, 'scene_count': 30, 'iterations': 300,
        'displayed_iterations': DISPLAY_ITERATIONS, 'displayed_metric': 'nmse_db',
        'displayed_methods': list(STYLE_KEYS),
        'snr_db': plan['snr_db'], 'phase_mode': plan['phase_mode'],
        'noise_mode': plan['noise_mode'], 'source': str(SOURCE),
        'plan_sha256': plan_hash, 'result_sha256': evidence,
        'scoring': plan['scoring'], 'curves': serial,
    })
    with (OUTPUT / 'curves.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['method', 'iteration', 'nmse_db', 'aer'])
        for method, data in curves.items():
            writer.writerows(zip([method] * 300, data['iteration'], data['nmse_db'], data['aer']))

    style.configure()
    plt.rcParams.update({'font.size': 8.5, 'axes.labelsize': 8.5,
                         'xtick.labelsize': 8.5, 'ytick.labelsize': 8.5,
                         'legend.fontsize': 8})
    palette_path = ROOT / 'src/configs/plots/manuscript.json'
    palette = read_json(palette_path)['figures']['snr_comparison']['styles']
    styles = {m: dict(palette[key]) for m, key in STYLE_KEYS.items()}
    for i, opts in enumerate(styles.values()):
        opts.update(linewidth=1., markersize=3.5,
                    markevery=sorted(set([0, DISPLAY_ITERATIONS-1] +
                                        list(range(9 + 3*i, DISPLAY_ITERATIONS-1, 20)))))
    plotted_points = 0

    def panel(ax):
        nonlocal plotted_points
        for method, data in curves.items():
            x = data['iteration'][:DISPLAY_ITERATIONS]
            y = data['nmse_db'][:DISPLAY_ITERATIONS]
            label = 'Off-grid SBL' if method == 'Off-grid SBL (7)' else method
            line, = ax.plot(x, y, label=label, **styles[method])
            np.testing.assert_array_equal(line.get_xdata(), x)
            np.testing.assert_array_equal(line.get_ydata(), y)
            plotted_points += len(x)
        ax.set_xlabel('Receiver iteration')
        ax.set_ylabel('NMSE (dB)')
        ax.set_xlim(1, DISPLAY_ITERATIONS)
        ax.set_xticks([1, 25, 50, 75, 100, 125, 150])
        ax.tick_params(which='both', direction='in', top=True, right=True)
        ax.grid(True, which='major', color='#b9b9b9', linewidth=.45, alpha=.65)
        values = np.concatenate([c['nmse_db'][:DISPLAY_ITERATIONS] for c in curves.values()])
        lo, hi = 5*np.floor(values.min()/5), max(0., 5*np.ceil(values.max()/5))
        ax.set_ylim(lo, hi if hi > lo else lo + 5)
        ax.yaxis.set_major_locator(MultipleLocator(5))

    fig, ax = plt.subplots(figsize=(3.5, 2.65))
    fig.subplots_adjust(left=.155, right=.975, top=.97, bottom=.18)
    panel(ax)
    legend = ax.legend(loc='upper right', handlelength=2.4,
                       frameon=True, fancybox=False, framealpha=1,
                       edgecolor='#777777')
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    box = legend.get_window_extent(renderer)
    assert 0 <= box.x0 < box.x1 <= fig.bbox.width
    assert 0 <= box.y0 < box.y1 <= fig.bbox.height
    assert not any(line.get_path().transformed(line.get_transform()).intersects_bbox(box, filled=False)
                   for line in ax.lines)
    assert plotted_points == 450
    for suffix in ('pdf', 'svg', 'png'):
        fig.savefig(OUTPUT / f'convergence_30_scenes.{suffix}', dpi=250)
    plt.close(fig)
    write_json(OUTPUT / 'VALIDATION.json', {
        'status': 'PASS', 'paired_scenes': 30, 'complete_cases': len(evidence),
        'actual_iterations_per_case': 300, 'plotted_points': plotted_points,
        'displayed_iterations': DISPLAY_ITERATIONS, 'displayed_metric': 'nmse_db',
        'displayed_methods': list(STYLE_KEYS), 'all_case_hashes_checked': True,
        'all_methods_same_truth': True, 'curves_match_saved_arrays': True,
        'legend_within_canvas_and_not_overlapping_curves': True,
        'palette_source': str(palette_path), 'palette_sha256': sha256(palette_path),
        'script_sha256': sha256(__file__),
        'smoothing': False, 'iteration_padding': False,
        'final_values': {m: {'nmse_db': float(c['nmse_db'][-1]), 'aer': float(c['aer'][-1])}
                         for m, c in curves.items()},
    })
    (OUTPUT / 'README.md').write_text(
        '# 前 30 个配对场景的收敛图\n\n'
        '固定使用场景 0–29、SNR = 0 dB、已知相位、观测估计噪声。'
        '每种算法每个场景均实际执行 300 次迭代，共核验 90 份完整结果。'
        '按作者 2026-11-06 要求，仅绘制前 150 次迭代的 NMSE，'
        '保留 GP-MP、STMP 和原基础配置 Off-grid SBL (7)。'
        'NMSE 按总误差能量除以总活动信号能量后转为 dB。'
        '不平滑，不补齐，不按结果筛选场景。\n\n'
        '作者已采用本图替换论文收敛图，并停止原 50 场景批次。'
        '图例使用 Off-grid SBL，不标注预算编号；底层仍为原 7 点基础配置。'
        '所选 90 份结果的完整 300 轮数据仍保存在原实验中。\n\n'
        '本脚本仅读取已保存结果，不运行推断。论文图由统一入口 '
        '`src/evaluation/plots/render_paper.py --figures convergence` 生成。\n\n'
        '复现：在仓库根目录运行 `.venv/Scripts/python.exe -X utf8 -B '
        'src/evaluation/plots/convergence_first30_20261105.py`。\n', encoding='utf-8')
    print(OUTPUT)
    print({m: {'nmse_db': round(float(c['nmse_db'][-1]), 4),
               'aer': round(float(c['aer'][-1]), 6)} for m, c in curves.items()})


if __name__ == '__main__':
    main()
