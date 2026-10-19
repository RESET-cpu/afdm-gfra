"""Zhao et al., TVT 74(3), 2025, pp. 4117-4131, Algorithm 1.

Full-resolution special case: alpha_m=1, Eqs. (20)-(30), (36), (49).
There is one undamped GAMP sweep followed by EM updates per iteration.
The scalar BG prior has zero mean, a separate beta for each entry, and a
single lambda refined by averaging all scalar posterior support probabilities.
This is not the shared-row BG denoiser or nested Vila EM-GAMP implementation.

Two inconsistencies in the printed paper are exposed, not silently copied:
* Eq. (40) is pi*(|active_mean|^2+active_variance), whereas the EM stationary
  equation (38), with derivative (39), gives the conditional second moment.
  The current implementation uses Eq. (38); the printed-form audit is archived.
* Eq. (56)'s log of a determinant difference contradicts Eqs. (51), (55).
  Detection evaluates the Gaussian log likelihood ratio in (51), (55).

AFDM adaptation: dictionary columns replace flat-fading pilot columns;
AP columns become antenna columns. A user's multi-path coefficient block
uses the sum of the same Gaussian log likelihoods under a diagonal covariance.
The effective variance is estimated by GAMP nu^r; no channel truth is used.
The paper does not supply numerical initial parameters or Tmax. They are
explicit project settings. Alpha=1, zero mean and undamped updates are native.
"""
from copy import deepcopy
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from scipy.special import expit

from afdm_jadcedd.project import ROOT
from afdm_jadcedd.system.dictionary import AFDMGrid
from afdm_jadcedd.system.observation import ReceiverInput, load_input
from afdm_jadcedd.utils import sha256, write_json

METHOD = 'em_gamp_zhao2025'
PAPER = 'references/zhao2025_mixed_fronthaul_jadce.pdf'
PAPER_SHA256 = 'd92d9dfac44ba6fd17cc6963fcab4c664a976a73a75117f39412b8fe95621fb6'


@dataclass(frozen=True)
class ZhaoControls:
    iterations: int = 1000
    initial_noise_fraction: float = .1
    variance_floor: float = 1e-12
    probability_floor: float = 1e-12
    beta_update: str = 'eq38_stationary'

    def __post_init__(self):
        if (not isinstance(self.iterations, int) or self.iterations < 1
                or not 0 < self.initial_noise_fraction < 1
                or not np.isfinite(self.variance_floor) or self.variance_floor <= 0
                or not 0 < self.probability_floor < .5
                or self.beta_update != 'eq38_stationary'):
            raise ValueError('invalid explicit Zhao Algorithm 1 controls')


def scalar_bg_moments(r, phi, beta, rate):
    """Proper-complex scalar Eq. (29)-(30), without row probability pooling."""
    r, phi, beta = np.asarray(r), np.asarray(phi), np.asarray(beta)
    if (r.shape != phi.shape or r.shape != beta.shape
            or not 0 < rate < 1 or np.any(phi <= 0) or np.any(beta <= 0)):
        raise ValueError('matched scalar pseudo-observations and positive variances required')
    weight = beta/(phi+beta)
    active_mean = weight*r
    active_variance = phi*weight
    log_bayes = -np.log1p(beta/phi) + abs(r)**2*weight/phi
    pi = expit(np.log(rate)-np.log1p(-rate)+log_bayes)
    mean = pi*active_mean
    variance = pi*active_variance + pi*(1-pi)*abs(active_mean)**2
    return mean, variance, pi, active_mean, active_variance


def em_updates(pi, active_mean, active_variance, y, z_mean, z_variance,
               *, beta_update='eq38_stationary'):
    """Eq. (36), its across-column refinement, Eq. (38), and Eq. (49)."""
    conditional_second = abs(active_mean)**2 + active_variance
    if beta_update != 'eq38_stationary':
        raise ValueError('The selected Zhao update follows Eq. (38)')
    beta = conditional_second
    rates = pi.mean(axis=0)
    noise = (abs(y-z_mean)**2+z_variance).mean(axis=0)
    return float(rates.mean()), beta, noise, rates


