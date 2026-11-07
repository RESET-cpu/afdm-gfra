"""Observed per-user phase hypotheses with fixed other-user Gaussian messages.

Independent candidate operation. The scalar-query and neural-density
approximations are explicit; this is not a proved full-observation objective.
"""
import numpy as np
from scipy.linalg import cho_factor
from scipy.linalg import cho_solve
from scipy.special import expit
from scipy.special import logit
from receiver.du.phase_math import observed_covariances
from receiver.stmp.phase_initialization_candidates import maxima
from channel.phase import phase_operator


def proposals(pilot,observation,noise,prior_mean,prior_variance,slopes,training_moment,
              activity_prior,reference_power,moments,evidence,proposal_gram=None):
    q,k,n=pilot.shape;m,nr=observation.shape[1:]
    op=phase_operator(pilot,slopes).reshape(q,k*n)
    mu=prior_mean.transpose(0,3,1,2).reshape(k*n,-1)
    y=observation.reshape(q,-1)
    residual=y-op@mu
    all_cov=noise*np.eye(q)+prior_variance*(op@op.conj().T)
    gram=observed_covariances(pilot,training_moment) if proposal_gram is None else proposal_gram
    gamma=float(reference_power);dimension=m*nr*n
    queries=[];variances=[];metadata=[]
    for user in range(k):
        ak=op[:,user*n:(user+1)*n]
        target=residual+ak@mu[user*n:(user+1)*n]
        base=all_cov-prior_variance*(ak@ak.conj().T)
        base=(base+base.conj().T)/2
        factor=cho_factor(base,lower=True,check_finite=True)
        inverse=cho_solve(factor,np.eye(q))
        solved=cho_solve(factor,target).reshape(q,m,nr).transpose(0,2,1).reshape(q*nr,m)
        negative_weight=solved@solved.conj().T/m-np.kron(inverse,np.eye(nr))
        cross=np.sum(gram[user].conj().reshape(q,nr,q,nr)*negative_weight.reshape(q,nr,q,nr),axis=(1,3))
        coefficients=np.array([np.trace(cross,offset=-lag) for lag in range(q)])
        angles=[(float(slopes[user]),'current')]
        for angle,_ in maxima(coefficients,slopes[user]):
            if any(abs(np.angle(np.exp(1j*(angle-old))))<1e-8 for old,_ in angles):continue
            angles.append((angle,'positive_stationary_point'))
        for angle,source in angles:
            a=pilot[:,user]*np.exp(1j*np.arange(q)*angle)[:,None]
            covariance=base+gamma*(a@a.conj().T)
            f=cho_factor(covariance,lower=True,check_finite=True)
            response=gamma*float(np.trace(a.conj().T@cho_solve(f,a)).real)/n
            if not 0<response<1:raise FloatingPointError('Invalid local Gaussian response')
            r=gamma/response*a.conj().T@cho_solve(f,target)
            r=r.reshape(n,m,nr).transpose(1,2,0)
            v=gamma*(1-response)/response
            log_gaussian=-m*nr*(q*np.log(np.pi)+2*np.log(np.diag(f[0]).real).sum())-np.vdot(target,cho_solve(f,target)).real
            metadata.append(dict(user=user,slope=float(angle),source=source,query_variance=float(v),
                gaussian_log_partition=float(log_gaussian),supported=bool(moments.noise_support[0]<=v<=moments.noise_support[1])))
            queries.append(r);variances.append(v)
    queries=np.asarray(queries);variances=np.asarray(variances)
    selected=np.array([d['supported'] for d in metadata])
    if selected.any():
        output=moments.infer(queries[selected],variances[selected])
        ell=np.asarray(evidence.infer(queries[selected],variances[selected],output.mean))-logit(evidence.training_class_prior)
        energy=np.sum(abs(queries[selected])**2,axis=(1,2,3))
        v=variances[selected]
        prior=-dimension*np.log(np.pi*v)-energy/v+np.logaddexp(np.log1p(-activity_prior),np.log(activity_prior)+ell)
        overlap=-dimension*np.log(np.pi*(v+gamma))-energy/(v+gamma)
        for index,log_bayes,correction in zip(np.flatnonzero(selected),ell,prior-overlap):
            metadata[index].update(log_bayes_factor=float(log_bayes),
                probability=float(expit(logit(activity_prior)+log_bayes)),
                conditional_score=float(metadata[index]['gaussian_log_partition']+correction))
    rows=[]
    for user in range(k):
        entries=[d for d in metadata if d['user']==user]
        current=entries[0]
        if not current['supported']:
            rows.append(dict(user=user,status='CURRENT_QUERY_UNSUPPORTED',candidates=entries));continue
        chosen=max((d for d in entries if d['supported']),key=lambda d:d['conditional_score'])
        rows.append(dict(user=user,status='COMPLETE',current=current,best=chosen,
            score_improvement=chosen['conditional_score']-current['conditional_score'],
            phase_increment=float(np.angle(np.exp(1j*(chosen['slope']-slopes[user])))),candidates=entries))
    return dict(users=rows,neural_query_count=int(selected.sum()),candidate_count=len(metadata),
        truth_used=False,global_descent_claim=False,reference_power=gamma)


def select_activity_hypothesis(result,activity_prior,probability_tolerance):
    """Require a resolved change in local probability, then rank its evidence.

    The tolerance is the existing probability tolerance, not a truth-selected
    cutoff or a user activity decision. Every user is examined symmetrically.
    """
    if not 0<probability_tolerance<1:raise ValueError('Positive probability tolerance below1 required')
    weight=lambda ell:float(np.logaddexp(np.log1p(-activity_prior),np.log(activity_prior)+ell))
    eligible=[]
    for row in result['users']:
        if row['status']!='COMPLETE':continue
        current=row['candidates'][0]
        best=max((d for d in row['candidates'] if d['supported']),key=lambda d:d['log_bayes_factor'])
        change=best['probability']-current['probability']
        if change<=probability_tolerance:continue
        gain=weight(best['log_bayes_factor'])-weight(current['log_bayes_factor'])
        if gain<=0:continue
        eligible.append(dict(user=row['user'],slope=best['slope'],evidence_gain=gain,
            probability_change=change,before_probability=current['probability'],after_probability=best['probability'],
            before_log_bayes_factor=current['log_bayes_factor'],after_log_bayes_factor=best['log_bayes_factor']))
    return max(eligible,key=lambda d:d['evidence_gain']) if eligible else None
