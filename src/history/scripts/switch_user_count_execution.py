"""Preserve the serial run and transfer it to the validated concurrent candidate."""
import json
from pathlib import Path
import subprocess
import time
import psutil

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT/'results/new_models_paired_20261019_v2'
NEW = ROOT/'results/new_models_paired_20261019_cuda_graph'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')


def main():
    if NEW.exists():
        raise ValueError('Candidate output already exists')
    for name in ('graph_cross40_v2', 'graph_user20', 'graph_user100'):
        assert read(ROOT/'results/receiver_execution_20261019'/name/'REPORT.json')['exact']
    old_state, user_state = read(OLD/'STATUS.json'), read(OLD/'user_count/STATUS.json')
    processes = []
    for state, expected in ((old_state, 'sequence_existing_evaluations.py'),
                            (user_state, 'evaluate_saved_baseline_inputs.py')):
        process = psutil.Process(state['pid'])
        command = ' '.join(process.cmdline()).replace('\\', '/')
        assert Path(process.cwd()).resolve() == ROOT and expected in command
        processes.append(process)
    record = dict(previous_supervisor=old_state, previous_user_count=user_state,
        new_output=str(NEW), time_unix=time.time(),
        interrupted_unsaved_case='Restart in new output; completed cases copied with hash verification')
    save(OLD/'CUDA_GRAPH_TRANSITION.json', record)
    for process in processes:
        process.terminate(); process.wait(timeout=20)
    python = str(ROOT/'.venv/Scripts/python.exe')
    subprocess.run([python, '-X', 'utf8', '-u', '-B', 'scripts/run_parallel_user_count.py', 'prepare', '--workers', '4'],
                   cwd=ROOT, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    with (NEW/'supervisor.stdout.log').open('a', encoding='utf-8') as out, (NEW/'supervisor.stderr.log').open('a', encoding='utf-8') as err:
        child = subprocess.Popen([python, '-X', 'utf8', '-u', '-B', 'scripts/run_parallel_user_count.py', 'run'],
            cwd=ROOT, stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)
    save(OLD/'STATUS.json', dict(status='SUPERSEDED', successor=str(NEW), successor_pid=child.pid,
        execution_order=['user_count', 'cross_channel'], updated_unix=time.time()))
    save(OLD/'user_count/STATUS.json', dict(status='SUPERSEDED', successor=str(NEW/'user_count'),
        completed=read(NEW/'user_count/PLAN.json')['execution']['old_results_reused'], updated_unix=time.time()))
    print(json.dumps(dict(started=True, pid=child.pid, output=str(NEW))), flush=True)


if __name__ == '__main__':
    main()
