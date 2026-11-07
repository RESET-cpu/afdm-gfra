"""Full validation reselection and independent deeper-initialization/gradient checks.

No optimizer steps. Never accesses the reserved final comparison scenarios.
"""
import importlib.util,json,math,os,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUN=Path(r'D:\afdm-gfra-cpu\runs\lstmp_refinenet_50000_fast_20261019')
OUT=ROOT/'results/lstmp_message_damping_resume_checks_20261019'
DEV=ROOT/'results/lstmp_message_damping_development_20261019'
os.environ['AFDM_LSTMP_ROOT']=str(ROOT)
os.environ['AFDM_LSTMP_CONFIG']=str(RUN/'source_code/experiments/lstmp_candidate_20261019/reuse_50000_fast.json')
sys.path.insert(0,str(RUN/'source_code'))
import torch
import numpy as np
from threadpoolctl import threadpool_limits
from experiments.lstmp_candidate_20261019 import common,data,receiver
from validate_lstmp_message_damping import make_case


def main():
    if OUT.exists():raise FileExistsError(OUT)
    if (RUN/'RUNNING.lock').exists():raise RuntimeError('Training still paused')
    if not json.loads((DEV/'REPORT.json').read_text())['acceptance_passed']:raise RuntimeError('Independent development failed')
    OUT.mkdir(parents=True)
    source=DEV/'source/receiver.py'
    if common.sha(source)!=common.sha(ROOT/'experiments/lstmp_message_damping_candidate_20261019/receiver.py'):raise RuntimeError('Candidate changed')
    spec=importlib.util.spec_from_file_location('frozen_message_receiver',source);candidate=importlib.util.module_from_spec(spec);spec.loader.exec_module(candidate)
    jobs=[dict(group='balanced',seed=202610201800001+i,condition=data.condition_for('validation',i)) for i in range(144)]
    jobs += [dict(group='stress',seed=202610201900001+i,condition=dict(users=100,frames=8,activity_probability=.1,snr_db=10)) for i in range(144)]
    plan=dict(candidate_sha256=common.sha(source),jobs=jobs,weights='Trained depth-2 last checkpoint; deeper layers initialized from the same completed 50000 score, deterministic original initialization seeds.',
        checks=['Full original 1200-case validation for epoch-0 versus epoch-2 with the same repaired forward. No intermediate checkpoint selection.',
                'Fresh 288-case bank at depths 2,3,5. Only depths 1-2 are trained. Deeper checks concern numerical stability, not accuracy claims.',
                'Frozen full-model backward on one predeclared fresh stress case at depth 5, original execution policy; no optimizer updates.'],
        stability=dict(finite_all=True,maximum_scene_nmse_linear=10.),gradient='Every trainable parameter has a finite gradient when connected; prior layer calibration gradients must be nonzero. Last beta is intentionally disconnected.',
        budget=dict(scene_count=4800,epoch_schedule=[2,2,2,2,4],completed_steps=19200,remaining_steps=38400,hard_time_budget_hours=12))
    common.save_json(OUT/'PLAN.json',plan)
    torch.set_num_threads(4);threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32=True;torch.backends.cudnn.allow_tf32=True;torch.backends.cudnn.benchmark=True
    scale=common.CONFIG['pretrained_score']['global_complex_rms'];start=time.time()
    saved=torch.load(RUN/'checkpoints/depth_2/last.pt',map_location='cpu',weights_only=False)
    for name,checkpoint in [('epoch0','best.pt'),('epoch2','last.pt')]:
        model=candidate.Receiver()
        for _ in range(2):model.add_layer(None)
        state=torch.load(RUN/'checkpoints/depth_2'/checkpoint,map_location='cpu',weights_only=False)
        model.load_state_dict(state['state']);model.cuda().eval();model.use_checkpoint=False;del state
        def progress(rows):
            if len(rows)%120==0:
                common.save_json(OUT/'STATUS.json',dict(stage='FULL_VALIDATION',checkpoint=name,scenes=len(rows),elapsed_seconds=time.time()-start))
                print(json.dumps(dict(checkpoint=name,scenes=len(rows))),flush=True)
        result=receiver.evaluate(model,data.Cases('validation',scale,'cuda'),on_row=progress)
        common.save_json(OUT/f'{name}_validation.json',result)
        del model;torch.cuda.empty_cache()
    pretrained=torch.load(ROOT/common.CONFIG['pretrained_score']['path'],map_location='cpu',weights_only=False)['state_dict']
    model=candidate.Receiver()
    for _ in range(2):model.add_layer(None)
    model.load_state_dict(saved['state']);del saved
    rows={str(d):[] for d in [2,3,5]}
    for depth in [2,3,5]:
        while len(model.layers)<depth:
            torch.manual_seed(common.CONFIG['seed']+len(model.layers)+1)
            model.add_layer(pretrained)
        model.cuda().eval();model.use_checkpoint=False
        with torch.no_grad():
            for i,job in enumerate(jobs):
                public,labels=make_case(job['seed'],job['condition'],scale)
                outputs,diagnostics=model(public)
                row=dict(**job,**receiver.metrics(outputs,labels),loss=float(receiver.loss(outputs,labels)),diagnostics=diagnostics)
                row['finite']=math.isfinite(row['loss']) and math.isfinite(row['nmse'])
                rows[str(depth)].append(row)
                if (i+1)%72==0:print(json.dumps(dict(development_depth=depth,scenes=i+1)),flush=True)
        common.save_json(OUT/'DEEP_INITIALIZATION.json',rows)
    # Check the exact selective recomputation settings used by the original run.
    model.checkpoint_first_layers=1;model.checkpoint_min_users=100;model.use_checkpoint=False
    model.train();torch.cuda.empty_cache();torch.cuda.reset_peak_memory_stats()
    public,labels=make_case(jobs[-1]['seed'],jobs[-1]['condition'],scale)
    before=common.cpu_state(model)
    outputs,diagnostics=model(public);value=receiver.loss(outputs,labels);value.backward()
    gradients=[]
    for i,layer in enumerate(model.layers):
        gradients.append(dict(layer=i+1,calibration_gradient=layer.calibration.grad.detach().cpu().tolist(),
            score_finite=all(p.grad is None or bool(torch.isfinite(p.grad).all()) for p in layer.score.parameters()),
            activity_finite=all(p.grad is None or bool(torch.isfinite(p.grad).all()) for p in layer.activity.parameters()),
            score_has_nonzero=any(p.grad is not None and bool(p.grad.abs().max()>0) for p in layer.score.parameters()),
            activity_has_nonzero=any(p.grad is not None and bool(p.grad.abs().max()>0) for p in layer.activity.parameters())))
    unchanged=all(torch.equal(before[k],v.detach().cpu()) for k,v in model.state_dict().items())
    gradient_ok=unchanged and all(g['score_finite'] and g['activity_finite'] and g['score_has_nonzero'] and g['activity_has_nonzero'] and all(math.isfinite(v) for v in g['calibration_gradient']) for g in gradients)
    gradient_ok=gradient_ok and all(all(v!=0 for v in g['calibration_gradient']) for g in gradients[:-1]) and gradients[-1]['calibration_gradient'][2]==0
    deep={d:dict(maximum_nmse=max(r['nmse'] for r in rr),finite=all(r['finite'] for r in rr),summary=receiver.summarize_rows(rr)) for d,rr in rows.items()}
    initial=json.loads((OUT/'epoch0_validation.json').read_text())['summary'];trained=json.loads((OUT/'epoch2_validation.json').read_text())['summary']
    passed=gradient_ok and trained['loss']<initial['loss'] and all(v['finite'] and v['maximum_nmse']<=10 for v in deep.values())
    report=dict(status='COMPLETE',candidate_sha256=common.sha(source),validation=dict(initial=initial,trained=trained),
        deeper_initialization=deep,gradient_check=dict(passed=gradient_ok,weights_unchanged=unchanged,loss=float(value.detach()),layers=gradients,
            peak_allocated_bytes=torch.cuda.max_memory_allocated(),peak_reserved_bytes=torch.cuda.max_memory_reserved()),
        optimizer_updates=0,acceptance_passed=passed,elapsed_seconds=time.time()-start)
    common.save_json(OUT/'REPORT.json',report)
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
