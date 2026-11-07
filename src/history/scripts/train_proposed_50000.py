"""Independent 50,000-channel training using the established random-start recipe.

Prepare once, then run first -> independent denoising -> second -> activity -> bind.
No small-sample training or receiver performance experiment is launched.
"""
from copy import deepcopy
from pathlib import Path
import argparse
import json
import math
import os
import subprocess
import sys
import time

import train_proposed_sizes as sizes

ROOT = sizes.ROOT


def prepare(output, *, device, smoke):
    if (output / 'PLAN.json').exists():
        return verify(output)
    if output.exists() and any(output.iterdir()):
        raise FileExistsError('Preparation requires an empty run directory')
    recipe = sizes.load_recipe()
    prior = sizes.load_prior(recipe)
    data = sizes.load_data(recipe, prior)
    train_ids = sizes.np.load(ROOT / 'data/proposed/train_identities.npy')
    val_ids = sizes.np.load(ROOT / 'data/proposed/validation_identities.npy')
    if sizes.np.intersect1d(train_ids[:, 0], val_ids[:, 0]).size:
        raise ValueError('Training and validation scenes overlap')
    output.mkdir(parents=True)
    initial = sizes.make_initialization(output / 'initialization', recipe['scale'])
    counts = dict(train=16 if smoke else 50000, validation=16 if smoke else 5000)
    if any(len(data[key]) < value for key, value in counts.items()):
        raise ValueError('Incomplete channel bank')
    selected_prior = sizes.bank_prior(output / 'data', prior,
        sizes.np.arange(counts['train']), sizes.np.arange(counts['validation']), recipe['scale'])
    config = deepcopy(recipe)
    config['prior_definition'] = sizes.relative(output / 'data/prior_definition.json')
    config['prior_definition_sha256'] = sizes.sha(ROOT / config['prior_definition'])
    config['data_files'] = selected_prior['data_files']
    config['moments_file'] = selected_prior['moments_file']
    config['bank'].update(train_samples=counts['train'], validation_samples=counts['validation'])
    config['runtime'].update(device=device, threads=1)
    config['random_start_training'] = dict(initialization='random', pretraining_samples=0,
        smoke_only=smoke, source_recipe='scripts/train_proposed_sizes.py',
        selection='Fixed-noise validation only; no test-based model selection')
    for index, stage in enumerate(sizes.STAGES):
        settings = config[stage]
        settings.update(initial_checkpoint=initial[stage]['path'],
            initial_checkpoint_sha256=initial[stage]['sha256'],
            seed=202610180720001 + 2 * index, validation_seed=202610180720002 + 2 * index,
            selection='Minimum fixed-noise validation objective, including initial baseline')
        settings.pop('continuation', None)
        settings.pop('continuation_schedule', None)
        if stage == 'first':
            settings.update(maximum_epochs=200, minimum_epochs=200, validation_patience=201,
                stopping='Exactly 200 complete data epochs; no validation early stop')
        if smoke:
            settings.update(maximum_epochs=1, minimum_epochs=1, validation_patience=2,
                batch_size=8, microbatch_size=4, checkpoint_seconds=10)
    sizes.save(output / 'training.json', config)
    sources = sizes.source_hashes()
    for path in (Path(__file__), Path(sizes.__file__)):
        sources[sizes.relative(path)] = sizes.sha(path)
    frozen = sizes.read(ROOT / 'configs/mainline_assets.json')
    # The exported copy omits historical L-DAMP results. Record that boundary;
    # all available frozen assets and the complete Proposed binding are checked.
    from afdm_jadcedd.algorithm.proposed.configuration import verify as verify_proposed
    verify_proposed()
    mainline = {name:digest for name, digest in frozen['sha256'].items() if (ROOT / name).exists()}
    unavailable = [name for name in frozen['sha256'] if name not in mainline]
    plan = dict(schema='proposed-50000-training-v1', created_unix=time.time(),
        smoke_only=smoke, device=device, samples=counts, initialization=initial,
        configuration_sha256=sizes.sha(output / 'training.json'), source_sha256=sources,
        mainline_sha256=mainline, historical_assets_not_exported=unavailable,
        stages=['first', 'denoising', 'second', 'activity', 'bind'],
        first_optimizer_steps=config['first']['maximum_epochs'] * math.ceil(counts['train']/config['first']['batch_size']),
        maximum_epochs={s:config[s]['maximum_epochs'] for s in sizes.STAGES},
        minimum_epochs={s:config[s]['minimum_epochs'] for s in sizes.STAGES},
        train_validation_scenes_disjoint=True)
    for name in ('experiment/channel_denoising.py', 'experiment/_common.py',
                 'experiment/_support/settings.py', 'experiment/_support/storage.py'):
        plan['source_sha256'][name] = sizes.sha(ROOT / name)
    sizes.save(output / 'PLAN.json', plan)
    return verify(output)


