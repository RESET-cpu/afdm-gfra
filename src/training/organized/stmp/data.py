"""Build the full-geometry active-channel bank before activity masking."""
from pathlib import Path
import json
import math
import os
import shutil
import time
import warnings

from workspace import ROOT
import numpy as np
from threadpoolctl import threadpool_limits
from scenario.geometry_consistent import draw_scene
from scenario.continuous import user_channel
from fileio import sha256
from fileio import write_json


def source_hashes():
    paths = [Path(__file__).resolve()]
    for folder in ('scenario', 'waveform', 'channel'):
        paths.extend((ROOT / 'src' / folder).rglob('*.py'))
    return {str(p.relative_to(ROOT)): sha256(p) for p in sorted(set(paths))}


def candidate_indices(seed, users, count):
    rng = np.random.default_rng(np.random.SeedSequence([seed, 20261006, 81]))
    return rng.choice(users, size=count, replace=False)


def build_split(configuration, split, destination):
    settings = configuration['bank']
    count = settings[split + '_samples']
    base = settings[split + '_seed_base']
    shape = (count, *configuration['shape'])
    data_path = destination / f'{split}_channel.npy'
    ids_path = destination / f'{split}_identities.npy'
    record_path = destination / f'{split}_complete.json'
    if record_path.exists():
        record = json.loads(record_path.read_text())
        if (record['configuration_sha256'] != configuration['_sha256']
                or record['source_sha256'] != source_hashes()
                or sha256(data_path) != record['sha256']
                or sha256(ids_path) != record['identities_sha256']):
            raise ValueError('Completed bank identity changed; existing files preserved')
        return record
    if data_path.exists() or ids_path.exists():
        raise FileExistsError('Incomplete bank exists; inspect it before rebuilding')
    required = int(np.prod(shape)) * 8 + count * 2 * 8
    if shutil.disk_usage(destination).free < required + settings['minimum_free_bytes']:
        raise RuntimeError('Insufficient space for bank and declared reserve')
    data = np.lib.format.open_memmap(data_path, mode='w+', dtype=np.complex64, shape=shape)
    identities = np.lib.format.open_memmap(ids_path, mode='w+', dtype=np.int64, shape=(count, 2))
    total = 0
    energy_sum = energy_square_sum = 0.0
    mean_sum = np.zeros(configuration['shape'], dtype=np.complex128)
    negative_z = 0
    start = time.time()
    groups = math.ceil(count / settings['candidates_per_scene'])
    for scene_index in range(groups):
        seed = base + scene_index
        scene, geometry = draw_scene(seed, n_users=settings['users'],
                                    spread_range_s=tuple(settings['spread_range_s']))
        # Candidate H exists for every user independently of the activity draw.
        # Selecting a uniform candidate before masking samples the active-channel
        # marginal without selecting a favorable scene or high-energy user.
        for user in candidate_indices(seed, settings['users'], settings['candidates_per_scene']):
            if total == count:
                break
            channel = user_channel(scene.paths_of(int(user)))
            if not np.isfinite(channel).all():
                raise FloatingPointError(f'Nonfinite physical H at {seed}/{user}')
            stored = channel.astype(np.complex64)
            data[total] = stored
            identities[total] = (seed, user)
            normalized = stored.astype(np.complex128) / configuration['scale']
            energy = float(np.vdot(normalized, normalized).real)
            energy_sum += energy
            energy_square_sum += energy * energy
            mean_sum += normalized
            negative_z += int(geometry.direction_cosines[user, 0] < 0)
            total += 1
        if scene_index % 100 == 0 or total == count:
            data.flush()
            identities.flush()
            row = dict(status='GENERATING', split=split, pid=os.getpid(), samples=total,
                       expected=count, elapsed_seconds=time.time()-start, updated_unix=time.time())
            write_json(destination / 'status.json', row)
            print(json.dumps(row), flush=True)
    data.flush()
    identities.flush()
    empirical_mean = mean_sum / count
    # Independent uniform gain phases give exact E[H]=0, also for Rician tap 1.
    # The finite-bank empirical mean is retained as a diagnostic.
    moment_path = destination / f'{split}_moments.npz'
    second = energy_sum / count
    np.savez(moment_path, prior_mean=np.zeros_like(empirical_mean),
             empirical_mean=empirical_mean, prior_second_moment=np.array(second))
    sample_variance = max(0., (energy_square_sum-count*second*second)/max(count-1, 1))
    record = dict(status='COMPLETE', configuration_sha256=configuration['_sha256'],
                  source_sha256=source_hashes(), path=str(data_path), shape=list(shape),
                  dtype='complex64', sha256=sha256(data_path), count=count,
                  identities_path=str(ids_path), identities_sha256=sha256(ids_path),
                  seed_base=base, scenes=groups, candidates_per_scene=settings['candidates_per_scene'],
                  moments_file=str(moment_path), moments_sha256=sha256(moment_path),
                  prior_second_moment=second, normalized_mean_element_power=second/int(np.prod(shape[1:])),
                  sample_energy_standard_error=math.sqrt(sample_variance/count),
                  standard_error_scope='Individual-sample descriptive value; shared-scene dependence is present',
                  negative_mu_z_samples=negative_z, mean_is_analytically_zero=True,
                  elapsed_seconds=time.time()-start)
    write_json(record_path, record)
    return record


def build_bank(configuration, destination, configuration_path):
    cfg = dict(configuration, _sha256=sha256(configuration_path))
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    with warnings.catch_warnings(record=True) as caught, threadpool_limits(limits=cfg['runtime']['threads']):
        records = {split: build_split(cfg, split, destination) for split in ('train', 'validation')}
    if (records['train']['seed_base'] + records['train']['scenes']
            > records['validation']['seed_base']):
        raise ValueError('Training and validation scene ranges overlap')
    prior = dict(schema='physical-training-prior-v1', generator=cfg['generator'],
                 bank_storage='physical_complex_npy', shape=cfg['shape'],
                 target_distribution='Unfiltered full geometry candidate marginal, before independent activity masking',
                 global_complex_rms=cfg['scale'], coordinate_scale_equals_new_population_rms=False,
                 train_samples=records['train']['count'], validation_samples=records['validation']['count'],
                 data_files={key: row['path'] for key, row in records.items()},
                 sample_files_sha256={key: row['sha256'] for key, row in records.items()},
                 dataset_identities=records,
                 moments_file=records['train']['moments_file'], moments_sha256=records['train']['moments_sha256'],
                 prior_second_moment=records['train']['prior_second_moment'],
                 normalized_mean_element_power=records['train']['normalized_mean_element_power'],
                 prior_mean_exact=True, prior_mean_definition='Zero by independent uniform complex gain phases',
                 prior_moments_exact=False, prior_moment_samples=records['train']['count'],
                 noise_support=cfg['noise_support'], training_configuration=str(configuration_path.resolve()),
                 training_configuration_sha256=cfg['_sha256'],
                 working_prior_conditions_on_receiver_geometry=False,
                 receiver_information_scope='Known phase operator and supplied received-power noise variance; same for all methods',
                 warning_count=len(caught), warning_examples=list(dict.fromkeys(str(w.message) for w in caught))[:5])
    write_json(destination/'prior_definition.json', prior)
    write_json(destination/'status.json', dict(status='COMPLETE', pid=os.getpid(), updated_unix=time.time(),
                                              prior_definition=str(ROOT/cfg['prior_definition'])))
    print(json.dumps(dict(status='COMPLETE', prior_definition=str(destination/'prior_definition.json')), ensure_ascii=False), flush=True)
    return prior

