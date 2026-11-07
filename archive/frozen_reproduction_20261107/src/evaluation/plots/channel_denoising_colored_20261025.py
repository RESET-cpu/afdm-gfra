"""Render the historical nine curves plus the paired colored-trained first network."""
import math
from pathlib import Path

from common import execute
from data import PlotData, digest, read
from channel_denoising import load_denoising, HISTORICAL_METHODS, HISTORICAL_LABELS, historical_style
import style

METHOD = 'pretrained_colored_first'


def load_append(source, experiment):
    source = Path(source).resolve()
    if source.is_dir():
        source = source/'SUMMARY.json'
    plan_path = source.parent/'PLAN.json'
    plan, summary = read(plan_path), read(source)
    audit_path = source.parent/'VERIFICATION.json'
    audit = read(audit_path)
    if (plan.get('schema') != 'direct-awgn-colored-append-v1'
            or plan['scene_count'] != 500 or summary['status'] != 'COMPLETE'
            or audit['status'] != 'PASS' or audit['paired_input_conditions'] != 3000
            or not audit['original_54_rows_unchanged']
            or summary['source_plan_sha256'] != digest(plan_path)
            or audit['new_summary_sha256'] != digest(source)):
        raise ValueError('A complete verified 500-scene append is required')
    original = Path(plan['source_summary'])
    if digest(original) != plan['source_summary_sha256']:
        raise ValueError('Original summary changed')
    old = load_denoising(original, experiment)
    if summary['rows'][:54] != read(original)['rows'] or len(summary['rows']) != 60:
        raise ValueError('The original 54 points must remain unchanged')
    rows = list(old.rows)
    seen = set()
    for saved in summary['rows'][54:]:
        row = dict(saved)
        variance = row['variance']
        if (row['method'] != METHOD or variance in seen or variance not in plan['variances']
                or row['scenes'] != 500 or row['samples'] != 2000
                or not math.isclose(10*math.log10(row['error']/row['energy']), row['nmse_db'], abs_tol=1e-10)
                or not math.isclose(-10*math.log10(variance), row['snr_db'], abs_tol=1e-10)):
            raise ValueError('Appended curve identity or pooled metric differs')
        seen.add(variance)
        row.update(parameters=dict(variance=variance, snr_db=row['snr_db']),
                   condition=plan['variances'].index(variance))
        rows.append(row)
    metadata = dict(old.metadata, source_summary=str(source), source_sha256=digest(source),
                    source_plan=str(plan_path), source_plan_sha256=digest(plan_path),
                    source_audit=str(audit_path), source_audit_sha256=digest(audit_path),
                    original_summary=str(original), original_summary_sha256=digest(original),
                    mode='historical 500-scene AWGN comparison with one appended first network',
                    appended_pairing=plan['pairing'],
                    labels=dict(HISTORICAL_LABELS, **{METHOD: 'Colored-trained score'}))
    return PlotData(experiment, rows, [*HISTORICAL_METHODS[:2], METHOD, *HISTORICAL_METHODS[2:]], 500, metadata)


def draw(data, out, args):
    fig, ax = style.plt.subplots(figsize=(3.5, 3.8))
    handles, xs, ys = {}, [], []
    for method in data.methods:
        rows = sorted((r for r in data.rows if r['method']==method), key=lambda r:r['snr_db'])
        x, y = [r['snr_db'] for r in rows], [r['nmse_db'] for r in rows]
        handles[method], = ax.plot(x, y, label=data.metadata['labels'][method], clip_on=False,
                                  zorder=5 if method==METHOD else 3,
                                  **historical_style(method))
        xs.extend(x); ys.extend(y)
    style.axes_style(ax, 'SNR (dB)', 'NMSE (dB)', xs)
    style.nmse_axis(ax, ys)
    ax.get_legend().remove()
    opts = dict(frameon=True, fancybox=False, framealpha=1, facecolor='white',
                edgecolor='#777777', handlelength=2.4, borderpad=.35,
                labelspacing=.15, handletextpad=.55, borderaxespad=.25)
    references = ax.legend(handles=[handles[m] for m in data.methods[:6]], loc='lower left', fontsize=8, **opts)
    references.get_frame().set_linewidth(.45)
    ax.add_artist(references)
    baselines = ax.legend(handles=[handles[m] for m in HISTORICAL_METHODS[5:]], loc='upper right', **opts)
    baselines.get_frame().set_linewidth(.45)
    style.save(fig, out, 'channel_denoising')
    return [('channel_denoising', False)], [
        'The original nine curves and all 54 saved points are unchanged.',
        'The added curve uses the colored-trained 50,000-channel first network, epoch 200 EMA, at C=vI.',
        'All 3,000 regenerated query/truth/standard-noise hash triples exactly match the historical cloud first-network inputs.',
        'Historical cloud/local platform differences for the original baselines remain as documented.',
        'NMSE = 10 log10(sum squared error / sum channel energy); four correlated candidates per physical scene.',
        'SNR = -10 log10(v) in fixed training coordinates. Genie retains its oracle side information.',
        'This is an AWGN comparison of first-network means; no second network or classifier is used.',
        'Six measured points per curve; no smoothing or statistical significance claim.']


if __name__ == '__main__':
    raise SystemExit(execute('channel_denoising', draw, load_data=load_append))
