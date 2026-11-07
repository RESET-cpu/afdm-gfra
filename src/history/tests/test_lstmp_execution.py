"""Changing Adam execution must retain the existing optimization trajectory."""
import copy
import pytest
import torch
from experiments.lstmp_candidate_20261019.execution import configure_execution


@pytest.mark.skipif(not torch.cuda.is_available(),reason='Paired fused Adam requires CUDA')
def test_fused_resume_preserves_moments_and_matches_next_adam_update():
    torch.manual_seed(71)
    model=torch.nn.Linear(9,5).cuda()
    optimizer=torch.optim.Adam(model.parameters(),lr=2e-5,foreach=False)
    x=torch.randn(13,9,device='cuda')
    for _ in range(4):
        optimizer.zero_grad(set_to_none=True)
        model(x).square().mean().backward();optimizer.step()
    paired=copy.deepcopy(model)
    fast=torch.optim.Adam(paired.parameters(),lr=2e-5,foreach=False)
    fast.load_state_dict(copy.deepcopy(optimizer.state_dict()))
    before=copy.deepcopy(fast.state_dict())
    configure_execution(paired,fast,dict(activation_checkpointing=False,adam_implementation='fused'),'cuda')
    assert not paired.use_checkpoint
    for key,state in fast.state_dict()['state'].items():
        for field in ('exp_avg','exp_avg_sq','step'):
            torch.testing.assert_close(state[field].cpu(),before['state'][key][field].cpu(),rtol=0,atol=0)
        assert state['step'].device.type=='cuda'
    for m,opt in ((model,optimizer),(paired,fast)):
        opt.zero_grad(set_to_none=True)
        m(x).square().mean().backward();opt.step()
    for original,accelerated in zip(model.parameters(),paired.parameters()):
        torch.testing.assert_close(original,accelerated,rtol=2e-6,atol=2e-7)
    assert all(int(state['step'])==5 for state in fast.state.values())
