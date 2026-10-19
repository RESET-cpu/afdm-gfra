"""Meaningful numerical and gradient checks before launching fresh training."""
import json, time, copy, io
import numpy as np
import torch
from threadpoolctl import threadpool_limits
from common import CONFIG, OUT, save_json, cpu_state
from data import pack, unpack, block
from backbone import FreshScore
from receiver import Receiver, linear_update, loss
from afdm_jadcedd.experiment.generate import generate_case


def main():
    torch.set_num_threads(1);threadpool_limits(1);torch.manual_seed(20261019)
    rng=np.random.default_rng(20261019)
    a=(rng.normal(size=(16,640))+1j*rng.normal(size=(16,640)))/np.sqrt(640)
    x=(rng.normal(size=(40,16,16,16))+1j*rng.normal(size=(40,16,16,16)))/np.sqrt(2)
    y=(rng.normal(size=(16,256))+1j*rng.normal(size=(16,256)))/np.sqrt(2)
    u,s,vh=np.linalg.svd(a,full_matrices=False)
    original_x=torch.tensor(np.stack((x.real,x.imag),axis=1),dtype=torch.float32)
    packed=pack(original_x)
    reference_x=x.transpose(0,3,1,2).reshape(640,256)
    packed_error=float(np.max(np.abs(packed.numpy()-np.concatenate((reference_x.real,reference_x.imag)))))
    assert torch.equal(unpack(packed),original_x)
    noise,pv=.7,.23
    inverse=np.linalg.solve(pv*(a@a.conj().T)+noise*np.eye(16),y-a@reference_x)
    expected=reference_x+pv*a.conj().T@inverse
    expected_variance=pv-pv**2*np.trace(np.linalg.solve(pv*a@a.conj().T+noise*np.eye(16),a@a.conj().T)).real/640
    public=dict(a=block(a,'cpu'),uh=block(u.conj().T,'cpu'),vv=block(vh.conj().T,'cpu'),
                s=torch.tensor(s,dtype=torch.float32),y=torch.tensor(np.concatenate((y.real,y.imag)),dtype=torch.float32),noise=noise,rho=.1)
    mean,variance=linear_update(public,original_x,torch.tensor(pv))
    mean_error=float(np.linalg.norm(pack(mean).numpy()-np.concatenate((expected.real,expected.imag)))/np.linalg.norm(expected))
    variance_error=abs(float(variance)-expected_variance)/expected_variance
    residual=public['y']-public['a']@pack(mean)
    torch_raw=float((residual.square().sum()-16*256*noise)/(256*public['a'].square().sum()/2))
    numpy_raw=(np.sum(abs(y-a@expected)**2)-16*256*noise)/(256*np.sum(abs(a)**2))
    residual_error=abs(torch_raw-numpy_raw)/max(1.,abs(numpy_raw))
    assert mean_error<3e-6 and variance_error<3e-6 and residual_error<3e-6

    timing={}
    state=cpu_state(FreshScore(width=CONFIG['width']))
    for device in ['cpu']+(['mps'] if torch.backends.mps.is_available() else []):
        score=FreshScore(width=CONFIG['width']).to(device);score.load_state_dict(state)
        sample=torch.randn(8,2,16,16,16,device=device);v=torch.ones(8,device=device)
        # warm and measure the real 32-sample batch with microbatch 8
        for _ in range(2):score(sample,v).square().mean().backward();score.zero_grad(set_to_none=True)
        if device=='mps':torch.mps.synchronize()
        started=time.monotonic()
        for _ in range(4):(score(sample,v).square().mean()/4).backward()
        if device=='mps':torch.mps.synchronize()
        timing[device]=time.monotonic()-started
        del score,sample,v
    device=CONFIG['device']
    # A physical held-out debug seed outside every registered train/validation/test range.
    inp,truth,_=generate_case(202610194900001,0.,1.)
    a=inp['operator'].reshape(16,640);u,s,vh=np.linalg.svd(a,full_matrices=False)
    y=inp['observation'].reshape(16,256)
    physical=dict(a=block(a,device),uh=block(u.conj().T,device),vv=block(vh.conj().T,device),
                  s=torch.tensor(s,dtype=torch.float32,device=device),y=torch.tensor(np.concatenate((y.real,y.imag)),dtype=torch.float32,device=device),
                  noise=float(inp['noise_variance']),rho=float(inp['activity_prior']))
    labels=dict(x=torch.tensor(np.stack((truth['channel'].real,truth['channel'].imag),axis=1),dtype=torch.float32,device=device),
                active=torch.tensor(truth['activity'],dtype=torch.float32,device=device))
    model=Receiver()
    for _ in range(CONFIG['receiver']['maximum_depth']):model.add_layer(state)
    model.to(device)
    ptrs=[set(p.data_ptr() for p in layer.parameters()) for layer in model.layers]
    assert all(not ptrs[i]&ptrs[j] for i in range(len(ptrs)) for j in range(i))
    physical_started=time.monotonic()
    outputs,diagnostics=model(physical);value=loss(outputs,labels);value.backward()
    physical_seconds=time.monotonic()-physical_started
    grads={}
    for i,layer in enumerate(model.layers):
        for name,module in [('score',layer.score),('activity',layer.activity)]:
            g=[p.grad for p in module.parameters() if p.grad is not None]
            assert g and all(bool(torch.isfinite(p).all()) for p in g)
            grads[f'layer{i+1}_{name}']=float(sum(p.square().sum() for p in g).sqrt())
            assert grads[f'layer{i+1}_{name}']>0
    assert all(d['feedback_variance']>0 and d['feedback_variance']<d['query_variance'] for d in diagnostics)
    assert bool(torch.isfinite(value))
    # Check optimizer state round-trip through CPU storage on the selected device.
    simple=torch.nn.Linear(3,2).to(device);opt=torch.optim.Adam(simple.parameters(),lr=.01)
    z=torch.ones(2,3,device=device)
    simple(z).square().mean().backward();opt.step();opt.zero_grad(set_to_none=True)
    state_m=cpu_state(simple)
    stream=io.BytesIO();torch.save(opt.state_dict(),stream);stream.seek(0)
    state_o=torch.load(stream,map_location='cpu',weights_only=False)
    simple(z).square().mean().backward();opt.step()
    restored=torch.nn.Linear(3,2).to(device);restored.load_state_dict(state_m)
    opt2=torch.optim.Adam(restored.parameters(),lr=.01);opt2.load_state_dict(state_o)
    restored(z).square().mean().backward();opt2.step()
    resume_error=max(float((p-q).abs().max()) for p,q in zip(simple.parameters(),restored.parameters()))
    assert resume_error<1e-7
    result=dict(status='PASS',packing_max_float32_error=packed_error,linear_mean_relative_error=mean_error,
                linear_variance_relative_error=variance_error,residual_variance_relative_error=residual_error,
                independent_layer_parameters=True,gradient_norms=grads,optimizer_resume_max_error=resume_error,
                batch32_microbatch8_forward_backward_seconds=timing,physical_diagnostics=diagnostics,
                five_layer_physical_forward_backward_seconds=physical_seconds,selected_device=device,
                finite_physical_loss=float(value.detach()),old_checkpoints_loaded=False,
                source_scope='debug seed only; no training/validation/test cases consumed')
    save_json(OUT/'PREFLIGHT.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
