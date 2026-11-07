"""Bounded, explicitly authorized pilot. Separate preflight/run/report commands."""
from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys
import time
import traceback

import numpy as np
import torch
from torch.nn import functional as F
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from algorithm.registry import load_models
from algorithm.proposed.inference import ProposedReceiver
from algorithm.candidates.wei_cai_20261022.receiver import Branches, Candidate, LocalTrainer, energy
from evaluation.receivers import setup
from utils import read_json, write_json, sha256, state_sha

DATA = Path(r'D:\afdm-gfra-cpu\runs\lstmp_conditional_bce_v3_depth10_fast_20261020\data')
OUT = ROOT/'result/candidates/wei_cai_20261022/pilot_v1'
VARIANTS = ('activity', 'joint_error', 'mixture')
SEED = 202610227100001


def selection():
    receipts = {split: read_json(DATA/f'receiver_{split}.json') for split in ('train', 'validation')}
    conditions = receipts['train']['identity']['conditions']
    assert len(conditions) == 19 and conditions == receipts['validation']['identity']['conditions']
    selected = {}
    for split, repetitions in (('train', 20), ('validation', 10)):
        selected[split] = [dict(index=index, condition=index % len(conditions),
            seed=receipts[split]['identity']['base_seed']+index,
            file=str(DATA/'receiver'/f'{split}_{index:04d}.npz'),
            sha256=receipts[split]['files'][f'{split}_{index:04d}.npz'])
            for index in range(repetitions*len(conditions))]
    assert not ({x['seed'] for x in selected['train']}&{x['seed'] for x in selected['validation']})
    return conditions, selected


def load_case(item, adapter):
    path = Path(item['file'])
    if sha256(path) != item['sha256']:
        raise ValueError('Training/validation sample changed: '+str(path))
    with np.load(path, allow_pickle=False) as saved:
        values = dict(saved)
    assert int(values['seed']) == item['seed']
    public, _ = adapter.data.prepare_public({key: values[key] for key in ('y','a','rho','noise')},
        adapter.scale, 'cuda', phase_mode='known', noise_mode='known')
    channel = values['x']/adapter.scale
    truth = torch.tensor(np.stack((channel.real,channel.imag),axis=1),dtype=torch.float32,device='cuda')
    active = torch.tensor(values['active'],dtype=torch.float32,device='cuda')
    return public, truth, active


def dependencies():
    paths = [Path(__file__), ROOT/'src/algorithm/candidates/wei_cai_20261022/receiver.py',
        ROOT/'src/algorithm/proposed/receiver.py', ROOT/'src/algorithm/proposed/components.py',
        ROOT/'src/algorithm/proposed/inputs.py', ROOT/'src/configs/final/receiver.json',
        ROOT/'src/configs/final/models.json', ROOT/'FINAL.json']
    return {str(path.relative_to(ROOT)).replace('\\','/'): sha256(path) for path in paths}


def model():
    setup('cuda')
    torch.manual_seed(SEED)
    adapter = ProposedReceiver(load_models(), 'cuda')
    return adapter, Candidate(adapter.model)


