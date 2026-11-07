"""Prepare and run the paired, randomly initialized training-size experiment."""
from pathlib import Path
from dataclasses import asdict
from copy import deepcopy
import argparse
import hashlib
import importlib
import json
import math
import os
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'experiment')]
import numpy as np
import torch
from afdm_jadcedd.algorithm.proposed.network import DirectCaiConfig, DirectCaiNetwork
from afdm_jadcedd.algorithm.proposed.activity import Config, EvidenceNetwork, SCHEMA
from afdm_jadcedd.experiment.training.scores.checkpoints import save_direct_checkpoint
from afdm_jadcedd.experiment.training.proposed.common import load_recipe, load_prior, load_data, source_hashes

DEFAULT_OUTPUT = ROOT / 'runs/proposed_sample_sizes_20261018'
STAGES = ('first', 'second', 'activity')
SELECTION_SEED = 202610180700001
INITIALIZATION_SEEDS = dict(first=202610180710001, second=202610180710002, activity=202610180710003)


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT))


def selected_rows(identities, count, seed):
    """Select complete physical scenes, independent of values or performance."""
    scenes, counts = np.unique(identities[:, 0], return_counts=True)
    if not np.all(counts == 4) or count % 4 or count > len(identities):
        raise ValueError('Complete groups of four candidate channels required')
    chosen = np.random.default_rng(seed).choice(scenes, count // 4, replace=False)
    return np.flatnonzero(np.isin(identities[:, 0], chosen))


def make_initialization(directory, scale):
    directory.mkdir(parents=True, exist_ok=True)
    score_config = DirectCaiConfig(antennas=16, side=16, base_channels=128,
                                  snr_db_min=-20, snr_db_max=30, noise_conditioning='continuous')
    result = {}
    for stage in STAGES:
        seed = INITIALIZATION_SEEDS[stage]
        torch.manual_seed(seed)
        metadata = dict(initialization='random', random_seed=seed, optimizer_steps=0,
                        training_samples_seen=0, pretrained_checkpoint_loaded=False)
        path = directory / (stage + '.pt')
        if stage == 'activity':
            model = EvidenceNetwork(Config())
            torch.save(dict(schema=SCHEMA, config=asdict(model.config),
                            state_dict={k:v.detach().cpu() for k,v in model.state_dict().items()},
                            metadata=metadata), path)
        else:
            model = DirectCaiNetwork(score_config, order=1 if stage == 'first' else 2)
            save_direct_checkpoint(path, model, scale=scale, metadata=metadata)
        result[stage] = dict(path=relative(path), sha256=sha(path), **metadata)
        del model
    return result


def bank_prior(directory, original, train_rows, validation_rows, scale):
    directory.mkdir(parents=True, exist_ok=True)
    prior = deepcopy(original)
    records, paths, digests = {}, {}, {}
    for split, rows in (('train', train_rows), ('validation', validation_rows)):
        source = ROOT / 'data/proposed' / (split + '_channel.npy')
        source_ids = ROOT / 'data/proposed' / (split + '_identities.npy')
        channels = np.load(source, mmap_mode='r', allow_pickle=False)
        identities = np.load(source_ids, allow_pickle=False)
        # Reuse the complete existing banks; materialize only smaller subsets.
        complete = len(rows) == len(channels) and np.array_equal(rows, np.arange(len(channels)))
        path, ids_path = source, source_ids
        if not complete:
            path, ids_path = directory / (split + '_channel.npy'), directory / (split + '_identities.npy')
            target = np.lib.format.open_memmap(path, mode='w+', dtype=np.complex64,
                                               shape=(len(rows), *channels.shape[1:]))
            for start in range(0, len(rows), 256):
                target[start:start+256] = channels[rows[start:start+256]]
            target.flush()
            del target
            np.save(ids_path, identities[rows], allow_pickle=False)
        selected = np.load(path, mmap_mode='r', allow_pickle=False)
        selected_ids = identities[rows]
        moments_path = ROOT / 'data/proposed' / (split + '_moments.npz')
        if not complete:
            total = np.zeros(channels.shape[1:], dtype=np.complex128)
            energy = 0.
            for start in range(0, len(selected), 128):
                values = selected[start:start+128].astype(np.complex128) / scale
                total += values.sum(axis=0)
                energy += float(np.sum(abs(values)**2))
            moments_path = directory / (split + '_moments.npz')
            np.savez(moments_path, prior_mean=np.zeros_like(total), empirical_mean=total/len(selected),
                     prior_second_moment=np.asarray(energy/len(selected)))
        with np.load(moments_path, allow_pickle=False) as moments:
            power = float(moments['prior_second_moment'])
        scene_seeds = np.unique(selected_ids[:, 0]).tolist()
        records[split] = dict(count=len(selected), scenes=len(scene_seeds), scene_seeds=scene_seeds,
                              candidates_per_scene=4, identities_path=relative(ids_path),
                              identities_sha256=sha(ids_path), path=relative(path), sha256=sha(path),
                              moments_file=relative(moments_path), moments_sha256=sha(moments_path),
                              prior_second_moment=power, normalized_mean_element_power=power/4096.)
        paths[split], digests[split] = relative(path), records[split]['sha256']
    prior.update(train_samples=len(train_rows), validation_samples=len(validation_rows),
                 data_files=paths, sample_files_sha256=digests, dataset_identities=records,
                 moments_file=records['train']['moments_file'], moments_sha256=records['train']['moments_sha256'],
                 prior_second_moment=records['train']['prior_second_moment'],
                 normalized_mean_element_power=records['train']['normalized_mean_element_power'],
                 prior_moment_samples=len(train_rows), training_configuration=None,
                 training_configuration_sha256=None,
                 initialization_exposure=dict(pretraining_samples=0, kind='random'),
                 coordinate_scale_policy='Fixed physical coordinate convention shared by both arms; no new scale fitting')
    save(directory / 'prior_definition.json', prior)
    np.save(directory / 'train_rows.npy', train_rows, allow_pickle=False)
    return prior


def prepare(output, smoke=False):
    if (output / 'PLAN.json').exists():
        return verify(output)
    if output.exists() and any(output.iterdir()):
        raise FileExistsError('Preparation requires an empty directory')
    output.mkdir(parents=True, exist_ok=True)
    recipe = load_recipe()
    original = load_prior(recipe)
    load_data(recipe, original)  # Verify original files before taking a subset.
    train_ids = np.load(ROOT / 'data/proposed/train_identities.npy', allow_pickle=False)
    val_ids = np.load(ROOT / 'data/proposed/validation_identities.npy', allow_pickle=False)
    assert not np.intersect1d(train_ids[:, 0], val_ids[:, 0]).size
    sizes = (16, 32) if smoke else (5000, 50000)
    full_rows = np.arange(sizes[1])
    small_rows = full_rows[selected_rows(train_ids[full_rows], sizes[0], SELECTION_SEED)]
    validation_rows = np.arange(16 if smoke else len(val_ids))
    initial = make_initialization(output / 'initialization', recipe['scale'])
    test_ranges = {}
    for name in ('snr_comparison', 'pilot_frames', 'user_count', 'activity_probability',
                 'convergence', 'channel_denoising', 'cross_channel'):
        settings = importlib.import_module(name).EXPERIMENT
        seeds = np.arange(settings['seed'], settings['seed'] + settings['scenes'])
        assert not np.intersect1d(seeds, train_ids[:, 0]).size
        assert not np.intersect1d(seeds, val_ids[:, 0]).size
        test_ranges[name] = [int(seeds[0]), int(seeds[-1])]
    recipes = {}
    for count, rows in zip(sizes, (small_rows, full_rows), strict=True):
        directory = output / 'data' / f'n{count}'
        prior = bank_prior(directory, original, rows, validation_rows, recipe['scale'])
        config = deepcopy(recipe)
        config['prior_definition'] = relative(directory / 'prior_definition.json')
        config['prior_definition_sha256'] = sha(directory / 'prior_definition.json')
        config['data_files'] = prior['data_files']
        config['moments_file'] = prior['moments_file']
        config['bank'].update(train_samples=count, validation_samples=len(validation_rows),
                              selection='Fixed nested subset of complete physical scenes; no performance selection')
        config['paired_training'] = dict(protocol=relative(output / 'PLAN.json'), initialization='random',
             pretraining_samples=0, epoch_definition='One complete pass through this arm\'s distinct clean-channel bank',
             sample_selection_seed=SELECTION_SEED, smoke_only=smoke)
        for index, stage in enumerate(STAGES):
            settings = config[stage]
            settings.update(initial_checkpoint=initial[stage]['path'],
                            initial_checkpoint_sha256=initial[stage]['sha256'],
                            seed=202610180720001 + 2*index, validation_seed=202610180720002 + 2*index)
            settings.pop('continuation', None)
            settings.pop('continuation_schedule', None)
            settings['selection'] = 'Minimum fixed-noise validation objective; no test-based selection'
            if stage == 'first':
                settings.update(maximum_epochs=200, minimum_epochs=200, validation_patience=201,
                                stopping='Exactly 200 complete data epochs; no validation early stop')
            if smoke:
                settings.update(maximum_epochs=1, minimum_epochs=1, validation_patience=2,
                                batch_size=8, microbatch_size=4, checkpoint_seconds=10)
        config_path = output / 'configs' / f'n{count}.json'
        save(config_path, config)
        recipes[str(count)] = relative(config_path)
    frozen = read(ROOT / 'results/baseline_comparison_500_20261018/PLAN.json')
    mainline_hashes = frozen['source_sha256'] | frozen['weight_sha256']
    for name, digest in mainline_hashes.items():
        assert sha(ROOT/name) == digest, name
    inputs = {}
    for config_name in recipes.values():
        config = read(ROOT/config_name)
        prior = read(ROOT/config['prior_definition'])
        names = [config_name, config['prior_definition'], config['moments_file'], *config['data_files'].values()]
        names += [v['identities_path'] for v in prior['dataset_identities'].values()]
        inputs.update({name:sha(ROOT/name) for name in names})
    sources = source_hashes() | {relative(Path(__file__)): sha(Path(__file__))}
    for name in ('experiment/channel_denoising.py', 'experiment/_common.py',
                 'experiment/_support/settings.py', 'experiment/_support/storage.py'):
        sources[name] = sha(ROOT/name)
    plan = dict(schema='paired-training-sizes-v1', status='PREPARED', created_unix=time.time(),
                sizes=list(sizes), validation_samples=len(validation_rows), recipes=recipes,
                initialization=initial, input_sha256=inputs, source_sha256=sources,
                mainline_sha256=mainline_hashes, subset_indices=relative(output/'data'/f'n{sizes[0]}'/'train_rows.npy'),
                test_scene_ranges=test_ranges, device=recipe['runtime']['device'], smoke_only=smoke,
                first_epochs=1 if smoke else 200, epochs_mean_distinct_bank_passes=True,
                equal_optimizer_steps=False,
                first_optimizer_steps={str(n):(1 if smoke else 200)*math.ceil(n/(8 if smoke else 64)) for n in sizes},
                order=['first_small', 'first_full', 'first_only_denoising', 'second_small',
                       'second_full', 'activity_small', 'activity_full', 'bind_small', 'bind_full'],
                monitoring=dict(interval_seconds=30, stall_advisory_seconds=900, stage_timeout_hours=96),
                selection='Use validation-selected weights after the full first-stage budget; test results never choose weights or alter later training',
                comparison_scope='Random initialization, identical architecture and epoch schedule; update counts differ with bank size')
    save(output / 'PLAN.json', plan)
    return verify(output)


def verify(output):
    plan = read(output / 'PLAN.json')
    for mapping in (plan['input_sha256'], plan['source_sha256'], plan['mainline_sha256']):
        for name, digest in mapping.items():
            if sha(ROOT/name) != digest:
                raise ValueError('Prepared dependency changed: ' + name)
    for stage, item in plan['initialization'].items():
        path = ROOT/item['path']
        assert sha(path) == item['sha256']
        blob = torch.load(path, map_location='cpu', weights_only=False)
        assert blob['metadata']['training_samples_seen'] == 0
        torch.manual_seed(item['random_seed'])
        model = (EvidenceNetwork(Config(**blob['config'])) if stage == 'activity' else
                 DirectCaiNetwork(DirectCaiConfig(**blob['config']), order=blob['order']))
        for key, tensor in model.state_dict().items():
            if not torch.equal(tensor.cpu(), blob['state_dict'][key]):
                raise ValueError('Initialization is not reproducible from its random seed')
    report = dict(status='PASS', sizes=plan['sizes'], validation_samples=plan['validation_samples'],
                  nested_physical_scene_subset=True, train_validation_test_disjoint=True,
                  shared_random_initialization_reproduced=True, pretrained_weights_loaded=False,
                  first_epochs=plan['first_epochs'], first_optimizer_steps=plan['first_optimizer_steps'],
                  frozen_mainline_unchanged=True, smoke_only=plan['smoke_only'])
    save(output / 'PREPARATION_CHECK.json', report)
    print(json.dumps(report, ensure_ascii=False), flush=True)
    return plan


def first_configuration(output, count):
    config = read(ROOT/read(output/'PLAN.json')['recipes'][str(count)])
    folder = output / f'n{count}' / 'first'
    record = read(folder/'complete.json')
    plan = read(output/'PLAN.json')
    if record['epochs'] != plan['first_epochs'] or record['optimizer_steps'] != plan['first_optimizer_steps'][str(count)]:
        raise ValueError('First-stage budget is incomplete')
    checkpoint = folder/'first_best.pt'
    assert sha(checkpoint) == record['weight_sha256']
    blob = torch.load(checkpoint, map_location='cpu', weights_only=False)
    assert blob['metadata']['initialization_sha256'] == plan['initialization']['first']['sha256']
    destination = output/f'n{count}'/'first_receiver.json'
    save(destination, dict(schema='proposed-first-score-evaluation-v1',
                           first_checkpoint=relative(checkpoint), first_checkpoint_sha256=sha(checkpoint),
                           prior_definition=config['prior_definition'],
                           prior_definition_sha256=config['prior_definition_sha256'], scale=config['scale'],
                           completion_record=relative(folder/'complete.json'),
                           completion_record_sha256=sha(folder/'complete.json'),
                           initialization='random', pretraining_samples=0))
    return destination


def run(output):
    import fcntl
    lock = (output/'queue.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    plan = verify(output)
    sizes = plan['sizes']
    child = None
    stopping = False

    def stop(*_):
        nonlocal stopping
        stopping = True
        if child is not None and child.poll() is None:
            child.send_signal(signal.SIGTERM)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    python = str(ROOT/'.venv/bin/python')
    trainer = str(ROOT/'scripts/train_proposed.py')
    jobs = []
    for stage in ('first', 'denoising', 'second', 'activity', 'bind'):
        if stage == 'denoising':
            jobs.append((stage, None))
        else:
            jobs.extend((stage, n) for n in sizes)
    queue_started = time.time()
    completed_jobs = []
    for stage, count in jobs:
        if stopping or (output/'pause.request').exists():
            save(output/'STATUS.json', dict(status='PAUSED', completed_jobs=completed_jobs, pid=os.getpid()))
            return 2
        if stage == 'denoising':
            small, full = [first_configuration(output, n) for n in sizes]
            destination = output/'first_denoising'
            script = str(ROOT/'experiment/channel_denoising.py')
            common = ['--output', str(destination)]
            if not (destination/'PLAN.json').exists():
                command = [python, '-B', script, 'plan', *common, '--first-only',
                           '--full-config', str(full), '--small-config', str(small), '--device', plan['device']]
                if plan['smoke_only']:
                    command += ['--scenes', '1', '--candidates', '1', '--values', '0.1', '1']
                subprocess.run(command, cwd=ROOT, check=True)
            command = [python, '-B', script, 'run', *common]
            watched = destination
        else:
            watched = output/f'n{count}'/stage
            command = [python, '-B', trainer, '--config', str(ROOT/plan['recipes'][str(count)]),
                       '--stage', stage, '--output', str(output/f'n{count}'), '--teachers', 'run']
        job_name = stage if count is None else f'{stage}_{count}'
        log_path = output/'logs'/f'{job_name}.log'
        log_path.parent.mkdir(exist_ok=True)
        started = time.time()
        with log_path.open('ab') as log:
            child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            save(output/'CURRENT_JOB.json', dict(job=job_name, command=command, child_pid=child.pid,
                 supervisor_pid=os.getpid(), started_unix=started, log=relative(log_path)))
            while True:
                code = child.poll()
                now = time.time()
                stage_status = read(watched/'status.json') if (watched/'status.json').exists() else None
                updated = max(log_path.stat().st_mtime, (watched/'status.json').stat().st_mtime
                              if (watched/'status.json').exists() else started)
                row = dict(status='RUNNING', job=job_name, pid=os.getpid(), child_pid=child.pid,
                           elapsed_job_seconds=now-started, updated_unix=now, stage_status=stage_status,
                           completed_jobs=completed_jobs, log=relative(log_path),
                           output_stall_advisory=now-updated > plan['monitoring']['stall_advisory_seconds'])
                save(output/'STATUS.json', row)
                if code is not None:
                    break
                if now-started > plan['monitoring']['stage_timeout_hours']*3600:
                    stop()
                if (output/'pause.request').exists():
                    stop()
                time.sleep(1 if plan['smoke_only'] else plan['monitoring']['interval_seconds'])
        receipt = dict(job=job_name, exit_code=code, command=command, started_unix=started,
                       finished_unix=time.time(), log=relative(log_path))
        save(output/'receipts'/f'{job_name}.json', receipt)
        if code != 0 or stopping:
            save(output/'STATUS.json', dict(status='PAUSED' if stopping or code == 2 else 'FAILED',
                                           pid=os.getpid(), completed_jobs=completed_jobs, **receipt))
            return code or 2
        if stage == 'first':
            first_configuration(output, count)
        completed_jobs.append(job_name)
    result = dict(status='COMPLETED', completed_jobs=completed_jobs,
                  seconds=time.time()-queue_started, sizes=sizes, smoke_only=plan['smoke_only'],
                  receiver_configurations={str(n):relative(output/f'n{n}'/'receiver.json') for n in sizes})
    save(output/'STATUS.json', result)
    save(output/'COMPLETE.json', result)
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'verify', 'run', 'status'))
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--smoke', action='store_true', help='Separate tiny integration check, never performance evidence')
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT/'runs'):
        raise ValueError('Use an independent directory under runs/')
    if args.command == 'prepare':
        prepare(output, args.smoke)
    elif args.command == 'verify':
        verify(output)
    elif args.command == 'status':
        print(json.dumps(read(output/'STATUS.json'), ensure_ascii=False, indent=2))
    else:
        try:
            return run(output)
        except Exception as error:
            save(output/'STATUS.json', dict(status='FAILED', error=repr(error), updated_unix=time.time()))
            raise
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
