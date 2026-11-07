"""Scientific plotting checks with explicitly synthetic, temporary result summaries."""
import importlib
import json
import math
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

PLOTS = Path(__file__).resolve().parents[1] / 'evaluation' / 'plots'
sys.path.insert(0, str(PLOTS))
import data as plot_data
import style
from common import execute

CONDITIONS = {
    'snr_comparison': [{'snr_db': s} for s in [-4, -2, 0, 2, 4, 6]],
    'pilot_frames': [{'frames': n} for n in [8, 16, 24, 32, 40, 48]],
    'user_count': [{'users': n} for n in [20, 40, 60, 80, 100]],
    'activity_probability': [{'activity_probability': p} for p in [.05, .1, .15, .2, .25]],
    'cross_channel': [{'channel_model': p, 'snr_db': s} for p in ['D', 'A', 'B', 'C'] for s in [-4, -2, 0, 2, 4, 6]],
    'channel_denoising': [{'variance': v} for v in [.001, .01, .1, 1, 10, 100]],
    'runtime_comparison': [{'snr_db': s} for s in [-4, 0, 4]],
    'density_ratio_ablation': [{'snr_db': s} for s in [-4, -2, 0, 2, 4, 6]],
}


def fixture(tmp_path, experiment='snr_comparison'):
    denoise = experiment == 'channel_denoising'
    methods = ['noisy', 'gaussian', 'genie_bound', 'pretrained_first', 'pretrained_colored_first'] if denoise else ['STMP', 'offgrid_sbl', 'gnn', 'gamp', 'somp']
    if experiment == 'density_ratio_ablation':
        methods = ['proposed', 'STMP', 'STMP_gaussian']
    plan = dict(experiment=experiment, experiment_kind='denoiser' if denoise else 'receiver',
                conditions=CONDITIONS[experiment], methods=methods, scene_count=2, mode='SYNTHETIC_PLOT_TEST',
                phase_mode='known', noise_mode='estimated', algorithm_specs={m: {'label': m} for m in methods})
    rows = []
    for i, condition in enumerate(plan['conditions']):
        for j, method in enumerate(methods):
            error = (j + 1) / (i + 1)
            row = dict(condition=i, parameters=condition, method=method, completed=2,
                       nmse_db=10 * math.log10(error / 10))
            if denoise:
                row.update(error=error, energy=10)
            else:
                row.update(full_error=error, signal_energy=10, misses=j+1, false_alarms=0,
                           active=8, inactive=72, aer=(j+1)/80,
                           mean_end_to_end_seconds=(j+1)*.2 + i*.01,
                           backend='cuda' if method == 'STMP' else 'cpu')
            rows.append(row)
    summary = dict(status='COMPLETE', experiment=experiment, rows=rows)
    (tmp_path / 'PLAN.json').write_text(json.dumps(plan), encoding='utf-8')
    source = tmp_path / 'SUMMARY.json'
    source.write_text(json.dumps(summary), encoding='utf-8')
    return source, plan, summary


@pytest.mark.parametrize('change,match', [
    ('count', 'same fully paired'), ('aer', 'pooled metrics'),
    ('energy', 'pooled metrics'), ('missing', 'same fully paired'),
])
def test_reject_unpaired_or_inconsistent_metrics(tmp_path, change, match):
    source, plan, summary = fixture(tmp_path)
    if change == 'count': summary['rows'][0]['completed'] = 1
    elif change == 'aer': summary['rows'][0]['aer'] += .1
    elif change == 'energy': summary['rows'][0]['full_error'] *= 2
    else: summary['rows'].pop()
    source.write_text(json.dumps(summary), encoding='utf-8')
    with pytest.raises(ValueError, match=match):
        plot_data.load(source, 'snr_comparison')


def test_wrong_experiment_and_unaudited_interim(tmp_path):
    source, plan, summary = fixture(tmp_path)
    with pytest.raises(ValueError, match='Expected user_count'):
        plot_data.load(source, 'user_count')
    summary['status'] = 'INTERIM'
    source.write_text(json.dumps(summary), encoding='utf-8')
    with pytest.raises(ValueError, match='shared physical scenes'):
        plot_data.load(source, 'snr_comparison')


def test_zero_aer_remains_zero(tmp_path):
    source, _, summary = fixture(tmp_path)
    summary['rows'][0].update(aer=0, misses=0, false_alarms=0)
    source.write_text(json.dumps(summary), encoding='utf-8')
    data = plot_data.load(source, 'snr_comparison')
    fig, ax = style.plt.subplots()
    assert style.panel(ax, data, 'snr_db', 'SNR (dB)', 'aer') == 'linear'
    assert ax.lines[0].get_ydata()[0] == 0
    style.plt.close(fig)
    with pytest.raises(ValueError, match='zero AER'):
        style.aer_scale([0, .01], 'log')


def test_concurrent_runtime_rejected_before_output(tmp_path):
    source, plan, _ = fixture(tmp_path, 'runtime_comparison')
    plan['timing'] = 'Concurrent throughput experiment, not isolated method latency'
    (tmp_path / 'PLAN.json').write_text(json.dumps(plan), encoding='utf-8')
    with pytest.raises(SystemExit) as error:
        execute('runtime_comparison', None, ['--input', str(source), '--output', str(tmp_path/'out')])
    assert error.value.code == 2
    assert not (tmp_path/'out').exists()


@pytest.mark.parametrize('experiment', CONDITIONS)
def test_each_entry_draws_actual_coordinates_and_fits_page(tmp_path, monkeypatch, experiment):
    source, _, _ = fixture(tmp_path, experiment)
    data = plot_data.load(source, experiment)
    style.configure()
    rendered = []

    def inspect(fig, out, name):
        style.compact_layout(fig)
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        for ax in fig.axes:
            if not ax.get_visible(): continue
            bounds = ax.get_tightbbox(renderer)
            assert bounds.x0 >= -1 and bounds.y0 >= -1, (experiment, bounds)
            assert bounds.x1 <= fig.bbox.x1 + 1 and bounds.y1 <= fig.bbox.y1 + 1, (experiment, bounds)
            assert len(ax.lines) == len(data.methods)
            if experiment == 'snr_comparison':
                assert list(ax.lines[0].get_xdata()) == [-4, -2, 0, 2, 4, 6]
        rendered.append(name)
        style.plt.close(fig)

    monkeypatch.setattr(style, 'save', inspect)
    outputs, _ = importlib.import_module(experiment).draw(data, tmp_path, SimpleNamespace(aer_scale='auto'))
    assert rendered == [name for name, _ in outputs]