def preflight():
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'PLAN.json').exists(), 'A pilot plan already exists; preserve it'
    conditions, selected = selection()
    adapter, receiver = model()
    checks=[]; timings=[]; joint=[]; conditional=[]
    for index in (5,6,9):
        public, truth, active = load_case(selected['train'][index],adapter)
        with torch.no_grad():
            baseline,_=adapter.model(public)
        torch.cuda.synchronize(); start=time.perf_counter()
        rows=receiver.forward(public)
        torch.cuda.synchronize(); timings.append(time.perf_counter()-start)
        for li,(before,after) in enumerate(zip(baseline,rows)):
            if not torch.equal(before['estimate'],after['estimate']) or not torch.equal(before['logits'],after['logits']):
                raise AssertionError(f'Baseline mismatch, scene {index}, layer {li+1}')
        joint.append([float(energy(truth-r['estimate']).mean()/r['query_variance']) for r in rows])
        conditional.append([float(energy(truth-r['conditional'])[active.bool()].mean()/r['query_variance']) for r in rows])
        checks.append(dict(name='exact_baseline_reproduction',training_case=index,users=len(active),layers=10,passed=True))
    ratios={'joint_error':np.clip(np.mean(joint,axis=0),1e-4,10).tolist(),
            'mixture':np.clip(np.mean(conditional,axis=0),1e-4,10).tolist()}
    torch.manual_seed(SEED+1)
    bank=Branches(adapter.model,'joint_error',ratios['joint_error']).cuda()
    trainer=LocalTrainer(bank,float(len(active)),float(active.sum()))
    frozen_versions=[p._version for p in adapter.model.parameters()]
    before_activity=state_sha(bank.activity[0]);before_error=state_sha(bank.error[0])
    q,v,mu=receiver.teacher(public)[0]
    row=bank.local(0,q,v,mu,public['rho'])
    update=trainer.update(0,row,truth,active)
    assert before_activity != state_sha(bank.activity[0]) and before_error != state_sha(bank.error[0])
    assert frozen_versions == [p._version for p in adapter.model.parameters()]
    assert all(p.grad is None and not p.requires_grad for p in adapter.model.parameters())
    train_ids={id(p) for group in trainer.optimizers[0].param_groups for p in group['params']}
    assert not train_ids.intersection(id(p) for p in adapter.model.parameters())
    assert sum(p.numel() for p in bank.error[0].parameters())==2273
    save_path=OUT/'PREFLIGHT_BRANCHES.pt'
    torch.save(bank.state_dict(),save_path)
    restored=Branches(adapter.model,'joint_error',ratios['joint_error']).cuda()
    restored.load_state_dict(torch.load(save_path,map_location='cuda',weights_only=True))
    assert state_sha(bank)==state_sha(restored)
    checks.extend([dict(name='activity_and_error_gradients_update_only_candidate',passed=True,update=update),
        dict(name='branch_serialization_round_trip',passed=True),dict(name='error_parameters_per_layer',value=2273,passed=True)])
    # One real training forward/backward for the largest selected condition.
    def update_layer(index,row): trainer.update(index,row,truth,active)
    torch.cuda.reset_peak_memory_stats();torch.cuda.synchronize();start=time.perf_counter()
    receiver.forward(public,bank,update_layer)
    torch.cuda.synchronize();training_seconds=time.perf_counter()-start
    assert frozen_versions == [p._version for p in adapter.model.parameters()]
    checks.append(dict(name='100_user_full_candidate_training_pass',passed=True,
                       seconds=training_seconds,peak_allocated_mib=torch.cuda.max_memory_allocated()/2**20))
    write_json(OUT/'PREFLIGHT.json',dict(status='PASS',checks=checks,initial_ratios=ratios,
        initialization_cases=[5,6,9],inference_seconds=timings,training_100user_seconds=training_seconds,
        source_sha256=dependencies(),selected_checkpoint_sha256=adapter.configuration['checkpoint_sha256'],
        note='Preflight branch updates discarded. Only original training samples were used.'))
    print(json.dumps(dict(status='PASS',inference_seconds=timings,training_100user_seconds=training_seconds,
                         initial_ratios=ratios),ensure_ascii=False),flush=True)


def save_checkpoint(banks,trainers,round_index,label):
    destination=OUT/'checkpoints'/f'{label}.pt'
    destination.parent.mkdir(exist_ok=True)
    temporary=destination.with_suffix('.tmp')
    torch.save(dict(round=round_index,branches={k:b.state_dict() for k,b in banks.items()},
        optimizers={k:[o.state_dict() for o in t.optimizers] for k,t in trainers.items()},
        base_checkpoint_sha256=load_models()['proposed']['checkpoint_sha256']),temporary)
    temporary.replace(destination)


def score(rows,truth,active):
    result=[]
    signal=float(truth.square().sum())
    mask=active.bool()
    for index,row in enumerate(rows):
        p=row['probability'];decision=p>=.5
        error=energy(truth-row['estimate'])
        raw=float(row['raw_scale']);mapped=float(row['feedback_scale'])
        bins=[]
        for low,high in zip((0,.1,.5,.9),(.1,.5,.9,1.000001)):
            use=(p>=low)&(p<high)
            bins.append(dict(count=int(use.sum()),sum_probability=float(p[use].sum()),
                             active=int(active[use].sum())))
        result.append(dict(layer=index+1,full_error=float((truth-row['estimate']).square().sum()),
            signal_energy=signal,active_error=float((truth[mask]-row['estimate'][mask]).square().sum()),
            users=len(active),active=int(active.sum()),misses=int((mask&~decision).sum()),
            false_alarms=int((~mask&decision).sum()),
            bce_sum=float(F.binary_cross_entropy_with_logits(row['logits'],active,reduction='sum')),
            raw_scale=raw,mapped_scale=mapped,actual_error_mean=float(error.mean()),
            actual_error_active=float(error[mask].mean()),
            actual_error_inactive=float(error[~mask].mean()) if (~mask).any() else None,
            query_variance=float(row['query_variance']),feedback_ratio=float(row['feedback_ratio']),
            probabilities=p.cpu().tolist(),bins=bins,
            false_high_confidence=int(((p>=.9)&~mask).sum()),
            missed_high_confidence=int(((p<=.1)&mask).sum())))
    return result


