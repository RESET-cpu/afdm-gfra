"""Small, independent calibration study. Run actions in the documented order.

No original checkpoint, formal input/result, or frozen implementation is edited.
"""
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
from scipy.special import expit, logit
from threadpoolctl import threadpool_limits
import evaluate_saved_baseline_inputs as P
from benchmark_receiver_execution import GraphForward
from _common import observation, estimated_phase, phase
from afdm_jadcedd.algorithm.proposed_calibration_candidate import (
    Calibration, CalibratedMoments, CalibratedEvidence, VARIANTS,
    covariance_from_query, feature_values, losses)

OUT = P.ROOT/'runs/message_calibration_candidates_20261019'
RESULT = P.ROOT/'results/message_calibration_candidates_20261019'
MODULE = P.ROOT/'src/afdm_jadcedd/algorithm/proposed_calibration_candidate.py'
SEED = 202610201100001


def verify():
    protocol = P.read(OUT/'PROTOCOL.json')
    for path, digest in protocol['source_and_weight_sha256'].items():
        assert P.sha(P.ROOT/path) == digest, path
    return protocol


def receiver(cfg):
    torch.set_num_threads(1)
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cuda.matmul.allow_tf32 = False
    obj = P.EstimatedNoiseProposedReceiver(cfg, device='cuda')
    obj.base.model.first = GraphForward(obj.base.model.first)
    obj.base.model.second = GraphForward(obj.base.model.second)
    return obj


