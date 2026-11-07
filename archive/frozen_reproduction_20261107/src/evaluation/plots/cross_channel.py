"""Compare SNR curves separately for each saved channel profile."""
import math
from common import execute_public as execute
import style


def draw(data, out, args):
    profiles = list(dict.fromkeys(r['parameters']['channel_model'] for r in data.rows))
    aer_scale = style.aer_scale([r['aer'] for r in data.rows], args.aer_scale)
    outputs = []
    for metric, suffix in [('nmse_db', 'nmse'), ('aer', 'aer')]:
        nrows = math.ceil(len(profiles) / 2)
        fig, axes = style.plt.subplots(nrows, 2, figsize=(7.16, 2.65 * nrows), squeeze=False)
        used = []
        for i, (ax, profile) in enumerate(zip(axes.flat, profiles)):
            style.panel(ax, data.subset(channel_model=profile), 'snr_db', 'SNR (dB)', metric,
                        requested_aer_scale=aer_scale)
            ax.set_title(f'({chr(97+i)}) Channel {profile}', pad=4)
            used.append(ax)
        limits = [ax.get_ylim() for ax in used]
        for ax in used:
            ax.set_ylim(min(lo for lo, _ in limits), max(hi for _, hi in limits))
            if metric == 'nmse_db':
                style.nmse_axis(ax, [r['nmse_db'] for r in data.rows])
        for ax in list(axes.flat)[len(profiles):]:
            ax.set_visible(False)
        name = 'cross_channel_' + suffix
        style.save(fig, out, name)
        outputs.append((name, True))
    return outputs, [f'Channel profiles are shown separately with a common vertical scale. AER uses a {aer_scale} axis.']


if __name__ == '__main__':
    raise SystemExit(execute('cross_channel', draw))