def gaussian_block_llr(coefficients, beta, effective_variance, users):
    """Eqs. (51), (53)-(55): log p(x|active)-log p(x|inactive).

    One row per user in the flat-fading paper. AFDM groups that user's grid
    rows into one diagonal Gaussian block. No prior odds or fitted threshold.
    The log-determinant ratio is invariant to a change of coefficient units.
    """
    x, b, v = map(np.asarray, (coefficients, beta, effective_variance))
    if (x.ndim != 2 or x.shape != b.shape or x.shape != v.shape
            or not isinstance(users, int) or users < 1 or len(x) % users
            or np.any(b <= 0) or np.any(v <= 0)
            or not all(np.isfinite(a).all() for a in (x, b, v))):
        raise ValueError('finite coefficient blocks with positive diagonal covariance required')
    entry_llr = abs(x)**2*(b/(v+b))/v - np.log1p(b/v)
    score = entry_llr.reshape(users, -1, x.shape[1]).sum(axis=(1, 2))
    return score, score > 0


def solve_zhao(design, received, activity_prior, *, controls=None, observer=None):
    """Algorithm 1, one E/M step per sweep, fixed Tmax and no damping."""
    c = controls or ZhaoControls()
    a, y = np.asarray(design, complex), np.asarray(received, complex)
    if (a.ndim != 2 or y.ndim != 2 or a.shape[0] != y.shape[0]
            or not all(a.shape) or not all(y.shape) or not 0 < activity_prior < 1
            or not all(np.isfinite(z).all() for z in (a, y))):
        raise ValueError('finite MMV design and observations with a public activity prior required')
    a2 = np.ascontiguousarray(abs(a)**2)
    ah = np.ascontiguousarray(a.conj().T)
    a2t = np.ascontiguousarray(a2.T)
    energy = (abs(y)**2).mean(axis=0)
    rate = float(activity_prior)
    noise = np.maximum(c.initial_noise_fraction*energy, c.variance_floor)
    initial_beta = np.maximum((1-c.initial_noise_fraction)*energy /
        (rate*a2.sum(axis=1).mean()), c.variance_floor)
    beta = np.broadcast_to(initial_beta, (a.shape[1], y.shape[1])).copy()
    mean = np.zeros(beta.shape, complex)
    variance = rate*beta
    message = np.zeros_like(y)
    trace = []
    for t in range(1, c.iterations+1):
        # Algorithm 1 steps 4-5, Eqs. (27)-(28).
        vp = np.maximum(a2@variance, c.variance_floor)
        p = a@mean-vp*message
        # Steps 6-9, full-resolution Eq. (20)-(21).
        denominator = vp+noise[None, :]
        z_mean = (noise[None, :]*p+vp*y)/denominator
        z_variance = vp*noise[None, :]/denominator
        message = (y-p)/denominator
        message_precision = 1/denominator
        # Steps 10-13. The complex observation model requires conjugate A.
        phi = 1/np.maximum(a2t@message_precision, c.variance_floor)
        r = mean+phi*(ah@message)
        old_mean = mean
        mean, variance, pi, active_mean, active_variance = scalar_bg_moments(r, phi, beta, rate)
        # Steps 14-16: all updates from the SAME current E step.
        rate_next, beta_next, noise_next, rates = em_updates(pi, active_mean,
            active_variance, y, z_mean, z_variance, beta_update=c.beta_update)
        row = dict(iteration=t, mean_change=float(np.linalg.norm(mean-old_mean)),
            rate=rate, next_rate=rate_next,
            beta_min=float(beta_next.min()), beta_max=float(beta_next.max()),
            next_noise_variance=noise_next.tolist(),
            mean_posterior_probability=float(pi.mean()))
        if not all(np.isfinite(z).all() for z in
                (mean, variance, phi, r, beta_next, noise_next)):
            raise FloatingPointError(f'nonfinite undamped Zhao state at iteration {t}')
        trace.append(row)
        if observer is not None:
            observer(row, mean)
        # Keep parameters used by the last posterior separate from next M step.
        posterior_beta = beta
        posterior_noise = noise
        posterior_rate = rate
        rate = float(np.clip(rate_next, c.probability_floor, 1-c.probability_floor))
        beta = np.maximum(beta_next, c.variance_floor)
        noise = np.maximum(noise_next, c.variance_floor)
        variance = np.maximum(variance, c.variance_floor)
    return dict(mean=mean, variance=variance, pseudo_mean=r, pseudo_variance=phi,
        posterior_probability=pi, posterior_beta=posterior_beta,
        posterior_noise=posterior_noise, posterior_rate=posterior_rate,
        next_beta=beta, next_noise=noise, next_rate=rate, next_rates=rates,
        initial_beta=initial_beta, initial_noise=c.initial_noise_fraction*energy,
        iterations=c.iterations, stopping_reason='FIXED_TMAX', trace=trace)


def inference_sources():
    paths = [Path(__file__), Path(__file__).with_name('receiver.py'),
             ROOT/PAPER, ROOT/'src/afdm_jadcedd/utils.py']
    paths += sorted((ROOT/'src/afdm_jadcedd/system').rglob('*.py'))
    return {str(p.relative_to(ROOT)): sha256(p) for p in paths}


