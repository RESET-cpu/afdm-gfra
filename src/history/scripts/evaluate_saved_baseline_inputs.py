"""Evaluate new Proposed weights on immutable, already scored baseline inputs."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import json
from pathlib import Path
import sys
import time
import traceback
import warnings

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'experiment')]
import numpy as np
from _common import condition, summarize
from _support.storage import read, save, sha, arrays, save_arrays, identities, verify_sources, pending_methods
from _support.settings import proposed_bundles, PHASE_CONFIG
from afdm_jadcedd.algorithm.proposed_noise_candidate import EstimatedNoiseProposedReceiver
from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput
from afdm_jadcedd.system.observation import ReceiverInput, array_sha256
from afdm_jadcedd.experiment.evaluation.metrics import score_arrays

PACKAGE=Path('D:/afdm-gfra-cpu/runs/cpu_9900x_20261018/package')
BASELINES=Path('D:/afdm-gfra-cpu/results_windows')
MODEL=ROOT/'runs/proposed_auxiliary_100_cuda_graph_20261019/n50000/receiver.json'
METHODS=('offgrid_sbl','gnn','gamp','somp')


def prepare(output,job):
    if output.exists():
        raise ValueError('A new output directory is required')
    source_plan=PACKAGE/'inputs'/job/'PLAN.json'
    original=read(source_plan)
    index_path=PACKAGE/'inputs/INDEX.json'
    index=read(index_path)['experiments'][job]
    source_manifest=read(PACKAGE/'SOURCE_MANIFEST.json')['files']
    assert sha(index_path)==source_manifest['inputs/INDEX.json']
    assert sha(source_plan)==source_manifest[f'inputs/{job}/PLAN.json']==index['source_plan_sha256']
    spec=original['experiment'].copy()
    expected={f'scene{s:03d}/condition{i:02d}' for s in range(spec['scenes']) for i in range(len(spec['values']))}
    assert set(index['cases'])==expected and index['conditions']==len(expected)
    assert read(BASELINES/job/'SUMMARY.json')['status']=='COMPLETE'
    bundles,hashes=proposed_bundles(full_config=MODEL)
    assert bundles['proposed']['train_samples']==50000
    assert spec['scale']==bundles['proposed']['configuration']['scale']
    assert read(PACKAGE/PHASE_CONFIG)['phase_estimation']==read(ROOT/PHASE_CONFIG)['phase_estimation']
    spec.update(methods=['proposed'],device='cuda',proposed_bundles=bundles,
        training_sample_comparison='NOT_APPLICABLE',receiver_configs={'proposed':str(MODEL)},phase_config=PHASE_CONFIG)
    for path in (source_plan,index_path,PACKAGE/'SOURCE_MANIFEST.json',BASELINES/job/'SUMMARY.json',Path(__file__)):
        hashes[str(path.resolve())]=sha(path)
    plan=dict(experiment=spec,job=job,input_package=str(PACKAGE),baseline_results=str(BASELINES/job),
        source_and_weight_sha256=identities()|hashes,created_unix=time.time(),expected_runs=len(expected),
        pairing='Read preserved public observation and conditional operator; validate original case, arrays, truth and phase before every inference. No scene regeneration.',
        baseline_methods=list(METHODS),baseline_results_recomputed=False,
        timing='New CUDA Proposed times and historical CPU/MPS baseline times are not a controlled speed comparison.')
    save(output/'PLAN.json',plan)
    save(output/'STATUS.json',dict(status='PREPARED',expected_runs=len(expected)))
    print(json.dumps(dict(status='PREPARED',job=job,expected_runs=len(expected))))


def load_case(plan,index,scene,number):
    spec=plan['experiment']; job=plan['job']
    key=f'scene{scene:03d}/condition{number:02d}'
    original=Path(plan['input_package'])/'inputs'/job/key
    baseline=Path(plan['baseline_results'])/key
    if sha(original/'CASE.json')!=index[key]:
        raise ValueError('Original case changed: '+key)
    case=read(original/'CASE.json')
    if case['seed']!=spec['seed']+scene or case['parameters']!=condition(spec,spec['values'][number]):
        raise ValueError('Scene seed/condition mismatch')
    pairing=read(baseline/'PAIRING.json')
    proof={str(original/'CASE.json'):sha(original/'CASE.json'),str(baseline/'PAIRING.json'):sha(baseline/'PAIRING.json')}
    loaded={}
    for name,record in pairing['files'].items():
        path=baseline/name
        if sha(path)!=record['sha256']:
            raise ValueError('Preserved baseline input changed: '+str(path))
        proof[str(path)]=record['sha256']
        if name.endswith('.npz'):
            loaded[name]=arrays(path)
            if 'arrays' in record and {k:array_sha256(v) for k,v in loaded[name].items()}!=record['arrays']:
                raise ValueError('Preserved input array identity changed')
    public=UnknownPhaseInput(**loaded['public.npz'])
    input_hash={k:array_sha256(v) for k,v in public.arguments().items()}
    if input_hash!=case['arrays'] or read(baseline/'INPUT.json')['arrays']!=input_hash:
        raise ValueError('Observation differs from original fixed input')
    truth=loaded['truth.npz']
    if {k:array_sha256(v) for k,v in truth.items()}!=case['truth_arrays']:
        raise ValueError('Scoring truth differs')
    cache=read(baseline/'PHASE_CACHE.json')
    if cache['identity']['inputs']!=input_hash or cache['identity']['controls']!=read(ROOT/PHASE_CONFIG)['phase_estimation']:
        raise ValueError('Estimated phase belongs to different inputs or controls')
    operator=loaded['operator.npz']['operator']
    reproduced=public.at_estimated_phase(loaded['phase.npz']['phase_slopes']).operator
    # Cross-platform exp/multiply can differ at double-precision roundoff.
    # This is only a consistency check; inference uses the exact saved operator.
    tolerance=8*np.finfo(float).eps
    if not np.allclose(reproduced,operator,rtol=tolerance,atol=tolerance*np.max(abs(operator))):
        raise ValueError('Saved operator differs from the saved estimated phase')
    for method in METHODS:
        path=baseline/f'{method}.json'; row=read(path)
        if row['status']!='COMPLETE' or row['input_array_sha256']!=input_hash or row['truth_used_in_inference'] is not False:
            raise ValueError('Baseline does not share the same public input')
        if sha(baseline/f'{method}.npz')!=row['compact_sha256']:
            raise ValueError('Baseline result changed')
        proof[str(path)]=sha(path)
    return ReceiverInput(public.observation,operator,1.,public.activity_prior),truth,input_hash,proof,case['generation'],read(baseline/'PHASE.json')


def run(output,limit=None):
    import torch
    from threadpoolctl import threadpool_limits
    plan=read(output/'PLAN.json'); verify_sources(plan)
    spec=plan['experiment']
    index=read(Path(plan['input_package'])/'inputs/INDEX.json')['experiments'][plan['job']]['cases']
    torch.set_num_threads(1)
    done=0; started=time.time()
    model=EstimatedNoiseProposedReceiver(spec['proposed_bundles']['proposed']['configuration'],device=spec['device'])
    with threadpool_limits(1):
        for scene in range(spec['scenes']):
            for number,value in enumerate(spec['values']):
                folder=output/f'scene{scene:03d}/condition{number:02d}'
                if not pending_methods(folder,['proposed']):
                    done+=1
                    continue
                save(output/'STATUS.json',dict(status='RUNNING',pid=os.getpid(),completed=done,
                    expected_runs=plan['expected_runs'],scene=scene,condition=number,value=value,updated_unix=time.time()))
                conditional,truth,hashes,proof,generation,phase=load_case(plan,index,scene,number)
                save(folder/'INPUT.json',dict(arrays=hashes,generation=generation))
                save(folder/'PAIRING_SOURCE.json',dict(files=proof,operator_sha256=array_sha256(conditional.operator),
                    public_input_sha256=hashes,no_regeneration=True))
                base=dict(scene=scene,condition=number,method='proposed',input_array_sha256=hashes,
                    phase_mode='estimated',noise_mode='estimated',truth_used_in_inference=False)
                try:
                    with warnings.catch_warnings(record=True) as notices:
                        warnings.simplefilter('always',RuntimeWarning)
                        prediction,record=model.infer(conditional)
                    if record.get('status','COMPLETE')!='COMPLETE' or not all(np.isfinite(v).all() for v in prediction.values()):
                        raise FloatingPointError('Incomplete or nonfinite receiver output')
                    metrics=score_arrays(prediction,truth)
                    compact={k:v for k,v in prediction.items() if np.asarray(v).ndim<=1}
                    compact.update(per_user_error=np.asarray(metrics['per_user_error']),truth_activity=truth['activity'])
                    save_arrays(folder/'proposed.npz',compact)
                    if scene==0:
                        save_arrays(folder/'proposed.prediction.npz',prediction)
                    save(folder/'proposed.record.json',record)
                    save(folder/'proposed.json',dict(base,status='COMPLETE',metrics=metrics,
                        receiver_seconds=record['seconds'],phase_seconds=phase['seconds'],
                        compact_sha256=sha(folder/'proposed.npz'),iterations=record['iterations'],
                        stopping_reason=record['stopping_reason'],
                        output_array_sha256={k:array_sha256(v) for k,v in prediction.items()},
                        warnings=[str(w.message) for w in notices]))
                except Exception:
                    save(folder/'proposed.json',dict(base,status='FAILED',traceback=traceback.format_exc()))
                    save(output/'STATUS.json',dict(status='FAILED',scene=scene,condition=number,updated_unix=time.time()))
                    raise
                done+=1
                print(json.dumps(dict(job=plan['job'],completed=done,expected=plan['expected_runs'],
                    scene=scene,condition=number,seconds=record['seconds'],iterations=record['iterations'])),flush=True)
                if limit and done>=limit:
                    save(output/'STATUS.json',dict(status='CHECKED_INITIAL_CASES',completed=done,
                        expected_runs=plan['expected_runs'],updated_unix=time.time()))
                    return
    verify_sources(plan)
    save(output/'STATUS.json',dict(status='COMPLETED',completed=done,elapsed_seconds=time.time()-started,updated_unix=time.time()))
    summarize(output,spec)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('plan','run'))
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--job',choices=('user_count','cross_channel'))
    parser.add_argument('--limit',type=int)
    args=parser.parse_args()
    if args.action=='plan':
        prepare(args.output.resolve(),args.job)
    else:
        run(args.output.resolve(),args.limit)
