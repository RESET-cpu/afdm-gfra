"""Accuracy versus measured end-to-end time, with computation backends shown."""
import math
from common import execute_public as execute
import style


def panel(ax, data, metric, scale):
    xs = []
    for method in data.methods:
        group = sorted((r for r in data.rows if r['method'] == method), key=lambda r: r['parameters']['snr_db'])
        backends = {r['backend'] for r in group}
        if len(backends) != 1:
            raise ValueError('A runtime curve must use one computation backend per method.')
        x = [r['mean_end_to_end_seconds'] for r in group]
        if any(not math.isfinite(v) or v <= 0 for v in x):
            raise ValueError('Measured end-to-end times must be positive and finite.')
        label = style.LABELS[method] + ' / ' + str(next(iter(backends)))
        ax.plot(x, [r[metric] for r in group], label=label, clip_on=False, **style.style(method))
        for row, t in zip(group, x):
            ax.annotate(f'{row["parameters"]["snr_db"]:g}', (t, row[metric]),
                        xytext=(3, 4), textcoords='offset points', fontsize=8)
        xs.extend(x)
    style.axes_style(ax, 'Mean end-to-end time (s)', 'AER' if metric == 'aer' else 'NMSE (dB)',
                     xs, 'log', scale if metric == 'aer' else 'linear')
    if metric == 'aer' and scale == 'linear':
        ax.set_ylim(bottom=0)
    if metric == 'nmse_db':
        style.nmse_axis(ax, [r[metric] for r in data.rows])


def draw(data, out, args):
    scale = style.aer_scale([r['aer'] for r in data.rows], args.aer_scale)
    fig, axes = style.plt.subplots(1, 2, figsize=(7.16, 2.90))
    for ax, metric, title in zip(axes, ('nmse_db', 'aer'), ('(a) Channel estimation', '(b) Activity detection')):
        panel(ax, data, metric, scale)
        ax.set_title(title, pad=4)
    style.save(fig, out, 'runtime_comparison')
    outputs = [('runtime_comparison', True)]
    for metric, suffix in [('nmse_db', 'nmse'), ('aer', 'aer')]:
        fig, ax = style.plt.subplots(figsize=(3.5, 2.65))
        panel(ax, data, metric, scale)
        name = 'runtime_comparison_' + suffix
        style.save(fig, out, name)
        outputs.append((name, False))
    return outputs, [f'AER uses a {scale} axis. Point annotations give SNR in dB; lines join points in SNR order.',
                     'Times include phase processing and retain the measured CPU/GPU backends. Cross-backend time ratios do not isolate algorithmic complexity.']


if __name__ == '__main__':
    raise SystemExit(execute('runtime_comparison', draw))
