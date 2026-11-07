"""Summarize existing validation records without running or changing a receiver."""
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics


ROOT = Path(__file__).resolve().parents[1]
RUNS = Path('D:/afdm-gfra-cpu/runs')
FIVE = RUNS / 'lstmp_refinenet_50000_epoch6_20261020'
SIX = RUNS / 'lstmp_refinenet_depth7_20261020'
OUT = ROOT / 'results/lstmp_five_layer_diagnosis_20261020'
SOURCES = {}


def read(path):
    data = path.read_bytes()
    SOURCES[str(path)] = hashlib.sha256(data).hexdigest()
    return json.loads(data)


def summary(rows):
    keys = ['error_energy', 'truth_energy', 'active_error_energy',
            'inactive_error_energy', 'misses', 'false_alarms', 'active', 'inactive']
    total = {k: sum(r[k] for r in rows) for k in keys}
    return dict(scenes=len(rows), **total,
                pooled_nmse_db=10 * math.log10(total['error_energy'] / total['truth_energy']),
                aer=(total['misses'] + total['false_alarms']) / (total['active'] + total['inactive']),
                missed_detection_rate=total['misses'] / total['active'],
                false_alarm_rate=total['false_alarms'] / total['inactive'],
                mean_scene_nmse=statistics.mean(r['nmse'] for r in rows),
                mean_scene_bce=statistics.mean(r['activity_bce'] for r in rows))


def condition_key(row):
    c = row['condition']
    return (c['users'], c['frames'], c['activity_probability'], row['snr'])


def layer_records(rows):
    result = []
    for i in range(len(rows[0]['layer_metrics'])):
        ds = [r['diagnostics'][i] for r in rows]
        result.append(dict(layer=i + 1,
            **summary([r['layer_metrics'][i] for r in rows]),
            median_query_variance_over_actual_mse=statistics.median(
                d['query_variance'] / d['query_mse'] for d in ds),
            median_active_over_inactive_query_mse=statistics.median(
                d['query_active_mse'] / d['query_inactive_mse'] for d in ds),
            median_feedback_ratio=statistics.median(d['feedback_ratio'] for d in ds),
            maximum_feedback_ratio=max(d['feedback_ratio'] for d in ds),
            median_damping=statistics.median(d['damping'] for d in ds),
            scenes_damped=sum(d['damping'] < 1 for d in ds),
            negative_residual_variance_scenes=sum(d['raw_residual_variance'] < 0 for d in ds),
            out_of_pretraining_support_scenes=sum(d['out_of_pretraining_support'] for d in ds)))
    return result


def same_inputs(left, right):
    return len(left) == len(right) and all(
        a['seed'] == b['seed'] and a['source_pool_index'] == b['source_pool_index']
        and condition_key(a) == condition_key(b)
        and a['frontend']['observation_sha256'] == b['frontend']['observation_sha256']
        and a['frontend']['operator_sha256'] == b['frontend']['operator_sha256']
        and a['truth_energy'] == b['truth_energy']
        for a, b in zip(left, right))


