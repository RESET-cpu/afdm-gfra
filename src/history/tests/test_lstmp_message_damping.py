"""Independent Gaussian density and derivative checks for the candidate."""
import torch
from experiments.lstmp_message_damping_candidate_20261019.receiver import damp_gaussian


def test_damped_density_matches_weighted_log_densities_up_to_constant():
    old=torch.tensor([1.,-2.],dtype=torch.float64)
    new=torch.tensor([3.,4.],dtype=torch.float64)
    v0=torch.tensor(.2,dtype=torch.float64);v1=torch.tensor(2.,dtype=torch.float64)
    ref=torch.tensor(.1,dtype=torch.float64)
    mean,var,amount=damp_gaussian(old,v0,new,v1,ref)
    points=torch.tensor([[0.,0.],[2.,-1.],[-3.,4.]],dtype=torch.float64)
    lhs=-(points-mean).square().sum(1)/(2*var)
    rhs=-(1-amount)*(points-old).square().sum(1)/(2*v0)-amount*(points-new).square().sum(1)/(2*v1)
    torch.testing.assert_close(lhs-lhs[0],rhs-rhs[0],rtol=1e-12,atol=1e-12)


def test_full_update_is_bitwise_unchanged():
    old=torch.ones(2);new=torch.tensor([-2.,3.]);v=torch.tensor(.02)
    mean,var,amount=damp_gaussian(old,torch.tensor(.1),new,v,torch.tensor(.1))
    assert amount==1 and torch.equal(mean,new) and torch.equal(var,v)


def test_damping_preserves_finite_gradients_and_positive_variance():
    args=(torch.tensor([1.,-2.],dtype=torch.float64,requires_grad=True),
          torch.tensor(.2,dtype=torch.float64,requires_grad=True),
          torch.tensor([3.,4.],dtype=torch.float64,requires_grad=True),
          torch.tensor(2.,dtype=torch.float64,requires_grad=True),
          torch.tensor(.1,dtype=torch.float64))
    assert torch.autograd.gradcheck(lambda *values:damp_gaussian(*values)[:2],args)
    for scale in [1e-8,1e-3,1.,1e3,1e8]:
        mean,var,amount=damp_gaussian(args[0],args[1],args[2],torch.tensor(scale,dtype=torch.float64),args[4])
        assert torch.isfinite(mean).all() and torch.isfinite(var) and var>0 and 0<amount<=1
