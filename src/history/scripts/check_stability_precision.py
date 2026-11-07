"""Compare identical fresh development queries across CPU, CUDA FP32 and TF32."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import numpy as np
import torch
from threadpoolctl import threadpool_limits
import repair_stability_development as d
from benchmark_receiver_execution import GraphForward
from afdm_jadcedd.algorithm.proposed.receiver import Receiver
from afdm_jadcedd.algorithm.proposed.linear import SpatialLinear
from afdm_jadcedd.algorithm.baselines.noise_estimation import estimate_spatial_noise


def run():
    output=d.OUT/'PRECISION_AUDIT.json'
    if output.exists():
        raise ValueError('Preserve previous precision audit')
    config=d.paired.read(d.paired.MODEL)
    inputs,_,folder=d.bank('development',0,20)
    noise,_=estimate_spatial_noise(inputs.observation)
    linear=SpatialLinear(inputs.operator,16,noise/config['scale']**2)
    initial=inputs.activity_prior*config['initialization']['normalized_training_second_moment']
    _,_,r,cov=linear.update(inputs.observation/config['scale'],np.zeros((20,16,16,16),complex),np.eye(16)*initial)
    v=np.full(20,np.trace(cov).real/16)
    outputs={}
    torch.set_num_threads(1)
    for mode in ('cpu_fp32','cuda_fp32','cuda_fp32_graph','cuda_tf32_graph'):
        torch.backends.cudnn.allow_tf32=mode=='cuda_tf32_graph'
        torch.backends.cuda.matmul.allow_tf32=False
        model=Receiver(config,device='cpu' if mode=='cpu_fp32' else 'cuda')
        if mode.endswith('_graph'):
            model.model.first=GraphForward(model.model.first)
            model.model.second=GraphForward(model.model.second)
        a=model.model.infer(r,v)
        logits=model.evidence.infer(r,v,a.mean)
        outputs[mode]=dict(mean=a.mean,variance=a.variance,logits=logits)
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    comparisons={}
    for mode,value in outputs.items():
        comparisons[mode]={key:dict(relative_l2=float(np.linalg.norm(x-outputs['cpu_fp32'][key])/max(np.linalg.norm(outputs['cpu_fp32'][key]),1e-12)),
            max_absolute=float(np.max(abs(x-outputs['cpu_fp32'][key])))) for key,x in value.items()}
    exact_graph={key:bool(np.array_equal(outputs['cuda_fp32'][key],outputs['cuda_fp32_graph'][key])) for key in outputs['cpu_fp32']}
    passed=all(x['relative_l2']<1e-4 for x in comparisons['cuda_fp32_graph'].values()) and all(exact_graph.values())
    d.paired.save(output,dict(passed=passed,query_input_manifest_sha256=d.paired.sha(folder/'READY.json'),
        query_sha256=d.paired.array_sha256(r),variance=v[0],truth_used=False,
        cpu_reference='PyTorch float32 CPU convolutions; not exact arithmetic',
        full_fp32_relative_l2_tolerance=1e-4,comparisons=comparisons,graph_exact=exact_graph))
    print(comparisons,exact_graph,'PASSED',passed,flush=True)
    assert passed

if __name__=='__main__':
    with threadpool_limits(1):
        run()
