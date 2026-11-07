"""Independent, predeclared evaluation of Gaussian-message damping; no training."""
import importlib.util,json,math,os,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUN=Path(r'D:\afdm-gfra-cpu\runs\lstmp_refinenet_50000_fast_20261019')
OUT=ROOT/'results/lstmp_message_damping_development_20261019'
os.environ['AFDM_LSTMP_ROOT']=str(ROOT)
os.environ['AFDM_LSTMP_CONFIG']=str(RUN/'source_code/experiments/lstmp_candidate_20261019/reuse_50000_fast.json')
sys.path.insert(0,str(RUN/'source_code'))
import numpy as np
import torch
from threadpoolctl import threadpool_limits
from experiments.lstmp_candidate_20261019 import common,data,receiver
from afdm_jadcedd.experiment.generate import generate_case


def make_case(seed,condition,scale):
    settings=dict(condition);snr=settings.pop('snr_db')
    inputs,truth,_=generate_case(seed,snr,scale,**settings)
    public,_=data.prepare_public(dict(y=inputs['observation'],a=inputs['operator'],noise=inputs['noise_variance'],rho=inputs['activity_prior']),scale,'cuda',phase_mode='known',noise_mode='known')
    labels=dict(x=common.real_tensor(truth['channel']/scale,'cuda'),active=torch.tensor(truth['activity'],dtype=torch.float32,device='cuda'),physical_scale=scale)
    return public,labels


def main():
    if OUT.exists():raise FileExistsError(OUT)
    if (RUN/'RUNNING.lock').exists():raise RuntimeError('Training remains stopped')
    OUT.mkdir(parents=True);(OUT/'source').mkdir()
    source=ROOT/'experiments/lstmp_message_damping_candidate_20261019/receiver.py'
    shutil.copy2(source,OUT/'source/receiver.py');shutil.copy2(__file__,OUT/'source/validate.py')
    spec=importlib.util.spec_from_file_location('frozen_message_receiver',OUT/'source/receiver.py')
    candidate=importlib.util.module_from_spec(spec);spec.loader.exec_module(candidate)
    jobs=[dict(group='balanced',seed=202610201600001+i,condition=data.condition_for('validation',i)) for i in range(240)]
    jobs += [dict(group='K100_Q8_SNR10',seed=202610201700001+i,condition=dict(users=100,frames=8,activity_probability=.1,snr_db=10)) for i in range(240)]
    path=RUN/'checkpoints/depth_2/last.pt'
    protected={str(p):common.sha(p) for p in [path,RUN/'checkpoints/depth_2/best.pt',RUN/'checkpoints/depth_1/best.pt',RUN/'MANIFEST.json',ROOT/'MAINLINE.json']}
    plan=dict(created_unix=time.time(),jobs=jobs,candidate_sha256=common.sha(source),protected=protected,
        source='Failed trained depth-2 last checkpoint; no optimizer updates',
        method='Gaussian natural parameters: a=min(1,v_initial/v_proposed), precision=(1-a)/v_previous+a/v_proposed, mean/variance interpolated by same a. Network outputs/activity logits unchanged; only subsequent-layer messages change.',
        independence='Fresh seeds, disjoint from training, validation, reserved tests, and previous development bank; no outcome selection',
        stability_criteria=dict(finite_all=True,maximum_scene_nmse_linear=10.),
        accuracy_criteria=dict(maximum_aer_increase_absolute=.01,maximum_median_paired_nmse_ratio=1.05,maximum_pooled_nmse_ratio=1.05),
        caveat='Variance-based damping coefficient is a project heuristic, not a convergence theorem. Passed depth-2 checks do not establish final depth-5 performance.')
    common.save_json(OUT/'PLAN.json',plan)
    torch.set_num_threads(4);threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32=True;torch.backends.cudnn.allow_tf32=True;torch.backends.cudnn.benchmark=True
    saved=torch.load(path,map_location='cpu',weights_only=False)
    models={}
    for name,cls in [('original',receiver.Receiver),('candidate',candidate.Receiver)]:
        model=cls()
        for _ in range(2):model.add_layer(None)
        model.load_state_dict(saved['state']);model.cuda().eval();model.use_checkpoint=False;models[name]=model
    del saved
    scale=common.CONFIG['pretrained_score']['global_complex_rms']
    rows={name:[] for name in models};started=time.time()
    with torch.no_grad():
        for i,job in enumerate(jobs):
            public,labels=make_case(job['seed'],job['condition'],scale)
            for name,model in models.items():
                outputs,diagnostics=model(public)
                row=dict(**job,case_index=i,**receiver.metrics(outputs,labels),loss=float(receiver.loss(outputs,labels)),diagnostics=diagnostics)
                row['finite']=all(np.isfinite(row[k]) for k in ['loss','nmse','error_energy'])
                rows[name].append(row)
            if (i+1)%48==0:
                common.save_json(OUT/'ROWS_PARTIAL.json',rows)
                status=dict(scenes=i+1,total=len(jobs),elapsed_seconds=time.time()-started)
                common.save_json(OUT/'STATUS.json',status);print(json.dumps(status),flush=True)
        known=[];cases=data.Cases('validation',scale,'cuda')
        for i in [807,903]:
            public,labels,_=cases[i]
            for name,model in models.items():
                outputs,diags=model(public)
                known.append(dict(case_index=i,method=name,**receiver.metrics(outputs,labels),diagnostics=diags))
    summaries={name:{group:receiver.summarize_rows([r for r in rr if r['group']==group]) for group in ['balanced','K100_Q8_SNR10']} for name,rr in rows.items()}
    comparisons={}
    for group in ['balanced','K100_Q8_SNR10']:
        a=[r for r in rows['original'] if r['group']==group];b=[r for r in rows['candidate'] if r['group']==group]
        paired=float(np.median([v['nmse']/u['nmse'] for u,v in zip(a,b)]))
        aer=summaries['candidate'][group]['aer']-summaries['original'][group]['aer']
        pooled=summaries['candidate'][group]['pooled_nmse']/summaries['original'][group]['pooled_nmse']
        maximum=max(r['nmse'] for r in b)
        comparisons[group]=dict(scenes=len(b),maximum_nmse=maximum,median_paired_nmse_ratio=paired,
            aer_difference=aer,pooled_nmse_ratio=pooled,original_catastrophic_scenes=sum(r['nmse']>10 for r in a),
            candidate_catastrophic_scenes=sum(r['nmse']>10 for r in b),
            scenes_damped=sum(r['diagnostics'][0]['damping']<1 for r in b),
            stability_passed=all(r['finite'] for r in b) and maximum<=10,
            accuracy_passed=aer<=.01 and paired<=1.05 and pooled<=1.05)
    report=dict(status='COMPLETE',summaries=summaries,comparisons=comparisons,scenes=len(jobs),known_failures=known,
        optimizer_updates=0,protected_assets_preserved={p:common.sha(p)==h for p,h in protected.items()},elapsed_seconds=time.time()-started,
        acceptance_passed=all(r['stability_passed'] and r['accuracy_passed'] for r in comparisons.values()))
    if not all(report['protected_assets_preserved'].values()):raise RuntimeError('Protected asset changed')
    common.save_json(OUT/'ROWS.json',rows);common.save_json(OUT/'REPORT.json',report)
    print(json.dumps(dict(summaries=summaries,comparisons=comparisons,acceptance_passed=report['acceptance_passed'])),flush=True)


if __name__=='__main__':main()
