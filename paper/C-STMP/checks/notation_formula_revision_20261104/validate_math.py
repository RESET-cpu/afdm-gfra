"""Small deterministic algebra examples, not receiver experiments or training."""
from pathlib import Path
import json, numpy as np
RUN=Path(__file__).resolve().parent
old=(RUN.parent/'notation_formula_review_20261104/check_identities.py').read_text(encoding='utf-8')
exec(old[old.index('rng=np.random'):old.index('aux=(paper/')])

# Independent time-domain construction versus the closed-form path expression.
N=8; c1=3/(2*N); c2=.037; Ts=.1; nu=.21; g=21
t=np.arange(N); n=np.arange(N)
FA=np.exp(-2j*np.pi*(c2*n[:,None]**2+n[:,None]*t[None,:]/N+c1*t[None,:]**2))/np.sqrt(N)
def phi(x):
    x=np.asarray(x)[:,None]; w=x%N
    z=np.floor(2*c1*w+n[None,:]/N)
    return np.exp(2j*np.pi*(c2*n[None,:]**2+c1*x*x+n[None,:]*w/N-z*w))/np.sqrt(N)
def path(delay,start):
    return FA@np.diag(np.exp(2j*np.pi*nu*Ts*(start+t)))@phi(t-delay)
def expansion(delay,start):
    out=np.zeros((N,N),complex)
    for r in range(N):
        for n1 in range(N):
            z=np.floor(2*c1*((t-delay)%N)+n1/N)
            prefix=np.exp(2j*np.pi*(c1*delay**2+c2*(n1*n1-r*r)-n1*delay/N+nu*Ts*start))/N
            out[r,n1]=prefix*np.sum(np.exp(2j*np.pi*(((n1-r)/N-2*c1*delay+nu*Ts)*t+z*delay)))
    return out
results['daft_unitarity']=rel(FA@FA.conj().T,np.eye(N))
results['continuous_basis_integer_samples']=rel(phi(t),FA.conj().T)
results['fractional_and_long_delay_expansion']=max(rel(path(d,g),expansion(d,g)) for d in [.31,7.42,13.73,24.25])
xx=np.array([-.3,-5.2,-8.7,-19.6,-31.2])
results['continuous_cpp_repetition']=rel(phi(xx),np.exp(2j*np.pi*c1*(xx**2-(xx%N)**2))[:,None]*phi(xx%N))
# Thesis (3.7),(3.9), after dimensionless time normalization: additional floor is an integer phase.
xx=np.array([.17,1.83,4.64,7.73]);zz=np.floor(2*c1*xx[:,None]+n[None,:]/N)
thesis=np.exp(2j*np.pi*(c2*n[None,:]**2+c1*xx[:,None]**2+n[None,:]*xx[:,None]/N-zz*xx[:,None]+np.floor(zz/(2*c1)*(zz-n[None,:]/N))))/np.sqrt(N)
results['thesis_piecewise_waveform_equivalence']=rel(thesis,phi(xx))
errors=[]
for d1 in [0,1,7,8,19,25]:
    Pi=np.eye(N)[(t-d1)%N,:]
    Om=np.diag(np.exp(2j*np.pi*c1*((t-d1)**2-((t-d1)%N)**2)))
    integer=FA@np.diag(np.exp(2j*np.pi*nu*Ts*(g+t)))@Om@Pi@FA.conj().T
    errors.append(rel(integer,path(d1,g)))
results['integer_cpp_matrix_including_long_delays']=max(errors)
frame_samples=N+21
results['common_doppler_frame_factor']=max(rel(path(13.73,g+q*frame_samples),np.exp(2j*np.pi*nu*Ts*q*frame_samples)*path(13.73,g)) for q in range(5))
def G0(d):return np.exp(-2j*np.pi*c1*d*d)*path(d,0)
results['phase_search_delay_periodicity']=max(rel(G0(3.37),G0(3.37+j*N)) for j in [1,2,3])

# Full covariance extension must whiten input and the nominal residual target.
d=6; BB=rng.normal(size=(d,d)); S=BB@BB.T+.3*np.eye(d); sd2=.5
def power(A,p):
    e,V=np.linalg.eigh(A);return (V*e**p)@V.T