def run():
    pre=read_json(OUT/'PREFLIGHT.json')
    assert pre['status']=='PASS' and pre['source_sha256']==dependencies()
    assert not (OUT/'PLAN.json').exists(), 'Preserve existing pilot; do not restart automatically'
    conditions,selected=selection()
    # Count active labels from training only; validation never defines a loss scale.
    users=[];actives=[]
    for item in selected['train']:
        assert sha256(item['file'])==item['sha256']
        with np.load(item['file'],allow_pickle=False) as saved:
            users.append(len(saved['active']));actives.append(int(np.sum(saved['active'])))
    mean_users,mean_active=float(np.mean(users)),float(np.mean(actives))
    plan=dict(status='PLANNED_AUTHORIZED_PILOT',created_utc=datetime.now(timezone.utc).isoformat(),
        authorization='User: 可以，请你尝试一下. Earlier 500-scene evaluation separately stopped at explicit request.',
        scope='Small-branch adaptation only; original ten score networks and scalar calibrations frozen.',
        conditions=conditions,selected=selected,training_scenes=380,validation_scenes=190,
        variants=['baseline',*VARIANTS],rounds=3,phase='known',noise='known',
        stage0='One shared baseline trajectory per training scene; adapt each branch on those fixed queries.',
        stages1and2='Two passes refreshing each candidate trajectory; local gradients only.',
        selection='Fixed final budget; no validation-based checkpoint choice in this small pilot.',
        deviation_from_full_design='Pilot uses 20/10 scenes per condition rather than 250/100; one final validation only.',
        decision_threshold=.5,activity_lr=1e-5,error_lr=1e-3,adam=dict(betas=[.9,.999],eps=1e-8),
        per_branch_gradient_clip=1.0,mean_training_users=mean_users,mean_training_active=mean_active,
        initial_ratios=pre['initial_ratios'],source_sha256=dependencies(),
        base_checkpoint_sha256=pre['selected_checkpoint_sha256'],seed=SEED,
        data_scope='Read-only original training and development archives; no 324-scene test data used for fitting or selection.',
        evaluation_scope='Development pilot, not an untouched final test or a replacement of the frozen model.')
    write_json(OUT/'PLAN.json',plan)
    import shutil
    for relative in dependencies():
        path=OUT/'source'/relative
        path.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/relative,path)
    adapter,receiver=model()
    versions=[p._version for p in adapter.model.parameters()]
    banks={};trainers={}
    for variant in VARIANTS:
        torch.manual_seed(SEED+1)
        banks[variant]=Branches(adapter.model,variant,pre['initial_ratios'].get(variant)).cuda()
        trainers[variant]=LocalTrainer(banks[variant],mean_users,mean_active)
    save_checkpoint(banks,trainers,-1,'initial')
    started=time.perf_counter();losses=[]
    def status(stage,**values):
        report=dict(stage=stage,elapsed_seconds=time.perf_counter()-started,
                    updated_utc=datetime.now(timezone.utc).isoformat(),**values)
        write_json(OUT/'STATUS.json',report)
        print(json.dumps(report,ensure_ascii=False),flush=True)
    try:
        for round_index in range(3):
            order=np.random.default_rng(SEED+round_index).permutation(len(selected['train']))
            accum=defaultdict(lambda:dict(activity_loss=0.0,error_loss=0.0,updates=0))
            status('TRAINING',round=round_index+1,scenes=0,total_scenes=380)
            for position,which in enumerate(order,1):
                item=selected['train'][int(which)]
                public,truth,active=load_case(item,adapter)
                if round_index==0:
                    teacher=receiver.teacher(public)
                    for variant,bank in banks.items():
                        for li,(query,v,mean) in enumerate(teacher):
                            row=bank.local(li,query,v,mean,public['rho'])
                            metrics=trainers[variant].update(li,row,truth,active)
                            for key in ('activity_loss','error_loss'):accum[variant][key]+=metrics[key]
                            accum[variant]['updates']+=1
                    del teacher
                else:
                    for variant,bank in banks.items():
                        def update_layer(index,row):
                            metrics=trainers[variant].update(index,row,truth,active)
                            for key in ('activity_loss','error_loss'):accum[variant][key]+=metrics[key]
                            accum[variant]['updates']+=1
                        trajectory=receiver.forward(public,bank,update_layer)
                        del trajectory
                del public,truth,active
                if position%20==0:
                    status('TRAINING',round=round_index+1,scenes=position,total_scenes=380,
                        mean_losses={key:{name:data[name]/data['updates'] for name in ('activity_loss','error_loss')}
                                     for key,data in accum.items()})
                if position%100==0:save_checkpoint(banks,trainers,round_index,'latest')
            save_checkpoint(banks,trainers,round_index,f'round_{round_index+1}')
            losses.append(dict(round=round_index+1,accumulated=dict(accum)))
            write_json(OUT/'TRAINING_LOSSES.json',losses)
            assert versions==[p._version for p in adapter.model.parameters()]
        status('VALIDATING',scenes=0,total_scenes=190)
        validation=[]
        for position,item in enumerate(selected['validation'],1):
            public,truth,active=load_case(item,adapter)
            for variant,bank in [('baseline',None),*banks.items()]:
                begin=time.perf_counter()
                trajectory=receiver.forward(public,bank)
                torch.cuda.synchronize()
                seconds=time.perf_counter()-begin
                validation.append(dict(variant=variant,index=item['index'],condition=item['condition'],seed=item['seed'],
                    seconds=seconds,truth_activity=active.bool().cpu().tolist(),layers=score(trajectory,truth,active)))
                del trajectory
            if position%10==0:
                write_json(OUT/'VALIDATION_PARTIAL.json',dict(rows=validation))
                status('VALIDATING',scenes=position,total_scenes=190)
        assert versions==[p._version for p in adapter.model.parameters()]
        assert dependencies()==plan['source_sha256'], 'Sources changed during pilot'
        write_json(OUT/'VALIDATION.json',dict(status='COMPLETE',rows=validation))
        save_checkpoint(banks,trainers,2,'final')
        write_json(OUT/'COMPLETE.json',dict(status='COMPLETE',elapsed_seconds=time.perf_counter()-started,
            frozen_base_unchanged=True,source_sha256=dependencies(),
            validation_sha256=sha256(OUT/'VALIDATION.json'),checkpoint_sha256=sha256(OUT/'checkpoints/final.pt')))
        status('COMPLETE',training_scenes=380,validation_scenes=190,rounds=3)
    except BaseException:
        write_json(OUT/'FAILURE.json',dict(traceback=traceback.format_exc(),elapsed_seconds=time.perf_counter()-started))
        status('FAILED')
        raise


