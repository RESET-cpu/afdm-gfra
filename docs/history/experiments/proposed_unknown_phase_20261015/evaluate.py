"""Evaluate Proposed with estimated phase on the saved five-baseline panel."""
import argparse
from collections import Counter
from dataclasses import asdict
import json
import os
from pathlib import Path
import platform
import sys
import time
import traceback

import numpy as np
import torch
from threadpoolctl import threadpool_limits

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from afdm_jadcedd.algorithm.registry import build_receiver,verify_algorithms
from afdm_jadcedd.system.observation import array_sha256
from afdm_jadcedd.utils import sha256,write_json
from evaluate_ldamp_joint import score,summarize


def read_npz(path):
    with np.load(path,allow_pickle=False) as saved:
        return {key:saved[key] for key in saved.files}


def verify_baseline_panel(folder):
    plan=json.loads((folder/'PLAN.json').read_text())
    status=json.loads((folder/'STATUS.json').read_text())
    audit=json.loads((folder/'OUTPUT_AUDIT.json').read_text())
    assert status['status']=='COMPLETE' and audit['status']=='PASS'
    rows=json.loads((folder/'ROWS.json').read_text())
    expected={(s,n,m) for s in range(plan['scenes']) for n in plan['snr_db'] for m in plan['methods']}
    assert len(rows)==len(expected) and {(r['scene'],r['snr_db'],r['method']) for r in rows}==expected
    # The original code snapshot, saved outputs and public inputs define the
    # preceding run. New optional receiver code need not match that snapshot.
    for name,digest in plan['sources'].items():
        assert sha256(folder/'sources'/name)==digest,name
    for row in rows:
        case=folder/f"scene{row['scene']:03d}"/f"snr{row['snr_db']:+03d}"
        assert row['status']=='COMPLETE'
        for field,name in [('output_sha256',row['method']+'.npz'),('input_sha256','estimated_operator_input.npz'),
                           ('public_unknown_phase_input_sha256','input.npz')]:
            assert row[field]==sha256(case/name),(row['scene'],row['snr_db'],name)
    return plan,rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-results',type=Path,default=ROOT/'results/unknown_phase_baselines_20261015/evaluation')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--device',choices=['cpu','mps'],default='mps')
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError('Fresh result directory required')
    prior,baseline_rows=verify_baseline_panel(args.baseline_results)
    torch.set_num_threads(1)
    config=ROOT/'configs/proposed_unknown_phase.json'
    with threadpool_limits(1):
        verification=verify_algorithms()
        receiver=build_receiver('proposed',config=config,device=args.device)
    assert asdict(receiver.controls)==prior['phase_controls']
    out=args.output;out.mkdir(parents=True)
    assets=json.loads((ROOT/'configs/mainline_assets.json').read_text())['sha256']
    paths=[ROOT/name for name in assets if name.endswith('.py')]
    paths += [Path(__file__),ROOT/'src/afdm_jadcedd/algorithm/phase_estimation.py',
              ROOT/'src/afdm_jadcedd/algorithm/unknown_phase_model.py',
              ROOT/'src/afdm_jadcedd/algorithm/proposed/unknown_phase.py',
              ROOT/'src/afdm_jadcedd/algorithm/registry.py',
              ROOT/'tests/test_proposed_unknown_phase.py',ROOT/'scripts/evaluate_ldamp_joint.py']
    sources={str(p.relative_to(ROOT)):sha256(p) for p in paths}
    for name in sources:
        target=out/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((ROOT/name).read_bytes())
    inputs={}
    for scene in range(prior['scenes']):
        for snr in prior['snr_db']:
            name=f'scene{scene:03d}/snr{snr:+03d}';case=args.baseline_results/name
            inputs[name]={key:sha256(case/key) for key in ['input.npz','truth.npz','phase.npz','estimated_operator_input.npz']}
    plan=dict(scenes=prior['scenes'],snr_db=prior['snr_db'],seeds=prior['seeds'],methods=['proposed',*prior['methods']],
              baseline_results=str(args.baseline_results.resolve()),baseline_plan_sha256=sha256(args.baseline_results/'PLAN.json'),
              baseline_rows_sha256=sha256(args.baseline_results/'ROWS.json'),
              baseline_audit_sha256=sha256(args.baseline_results/'OUTPUT_AUDIT.json'),
              seed_audit_sha256=sha256(args.baseline_results/'SEED_AUDIT.json'),
              seed_scope='Same evaluation panel as baselines; no new training, calibration or parameter selection',
              configuration=receiver.configuration,configurations={'proposed':receiver.configuration},
              configuration_sha256={str(config.relative_to(ROOT)):sha256(config)},
              sources=sources,input_sha256=inputs,mainline_verification=verification,
              inference_sha256=receiver.signature,base_inference_sha256=receiver.base_signature,
              phase_inference_sha256=receiver.phase_signature,
              procedure='Run observation-only phase estimation afresh on each saved public input, then Proposed',
              primary_metrics=['full_channel_nmse','aer'],threshold=.5,
              timing='Full phase plus conditional Proposed; loading and generation excluded',
              environment=dict(python=sys.version,numpy=np.__version__,torch=torch.__version__,
                               platform=platform.platform(),device=args.device,torch_threads=1,blas_threads=1),
              pid=os.getpid(),started_unix=time.time(),hard_timeout_seconds=7200)
    write_json(out/'PLAN.json',plan)
    rows=[];parity=[];started=time.monotonic()

    def progress(stage,scene,snr,iteration=None):
        state=dict(status='RUNNING',stage=stage,scene=scene,snr_db=snr,iteration=iteration,
                   completed_rows=len(rows),expected_rows=prior['scenes']*len(prior['snr_db']),
                   failures=sum(r['status']!='COMPLETE' for r in rows),pid=os.getpid(),seconds=time.monotonic()-started)
        write_json(out/'STATUS.json',state);print(json.dumps(state),flush=True)
        if state['seconds']>plan['hard_timeout_seconds']:raise TimeoutError('Two-hour recorded experiment budget exceeded')

    for scene in range(prior['scenes']):
        for snr in prior['snr_db']:
            name=f'scene{scene:03d}/snr{snr:+03d}';source=args.baseline_results/name
            target=out/name;target.mkdir(parents=True)
            try:
                progress('phase_estimation',scene,snr)
                count=[0]
                def observe(row,*state):
                    count[0]+=1
                    if count[0]==1 or count[0]%20==0:progress('proposed',scene,snr,count[0])
                with threadpool_limits(1):
                    record=receiver.run(source/'input.npz',target/'proposed.npz',observer=observe,
                                        phase_observer=lambda row:progress('phase_sweep_'+str(row['sweep']),scene,snr))
                arrays=read_npz(target/'proposed.npz')
                # The saved reference phase is read only after this independent
                # inference completes, and is used solely for parity checks.
                reference=read_npz(source/'phase.npz')
                for key,value in reference.items():
                    np.testing.assert_array_equal(arrays[key if key=='phase_slopes' else 'phase_'+key],value)
                conditional=read_npz(source/'estimated_operator_input.npz')
                assert record['estimated_operator_sha256']==array_sha256(conditional['operator'])
                np.testing.assert_array_equal(arrays['activity_decision'],arrays['probabilities']>=.5)
                assert not record['truth_used_in_inference'] and not record['truth_loaded']
                assert record['input_sha256']==inputs[name]['input.npz']
                parity.append(dict(scene=scene,snr_db=snr,phase_arrays_exact=True,operator_exact=True))
                truth=read_npz(source/'truth.npz')
                row=dict(scene=scene,snr_db=snr,method='proposed',status='COMPLETE',**score(arrays,truth),
                         seconds=record['seconds'],baseline_seconds=record['base_seconds'],phase_seconds=record['phase_seconds'],
                         iterations=record['iterations'],stopping_reason=record['stopping_reason'],
                         input_sha256=record['input_sha256'],output_sha256=record['output_sha256'],
                         inference_sha256=record['inference_sha256'])
                del truth
            except Exception as error:
                row=dict(scene=scene,snr_db=snr,method='proposed',status='FAILED',
                         error=repr(error),traceback=traceback.format_exc())
                write_json(target/'evaluation_failure.json',row)
                print(json.dumps(row),flush=True)
            rows.append(row);write_json(out/'ROWS.json',rows);write_json(out/'PHASE_PARITY.json',parity)
            progress('condition_complete',scene,snr)
    combined=[*baseline_rows,*rows]
    write_json(out/'COMPARISON_ROWS.json',combined)
    changed=[name for name,digest in sources.items() if sha256(ROOT/name)!=digest]
    for name,digest in plan['configuration_sha256'].items():
        if sha256(ROOT/name)!=digest:changed.append(name)
    for name,files in inputs.items():
        for file,digest in files.items():
            if sha256(args.baseline_results/name/file)!=digest:changed.append(name+'/'+file)
    failures=[r for r in rows if r['status']!='COMPLETE']
    write_json(out/'SUMMARY.json',dict(results=summarize(combined),failures=failures,source_changes=changed,
                                      stopping_reasons=dict(Counter(r.get('stopping_reason','FAILED') for r in rows))))
    state=dict(status='COMPLETE' if not failures and not changed else 'FAILED',completed_rows=len(rows),
               expected_rows=prior['scenes']*len(prior['snr_db']),failures=len(failures),source_changes=changed,
               phase_parity_conditions=len(parity),seconds=time.monotonic()-started,pid=os.getpid())
    write_json(out/'STATUS.json',state);print(json.dumps(state),flush=True)
    if failures or changed:raise SystemExit(1)


if __name__=='__main__':main()
