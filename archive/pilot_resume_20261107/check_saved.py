"""Read-only validation of the failed pilot sweep before author-requested resume."""
from collections import Counter
import json
from pathlib import Path
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from experiment.studies.white_followup import receivers as r


def main():
    folder = r.stage_folder('pilot_frames')
    r.no_other_execution(folder)
    plan = r.verify_plan(folder)
    r.adoption_gate('pilot_frames')
    cases = r.read_json(folder / 'INPUTS.json')
    tasks = r.read_json(folder / 'TASKS.json')
    r.validate_coverage(cases, plan['conditions'])
    expected = {t['key'] for t in tasks}
    pointers = {p.stem: p for p in (folder / 'results').glob('*.json')}
    if not set(pointers) <= expected:
        raise ValueError('Unexpected result pointers')
    native = Path(plan['native_directory'])
    expected_native = {t['key'] for t in tasks if 'reuse' not in t}
    if any(p.name not in expected_native for p in native.iterdir()):
        raise ValueError('Unexpected native output')
    unpointed = [t['key'] for t in tasks if t['key'] not in pointers
                 and (native / t['key']).exists()]
    if unpointed:
        raise ValueError('Unpointed/partial output: ' + repr(unpointed))
    results, pointer_hashes = [], {}
    for task in tasks:
        if task['key'] in pointers:
            results.append(r.validate_result(folder, plan, task, cases[task['position']]))
            pointer_hashes[task['key']] = r.sha256(pointers[task['key']])
            if len(results) % 250 == 0:
                print(json.dumps({'rescored': len(results), 'saved': len(pointers)}), flush=True)
    remaining = [t for t in tasks if t['key'] not in pointers]
    required = sum(r.estimated_bytes(t, cases[t['position']]) for t in remaining)
    if not r.disk_ready(plan, required):
        raise RuntimeError('Insufficient result disk reserve')
    report = dict(status='PASS', planned=len(tasks), saved_predictions_rescored=len(results),
                  complete_by_method=dict(Counter(row['method'] for row in results)),
                  remaining=len(remaining), frozen_assets_verified=len(plan['assets']),
                  plan_sha256=r.sha256(folder / 'PLAN.json'),
                  original_failure_sha256=r.sha256(folder / 'FAILURE.json'),
                  unknown_results=[], partial_native_outputs=[],
                  expected_additional_bytes=required, free_result_bytes=shutil.disk_usage(native).free,
                  pointer_sha256=pointer_hashes, checked_unix=time.time(),
                  material_passport=dict(origin_skill='academic-research-suite/experiment-agent',
                                         origin_mode='run', verification_status='VERIFIED',
                                         scope='Saved-result integrity only; stage not complete'))
    r.write_json(Path(__file__).with_name('SAVED_RESULTS.json'), report)
    print(json.dumps({k: v for k, v in report.items() if k != 'pointer_sha256'}), flush=True)


if __name__ == '__main__':
    main()
