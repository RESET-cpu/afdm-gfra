"""Independent 200-epoch auxiliary runs using the completed 5k/50k first scores.

The only supported budget migration is within epoch one, when the old and new
cosine schedules have the same learning rate. Original artifacts stay intact.
"""
import argparse
from copy import deepcopy
import ctypes
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from afdm_jadcedd.experiment.training.proposed.common import (
    load_data, load_prior, relative, resolve, source_hashes,
)
from afdm_jadcedd.experiment.training.proposed.auxiliary import atomic_json, first_record
from afdm_jadcedd.utils import sha256

DEFAULT = ROOT / 'runs/proposed_auxiliary_200_cuda_20261018'
PARENT = ROOT / 'runs/proposed_50000_cuda_graph_20261018'
SMALL = ROOT / 'runs/proposed_sample_sizes_20261018'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def same(a, b):
    """Exact recursive comparison of all numerical resume state."""
    import numpy as np
    import torch
    if torch.is_tensor(a):
        return torch.is_tensor(b) and a.dtype == b.dtype and torch.equal(a, b)
    if isinstance(a, np.ndarray):
        return isinstance(b, np.ndarray) and a.dtype == b.dtype and np.array_equal(a, b)
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return type(a) is type(b) and len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def migrate(source, target, specification):
    import torch
    from afdm_jadcedd.experiment.training.proposed.auxiliary import atomic_torch
    old_spec = source / 'specification.json'
    state = torch.load(source / 'last.pt', map_location='cpu', weights_only=False)
    if (state['epoch'] != 1 or state['stage'] != 'second'
            or state['specification_sha256'] != sha256(old_spec)
            or state['selected_epoch'] != 0
            or read(source / 'status.json')['status'] != 'PAUSED'):
        raise ValueError('Only a paused second-score checkpoint within epoch one is supported')
    target.mkdir(parents=True, exist_ok=False)
    atomic_json(target / 'specification.json', specification)
    new_hash = sha256(target / 'specification.json')
    moved = dict(state, specification_sha256=new_hash)
    atomic_torch(target / 'last.pt', moved)
    loaded = torch.load(target / 'last.pt', map_location='cpu', weights_only=False)
    assert same({k:v for k,v in state.items() if k != 'specification_sha256'},
                {k:v for k,v in loaded.items() if k != 'specification_sha256'})
    selected = torch.load(source / 'second_best.pt', map_location='cpu', weights_only=False)
    if selected['metadata']['specification_sha256'] != sha256(old_spec):
        raise ValueError('Selected checkpoint specification differs')
    revised = deepcopy(selected)
    revised['metadata']['specification_sha256'] = new_hash
    atomic_torch(target / 'second_best.pt', revised)
    restored = torch.load(target / 'second_best.pt', map_location='cpu', weights_only=False)
    restored['metadata']['specification_sha256'] = selected['metadata']['specification_sha256']
    assert same(selected, restored)
    for name in ('baseline.json', 'history.json'):
        if (source / name).exists():
            shutil.copy2(source / name, target / name)
    atomic_json(target / 'MIGRATION.json', dict(
        source=relative(source), source_sha256={name:sha256(source / name) for name in
            ('last.pt', 'second_best.pt', 'specification.json')},
        destination_specification_sha256=new_hash, epoch=state['epoch'],
        cursor=state['cursor'], optimizer_steps=state['steps'],
        exact_model_optimizer_ema_rng_cursor_history_comparison='PASS',
        change='200 total epochs; no early stopping; cosine decay now spans 200 epochs',
        learning_rate_before_and_after=specification['configuration']['second']['learning_rate']))


def prepare(output):
    if output.exists():
        raise ValueError('Use a new output directory; previous runs are preserved')
    if read(PARENT / 'STATUS.json')['status'] != 'PAUSED':
        raise ValueError('Pause the original supervisor before preparing continuation')
    old = read(PARENT / 'model/second/specification.json')
    if old['source_sha256'] != source_hashes():
        raise ValueError('Training source changed since the paused run')
    output.mkdir(parents=True)
    configs = {}
    for size in (50000, 5000):
        config = deepcopy(old['configuration']) if size == 50000 else read(SMALL / 'configs/n5000.json')
        config['runtime'] = dict(device='cuda', threads=1)
        config['output'] = relative(output / f'n{size}')
        if size == 5000:
            first = SMALL / 'n5000/first'
            for key, name in (('checkpoint', 'first_best.pt'), ('training_record', 'complete.json'),
                              ('training_specification', 'specification.json')):
                config['first_' + key] = relative(first / name)
        for stage in ('second', 'activity'):
            config[stage].update(maximum_epochs=200, minimum_epochs=200, validation_patience=201,
                stopping='Exactly 200 complete data epochs; no validation early stop')
        second = output / f'n{size}/second'
        for key, name in (('checkpoint', 'second_best.pt'), ('training_record', 'complete.json'),
                          ('training_specification', 'specification.json')):
            config['second_' + key] = relative(second / name)
        first_record(config)
        load_data(config, load_prior(config))
        for stage in ('second', 'activity'):
            if sha256(resolve(config[stage]['initial_checkpoint'])) != config[stage]['initial_checkpoint_sha256']:
                raise ValueError('Initialization changed')
        path = output / f'n{size}.json'
        atomic_json(path, config)
        configs[str(size)] = dict(path=relative(path), sha256=sha256(path),
            first_sha256=sha256(resolve(config['first_checkpoint'])))
        if size == 50000:
            spec = deepcopy(old)
            spec['configuration'] = config
            migrate(PARENT / 'model/second', second, spec)
    plan = dict(configs=configs, source_sha256=source_hashes(), script_sha256=sha256(__file__),
        mainline_sha256=sha256(ROOT / 'MAINLINE.json'),
        queue=[dict(samples=n, stage=s) for n in (50000, 5000) for s in ('second', 'activity', 'bind')],
        total_epochs=200, early_stopping=False, selected_weights='Minimum fixed validation loss',
        created_unix=time.time())
    atomic_json(output / 'PLAN.json', plan)
    atomic_json(output / 'STATUS.json', dict(status='PREPARED', queue=plan['queue']))
    print(json.dumps(plan, indent=2))


