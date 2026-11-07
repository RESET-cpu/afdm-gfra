"""Replay all 500 historical AWGN scenes with the adopted white denoiser."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import time
import traceback

import numpy as np
from threadpoolctl import threadpool_limits
from scenario.channel_samples import clean_channels
from experiment.metrics import denoising_metrics
from channel.observation import array_sha256
from fileio import read_json, write_json, sha256
from experiment.studies.provenance import execution_identity
from .common import ROOT, OUT, CONFIG, ARCHIVE, checked, publish, setup, acquire, verify_plan

DEST = ROOT / 'result/channel_denoising/data/white_mainline_500_20261107'
RECORDS = ROOT / 'result/channel_denoising/data/imports/denoising_mac_20261023_4173ccc/source/results/denoising_merged_20261018/records'
OLD = ROOT / 'result/channel_denoising/data/colored_first_500_20261025_v2'
PLOT = ROOT / 'result/channel_denoising/figures/narrow_paper_20261026/PLOT_DATA.json'
VALUES = [.001, .01, .1, 1., 10., 100.]
SEED = 202610180500001


def paired_inputs(scene, scale):
    seed = SEED + scene
    physical, users = clean_channels(seed, 40, 4)
    truth = physical / scale
    rng = np.random.default_rng(np.random.SeedSequence([seed, 8240]))
    epsilon = (rng.normal(size=truth.shape) + 1j*rng.normal(size=truth.shape))/np.sqrt(2)
    queries, identities = [], []
    for index, variance in enumerate(VALUES):
        query = truth + np.sqrt(variance)*epsilon
        expected = read_json(RECORDS/f'scene{scene:03d}/condition{index:02d}/INPUT_cloud.json')
        actual = dict(seed=seed, users=users.tolist(), variance=variance, scale=scale,
                      truth_sha256=array_sha256(truth), query_sha256=array_sha256(query),
                      standard_noise_sha256=array_sha256(epsilon))
        if any(expected[k] != value for k, value in actual.items()):
            raise ValueError(f'Historical input mismatch: scene {scene}, condition {index}')
        queries.append(query)
        identities.append(actual)
    return truth, np.concatenate(queries), identities


def prepare():
    if (DEST/'PLAN.json').exists():
        return verify_plan(DEST)
    DEST.mkdir(parents=True, exist_ok=True)
    c = read_json(CONFIG)
    files = set((ROOT/'src/receiver/gp_mp').glob('*.py'))
    files.update(ROOT/'src/experiment/studies/white_followup'/name
                 for name in ('__init__.py','common.py','denoising.py'))
    files.update([CONFIG, PLOT, OLD/'PLAN.json', OLD/'VERIFICATION.json',
                  ROOT/'src/scenario/channel_samples.py', ROOT/'src/experiment/metrics.py',
                  OUT/'REQUEST.json', ARCHIVE/'VALIDATION.json'])
    files.update(ROOT/c[k] for k in c if k+'_sha256' in c)
    for scene in range(500):
        for i in range(6):
            files.add(RECORDS/f'scene{scene:03d}/condition{i:02d}/INPUT_cloud.json')
    plan = dict(schema='white-paper-denoising-v1', scenes=500, inputs=3000,
        candidates_per_scene=4, variances=VALUES, base_seed=SEED, scale=c['scale'],
        configuration=str(CONFIG), batch_size=4, device='cuda', threads=2,
        fp32=True, tf32=False, cudnn_tf32=False, benchmark=False,
        prediction_saved_for_every_scene=True, previous_plot=str(PLOT),
        original_data_unchanged=True, timeout_seconds=7200,
        assets={str(p.relative_to(ROOT)):sha256(p) for p in sorted(files)},
        limitations=['Retrospective fixed historical scenes, not an untouched test set.',
            'Historical other-platform baselines share scene/noise identities; their array hashes can differ.',
            'This evaluates the conditional mean on AWGN; it is not a receiver or classifier test.'])
    write_json(DEST/'PLAN.json', plan)
    write_json(DEST/'PLAN_HASH.json', {'sha256':sha256(DEST/'PLAN.json')})
    return plan


def score_saved(path, plan, scene):
    receipt = read_json(path.with_suffix('.json'))
    checked(path, receipt['prediction_sha256'])
    truth, _, identities = paired_inputs(scene, plan['scale'])
    if identities != receipt['inputs']:
        raise ValueError('Saved input identity mismatch')
    with np.load(path, allow_pickle=False) as z:
        estimate = z['estimate']
    assert estimate.shape == (24,16,16,16) and np.isfinite(estimate).all()
    scored = denoising_metrics(estimate, np.tile(truth,(6,1,1,1)))
    for key in ('error','energy'):
        np.testing.assert_allclose(scored[key].reshape(6,4),receipt[key],rtol=1e-12,atol=1e-12)
    return scored


def summarize(plan):
    errors, energies, hashes = [], [], {}
    for scene in range(500):
        path = DEST/'scenes'/f'scene{scene:03d}.npz'
        scored = score_saved(path,plan,scene)
        errors.append(scored['error'].reshape(6,4));energies.append(scored['energy'].reshape(6,4))
        hashes[str(path)] = sha256(path)
        hashes[str(path.with_suffix('.json'))] = sha256(path.with_suffix('.json'))
    assert len(list((DEST/'scenes').glob('scene*.json')))==500
    error,energy=np.stack(errors),np.stack(energies)
    rows=[]
    for i,v in enumerate(VALUES):
        e,p=float(error[:,i].sum()),float(energy[:,i].sum())
        rows.append(dict(method='pretrained_white_first',variance=v,snr_db=float(-10*np.log10(v)),
                         scenes=500,samples=2000,error=e,energy=p,nmse_db=float(10*np.log10(e/p)),
                         parameters=dict(variance=v,snr_db=float(-10*np.log10(v))),condition=i))
    verify_plan(DEST)
    write_json(DEST/'OUTPUT_HASHES.json',hashes)
    write_json(DEST/'SUMMARY.json',dict(status='VERIFIED',experiment='channel_denoising',rows=rows,
        inputs=3000,channel_queries=12000,scenes=500,plan_sha256=sha256(DEST/'PLAN.json'),
        saved_predictions_rescored=True,all_input_array_hashes_match=True,limitations=plan['limitations']))
    write_json(DEST/'COMPLETION.json',dict(status='PASS',completed_unix=time.time(),inputs=3000,
        summary_sha256=sha256(DEST/'SUMMARY.json'),output_hashes_sha256=sha256(DEST/'OUTPUT_HASHES.json'),
        predictions_rescored=True,all_source_hashes_verified=True,coordinator_exit_requires_followup=True))


def run():
    plan=verify_plan(DEST)
    execution=execution_identity()
    lock,token=acquire(DEST)
    began=time.time(); completed=0
    write_json(DEST/'START.json',dict(**token,started_unix=began,execution=execution,plan_sha256=sha256(DEST/'PLAN.json')))
    try:
        setup()
        from receiver.gp_mp.denoising import Denoiser
        import torch
        c=read_json(CONFIG)
        model=Denoiser(CONFIG,device='cuda',batch_size=4)
        # Model construction verifies the adopted white checkpoint.
        write_json(DEST/'PREFLIGHT.json',dict(status='PASS',white_model_verified=True,
            execution=execution,
            checkpoint_sha256=c['first_checkpoint_sha256']))
        with threadpool_limits(2):
            for scene in range(500):
                if (DEST/'STOP.json').exists():
                    publish(DEST/'STATUS.json',dict(stage='PAUSED',completed=completed,planned=500,**token));return
                if time.time()-began>plan['timeout_seconds']:
                    raise TimeoutError('Bounded denoising run exceeded two hours')
                path=DEST/'scenes'/f'scene{scene:03d}.npz'
                if path.exists() or path.with_suffix('.json').exists():
                    score_saved(path,plan,scene)
                else:
                    truth,query,identities=paired_inputs(scene,plan['scale'])
                    mean,record=model.infer(query,np.repeat(VALUES,4),priors=None)
                    assert mean.shape==query.shape and np.isfinite(mean).all()
                    path.parent.mkdir(parents=True,exist_ok=True)
                    # Save predictions before scoring, retain every scene.
                    with path.open('xb') as stream:
                        np.savez_compressed(stream,estimate=mean)
                    metrics=denoising_metrics(mean,np.tile(truth,(6,1,1,1)))
                    write_json(path.with_suffix('.json'),dict(status='COMPLETE',scene=scene,inputs=identities,
                        prediction_sha256=sha256(path),record=record,
                        error=metrics['error'].reshape(6,4).tolist(),energy=metrics['energy'].reshape(6,4).tolist()))
                completed=scene+1
                publish(DEST/'STATUS.json',dict(stage='RUNNING',completed=completed,planned=500,
                    completed_inputs=completed*6,planned_inputs=3000,updated_unix=time.time(),**token))
        publish(DEST/'STATUS.json',dict(stage='VERIFYING',completed=completed,planned=500,**token))
        summarize(plan)
        publish(DEST/'STATUS.json',dict(stage='COMPLETE',completed=500,planned=500,updated_unix=time.time(),**token))
    except Exception:
        write_json(DEST/'FAILURE.json',dict(status='FAILED',traceback=traceback.format_exc(),
            completed_scenes=completed,automatic_retry=False,**token))
        raise
    finally:
        lock.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['prepare','run','inspect'])
    command=parser.parse_args().command
    if command=='prepare':print(json.dumps(prepare()))
    elif command=='run':run()
    else: print(json.dumps({'plan_valid':bool(verify_plan(DEST)), 'status':read_json(DEST/'STATUS.json') if (DEST/'STATUS.json').exists() else 'PREPARED'}))
