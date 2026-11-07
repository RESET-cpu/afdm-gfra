"""Experimental frozen-score calibration; deliberately separate from mainline.

L-STMP motivates learned scalar corrections, not this particular architecture.
The covariance features and soft derivative losses are research candidates.
See docs/TERMINOLOGY.md for assumptions and source equations.
"""
import numpy as np
import torch
from torch import nn
from .proposed.moments import MatrixMomentEstimate

FEATURES = ('log_variance', 'query_energy', 'mean_energy', 'query_mean',
            'residual_energy', 'variance_ratio', 'raw_logit',
            'largest_eigen_fraction', 'covariance_purity',
            'whitened_query_energy', 'whitened_mean_energy',
            'whitened_query_mean', 'whitened_residual_energy')
VARIANTS = ('scalar', 'correlation', 'consistency')


def covariance_from_query(query, variance, shrinkage=.05):
    """Uncentered spatial moment of the lower-energy half; no labels needed."""
    r = np.asarray(query, complex)
    selected = np.argsort(np.mean(abs(r)**2, axis=(1, 2, 3)), kind='stable')[:max(1, len(r)//2)]
    x = r[selected].transpose(1, 0, 2, 3).reshape(r.shape[1], -1)
    c = x @ x.conj().T / x.shape[1]
    m = len(c); energy = float(np.trace(c).real)
    c = np.eye(m)*variance if energy <= 0 else c * (m*variance/energy)
    return (1-shrinkage)*c + shrinkage*variance*np.eye(m)


def feature_values(query, variance, mean, raw_variance, raw_logit, covariance):
    r, f = np.asarray(query, complex), np.asarray(mean, complex)
    v = np.broadcast_to(np.asarray(variance, float), (len(r),))
    axes = tuple(range(1, r.ndim))
    energy = lambda x: np.mean(abs(x)**2, axis=axes)
    signedlog = lambda x: np.sign(x)*np.log1p(abs(x))
    eig, u = np.linalg.eigh(covariance)
    if eig[0] <= 0 or not np.isfinite(eig).all():
        raise ValueError('Positive definite covariance required')
    inverse_sqrt = (u / np.sqrt(eig)) @ u.conj().T
    rw = np.einsum('mn,knrc->kmrc', inverse_sqrt, r, optimize=False)
    fw = np.einsum('mn,knrc->kmrc', inverse_sqrt, f, optimize=False)
    values = [np.log(v)/5, np.log1p(energy(r)/v), np.log1p(energy(f)/v),
              signedlog(np.mean((r.conj()*f).real, axis=axes)/v),
              np.log1p(energy(r-f)/v), np.tanh(np.asarray(raw_variance)/v),
              np.tanh(np.asarray(raw_logit)/50),
              np.full(len(r), eig[-1]/eig.sum()),
              np.full(len(r), np.sum(eig**2)/eig.sum()**2),
              np.log1p(energy(rw)), np.log1p(energy(fw)),
              signedlog(np.mean((rw.conj()*fw).real, axis=axes)),
              np.log1p(energy(rw-fw))]
    result = np.stack(values, axis=-1).astype(np.float32)
    if not np.isfinite(result).all():
        raise FloatingPointError('Nonfinite calibration features')
    return result


class Calibration(nn.Module):
    def __init__(self, variant):
        super().__init__()
        if variant not in VARIANTS:
            raise ValueError(variant)
        self.variant = variant
        self.layers = nn.Sequential(nn.Linear(len(FEATURES), 32), nn.SiLU(),
                                    nn.Linear(32, 32), nn.SiLU(), nn.Linear(32, 4))
        nn.init.zeros_(self.layers[-1].weight)
        nn.init.zeros_(self.layers[-1].bias)
        mask = torch.ones(len(FEATURES))
        if variant == 'scalar':
            mask[7:] = 0
        self.register_buffer('feature_mask', mask)

    def forward(self, features, raw_ratio, raw_logit):
        z = torch.tanh(self.layers(features*self.feature_mask))
        alpha = torch.exp(np.log(4)*z[..., 0])
        # This bound is an algorithmic restriction for positive Gaussian sites,
        # not a theorem that every conditional posterior variance is below v.
        ratio = torch.sigmoid(torch.logit(raw_ratio.clamp(1e-5, 1-1e-5)) + 8*z[..., 1])
        ell = torch.exp(np.log(100)*z[..., 2])*raw_logit + 100*z[..., 3]
        return alpha, ratio, ell


def losses(model, batch, delta=.02):
    """Cached +/- queries keep the frozen networks out of the training graph.

    C is held fixed for the directional derivatives. Direction is C_complex*z /
    sqrt(2*v), with independent +/-1 real and imaginary coordinates of z.
    The normalized curvature estimates tau_complex/v in expectation over z.
    """
    alpha, ratio, ell = model(batch['features'], batch['raw_ratio'], batch['raw_logit'])
    a = alpha[:, 0]; v = batch['variance']; active = batch['active'].bool()
    mse = (batch['mse0'] + 2*a*batch['mse_cross'] + a*a*batch['delta_energy']).clamp_min(1e-12)
    mean_loss = mse[active].mean()
    tau = (v*ratio[:, 0]).clamp_min(1e-8)
    risk = (torch.log(tau[active]) + mse[active]/tau[active]).mean()
    evidence = nn.functional.binary_cross_entropy_with_logits(ell[:, 0], batch['active'])
    dimension = batch['real_dimension']
    first = (ell[:, 1]-ell[:, 2])/(2*delta*torch.sqrt(dimension))
    target = batch['project_r'] + a*batch['project_delta']
    normalization = torch.sqrt(1+1/v)
    first_loss = nn.functional.smooth_l1_loss(first/normalization, target/normalization)
    second = (ell[:, 1]-2*ell[:, 0]+ell[:, 2])/(delta**2*dimension)
    second_loss = nn.functional.smooth_l1_loss(second, ratio[:, 0])
    common = mean_loss + .05*risk + evidence
    consistency = first_loss + second_loss
    total = common + (.1*consistency if model.variant == 'consistency' else 0)
    return dict(total=total, common=common, mean_mse=mean_loss, variance_risk=risk,
                evidence_bce=evidence, derivative_mean=first_loss,
                derivative_variance=second_loss, consistency=consistency)


class CalibratedMoments:
    def __init__(self, original, evidence, calibration):
        self.original = original
        self.original_evidence = evidence
        self.calibration = calibration.cpu().eval().requires_grad_(False)
        self.cache = None
        self.diagnostics = []

    def __getattr__(self, key):
        return getattr(self.original, key)

    def infer(self, query, variance):
        if self.cache is not None:
            raise AssertionError('Previous calibrated evidence was not consumed')
        raw = self.original.infer(query, variance)
        ell = self.original_evidence.infer(query, variance, raw.mean)
        v = np.asarray(variance, float)
        if not np.allclose(v, v[0], rtol=1e-12, atol=0):
            raise ValueError('Candidate uses the native shared query variance')
        c = covariance_from_query(query, float(v[0]))
        x = feature_values(query, v, raw.mean, raw.variance, ell, c)
        with torch.inference_mode():
            a, t, l = self.calibration(torch.from_numpy(x),
                torch.tensor(raw.variance/v, dtype=torch.float32),
                torch.tensor(ell, dtype=torch.float32))
        a, t, l = [value.numpy().astype(float) for value in (a, t, l)]
        self.cache = (np.array(query, copy=True), v.copy(), l)
        self.diagnostics.append(dict(alpha_quantiles=np.quantile(a, [0, .5, 1]).tolist(),
            variance_ratio_quantiles=np.quantile(t, [0, .5, 1]).tolist(),
            raw_ratio_outside_bounds=int(np.sum((raw.variance/v<1e-5)|(raw.variance/v>1-1e-5))),
            covariance_largest_eigen_fraction=float(np.linalg.eigvalsh(c)[-1]/np.trace(c).real)))
        return MatrixMomentEstimate(query+a[:, None, None, None]*(raw.mean-query), v*t)


class CalibratedEvidence:
    def __init__(self, moments):
        self.moments = moments
        self.noise_support = moments.original_evidence.noise_support
        self.training_class_prior = moments.original_evidence.training_class_prior

    def infer(self, query, variance, mean):
        # The frozen classifier saw its own same-query frozen score mean above.
        # Feeding the calibrated mean to that classifier would be a new mismatch.
        if self.moments.cache is None:
            raise AssertionError('No matching calibrated query')
        r, v, ell = self.moments.cache
        if not np.array_equal(r, query) or not np.array_equal(v, variance):
            raise AssertionError('Calibrated evidence belongs to another query')
        self.moments.cache = None
        return ell
