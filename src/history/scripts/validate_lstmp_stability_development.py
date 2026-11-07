"""Freeze a candidate before paired evaluation on new independent development seeds."""
import importlib.util,json,math,os,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUN=Path(r'D:\afdm-gfra-cpu\runs\lstmp_refinenet_50000_fast_20261019')
OUT=ROOT/'results/lstmp_stability_development_20261019'
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
    inputs,truth,metadata=generate_case(seed,snr,scale,**settings)
    values=dict(y=inputs['observation'],a=inputs['operator'],noise=inputs['noise_variance'],rho=inputs['activity_prior'])
    public,_=data.prepare_public(values,scale,'cuda',phase_mode='known',noise_mode='known')
    labels=dict(x=common.real_tensor(truth['channel']/scale,'cuda'),active=torch.tensor(truth['activity'],dtype=torch.float32,device='cuda'),physical_scale=scale)
    return public,labels,dict(seed=seed,snr=float(snr),condition=condition,actual_active_users=int(truth['activity'].sum()))


def main():
    if OUT.exists():raise FileExistsError(OUT)
    if (RUN/'RUNNING.lock').exists():raise RuntimeError('Training remains stopped')
    OUT.mkdir(parents=True);(OUT/'source').mkdir()
    source=ROOT/'experiments/lstmp_stability_candidate_20261019/receiver.py'
    shutil.copy2(source,OUT/'source/receiver.py');shutil.copy2(__file__,OUT/'source/validate.py')
    spec=importlib.util.spec_from_file_location('frozen_stability_receiver',OUT/'source/receiver.py')
    candidate=importlib.util.module_from_spec(spec);spec.loader.exec_module(candidate)
    jobs=[]
    for i in range(240):
        jobs.append(dict(group='balanced',seed=202610199600001+i,condition=data.condition_for('validation',i)))
    for i in range(240):
        jobs.append(dict(group='K100_Q8_SNR10',seed=202610199700001+i,condition=dict(users=100,frames=8,activity_probability=.1,snr_db=10)))
    path=RUN/'checkpoints/depth_2/last.pt'
    protected={str(p):common.sha(p) for p in [path,RUN/'checkpoints/depth_2/best.pt',RUN/'checkpoints/depth_1/best.pt',RUN/'MANIFEST.json',ROOT/'MAINLINE.json']}
    plan=dict(created_unix=time.time(),jobs=jobs,candidate_sha256=common.sha(source),protected=protected,
        source='Current failed depth-2 last checkpoint; no optimizer updates',
        method='Accept full proposal if J does not increase; otherwise minimize J along its segment. J=||A X-Y||^2+noise/(rho*training_second_moment)||X||^2. Dampen channel mean and activity probability with the same coefficient.',
        independence='Fresh seed ranges disjoint from prior training, receiver train/validation/test and reserved 20 comparison scenes; no outcome selection',
        selected_before_development_results=True,
        stability_criteria=dict(finite_all=True,maximum_scene_nmse_linear=10.,maximum_quadratic_relative_increase=2e-5),
        accuracy_criteria=dict(maximum_aer_increase_absolute=.01,maximum_median_paired_nmse_ratio=1.05),
        caveat='These are development acceptance criteria, not guarantees or paper performance claims; all cases retained.')
    common.save_json(OUT/'PLAN.json',plan)
    torch.set_num_threads(4);threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32=True;torch.backends.cudnn.allow_tf32=True;torch.backends.cudnn.benchmark=True
    saved=torch.load(path,map_location='cpu',weights_only=False)
    models={}
    for name,cls in [('original',receiver.Receiver),('candidate',candidate.Receiver)]:
        model=cls()
        for _ in range(2):model.add_layer(None)
        model.load_state_dict(saved['state']);model.cuda().eval();model.use_checkpoint=False
        models[name]=model
    del saved
    scale=common.CONFIG['pretrained_score']['global_complex_rms']
    rows={name:[] for name in models};started=time.time()
    with torch.no_grad():
        for i,job in enumerate(jobs):
            public,labels,info=make_case(job['seed'],job['condition'],scale)
            for name,model in models.items():
                outputs,diagnostics=model(public)
                scores=receiver.metrics(outputs,labels)
                row=dict(**info,group=job['group'],case_index=i,**scores,loss=float(receiver.loss(outputs,labels)),diagnostics=diagnostics)
                if not all(np.isfinite(row[k]) for k in ['loss','nmse','error_energy']):raise FloatingPointError(f'Nonfinite {name} scene {i}; preserved')
                rows[name].append(row)
            if (i+1)%24==0:
                common.save_json(OUT/'ROWS_PARTIAL.json',rows)
                status=dict(scenes=i+1,total=len(jobs),elapsed_seconds=time.time()-started)
                common.save_json(OUT/'STATUS.json',status);print(json.dumps(status),flush=True)
    summaries={name:{group:receiver.summarize_rows([r for r in data_rows if r['group']==group]) for group in ('balanced','K100_Q8_SNR10')} for name,data_rows in rows.items()}
    comparisons={}
    for group in ('balanced','K100_Q8_SNR10'):
        a=[r for r in rows['original'] if r['group']==group];b=[r for r in rows['candidate'] if r['group']==group]
        paired_ratio=float(np.median([v['nmse']/u['nmse'] for u,v in zip(a,b)]))
        aer_delta=summaries['candidate'][group]['aer']-summaries['original'][group]['aer']
        maximum=max(r['nmse'] for r in b)
        cost_increase=max(d['quadratic_relative_increase'] for r in b for d in r['diagnostics'])
        comparisons[group]=dict(scenes=len(b),maximum_nmse=maximum,median_paired_nmse_ratio=paired_ratio,
            aer_difference=aer_delta,quadratic_relative_increase=cost_increase,
            original_catastrophic_scenes=sum(r['nmse']>10 for r in a),candidate_catastrophic_scenes=sum(r['nmse']>10 for r in b),
            scenes_damped=sum(any(d['damping']<1 for d in r['diagnostics']) for r in b),
            stability_passed=maximum<=10 and cost_increase<=2e-5,
            accuracy_passed=aer_delta<=.01 and paired_ratio<=1.05)
    report=dict(status='COMPLETE',summaries=summaries,comparisons=comparisons,scenes=len(jobs),optimizer_updates=0,
        protected_assets_preserved={p:common.sha(p)==h for p,h in protected.items()},elapsed_seconds=time.time()-started,
        acceptance_passed=all(r['stability_passed'] and r['accuracy_passed'] for r in comparisons.values()))
    if not all(report['protected_assets_preserved'].values()):raise RuntimeError('Protected asset changed')
    common.save_json(OUT/'ROWS.json',rows);common.save_json(OUT/'REPORT.json',report)
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
