"""Complex matrix L-DAMP with exact CNN directions and a Monte Carlo partial trace.

B[a,b] = sum_i d D[i,b] / d q[i,a] / Q, with Wirtinger derivatives.
The residual correction is z @ B. Denoisers are independent across fixed beams,
so cross-beam Jacobian blocks are exactly zero. Structured AFDM pilots do not
satisfy the iid Gaussian assumptions of AMP state-evolution theory; performance
is checked empirically on disjoint physical scenes.
"""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Controls:
    iterations: int = 10
    probes: int = 8
    divergence_seed: int = 202610146201


def to_matrix(channel):
    k,m,r,n=channel.shape
    return channel.transpose(0,3,1,2).reshape(k*n,m*r)


def from_matrix(matrix,shape):
    k,m,r,n=shape
    return matrix.reshape(k,n,m,r).transpose(0,2,3,1)


def orthogonal_probe(rows,features,rng):
    """Unit-magnitude isotropic probes with U^H U = rows * I."""
    if features>rows:raise ValueError('Probe feature count exceeds sensed coordinates')
    frequencies=rng.permutation(rows)[:features]
    positions=rng.permutation(rows)
    phases=rng.uniform(0,2*np.pi,rows)[:,None]+rng.uniform(0,2*np.pi,features)[None,:]
    return np.exp(1j*(2*np.pi*positions[:,None]*frequencies[None,:]/rows+phases))


def partial_trace(directional_derivative,*,rows,features,measurements,group_size,rng,probes):
    """Average U^H [D'(U) - i D'(iU)] / (2Q) within independent groups.

    Grouping is valid only for structurally independent denoiser groups. The
    two real directions cancel the conjugate derivative for each probe. The
    CNN directions are exact chain-rule evaluations; the trace is stochastic.
    """
    if probes<1 or group_size<1 or features%group_size:raise ValueError('Invalid derivative controls')
    correction=np.zeros((features,features),dtype=np.complex128)
    for _ in range(probes):
        u=np.concatenate([orthogonal_probe(rows,group_size,rng) for _ in range(features//group_size)],axis=1)
        real_direction,imag_direction=directional_derivative(np.stack([u,1j*u]))
        derivative=(real_direction-1j*imag_direction)/2
        for start in range(0,features,group_size):
            sl=slice(start,start+group_size)
            correction[sl,sl]+=np.einsum('ni,nj->ij',u[:,sl].conj(),derivative[:,sl],optimize=False)/measurements
    return correction/probes


def solve(inputs,denoise,*,scale,controls=Controls(),observer=None):
    p=np.asarray(inputs.operator,np.complex128);observation=np.asarray(inputs.observation,np.complex128)
    q,k,n=p.shape;m,r=observation.shape[1:];shape=(k,m,r,n)
    gain=float(np.sqrt(np.sum(abs(p)**2)/(k*n)))
    if not np.isfinite(gain) or gain<=0 or scale<=0 or controls.iterations<1:
        raise ValueError('Positive operator gain, population scale and iteration count required')
    a=p.reshape(q,k*n)/gain;y=observation.reshape(q,m*r)/(scale*gain)
    x=np.zeros((k*n,m*r),dtype=np.complex128);z=y.copy()
    rng=np.random.default_rng(controls.divergence_seed);trace=[]
    for step in range(controls.iterations):
        query=x+np.einsum('qn,qc->nc',a.conj(),z,optimize=False)
        covariance=np.einsum('qi,qj->ij',z,z.conj(),optimize=False)/q
        output,channel_directions=denoise.linearize(from_matrix(query,shape),covariance)
        estimate=to_matrix(output)
        if estimate.shape!=query.shape or not np.isfinite(estimate).all():
            raise FloatingPointError('Invalid linearized denoiser output')
        def directions(deltas):
            values=channel_directions(np.stack([from_matrix(d,shape) for d in deltas]))
            return np.stack([to_matrix(value) for value in values])
        correction=partial_trace(directions,rows=k*n,features=m*r,measurements=q,
                                 group_size=r,rng=rng,probes=controls.probes)
        residual=y-np.einsum('qn,nc->qc',a,estimate,optimize=False)
        next_z=residual+np.einsum('qi,ij->qj',z,correction,optimize=False)
        if not np.isfinite(next_z).all():raise FloatingPointError('Nonfinite matrix L-DAMP residual')
        row=dict(iteration=step+1,effective_complex_variance=float(np.trace(covariance).real/(m*r)),
            covariance_offdiagonal_fraction=float(np.sum(abs(covariance-np.diag(np.diag(covariance)))**2)/max(float(np.sum(abs(covariance)**2)),1e-30)),
            correction_frobenius=float(np.linalg.norm(correction)),
            correction_diagonal_mean_real=float(np.trace(correction).real/(m*r)),
            correction_diagonal_mean_imag=float(np.trace(correction).imag/(m*r)),
            epsilon=None,derivative_method='exact_paired',residual_energy=float(np.sum(abs(residual)**2)))
        x,z=estimate,next_z;trace.append(row)
        if observer is not None:observer(row,scale*from_matrix(x,shape))
    return dict(estimate=scale*from_matrix(x,shape),trace=trace,operator_normalization=gain,iterations=len(trace))
