"""OAMP dispatch and retained standard/Ying reference variants.

The current group_bg_common_rate recipe dispatches to common_rate_oamp.py.
"""
import numpy as np
from scipy.special import expit, logit, ndtr
from afdm_jadcedd.algorithm.baselines.common import SparseControls, validate, initial_power, gaussian_moments, bg_moments, change


def oamp_linear(a, ah, y, d, variance, noise, eigenvalues, eigenvectors):
    """Ying (10a),(13a),(14); row-space eigendecomposition equals thin SVD."""
    n = a.shape[1]
    gain = variance/(variance*eigenvalues+noise)
    decorrelation = n/np.sum(gain*eigenvalues)
    residual = y-a@d
    r = d+decorrelation*(ah@(eigenvectors@(gain[:, None]*(eigenvectors.conj().T@residual))))
    # ||I-WA||_F^2 = N-2 tr(WA)+||WA||_F^2, including the nullspace.
    wa = decorrelation*gain*eigenvalues
    tau = (variance*(n-2*wa.sum()+np.sum(wa**2))
           +noise*np.sum((decorrelation*gain)**2*eigenvalues))/n
    return r, float(max(tau, np.finfo(float).tiny))


def solve_oamp_mmv(design, received, noise_variance, *, controls=None, observer=None, channel_reconstruct=None):
    a, y = validate(design, received, noise_variance); c = controls or SparseControls()
    if c.oamp_variant == 'group_bg_common_rate':
        from afdm_jadcedd.algorithm.baselines.common_rate_oamp import solve_common_rate_oamp
        return solve_common_rate_oamp(a, y, noise_variance, controls=c,
            observer=observer, channel_reconstruct=channel_reconstruct)
    if c.oamp_variant == 'ying_equations':
        return solve_oamp_equations(a, y, noise_variance, iterations=c.iterations, observer=observer)
    author = c.oamp_variant == 'ying_author'
    n, m = a.shape[1], y.shape[1]
    ah = a.conj().T.copy()
    eigen, vectors = np.linalg.eigh(a@ah); eigen = np.maximum(eigen, 0.)
    # Ying author's initialization depends on the public measurement ratio.
    alpha = min(a.shape[0]/n, 1.)
    # At zero the phase-transition expression has a removable/negative-infinite
    # endpoint (0/0 for a square matrix); evaluate only its positive grid points.
    alpha_grid = np.linspace(0, 10, 1024)[1:]
    term = (1+alpha_grid**2)*ndtr(-alpha_grid)-alpha_grid*np.exp(-alpha_grid**2/2)/np.sqrt(2*np.pi)
    initial_probability = float(np.clip(alpha*np.max((1-2*term/alpha)/(1+alpha_grid**2-2*term)), 1e-8, 1-1e-8))
    rho = np.full((n, 1), initial_probability)
    gamma = initial_power(a, y, noise_variance, initial_probability, c.variance_floor)
    mu = 0j; d = np.zeros((n, m), complex)
    variance = np.maximum(initial_power(a, y, noise_variance, 1., c.variance_floor), c.variance_floor)
    previous = d.copy(); trace = []; status = 'MAX_ITERATIONS'; clipped = 0; stable = 0
    residual_floors = 0; precision_floors = 0
    for it in range(c.iterations):
        r, tau = oamp_linear(a, ah, y, d, variance, noise_variance, eigen, vectors)
        if author:
            # Ying gmmv_oamp_app2.m permits exact zero/one probabilities.
            # Log odds evaluate the same density ratio without exp overflow.
            cm, cv = gaussian_moments(r, tau, gamma, mu)
            likelihood = -np.log1p(gamma/tau)+abs(r)**2/tau-abs(r-mu)**2/(tau+gamma)
            pi = expit(logit(rho)+likelihood)
            mean = pi*cm
            vx = pi*cv+pi*(1-pi)*abs(cm)**2
        else:
            mean, vx, pi, cm, cv = bg_moments(r, tau, gamma, rho, mu, joint_support=False)
        average = np.mean(vx, axis=0, keepdims=True)
        clipped += int(np.sum(average >= tau))
        # OAMP's extrinsic precision must be positive; record every floor use.
        ratio = average/tau if author else np.minimum(average/tau, 1-1e-6)
        extrinsic = (mean-ratio*r)/(1-ratio)
        next_d = (1-c.damping)*d+c.damping*extrinsic
        residual = y-a@extrinsic
        residual_variance = float((np.sum(abs(residual)**2)/m-a.shape[0]*noise_variance)/np.sum(abs(a)**2))
        residual_floors += int(residual_variance <= c.variance_floor)
        if c.oamp_variance_update == 'residual':
            raw_variance = max(residual_variance, 1e-20 if author else c.variance_floor)
        else:
            # Alternative (39b) documented in Ying author's gmmv_oamp_app2.m.
            posterior_variance = float(average.mean())
            precision = 1/posterior_variance-1/tau
            precision_floors += int(precision <= 0)
            raw_variance = max(1/precision, c.variance_floor)
        next_variance = (1-c.damping)*variance+c.damping*raw_variance
        mass = float(pi.sum()) if author else max(float(pi.sum()), c.variance_floor)
        next_mu = (pi*cm).sum()/mass
        next_gamma = float((pi*(abs(cm-next_mu)**2+cv)).sum()/mass)
        if author:
            # The author's T=1 branch learns one scalar sparsity rate.
            next_rho = pi.mean(axis=1, keepdims=True) if m > 1 else np.full((n, 1), pi.mean())
        else:
            next_gamma = max(next_gamma, c.variance_floor)
            next_rho = np.clip(pi.mean(axis=1, keepdims=True), 1e-8, 1-1e-8)
        author_statistic = float(np.linalg.norm(mean-next_d)**2/np.linalg.norm(next_d)**2) if author else None
        components = dict(mean_change=change(mean, previous, c.variance_floor),
                          extrinsic_mean_change=change(next_d, d, c.variance_floor),
                          probability_change=float(np.max(abs(next_rho-rho))),
                          prior_mean_change=float(abs(next_mu-mu)/max(abs(next_mu), np.sqrt(c.variance_floor))),
                          prior_variance_change=float(abs(next_gamma-gamma)/max(next_gamma, c.variance_floor)),
                          residual_variance_change=float(abs(next_variance-variance)/max(next_variance, c.variance_floor)))
        delta = max(components[k] for k in ('mean_change', 'extrinsic_mean_change', 'probability_change'))
        stable = stable+1 if delta < c.tolerance else 0
        if (not np.isfinite(mean).all() or not np.isfinite(next_d).all()
                or (author and (not np.isfinite(next_mu) or not np.isfinite(next_gamma)
                                or next_gamma <= 0 or mass <= 0))):
            raise FloatingPointError('nonfinite OAMP-MMV state')
        d, variance, mu, gamma, rho, previous = next_d, next_variance, next_mu, next_gamma, next_rho, mean.copy()
        trace.append(dict(iteration=it+1, relative_change=delta, equivalent_noise=tau,
                          residual_variance=variance, extrinsic_variance_clips=clipped,
                          residual_variance_floor_events=residual_floors,
                          posterior_precision_floor_events=precision_floors,
                          variance_update=c.oamp_variance_update,
                          stopping_statistic=delta, stopping_rule=c.stopping_rule, stable_iterations=stable, **components))
        if author:
            trace[-1].update(author_stopping_statistic=author_statistic,
                prior_mean_real=float(mu.real), prior_mean_imag=float(mu.imag), prior_variance=gamma,
                old_value_weight=1-c.damping, oamp_variant=c.oamp_variant)
            if c.stopping_rule == 'author':
                trace[-1]['stopping_statistic'] = author_statistic
        if observer is not None:
            observer(trace[-1], mean)
        if c.stopping_rule == 'author' and author_statistic < 1e-5:
            status = 'AUTHOR_STOP'; break
        if c.stopping_rule == 'state' and it+1 >= c.min_iterations and stable >= c.convergence_patience:
            status = 'CONVERGED'; break
    return dict(mean=mean, variance=vx, row_probability=rho[:, 0], trace=trace,
                iterations=len(trace), status=status, extrinsic_variance_clips=clipped)


