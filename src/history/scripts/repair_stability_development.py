"""Independent development/acceptance bank; never modifies frozen experiments."""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
from copy import deepcopy
from pathlib import Path
import time
import traceback
import numpy as np
import torch
from threadpoolctl import threadpool_limits
import evaluate_saved_baseline_inputs as paired
from benchmark_receiver_execution import GraphForward
from _common import observation, estimated_phase, phase
from _support.settings import solver

ROOT = paired.ROOT
OUT = ROOT/'runs/stability_repair_20261019'
SEEDS = {'development': 202610191000001, 'acceptance': 202610192000001}


def prepare():
    if (OUT/'PROTOCOL.json').exists():
        return
    config = paired.read(paired.MODEL)
    prior = paired.read(ROOT/config['prior_definition'])
    training = set()
    def seeds(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == 'scene_seeds':
                    training.update(item)
                else:
                    seeds(item)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, (dict, list)):
                    seeds(item)
    seeds(prior)
    formal = set()
    for start in [202610172000001, 202610180100001, 202610180200001,
                  202610180300001, 202610180400001, 202610180500001, 202610180600001]:
        formal.update(range(start, start+500))
    development = set(range(SEEDS['development'], SEEDS['development']+4))
    acceptance = set(range(SEEDS['acceptance'], SEEDS['acceptance']+12))
    assert not development & acceptance and not (development | acceptance) & (training | formal)
    preservation = paired.identities()
    for path in [paired.MODEL, ROOT/config['prior_definition']] + [ROOT/config[k] for k in
                 ('first_checkpoint', 'second_checkpoint', 'evidence_checkpoint')]:
        preservation[str(path.resolve())] = paired.sha(path)
    for path in (ROOT/'results/new_models_paired_20261019_cuda_graph').rglob('*'):
        if path.is_file() and path.suffix in ('.json', '.npz'):
            preservation[str(path.resolve())] = paired.sha(path)
    paired.save(OUT/'PRESERVATION.json', preservation)
    paired.save(OUT/'PROTOCOL.json', dict(created_unix=time.time(), seed_bases=SEEDS,
        development_scenes=4, acceptance_scenes=12, users=[20,40,60,80,100],
        parameters=dict(snr_db=0., frames=16, activity_probability=.1),
        training_validation_unique_seeds=len(training), formal_reserved_seeds=len(formal),
        seed_overlap=False, weights_changed=False, official_inputs_used_for_tuning=False,
        screening='One development scene at K=20,60,100; retain all attempts. Expand promising candidates to all 20 development cases.',
        candidate_selection='Use only development cases. Freeze one configuration and code hashes before opening the 60 acceptance cases. Acceptance cannot be reused for tuning.',
        candidate_family='First examine unchanged receiver with damping 0.2 (reference), 0.1, 0.05, 0.02; other candidates require a documented amendment before their runs.',
        acceptance_gates=dict(all_outputs_finite=True, all_cases_original_convergence_criteria=True,
            all_final_queries_inside_training_support=True, each_condition_pooled_nmse_db_below=0.,
            worst_case_nmse_db_at_most=3., per_condition_nmse_db_vs_sbl_at_most=1.,
            per_condition_aer_vs_sbl_at_most=.02),
        scope='Only user-count resumption at original settings; other experiment families require separate validation.',
        truth_policy='Truth only used by separate scoring observer, never receiver initialization, parameter updates or stopping.',
        sources={'damping':'Cai arXiv:2506.00581v2, V-B1, equations (57)-(58) and Algorithm 2'},
        preserved_sha256_file='PRESERVATION.json'))
    for damping in (.2,.1,.05,.02):
        candidate = deepcopy(config)
        candidate['ep']['damping'] = damping
        paired.save(OUT/'configs'/f'damping{damping:g}.json', candidate)


def bank(split, scene, users):
    if split == 'acceptance' and not (OUT/'FROZEN_CANDIDATE.json').exists():
        raise ValueError('Acceptance is sealed until development passes')
    folder = OUT/'bank'/split/f'scene{scene:03d}_users{users}'
    ready = folder/'READY.json'
    if not ready.exists():
        config = paired.read(paired.MODEL)
        parameters = dict(snr_db=0., frames=16, activity_probability=.1, users=users)
        public, truth, generation = observation(SEEDS[split]+scene, parameters, config['scale'])
        controls = phase.Controls(**paired.read(ROOT/paired.PHASE_CONFIG)['phase_estimation'])
        values, record = estimated_phase(public, folder, controls)
        inputs = public.at_estimated_phase(values['phase_slopes'])
        paired.save_arrays(folder/'public.npz', public.arguments())
        paired.save_arrays(folder/'input.npz', dict(observation=inputs.observation, operator=inputs.operator,
            noise_variance=inputs.noise_variance, activity_prior=inputs.activity_prior))
        paired.save_arrays(folder/'truth.npz', truth)
        paired.save(folder/'GENERATION.json', generation)
        paired.save(ready, dict(seed=SEEDS[split]+scene, users=users,
            sha256={p.name:paired.sha(p) for p in folder.iterdir() if p.is_file()}))
    for name, digest in paired.read(ready)['sha256'].items():
        assert paired.sha(folder/name) == digest
    data = paired.arrays(folder/'input.npz')
    inputs = paired.ReceiverInput(data['observation'], data['operator'], float(data['noise_variance']), float(data['activity_prior']))
    return inputs, paired.arrays(folder/'truth.npz'), folder


