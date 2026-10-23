"""Expose the frozen GAMP/SBL moments used for phase learning.

The off-grid loop mirrors the selected solver and calls its existing numerical
kernels. This separate adapter preserves the frozen solver/readout identities;
native-output parity is tested. It also retains the FINAL linearized dictionary
and Gaussian covariance, which the original public receiver does not export.
"""
from dataclasses import asdict, dataclass
import time

import numpy as np

from .receiver import BaselineReceiver, load_configuration as gamp_configuration
from .gamp_sbl_mmv import MMVControls, solve_mmv
from .ding import coefficient_activity
from .readout import nearest_node, public_snr_db
from .offgrid.receiver import OffGridReceiver, load_configuration as sbl_configuration
from .offgrid import atoms, sbl
from afdm_jadcedd.system.dictionary import AFDMGrid


@dataclass
class Posterior:
    design: np.ndarray
    mean: np.ndarray
    user_ids: np.ndarray
    diagonal_variance: np.ndarray | None = None
    covariance: np.ndarray | None = None
    model: str = ''


def solve_offgrid_with_posterior(inputs, settings):
    """Same fixed-centre SBL iterations/output, plus its final joint posterior."""
    p = np.asarray(inputs.operator, complex)
    y = atoms.stack_observation(inputs.observation)
    coarse, norms, coordinates, spacing = atoms.coarse_dictionary(p, settings.doppler_step)
    score = np.sum(abs(coarse.conj().T@y)**2, axis=1).reshape(p.shape[1], -1)
    count = min(settings.candidates_per_user, len(coordinates))
    indices = np.concatenate([u*len(coordinates)+np.argsort(-score[u], kind='stable')[:count]
                              for u in range(p.shape[1])])
    users = indices//len(coordinates)
    centers = coordinates[indices % len(coordinates)].copy()
    scales = norms[indices]
    a0 = coarse[:, indices].copy()
    coarse_columns = coarse.shape[1]
    del coarse, score, norms
    derivatives = np.empty((2, a0.shape[0], a0.shape[1]), complex)
    for j, (u, position) in enumerate(zip(users, centers)):
        derivatives[:, :, j] = atoms.sensed_atom(p, u, position, True)[1]/scales[j]
    bounds = np.array([atoms.delay_bounds(d)-d for d in centers[:, 0]])
    lower = np.column_stack([bounds[:, 0], np.maximum(-spacing/2, -atoms.MAX_FREQUENCY-centers[:, 1])])
    upper = np.column_stack([bounds[:, 1], np.minimum(spacing/2, atoms.MAX_FREQUENCY-centers[:, 1])])
    offsets = np.zeros_like(centers)
    noise = float(inputs.noise_variance)
    initial = max((np.sum(abs(y)**2)-y.size*noise)/(y.shape[1]*a0.shape[1]), noise*1e-3)
    variance = np.full(a0.shape[1], initial)
    trace, status = [], 'MAX_ITERATIONS'
    for iteration in range(1, settings.iterations+1):
        a = a0+derivatives[0]*offsets[:, 0]+derivatives[1]*offsets[:, 1]
        mean, diagonal, inv_a = sbl.posterior(a, y, variance, noise)
        updated = sbl.variance_update(np.sum(abs(mean)**2, axis=1)+y.shape[1]*diagonal,
                                     y.shape[1], settings.rho)
        updated = np.maximum(updated, np.finfo(float).eps*max(1., initial))
        delta_size = 0.
        if iteration > settings.warmup:
            selected = np.argsort(-updated, kind='stable')[:settings.offset_candidates]
            q, b = sbl.offset_quadratic(a, y, mean, variance, inv_a, derivatives, selected, noise)
            low = (lower[selected]-offsets[selected]).T.reshape(-1)
            high = (upper[selected]-offsets[selected]).T.reshape(-1)
            delta = sbl.bounded_quadratic(q, b, low, high, settings.offset_sweeps).reshape(2, -1).T
            offsets[selected] += delta
            delta_size = float(np.max(abs(delta), initial=0.))
        relative = float(np.linalg.norm(updated-variance)/np.linalg.norm(variance))
        variance = updated
        trace.append(dict(iteration=iteration, variance_relative_change=relative,
                          max_offset_increment=delta_size))
        if iteration > settings.warmup and relative < settings.tolerance and delta_size < settings.tolerance:
            status = 'HYPERPARAMETER_CHANGE'
            break
    a = a0+derivatives[0]*offsets[:, 0]+derivatives[1]*offsets[:, 1]
    mean, _, inv_a = sbl.posterior(a, y, variance, noise)
    positions = centers+offsets
    gains = mean/scales[:, None]
    h = atoms.reconstruct(p.shape[1], y.shape[1], users, positions, gains)
    exact_observation = np.einsum('qkn,kmrn->qmr', p, h, optimize=True)
    exact_y = atoms.stack_observation(exact_observation)
    result = dict(estimate=h, user_ids=users, positions=positions, gains=gains,
        iterations=iteration, stopping_reason=status, trace=trace, coarse_columns=coarse_columns,
        screened_columns=len(indices), residual_energy=float(np.sum(abs(y-exact_y)**2)),
        linearization_relative_error=float(np.linalg.norm(exact_y-a@mean)/max(np.linalg.norm(exact_y), 1e-30)))
    export_start = time.perf_counter()
    covariance = np.diag(variance)-(variance[:, None]*(a.conj().T@inv_a))*variance[None, :]
    covariance = (covariance+covariance.conj().T)/2
    result['posterior_export_seconds'] = time.perf_counter()-export_start
    return result, Posterior(a, mean, users, covariance=covariance,
                            model='Gaussian joint posterior of final fixed-centre linearized SBL model')


