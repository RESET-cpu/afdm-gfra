"""Append one first-network curve to the frozen historical 500-scene AWGN panel."""
import argparse
from copy import deepcopy
from pathlib import Path
import csv
import json
import os
import sys
import time
import traceback

import numpy as np
from threadpoolctl import threadpool_limits

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from algorithm import registry
from evaluation.denoising import clean_channels, denoising_metrics
from evaluation.receivers import setup
from project import ROOT, source_files
from system.observation import array_sha256
from utils import read_json, write_json, sha256

IMPORT = ROOT/'result/channel_denoising/data/imports/denoising_mac_20261023_4173ccc'
SOURCE = IMPORT/'source/results/denoising_four_baselines_20261018'
RECORDS = IMPORT/'source/results/denoising_merged_20261018/records'
METHOD = 'pretrained_colored_first'
VALUES = [.001, .01, .1, 1., 10., 100.]
SEED = 202610180500001


def publish_progress(path, value):
    """Windows readers can briefly deny an atomic STATUS replacement."""
    for attempt in range(10):
        try:
            write_json(path, value)
            return
        except PermissionError:
            if attempt == 9:
                raise
            time.sleep(.1)


def paired_inputs(scene, scale):
    """Regenerate only when every array hash matches the old cloud first-network input."""
    seed = SEED+scene
    physical, users = clean_channels(seed, 40, 4)
    truth = physical/scale
    rng = np.random.default_rng(np.random.SeedSequence([seed, 8240]))
    epsilon = (rng.normal(size=truth.shape)+1j*rng.normal(size=truth.shape))/np.sqrt(2)
    queries, identities = [], []
    for i, variance in enumerate(VALUES):
        query = truth+np.sqrt(variance)*epsilon
        expected = read_json(RECORDS/f'scene{scene:03d}/condition{i:02d}/INPUT_cloud.json')
        actual = dict(seed=seed, users=users.tolist(), variance=variance, scale=scale,
                      truth_sha256=array_sha256(truth), query_sha256=array_sha256(query),
                      standard_noise_sha256=array_sha256(epsilon))
        if any(expected[k] != v for k, v in actual.items()):
            raise ValueError(f'Historical input identity differs: scene {scene}, condition {i}')
        queries.append(query)
        identities.append(actual)
    return truth, epsilon, np.concatenate(queries), identities


def historical_errors(scene, energy):
    errors = []
    for i in range(len(VALUES)):
        path = RECORDS/f'scene{scene:03d}/condition{i:02d}/proposed.json'
        row = read_json(path)
        if row['status'] != 'COMPLETE' or sha256(path.with_suffix('.npz')) != row['compact_sha256']:
            raise ValueError('Historical first-network record changed')
        with np.load(path.with_suffix('.npz'), allow_pickle=False) as compact:
            np.testing.assert_allclose(compact['energy'], energy, rtol=1e-12, atol=1e-12)
            np.testing.assert_allclose(compact['error'].sum(), row['error'], rtol=1e-12)
            errors.append(compact['error'])
    return np.stack(errors)


def run(out, device, scenes):
    if out.exists():
        raise FileExistsError('Use a new output directory')
    out.mkdir(parents=True)
    start = time.monotonic()
    # Reuse the historical plot loader's source/Git audit before copying any curve.
    sys.path.insert(0, str(ROOT/'src/evaluation/plots'))
    from channel_denoising import load_denoising
    load_denoising(SOURCE, 'channel_denoising')
    old_plan, old_summary = read_json(SOURCE/'PLAN.json'), read_json(SOURCE/'SUMMARY.json')
    definitions = {METHOD: deepcopy(registry.load_catalog()[METHOD])}
    definitions[METHOD]['kwargs']['batch_size'] = 4
    binding = {'STMP': {'scale': old_plan['scale']}}
    files = set(source_files())
    files.update(registry.source_files(definitions[METHOD], binding, device))
    files.update([SOURCE/'PLAN.json', SOURCE/'SUMMARY.json', IMPORT/'AUDIT.json', IMPORT/'REMOTE.json',
                  ROOT/'FINAL.json', ROOT/'MAINLINE.json', ROOT/'src/configs/final/models.json',
                  ROOT/'src/configs/final/STMP.json', ROOT/'src/configs/candidates/C_STMP_20261024.json'])
    for scene in range(scenes):
        for i in range(6):
            folder = RECORDS/f'scene{scene:03d}/condition{i:02d}'
            files.update(folder/name for name in ('INPUT_cloud.json', 'proposed.json', 'proposed.npz'))
    assets = {str(p.relative_to(ROOT)): sha256(p) for p in sorted(files)}
    plan = dict(schema='direct-awgn-colored-append-v1', experiment='channel_denoising',
                scene_count=scenes, candidates=4, base_seed=SEED, variances=VALUES,
                scale=old_plan['scale'], device=device, batch_size=4, tf32=False,
                source_summary=str(SOURCE/'SUMMARY.json'), source_summary_sha256=sha256(SOURCE/'SUMMARY.json'),
                algorithm_specs=definitions, assets=assets,
                pairing='Bitwise equality of all truth, query and standard-noise hashes to historical cloud first-network inputs.',
                legacy_pairing=old_plan['cloud_pairing'],
                mode='FORMAL_HISTORICAL_500' if scenes == 500 else 'PREFLIGHT_ONLY',
                authorized_request='请你追加一下这条曲线',
                hard_timeout_seconds=1800)
    write_json(out/'PLAN.json', plan)
    # Preserve the exact executable sources without altering old source snapshots.
    for path in source_files():
        target = out/'source'/path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    try:
        setup(device)
        model = registry.build_algorithm(METHOD, binding=binding, device=device, definitions=definitions)
        with threadpool_limits(4):
            for scene in range(scenes):
                if time.monotonic()-start > plan['hard_timeout_seconds']:
                    raise TimeoutError('Thirty-minute execution limit reached')
                truth, epsilon, queries, identities = paired_inputs(scene, old_plan['scale'])
                variance = np.repeat(VALUES, 4)
                mean, _ = model.infer(queries, variance, priors=None)
                metrics = denoising_metrics(mean, np.tile(truth, (6, 1, 1, 1)))
                error, energy = metrics['error'].reshape(6, 4), metrics['energy'].reshape(6, 4)
                old_error = historical_errors(scene, energy[0])
                path = out/'scenes'/f'scene{scene:03d}.npz'
                path.parent.mkdir(parents=True, exist_ok=True)
                np.savez_compressed(path, error=error, energy=energy, old_error=old_error)
                write_json(path.with_suffix('.json'), dict(scene=scene, inputs=identities,
                           compact_sha256=sha256(path), status='COMPLETE'))
                if scene == 0:
                    np.savez_compressed(out/'scene000_predictions.npz', truth=truth,
                                        standard_noise=epsilon, query=queries.reshape(6, 4, 16, 16, 16),
                                        estimate=mean.reshape(6, 4, 16, 16, 16))
                status = dict(status='RUNNING', pid=os.getpid(), completed_scenes=scene+1,
                              total_scenes=scenes, elapsed_seconds=time.monotonic()-start)
                publish_progress(out/'STATUS.json', status)
                if (scene+1) % 25 == 0 or scene+1 == scenes:
                    print(json.dumps(status), flush=True)
        for name, expected in assets.items():
            if sha256(ROOT/name) != expected:
                raise ValueError('Bound source/weight/result changed: '+name)
        summarize(out, plan, old_summary)
        publish_progress(out/'STATUS.json', dict(status='COMPLETE', completed_scenes=scenes,
                   total_scenes=scenes, elapsed_seconds=time.monotonic()-start))
    except BaseException:
        write_json(out/'FAILURE.json', dict(traceback=traceback.format_exc(), elapsed_seconds=time.monotonic()-start))
        raise