def run(split, scene, users, candidate):
    prepare()
    if split == 'acceptance':
        freeze = paired.read(OUT/'FROZEN_CANDIDATE.json')
        if candidate not in (freeze['candidate'], 'offgrid_sbl'):
            raise ValueError('Only the frozen candidate may access acceptance')
        for path, digest in freeze['source_and_weight_sha256'].items():
            if paired.sha(ROOT/path) != digest:
                raise ValueError('Frozen source changed: '+path)
    out = OUT/'evaluations'/split/candidate/f'scene{scene:03d}_users{users}'
    if (out/'SUMMARY.json').exists():
        print('Already recorded', out, flush=True)
        return
    if out.exists():
        raise ValueError('Unfinished attempt requires inspection; no overwrite')
    inputs, truth, folder = bank(split,scene,users)
    torch.set_num_threads(1)
    if candidate.endswith('_fp32'):
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cuda.matmul.allow_tf32 = False
    candidate_implementation = None
    if candidate.startswith('anderson_'):
        import importlib.util
        import afdm_jadcedd.algorithm.proposed.receiver as receiver_module
        path = OUT/'candidate_implementation/anderson_iterations.py'
        spec = importlib.util.spec_from_file_location('afdm_jadcedd.algorithm.proposed.anderson_candidate',path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receiver_module.run_spatial_score = module.run_spatial_score
        candidate_implementation = {str(path):paired.sha(path),
            str(ROOT/'scripts/stability_anderson.py'):paired.sha(ROOT/'scripts/stability_anderson.py')}
    config = None if candidate == 'offgrid_sbl' else paired.read(OUT/'configs'/f'{candidate}.json')
    if config is None:
        # Frozen policy uses POSIX path keys; keep all source digests unchanged.
        from afdm_jadcedd.algorithm.baselines.offgrid import receiver as offgrid
        original = offgrid.inference_sources
        offgrid.inference_sources = lambda: {k.replace('\\', '/'):v for k,v in original().items()}
    model = (solver('offgrid_sbl',dict(device='cpu')) if config is None
             else paired.EstimatedNoiseProposedReceiver(config,device='cuda'))
    if config is not None:
        model.base.model.first = GraphForward(model.base.model.first)
        model.base.model.second = GraphForward(model.base.model.second)
    paired.save(out/'PLAN.json', dict(candidate=candidate, split=split, scene=scene, users=users,
        input_manifest_sha256=paired.sha(folder/'READY.json'), config=config,
        cudnn_allow_tf32=torch.backends.cudnn.allow_tf32,
        matmul_allow_tf32=torch.backends.cuda.matmul.allow_tf32,
        candidate_implementation_sha256=candidate_implementation,
        script_sha256=paired.sha(Path(__file__)), truth_used_in_inference=False))
    rows = []
    def observe(row,state,query,covariance,*unused):
        target = truth['channel']/config['scale']
        nmse = float(np.sum(abs(state.mean-target)**2)/np.sum(abs(target)**2))
        rows.append(dict(iteration=row['iteration'],nmse_db=float(10*np.log10(nmse)),
            estimate_change=row['estimate_change'],raw_site_residual=row['raw_site_residual'],
            activity_change=row['activity_change'], query_variance=row['query_variance_min'],
            supported=row['moment_samples']>0, site_accepted=row['site_accepted']))
    try:
        prediction, record = model.infer(inputs,**({} if config is None else dict(observer=observe)))
        if candidate_implementation:
            record['candidate_implementation_sha256'] = candidate_implementation
        metrics = paired.score_arrays(prediction,truth)
        finite = all(np.isfinite(value).all() for value in prediction.values())
        summary = dict(candidate=candidate,scene=scene,users=users,status='COMPLETE',
            iterations=record['iterations'],stopping_reason=record['stopping_reason'],
            seconds=record['seconds'],metrics=metrics,finite=finite,
            supported_iterations=record.get('supported_query_iterations'),last=rows[-1] if rows else None)
        paired.save(out/'record.json',record)
        paired.save(out/'TRACE.json',rows)
        paired.save_arrays(out/'prediction.npz',prediction)
        summary['prediction_sha256'] = paired.sha(out/'prediction.npz')
        paired.save(out/'SUMMARY.json',summary)
        print(candidate,scene,users,metrics['nmse_db'],record['stopping_reason'],record['iterations'],flush=True)
    except Exception:
        paired.save(out/'FAILURE.json',dict(error=traceback.format_exc()))
        raise


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--candidate',default='damping0.2')
    parser.add_argument('--split',default='development',choices=list(SEEDS))
    parser.add_argument('--scene',type=int,default=0)
    parser.add_argument('--users',type=int,nargs='+',default=[20,60,100])
    args=parser.parse_args()
    with threadpool_limits(1):
        if args.prepare:
            prepare()
        else:
            for users in args.users:
                run(args.split,args.scene,users,args.candidate)
