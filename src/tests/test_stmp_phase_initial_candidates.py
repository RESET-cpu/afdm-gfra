"""Independent calculus and likelihood checks for finite initialization starts."""
import numpy as np
from algorithm.STMP.phase_initialization_candidates import maxima, coordinate
from algorithm.proposed.phase_math import observed_covariances


def normal(rng,shape):
    return (rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)


def test_stationary_maxima_include_positive_global_direction_without_grid_in_solver():
    rng=np.random.default_rng(7529)
    grid=np.linspace(-np.pi,np.pi,30001,endpoint=False)  # Independent test reference only.
    for _ in range(15):
        c=normal(rng,(7,));orders=np.arange(1,len(c))
        candidates=maxima(c,.37)
        grid_values=c[0].real+2*np.real(np.exp(-1j*grid[:,None]*orders)@c[1:])
        if grid_values.max()<=0:
            assert not candidates
            continue
        assert max(v for _,v in candidates)>=grid_values.max()-1e-8
        for angle,value in candidates:
            powers=np.exp(-1j*angle*orders)
            derivative=2*np.real(powers@(-1j*orders*c[1:]))
            second=-2*np.real(powers@(orders**2*c[1:]))
            assert value>0 and abs(derivative)<1e-7 and second<1e-7
    assert maxima(np.array([2.,0.,0.]),.37)==[(.37,2.)]
    assert maxima(np.array([-2.,0.,0.]),.37)==[]


def test_directional_polynomial_matches_finite_power_likelihood_derivative():
    rng=np.random.default_rng(993)
    q,r,n,m=5,2,3,7
    b=normal(rng,(q*r,n));gram=b@b.conj().T
    root=normal(rng,(q*r,q*r));base=.5*np.eye(q*r)+root@root.conj().T
    y=normal(rng,(q*r,m));sample=y@y.conj().T/m
    inverse=np.linalg.inv(base);weight=inverse-inverse@sample@inverse
    cross=np.sum(gram.conj().reshape(q,r,q,r)*(-weight).reshape(q,r,q,r),axis=(1,3))
    coefficients=np.array([np.trace(cross,offset=-lag) for lag in range(q)])
    frames=np.repeat(np.arange(q),r)
    def objective(covariance):
        return np.linalg.slogdet(covariance)[1]+np.trace(np.linalg.solve(covariance,sample)).real
    epsilon=1e-6
    for angle in (-2.7,-.3,.6,2.1):
        phi=np.exp(1j*frames*angle);g=gram*phi[:,None]*phi[None,:].conj()
        derivative=(objective(base+epsilon*g)-objective(base-epsilon*g))/(2*epsilon)
        gain=coefficients[0].real+2*np.real(np.exp(-1j*angle*np.arange(1,q))@coefficients[1:])
        np.testing.assert_allclose(gain,-derivative,rtol=2e-7,atol=2e-7)


def test_coordinate_updates_keep_finite_likelihood_nonincreasing():
    rng=np.random.default_rng(631)
    q,k,n,r,m=4,3,2,2,5
    pilot=normal(rng,(q,k,n));root=normal(rng,(r*n,r*n));moment=root@root.conj().T
    gram=observed_covariances(pilot,moment)
    frames=np.repeat(np.arange(q),r);y=normal(rng,(q*r,m));sample=y@y.conj().T/m
    beta,power,record=coordinate(gram,sample,.7,frames,.2,sweeps=2,local_maxiter=40)
    assert np.min(power)>=0 and np.max(np.diff(record['objective']))<=1e-8
    phi=np.exp(1j*beta[:,None]*frames)
    covariance=.7*np.eye(q*r)+np.einsum('k,kij->ij',power,gram*phi[:,:,None]*phi[:,None,:].conj())
    direct=np.linalg.slogdet(covariance)[1]+np.trace(np.linalg.solve(covariance,sample)).real
    np.testing.assert_allclose(record['objective'][-1],direct,rtol=1e-12,atol=1e-12)
    assert len(record['coordinates'])==2*k
    assert all(row['after']<=row['before']+1e-8 for row in record['coordinates'])
