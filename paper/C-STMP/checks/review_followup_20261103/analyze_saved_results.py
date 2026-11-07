"""Read saved metrics only; never run a receiver or alter experimental assets."""
from pathlib import Path
import csv
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SNR = [-4, -2, 0, 2, 4, 6]
manifest = {}


def read_json(path, expected=None):
    path = Path(path)
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if expected is not None:
        assert digest == expected, str(path)
    manifest[str(path)] = digest
    return json.loads(raw)


def read_csv(path):
    path = Path(path)
    manifest[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def write_json(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def write_csv(name, rows):
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def aggregate_scenes(rows):
    error = math.fsum(float(r['full_error']) for r in rows)
    signal = math.fsum(float(r['signal_energy']) for r in rows)
    misses = sum(int(r['misses']) for r in rows)
    false_alarms = sum(int(r['false_alarms']) for r in rows)
    decisions = sum(int(r['active']) + int(r['inactive']) for r in rows)
    caps = sum(r['stopping_reason'] == 'MAX_ITERATIONS' for r in rows)
    return dict(scenes=len(rows), full_error=error, signal_energy=signal,
                nmse_db=10 * math.log10(error / signal), misses=misses,
                false_alarms=false_alarms, decisions=decisions,
                aer_percent=100 * (misses + false_alarms) / decisions,
                iteration_limit_count=caps, iteration_limit_percent=100 * caps / len(rows))


def user_count_sensitivity():
    base = ROOT / 'result/user_count/data'
    original = read_csv(base / 'c_stmp_variance_em_500_k100beta02_20261026/per_scene.csv')
    current = read_csv(base / 'stmp_500_k60_k80_k100_beta01_20261027/per_scene.csv')
    before = {int(r['scene']): r for r in original if r['method'] == 'C_STMP' and int(r['users']) == 80}
    after = {int(r['scene']): r for r in current if r['method'] == 'C_STMP' and int(r['users']) == 80}
    assert set(before) == set(after) == set(range(500))
    changed = []
    for scene in before:
        assert float(before[scene]['signal_energy']) == float(after[scene]['signal_energy'])
        if any(float(before[scene][k]) != float(after[scene][k]) for k in
               ['full_error', 'active_error', 'misses', 'false_alarms', 'iterations']):
            changed.append(scene)
    assert changed == [372], changed
    baseline = [r for r in current if r['method'] == 'STMP' and int(r['users']) == 80]
    result = {
        'condition': {'users': 80, 'snr_db': 0, 'frames': 16},
        'changed_scenes': changed,
        'original_fixed_damping': aggregate_scenes(list(before.values())),
        'displayed_replacement': aggregate_scenes(list(after.values())),
        'gp_mp_reference': aggregate_scenes(baseline),
        'difference_db': aggregate_scenes(list(before.values()))['nmse_db'] - aggregate_scenes(list(after.values()))['nmse_db'],
        'scene372_original': before[372], 'scene372_replacement': after[372],
        'original_error_fraction_scene372': float(before[372]['full_error']) / math.fsum(float(r['full_error']) for r in before.values()),
        'scope': 'Read-only reaggregation of existing per-scene energies. No scenes removed and no figure altered.'
    }
    write_json('scene372_sensitivity.json', result)
    print('SCENE372', json.dumps({k:v for k,v in result.items() if k not in ['scene372_original','scene372_replacement']}))


def activity_ablation():
    folder = ROOT / 'result/snr_comparison/data/c_stmp_ablation_1000_20261028'
    refs = read_json(folder / 'REFERENCES.json')
    known_refs = {(r['scene'], r['index']): r for r in refs}
    candidates = {}
    for path in sorted((folder / 'results/gaussian_evidence').glob('*.json')):
        ref = read_json(path)
        row_path = Path(ref['stem']).with_suffix('.json')
        row = read_json(row_path, ref['files'][str(row_path)])
        key = (row['scene'], row['index'])
        assert key == (ref['scene'], ref['index']) and key not in candidates
        assert row['snr_db'] == SNR[row['index']]
        candidates[key] = row
    complete = sorted(s for s in {key[0] for key in candidates} if all((s, i) in candidates for i in range(6)))
    assert complete == list(range(354)), complete
    rows = []
    truth_checks = 0
    for scene in complete:
        for index, snr in enumerate(SNR):
            g = candidates[(scene, index)]
            ref = known_refs[(scene, index)]
            ptr = read_json(ref['pointer'], ref['pointer_sha256'])
            assert Path(ptr['stem']) == Path(ref['stem'])
            path = Path(ref['stem']).with_suffix('.json')
            k = read_json(path, ref['files'][str(path)])
            assert k['scene'] == scene and k['index'] == index and k['snr_db'] == snr
            assert g['reference_pointer'] == ref['pointer']
            assert g['reference_pointer_sha256'] == ref['pointer_sha256']
            for field in ['active', 'inactive', 'misses', 'false_alarms']:
                assert k['metrics'][field] == g['reference_metrics'][field]
            assert math.isclose(k['metrics']['signal_energy'], g['metrics']['signal_energy'], rel_tol=1e-12)
            truth = k.get('truth_activity')
            for method, row in [('learned_density_ratio', k), ('gaussian_approximation', g)]:
                m = row['metrics']
                assert m['active'] + m['inactive'] == 40
                if truth is not None:
                    dec = m['decisions']
                    assert len(truth) == len(dec) == 40
                    assert sum(bool(t) and not bool(d) for t,d in zip(truth,dec)) == m['misses']
                    assert sum(not bool(t) and bool(d) for t,d in zip(truth,dec)) == m['false_alarms']
                    truth_checks += 1
                cap = row['stopping_reason'] == 'MAX_ITERATIONS'
                assert cap == (int(row['iterations']) == 600 and not row['converged'])
                assert row['stopping_reason'] in ['MAX_ITERATIONS', 'CONVERGED']
                rows.append(dict(method=method, scene=scene, snr_db=snr, active=m['active'],
                                 inactive=m['inactive'], misses=m['misses'], false_alarms=m['false_alarms'],
                                 iterations=row['iterations'], iteration_limit=int(cap)))
    grouped = []
    for snr in SNR + ['pooled']:
        for method in ['learned_density_ratio', 'gaussian_approximation']:
            selected = [r for r in rows if r['method'] == method and (snr == 'pooled' or r['snr_db'] == snr)]
            misses = sum(r['misses'] for r in selected)
            false_alarms = sum(r['false_alarms'] for r in selected)
            decisions = sum(r['active']+r['inactive'] for r in selected)
            caps = sum(r['iteration_limit'] for r in selected)
            grouped.append(dict(snr_db=snr, method=method, runs=len(selected), physical_scenes=354,
                                decisions=decisions, misses=misses, false_alarms=false_alarms,
                                aer_percent=100*(misses+false_alarms)/decisions,
                                iteration_limit_count=caps, iteration_limit_percent=100*caps/len(selected)))
    pooled = {r['method']:r for r in grouped if r['snr_db']=='pooled'}
    assert (pooled['learned_density_ratio']['misses'], pooled['learned_density_ratio']['false_alarms']) == (111,3)
    assert (pooled['gaussian_approximation']['misses'], pooled['gaussian_approximation']['false_alarms'], pooled['gaussian_approximation']['iteration_limit_count']) == (187,31207,724)
    write_csv('activity_by_snr.csv', grouped)
    write_csv('activity_per_scene.csv', rows)
    write_json('activity_summary.json', dict(physical_scenes=354, scene_ids=complete,
        saved_gaussian_outputs=len(candidates), complete_paired_runs=2124,
        incomplete_scene_outputs=[{'scene':s,'index':i} for s,i in candidates if s not in complete],
        verification='Saved JSON hashes and pair identities checked; AER recounted from saved decisions where truth labels are present. No new inference or training.',
        saved_decision_truth_checks=truth_checks, rows=grouped))
    print('ACTIVITY', json.dumps(grouped))


if __name__ == '__main__':
    user_count_sensitivity()
    activity_ablation()
    write_json('source_hashes.json', manifest)
