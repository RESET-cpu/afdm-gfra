"""Extend the immutable 200-scene experiment after it has finished and passed.

The 200-scene process is never interrupted. Its scene records are copied with
file-identity checks, then the 600-scene runner resumes at the missing cases.
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback
from run import ROOT, HERE, OUT, read, save, sha, verify_sources

PREVIOUS = ROOT / 'results/baseline_comparison_200_20261017'
PHASE = ROOT / 'results/phase_optimization_20261017'


def status(stage, **extra):
    save(OUT / 'CONTINUATION_STATUS.json', dict(status='RUNNING', stage=stage,
         pid=os.getpid(), updated_unix=time.time(), **extra))


def compatible(previous, current):
    assert previous['scenes'] == 200 and current['scenes'] == 600
    assert current['seeds'][:200] == previous['seeds']
    assert len(set(current['seeds'])) == 600
    for key in ['snr_db', 'methods', 'configurations', 'scale', 'users', 'frames',
                'antennas', 'noise_mode', 'phase_mode', 'phase_controls', 'proposed_device',
                'threads_per_worker', 'proposed_workers', 'weight_sha256', 'environment',
                'phase_selection_sha256', 'qualification_status_sha256', 'noise_decision_sha256',
                'real_pipeline_preflight_sha256', 'public_integration_sha256']:
        assert previous[key] == current[key], key
    for name, identity in previous['source_sha256'].items():
        if name.startswith(('src/', 'configs/')) or name.endswith('proposed_original_snr8_10_20261016/analyze.py'):
            assert current['source_sha256'][name] == identity, name


def identities(folder):
    paths = sorted(folder.rglob('*'))
    assert not any(p.is_symlink() for p in paths)
    return {str(p.relative_to(folder)): sha(p) for p in paths if p.is_file()}


def copy_prefix(previous, destination, count, seeds):
    destination.mkdir(parents=True, exist_ok=True)
    records = []
    for scene in range(count):
        name = f'scene{scene:03d}'
        source, target = previous / name, destination / name
        assert read(source / 'READY.json')['seed'] == seeds[scene]
        files = identities(source)
        if target.exists():
            assert identities(target) == files, f'Existing prefix differs: {name}'
        else:
            temporary = destination / (name + '.copying')
            shutil.copytree(source, temporary, dirs_exist_ok=True)
            assert identities(temporary) == files
            os.replace(temporary, target)
        records.append(dict(scene=scene, seed=seeds[scene], files=files))
    return records


def execute(stage, script, *arguments):
    status(stage)
    with (OUT / (stage + '.log')).open('a') as log:
        process = subprocess.Popen([sys.executable, '-B', str(script), *arguments],
                                   stdout=log, stderr=subprocess.STDOUT)
        status(stage, child_pid=process.pid)
        code = process.wait()
    if code:
        raise RuntimeError(f'{stage} failed with exit code {code}')


def main():
    current = verify_sources()
    previous = read(PREVIOUS / 'PLAN.json')
    compatible(previous, current)
    assert sha(PREVIOUS / 'PLAN.json') == current['reused_prefix']['plan_sha256']
    status('waiting_for_original_200')
    while True:
        state = read(PHASE / 'CONTINUATION_STATUS.json')
        run = read(PREVIOUS / 'RUN.json')
        if state['status'] == 'RESULTS_READY_FOR_REVIEW':
            assert run['status'] == 'INFERENCE_COMPLETE'
            assert read(PREVIOUS / 'VERIFICATION.json')['status'] == 'PASS'
            break
        if state['status'] == 'FAILED' or run['status'] == 'FAILED':
            raise RuntimeError('Original 200-scene run requires diagnosis; it was not restarted')
        os.kill(state['pid'], 0)
        time.sleep(5)
    execute('prefix_record_audit', ROOT / 'experiments/phase_optimization_20261017/audit_comparison_records.py')
    verify_sources()
    status('copying_verified_prefix')
    records = copy_prefix(PREVIOUS / 'scenes', OUT / 'scenes', 200, current['seeds'])
    save(OUT / 'REUSED_PREFIX.json', dict(status='PASS', physical_scenes=200,
         receiver_runs=7000, source=str(PREVIOUS), source_plan_sha256=sha(PREVIOUS / 'PLAN.json'),
         source_verification_sha256=sha(PREVIOUS / 'VERIFICATION.json'),
         source_record_audit_sha256=sha(PREVIOUS / 'RECORD_AUDIT.json'), records=records))
    execute('comparison_600', HERE / 'run.py', 'run')
    execute('comparison_report', HERE / 'report.py')
    execute('record_audit', HERE / 'record_audit.py')
    save(OUT / 'CONTINUATION_STATUS.json', dict(status='RESULTS_READY_FOR_REVIEW',
         updated_unix=time.time(), physical_scenes=600, receiver_runs=21000,
         reused_scenes=200, additional_scenes=400, figure=str(OUT / 'comparison.png')))


if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        save(OUT / 'CONTINUATION_STATUS.json', dict(status='FAILED', error=repr(error),
             traceback=traceback.format_exc(), updated_unix=time.time()))
        raise
