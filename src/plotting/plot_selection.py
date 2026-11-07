"""Saved-data adapters and paired scene selection. No receiver imports."""
import csv
import json
import math
from pathlib import Path

from plotting.data import PlotData
from plotting.data import digest
from plotting.data import load
from plotting.data import read

COORDINATES = dict(snr_comparison='snr_db', pilot_frames='frames', user_count='users',
                   activity_probability='activity_probability', cross_channel='snr_db',
                   channel_denoising='variance', runtime_comparison='mean_end_to_end_seconds',
                   density_ratio_ablation='snr_db')


def verify_file(path, expected):
    if digest(path) != expected:
        raise ValueError(f'Saved file hash changed: {path}')


def sealed_file(path, metadata):
    """Validate an individual member of a frozen completion manifest."""
    seal = Path(metadata['source_summary']).parent / 'COMPLETE.json'
    document = read(seal)
    if document.get('status') != 'COMPLETE':
        raise ValueError('Snapshot completion manifest is not complete')
    matches = [v for k, v in document['files'].items()
               if (Path(k) if Path(k).is_absolute() else seal.parent/Path(k)).resolve() == path.resolve()]
    if len(matches) != 1:
        raise ValueError(f'No completion-manifest hash for {path}')
    verify_file(path, matches[0])
    metadata.setdefault('selection_sources', {})[str(path)] = matches[0]
    metadata['selection_sources'][str(seal)] = digest(seal)


def validate_rows(data):
    keys, counts = set(), set()
    conditions = {json.dumps(r['parameters'], sort_keys=True) for r in data.rows}
    for r in data.rows:
        k = (r['method'], json.dumps(r['parameters'], sort_keys=True))
        if k in keys:
            raise ValueError('Duplicate method/condition row')
        keys.add(k)
        counts.add(r.get('scenes', r.get('completed')))
        error, energy = (r['error'], r['energy']) if 'error' in r else (r['full_error'], r['signal_energy'])
        if not (math.isfinite(error) and math.isfinite(energy) and error > 0 and energy > 0):
            raise ValueError('Invalid pooled error or signal energy')
        if not math.isclose(r['nmse_db'], 10 * math.log10(error / energy), abs_tol=1e-9):
            raise ValueError('NMSE disagrees with pooled energy sums')
        if 'aer' in r:
            a, b, m, f = (r[k] for k in ('active', 'inactive', 'misses', 'false_alarms'))
            if any(v < 0 or int(v) != v for v in (a,b,m,f)) or m > a or f > b or a+b <= 0:
                raise ValueError('Invalid activity counts')
            if not math.isclose(r['aer'], (m+f)/(a+b), abs_tol=1e-12):
                raise ValueError('AER disagrees with pooled counts')
    if keys != {(m,c) for m in data.methods for c in conditions} or counts != {data.scenes} or data.scenes <= 0:
        raise ValueError('All methods/conditions need the same complete paired scene set')


def load_saved(source, experiment):
    source = Path(source).resolve()
    if source.is_dir():
        source /= 'SUMMARY.json'
    summary = read(source)
    if 'raw_plan' in summary:
        return load_readout_snapshot(source, summary, experiment)
    plan_path = Path(summary.get('source_plan', source.parent / 'PLAN.json'))
    if not plan_path.is_absolute():
        plan_path = source.parent / plan_path
    plan = read(plan_path)
    if plan.get('experiment_kind'):
        data = load(source, experiment)
    elif experiment == 'channel_denoising':
        if plan.get('schema') == 'direct-awgn-colored-append-v1':
            from plotting.historical_data import load_append
            data = load_append(source, experiment)
        else:
            from plotting.historical_data import load_denoising
            data = load_denoising(source, experiment)
    else:
        # Frozen C-STMP snapshots have a completion seal and a different plan schema.
        coordinate = COORDINATES[experiment]
        if experiment not in ('snr_comparison', 'pilot_frames', 'user_count') or coordinate not in summary['rows'][0]:
            raise ValueError('Unsupported saved schema; use a standard SUMMARY/PLAN pair')
        if summary.get('experiment', experiment) != experiment or summary['status'] not in ('COMPLETE','INTERIM'):
            raise ValueError('Wrong experiment or unfinished snapshot')
        ids = summary['scene_ids']
        if len(ids) != summary['scene_count'] or len(set(ids)) != len(ids):
            raise ValueError('Snapshot scene IDs are missing or duplicated')
        metadata = dict(source_summary=str(source), source_sha256=digest(source),
                        source_plan=str(plan_path), source_plan_sha256=digest(plan_path),
                        status='INTERIM' if summary.get('interim') else summary['status'],
                        planned_scenes=plan.get('main_continues_to_scenes', len(plan.get('scenes', ids))),
                        scene_ids=ids, labels={}, phase_mode=summary.get('phase_mode'),
                        noise_mode=summary.get('noise_mode'), limitations=summary.get('limitations'),
                        sealed_snapshot=True)
        sealed_file(source, metadata)
        sealed_file(source.parent/'PLAN.json', metadata)
        if summary.get('source_plan_sha256'):
            verify_file(plan_path, summary['source_plan_sha256'])
        rows = [dict(r, parameters={coordinate:r[coordinate]}) for r in summary['rows']]
        data = PlotData(experiment, rows, summary['methods'], len(ids), metadata)
    data.metadata['limitations'] = summary.get('limitations', plan.get('limitations', data.metadata.get('limitations')))
    if data.metadata.get('scene_ids') is None:
        data.metadata['scene_ids'] = summary.get('scene_ids')
    validate_rows(data)
    return data


