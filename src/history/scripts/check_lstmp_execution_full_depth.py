"""Discarded five-layer memory and gradient check at the declared maximum K."""
import gc
import json
import time
import benchmark_lstmp_training_execution as B
import torch
from threadpoolctl import threadpool_limits


def main():
    assert not (B.RUN/'RUNNING.lock').exists()
    torch.set_num_threads(4);threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32=True
    torch.backends.cudnn.allow_tf32=True
    torch.backends.cudnn.benchmark=True
    saved=torch.load(B.RUN/'checkpoints/depth_2/last.pt',map_location='cpu',weights_only=False)
    first=torch.load(B.ROOT/B.common.CONFIG['pretrained_score']['path'],map_location='cpu',weights_only=False)
    cases=B.data.Cases('train',first['global_complex_rms'],'cuda')
    positions=[next(i for i,p in enumerate(cases.indices) if p%24==j) for j in (0,4,8,12,16,20)]
    fixed=[cases[i] for i in positions]
    results={}
    for name,checkpoint,fused in [('reference',True,False),('no_recomputation_fused_adam',False,True)]:
        torch.manual_seed(B.common.CONFIG['seed']+5)
        model=B.receiver.Receiver()
        for _ in range(5):model.add_layer(first['state_dict'])
        model.load_state_dict(saved['state'],strict=False)
        model.cuda().train();model.use_checkpoint=checkpoint
        s=B.common.CONFIG['receiver']
        optimizer=torch.optim.Adam([
            dict(params=[p for layer in model.layers for p in layer.score.parameters() if p.requires_grad],lr=s['learning_rate']),
            dict(params=[p for layer in model.layers for p in layer.activity.parameters() if p.requires_grad],lr=s['activity_learning_rate']),
            dict(params=[layer.calibration for layer in model.layers],lr=s['calibration_learning_rate'])],foreach=False,fused=fused)
        torch.cuda.reset_peak_memory_stats()
        try:
            warmup=[B.step(model,optimizer,case) for case in fixed]
            rows=[dict(users=case[2]['users'],frames=case[2]['frames'],**B.step(model,optimizer,case)) for case in fixed]
            free,total=torch.cuda.mem_get_info()
            results[name]=dict(depth=5,maximum_users=100,all_losses_and_gradients_finite=True,
                mean_seconds=sum(row['seconds'] for row in rows)/len(rows),rows=rows,
                peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,
                peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30,
                device_free_gib_after_steps=free/2**30,device_total_gib=total/2**30,
                scope='Layers 1-2 use current checkpoint; layers 3-5 use declared initialization. Capacity/execution check, not trained model accuracy.')
        except torch.OutOfMemoryError as error:
            results[name]=dict(out_of_memory=True,error=str(error))
        print(json.dumps(dict(variant=name,**results[name])),flush=True)
        B.common.save_json(B.OUT/'FULL_DEPTH_CAPACITY.json',dict(weights_discarded=True,results=results))
        del model,optimizer;gc.collect();torch.cuda.empty_cache()


if __name__=='__main__':main()
