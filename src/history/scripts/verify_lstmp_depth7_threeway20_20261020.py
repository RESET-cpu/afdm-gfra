"""Rescore all sixty saved predictions and audit paired scene/weight bindings."""
import argparse
import csv
import importlib.util
import json
from pathlib import Path
import time

import numpy as np

ROOT = Path(r'C:\Users\25911\Desktop\afdm-gfra')
OUT = ROOT/'results/lstmp_depth7_threeway20_20261020'


def close(a, b):
    if not np.isclose(a, b, rtol=1e-10, atol=1e-12):
        raise AssertionError((a, b))


def audit(out):
    source = out/'source/evaluate_lstmp_depth7_threeway_20261020.py'
    spec = importlib.util.spec_from_file_location('frozen_depth7_evaluation', source)
    E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E)
    plan, report, complete, binding = [E.read(out/name) for name in ('PLAN.json','SUMMARY.json','COMPLETE.json','BINDING.json')]
    if (out/'RUNNING.lock').exists(): raise ValueError('Evaluation still running')
    E.verify_plan(out, plan)
    assert E.readiness(Path(plan['training_run']))[0]
    assert complete['scene_counts'] == dict.fromkeys(E.METHODS, 20)
    assert E.sha(out/'PLAN.json') == binding['plan_sha256'] == complete['plan_sha256']
    assert E.sha(out/'SUMMARY.json') == complete['summary_sha256']
    run = Path(plan['training_run'])
    assert E.sha(run/'COMPLETE.json') == binding['training_complete_sha256']
    assert E.sha(run/plan['new_checkpoint']) == binding['selected_seven_sha256']
    assert binding['frozen_five_sha256'] == plan['five_layer_binding']['checkpoint_sha256']
    with (out/'summary.csv').open(encoding='utf-8-sig', newline='') as f: summary_csv = list(csv.DictReader(f))
    with (out/'per_scene.csv').open(encoding='utf-8-sig', newline='') as f: scene_csv = list(csv.DictReader(f))
    assert len(summary_csv) == 3 and len(scene_csv) == 60
    paired = {}
    for method in E.METHODS:
        folder = out/method; rows = [E.read(folder/f'{i:03d}.json') for i in range(20)]
        assert len(list(folder.glob('[0-9][0-9][0-9].json'))) == 20
        for row, case in zip(rows, plan['cases']):
            i = case['index']; trace = E.read(folder/f'{i:03d}_trace.json')
            assert row['status'] == 'COMPLETE' and row['case_index'] == i and row['seed'] == case['seed']
            assert row['input_sha256'] == case['input_sha256']
            assert row['prediction_sha256'] == E.sha(folder/f'{i:03d}.npz')
            if method in E.DEPTHS:
                depth = E.DEPTHS[method]
                assert row['iterations'] == depth and row['converged'] is None
                assert row['stopping_reason'] == f'FIXED_{depth}_LAYERS' and len(trace['diagnostics']) == depth
                assert row['first_score_calls'] == depth and row['second_score_calls'] == 0
            else:
                assert trace['checkpoint_sha256'] == plan['old_binding']['checkpoint_sha256']
                with np.load(out/'cases'/f'{i:03d}'/'input.npz') as public:
                    expected = dict(plan['old_binding']['applied_configuration'], device=plan['device'],
                                    activity_prior=float(public['activity_prior']))
                assert trace['configuration'] == expected
                assert row['iterations'] <= 600 and len(trace['trace']) == row['iterations']
            with np.load(folder/f'{i:03d}.npz', allow_pickle=False) as z:
                estimate, probability = z['estimate'], z['probabilities']
            with np.load(out/'cases'/f'{i:03d}'/'truth.npz', allow_pickle=False) as z:
                truth, active = z['channel'], z['activity'].astype(bool)
            assert np.isfinite(estimate).all() and np.isfinite(probability).all()
            assert np.all((probability >= 0) & (probability <= 1))
            error = np.abs(estimate.astype(np.complex128)-truth)**2; energy = np.abs(truth)**2
            close(float(error.sum()), row['error_energy']); close(float(energy.sum()), row['truth_energy'])
            close(float(error.sum()/energy.sum()), row['nmse'])
            close(float(error[active].sum()), row['active_error_energy'])
            assert row['misses'] == int(np.sum(active & (probability < .5)))
            assert row['false_alarms'] == int(np.sum(~active & (probability >= .5)))
            assert row['active'] == int(active.sum()) and row['inactive'] == int((~active).sum())
            close(row['preparation_seconds']+row['inference_seconds'], row['total_seconds'])
            cr = next(r for r in scene_csv if r['method'] == method and int(r['case_index']) == i)
            for key, value in row.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool): close(float(cr[key]), value)
                elif value is not None: assert cr[key] == str(value)
        summary = report['methods'][method]; cr = next(r for r in summary_csv if r['method'] == method)
        for key, value in summary.items():
            if isinstance(value, (int, float)): close(float(cr[key]), value)
        total = lambda key: sum(r[key] for r in rows)
        close(summary['pooled_nmse_db'], 10*np.log10(total('error_energy')/total('truth_energy')))
        close(summary['mean_scene_nmse_db'], 10*np.log10(np.mean([r['nmse'] for r in rows])))
        close(summary['aer'], (total('misses')+total('false_alarms'))/800)
        close(summary['missed_detection_rate'], total('misses')/total('active'))
        close(summary['false_alarm_rate'], total('false_alarms')/total('inactive'))
        close(summary['mean_seconds'], np.mean([r['total_seconds'] for r in rows]))
        close(summary['median_seconds'], np.median([r['total_seconds'] for r in rows]))
        assert summary['fixed_depth_scenes'] == (20 if method in E.DEPTHS else 0)
        paired[method] = rows
    indices = np.random.default_rng(2026102097).integers(0, 20, size=(10000, 20))
    boot = {}
    for method, rows in paired.items():
        a = lambda key: np.asarray([r[key] for r in rows])[indices].sum(1)
        boot[method] = dict(nmse_db=10*np.log10(a('error_energy')/a('truth_energy')),
            aer=(a('misses')+a('false_alarms'))/800, missed_detection_rate=a('misses')/a('active'),
            false_alarm_rate=a('false_alarms')/a('inactive'), mean_seconds=a('total_seconds')/20)
    intervals = {other: {key: np.quantile(boot[E.METHODS[0]][key]-boot[other][key], [.025,.975]).tolist()
                         for key in boot[other]} for other in E.METHODS[1:]}
    for other in E.METHODS[1:]:
        new, old = report['methods'][E.METHODS[0]], report['methods'][other]
        delta = report['paired_seven_comparisons'][other]
        close(delta['seven_minus_other_nmse_db'], new['pooled_nmse_db']-old['pooled_nmse_db'])
        close(delta['seven_minus_other_aer'], new['aer']-old['aer'])
        close(delta['other_over_seven_seconds'], old['mean_seconds']/new['mean_seconds'])
    # Compare the final models over the same full validation pool and its strata.
    five = E.read(Path(plan['five_layer_binding']['run'])/'checkpoints/depth_5/best_validation.json')
    seven = E.read(run/'checkpoints/depth_7/best_validation.json')
    assert len(five['rows']) == len(seven['rows']) == 1200
    assert [(r['seed'], r['snr'], r['condition']) for r in five['rows']] == [(r['seed'], r['snr'], r['condition']) for r in seven['rows']]
    validation = dict(scope='Checkpoint-selection validation, not held-out test',
        frozen_five=dict(summary=five['summary'], by_condition=five['by_condition'], layer_summary=five['layer_summary']),
        trained_seven=dict(summary=seven['summary'], by_condition=seven['by_condition'], layer_summary=seven['layer_summary']))
    E.write(out/'VALIDATION_COMPARISON.json', validation)
    result = dict(status='PASSED', checked_unix=time.time(),
        checks=['All three methods 20/20; every prediction independently rescored',
                'Input, truth, source, parent and selected depth-seven checkpoint bindings verified',
                'All seven stage budgets complete; five-layer checkpoint preserved',
                'CSV, JSON, timing, iterations and network call counts checked',
                'Same 1200 validation scenes and conditions retained'],
        paired_bootstrap_seven_minus_other_95_percentile=intervals, bootstrap_resamples=10000,
        uncertainty_note='Descriptive paired scene bootstrap for one condition; not an equal-accuracy speed guarantee or population zero-error claim.',
        plan_sha256=E.sha(out/'PLAN.json'), summary_sha256=E.sha(out/'SUMMARY.json'),
        per_scene_csv_sha256=E.sha(out/'per_scene.csv'))
    E.write(out/'RESULT_AUDIT.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, default=OUT)
    print(json.dumps(audit(parser.parse_args().output), ensure_ascii=False))