def solve_oamp_equations(a,y,noise,*,iterations=40,observer=None):
    """Ying Eqs10--23: per-antenna EM and current extrinsic residual variance.

    Author initialization interpreted per column, with its 1e-20 floor.
    This printed-equation mode has no added damping or early exit. The
    selected 40-step budget is from the author example. Its identity and
    differences from that example are documented in BASELINE_IMPLEMENTATION.
    """
    a,y=validate(a,y,noise)
    rows,n=a.shape;q=y.shape[1];floor=1e-20
    ah=a.conj().T.copy();eigen,u=np.linalg.eigh(a@ah);eigen=np.maximum(eigen,0.)
    total=float(np.sum(abs(a)**2));alpha=rows/n;grid=np.linspace(0,10,1024)[1:]
    term=(1+grid**2)*ndtr(-grid)-grid*np.exp(-grid**2/2)/np.sqrt(2*np.pi)
    initial_rho=alpha*np.max((1-2*term/alpha)/(1+grid**2-2*term))
    rho=np.full((n,1),initial_rho);mu=np.zeros((1,q),complex)
    initial_var=(np.sum(abs(y)**2,axis=0,keepdims=True)-rows*noise)/total
    gamma=np.maximum(initial_var/initial_rho,floor)
    d=np.zeros((n,q),complex);trace=[]
    for it in range(iterations):
        residual=y-a@d
        # Eq13b is evaluated on the same d used by Eq10a, independently per j.
        raw_v=(np.sum(abs(residual)**2,axis=0,keepdims=True)-rows*noise)/total
        v=np.maximum(raw_v,floor)
        gain=1/(eigen[:,None]*v+noise);scale=n/np.sum(eigen[:,None]*gain,axis=0,keepdims=True)
        gains=scale*gain
        r=d+ah@(u@(gains*(u.conj().T@residual)))
        wa=eigen[:,None]*gains
        tau=(v*(n-2*wa.sum(axis=0,keepdims=True)+(wa**2).sum(axis=0,keepdims=True))
             +noise*np.sum(gains**2*eigen[:,None],axis=0,keepdims=True))/n
        active_mean=(mu*tau+r*gamma)/(tau+gamma)
        active_var=tau*gamma/(tau+gamma)
        ll=np.log(tau/(tau+gamma))+abs(r)**2/tau-abs(r-mu)**2/(tau+gamma)
        pi=expit(logit(rho)+ll)
        mean=pi*active_mean
        variance=pi*(abs(active_mean)**2+active_var)-abs(mean)**2
        average=variance.mean(axis=0,keepdims=True)
        ratio=average/tau;next_d=(mean-ratio*r)/(1-ratio)
        mass=pi.sum(axis=0,keepdims=True)
        next_mu=(pi*active_mean).sum(axis=0,keepdims=True)/mass
        # Eq22c explicitly has the OLD mean; author code uses the new mean.
        next_gamma=(pi*(abs(mu-active_mean)**2+active_var)).sum(axis=0,keepdims=True)/mass
        next_rho=pi.mean(axis=1,keepdims=True)
        if not all(np.isfinite(z).all() for z in (mean,variance,next_d,next_mu,next_gamma,next_rho)):
            raise FloatingPointError(f'Nonfinite Eq10--23 state at iteration {it+1}')
        row=dict(iteration=it+1,variance_floor_columns=int(np.sum(raw_v<floor)),
            nonpositive_extrinsic_denominators=int(np.sum(ratio>=1)),
            minimum_prior_variance=float(next_gamma.min()),
            minimum_equivalent_noise=float(tau.min()),maximum_equivalent_noise=float(tau.max()))
        trace.append(row)
        if observer is not None:observer(row,mean)
        d,mu,gamma,rho=next_d,next_mu,next_gamma,next_rho
    return dict(mean=mean,variance=variance,row_probability=rho[:,0],trace=trace,iterations=iterations,status='FIXED_BUDGET')
