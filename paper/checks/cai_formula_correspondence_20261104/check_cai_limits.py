"""Deterministic checks of reductions to the published Cai formulas.

These verify algebraic correspondences, not receiver performance or convergence.
"""
from pathlib import Path
import json
import numpy as np

rng = np.random.default_rng(20261104)
results = {}

def cx(shape):
    return (rng.normal(size=shape) + 1j*rng.normal(size=shape))/np.sqrt(2)

def rel(x, y):
    return float(np.linalg.norm(x-y)/max(1.0, np.linalg.norm(y)))

# Cai (7)-(8): general Gaussian conditioning reduces to the row-orthogonal case.
n, m, columns = 12, 5, 4
row_power, gamma, noise = 2.3, .7, .4
dft = np.exp(-2j*np.pi*np.arange(n)[:,None]*np.arange(n)[None,:]/n)/np.sqrt(n)
A = np.sqrt(row_power)*dft[[0,2,5,8,10]]
Xpri, Y = cx((n,columns)), cx((m,columns))
general = Xpri + gamma*A.conj().T @ np.linalg.solve(noise*np.eye(m)+gamma*A@A.conj().T, Y-A@Xpri)
cai = Xpri + gamma/(noise+gamma*row_power)*A.conj().T@(Y-A@Xpri)
results['cai_7_row_orthogonal_lmmse'] = rel(general,cai)
covariance = np.linalg.inv(np.eye(n)/gamma+A.conj().T@A/noise)
scalar = gamma-(m/n)*gamma**2*row_power/(noise+gamma*row_power)
results['cai_8_row_orthogonal_trace'] = abs(float(np.trace(covariance).real/n)-scalar)

# Cai (35)-(38): element-wise mixture variance agrees with the pooled formula.
K, M, N2 = 3, 4, 9
D = M*N2
H, probabilities, tau = cx((K,M,N2)), np.array([.12,.51,.91]), np.array([.08,.13,.21])
p = probabilities[:,None,None]
element_variance = p*(abs(H)**2+tau[:,None,None])-abs(p*H)**2
pooled = np.mean(probabilities*tau+probabilities*(1-probabilities)*np.sum(abs(H)**2,axis=(1,2))/D)
results['cai_36_38_mixture_pooling'] = abs(float(np.mean(element_variance))-float(pooled))
spatial = [probabilities[k]*tau[k]*np.eye(M)+probabilities[k]*(1-probabilities[k])/N2*H[k]@H[k].conj().T for k in range(K)]
results['spatial_diagonal_vs_cai_36'] = max(rel(np.diag(spatial[k]).real,np.mean(element_variance[k],axis=1)) for k in range(K))

# Cai (41)-(42): precision-subtraction and the b shorthand are identical.
v, t = .8, .21
R, X = cx((5,3)), cx((5,3))
ve = 1/(1/t-1/v)
xe = ve*(X/t-R/v)
b = t/v
results['cai_41_42_compact_extrinsic'] = max(abs(ve-v*b/(1-b)),rel(xe,(X-b*R)/(1-b)))

# Cai (30): common variances and stacked coordinates yield our Gaussian fallback.
R, E = cx((2,3)), cx((2,3)); v, ext, rho = .7, .4, .13
log0 = sum(-3*np.log(np.pi*v)-np.sum(abs(row)**2)/v for row in R)
log1 = sum(-3*np.log(np.pi*(v+ext))-np.sum(abs(row-e)**2)/(v+ext) for row,e in zip(R,E))
cai_p = 1/(1+(1-rho)/rho*np.exp(log0-log1))
ell = np.sum(abs(R)**2)/v-np.sum(abs(R-E)**2)/(v+ext)-R.size*np.log1p(ext/v)
ours_p = 1/(1+np.exp(-np.log(rho/(1-rho))-ell))
results['cai_30_gaussian_activity_log_form'] = abs(float(cai_p-ours_p))

# Cai (48)-(49): in white noise, the reparameterized loss agrees up to 1/D.
dim, v = 9, .63
h, u, f = cx(dim), cx(dim), cx(dim)
score = (f-u)/v
cai_weighted = v*np.sum(abs(score+(u-h)/v)**2)/dim
error_real = np.r_[np.real(f-h),np.imag(f-h)]
ours_loss = np.sum(error_real**2)/(2*dim*(v/2))
results['cai_48_49_white_noise_loss_normalization'] = abs(float(cai_weighted-ours_loss))

assert max(results.values()) < 1e-10, results
report = {'checks':results,'count':len(results),'tolerance':1e-10,
          'maximum_error':max(results.values()),
          'scope':'Only algebraic reductions in the stated common-variance or row-orthogonal cases; not a performance, stability, convergence or full implementation audit.'}
Path(__file__).with_name('CAI_LIMIT_CHECKS.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
