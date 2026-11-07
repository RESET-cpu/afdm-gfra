"""Render the audited C-STMP interim summary with the shared manuscript style."""
import math
from pathlib import Path

from common import execute
from data import PlotData, digest, read
import style


def load_interim(source, experiment):
    source = Path(source).resolve()
    if source.is_dir():
        source /= 'SUMMARY.json'
    complete_path = source.parent/'COMPLETE.json'
    complete = read(complete_path)
    if complete['status'] != 'COMPLETE':
        raise ValueError('The paired interim snapshot is not complete.')
    recorded = {str(Path(p).resolve()): h for p, h in complete['files'].items()}
    for name in ('SUMMARY.json', 'AUDIT.json', 'per_scene.csv'):
        path = source.parent/name
        if recorded.get(str(path.resolve())) != digest(path):
            raise ValueError(f'Interim source hash differs: {path}')
    for path, expected in recorded.items():
        if digest(path) != expected:
            raise ValueError(f'Original completed output hash differs: {path}')
    summary, audit = read(source), read(source.parent/'AUDIT.json')
    run = source.parent.parent
    plan_path = run/'inference/PLAN.json'
    plan = read(plan_path)
    if digest(plan_path) != summary['main_plan_sha256']:
        raise ValueError('Frozen main plan hash differs.')
    scenes, methods = summary['scene_count'], summary['methods']
    snrs = [c['snr_db'] for c in plan['conditions']]
    if (summary['scene_ids'] != list(range(scenes))
            or summary['inputs_per_method'] != scenes*len(snrs)
            or complete['inputs_per_method'] != summary['inputs_per_method']
            or audit['status'] != 'PASS'
            or audit['paired_inputs'] != summary['inputs_per_method']
            or audit['results'] != summary['inputs_per_method']*len(methods)):
        raise ValueError('Paired scene coverage disagrees with the saved audit.')
    rows, keys = [], set()
    for saved in summary['rows']:
        key = (saved['method'], saved['snr_db'])
        if key in keys or saved['scenes'] != scenes:
            raise ValueError('Duplicate or incompletely paired data row.')
        keys.add(key)
        nmse = 10*math.log10(saved['full_error']/saved['signal_energy'])
        aer = (saved['misses']+saved['false_alarms'])/(saved['active']+saved['inactive'])
        if not math.isclose(nmse, saved['nmse_db'], abs_tol=1e-9) or not math.isclose(aer, saved['aer'], abs_tol=1e-12):
            raise ValueError('Saved metrics disagree with counts or energy sums.')
        rows.append(dict(saved, parameters={'snr_db': saved['snr_db']}))
    if keys != {(m, s) for m in methods for s in snrs}:
        raise ValueError('Missing method/SNR combination.')
    metadata = dict(source_summary=str(source), source_sha256=digest(source),
        source_plan=str(plan_path), source_plan_sha256=digest(plan_path),
        source_complete=str(complete_path), source_complete_sha256=digest(complete_path),
        status='INTERIM', mode='saved paired C-STMP results', planned_scenes=1000,
        phase_mode=summary['phase_mode'], noise_mode=summary['noise_mode'],
        scene_ids=summary['scene_ids'], run_stage=read(run/'STATUS.json')['stage'])
    return PlotData(experiment, rows, methods, scenes, metadata)


def draw(data, out, args):
    # Zero observations have no logarithm: show them in their own categorical strip.
    fig = style.plt.figure(figsize=(7.16, 4.0))
    grid = fig.add_gridspec(2, 2, height_ratios=(4, 1))
    nmse = fig.add_subplot(grid[:, 0])
    aer = fig.add_subplot(grid[0, 1])
    zeros = fig.add_subplot(grid[1, 1], sharex=aer)
    style.panel(nmse, data, 'snr_db', 'SNR (dB)', 'nmse_db')
    nmse.set_title('(a) Channel estimation', pad=4)
    nmse.legend(loc='upper right', ncol=2, frameon=True, fancybox=False,
        framealpha=1, facecolor='white', edgecolor='#777777', handlelength=2.4,
        borderpad=.35, labelspacing=.25, handletextpad=.55, borderaxespad=.45,
        columnspacing=.7).get_frame().set_linewidth(.45)
    positive, xvalues, zero_methods = [], [], []
    for method in data.methods:
        rows = sorted((r for r in data.rows if r['method'] == method), key=lambda r: r['snr_db'])
        x = [r['snr_db'] for r in rows]
        y = [r['aer'] if r['aer'] > 0 else math.nan for r in rows]
        positive.extend(r['aer'] for r in rows if r['aer'] > 0)
        xvalues.extend(x)
        aer.plot(x, y, label=style.LABELS[method], clip_on=False, **style.style(method))
        zx = [r['snr_db'] for r in rows if r['aer'] == 0]
        if zx:
            zero_methods.append(method)
            zero_style = style.style(method)
            zero_style['linestyle'] = 'None'
            zeros.plot(zx, [len(zero_methods)]*len(zx), clip_on=False, **zero_style)
    style.axes_style(aer, '', 'AER', xvalues, yscale='log')
    aer.set_ylim(min(positive)*.6, 10**math.ceil(math.log10(max(positive))))
    aer.legend(loc='upper right', ncol=2, frameon=True, fancybox=False,
        framealpha=1, facecolor='white', edgecolor='#777777', handlelength=2.4,
        borderpad=.35, labelspacing=.25, handletextpad=.55, borderaxespad=.45,
        columnspacing=.7).get_frame().set_linewidth(.45)
    aer.tick_params(labelbottom=False)
    aer.set_title('(b) Activity detection', pad=4)
    zeros.set_yticks(range(1, len(zero_methods)+1), [style.LABELS[m] for m in zero_methods])
    zeros.set_ylim(len(zero_methods)+.6, .4)
    zeros.set_xticks(sorted(set(xvalues)))
    zeros.set_xlim(min(xvalues), max(xvalues))
    zeros.set_xlabel('SNR (dB)', labelpad=3)
    zeros.set_title('Observed AER = 0', fontsize=9, pad=3)
    zeros.tick_params(axis='y', labelsize=8, length=0, pad=3)
    zeros.tick_params(axis='x', direction='in', length=3, width=.55, pad=3)
    zeros.grid(axis='x', color='#b9b9b9', linewidth=.45, alpha=.8)
    style.save(fig, out, 'comparison')
    outputs = [('comparison', True)]
    notes = ['AER is a probability on a logarithmic axis. Observed zeros are shown only in the separate categorical strip below the AER panel, with their actual SNRs; no floor or pseudocount is substituted. Lines are broken at zero observations.']
    notes.extend([
        'C-STMP uses the classifier retrained for 100 epochs (selected epoch 90 EMA), derivative variance and beta=0.4; STMP uses beta=0.2.',
        'Baseline threshold development overlaps these evaluation scenes: this is a retrospective comparison.',
        'Full experiment status at plotting: '+data.metadata['run_stage']+'.',
        'Presentation only; all 48 saved NMSE/AER pairs and all observed zeros are unchanged.'
    ])
    return outputs, notes


if __name__ == '__main__':
    raise SystemExit(execute('snr_comparison', draw, load_data=load_interim))