def summarize(out, plan, original):
    error, energy, old_error = [], [], []
    for scene in range(plan['scene_count']):
        path = out/'scenes'/f'scene{scene:03d}.npz'
        receipt = read_json(path.with_suffix('.json'))
        if sha256(path) != receipt['compact_sha256']:
            raise ValueError('Appended compact result changed')
        with np.load(path, allow_pickle=False) as arrays:
            error.append(arrays['error']); energy.append(arrays['energy']); old_error.append(arrays['old_error'])
    error, energy, old_error = np.stack(error), np.stack(energy), np.stack(old_error)
    new_rows = []
    for i, variance in enumerate(VALUES):
        e, power = float(error[:, i].sum()), float(energy[:, i].sum())
        new_rows.append(dict(method=METHOD, variance=variance, snr_db=float(-10*np.log10(variance)),
                             scenes=plan['scene_count'], samples=4*plan['scene_count'],
                             error=e, energy=power, nmse_db=float(10*np.log10(e/power))))
    differences = []
    for i, row in enumerate(new_rows):
        delta = float(10*np.log10(error[:, i].sum()/old_error[:, i].sum()))
        differences.append(dict(snr_db=row['snr_db'], delta_nmse_db=delta,
                                definition='New minus original 50k first network; negative means lower NMSE.'))
    formal = plan['scene_count'] == 500
    if formal:
        for i, variance in enumerate(VALUES):
            old = next(r for r in original['rows'] if r['method']=='proposed' and r['variance']==variance)
            np.testing.assert_allclose([old_error[:, i].sum(), energy[:, i].sum()],
                                       [old['error'], old['energy']], rtol=1e-12)
    summary = dict(status='COMPLETE' if formal else 'PREFLIGHT_ONLY',
                   experiment='channel_denoising', rows=deepcopy(original['rows'])+new_rows if formal else new_rows,
                   differences_from_old_50k=differences, source_plan_sha256=sha256(out/'PLAN.json'))
    write_json(out/'SUMMARY.json', summary)
    with (out/'NEW_CURVE.csv').open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(new_rows[0])); writer.writeheader(); writer.writerows(new_rows)
    write_json(out/'VERIFICATION.json', dict(status='PASS', physical_scenes=plan['scene_count'],
               paired_input_conditions=plan['scene_count']*6, hashes_matched_per_condition=3,
               pairing=plan['pairing'], original_54_rows_unchanged=formal,
               new_summary_sha256=sha256(out/'SUMMARY.json'), original_summary_sha256=sha256(SOURCE/'SUMMARY.json'),
               checkpoint_sha256=plan['algorithm_specs'][METHOD]['kwargs']['checkpoint_sha256'],
               all_source_and_checkpoint_hashes_unchanged=True, finite_outputs=True,
               material_passport=dict(origin_skill='academic-research-suite / experiment-agent',
                   origin_mode='run', origin_date='2026-10-25', verification_status='ANALYZED',
                   version_label='colored_first_append_500_v1'),
               limitations=[plan['legacy_pairing'], 'AWGN evaluation at C=vI; not a colored-noise evaluation.',
                            'Point estimates only; no statistical significance claim.']))
    print(json.dumps(dict(status=summary['status'], scenes=plan['scene_count'], new_points=6)), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--device', choices=['cpu', 'cuda'], default='cuda')
    parser.add_argument('--scenes', type=int, choices=[1, 500], default=500)
    args = parser.parse_args()
    run(args.output.resolve(), args.device, args.scenes)