def verify(output):
    plan = sizes.read(output / 'PLAN.json')
    if sizes.sha(output / 'training.json') != plan['configuration_sha256']:
        raise ValueError('Training configuration changed')
    for mapping in (plan['source_sha256'], plan['mainline_sha256']):
        for name, digest in mapping.items():
            if sizes.sha(ROOT / name) != digest:
                raise ValueError('Prepared dependency changed: ' + name)
    for item in plan['initialization'].values():
        if sizes.sha(ROOT / item['path']) != item['sha256']:
            raise ValueError('Random initialization changed')
    config = sizes.load_recipe(output / 'training.json')
    sizes.load_data(config, sizes.load_prior(config))
    sizes.save(output / 'PREPARATION_CHECK.json', dict(status='PASS', samples=plan['samples'],
        device=plan['device'], source_and_mainline_verified=True, smoke_only=plan['smoke_only']))
    return plan


def prepare_cuda_continuation(output, parent):
    """Preserve the parent and continue its exact budget/random-query schedule."""
    if output.exists():
        raise FileExistsError('Continuation requires a new run directory')
    previous_plan = sizes.read(parent / 'PLAN.json')
    paused = sizes.read(parent / 'model/first/status.json')
    if paused['status'] != 'PAUSED' or previous_plan['device'] != 'cuda':
        raise ValueError('A safely paused CUDA first-stage run is required')
    config = sizes.read(parent / 'training.json')
    config['cuda_execution'] = dict(first=dict(batch_size=64, foreach_ema=True),
        precision='float32', random_query_draw_size=config['first']['microbatch_size'],
        effective_optimizer_batch_unchanged=True, validation_execution_unchanged=True)
    folder = parent / 'model/first'
    assets = dict(checkpoint=folder/'last.pt', specification=folder/'specification.json',
                  best_checkpoint=folder/'first_best.pt', baseline=folder/'baseline.json')
    source = dict(execution_only=True)
    for key, path in assets.items():
        source[key] = sizes.relative(path)
        source[key+'_sha256'] = sizes.sha(path)
    config['first']['continuation'] = source
    output.mkdir(parents=True)
    sizes.save(output/'training.json', config)
    plan = deepcopy(previous_plan)
    plan.update(created_unix=time.time(), parent_run=sizes.relative(parent),
        parent_plan_sha256=sizes.sha(parent/'PLAN.json'),
        configuration_sha256=sizes.sha(output/'training.json'), source_sha256=sizes.source_hashes())
    for name in ('scripts/train_proposed_50000.py', 'scripts/train_proposed_sizes.py',
                 'experiment/channel_denoising.py', 'experiment/_common.py',
                 'experiment/_support/settings.py', 'experiment/_support/storage.py'):
        plan['source_sha256'][name] = sizes.sha(ROOT / name)
    sizes.save(output/'PLAN.json', plan)
    return verify(output)


def run(output):
    # Exclusive lock is released by the OS if the process exits unexpectedly.
    lock = (output / 'run.lock').open('a+b')
    if os.name == 'nt':
        import msvcrt
        lock.seek(0)
        if not lock.read(1):
            lock.write(b'0'); lock.flush()
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    started = time.time()
    if os.name == 'nt':
        import ctypes
        # This process keeps training awake without changing the power plan.
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    try:
        plan = verify(output)
        sizes.save(output / 'STATUS.json', dict(status='RUNNING', pid=os.getpid(),
            started_unix=started, device=plan['device'], stages=plan['stages']))
        code = 0
        for stage in plan['stages']:
            verify(output)
            sizes.save(output / 'STATUS.json', dict(status='RUNNING', pid=os.getpid(),
                stage=stage, started_unix=started, updated_unix=time.time(), device=plan['device']))
            if stage == 'denoising':
                commands = denoising_commands(output, plan)
            else:
                commands = [[sys.executable, '-X', 'utf8', '-u', '-B', str(ROOT / 'scripts/train_proposed.py'),
                    '--config', str(output / 'training.json'), '--stage', stage,
                    '--output', str(output / 'model'), '--device', plan['device'], '--teachers', 'run']]
            for command in commands:
                logs = output / 'logs'
                logs.mkdir(exist_ok=True)
                with (logs / (stage + '.log')).open('a', encoding='utf-8') as log:
                    child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
                    sizes.save(output / 'CURRENT_JOB.json', dict(stage=stage, child_pid=child.pid,
                        supervisor_pid=os.getpid(), command=command, started_unix=time.time()))
                    code = child.wait()
                if code:
                    break
            if code:
                break
        if code not in (0, 2):
            raise RuntimeError(f'{stage} failed with exit code {code}; see logs/{stage}.log')
        result = dict(status='COMPLETED' if code == 0 else 'PAUSED', pid=os.getpid(),
            exit_code=code, started_unix=started, updated_unix=time.time(),
            receiver=sizes.relative(output / 'model/receiver.json') if code == 0 else None,
            smoke_only=plan['smoke_only'], receiver_performance_evaluated=False)
        sizes.save(output / 'STATUS.json', result)
        if code == 0:
            sizes.save(output / 'COMPLETE.json', result)
        return code
    except BaseException as error:
        sizes.save(output / 'STATUS.json', dict(status='FAILED', pid=os.getpid(),
            error=repr(error), updated_unix=time.time()))
        raise
    finally:
        if os.name == 'nt':
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        lock.close()


