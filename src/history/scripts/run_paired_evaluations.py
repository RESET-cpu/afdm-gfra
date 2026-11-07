"""Prepare denoising reuse and supervise independent paired evaluation jobs."""
import argparse
import ctypes
import hashlib
import json
import msvcrt
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT/'results/new_models_paired_20261019_v2'
OLD = ROOT/'runs/proposed_50000_cuda_graph_20261018/first_denoising'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2), encoding='utf-8')
    os.replace(temp, path)


def prepare_denoising():
    target = OUTPUT/'channel_denoising'
    old, new = read(OLD/'PLAN.json'), read(target/'PLAN.json')
    assert read(OLD/'SUMMARY.json')['status'] == 'COMPLETE'
    a, b = old['experiment'], new['experiment']
    for key in ('scenes', 'seed', 'users', 'candidates', 'values', 'scale'):
        assert a[key] == b[key], key
    for method in ('proposed', 'proposed_small'):
        before = a['proposed_bundles'][method]['configuration']
        after = b['proposed_bundles'][method]['configuration']
        assert before['first_checkpoint_sha256'] == after['first_checkpoint_sha256']
        assert before['initialization']['normalized_training_second_moment'] == after['initialization']['normalized_training_second_moment']
    # Preserve the original generator and denoising implementation identity.
    for name, expected in old['source_and_weight_sha256'].items():
        normalized = name.replace('\\', '/')
        if normalized.startswith('src/afdm_jadcedd/system/') or normalized == 'experiment/channel_denoising.py':
            assert sha(ROOT/name) == expected, name
    manifest = dict(source=str(OLD), source_plan_sha256=sha(OLD/'PLAN.json'),
                    source_summary_sha256=sha(OLD/'SUMMARY.json'), cases={})
    for scene in range(b['scenes']):
        for condition, variance in enumerate(b['values']):
            key = f'scene{scene:03d}/condition{condition:02d}'
            source, dest = OLD/key, target/key
            identity = read(source/'INPUT.json')
            assert identity['seed'] == b['seed']+scene and identity['variance'] == variance
            dest.mkdir(parents=True, exist_ok=True)
            files = ['INPUT.json']
            for method in ('noisy', 'gaussian', 'genie_bound'):
                record = read(source/f'{method}.json')
                assert record['status'] == 'COMPLETE'
                assert record['scene'] == scene and record['condition'] == condition
                assert record['compact_sha256'] == sha(source/f'{method}.npz')
                files.extend((f'{method}.json', f'{method}.npz'))
            manifest['cases'][key] = {}
            for name in files:
                digest = sha(source/name)
                if (dest/name).exists():
                    assert sha(dest/name) == digest
                else:
                    shutil.copy2(source/name, dest/name)
                assert sha(dest/name) == digest
                manifest['cases'][key][name] = digest
    save(target/'REUSED_INPUTS.json', manifest)
    new['source_and_weight_sha256'][str(target/'REUSED_INPUTS.json')] = sha(target/'REUSED_INPUTS.json')
    new['source_and_weight_sha256'][str(Path(__file__))] = sha(Path(__file__))
    new['reuse'] = dict(source=str(OLD), cases=len(manifest['cases']),
        baseline_methods=['noisy', 'gaussian', 'genie_bound'],
        regenerated_queries_must_match_preserved_input_hashes=True,
        new_methods=['proposed', 'proposed_small'],
        purpose='Evaluate first-score means and newly trained second-score uncertainty on the original queries.')
    save(target/'PLAN.json', new)
    print(json.dumps(dict(reused_cases=len(manifest['cases']), reused_baseline_results=3*len(manifest['cases']))))


def supervise():
    with (OUTPUT/'run.lock').open('a+b') as lock:
        lock.seek(0)
        if not lock.read(1):
            lock.write(b'0'); lock.flush()
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
        children, logs, state = {}, {}, {}
        (OUTPUT/'logs').mkdir(exist_ok=True)
        try:
            # Independent single-thread CPU suppliers, with shared GPU inference.
            for job in ('user_count', 'cross_channel', 'channel_denoising'):
                script = 'experiment/channel_denoising.py' if job == 'channel_denoising' else 'scripts/evaluate_saved_baseline_inputs.py'
                command = [sys.executable, '-X', 'utf8', '-u', '-B', script, 'run', '--output', str(OUTPUT/job)]
                logs[job] = (OUTPUT/'logs'/f'{job}.log').open('a', encoding='utf-8')
                child = subprocess.Popen(command, cwd=ROOT, stdout=logs[job], stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    env=dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1'))
                children[job] = child
                state[job] = dict(status='RUNNING', pid=child.pid, command=command, started_unix=time.time())
            while True:
                for job, child in children.items():
                    code = child.poll()
                    if code is not None and state[job]['status'] == 'RUNNING':
                        state[job].update(status='COMPLETE' if code == 0 else 'FAILED', exit_code=code, ended_unix=time.time())
                running = any(s['status'] == 'RUNNING' for s in state.values())
                status = 'RUNNING' if running else ('COMPLETE' if all(s['status'] == 'COMPLETE' for s in state.values()) else 'FAILED')
                save(OUTPUT/'STATUS.json', dict(status=status, pid=os.getpid(), jobs=state, updated_unix=time.time()))
                if not running:
                    return 0 if status == 'COMPLETE' else 1
                time.sleep(20)
        finally:
            for stream in logs.values():
                stream.close()
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare-denoising', 'run'))
    args = parser.parse_args()
    if args.action == 'prepare-denoising':
        prepare_denoising()
    else:
        raise SystemExit(supervise())
