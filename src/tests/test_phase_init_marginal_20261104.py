"""Check complex multi-column marginal algebra and physical gradients."""
import numpy as np
import pytest
from scipy.optimize import minimize_scalar
from receiver.gp_mp import initialization as init
from channel.phase_atoms import sensed_atom


@pytest.mark.parametrize('seed',[2,19,53])
def test_rank_one_marginal_and_profiled_power_match_dense(seed):
    rng=np.random.default_rng(seed)
    a=rng.normal(size=(9,4))+1j*rng.normal(size=(9,4))
    powers=np.array([0.,.3,1.2,.1]);noise=.7
    y=rng.normal(size=(9,3))+1j*rng.normal(size=(9,3))
    inverse,logdet=init.inverse_covariance(a,powers,noise)
    c=noise*np.eye(9)+(a*powers)@a.conj().T
    np.testing.assert_allclose(inverse,np.linalg.inv(c),rtol=1e-12,atol=1e-12)
    np.testing.assert_allclose(logdet,np.linalg.slogdet(c)[1],rtol=1e-12)
    atom=a[:,0];s,t=init.statistics(atom,inverse,inverse@y)
    optimum=init.optimum_power(s,t,3)
    for p in [0.,.14,.8,optimum]:
        new=c+p*np.outer(atom,atom.conj())
        direct=np.linalg.slogdet(new)[1]+np.vdot(y,np.linalg.solve(new,y)).real/3
        baseline=logdet+np.vdot(y,inverse@y).real/3
        np.testing.assert_allclose(direct-baseline,init.coordinate_value(p,s,t,3),rtol=1e-10,atol=1e-12)
    fit=minimize_scalar(lambda p:init.coordinate_value(p,s,t,3),bounds=(0.,max(2.,2*optimum)),method='bounded')
    assert init.coordinate_value(optimum,s,t,3)<=fit.fun+1e-9


def test_noise_only_power_and_arbitrary_column_count():
    for m in (1,3,16):
        assert init.optimum_power(2.,m*2.,m)==0
        assert init.optimum_power(2.,m*1.,m)==0
        np.testing.assert_allclose(init.optimum_power(2.,m*6.,m),1.)


def test_atom_gradient_in_correlated_complex_background():
    rng=np.random.default_rng(31)
    pilot=(rng.normal(size=(4,2,16))+1j*rng.normal(size=(4,2,16)))/np.sqrt(32)
    b=rng.normal(size=(64,3))+1j*rng.normal(size=(64,3))
    inverse,_=init.inverse_covariance(b,np.array([.05,.08,.1]),.9)
    y=rng.normal(size=(64,5))+1j*rng.normal(size=(64,5));solved=inverse@y
    x=np.array([3.232,.231])
    value,gradient=init.objective(x,pilot,1,inverse,solved)
    for j in range(2):
        delta=np.eye(2)[j]*1e-7
        numeric=(init.objective(x+delta,pilot,1,inverse,solved)[0]-init.objective(x-delta,pilot,1,inverse,solved)[0])/2e-7
        np.testing.assert_allclose(gradient[j],numeric,rtol=3e-5,atol=1e-6)


def test_white_covariance_alias_ranking_matches_original_matched_filter():
    rng=np.random.default_rng(12)
    pilot=(rng.normal(size=(4,2,16))+1j*rng.normal(size=(4,2,16)))/np.sqrt(32)
    y=rng.normal(size=(64,3))+1j*rng.normal(size=(64,3));noise=.3
    for position in [np.array([2.31,-.43]),np.array([6.22,.16])]:
        atom=sensed_atom(pilot,0,position)
        s,t=init.statistics(atom,np.eye(64)/noise,y/noise)
        expected=np.linalg.norm(atom.conj()@y)**2/(np.vdot(atom,atom).real*noise)
        np.testing.assert_allclose(t/s,expected,rtol=1e-12)


def test_reject_invalid_covariance():
    with pytest.raises(ValueError):init.inverse_covariance(np.ones((3,2)),np.array([1.,-1.]),1.)