def denoising_commands(output, plan):
    config = sizes.read(output / 'training.json')
    folder = output / 'model/first'
    record = sizes.read(folder / 'complete.json')
    checkpoint = folder / 'first_best.pt'
    if (record['epochs'] != plan['maximum_epochs']['first']
            or record['optimizer_steps'] != plan['first_optimizer_steps']
            or sizes.sha(checkpoint) != record['weight_sha256']):
        raise ValueError('First-stage budget and selected checkpoint must be complete')
    first_config = output / 'model/first_receiver.json'
    sizes.save(first_config, dict(schema='proposed-first-score-evaluation-v1',
        first_checkpoint=sizes.relative(checkpoint), first_checkpoint_sha256=sizes.sha(checkpoint),
        prior_definition=config['prior_definition'], prior_definition_sha256=config['prior_definition_sha256'],
        scale=config['scale'], completion_record=sizes.relative(folder / 'complete.json'),
        completion_record_sha256=sizes.sha(folder / 'complete.json'),
        initialization='random', pretraining_samples=0))
    destination = output / 'first_denoising'
    script = str(ROOT / 'experiment/channel_denoising.py')
    commands = []
    if not (destination / 'PLAN.json').exists():
        command = [sys.executable, '-X', 'utf8', '-u', '-B', script, 'plan', '--output', str(destination),
            '--first-only', '--full-config', str(first_config), '--device', plan['device']]
        # An explicitly supplied, completed small model may be registered while first trains.
        small = output / 'SMALL_MODEL.json'
        if small.exists():
            reference = sizes.read(small)
            path = Path(reference['configuration'])
            if sizes.sha(path) != reference['sha256']:
                raise ValueError('Registered small-model configuration changed')
            command += ['--small-config', str(path)]
        if plan['smoke_only']:
            command += ['--scenes', '1', '--candidates', '1', '--values', '0.1', '1']
        commands.append(command)
    commands.append([sys.executable, '-X', 'utf8', '-u', '-B', script, 'run', '--output', str(destination)])
    return commands


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'prepare-cuda-continuation', 'verify', 'run', 'status', 'attach-small'))
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--device', default='cuda', choices=('cpu', 'mps', 'cuda'))
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--small-config', type=Path)
    parser.add_argument('--from-run', type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / 'runs'):
        raise ValueError('Use an independent directory under runs/')
    if args.command == 'prepare':
        result = prepare(output, device=args.device, smoke=args.smoke)
        print(json.dumps({k:result[k] for k in ('samples', 'device', 'maximum_epochs', 'smoke_only')}))
    elif args.command == 'prepare-cuda-continuation':
        if args.from_run is None:
            parser.error('--from-run is required')
        prepare_cuda_continuation(output, args.from_run.resolve())
        print('Prepared independent continuation with unchanged training budget')
    elif args.command == 'verify':
        verify(output)
        print('PASS')
    elif args.command == 'attach-small':
        if args.small_config is None:
            parser.error('--small-config is required')
        if (output / 'first_denoising/PLAN.json').exists():
            raise ValueError('Denoising already planned; preserve it and use a new comparison directory')
        from channel_denoising import first_score_bundles
        path = args.small_config.resolve()
        bundles, _ = first_score_bundles(path)
        if bundles['proposed']['train_samples'] != 5000:
            raise ValueError('A completed 5,000-channel first model is required')
        sizes.save(output / 'SMALL_MODEL.json', dict(configuration=str(path), sha256=sizes.sha(path)))
        print('Registered verified 5,000-channel first model')
    elif args.command == 'status':
        print(json.dumps(sizes.read(output / 'STATUS.json'), indent=2))
        for stage in sizes.STAGES:
            path = output / 'model' / stage / 'status.json'
            if path.exists():
                print(stage, path.read_text())
    else:
        return run(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
