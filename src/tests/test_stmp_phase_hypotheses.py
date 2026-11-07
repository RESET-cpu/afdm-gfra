"""Check local Gaussian derivatives and activity-evidence selection."""
from types import SimpleNamespace
import numpy as np
from scipy.special import logit
from receiver.stmp import phase_hypotheses as subject
from receiver.frontend.phase_math import observed_covariances
from channel.phase import phase_operator


def entry(p,slope=0.,rho=.1):
    return dict(probability=p,log_bayes_factor=float(logit(p)-logit(rho)),slope=slope,supported=True)


def test_probability_tolerance_rejects_numerically_irrelevant_inactive_changes():
    result=dict(users=[dict(user=0,status='COMPLETE',candidates=[entry(1e-7),entry(1e-5,1.)])])
    assert subject.select_activity_hypothesis(result,.1,.001) is None


def test_selection_uses_all_users_and_existing_probability_tolerance():
    result=dict(users=[
        dict(user=0,status='COMPLETE',candidates=[entry(.01),entry(.7,1.)]),
        dict(user=1,status='COMPLETE',candidates=[entry(.001),entry(.999,2.)]),
        dict(user=2,status='COMPLETE',candidates=[entry(.4),entry(.41,3.)])])
    chosen=subject.select_activity_hypothesis(result,.1,.001)
    assert chosen['user']==1 and chosen['slope']==2.
    np.testing.assert_allclose(chosen['evidence_gain'],np.log((1-.001)/(1-.999)),rtol=1e-13)


def test_no_activity_hard_threshold_is_used():
    result=dict(users=[dict(user=0,status='COMPLETE',candidates=[entry(.01),entry(.02,1.)])])
    assert subject.select_activity_hypothesis(result,.1,.001)['user']==0


def test_directional_coefficients_equal_direct_gaussian_covariance_derivative(monkeypatch):
    rng=np.random.default_rng(329)
    z=lambda shape:(rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)
    q,k,n,m,nr=3,2,2,3,2
    pilot=z((q,k,n));y=z((q,m,nr));mean=z((k,m,nr,n));beta=np.array([.3,-.5])
    noise=.9;c=.4;t=z((nr*n,nr*n));moment=t@t.conj().T+np.eye(nr*n)
    captured=[];original=subject.maxima
    def save(coefficients,previous):
        captured.append(coefficients.copy());return original(coefficients,previous)
    monkeypatch.setattr(subject,'maxima',save)
    class Moments:
        noise_support=(1e-12,1e12)
        def infer(self,r,v):return SimpleNamespace(mean=np.zeros_like(r))
    class Evidence:
        training_class_prior=.5
        def infer(self,r,v,mean):return np.zeros(len(r))
    result=subject.proposals(pilot,y,noise,mean,c,beta,moment,.1,1.,Moments(),Evidence())
    assert len(captured)==k and len(result['users'])==k
    a=phase_operator(pilot,beta).reshape(q,k*n)
    x=mean.transpose(0,3,1,2).reshape(k*n,-1)
    gram=observed_covariances(pilot,moment);frames=np.repeat(np.arange(q),nr)
    for user,coef in enumerate(captured):
        ak=a[:,user*n:(user+1)*n]
        base=noise*np.eye(q)+c*(a@a.conj().T-ak@ak.conj().T)
        full=np.kron(base,np.eye(nr))
        residual=(y.reshape(q,-1)-a@x+ak@x[user*n:(user+1)*n]).reshape(q,m,nr).transpose(0,2,1).reshape(q*nr,m)
        sample=residual@residual.conj().T/m
        inv=np.linalg.inv(full)
        for slope in (.127,-1.03):
            phase=np.exp(1j*frames*slope)
            g=gram[user]*phase[:,None]*phase[None,:].conj()
            expected=float(np.trace((inv@sample@inv-inv)@g).real)
            actual=float(coef[0].real+2*np.real(np.exp(-1j*np.arange(1,q)*slope)@coef[1:]))
            np.testing.assert_allclose(actual,expected,rtol=1e-12,atol=1e-11)


def test_local_queries_match_gaussian_conditioning_in_precision_form():
    """Check the covariance-form implementation against posterior precision.

    This tests the Gaussian reference query only. The scalarization and
    learned density ratio do not thereby become an exact joint likelihood.
    """
    rng=np.random.default_rng(2401)
    z=lambda shape:(rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)
    q,k,n,m,nr=4,3,2,3,2
    pilot=z((q,k,n));y=z((q,m,nr));mean=z((k,m,nr,n))
    beta=np.array([.3,-.5,.8]);noise=.7;feedback_variance=.4;gamma=1.3
    captured={}
    class Moments:
        noise_support=(1e-12,1e12)
        def infer(self,r,v):
            captured.update(queries=r.copy(),variances=v.copy())
            return SimpleNamespace(mean=np.zeros_like(r))
    class Evidence:
        training_class_prior=.5
        def infer(self,r,v,mean):return np.zeros(len(r))
    result=subject.proposals(pilot,y,noise,mean,feedback_variance,beta,
        np.eye(nr*n),.1,gamma,Moments(),Evidence())
    entries=[c for row in result['users'] for c in row['candidates']]
    assert len(entries)==len(captured['queries'])
    operator=phase_operator(pilot,beta).reshape(q,k*n)
    channels=mean.transpose(0,3,1,2).reshape(k*n,m*nr)
    for i,entry in enumerate(entries):
        user=entry['user'];keep=np.ones(k*n,dtype=bool);keep[user*n:(user+1)*n]=False
        others=operator[:,keep]
        residual=y.reshape(q,m*nr)-others@channels[keep]
        covariance=noise*np.eye(q)+feedback_variance*(others@others.conj().T)
        atom=pilot[:,user]*np.exp(1j*np.arange(q)*entry['slope'])[:,None]
        solved_atom=np.linalg.solve(covariance,atom)
        precision=np.eye(n)/gamma+atom.conj().T@solved_atom
        posterior_covariance=np.linalg.inv(precision)
        posterior_mean=np.linalg.solve(precision,atom.conj().T@np.linalg.solve(covariance,residual))
        tau=float(np.trace(posterior_covariance).real)/n
        query_variance=1/(1/tau-1/gamma)
        query=(posterior_mean/(1-tau/gamma)).reshape(n,m,nr).transpose(1,2,0)
        np.testing.assert_allclose(captured['queries'][i],query,rtol=2e-12,atol=2e-12)
        np.testing.assert_allclose(captured['variances'][i],query_variance,rtol=2e-12,atol=2e-12)
