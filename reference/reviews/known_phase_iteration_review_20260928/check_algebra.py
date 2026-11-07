"""Small deterministic checks of the review's own algebra; no receiver runs."""
import json
from pathlib import Path

import numpy as np
from threadpoolctl import threadpool_limits


def run():
    rng = np.random.default_rng(20260928)
    def cn(shape):
        return (rng.normal(size=shape) + 1j*rng.normal(size=shape))/np.sqrt(2)
    def ah(x):
        return x.conj().T
    k, q, m, n, r = 3, 5, 4, 2, 3
    p, mean = cn((k,q,n)), cn((k,n,r))
    positions = np.array([[0,0],[0,1],[1,0],[1,1]])
    def steering(u):
        return np.exp(1j*np.pi*positions@u)
    b = np.stack([steering(u) for u in rng.uniform(-.5,.5,(k,2))])
    def operator(bb):
        return np.einsum('kqn,km->qmkn',p,bb).reshape(q*m,k*n)
    a = operator(b)
    mu = mean.reshape(k*n,r)
    pred = np.einsum('kqn,km,knr->qmr',p,b,mean)
    pack_err = np.linalg.norm(a@mu-pred.reshape(q*m,r))/np.linalg.norm(pred)

    # Completing the square with a fixed steering vector and colored covariance.
    tmp = cn((m,m)); v = tmp@ah(tmp)+np.eye(m)
    v_inv = np.linalg.inv(v); rr = cn((m,7)); bb = b[0]
    eta = 1/np.vdot(bb,v_inv@bb).real
    z = eta*bb.conj()@v_inv@rr
    gs = [cn((7,)),cn((7,))]
    def spatial_cost(g):
        e = rr-bb[:,None]*g[None,:]
        return np.trace(ah(e)@v_inv@e).real
    differences = (spatial_cost(gs[0])-spatial_cost(gs[1]),
                   (np.linalg.norm(z-gs[0])**2-np.linalg.norm(z-gs[1])**2)/eta)
    compression_err = abs(differences[0]-differences[1])/max(1.,abs(differences[0]))

    # Full cross-user covariance changes with angles; block diagonal does not.
    tmp = cn((k*n,k*n)); cov = tmp@ah(tmp)+np.eye(k*n)
    block = np.zeros_like(cov)
    for i in range(k):
        block[i*n:(i+1)*n,i*n:(i+1)*n] = cov[i*n:(i+1)*n,i*n:(i+1)*n]
    b2=b.copy(); b2[0]=steering(np.array([.7,-.2])); a2=operator(b2)
    def trace_term(aa,cc):
        return np.trace(aa@cc@ah(aa)).real
    block_change = abs(trace_term(a2,block)-trace_term(a,block))/trace_term(a,block)
    full_change = abs(trace_term(a2,cov)-trace_term(a,cov))/trace_term(a,cov)

    # A one-user angular update is a linear steering-vector objective even
    # when the fixed likelihood belief retains cross-user covariance.
    y=cn((q,m,r)); idx=0
    residual=y-sum(np.einsum('m,qr->qmr',b[j],p[j]@mean[j]) for j in range(k) if j!=idx)
    d=np.einsum('qmr,qr->m',residual,(p[idx]@mean[idx]).conj())
    for j in range(k):
        if j!=idx:
            cji=cov[j*n:(j+1)*n,idx*n:(idx+1)*n]
            d-=b[j]*np.trace(p[j]@cji@ah(p[idx]))
    def objective(aa):
        return np.linalg.norm(y.reshape(q*m,r)-aa@mu)**2+trace_term(aa,cov)
    delta_actual=objective(a2)-objective(a)
    delta_steering=-2*np.real(np.vdot(b2[idx]-b[idx],d))
    direction_err=abs(delta_actual-delta_steering)/max(1.,abs(delta_actual))

    # Exact finite enumeration under q(u) q(g|active), including inactivity.
    probs=np.array([.2,.3,.5]); bs=np.stack([steering(u) for u in [[.1,.2],[-.3,.5],[.6,-.1]]])
    gp=np.array([.4,.6]); gv=cn((2,)); pi=.37
    gmean=np.sum(gp*gv); gvar=np.sum(gp*abs(gv-gmean)**2)
    bmean=probs@bs; second=sum(w*np.outer(vv,vv.conj()) for w,vv in zip(probs,bs))
    predicted_cov=pi*(gvar+abs(gmean)**2)*second-pi*pi*abs(gmean)**2*np.outer(bmean,bmean.conj())
    states=[np.zeros(m,complex)]; weights=[1-pi]
    for w,vv in zip(probs,bs):
        for wg,g in zip(gp,gv):states.append(vv*g);weights.append(pi*w*wg)
    states=np.array(states);weights=np.array(weights); hm=weights@states
    exact_cov=sum(w*np.outer(h-hm,(h-hm).conj()) for w,h in zip(weights,states))
    moment_err=np.linalg.norm(exact_cov-predicted_cov)/np.linalg.norm(exact_cov)
    results={
      'scope':'Deterministic algebra checks only; synthetic small arrays; no performance claim',
      'seed':20260928,'operator_rearrangement_relative_error':float(pack_err),
      'colored_compression_cost_difference_relative_error':float(compression_err),
      'block_diagonal_covariance_trace_relative_change':float(block_change),
      'full_covariance_trace_relative_change_example':float(full_change),
      'one_user_direction_objective_difference_relative_error':float(direction_err),
      'uncertain_direction_reconstruction_covariance_relative_error':float(moment_err),
    }
    assert max(pack_err,compression_err,block_change,direction_err,moment_err)<1e-12
    assert full_change>1e-4
    return results


if __name__=='__main__':
    with threadpool_limits(limits=1):
        result=run()
    Path(__file__).with_name('ALGEBRA_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
