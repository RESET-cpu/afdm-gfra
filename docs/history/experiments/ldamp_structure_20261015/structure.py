"""Rank-one approximation of each estimated spatial unfolding and its real JVP.

Uses only estimated channels. The physical zero-direction-spread model motivates
this restriction but does not make it an optimal posterior mean. See
Gavish–Donoho, arXiv:1405.7511v3, Sec.1, TSVD following Eq.(2).
"""
import numpy as np


def linearize_rank_one(value):
    value=np.asarray(value,np.complex128)
    shape=value.shape
    if value.ndim!=4:
        raise ValueError('Expected [user, antenna, output, input]')
    h=value.reshape(shape[0],shape[1],-1)
    gram=np.einsum('kic,kjc->kij',h,h.conj(),optimize=False)
    eigenvalues,vectors=np.linalg.eigh(gram)
    u=vectors[:,:,-1];others=vectors[:,:,:-1]
    gaps=eigenvalues[:,-1,None]-eigenvalues[:,:-1]
    zeros=np.max(abs(h),axis=(1,2))==0
    # At zero choose zero JVP by convention; the rank-one map is not Frechet
    # differentiable there. Nonzero repeated leading eigenvalues are rejected.
    bad=(gaps[:,-1] <= 1e-12*np.maximum(eigenvalues[:,-1],np.finfo(float).tiny)) & ~zeros
    if np.any(bad):raise FloatingPointError('Nondifferentiable repeated leading singular value')
    safe=np.where(zeros[:,None],1.,gaps)
    row=np.einsum('ki,kic->kc',u.conj(),h,optimize=False)
    output=u[:,:,None]*row[:,None,:]
    output[zeros]=0
    def directions(delta):
        delta=np.asarray(delta,np.complex128)
        if delta.ndim!=5 or delta.shape[1:]!=shape:raise ValueError('Invalid direction shape')
        d=delta.reshape(len(delta),*h.shape)
        dc=np.einsum('pkic,kjc->pkij',d,h.conj(),optimize=False)+np.einsum('kic,pkjc->pkij',h,d.conj(),optimize=False)
        g=np.einsum('pkij,kj->pki',dc,u,optimize=False)
        weights=np.einsum('kij,pki->pkj',others.conj(),g,optimize=False)/safe[None]
        du=np.einsum('kij,pkj->pki',others,weights,optimize=False)
        left=np.einsum('ki,pkic->pkc',u.conj(),d,optimize=False)
        right=np.einsum('pki,kic->pkc',du.conj(),h,optimize=False)
        result=u[None,:,:,None]*(left+right)[:,:,None,:]+du[:,:,:,None]*row[None,:,None,:]
        result[:,zeros]=0
        return result.reshape(delta.shape)
    return output.reshape(shape),directions


def rank_one(value):
    return linearize_rank_one(value)[0]


class StructuredDenoiser:
    """Composition P(D(R)); includes both terms in the projection derivative."""
    def __init__(self,base):
        self.base=base;self.scale=base.scale
    def linearize(self,query,covariance):
        value,base_direction=self.base.linearize(query,covariance)
        result,projection_direction=linearize_rank_one(value)
        def directions(delta):return projection_direction(base_direction(delta))
        return result,directions