def main():
    five = read(FIVE / 'checkpoints/depth_5/best_validation.json')
    history = read(FIVE / 'checkpoints/depth_5/history.json')
    config = read(FIVE / 'MANIFEST.json')['configuration']
    complete = read(FIVE / 'checkpoints/depth_5/COMPLETE.json')
    six0 = read(SIX / 'checkpoints/depth_6/validation_epoch_0.json')
    six1 = read(SIX / 'checkpoints/depth_6/validation_epoch_1.json')
    paired = read(ROOT / 'results/lstmp_epoch6_vs_legacy20_20261020/POSTCOMPARISON_REVIEW.json')
    assert len(five['rows']) == 1200
    assert same_inputs(five['rows'], six0['rows'])
    assert same_inputs(five['rows'], six1['rows'])
    totals = summary(five['rows'])
    for key in ['pooled_nmse_db', 'aer', 'misses', 'false_alarms']:
        assert abs(totals[key] - five['summary'][key]) < 1e-10
    layers = layer_records(five['rows'])
    groups = {}
    for row in five['rows']:
        groups.setdefault(condition_key(row), []).append(row)
    by_condition = [dict(condition=dict(zip(['users', 'frames', 'activity_probability', 'snr_db'], key)),
                         **summary(rows), layers=layer_records(rows)) for key, rows in groups.items()]
    six = {}
    for name, saved in [('copied_layer_no_updates', six0), ('one_adaptation_epoch', six1)]:
        sg = {}
        for row in saved['rows']:
            sg.setdefault(condition_key(row), []).append(row)
        six[name] = dict(summary=summary(saved['rows']),
            preceding_five_layer_output=summary([r['layer_metrics'][4] for r in saved['rows']]),
            by_condition=[dict(condition=dict(zip(['users', 'frames', 'activity_probability', 'snr_db'], k)),
                               **summary(rs)) for k, rs in sg.items()])
    prefix_change = max(abs(a['layer_metrics'][i]['nmse'] - b['layer_metrics'][i]['nmse'])
                       for a, b in zip(six0['rows'], six1['rows']) for i in range(5))
    assert prefix_change == 0
    weighted_nmse = sum((.2 if i < 4 else 1) * r['mean_scene_nmse'] for i, r in enumerate(layers)) / 1.8
    weighted_bce = sum((.2 if i < 4 else 1) * .1 * r['mean_scene_bce'] for i, r in enumerate(layers)) / 1.8
    assert abs(weighted_nmse + weighted_bce - five['summary']['loss']) < 1e-6
    settings = config['receiver']
    result = dict(
        scope='Existing-record analysis only; no training, inference, threshold changes or checkpoint selection.',
        five_layer_selected_epoch=complete['selected_epoch'], summary=totals, layers=layers,
        by_condition=by_condition, stage5_history=history,
        six_layer_interim=six,
        checks=dict(all_1200_scenes_retained=True, saved_summary_reproduced=True,
                    paired_observation_and_operator_hashes_match=True,
                    six_epoch0_to_epoch1_prefix_nmse_max_change=prefix_change,
                    weighted_nmse_contribution=weighted_nmse, weighted_bce_contribution=weighted_bce),
        training_settings={k: settings[k] for k in ['train_scenes', 'validation_scenes',
            'epoch_schedule', 'activity_loss_weight', 'earlier_layer_loss_weight', 'selection',
            'phase_mode', 'noise_mode', 'conditions']},
        standard_paired_comparison=paired,
        interpretation_limits=[
            'Layers inside one final model are not independently trained depth-only comparisons.',
            'Depth-six epoch one is a completed interim validation, not the completed depth-seven result.',
            'The adaptation epoch changes the new layer and preceding feedback calibration; it is not depth alone.',
            'Validation is reused for selection, so these are descriptive diagnostics, not new held-out confirmation.',
            'The old-algorithm paired comparison covers K40/Q16/rho0.1/SNR5, not the difficult groups.',
            'Known phase and known noise exclude estimated-front-end errors as a cause of these current results.',
            'Query variance is trainably calibrated; disagreement with realized error is not by itself an algebra bug.',
            'Final-layer feedback does not affect that layer output; its statistics cannot explain current-layer error.',
            'Loss value contributions are not gradient contributions; they do not prescribe an optimal BCE weight.',
            'AER weights misses and false alarms by actual active/inactive counts; always retain both rates.',
        ],
        sources=SOURCES,
        literature=[
            dict(url='https://arxiv.org/html/2610.17785v1', locations='III-B equations 8-10; III-C equation 12; III-D; V-A',
                 scope='Single-user recovery; five independent NCSN++; progressive joint training. No AFDM AER guarantee.'),
            dict(url='https://arxiv.org/html/2506.00581v2', locations='III-B3 equations 35-38; V-B1 equations 57-58',
                 scope='Activity mixture moments and damping; not proof of calibrated learned AFDM messages.'),
        ])
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'ANALYSIS.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    fields = ['users', 'frames', 'activity_probability', 'snr_db', 'layer', 'pooled_nmse_db',
              'aer', 'misses', 'false_alarms', 'active', 'inactive', 'missed_detection_rate',
              'false_alarm_rate', 'median_query_variance_over_actual_mse',
              'median_active_over_inactive_query_mse', 'median_damping', 'scenes_damped',
              'negative_residual_variance_scenes']
    with (OUT / 'CONDITION_LAYERS.csv').open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        for group in by_condition:
            for layer in group['layers']:
                writer.writerow(dict(group['condition'], **layer))
    print(json.dumps(dict(output=str(OUT), scenes=len(five['rows']), conditions=len(groups),
                          checks=result['checks']), indent=2))


if __name__ == '__main__':
    main()
