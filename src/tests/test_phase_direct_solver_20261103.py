"""Independent checks of the constrained phase M step."""
import numpy as np
from algorithm.C_STMP_phase_direct_20261103.phase import rotations
from algorithm.proposed.phase_math import quadratic_objective


def test_single_user_global_coordinate_matches_dense_reference():
    rng=np.random.default_rng(32)
    q=7
    b=rng.normal(size=(q,1))+1j*rng.normal(size=(q,1))
    g=np.ones((q,1,1),complex)*2
    beta,angle,record=rotations(np.array([1.2]),g,b,sweeps=1)
    grid=np.linspace(-np.pi,np.pi,100001)
    reference=np.real(np.exp(-1j*grid[:,None]*np.arange(q))@b[:,0]).max()
    actual=np.real(np.exp(-1j*beta[0]*np.arange(q))@b[:,0])
    assert actual >= reference-1e-9
    np.testing.assert_array_equal(angle,np.zeros(1))


def test_random_multidevice_quadratic_decreases():
    rng=np.random.default_rng(20261103)
    for offset in (False,True):
        q,k=8,4
        a=rng.normal(size=(q,k,k))+1j*rng.normal(size=(q,k,k))
        g=np.einsum('qji,qjl->qil',a.conj(),a)
        b=rng.normal(size=(q,k))+1j*rng.normal(size=(q,k))
        initial=rng.uniform(-np.pi,np.pi,k)
        beta,angle,record=rotations(initial,g,b,sweeps=2,fit_offset=offset)
        old=np.exp(1j*np.arange(q)[:,None]*initial)
        new=np.exp(1j*(np.arange(q)[:,None]*beta+angle))
        assert quadratic_objective(new,g,b)<=quadratic_objective(old,g,b)+1e-9
        assert np.max(np.diff(record['objectives']))<=1e-9


def test_zero_information_keeps_phase():
    initial=np.array([.8,-2.1])
    beta,angle,_=rotations(initial,np.zeros((5,2,2)),np.zeros((5,2)),sweeps=1)
    np.testing.assert_allclose(beta,initial,atol=1e-14)
