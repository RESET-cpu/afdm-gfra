"""Read saved v2 validation only; never touch training state or run inference."""
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RUN = Path('D:/afdm-gfra-cpu/runs/lstmp_conditional_bce_v2_20261020')
KEYS = ('selection_loss', 'channel_loss', 'activity_loss', 'pooled_nmse_db',
        'mean_scene_nmse_db', 'conditional_nmse_db', 'active_nmse_db', 'aer',
        'missed_detection_rate', 'false_alarm_rate', 'misses', 'false_alarms')


def read_bound(path, provenance):
    raw = path.read_bytes()
    provenance[str(path)] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw.decode('utf-8-sig'))


def aggregate(rows):
    total = lambda key: sum(r[key] for r in rows)
    active, inactive = total('active'), total('inactive')
    error, truth = total('error_energy'), total('truth_energy')
    return dict(scenes=len(rows), active=active, inactive=inactive,
        misses=total('misses'), false_alarms=total('false_alarms'),
        aer=(total('misses') + total('false_alarms')) / (active + inactive),
        missed_detection_rate=total('misses') / active,
        false_alarm_rate=total('false_alarms') / inactive,
        pooled_nmse_db=10 * np.log10(error / truth),
        conditional_nmse_db=10 * np.log10(total('conditional_error_energy') / truth),
        active_nmse_db=10 * np.log10(total('active_error_energy') / truth),
        active_error_energy=total('active_error_energy'),
        inactive_error_energy=total('inactive_error_energy'),
        conditional_error_energy=total('conditional_error_energy'),
        selection_loss=sum(r['selection_loss'] for r in rows) / len(rows))


def condition_key(row, with_snr=True):
    condition = dict(row['condition'])
    if with_snr:
        condition['snr_db'] = row['snr']
    else:
        condition.pop('snr_db', None)
    return tuple(sorted(condition.items()))


def probability_statistics(rows):
    p = np.concatenate([r['user_probabilities'] for r in rows])
    active = np.concatenate([r['user_activity'] for r in rows]).astype(bool)
    energy = np.concatenate([r['user_truth_energy'] for r in rows])[active]
    cuts = np.quantile(energy, [.25, .5, .75])
    groups = np.digitize(energy, cuts, right=True)
    return dict(active_probability_mean=float(p[active].mean()),
        active_probability_median=float(np.median(p[active])),
        inactive_probability_mean=float(p[~active].mean()),
        active_energy_quartiles=[dict(quartile=i+1, users=int((groups == i).sum()),
            missed_detection_rate=float((p[active][groups == i] < .5).mean()))
            for i in range(4)],
        quartiles_for_description_only=True)


def bootstrap_delta(a, b):
    groups = defaultdict(list)
    for i, row in enumerate(a):
        groups[condition_key(row)].append(i)
    rng = np.random.default_rng(202610200127)
    indices = np.concatenate([rng.choice(group, size=(2000, len(group)), replace=True)
                              for group in groups.values()], axis=1)
    summed = lambda rows, key: np.array([r[key] for r in rows])[indices].sum(axis=1)
    active, inactive = summed(a, 'active'), summed(a, 'inactive')
    md = summed(b, 'misses') - summed(a, 'misses')
    fa = summed(b, 'false_alarms') - summed(a, 'false_alarms')
    values = dict(aer_percentage_points=100*(md+fa)/(active+inactive),
                  md_percentage_points=100*md/active,
                  fa_percentage_points=100*fa/inactive,
                  nmse_db=10*np.log10(summed(b, 'error_energy') / summed(a, 'error_energy')))
    return {key: np.quantile(value, [.025, .975]).tolist() for key, value in values.items()}