def prepare():
    assert not OUT.exists(), 'Fresh directory required'
    cfg = deepcopy(P.read(P.MODEL))
    cfg['ep'].update(damping=.1, iterations=300, min_iterations=301)
    prior = P.read(P.ROOT/cfg['prior_definition'])
    source = P.identities()
    for path in (P.MODEL, Path(__file__), MODULE,
                 P.ROOT/'scripts/benchmark_receiver_execution.py',
                 P.ROOT/cfg['prior_definition']):
        source[str(path.resolve())] = P.sha(path)
    for key in ('first_checkpoint', 'second_checkpoint', 'evidence_checkpoint'):
        source[str((P.ROOT/cfg[key]).resolve())] = P.sha(P.ROOT/cfg[key])
    for split, path in prior['data_files'].items():
        actual = P.sha(P.ROOT/path)
        assert actual == prior['sample_files_sha256'][split]
        source[str((P.ROOT/path).resolve())] = actual
    # Reserve new physical seeds, distinct from training, previous diagnosis and formal sets.
    occupied = set()
    def collect(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == 'scene_seeds': occupied.update(item)
                elif isinstance(item, (dict, list)): collect(item)
        elif isinstance(value, list):
            for item in value: collect(item)
    collect(prior)
    for base in (202610172000001, 202610180100001, 202610180200001,
                 202610180300001, 202610180400001, 202610180500001,
                 202610180600001, 202610191000001, 202610192000001,
                 202610193000001, 202610195000001):
        occupied.update(range(base, base+500))
    seeds = [202610202100001, 202610202100002]
    assert not set(seeds) & occupied
    conditions = [dict(users=20, frames=16, activity_probability=.1, snr_db=0.),
                  dict(users=100, frames=16, activity_probability=.1, snr_db=0.),
                  dict(users=60, frames=12, activity_probability=.2, snr_db=0.),
                  dict(users=80, frames=20, activity_probability=.05, snr_db=0.)]
    P.save(OUT/'PROTOCOL.json', dict(configuration=cfg,
        source_and_weight_sha256=source, calibration_seed=SEED,
        train=dict(groups=128, users_per_group=32, epochs=100, batch_size=128,
                   learning_rate=.001, variance_range=[.001,100.], covariance_shrinkage=.05,
                   white_group_fraction=.25, correlated_rank_range=[1,4],
                   correlation_strength_range=[.1,.995], finite_difference_delta=.02,
                   validation_groups=32, test_groups=32, consistency_weight=.1),
        data_policy='Frozen 50k training bank subset for fitting; distinct subsets of original validation bank for selection and synthetic test. Synthetic test is unseen by calibration fitting, but not an independent test of the original 50k networks.',
        covariance='Receiver-observable lower-energy-half spatial second moment, trace normalized then 5% isotropic shrinkage. This estimate, not generating covariance, is used by features and derivatives. Held fixed for +/- queries.',
        variants=['baseline']+list(VARIANTS), physical_seeds=seeds, physical_conditions=conditions,
        physical_policy='No physical messages used in calibration fitting or checkpoint selection. All 8 paired physical cases opened only after best checkpoints are frozen. 300 updates equally; no convergence claim. Two physical seeds, not eight independent seeds.',
        checkpoint_selection='Lowest common validation prediction loss among epochs 1..100; same initialization, samples, minibatch order and capacity. Scalar masks correlation features. Consistency weight excluded from selection score.',
        loss='active MSE + .05*(log(tau)+active MSE/tau) + balanced evidence BCE; consistency candidate adds .1 times two normalized smooth-L1 directional derivative penalties.',
        scope='L-STMP-inspired small calibration heads, not a complete L-STMP reproduction, not jointly unfolded original score-network training. Scalar head uses query scalar statistics, not only layerwise constants.',
        limitations='Only 16x16 antenna covariance features; remaining grid coordinates treated independent. Isotropic native posterior pooling remains. Soft sampled derivative penalties do not impose exact joint-density consistency; signal-dependent late error is unmodeled.',
        success_screen='All finite; paired aggregate NMSE improvement without >0.5 dB regression in any case or increased aggregate miss+false-alarm count. This is only a small diagnostic screen, never formal experiment acceptance.',
        original_weights_frozen=True, formal_experiments='PAUSED'))
    P.save(OUT/'STATUS.json', dict(status='PREPARED'))
    print('PREPARED', flush=True)


def cache():
    protocol = verify(); cfg = protocol['configuration']; spec = protocol['train']
    obj = receiver(cfg).base
    prior = P.read(P.ROOT/cfg['prior_definition'])
    rng_index = np.random.default_rng(SEED)
    train_bank = np.load(P.ROOT/prior['data_files']['train'], mmap_mode='r')
    val_bank = np.load(P.ROOT/prior['data_files']['validation'], mmap_mode='r')
    train_ids = rng_index.choice(len(train_bank), spec['groups']*16, replace=False)
    val_ids = rng_index.permutation(len(val_bank))[:(spec['validation_groups']+spec['test_groups'])*16]
    splits = [('train', train_bank, train_ids, spec['groups']),
              ('validation', val_bank, val_ids[:spec['validation_groups']*16], spec['validation_groups']),
              ('test', val_bank, val_ids[spec['validation_groups']*16:], spec['test_groups'])]
    assert len(set(splits[1][2]) & set(splits[2][2])) == 0
    for split_index, (split, bank, selected, groups) in enumerate(splits):
        destination = OUT/'cache'/f'{split}.npz'
        assert not destination.exists()
        rows = []; metadata = []
        rng = np.random.default_rng(SEED+split_index+1)
        for group in range(groups):
            v = float(np.exp(rng.uniform(np.log(.001), np.log(100.))))
            white = group % 4 == 0
            rank = int(rng.integers(1,5))
            basis = rng.normal(size=(16,rank))+1j*rng.normal(size=(16,rank))
            basis = np.linalg.qr(basis)[0]
            strength = 0. if white else float(rng.uniform(.1,.995))
            generating_c = v*((1-strength)*np.eye(16) + strength*16/rank*(basis@basis.conj().T))
            factor = np.linalg.cholesky(generating_c)
            ids = selected[group*16:(group+1)*16]
            clean = np.zeros((32,16,16,16), complex)
            clean[:16] = np.asarray(bank[ids], complex)/cfg['scale']
            active = np.r_[np.ones(16), np.zeros(16)]
            z = (rng.normal(size=clean.shape)+1j*rng.normal(size=clean.shape))/np.sqrt(2)
            query = clean + np.einsum('mn,knrc->kmrc',factor,z,optimize=False)
            cov = covariance_from_query(query,v)
            direction_z = (2*rng.integers(2,size=query.shape)-1)+1j*(2*rng.integers(2,size=query.shape)-1)
            direction = np.einsum('mn,knrc->kmrc',cov,direction_z,optimize=False)/np.sqrt(2*v)
            label = np.full(32,v); features=[]; ratios=[]; logits=[]; base_mean=None
            for offset in (0, spec['finite_difference_delta'], -spec['finite_difference_delta']):
                q = query+offset*direction
                moment = obj.model.infer(q,label)
                ell = obj.evidence.infer(q,label,moment.mean)
                features.append(feature_values(q,label,moment.mean,moment.variance,ell,cov))
                ratios.append(moment.variance/label); logits.append(ell)
                if offset == 0: base_mean=moment.mean
            d = base_mean-query; error = query-clean; axes=(1,2,3); size=query[0].size
            rows.append(dict(features=np.stack(features,axis=1),raw_ratio=np.stack(ratios,axis=1),
                raw_logit=np.stack(logits,axis=1), variance=label, active=active,
                mse0=np.mean(abs(error)**2,axis=axes), mse_cross=np.mean((error.conj()*d).real,axis=axes),
                delta_energy=np.mean(abs(d)**2,axis=axes),
                project_r=np.sum((direction_z.conj()*query).real,axis=axes)/np.sqrt(v*size),
                project_delta=np.sum((direction_z.conj()*d).real,axis=axes)/np.sqrt(v*size),
                real_dimension=np.full(32,2*size), clean_energy=np.mean(abs(clean)**2,axis=axes),
                group=np.full(32,group),white=np.full(32,white)))
            metadata.append(dict(group=group,variance=v,white=white,rank=rank,strength=strength,
                clean_indices=ids.tolist(),estimated_covariance_relative_error=float(np.linalg.norm(cov-generating_c)/np.linalg.norm(generating_c))))
            if (group+1)%8==0:
                print('CACHE',split,group+1,groups,flush=True)
                P.save(OUT/'STATUS.json',dict(status='CACHE',split=split,completed_groups=group+1,total_groups=groups))
        data = {key:np.concatenate([row[key] for row in rows]).astype(np.float32) for key in rows[0]}
        P.save_arrays(destination,data)
        P.save(destination.with_suffix('.json'),dict(groups=metadata,cache_sha256=P.sha(destination),
            shape={key:list(value.shape) for key,value in data.items()}))
    verify()


def tensors(split):
    path=OUT/'cache'/f'{split}.npz'
    assert P.sha(path)==P.read(path.with_suffix('.json'))['cache_sha256']
    return {key:torch.from_numpy(value) for key,value in P.arrays(path).items()}


def measurements(model, batch):
    with torch.no_grad():
        alpha, ratio, ell = model(batch['features'],batch['raw_ratio'],batch['raw_logit'])
        result={key:float(value) for key,value in losses(model,batch).items()}
        a=alpha[:,0]; active=batch['active'].bool()
        mse=(batch['mse0']+2*a*batch['mse_cross']+a*a*batch['delta_energy']).clamp_min(0)
        result['active_nmse_db']=float(10*torch.log10(mse[active].sum()/batch['clean_energy'][active].sum()))
        z=ell[:,0].numpy()+logit(.1); truth=active.numpy(); prob=expit(z)
        result.update(misses=int(np.sum(truth&(z<0))),false_alarms=int(np.sum(~truth&(z>=0))),
                      probability_squared_error=float(np.mean((prob-truth)**2)),
                      active=int(truth.sum()),inactive=int((~truth).sum()))
    return result


def train():
    protocol=verify(); spec=protocol['train'];torch.set_num_threads(1)
    training=tensors('train'); validation=tensors('validation'); test=tensors('test')
    results=[]
    for variant in VARIANTS:
        dest=OUT/'models'/variant;assert not dest.exists();dest.mkdir(parents=True)
        torch.manual_seed(7319); model=Calibration(variant)
        opt=torch.optim.Adam(model.parameters(),lr=spec['learning_rate'])
        shuffle=torch.Generator().manual_seed(6194)
        best=float('inf'); history=[]; initial=measurements(model,validation)
        for epoch in range(1,spec['epochs']+1):
            model.train(); order=torch.randperm(len(training['active']),generator=shuffle)
            accumulated={}
            for indices in order.split(spec['batch_size']):
                batch={key:value[indices] for key,value in training.items()}
                opt.zero_grad(set_to_none=True); loss=losses(model,batch,spec['finite_difference_delta'])
                if not bool(torch.isfinite(loss['total'])): raise FloatingPointError('Training loss')
                loss['total'].backward();torch.nn.utils.clip_grad_norm_(model.parameters(),10.)
                opt.step()
                for key,value in loss.items(): accumulated[key]=accumulated.get(key,0)+float(value.detach())*len(indices)/len(order)
            model.eval(); val=measurements(model,validation)
            history.append(dict(epoch=epoch,train=accumulated,validation=val))
            payload=dict(variant=variant,state_dict=model.state_dict(),epoch=epoch,
                protocol_sha256=P.sha(OUT/'PROTOCOL.json'),validation=val,
                original_weights_frozen=True,parameters=sum(p.numel() for p in model.parameters()))
            if val['common']<best:
                best=val['common'];torch.save(payload,dest/'best.pt')
            if epoch%10==0: print('TRAIN',variant,epoch,round(val['common'],5),flush=True)
        torch.save(payload,dest/'last.pt')
        best_blob=torch.load(dest/'best.pt',weights_only=False);model.load_state_dict(best_blob['state_dict'])
        P.save(dest/'HISTORY.json',dict(initial_validation=initial,epochs=history))
        # Common validation loss selected the checkpoint before this test readout.
        result=dict(variant=variant,epoch=best_blob['epoch'],parameters=best_blob['parameters'],
                    validation=best_blob['validation'],synthetic_test=measurements(model,test),
                    best_sha256=P.sha(dest/'best.pt'),last_sha256=P.sha(dest/'last.pt'))
        P.save(dest/'SUMMARY.json',result);results.append(result)
    baseline=Calibration('correlation').eval()
    # Identity head clamps extreme raw variances; label it separately from exact baseline.
    P.save(OUT/'models/SUMMARY.json',dict(results=results,identity_with_variance_bounds=measurements(baseline,test),
        test_note='Synthetic samples balance labels; probability errors at rho=.1 are descriptive, not population-calibration estimates.'))
    P.save(OUT/'FROZEN_MODELS.json',dict(models={row['variant']:row['best_sha256'] for row in results},
        source_and_weight_sha256=protocol['source_and_weight_sha256'],physical_test_opened=False))
    verify()


def banks():
    protocol=verify();assert (OUT/'FROZEN_MODELS.json').exists()
    controls=phase.Controls(**P.read(P.ROOT/P.PHASE_CONFIG)['phase_estimation'])
    for i,seed in enumerate(protocol['physical_seeds']):
        for j,parameters in enumerate(protocol['physical_conditions']):
            name=f'seed{i:02d}_condition{j:02d}';folder=OUT/'bank'/name
            if (folder/'READY.json').exists():continue
            public,truth,generation=observation(seed,parameters,protocol['configuration']['scale'])
            values,record=estimated_phase(public,folder,controls)
            conditional=public.at_estimated_phase(values['phase_slopes'])
            P.save_arrays(folder/'public.npz',public.arguments())
            P.save_arrays(folder/'input.npz',conditional.arguments())
            P.save_arrays(folder/'truth.npz',truth)
            P.save(folder/'GENERATION.json',generation)
            P.save(folder/'READY.json',dict(seed=seed,parameters=parameters,
                sha256={file:P.sha(folder/file) for file in ('public.npz','input.npz','truth.npz','GENERATION.json')}))
            print('BANK',name,flush=True)


def physical():
    protocol=verify();frozen=P.read(OUT/'FROZEN_MODELS.json');cfg=protocol['configuration']
    obj=receiver(cfg);original_moments=obj.base.model;original_evidence=obj.base.evidence
    results=[];checkpoints=(1,5,10,20,30,60,120,180,240,300)
    for folder in sorted((OUT/'bank').iterdir()):
        ready=P.read(folder/'READY.json')
        for name,digest in ready['sha256'].items(): assert P.sha(folder/name)==digest
        data=P.arrays(folder/'input.npz');inp=P.ReceiverInput(**data)
        for variant in protocol['variants']:
            dest=OUT/'physical'/folder.name/variant
            if (dest/'SUMMARY.json').exists():
                results.append(P.read(dest/'SUMMARY.json'));continue
            assert not dest.exists(), 'Incomplete run preserved; inspect before retry'
            dest.mkdir(parents=True)
            adapter=None
            if variant=='baseline':
                obj.base.model=original_moments;obj.base.evidence=original_evidence
            else:
                path=OUT/'models'/variant/'best.pt';assert P.sha(path)==frozen['models'][variant]
                model=Calibration(variant);model.load_state_dict(torch.load(path,weights_only=False)['state_dict'])
                adapter=CalibratedMoments(original_moments,original_evidence,model)
                obj.base.model=adapter;obj.base.evidence=CalibratedEvidence(adapter)
            snapshots=[];started=time.monotonic();warnings_list=[]
            def observer(row,state,*unused):
                iteration=row['iteration']
                if iteration in checkpoints:
                    snapshots.append((iteration,dict(estimate=(state.mean*cfg['scale']).copy(),
                        probabilities=state.activity.copy(),activity_decision=(state.activity>=.5).copy())))
                if iteration%100==0:
                    print('PHYSICAL',folder.name,variant,iteration,round(time.monotonic()-started,1),flush=True)
                    P.save(OUT/'STATUS.json',dict(status='PHYSICAL',case=folder.name,variant=variant,
                        iteration=iteration,completed=len(results),total=32))
            import warnings
            try:
                with warnings.catch_warnings(record=True) as notices:
                    warnings.simplefilter('always',RuntimeWarning)
                    prediction,record=obj.infer(inp,observer=observer)
                warnings_list=[str(item.message) for item in notices]
                if not all(np.isfinite(value).all() for value in prediction.values()):
                    raise FloatingPointError('Nonfinite prediction')
                assert record['iterations']==300 and not record['converged']
                if adapter is not None:
                    assert adapter.cache is None
                    record['calibration_diagnostics']=adapter.diagnostics
                record['calibration_variant']=variant
                P.save(dest/'record.json',record);P.save_arrays(dest/'prediction.npz',prediction)
                # Ground truth is first read after the complete receiver run.
                truth=P.arrays(folder/'truth.npz');trace=[]
                for iteration,values in snapshots:
                    trace.append(dict(iteration=iteration,**P.score_arrays(values,truth),
                        probability_squared_error=float(np.mean((values['probabilities']-truth['activity'])**2))))
                result=dict(case=folder.name,seed=ready['seed'],parameters=ready['parameters'],variant=variant,
                    status='COMPLETE',metrics=P.score_arrays(prediction,truth),trace=trace,
                    probability_squared_error=float(np.mean((prediction['probabilities']-truth['activity'])**2)),
                    iterations=record['iterations'],seconds=record['seconds'],convergence_claim=False,
                    unsupported_user_queries=record['unsupported_user_queries'],
                    reused_site_iterations=record['reused_site_iterations'],
                    input_sha256=ready['sha256']['input.npz'],truth_used_in_inference=False,warnings=warnings_list)
                del truth,snapshots
            except Exception:
                result=dict(case=folder.name,seed=ready['seed'],parameters=ready['parameters'],variant=variant,
                    status='FAILED',traceback=traceback.format_exc(),seconds=time.monotonic()-started,
                    completed_checkpoints=[item[0] for item in snapshots],warnings=warnings_list)
                # Retain failure and continue other paired candidates; never drop a case.
                obj.base.last_trace=[]
            P.save(dest/'SUMMARY.json',result);results.append(result)
            print('FINISHED',folder.name,variant,result['status'],result.get('metrics',{}).get('nmse_db'),flush=True)
    verify()
    P.save(OUT/'physical/SUMMARY.json',dict(status='COMPLETE',results=results))


def report():
    protocol=verify();rows=P.read(OUT/'physical/SUMMARY.json')['results']
    assert len(rows)==32
    baseline={r['case']:r for r in rows if r['variant']=='baseline'}
    aggregate={}
    for variant in protocol['variants']:
        selected=[r for r in rows if r['variant']==variant]
        completed=[r for r in selected if r['status']=='COMPLETE']
        result=dict(cases=len(selected),failures=len(selected)-len(completed))
        if completed:
            result.update(pooled_nmse_db=float(10*np.log10(sum(r['metrics']['full_error'] for r in completed)/sum(r['metrics']['signal_energy'] for r in completed))),
                misses=sum(r['metrics']['misses'] for r in completed),
                false_alarms=sum(r['metrics']['false_alarms'] for r in completed),
                mean_probability_squared_error=float(np.mean([r['probability_squared_error'] for r in completed])),
                receiver_seconds=sum(r['seconds'] for r in selected),
                paired_delta_db={r['case']:r['metrics']['nmse_db']-baseline[r['case']]['metrics']['nmse_db'] for r in completed if baseline[r['case']]['status']=='COMPLETE'})
        aggregate[variant]=result
    reference=aggregate['baseline']
    for variant in VARIANTS:
        value=aggregate[variant]
        value['passes_small_screen']=bool(value['failures']==0 and reference['failures']==0 and
            value['pooled_nmse_db']<reference['pooled_nmse_db'] and max(value['paired_delta_db'].values())<=.5 and
            value['misses']+value['false_alarms']<=reference['misses']+reference['false_alarms'])
    preservation=P.read(P.ROOT/'runs/stability_repair_20261019/PRESERVATION.json')
    for name,digest in preservation.items():assert P.sha(P.ROOT/name)==digest,name
    P.save(RESULT/'REPORT.json',dict(status='COMPLETE',aggregate=aggregate,results=rows,
        training=P.read(OUT/'models/SUMMARY.json'),protocol_sha256=P.sha(OUT/'PROTOCOL.json'),
        preserved_historical_files=len(preservation),protocol_files_verified=len(protocol['source_and_weight_sha256']),
        formal_experiments='PAUSED',original_weights_changed=False,
        limitation='Two fresh physical seeds, eight paired configurations, fixed 300 iterations. Screening does not establish convergence, formal acceptance or publication-level superiority.'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    colors=dict(baseline='#343a40',scalar='#e69f00',correlation='#0072b2',consistency='#009e73')
    fig,axes=plt.subplots(2,4,figsize=(16,7),sharex=True)
    for ax,(case,base) in zip(axes.flat,baseline.items()):
        for row in [r for r in rows if r['case']==case and r['status']=='COMPLETE']:
            ax.plot([t['iteration'] for t in row['trace']],[t['nmse_db'] for t in row['trace']],
                label=row['variant'],color=colors[row['variant']],marker='.',ms=4)
        p=base['parameters'];ax.set_title(f"Seed {str(base['seed'])[-3:]} | K={p['users']}, Q={p['frames']}, rho={p['activity_probability']}",fontsize=10)
        ax.grid(alpha=.2);ax.set_xlabel('Iteration');ax.set_ylabel('NMSE (dB)')
    axes.flat[0].legend(fontsize=8)
    fig.suptitle('Frozen 50k networks + calibration: new physical scenes | damping 0.1 | fixed budget')
    fig.tight_layout();fig.savefig(RESULT/'physical_nmse.png',dpi=160);fig.savefig(RESULT/'physical_nmse.pdf');plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(13,3.6))
    for variant in VARIANTS:
        history=P.read(OUT/'models'/variant/'HISTORY.json')['epochs']
        for ax,key in zip(axes,('common','evidence_bce','consistency')):
            ax.plot([h['epoch'] for h in history],[h['validation'][key] for h in history],color=colors[variant],label=variant)
            ax.set_title(key);ax.set_xlabel('Epoch');ax.grid(alpha=.2)
    axes[0].legend();fig.suptitle('Held-out synthetic validation; original score networks frozen')
    fig.tight_layout();fig.savefig(RESULT/'training_validation.png',dpi=160);plt.close(fig)
    P.save(OUT/'STATUS.json',dict(status='COMPLETE',physical_runs=32,report=str(RESULT/'REPORT.json')))
    print(aggregate,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','cache','train','banks','physical','report'))
    action=parser.parse_args().action
    with threadpool_limits(1):globals()[action]()
