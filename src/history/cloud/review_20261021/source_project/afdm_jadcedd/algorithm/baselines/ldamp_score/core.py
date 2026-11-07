"""The existing matrix L-DAMP recurrence with a full joint-denoiser partial trace.

The per-beam baseline may still exploit its exact structural Jacobian zeros.
Probe layout and RNG consumption match ldamp.matrix.partial_trace in both modes.
"""
import numpy as np
from afdm_jadcedd.algorithm.baselines.ldamp.matrix import Controls,to_matrix,from_matrix,orthogonal_probe,partial_trace
from afdm_jadcedd.algorithm.score_amp.core import UnsupportedVariance


def full_partial_trace(directions,*,rows,features,measurements,probe_group_size,rng,probes,residual=None):
    if probes<1 or probe_group_size<1 or features%probe_group_size:
        raise ValueError('Invalid probe controls')
    samples=[]
    for _ in range(probes):
        u=np.concatenate([orthogonal_probe(rows,probe_group_size,rng) for _ in range(features//probe_group_size)],axis=1)
        real,imag=directions(np.stack([u,1j*u]))
        derivative=(real-1j*imag)/2
        samples.append(np.einsum('ni,nj->ij',u.conj(),derivative,optimize=False)/measurements)
    samples=np.stack(samples);correction=samples.mean(axis=0);diagnostic={}
    if residual is not None:
        products=np.einsum('qa,pab->pqb',residual,samples,optimize=False)
        se=np.sqrt(np.sum(abs(products-products.mean(axis=0))**2)/(probes*(probes-1))) if probes>1 else None
        norm=max(float(np.linalg.norm(residual)),1e-30)
        diagnostic=dict(correction_mc_se_over_residual=None if se is None else float(se/norm),
                        correction_norm_over_residual=float(np.linalg.norm(products.mean(axis=0))/norm))
    return correction,diagnostic


def solve(inputs,denoise,*,scale,controls=Controls(),independent_beams=False,observer=None):
    """Inputs and estimates are in beam coordinates; no truth-dependent input."""
    p=np.asarray(inputs.operator,np.complex128);observation=np.asarray(inputs.observation,np.complex128)
    q,k,n=p.shape;m,r=observation.shape[1:];shape=(k,m,r,n)
    gain=float(np.sqrt(np.sum(abs(p)**2)/(k*n)))
    if not np.isfinite(gain) or gain<=0 or scale<=0 or controls.iterations<1:raise ValueError('Invalid controls')
    a=p.reshape(q,k*n)/gain;y=observation.reshape(q,m*r)/(scale*gain)
    x=np.zeros((k*n,m*r),np.complex128);z=y.copy();rng=np.random.default_rng(controls.divergence_seed)
    trace=[];status='COMPLETE';error=None;attempt=None;accepted_probabilities=None
    for step in range(controls.iterations):
        query=x+np.einsum('qn,qc->nc',a.conj(),z,optimize=False)
        covariance=np.einsum('qi,qj->ij',z,z.conj(),optimize=False)/q
        variance=float(np.trace(covariance).real/(m*r))
        try:
            output,channel_directions=denoise.linearize(from_matrix(query,shape),covariance)
            estimate=to_matrix(output)
            if estimate.shape!=query.shape or not np.isfinite(estimate).all():raise FloatingPointError('Invalid denoiser output')
            def directions(deltas):
                values=channel_directions(np.stack([from_matrix(d,shape) for d in deltas]))
                return np.stack([to_matrix(value) for value in values])
            if independent_beams:
                correction=partial_trace(directions,rows=k*n,features=m*r,measurements=q,
                    group_size=r,rng=rng,probes=controls.probes);diagnostic={}
            else:
                correction,diagnostic=full_partial_trace(directions,rows=k*n,features=m*r,measurements=q,
                    probe_group_size=r,rng=rng,probes=controls.probes,residual=z)
            residual=y-np.einsum('qn,nc->qc',a,estimate,optimize=False)
            next_z=residual+np.einsum('qi,ij->qj',z,correction,optimize=False)
            if not np.isfinite(next_z).all():raise FloatingPointError('Nonfinite residual')
        except (UnsupportedVariance,FloatingPointError,RuntimeError) as exc:
            status='FAILED';error=str(exc);attempt=dict(iteration=step+1,effective_complex_variance=variance,
                error=error,error_type=type(exc).__name__)
            if observer is not None:observer(attempt,dict(query=from_matrix(query,shape),covariance=covariance,
                prior_residual=z,previous_estimate=scale*from_matrix(x,shape)))
            break
        diagonal=np.zeros_like(correction)
        for beam in range(m):
            sl=slice(beam*r,(beam+1)*r);diagonal[sl,sl]=correction[sl,sl]
        row=dict(iteration=step+1,effective_complex_variance=variance,
            covariance_offdiagonal_fraction=float(np.sum(abs(covariance-np.diag(np.diag(covariance)))**2)/max(float(np.sum(abs(covariance)**2)),1e-30)),
            correction_frobenius=float(np.linalg.norm(correction)),
            correction_cross_beam_energy_fraction=float(np.sum(abs(correction-diagonal)**2)/max(float(np.sum(abs(correction)**2)),1e-30)),
            correction_diagonal_mean_real=float(np.trace(correction).real/(m*r)),
            correction_diagonal_mean_imag=float(np.trace(correction).imag/(m*r)),
            epsilon=None,derivative_method='exact_paired',residual_energy=float(np.sum(abs(residual)**2)),**diagnostic)
        if observer is not None:observer(row,dict(query=from_matrix(query,shape),covariance=covariance,output=output,
            prior_residual=z,correction=correction,next_residual=next_z,estimate=scale*from_matrix(estimate,shape)))
        x,z=estimate,next_z;trace.append(row)
        probability=getattr(denoise,'last_probabilities',None)
        if probability is not None:accepted_probabilities=np.asarray(probability).copy()
    return dict(estimate=scale*from_matrix(x,shape),trace=trace,operator_normalization=gain,
        iterations=len(trace),status=status,error=error,last_attempt=attempt,
        last_valid_probabilities=accepted_probabilities,
        stopping_reason='FIXED_ITERATIONS' if status=='COMPLETE' else 'INVALID_QUERY_OR_UPDATE')