B=power(sd2*np.eye(d)+S,-.5)
K=sd2*np.linalg.inv(sd2*np.eye(d)+S)
O=np.sqrt(sd2)*power(S@np.linalg.inv(sd2*np.eye(d)+S),.5)
target=(np.eye(d)-K)@(sd2*np.eye(d))@(np.eye(d)-K).T+K@S@K.T
results['preconditioner_input_whitening']=rel(B@(sd2*np.eye(d)+S)@B.T,np.eye(d))
results['preconditioner_output_residual_covariance']=rel(O@O.T,target)
sig2=.6
results['preconditioner_scalar_karras_limit']=rel(np.sqrt(sd2)*power(sig2*np.eye(d)/(sd2+sig2),.5),np.eye(d)*np.sqrt(sd2*sig2/(sd2+sig2)))

# Gaussian site division followed by multiplication recovers the supplied moments.
v=.8; tau=.17; F=complex_array((3,4)); R=complex_array((3,4))
ext=1/(1/tau-1/v); E=ext*(F/tau-R/v)
results['site_mean_reconstruction']=rel((ext*R+v*E)/(ext+v),F)
results['site_variance_reconstruction']=abs(ext*v/(ext+v)-tau)
sdiff=complex_array((3,4)); score=np.linalg.solve(S, rng.normal(size=d))
u=rng.normal(size=d); h=rng.normal(size=d); f=u+S@score
results['dsm_mean_loss_equivalence']=abs(np.linalg.norm(power(S,.5)@(score+np.linalg.solve(S,u-h)))**2-np.linalg.norm(power(S,-.5)@(f-h))**2)
rho=.13;ratio=3.7
results['balanced_logit_bayes_relation']=abs(rho*ratio/(1-rho+rho*ratio)-1/(1+np.exp(-(np.log(rho/(1-rho))+np.log(ratio)))))
# Gaussian noise update: minimizing a log variance plus posterior expected residual.
p=.4; tk=.12; mu=complex_array((3,4)); mean=p*mu
var=p*tk+p*(1-p)*np.linalg.norm(mu)**2/mu.size
vtar=np.linalg.norm(R-mean)**2/R.size+var
mean_energy=np.linalg.norm(R)**2-2*np.real(np.vdot(R,mean))+p*(np.linalg.norm(mu)**2+mu.size*tk)
results['expected_residual_variance_target']=abs(vtar-mean_energy/mu.size)
results['variance_objective_stationarity']=abs(1/vtar-(mean_energy/mu.size)/vtar**2)

# Partial-DFT energy is preserved; device phase rotations do not imply row orthogonality.
K,N,Q=3,4,5; Ep=2.3; perm=rng.permutation(K*N); rows=rng.choice(K*N,Q,replace=False)
P=np.sqrt(Ep/N)*np.exp(-2j*np.pi*rows[:,None]*perm[None,:]/(K*N))*np.exp(1j*rng.normal(size=K*N))
results['pilot_row_energy']=rel(P@P.conj().T,K*Ep*np.eye(Q))
results['pilot_device_frame_energy']=float(np.max(abs(np.sum(abs(P.reshape(Q,K,N))**2,axis=2)-Ep)))
beta=np.array([.1,.7,-.6]);A=(P.reshape(Q,K,N)*np.exp(1j*np.arange(Q)[:,None,None]*beta[None,:,None])).reshape(Q,K*N)
counterexample=rel(A@A.conj().T,K*Ep*np.eye(Q))
assert counterexample>.01

# Variable projection formula agrees with an independent least-squares solve.
a=complex_array((15,1)); Z=complex_array((15,3)); gain=np.linalg.lstsq(a,Z,rcond=None)[0]
J1=np.linalg.norm(Z-a@gain)**2
J2=np.linalg.norm(Z)**2-np.linalg.norm(a.conj().T@Z)**2/np.linalg.norm(a)**2
results['phase_variable_projection']=abs(J1-J2)
tol=1e-10
assert max(results.values())<tol,results
report={'algebra_checks':results,'count':len(results),'largest_residual':max(results.values()),
        'tolerance':tol,'phase_rotated_A_row_orthogonality_counterexample':counterexample,
        'scope':'Small deterministic identities; does not establish trained-network accuracy, convergence, or experimental outcomes.'}
(RUN/'MATH_VALIDATION.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