def load_readout_snapshot(source, summary, experiment):
    """Completed baseline readout applications retain a raw-plan link, not a sibling plan."""
    plan_path = Path(summary['raw_plan'])
    verify_file(plan_path, summary['raw_plan_sha256'])
    plan = read(plan_path)
    if summary['status']!='COMPLETE' or summary['experiment']!=experiment or plan['experiment']!=experiment:
        raise ValueError('Readout snapshot has wrong experiment/status')
    ids=summary['full_scene_ids']
    if len(ids)!=summary['scene_count'] or len(set(ids))!=len(ids):
        raise ValueError('Readout snapshot has invalid paired scene IDs')
    metadata=dict(source_summary=str(source),source_sha256=digest(source),source_plan=str(plan_path),
                  source_plan_sha256=digest(plan_path),status='COMPLETE',planned_scenes=plan['scene_count'],
                  phase_mode=summary['phase_mode'],noise_mode=summary['noise_mode'],mode=summary['mode'],
                  timing=summary.get('timing'),parallel_execution=plan.get('parallel_execution'),
                  labels={m:plan['algorithm_specs'][m]['label'] for m in summary['methods']},
                  scene_ids=ids,sealed_snapshot=True,
                  limitations={'independent_test':summary.get('independent_test'),'statistics':summary.get('statistics')})
    sealed_file(source,metadata)
    audit=source.parent/'RESULT_AUDIT.json';sealed_file(audit,metadata)
    if read(audit)['status']!='PASS':raise ValueError('Readout snapshot audit did not pass')
    data=PlotData(experiment,summary['rows'],summary['methods'],len(ids),metadata)
    validate_rows(data)
    return data


def parse_cell(value):
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return value


def scene_records(data, requested, per_scene=None):
    source = Path(data.metadata['source_summary']).parent
    path = Path(per_scene) if per_scene else source / 'per_scene.csv'
    if not path.exists():
        raise ValueError('Scene selection needs per_scene.csv (or selection.per_scene); aggregate summaries cannot be split')
    if data.metadata.get('sealed_snapshot') and path.resolve() == (source/'per_scene.csv').resolve():
        sealed_file(path, data.metadata)
    else:
        data.metadata.setdefault('selection_sources', {})[str(path.resolve())] = digest(path)
    with path.open(encoding='utf-8-sig', newline='') as stream:
        records = [{k:parse_cell(v) for k,v in r.items()} for r in csv.DictReader(stream)]
    records = [r for r in records if r['scene'] in requested and r['method'] in data.methods]
    # The original SNR CSV contains only C-STMP/STMP. Its frozen baseline audit
    # supplies the exact adopted thresholds; never reuse native activity counts.
    missing = set(data.methods) - {r['method'] for r in records}
    if missing and data.experiment == 'snr_comparison' and data.metadata.get('sealed_snapshot') and not per_scene:
        import numpy as np
        audit_path = source / 'BASELINE_AUDIT.json'
        sealed_file(audit_path, data.metadata)
        plan = read(data.metadata['source_plan'])
        snrs = plan['snrs']
        for ref in read(audit_path)['references']:
            if ref['method'] not in missing or ref['scene'] not in requested:
                continue
            p = Path(ref['result'])
            verify_file(p, ref['sha256'])
            native = read(p)
            compact = p.with_suffix('.npz')
            verify_file(compact, native['compact_sha256'])
            with np.load(compact, allow_pickle=False) as z:
                truth = z['truth_activity'].astype(bool)
                # Match the frozen readout's float64 conversion before comparison.
                # Comparing float32 arrays to a Python float can round a threshold
                # onto a score and change one decision at the boundary.
                score = np.asarray(z['activity_score'], dtype=np.float64)
                energy = np.asarray(z['channel_energy' if ref['method']=='offgrid_sbl' else 'coefficient_energy'], dtype=np.float64)
                decision = (score >= ref['threshold']) & (energy.max() > 0)
                metrics = dict(native['metrics'], misses=int((truth & ~decision).sum()),
                               false_alarms=int((~truth & decision).sum()))
            records.append(dict(metrics, scene=ref['scene'], method=ref['method'], snr_db=snrs[ref['index']]))
        data.metadata['baseline_readout'] = 'Frozen BASELINE_AUDIT thresholds applied to verified saved predictions; no fitting'
    return records


