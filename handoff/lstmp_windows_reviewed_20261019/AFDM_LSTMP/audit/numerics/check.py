"""Numerical checks only; never resume or change the saved training run."""
from pathlib import Path
import io
import json
import os
import sys
import numpy as np
import torch

BASE = Path(__file__).resolve().parents[2]
ROOT = BASE if (BASE/'run_windows.py').exists() else BASE/'AFDM_LSTMP'
os.environ['AFDM_LSTMP_ROOT'] = str(ROOT)
sys.path.insert(0, str(ROOT/'runs/lstmp_fresh_20261019/source_experiment'))
from common import CONFIG, cpu_state
from data import pack, unpack, block
from receiver import linear_update
from backbone import FreshScore
from threadpoolctl import threadpool_limits

torch.set_num_threads(1)
threadpool_limits(1)
torch.manual_seed(2026101907)
rng = np.random.default_rng(2026101907)
a = (rng.normal(size=(16,640))+1j*rng.normal(size=(16,640)))/np.sqrt(640)
x = (rng.normal(size=(40,16,16,16))+1j*rng.normal(size=(40,16,16,16)))/np.sqrt(2)
y = (rng.normal(size=(16,256))+1j*rng.normal(size=(16,256)))/np.sqrt(2)
u,s,vh = np.linalg.svd(a,full_matrices=False)
xt = torch.tensor(np.stack((x.real,x.imag),axis=1),dtype=torch.float32)
reference_x = x.transpose(0,3,1,2).reshape(640,256)
assert torch.equal(unpack(pack(xt)),xt)
# Independent contraction avoids relying on the same complex BLAS path as the code under test.
matmul=lambda left,right: np.einsum('ik,kj->ij',left,right,optimize=False)
aah=matmul(a,a.conj().T)
rows=[]
for prior,noise in ((1e-4,.01),(.2,.7),(10.,1e-4)):
    public=dict(a=block(a,'cpu'),uh=block(u.conj().T,'cpu'),vv=block(vh.conj().T,'cpu'),
                s=torch.tensor(s,dtype=torch.float32),
                y=torch.tensor(np.concatenate((y.real,y.imag)),dtype=torch.float32),noise=noise)
    inverse=np.linalg.solve(prior*aah+noise*np.eye(16),y-matmul(a,reference_x))
    expected=reference_x+prior*matmul(a.conj().T,inverse)
    expected_v=prior-prior**2*np.trace(np.linalg.solve(prior*aah+noise*np.eye(16),aah)).real/640
    mean,var=linear_update(public,xt,torch.tensor(prior))
    mean_error=np.linalg.norm(pack(mean).numpy()-np.concatenate((expected.real,expected.imag)))/np.linalg.norm(expected)
    variance_error=abs(float(var)-expected_v)/expected_v
    residual=public['y']-public['a']@pack(mean)
    raw=float((residual.square().sum()-16*256*noise)/(256*public['a'].square().sum()/2))
    raw_reference=(np.sum(abs(y-matmul(a,expected))**2)-16*256*noise)/(256*np.sum(abs(a)**2))
    residual_error=abs(raw-raw_reference)/max(1.,abs(raw_reference))
    assert max(mean_error,variance_error,residual_error)<3e-6
    rows.append(dict(prior_variance=prior,noise_variance=noise,
                     mean_relative_error=float(mean_error),variance_relative_error=float(variance_error),
                     residual_scaled_error=float(residual_error)))

# A known Gaussian real-coordinate prior gives an exact factor-of-two reference.
r=torch.randn(2,2,16,16,16,dtype=torch.float64)
tau,v=.3,1.7
score=-r/(tau+v/2)
mean=r+v/2*score
gaussian_error=float((mean-tau/(tau+v/2)*r).abs().max())
assert gaussian_error<2e-15

# Exercise a real NCSN++ Adam state across a serialization boundary in memory.
model=FreshScore(CONFIG['width'])
optimizer=torch.optim.Adam(model.parameters(),lr=2e-4)
sample=torch.randn(2,2,16,16,16)
variance=torch.tensor([.1,1.])
target=torch.randn_like(sample)
def step(net,opt):
    opt.zero_grad(set_to_none=True)
    objective=(net(sample,variance)-target).square().mean()
    objective.backward()
    torch.nn.utils.clip_grad_norm_(net.parameters(),1.,error_if_nonfinite=True)
    opt.step()
step(model,optimizer)
stream=io.BytesIO()
torch.save(dict(model=cpu_state(model),optimizer=optimizer.state_dict()),stream)
step(model,optimizer)
stream.seek(0)
state=torch.load(stream,map_location='cpu',weights_only=False)
restored=FreshScore(CONFIG['width']);restored.load_state_dict(state['model'])
resumed_optimizer=torch.optim.Adam(restored.parameters(),lr=2e-4)
resumed_optimizer.load_state_dict(state['optimizer'])
step(restored,resumed_optimizer)
resume_error=max(float((p-q).detach().abs().max()) for p,q in zip(model.parameters(),restored.parameters()))
assert resume_error==0.

report=dict(status='PASS',scope='Synthetic numerical and in-memory optimizer checks; no formal training/test scenes',
            linear_checks=rows,complex_to_real_tweedie_max_error=gaussian_error,
            ncsnpp_adam_resume_max_parameter_error=resume_error,formal_training_resumed=False)
(Path(__file__).parent/'RESULTS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
