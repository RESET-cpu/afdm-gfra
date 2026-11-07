"""Synthetic algebra/complex-coordinate checks, not channel performance."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import numpy as np
import validate_receiver_covariance as audit
from receiver_covariance_candidates import receiver_candidates,second_moment


def main():
    rng=np.random.default_rng(202610196000001)
    complex_normal=lambda shape:(rng.standard_normal(shape)+1j*rng.standard_normal(shape))/np.sqrt(2)
    k,m,q,p,n=5,16,8,16,4
    a=complex_normal((q,k*p))/np.sqrt(p)
    b=complex_normal((m,3));cx=b@b.conj().T/m+.2*np.eye(m)
    noise=.7;gamma=.12;power=np.linalg.norm(a)**2/q
    cy=power*cx+noise*np.eye(m)
    eig,u=np.linalg.eigh(cy);root=(u*np.sqrt(eig))@u.conj().T
    z=complex_normal((m,q*n));val,vec=np.linalg.eigh(z@z.conj().T/(q*n))
    z=((vec/np.sqrt(val))@vec.conj().T)@z
    y=(root@z).reshape(m,q,n).transpose(1,0,2)
    gain=gamma*a.conj().T@np.linalg.inv(noise*np.eye(q)+gamma*a@a.conj().T)
    w=gain/(np.trace(a@gain).real/(k*p))
    query=(w@y.reshape(q,-1)).reshape(k,p,m,n).transpose(0,2,3,1)
    kwargs=dict(nominal_variance=2.,observation=y,operator=a.reshape(q,k,p),noise=noise,
        activity_prior=.1,initial_power=gamma/.1,iteration=1)
    mean=complex_normal(query.shape)*.1
    post=np.broadcast_to(.03*np.eye(m),(k,m,m)).copy()
    estimated,selection=receiver_candidates(query,mean=mean,posterior_covariance=post,**kwargs)
    response=w@a-np.eye(k*p)
    expected=np.linalg.norm(response)**2/(k*p)*cx+noise*np.linalg.norm(w)**2/(k*p)*np.eye(m)
    relative=lambda x,y:float(np.linalg.norm(x-y)/np.linalg.norm(y))
    propagation_error=relative(estimated['first_linear_propagation'],expected)
    assert propagation_error<1e-11
    rotation,_=np.linalg.qr(complex_normal((m,m)))
    transform=lambda x:np.einsum('ab,kbrc->karc',rotation,x,optimize=False)
    rotated_kwargs=dict(kwargs,observation=np.einsum('ab,qbr->qar',rotation,y,optimize=False))
    rotated,selection2=receiver_candidates(transform(query),mean=transform(mean),
        posterior_covariance=np.einsum('ab,kbc,dc->kad',rotation,post,rotation.conj(),optimize=False),**rotated_kwargs)
    rotation_errors={name:relative(rotated[name],rotation@cov@rotation.conj().T) for name,cov in estimated.items()}
    assert np.array_equal(selection,selection2)
    assert max(rotation_errors.values())<1e-11
    result=dict(passed=True,synthetic_only=True,population_observation_covariance_error=relative(second_moment(y),cy),
        explicit_linear_covariance_propagation_error=propagation_error,unitary_rotation_errors=rotation_errors,
        lower_energy_selection_rotation_invariant=True,
        interpretation='Checks conjugation, antenna axes and a population identity under independent input-row assumptions. Does not establish those assumptions in actual AFDM messages.')
    audit.P.save(audit.OUT/'ALGEBRA_CHECK.json',result)
    print(result,flush=True)


if __name__=='__main__':main()