def select(data, selection):
    methods = selection.get('methods') or data.methods
    if len(set(methods)) != len(methods) or not set(methods) <= set(data.methods):
        raise ValueError(f'Select distinct saved method IDs from {data.methods}; labels do not change identities')
    filters = selection.get('conditions', {})
    available = {k for r in data.rows for k in r['parameters']}
    if set(filters) - available:
        raise ValueError(f'Unknown condition filters: {set(filters)-available}')
    for key, wanted in filters.items():
        present = {r['parameters'].get(key) for r in data.rows}
        if not set(wanted if isinstance(wanted,list) else [wanted]) <= present:
            raise ValueError(f'Requested {key} values are not all present in saved conditions')
    rows = [r for r in data.rows if r['method'] in methods and all(
        r['parameters'].get(k) in (v if isinstance(v,list) else [v]) for k,v in filters.items())]
    if not rows:
        raise ValueError('Selection contains no saved data')
    data = PlotData(data.experiment, rows, list(methods), data.scenes, dict(data.metadata))
    scenes = selection.get('scenes', {})
    if scenes:
        if len(scenes) != 1 or not set(scenes) <= {'ids','first','range'}:
            raise ValueError('scenes accepts exactly one of ids, first, range (end exclusive)')
        available_ids = data.metadata.get('scene_ids')
        if 'first' in scenes:
            if not available_ids:
                raise ValueError('First N requires saved scene_ids; use explicit ids with per-scene records')
            n = scenes['first']
            if type(n) is not int or not 0 < n <= len(available_ids):
                raise ValueError('first must be within the available scene count')
            ids = sorted(available_ids)[:n]
        elif 'range' in scenes:
            ids = list(range(*scenes['range']))
        else:
            ids = scenes['ids']
        if not ids or any(type(i) is not int for i in ids) or len(set(ids)) != len(ids):
            raise ValueError('Scene IDs must be nonempty, distinct integers')
        if available_ids is not None and not set(ids) <= set(available_ids):
            raise ValueError('Requested scene IDs are not in the saved snapshot')
        records = scene_records(data, set(ids), selection.get('per_scene'))
        pooled = []
        for row in data.rows:
            group = [r for r in records if r['method'] == row['method'] and all(
                (r.get(k) == v) for k,v in row['parameters'].items())]
            # For a CSV with condition indices, the full physical parameters need not be duplicated.
            if not group and 'condition' in row:
                group = [r for r in records if r['method']==row['method'] and r.get('condition')==row['condition']]
            if len(group) != len(ids) or {r['scene'] for r in group} != set(ids):
                raise ValueError(f'Missing/duplicate paired scene records for {row["method"]}, {row["parameters"]}')
            denoising = 'error' in row
            fields = ('error','energy') if denoising else ('full_error','signal_energy','active','inactive','misses','false_alarms')
            sums = {k:math.fsum(r[k] for r in group) for k in fields}
            error, energy = (sums['error'],sums['energy']) if denoising else (sums['full_error'],sums['signal_energy'])
            result = dict(method=row['method'], parameters=row['parameters'], scenes=len(ids),
                          **sums, nmse_db=10*math.log10(error/energy))
            if not denoising:
                result['aer'] = (sums['misses']+sums['false_alarms'])/(sums['active']+sums['inactive'])
                if sums['active']>0: result['miss_rate']=sums['misses']/sums['active']
                if sums['inactive']>0: result['false_alarm_rate']=sums['false_alarms']/sums['inactive']
            for saved,raw in [('mean_iterations','iterations'),('mean_receiver_seconds','receiver_seconds'),
                              ('mean_end_to_end_seconds','end_to_end_seconds')]:
                if all(raw in r for r in group):
                    result[saved]=math.fsum(r[raw] for r in group)/len(group)
            if data.experiment == 'runtime_comparison':
                result['mean_end_to_end_seconds'] = math.fsum(r['end_to_end_seconds'] for r in group)/len(group)
                backends = {r['backend'] for r in group}
                if len(backends)!=1:
                    raise ValueError('Runtime CSV mixes backends within a curve')
                result['backend'] = backends.pop()
            pooled.append(result)
        data.rows, data.scenes = pooled, len(ids)
        data.metadata.update(scene_ids=ids, scene_selection='Recomputed pooled metrics from paired saved scene records')
    data.metadata['selection'] = selection
    validate_rows(data)
    return data
