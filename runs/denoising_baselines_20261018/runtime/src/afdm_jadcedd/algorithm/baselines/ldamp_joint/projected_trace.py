"""Compute Z times the partial trace by probing only the user row coordinate.

For independent user blocks with N rows each, choose per-user eta vectors with
unit entries and E conj(eta_i) eta_j = delta_ij. For each observation row z_q,
apply the complete Wirtinger Jacobian to eta_i*z_q and sum conj(eta_i) times the
matching output rows, divided by Q. This estimates Z B directly and does not
approximate feature mixing by an additional random projection. Averaging all
N orthogonal eta vectors is exact for the frozen user-separable Jacobian,
up to floating-point directional-derivative error. No cross-beam terms vanish.
"""
import numpy as np
from afdm_jadcedd.algorithm.baselines.ldamp.matrix import orthogonal_probe


def projected_partial_trace(direction,z,*,rows,row_block_size,rng,probes,return_samples=False,measurement_batch=1):
    if rows%row_block_size or not 1<=probes<=row_block_size:
        raise ValueError('One to N row probes required for independent user blocks')
    q,features=z.shape
    if measurement_batch<1:raise ValueError('Positive direction batch required')
    phases=np.concatenate([orthogonal_probe(row_block_size,row_block_size,rng)
        for _ in range(rows//row_block_size)],axis=0)
    samples=[]
    for probe in range(probes):
        eta=phases[:,probe];correction=np.zeros_like(z,dtype=np.complex128)
        for start in range(0,q,measurement_batch):
            stop=min(start+measurement_batch,q);count=stop-start
            u=eta[None,:,None]*z[start:stop,None,:]
            outputs=direction(np.concatenate([u,1j*u],axis=0))
            real,imag=outputs[:count],outputs[count:]
            derivative=(real-1j*imag)/2
            correction[start:stop]=np.einsum('i,pib->pb',eta.conj(),derivative,optimize=False)/q
        samples.append(correction)
    samples=np.stack(samples)
    return (samples.mean(axis=0),samples) if return_samples else samples.mean(axis=0)
