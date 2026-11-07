"""Finish the active user-count evaluation before resuming cross-channel cases."""
import ctypes
import json
import os
from pathlib import Path
import subprocess
import time
import psutil

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT/'results/new_models_paired_20261019_v2'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, data):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2), encoding='utf-8')
    os.replace(temp, path)


def check_process(pid, marker):
    process = psutil.Process(pid)
    command = ' '.join(process.cmdline()).replace('\\', '/')
    if str(ROOT).replace('\\', '/') not in command or marker not in command:
        raise ValueError('Process does not belong to this evaluation')
    return process


def main():
    state = read(OUTPUT/'STATUS.json')
    user_state = read(OUTPUT/'user_count/STATUS.json')
    cross_state = read(OUTPUT/'cross_channel/STATUS.json')
    user = check_process(user_state['pid'], 'evaluate_saved_baseline_inputs.py')
    cross = check_process(cross_state['pid'], 'evaluate_saved_baseline_inputs.py')
    supervisor = check_process(state['pid'], 'run_paired_evaluations.py')
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    try:
        supervisor.terminate(); supervisor.wait(timeout=20)
        # Completed cases remain immutable. An interrupted, unsaved case restarts later.
        cross.terminate(); cross.wait(timeout=20)
        save(OUTPUT/'SEQUENTIAL_TRANSITION.json', dict(time_unix=time.time(),
            previous_supervisor=state, interrupted_cross_case=cross_state,
            policy='Finish user_count, then resume cross_channel; retain every verified completed case.'))
        cross_state.update(status='QUEUED', reason='WAITING_FOR_USER_COUNT', updated_unix=time.time())
        save(OUTPUT/'cross_channel/STATUS.json', cross_state)
        state.update(pid=os.getpid(), execution_order=['user_count', 'cross_channel'])
        state['jobs']['cross_channel'].update(status='QUEUED', reason='WAITING_FOR_USER_COUNT')
        while user.is_running():
            state.update(status='RUNNING', current_job='user_count', updated_unix=time.time())
            save(OUTPUT/'STATUS.json', state)
            try:
                user.wait(timeout=20)
            except psutil.TimeoutExpired:
                pass
        summary_path = OUTPUT/'user_count/SUMMARY.json'
        if not summary_path.exists() or read(summary_path)['status'] != 'COMPLETE':
            state.update(status='FAILED', reason='User-count process ended without complete summary')
            state['jobs']['user_count']['status'] = 'FAILED'
            save(OUTPUT/'STATUS.json', state)
            return 1
        state['jobs']['user_count']['status'] = 'COMPLETE'
        command = [str(ROOT/'.venv/Scripts/python.exe'), '-X', 'utf8', '-u', '-B',
            'scripts/evaluate_saved_baseline_inputs.py', 'run', '--output', str(OUTPUT/'cross_channel')]
        with (OUTPUT/'logs/cross_channel.log').open('a', encoding='utf-8') as log:
            child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW,
                env=dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1'))
            state['jobs']['cross_channel'].update(status='RUNNING', pid=child.pid, command=command)
            state['jobs']['cross_channel'].pop('reason', None)
            while child.poll() is None:
                state.update(status='RUNNING', current_job='cross_channel', updated_unix=time.time())
                save(OUTPUT/'STATUS.json', state)
                time.sleep(20)
            state['jobs']['cross_channel'].update(status='COMPLETE' if child.returncode == 0 else 'FAILED', exit_code=child.returncode)
        state.update(status=state['jobs']['cross_channel']['status'], updated_unix=time.time())
        save(OUTPUT/'STATUS.json', state)
        return child.returncode
    finally:
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)


if __name__ == '__main__':
    raise SystemExit(main())
