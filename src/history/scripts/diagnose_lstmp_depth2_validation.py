"""Read-only re-evaluation of a failed depth-two stage on its existing validation bank."""
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
RUN=Path(r'D:\afdm-gfra-cpu\runs\lstmp_refinenet_50000_fast_20261019')
OUT=ROOT/'results/lstmp_depth2_validation_failure_20261019'
os.environ['AFDM_LSTMP_ROOT']=str(ROOT)
os.environ['AFDM_LSTMP_CONFIG']=str(RUN/'source_code/experiments/lstmp_candidate_20261019/reuse_50000_fast.json')
sys.path.insert(0,str(RUN/'source_code'))
import numpy as np
import torch
from threadpoolctl import threadpool_limits
from experiments.lstmp_candidate_20261019 import common,data,receiver


def main():
    if OUT.exists():raise FileExistsError(OUT)
    if (RUN/'RUNNING.lock').exists():raise RuntimeError('Training is still running')
    OUT.mkdir(parents=True)
    selected=RUN/'checkpoints/depth_2/last.pt'
    protected={str(p):common.sha(p) for p in [selected,RUN/'checkpoints/depth_2/best.pt',RUN/'checkpoints/depth_1/best.pt',RUN/'MANIFEST.json',ROOT/'MAINLINE.json']}
    common.save_json(OUT/'PLAN.json',dict(checkpoint=str(selected),protected=protected,optimizer_updates=0,
        scope='Existing 1200 validation scenes; not the reserved 20 test scenes. Diagnose failed depth-two completion without changing weights, settings, or budget.'))
    started=time.time()
    torch.set_num_threads(4);threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32=True;torch.backends.cudnn.allow_tf32=True;torch.backends.cudnn.benchmark=True
    saved=torch.load(selected,map_location='cpu',weights_only=False)
    model=receiver.Receiver()
    for _ in range(2):model.add_layer(None)
    model.load_state_dict(saved['state'])
    checkpoint_info={k:saved[k] for k in ('depth','epoch','cursor','steps','selected_epoch','best')}
    del saved
    model.cuda().eval();model.use_checkpoint=False
    calibration=[layer.calibration.detach().cpu().tolist() for layer in model.layers]
    cases=data.Cases('validation',common.CONFIG['pretrained_score']['global_complex_rms'],'cuda')
    def progress(rows):
        if len(rows)%64==0 or len(rows)==len(cases):
            status=dict(scenes=len(rows),total=len(cases),elapsed_seconds=time.time()-started)
            common.save_json(OUT/'STATUS.json',status);print(json.dumps(status),flush=True)
    evaluated=receiver.evaluate(model,cases,on_row=progress)
    common.save_json(OUT/'validation.json',evaluated)
    initial=json.loads((RUN/'checkpoints/depth_2/initial_validation.json').read_text())
    rows=evaluated['rows'];base=initial['rows']
    for i,(a,b) in enumerate(zip(rows,base)):
        if a['seed']!=b['seed']:raise ValueError('Validation identity mismatch')
    worst=sorted(rows,key=lambda r:r['loss'],reverse=True)
    total_loss=sum(r['loss'] for r in rows)
    report=dict(checkpoint=checkpoint_info,calibration=calibration,initial_summary=initial['summary'],
        final_summary=evaluated['summary'],initial_layers=initial['layer_summary'],final_layers=evaluated['layer_summary'],
        worst_conditions=sorted(evaluated['by_condition'],key=lambda r:r['loss'],reverse=True),
        loss_share_of_worst={str(n):sum(r['loss'] for r in worst[:n])/total_loss for n in (1,5,10,50,100)},
        nmse_quantiles={str(q):float(np.quantile([r['nmse'] for r in rows],q)) for q in (.5,.9,.95,.99,1.)},
        final_nmse_above_one=sum(r['nmse']>1 for r in rows),final_nmse_above_ten=sum(r['nmse']>10 for r in rows),
        scenes_better_nmse_than_initial=sum(a['nmse']<b['nmse'] for a,b in zip(rows,base)),
        worst_scenes=[{k:r[k] for k in ('case_index','seed','condition','snr','loss','nmse','diagnostics','layer_metrics') if k in r} for r in worst[:10]],
        elapsed_seconds=time.time()-started,optimizer_updates=0,
        protected_assets_preserved={p:common.sha(p)==digest for p,digest in protected.items()})
    if not all(report['protected_assets_preserved'].values()):raise RuntimeError('A protected file changed')
    common.save_json(OUT/'REPORT.json',report)
    common.save_json(OUT/'COMPLETE.json',dict(status='COMPLETE',optimizer_updates=0,scenes=len(rows),seconds=time.time()-started))
    print(json.dumps(dict(status='COMPLETE',scenes=len(rows),output=str(OUT))),flush=True)


if __name__=='__main__':main()