def verify(output):
    plan = read(output / 'PLAN.json')
    budget = plan['total_epochs']
    if type(budget) is not int or budget < 1:
        raise ValueError('A positive integer epoch budget is required')
    if (plan['source_sha256'] != source_hashes() or plan['script_sha256'] != sha256(__file__)
            or plan['mainline_sha256'] != sha256(ROOT / 'MAINLINE.json')):
        raise ValueError('Source or frozen mainline changed')
    for entry in plan['configs'].values():
        if sha256(resolve(entry['path'])) != entry['sha256']:
            raise ValueError('Configuration changed')
        config = read(resolve(entry['path']))
        first_record(config)
        if sha256(resolve(config['first_checkpoint'])) != entry['first_sha256']:
            raise ValueError('Frozen first changed')
        for stage in ('second', 'activity'):
            assert config[stage]['maximum_epochs'] == config[stage]['minimum_epochs'] == budget
            assert config[stage]['validation_patience'] > budget
    return plan


def worker(output, samples, stage):
    import torch
    from threadpoolctl import threadpool_limits
    from afdm_jadcedd.experiment.training.proposed.cli import bind, run_auxiliary
    plan = verify(output)
    config = read(resolve(plan['configs'][str(samples)]['path']))
    torch.set_num_threads(config['runtime']['threads'])
    prior = load_prior(config)
    with threadpool_limits(limits=config['runtime']['threads']):
        if stage == 'bind':
            bind(config, prior)
        elif not run_auxiliary(config, prior, stage):
            return 2
    return 0


def run(output):
    import msvcrt
    with (output / 'run.lock').open('a+b') as lock:
        lock.seek(0)
        if not lock.read(1):
            lock.write(b'0'); lock.flush()
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        kernel = ctypes.windll.kernel32
        kernel.GetCurrentProcess.restype = ctypes.c_void_p
        kernel.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        if not kernel.SetProcessAffinityMask(kernel.GetCurrentProcess(), 15):
            raise OSError('Cannot reserve the GPU supplier CPUs')
        kernel.SetThreadExecutionState(0x80000001)
        try:
            plan = verify(output)
            (output / 'logs').mkdir(exist_ok=True)
            for job in plan['queue']:
                verify(output)
                status = dict(status='RUNNING', pid=os.getpid(), updated_unix=time.time(), **job)
                atomic_json(output / 'STATUS.json', status)
                command = [sys.executable, '-X', 'utf8', '-u', '-B', __file__, 'worker',
                    '--output', str(output), '--samples', str(job['samples']), '--stage', job['stage']]
                with (output / 'logs' / f"n{job['samples']}_{job['stage']}.log").open('a', encoding='utf-8') as log:
                    child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
                    atomic_json(output / 'CURRENT_JOB.json', dict(**status, child_pid=child.pid, command=command))
                    code = child.wait()
                if code:
                    atomic_json(output / 'STATUS.json', dict(status='PAUSED' if code == 2 else 'FAILED',
                        exit_code=code, updated_unix=time.time(), **job))
                    return code
            atomic_json(output / 'STATUS.json', dict(status='COMPLETED', updated_unix=time.time()))
        finally:
            kernel.SetThreadExecutionState(0x80000000)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'verify', 'run', 'worker'))
    parser.add_argument('--output', type=Path, default=DEFAULT)
    parser.add_argument('--samples', type=int, choices=(5000, 50000))
    parser.add_argument('--stage', choices=('second', 'activity', 'bind'))
    args = parser.parse_args()
    args.output = args.output.resolve()
    if args.action == 'worker':
        raise SystemExit(worker(args.output, args.samples, args.stage))
    result = globals()[args.action](args.output)
    if args.action == 'run':
        raise SystemExit(result)