def compare(a, b):
    for x, y in zip(a['rows'], b['rows']):
        for key in ('seed', 'source_pool_index', 'condition', 'active', 'inactive',
                    'truth_energy', 'user_activity', 'user_truth_energy'):
            assert x[key] == y[key], (key, x['seed'])
        for key in ('observation_sha256', 'operator_sha256'):
            assert x['frontend'][key] == y['frontend'][key]
    sa, sb = aggregate(a['rows']), aggregate(b['rows'])
    delta = {key + '_percentage_points': 100 * (sb[key] - sa[key])
             for key in ('aer', 'missed_detection_rate', 'false_alarm_rate')}
    delta.update({key + '_change': sb[key] - sa[key]
                  for key in ('pooled_nmse_db', 'conditional_nmse_db', 'active_nmse_db',
                              'misses', 'false_alarms', 'selection_loss')})
    delta.update({key + '_relative_percent': 100 * (sb[key] / sa[key] - 1)
                  for key in ('active_error_energy', 'inactive_error_energy', 'conditional_error_energy')})
    conditions = []
    profiles = []
    for with_snr, destination in ((True, conditions), (False, profiles)):
        groups = defaultdict(lambda: [[], []])
        for old, new in zip(a['rows'], b['rows']):
            pair = groups[condition_key(old, with_snr)]
            pair[0].append(old)
            pair[1].append(new)
        for key, (old, new) in groups.items():
            before, after = aggregate(old), aggregate(new)
            destination.append(dict(condition=dict(key), before=before, after=after,
                nmse_db_change=after['pooled_nmse_db'] - before['pooled_nmse_db'],
                md_percentage_point_change=100*(after['missed_detection_rate'] - before['missed_detection_rate'])))
    return dict(before=a['name'], after=b['name'], delta=delta,
                conditions_with_worse_nmse=int(sum(r['nmse_db_change'] > 0 for r in conditions)),
                conditions_with_higher_md=int(sum(r['md_percentage_point_change'] > 0 for r in conditions)),
                profiles=profiles, conditions=conditions,
                descriptive_stratified_paired_scene_bootstrap_95_percent=bootstrap_delta(a['rows'], b['rows']))


def main():
    now = datetime.now(timezone(timedelta(hours=8)))
    output = ROOT / 'results/lstmp_training_v2_progress_20261020' / now.strftime('%H%M%S')
    output.mkdir(parents=True, exist_ok=False)
    provenance = {}
    progress = read_bound(RUN / 'STATUS.json', provenance)
    snapshots = {}
    selected = {}
    for folder in sorted((RUN / 'checkpoints').glob('depth_*')):
        depth = int(folder.name.split('_')[-1])
        if (folder / 'BEST.json').exists():
            selected[str(depth)] = read_bound(folder / 'BEST.json', provenance)
        for path in sorted(folder.glob('validation_epoch_*.json')):
            epoch = int(path.stem.split('_')[-1])
            if epoch == 0:
                continue
            value = read_bound(path, provenance)
            rows = value['rows']
            assert len(rows) == 1200
            check = aggregate(rows)
            for key in ('aer', 'missed_detection_rate', 'false_alarm_rate', 'pooled_nmse_db',
                        'active_nmse_db', 'conditional_nmse_db', 'selection_loss'):
                assert np.isclose(check[key], value['summary'][key], rtol=1e-10, atol=1e-10), (path, key)
            snapshots[depth, epoch] = dict(name=f'depth_{depth}_epoch_{epoch}', depth=depth, epoch=epoch,
                phase='ADAPTATION' if epoch == 1 else 'JOINT', rows=rows,
                summary={key: value['summary'][key] for key in KEYS},
                probability_statistics=probability_statistics(rows))
    comparisons = []
    for depth in sorted({d for d, _ in snapshots}):
        for before, after in ((1, 2), (1, 3), (2, 3)):
            if (depth, before) in snapshots and (depth, after) in snapshots:
                comparisons.append(compare(snapshots[depth, before], snapshots[depth, after]))
        if depth > 1 and (depth, 1) in snapshots and str(depth-1) in selected:
            before = selected[str(depth-1)]['epoch']
            if (depth-1, before) in snapshots:
                comparisons.append(compare(snapshots[depth-1, before], snapshots[depth, 1]))
    compact = [{key: value for key, value in row.items() if key != 'rows'} for row in snapshots.values()]
    report = dict(as_of_shanghai=now.isoformat(), training_progress_snapshot=progress,
                  selection=selected, checkpoints=compact, comparisons=comparisons,
                  source_sha256=provenance, training_modified=False, inference_performed=False,
                  uncertainty='Descriptive validation-set pairing only; no independent test or training-seed uncertainty.')
    path = output / 'ANALYSIS.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    print(json.dumps(dict(report=str(path), as_of=now.isoformat(),
                         progress={k: progress[k] for k in ('stage', 'depth', 'epoch', 'cursor', 'completed_updates',
                                                          'elapsed_seconds')},
                         checkpoints=compact,
                         comparisons=[{k: c[k] for k in ('before', 'after', 'delta', 'conditions_with_worse_nmse',
                                                         'conditions_with_higher_md',
                                                         'descriptive_stratified_paired_scene_bootstrap_95_percent')}
                                      for c in comparisons]), ensure_ascii=False))


if __name__ == '__main__':
    main()
