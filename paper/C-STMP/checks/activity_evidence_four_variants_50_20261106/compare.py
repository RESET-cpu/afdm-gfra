"""Read-only, paired first-50-scene interim analysis; no inference or manuscript changes."""
import json
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta

import psutil
from evaluation.activity_evidence_500_20261105.common import (
    OUT, SNRS, METHODS, read_json, write_json, sha256, checked, tag,
    check_new, reuse_metrics, arrays, aggregate,
)

HERE = Path(__file__).resolve().parent
psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
plan = read_json(OUT / 'PLAN.json')
checked(OUT / 'PLAN.json', read_json(OUT / 'PLAN_HASH.json')['sha256'])
cases = read_json(OUT / 'INPUTS.json')
reuse = read_json(OUT / 'REUSE.json')
names = ('STMP-Gaussian', 'STMP-LR', 'GP-MP-Gaussian', 'GP-MP-LR')
rows = {m: [] for m in names}
sources = {}

def audit(path, digest):
    checked(path, digest)
    sources[str(path)] = digest

for i in range(300):
    case = cases[i]
    assert (case['scene'], case['index'], case['snr_db']) == (i//6, i%6, SNRS[i%6])
    folder = Path(case['ready']).parent
    audit(case['ready'], case['ready_sha256'])
    for name, digest in case['files'].items():
        audit(folder/name, digest)
    truth = arrays(folder/'truth.npz')
    for method in names:
        if method in METHODS:
            pointer_path = OUT/'results'/(method+'_'+tag(i)+'.json')
            pointer = read_json(pointer_path)
            audit(pointer_path, sha256(pointer_path))
            audit(pointer['result'], pointer['sha256'])
            assert Path(pointer['result']) == Path(plan['native_directory'])/method/tag(i)/'RESULT.json'
            row = check_new(method, i, plan)
            sources.update(row['files'])
        else:
            ref = reuse[i][method]
            for path, digest in ref['files'].items():
                audit(path, digest)
            row, record = read_json(ref['result']), read_json(ref['record'])
            if method == 'STMP-LR':
                assert row['identity']['input'] == case['files']
                assert row['identity']['runtime'] == ref['runtime_identity']
                assert row['identity']['method'] == 'STMP'
                assert row['identity']['phase_mode'] == 'known'
            else:
                assert row['input_files'] == case['files']
                assert (row['scene'], row['index'], row['snr_db']) == (case['scene'],case['index'],case['snr_db'])
            row['metrics'] = reuse_metrics(ref, truth, row['metrics'])
            row['converged'] = record['converged']
            assert row['iterations'] == record['iterations']
        rows[method].append(dict(scene=case['scene'], index=case['index'], snr_db=case['snr_db'],
            metrics=row['metrics'], iterations=row['iterations'], converged=row['converged']))
    if (i+1) % 60 == 0:
        print(json.dumps({'checked_paired_inputs': i+1, 'planned': 300}), flush=True)

summary = {m: {str(s): aggregate([r for r in rows[m] if r['snr_db']==s]) for s in SNRS} for m in names}
assert all(v['inputs']==50 and v['decisions']==2000 for group in summary.values() for v in group.values())
overall = {m: aggregate(rows[m]) for m in names}
result = dict(status='INTERIM_SAVED_DATA_CHECKED', verification_status='ANALYZED',
    checked_at=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),
    scenes=list(range(50)), snrs=SNRS, total_method_inputs=1200,
    paired_coverage_verified=True, methods=summary, overall=overall,
    source_plan_sha256=sha256(OUT/'PLAN.json'), script_sha256=sha256(__file__),
    limitations=[
        'Fixed first 50 of the planned 500 scenes, not selected by performance; interim descriptive results.',
        'All activity predictions rescored. Historical STMP-LR channel NMSE uses full predictions for scene 0 and retained per-user error statistics for scenes 1-49.',
        'Other three arms rescored from full saved channel predictions; finite iteration-limit outputs included.',
        'No inference rerun, no manuscript update, no statistical significance or population equivalence claim.',
        'Across-backbone comparisons are receiver comparisons; within-backbone activity-evidence replacement preserves the frozen receiver configuration.',
    ],
    fallacy_scan=dict(coverage='11/11', interpretation='Descriptive paired comparison only; no significance testing or independent-device sampling assumption.'),
    source_hashes_file='SOURCE_HASHES.json', paired_rows_file='PAIRED_ROWS.json')
write_json(HERE/'SOURCE_HASHES.json', sources)
write_json(HERE/'PAIRED_ROWS.json', rows)
result['source_hashes_sha256'] = sha256(HERE/'SOURCE_HASHES.json')
result['paired_rows_sha256'] = sha256(HERE/'PAIRED_ROWS.json')
write_json(HERE/'SUMMARY.json', result)
print(json.dumps({'methods':summary,'overall':overall}, ensure_ascii=False), flush=True)