def report():
    plan=read_json(OUT/'PLAN.json');rows=read_json(OUT/'VALIDATION.json')['rows']
    conditions=plan['conditions'];summaries=[]
    for variant in ('baseline',*VARIANTS):
        per_condition=[]
        for ci,condition in enumerate(conditions):
            selected=[r for r in rows if r['variant']==variant and r['condition']==ci]
            end=[r['layers'][-1] for r in selected]
            total={key:sum(r[key] for r in end) for key in ('full_error','signal_energy','active_error','users','active','misses','false_alarms','bce_sum')}
            per_condition.append(dict(condition=condition,index=ci,scenes=len(end),
                nmse_db=float(10*np.log10(total['full_error']/total['signal_energy'])),
                error_ratio=total['full_error']/total['signal_energy'],
                aer_percent=100*(total['misses']+total['false_alarms'])/total['users'],**total))
        all_final=[r['layers'][-1] for r in rows if r['variant']==variant]
        summaries.append(dict(variant=variant,conditions=per_condition,
            condition_equal_nmse_db=float(10*np.log10(np.mean([r['error_ratio'] for r in per_condition]))),
            condition_equal_aer_percent=float(np.mean([r['aer_percent'] for r in per_condition])),
            pooled_aer_percent=100*sum(r['misses']+r['false_alarms'] for r in all_final)/sum(r['users'] for r in all_final),
            misses=sum(r['misses'] for r in all_final),false_alarms=sum(r['false_alarms'] for r in all_final),
            mean_seconds=float(np.mean([r['seconds'] for r in rows if r['variant']==variant]))))
    write_json(OUT/'SUMMARY.json',dict(status='COMPLETE_DEVELOPMENT_PILOT',summaries=summaries,
        scope='19 conditions, 10 disjoint development scenes each. No final-test performance claim.'))
    print(json.dumps([dict(variant=r['variant'],nmse_db=r['condition_equal_nmse_db'],
        aer_percent=r['condition_equal_aer_percent'],misses=r['misses'],false_alarms=r['false_alarms'])
        for r in summaries],ensure_ascii=False,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('preflight','run','report'))
    args=parser.parse_args()
    with threadpool_limits(4):
        {'preflight':preflight,'run':run,'report':report}[args.command]()
