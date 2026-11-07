"""Check maximum-depth capacity with the first score selectively recomputed."""
import importlib.util
import json
import benchmark_lstmp_training_execution as B
import torch
from threadpoolctl import threadpool_limits


def main():
    modules={}
    for name in ('receiver','execution'):
        spec=importlib.util.spec_from_file_location('experiments.lstmp_candidate_20261019.'+name+'_performance',B.ROOT/'experiments/lstmp_candidate_20261019'/f'{name}.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        modules[name]=module
    assert not (B.RUN/'RUNNING.lock').exists()
    torch.set_num_threads(4);threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32=True;torch.backends.cudnn.allow_tf32=True;torch.backends.cudnn.benchmark=True
    saved=torch.load(B.RUN/'checkpoints/depth_2/last.pt',map_location='cpu',weights_only=False)
    first=torch.load(B.ROOT/B.common.CONFIG['pretrained_score']['path'],map_location='cpu',weights_only=False)
    cases=B.data.Cases('train',first['global_complex_rms'],'cuda')
    fixed=[cases[next(i for i,p in enumerate(cases.indices) if p%24==j)] for j in (0,4,8,12,16,20)]
    torch.manual_seed(B.common.CONFIG['seed']+5)
    model=modules['receiver'].Receiver()
    for _ in range(5):model.add_layer(first['state_dict'])
    model.load_state_dict(saved['state'],strict=False);model.cuda().train()
    s=B.common.CONFIG['receiver']
    optimizer=torch.optim.Adam([
        dict(params=[p for layer in model.layers for p in layer.score.parameters() if p.requires_grad],lr=s['learning_rate']),
        dict(params=[p for layer in model.layers for p in layer.activity.parameters() if p.requires_grad],lr=s['activity_learning_rate']),
        dict(params=[layer.calibration for layer in model.layers],lr=s['calibration_learning_rate'])],foreach=False)
    settings=dict(activation_checkpointing=False,adam_implementation='fused',
        selective_checkpoint=dict(minimum_depth=5,minimum_users=100,first_layers=1))
    modules['execution'].configure_execution(model,optimizer,settings,'cuda')
    torch.cuda.reset_peak_memory_stats()
    for case in fixed:B.step(model,optimizer,case)
    rows=[dict(users=case[2]['users'],frames=case[2]['frames'],**B.step(model,optimizer,case)) for case in fixed]
    free,total=torch.cuda.mem_get_info()
    report=dict(settings=settings,weights_discarded=True,depth=5,maximum_users=100,
        mean_seconds=sum(r['seconds'] for r in rows)/len(rows),
        peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,
        peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30,
        device_free_gib_after_steps=free/2**30,rows=rows,
        memory_margin_passed=free>2**30,
        scope='Execution and memory only; later layers have not been trained')
    B.common.save_json(B.OUT/'SELECTIVE_FULL_DEPTH_CAPACITY.json',report)
    print(json.dumps(report),flush=True)
    assert report['memory_margin_passed']


if __name__=='__main__':main()