def inference_signature(configuration):
    recipe = dict(dictionary=configuration['dictionary'],
        settings=configuration['methods'][METHOD], source_sha256=inference_sources())
    return hashlib.sha256(json.dumps(recipe, sort_keys=True,
        separators=(',', ':'), allow_nan=False).encode()).hexdigest()


class ZhaoGAMPReceiver:
    def __init__(self, configuration):
        from .receiver import GRID
        cfg = deepcopy(configuration)
        setting = cfg['methods'][METHOD]
        if (cfg.get('dictionary') != GRID
                or cfg.get('channel_output') != 'dictionary_reconstruction'
                or setting.get('noise_mode') != 'learned_per_column'
                or setting.get('activity_statistic') != 'zhao_eq51_gaussian_block_llr'
                or setting.get('activity_threshold') != 0
                or setting.get('activity_comparator') != '>'
                or setting.get('effective_variance') != 'gamp_pseudo_variance'
                or setting.get('detector_input') != 'posterior_mean'
                or sha256(ROOT/PAPER) != PAPER_SHA256):
            raise ValueError('explicit full-resolution Zhao recipe and source PDF required')
        self.configuration = cfg
        self.controls = ZhaoControls(**setting['solver'])

    def infer(self, inputs, *, observer=None):
        if not isinstance(inputs, ReceiverInput):
            raise ValueError('public ReceiverInput required')
        started = time.perf_counter()
        cfg = self.configuration
        grid = AFDMGrid.from_operator(inputs.operator, **cfg['dictionary'])
        y = grid.stack(inputs.observation)
        result = solve_zhao(grid.design, y, inputs.activity_prior,
            controls=self.controls, observer=observer)
        z = result['mean']/grid.norms[:, None]
        # Use last M-step beta for the final decision after Algorithm 1 step 18.
        physical_beta = result['next_beta']/grid.norms[:, None]**2
        physical_phi = result['pseudo_variance']/grid.norms[:, None]**2
        score, decision = gaussian_block_llr(z, physical_beta, physical_phi, grid.users)
        arrays = dict(estimate=grid.reconstruct(result['mean']), coefficients=z,
            activity_score=score, activity_decision=decision,
            coefficient_energy=(abs(z.reshape(grid.users, len(grid.atoms), -1))**2).mean(axis=(1, 2)),
            learned_beta=physical_beta, effective_variance=physical_phi,
            posterior_probability=result['posterior_probability'])
        if not all(np.isfinite(value).all() for value in arrays.values()):
            raise FloatingPointError('nonfinite Zhao receiver output')
        native = dict(status='COMPLETE', method=METHOD, iterations=result['iterations'],
            stopping_reason=result['stopping_reason'], seconds=time.perf_counter()-started,
            configuration=cfg, controls=asdict(self.controls), trace=result['trace'],
            dictionary=cfg['dictionary'], coefficient_coordinates='physical',
            source_sha256=inference_sources(), inference_sha256=inference_signature(cfg),
            truth_loaded=False, activity_count_or_truth_used=False,
            supplied_noise_variance_used=False, supplied_activity_prior_used=True,
            noise_mode='learned_per_column', slab_mean=0., damping=1.,
            learned_noise_variance=result['next_noise'].tolist(), learned_rate=result['next_rate'],
            posterior_noise_variance=result['posterior_noise'].tolist(),
            posterior_rate=result['posterior_rate'], initial_beta=result['initial_beta'].tolist(),
            activity_statistic='zhao_eq51_gaussian_block_llr',
            activity_comparator='>', activity_threshold=0.,
            threshold_status='analytic_equal_likelihood_zero_no_calibration',
            activity_provenance='Zhao p.4125 Eqs.(51),(53)-(55); AFDM diagonal block extension',
            effective_variance_provenance='GAMP Eq.(24) nu^r; empirical covariance estimate for Eq.(52), not oracle state evolution',
            source_formula_resolution=cfg['methods'][METHOD]['source_formula_resolution'])
        return arrays, native

    def run(self, input_path, output_path):
        output = Path(output_path)
        if output.suffix != '.npz' or output.exists() or output.with_suffix('.json').exists():
            raise ValueError('fresh .npz output required')
        arrays, native = self.infer(load_input(input_path))
        output.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(output, **arrays)
        native.update(input_sha256=sha256(input_path), output_sha256=sha256(output))
        write_json(output.with_suffix('.json'), native)
        return native
