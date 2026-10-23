"""Unchanged matrix AMP recurrence with direct estimation of the Z B product."""
import time
import numpy as np
from .projected_trace import projected_partial_trace
from afdm_jadcedd.algorithm.baselines.ldamp.matrix import to_matrix,from_matrix
from afdm_jadcedd.algorithm.baselines.ldamp.representation import beam_transform
from afdm_jadcedd.system.observation import ReceiverInput


def solve_projected(inputs,denoiser,*,iterations=10,row_probes=2,measurement_batch=4,seed=202610150201,observer=None):
    if not isinstance(inputs,ReceiverInput):raise TypeError('Public receiver input required')
    p=np.asarray(inputs.operator,np.complex128);observation=beam_transform(inputs.observation)
    q,k,n=p.shape;m,r=observation.shape[1:];shape=(k,m,r,n)
    gain=float(np.sqrt(np.sum(abs(p)**2)/(k*n)));scale=denoiser.scale
    a=p.reshape(q,k*n)/gain;y=observation.reshape(q,m*r)/(scale*gain)
    x=np.zeros((k*n,m*r),complex);z=y.copy();trace=[];rng=np.random.default_rng(seed);started=time.monotonic()
    linearize=getattr(denoiser,'linearize_complete',denoiser.linearize)
    for step in range(iterations):
        query=x+np.einsum('qn,qc->nc',a.conj(),z,optimize=False)
        covariance=np.einsum('qi,qj->ij',z,z.conj(),optimize=False)/q
        value,channel_directions=linearize(from_matrix(query,shape),covariance);estimate=to_matrix(value)
        def directions(delta):
            result=channel_directions(np.stack([from_matrix(d,shape) for d in delta]))
            return np.stack([to_matrix(v) for v in result])
        correction=projected_partial_trace(directions,z,rows=k*n,row_block_size=n,
            rng=rng,probes=row_probes,measurement_batch=measurement_batch)
        residual=y-np.einsum('qn,nc->qc',a,estimate,optimize=False);next_z=residual+correction
        if not all(np.isfinite(v).all() for v in [estimate,correction,next_z]):raise FloatingPointError('Nonfinite AMP state')
        row=dict(iteration=step+1,variance_mean=float(np.trace(covariance).real/(m*r)),
            correction_term_norm=float(np.linalg.norm(correction)),residual_energy=float(np.sum(abs(residual)**2)))
        trace.append(row)
        if observer is not None:observer(dict(row),value.copy(),from_matrix(query,shape).copy(),covariance.copy())
        x,z=estimate,next_z
    estimate=scale*beam_transform(from_matrix(x,shape),inverse=True)
    return dict(estimate=estimate,energy=np.sum(abs(estimate)**2,axis=(1,2,3)),trace=trace,
        iterations=iterations,row_probes=row_probes,measurement_batch=measurement_batch,seed=seed,
        seconds=time.monotonic()-started,stopping_reason='FIXED_ITERATION_BUDGET',truth_used_in_inference=False,
        partial_trace='Direct Z B product; orthogonal phases within user rows; complete row basis if row_probes=N')
