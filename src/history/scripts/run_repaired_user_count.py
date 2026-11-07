"""Resume paired user-count evaluation only after independent acceptance passes."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
from copy import deepcopy
import ctypes
import msvcrt
from pathlib import Path
import subprocess
import sys
import time
import traceback
import numpy as np
import torch
from threadpoolctl import threadpool_limits
import repair_stability_development as d
from benchmark_receiver_execution import GraphForward

paired=d.paired
OUT=Path('D:/afdm-gfra-cpu/results_proposed_stability_20261019')
TARGET=OUT/'user_count'


def prepare():
    if OUT.exists():raise ValueError('Fresh formal candidate output required')
    gate=paired.read(d.OUT/'ACCEPTANCE_GATE.json')
    if not gate['passed'] or gate['cases']!=60:
        raise ValueError('Independent acceptance did not pass')
    freeze=paired.read(d.OUT/'FROZEN_CANDIDATE.json')
    if gate['candidate']!=freeze['candidate'] or gate['protocol_sha256']!=paired.sha(d.OUT/'PROTOCOL.json'):
        raise ValueError('Acceptance is not bound to this frozen candidate and protocol')
    if freeze['development_gate_sha256']!=paired.sha(d.OUT/'DEVELOPMENT_GATE.json'):
        raise ValueError('Frozen development evidence changed')
    if not freeze['candidate'].startswith('damping'):
        raise ValueError('This formal runner supports the unchanged native iteration only')
    paired.verify_sources(freeze)
    old=d.ROOT/'results/new_models_paired_20261019_cuda_graph/user_count/PLAN.json'
    plan=deepcopy(paired.read(old));paired.verify_sources(plan)
    spec=plan['experiment'];config=freeze['configuration']
    spec['proposed_bundles']['proposed']['configuration']=config
    spec['receiver_configs']['proposed']=str(d.OUT/'configs'/f'{freeze["candidate"]}.json')
    plan['source_and_weight_sha256'].update(freeze['source_and_weight_sha256'])
    for path in (Path(__file__),d.OUT/'ACCEPTANCE_GATE.json',d.OUT/'FROZEN_CANDIDATE.json',old):
        plan['source_and_weight_sha256'][str(path.resolve())]=paired.sha(path)
    plan.update(created_unix=time.time(),predecessor=str(old.parent),candidate=freeze['candidate'],
        original_results_reused=0,mainline_promoted=False,
        execution=dict(workers=4,cudnn_allow_tf32=False,matmul_allow_tf32=False,
            precision='FP32 convolution/linear layers; float64 and complex128 CPU iteration',
            cuda_graph_first_second=True,damping=config['ep']['damping'],max_iterations=config['ep']['iterations'],
            convergence_tolerances_unchanged=True,weights_changed=False),
        validation='Independent development and sealed 60-case acceptance gates passed; no universal stability guarantee',
        pause_policy='After any nonconverged or invalid case, preserve it and drain in-flight cases before pausing.',
        cross_channel='PAUSED_PENDING_SEPARATE_VALIDATION')
    paired.save(TARGET/'PLAN.json',plan)
    paired.save(OUT/'STATUS.json',dict(status='PREPARED',completed=0,expected_runs=2500))


def worker(number):
    plan=paired.read(TARGET/'PLAN.json');paired.verify_sources(plan)
    spec=plan['experiment'];index=paired.read(Path(plan['input_package'])/'inputs/INDEX.json')['experiments']['user_count']['cases']
    torch.set_num_threads(1);torch.backends.cudnn.allow_tf32=False;torch.backends.cuda.matmul.allow_tf32=False
    model=paired.EstimatedNoiseProposedReceiver(spec['proposed_bundles']['proposed']['configuration'],device='cuda')
    model.base.model.first=GraphForward(model.base.model.first);model.base.model.second=GraphForward(model.base.model.second)
    with threadpool_limits(1):
        for flat in range(number,plan['expected_runs'],4):
            if (OUT/'PAUSE.json').exists():break
            scene,condition=divmod(flat,5);folder=TARGET/f'scene{scene:03d}/condition{condition:02d}'
            if not paired.pending_methods(folder,['proposed']):continue
            paired.save(TARGET/f'STATUS.worker{number}.json',dict(status='RUNNING',scene=scene,condition=condition,pid=os.getpid()))
            base=dict(scene=scene,condition=condition,method='proposed',phase_mode='estimated',noise_mode='estimated',truth_used_in_inference=False)
            try:
                inputs,truth,hashes,proof,generation,phase=paired.load_case(plan,index,scene,condition)
                base['input_array_sha256']=hashes
                paired.save(folder/'INPUT.json',dict(arrays=hashes,generation=generation))
                paired.save(folder/'PAIRING_SOURCE.json',dict(files=proof,operator_sha256=paired.array_sha256(inputs.operator),
                    public_input_sha256=hashes,no_regeneration=True))
                prediction,record=model.infer(inputs)
                if not all(np.isfinite(v).all() for v in prediction.values()):raise FloatingPointError('Nonfinite receiver output')
                metrics=paired.score_arrays(prediction,truth)
                compact={k:v for k,v in prediction.items() if np.asarray(v).ndim<=1}
                compact.update(per_user_error=np.asarray(metrics['per_user_error']),truth_activity=truth['activity'])
                paired.save_arrays(folder/'proposed.npz',compact)
                if scene==0 or not record['converged']:paired.save_arrays(folder/'proposed.prediction.npz',prediction)
                record['execution']=plan['execution'];paired.save(folder/'proposed.record.json',record)
                paired.save(folder/'proposed.json',dict(base,status='COMPLETE',metrics=metrics,
                    receiver_seconds=record['seconds'],phase_seconds=phase['seconds'],
                    compact_sha256=paired.sha(folder/'proposed.npz'),iterations=record['iterations'],
                    stopping_reason=record['stopping_reason'],converged=record['converged'],
                    output_array_sha256={k:paired.array_sha256(v) for k,v in prediction.items()}))
                if not record['converged']:
                    paired.save(OUT/'PAUSE.json',dict(reason='Candidate did not meet unchanged stopping criteria',scene=scene,condition=condition,retained_result=str(folder)))
                print(scene,condition,metrics['nmse_db'],record['iterations'],record['stopping_reason'],flush=True)
            except Exception:
                error=traceback.format_exc();paired.save(folder/'proposed.json',dict(base,status='FAILED',traceback=error))
                paired.save(OUT/'PAUSE.json',dict(reason='Inference failure',scene=scene,condition=condition,traceback=error))
                raise
    paired.save(TARGET/f'STATUS.worker{number}.json',dict(status='STOPPED' if (OUT/'PAUSE.json').exists() else 'COMPLETE'))


def supervise():
    plan=paired.read(TARGET/'PLAN.json');paired.verify_sources(plan)
    with (OUT/'run.lock').open('a+b') as lock:
        lock.seek(0)
        if not lock.read(1):lock.write(b'0');lock.flush()
        lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
        children=[];streams=[];started=time.time()
        (OUT/'logs').mkdir(exist_ok=True)
        try:
            for number in range(4):
                log=(OUT/'logs'/f'worker{number}.log').open('a');streams.append(log)
                children.append(subprocess.Popen([sys.executable,'-u',__file__,'worker','--worker',str(number)],
                    cwd=d.ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW))
            while True:
                codes=[p.poll() for p in children]
                if any(c not in (None,0) for c in codes) and not (OUT/'PAUSE.json').exists():
                    paired.save(OUT/'PAUSE.json',dict(reason='Worker exited unexpectedly',exit_codes=codes))
                paths=list(TARGET.glob('scene*/condition*/proposed.json'))
                complete=sum(paired.read(p)['status']=='COMPLETE' for p in paths)
                state=dict(status='DRAINING_FOR_PAUSE' if (OUT/'PAUSE.json').exists() else 'RUNNING',
                    completed=complete,expected_runs=2500,pid=os.getpid(),worker_pids=[p.pid for p in children],
                    started_unix=started,updated_unix=time.time(),cross_channel='PAUSED_PENDING_SEPARATE_VALIDATION')
                paired.save(OUT/'STATUS.json',state);paired.save(TARGET/'STATUS.json',state)
                if all(c is not None for c in codes):break
                time.sleep(10)
            if (OUT/'PAUSE.json').exists():
                paired.save(OUT/'STATUS.json',dict(state,status='PAUSED_FOR_INSPECTION'))
            else:
                paired.verify_sources(plan);paired.summarize(TARGET,spec=plan['experiment'])
                paired.save(OUT/'STATUS.json',dict(state,status='COMPLETE'))
        finally:
            for stream in streams:stream.close()
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','run','worker']);parser.add_argument('--worker',type=int)
    args=parser.parse_args()
    if args.action=='prepare':prepare()
    elif args.action=='worker':worker(args.worker)
    else:supervise()