class ConditionalReceiver:
    """Preserve each native point estimate, stopping rule and activity readout."""
    def __init__(self, method):
        self.method = method
        if method == 'gamp':
            self.base = BaselineReceiver(gamp_configuration(), method)
        elif method == 'offgrid_sbl':
            self.base = OffGridReceiver(sbl_configuration(), method)
        else:
            raise ValueError('Phase-posterior adapter supports gamp and offgrid_sbl')

    def infer(self, inputs):
        started = time.perf_counter()
        if self.method == 'gamp':
            grid = AFDMGrid.from_operator(inputs.operator, **self.base.configuration['dictionary'])
            y = grid.stack(inputs.observation)
            design = np.ascontiguousarray(grid.design*grid.norms[None, :])
            controls = MMVControls(**self.base.setting['solver'], noise_shape=1+y.size,
                                   noise_rate=y.size*inputs.noise_variance)
            result = solve_mmv(design, y, controls)
            z = result['mean']
            arrays = dict(estimate=grid.reconstruct(z*grid.norms[:, None]), coefficients=z)
            score, energy = coefficient_activity(z, grid.users)
            decision, rule = self.base.readout.decide(inputs, self.method, score, energy)
            arrays.update(activity_score=score, relative_coefficient_score=score,
                          coefficient_energy=energy, activity_decision=decision)
            record = dict(iterations=result['iterations'], stopping_reason=result['stopping_reason'],
                trace=result['trace'], controls=asdict(controls), activity_threshold=rule['threshold'],
                public_numeric_control=rule, activity_statistic='ding_eq27_normalized_coefficient_energy',
                noise_variance_estimate=result['noise_variance'], posterior_export_seconds=0.)
            posterior = Posterior(design, z, np.repeat(np.arange(grid.users), len(grid.atoms)),
                diagonal_variance=result['variance'], model='GAMP factorized Gaussian marginal approximation')
        else:
            result, posterior = solve_offgrid_with_posterior(inputs, self.base.settings)
            score, energy = atoms.activity_score(result['estimate'])
            index = nearest_node(public_snr_db(inputs), self.base.nodes)
            threshold = float(self.base.thresholds[index])
            arrays = dict(estimate=result['estimate'], component_user_ids=result['user_ids'],
                folded_delay_samples=result['positions'][:, 0], doppler_hz=result['positions'][:, 1]*30000.,
                component_coefficients=result['gains'], activity_score=score, channel_energy=energy,
                activity_decision=(score >= threshold)&(energy > 0))
            record = {k:v for k,v in result.items() if k not in ('estimate', 'user_ids', 'positions', 'gains')}
            record.update(activity_threshold=threshold, readout_snr_node_db=float(self.base.nodes[index]),
                          activity_statistic='relative_channel_frobenius_energy')
        if not all(np.isfinite(a).all() for a in arrays.values()):
            raise FloatingPointError('Nonfinite conditional baseline estimate')
        record.update(status='COMPLETE', method=self.method, native_inference_sha256=self.base.signature,
            seconds=time.perf_counter()-started, configuration=self.base.configuration,
            posterior_model=posterior.model, truth_used_in_inference=False,
            threshold_scope='Original frozen readout transferred unchanged to estimated phases')
        return arrays, record, posterior


def phase_moments(posterior, slopes, observation):
    """B[q,k,l]=E[z_qk^H z_ql], b[q,k]=E[z_qk]^H y_q.

The covariance term is M sum_ij (D_k^H D_l)_ij Sigma_ji, not Sigma_ij.
Within-user terms are constant under unit-modulus phase; cross-user terms are
kept. The SBL dictionary is its linearized likelihood, not a plug-in exact atom.
"""
    frames, antennas, samples = observation.shape
    users = len(slopes)
    a, mu, ids = posterior.design, posterior.mean, posterior.user_ids
    if a.shape != (frames*samples, len(ids)) or mu.shape != (len(ids), antennas):
        raise ValueError('Posterior dimensions must match observation')
    if (posterior.covariance is None) == (posterior.diagonal_variance is None):
        raise ValueError('Exactly one covariance representation required')
    raw = a.reshape(frames, samples, -1)*np.exp(-1j*np.arange(frames)[:, None, None]*slopes[ids][None, None, :])
    groups = [np.flatnonzero(ids == k) for k in range(users)]
    z = np.stack([np.einsum('qri,im->qrm', raw[:, :, group], mu[group], optimize=False)
                  for group in groups], axis=-1)
    y = observation.transpose(0, 2, 1)
    mean_gram = np.einsum('qrmk,qrml->qkl', z.conj(), z, optimize=False)
    matched = np.einsum('qrmk,qrm->qk', z.conj(), y, optimize=False)
    covariance_gram = np.zeros_like(mean_gram)
    if posterior.diagonal_variance is not None:
        power = np.sum(abs(raw)**2, axis=1)*posterior.diagonal_variance.sum(axis=1)[None, :]
        for k, group in enumerate(groups):
            covariance_gram[:, k, k] = power[:, group].sum(axis=1)
    else:
        covariance = posterior.covariance
        if covariance.shape != (len(ids), len(ids)):
            raise ValueError('Joint covariance shape mismatch')
        for q in range(frames):
            weighted = antennas*(raw[q].conj().T@raw[q])*covariance.T
            np.add.at(covariance_gram[q], (ids[:, None], ids[None, :]), weighted)
    gram = mean_gram+covariance_gram
    gram = (gram+gram.conj().transpose(0, 2, 1))/2
    if not all(np.isfinite(x).all() for x in (gram, matched, covariance_gram)):
        raise FloatingPointError('Nonfinite phase posterior moments')
    return gram, matched, covariance_gram
