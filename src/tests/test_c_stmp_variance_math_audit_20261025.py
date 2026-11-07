"""Independent algebraic checks; these do not assert neural-receiver convergence."""
import numpy as np
from scipy.optimize import minimize_scalar
from algorithm.C_STMP_variance_em_20261025.iterations import expected_residual_power
from algorithm.STMP.gaussian import gaussian_extrinsic, inverse, spatial_apply


def test_complex_likelihood_and_real_two_coordinate_likelihood_agree():
    rng=np.random.default_rng(81)
    residual=rng.normal(size=13)+1j*rng.normal(size=13)
    power=np.vdot(residual,residual).real
    for v in [.03,.5,4.]:
        complex_log=-13*np.log(np.pi*v)-power/v
        real_log=-26/2*np.log(2*np.pi*v/2)-power/(2*(v/2))
        np.testing.assert_allclose(complex_log,real_log,rtol=1e-15)


def test_target_is_unique_optimizer_of_fixed_gaussian_expected_log_likelihood():
    rng=np.random.default_rng(82)
    r=rng.normal(size=(3,2,4,5))+1j*rng.normal(size=(3,2,4,5))
    m=.25*r
    cov=np.broadcast_to(.6*np.eye(2),(3,2,2))
    target,_,_=expected_residual_power(r,m,cov)
    # Numerical optimization in log variance, independent of the closed-form argmax.
    solution=minimize_scalar(lambda u: u+target*np.exp(-u),bounds=(-10,10),
                             method='bounded',options={'xatol':1e-11})
    np.testing.assert_allclose(np.exp(solution.x),target,rtol=1e-7)


def test_scale_and_complex_coordinate_count():
    rng=np.random.default_rng(83)
    r=rng.normal(size=(2,3,4,5))+1j*rng.normal(size=(2,3,4,5))
    m=.3*r
    cov=np.broadcast_to(.7*np.eye(3),(2,3,3))
    target,*_=expected_residual_power(r,m,cov)
    for scale in [.02,.2647966452702405,7.]:
        scaled,*_=expected_residual_power(scale*r,scale*m,scale**2*cov)
        np.testing.assert_allclose(scaled,scale**2*target,rtol=3e-15)
    total_trace=4*5*np.trace(cov,axis1=1,axis2=2).real.sum()
    np.testing.assert_allclose(target,(np.sum(abs(r-m)**2)+total_trace)/r.size,rtol=2e-15)


def test_exact_gaussian_special_case_increases_marginal_likelihood():
    rng=np.random.default_rng(84)
    r=rng.normal(size=(2,3,4,5))+1j*rng.normal(size=(2,3,4,5))
    r*=np.sqrt(3.7/np.mean(abs(r)**2))
    prior=.9
    for initial in [.1,20.]:
        v=initial
        old=-np.log(prior+v)-3.7/(prior+v)
        for _ in range(350):
            mean=prior/(prior+v)*r
            cov=np.broadcast_to(prior*v/(prior+v)*np.eye(3),(2,3,3))
            target,*_=expected_residual_power(r,mean,cov)
            v=.6*v+.4*target
            new=-np.log(prior+v)-3.7/(prior+v)
            assert new >= old-2e-14
            old=new
        np.testing.assert_allclose(v,3.7-prior,rtol=1e-11)


def test_extrinsic_natural_parameters_with_and_without_covariance_projection():
    rng=np.random.default_rng(85)
    mean=rng.normal(size=(2,2,3,4))+1j*rng.normal(size=(2,2,3,4))
    query=.6*mean+1
    v=1.7
    for eigenvalues in [[.2,.6],[.2,2.8]]:
        post=np.diag(eigenvalues)
        out,out_cov,raw,used=gaussian_extrinsic(mean,post,query,v*np.eye(2),floor=1e-5,ceiling=.99)
        projected=np.diag(np.clip(np.asarray(eigenvalues)/v,1e-5,.99)*v)
        np.testing.assert_allclose(inverse(out_cov)+np.eye(2)/v,inverse(projected),rtol=3e-14,atol=3e-14)
        np.testing.assert_allclose(spatial_apply(inverse(out_cov),out)+query/v,
                                   spatial_apply(inverse(projected),mean),rtol=3e-14,atol=3e-14)
        assert np.all(used>0) and np.all(used<1)
        if eigenvalues[-1]>v:
            assert not np.allclose(projected,post)


def test_ratio_damping_ascends_only_the_frozen_local_objective():
    beta=.4
    for v in np.logspace(-4,3,15):
        for target in np.logspace(-4,3,15):
            raw=.7
            ratio=v/raw
            updated_ratio=(1-beta)*ratio+beta*target/raw
            virtual=raw*updated_ratio
            np.testing.assert_allclose(virtual,(1-beta)*v+beta*target,rtol=3e-15)
            q=lambda x:-np.log(x)-target/x
            assert q(virtual)>=q(v)-1e-12*max(1,abs(q(v)))
    # A changing next linear variance can undo this one-dimensional ascent.
    q=lambda v:-np.log(v)-2/v
    assert q(1.4)>q(1.)
    assert q(10*1.4)<q(1.)
