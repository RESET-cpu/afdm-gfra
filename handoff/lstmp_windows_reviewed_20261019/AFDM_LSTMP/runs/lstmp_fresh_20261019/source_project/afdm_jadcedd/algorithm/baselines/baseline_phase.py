"""Shen-inspired posterior phase learning for GAMP-SBL and off-grid SBL.

Keep exp(j*q*beta_k), update a frozen posterior objective, then rerun the same
native conditional solver. This is an AFDM adaptation, not Shen's OTFS receiver.
"""
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import time
import warnings

import numpy as np
from scipy.optimize import minimize_scalar

from .. import phase_estimation
from . import baseline_phase_posterior
from .baseline_phase_posterior import ConditionalReceiver, phase_moments
from ..unknown_phase_model import load_input
from afdm_jadcedd.system.phase import wrap
from afdm_jadcedd.utils import sha256, write_json


@dataclass(frozen=True)
class Controls:
    sweeps: int = 2
    phase_bins: int = 256
    candidates: int = 4
    refinement_iterations: int = 50
    phase_weight: float = 1.

    def __post_init__(self):
        if any(type(v) is not int or v < 1 for v in
               (self.sweeps, self.phase_bins, self.candidates, self.refinement_iterations)):
            raise ValueError('Positive integer phase budgets required')
        if self.candidates > self.phase_bins or not 0 < self.phase_weight <= 1:
            raise ValueError('Valid candidate budget and new-value phase weight required')


def quadratic(slopes, gram, matched):
    q = np.arange(len(gram))[:, None]
    phi = np.exp(1j*q*np.asarray(slopes)[None])
    response = np.einsum('qkl,ql->qk', gram, phi, optimize=False)
    value = float(np.vdot(phi, response).real-2*np.vdot(matched, phi).real)
    gradient = 2*np.sum(q*(phi.conj()*(response-matched)).imag, axis=0)
    return value, gradient


def update_phase(slopes, gram, matched, controls=Controls()):
    """Coordinate search including the old feasible point; circular damping."""
    started = time.perf_counter()
    beta = np.asarray(slopes, float).copy()
    if (gram.shape != (len(matched), len(beta), len(beta)) or matched.shape[1:] != beta.shape
            or controls.phase_bins < len(matched)
            or not all(np.isfinite(x).all() for x in (beta, gram, matched))):
        raise ValueError('Finite compatible phase moments and sufficient search bins required')
    if not np.allclose(gram, gram.conj().transpose(0, 2, 1), rtol=1e-11, atol=1e-11):
        raise ValueError('Hermitian phase quadratic required')
    initial = beta.copy()
    frames = np.arange(len(gram))
    # The diagonal is constant. Removing it avoids cancellation in acceptance.
    coupled = gram.copy()
    coupled[:, np.arange(len(beta)), np.arange(len(beta))] = 0
    before = quadratic(beta, coupled, matched)[0]
    grid = np.arange(controls.phase_bins)*2*np.pi/controls.phase_bins-np.pi
    basis = np.exp(-1j*frames[:, None]*grid[None, :])
    phase = np.exp(1j*frames[:, None]*beta[None, :])
    order = np.argsort(-np.diagonal(gram, axis1=1, axis2=2).real.sum(axis=0), kind='stable')
    trace = []
    scalar_refinement_failures = 0
    for sweep in range(controls.sweeps):
        old_objective = quadratic(beta, coupled, matched)[0]
        accepted = 0
        for k in order:
            correlation = matched[:, k]-np.einsum('ql,ql->q', coupled[:, k, :], phase, optimize=False)
            if not np.any(correlation):
                continue
            scores = np.einsum('q,qg->g', correlation, basis, optimize=False).real
            def loss(value):
                return float(-2*np.real(np.sum(correlation*np.exp(-1j*frames*value))))
            best, best_loss = float(beta[k]), loss(beta[k])
            for index in np.argsort(scores, kind='stable')[-controls.candidates:]:
                center, step = float(grid[index]), 2*np.pi/controls.phase_bins
                fit = minimize_scalar(loss, bounds=(center-step, center+step), method='bounded',
                    options=dict(maxiter=controls.refinement_iterations, xatol=1e-10))
                scalar_refinement_failures += int(not fit.success)
                for candidate in (center, fit.x):
                    candidate = beta[k]+controls.phase_weight*float(wrap(candidate-beta[k]))
                    value = loss(candidate)
                    if np.isfinite(value) and value < best_loss:
                        best, best_loss = float(candidate), value
            if best != beta[k]:
                candidate = beta.copy(); candidate[k] = float(wrap(best))
                if quadratic(candidate, coupled, matched)[0] < quadratic(beta, coupled, matched)[0]:
                    beta = candidate
                    phase[:, k] = np.exp(1j*frames*beta[k])
                    accepted += 1
        after = quadratic(beta, coupled, matched)[0]
        trace.append(dict(sweep=sweep+1, accepted_user_updates=accepted,
                          objective_before=old_objective, objective_after=after))
        if after > old_objective+1e-12*max(1., abs(old_objective)):
            raise FloatingPointError('Phase objective increased')
    return beta, dict(seconds=time.perf_counter()-started, controls=asdict(controls), trace=trace,
        scalar_refinement_failures=scalar_refinement_failures,
        objective_before=quadratic(initial, gram, matched)[0],
        objective_after=quadratic(beta, gram, matched)[0],
        variable_objective_before=before, variable_objective_after=quadratic(beta, coupled, matched)[0],
        max_phase_change=float(abs(wrap(beta-initial)).max(initial=0)), truth_used_in_inference=False)


class BaselinePhaseReceiver:
    def __init__(self, method, phase_weight=1.):
        self.conditional = ConditionalReceiver(method)
        self.method = method
        self.controls = Controls(phase_weight=phase_weight)
        self.initial_controls = phase_estimation.Controls()
        self.signature = hashlib.sha256(json.dumps(dict(method=method, controls=asdict(self.controls),
            base=self.conditional.base.signature, initial=phase_estimation.signature(self.initial_controls),
            source=sha256(Path(__file__)), moments=sha256(Path(baseline_phase_posterior.__file__))),
            sort_keys=True).encode()).hexdigest()

    def initial(self, inputs, slopes):
        """Experiment reuse requires a saved observation-only initializer."""
        return self.conditional.infer(inputs.at_estimated_phase(slopes))

    def refine(self, inputs, slopes, initial_record, posterior):
        started = time.perf_counter()
        moment_start = time.perf_counter()
        gram, matched, covariance_gram = phase_moments(posterior, slopes, inputs.observation)
        moment_seconds = time.perf_counter()-moment_start
        updated, phase_record = update_phase(slopes, gram, matched, self.controls)
        arrays, record, _ = self.conditional.infer(inputs.at_estimated_phase(updated))
        arrays.update(initial_phase_slopes=np.asarray(slopes).copy(), phase_slopes=updated,
                      phase_slope_history=np.stack([slopes, updated]))
        record.update(method=self.method+'_learned_phase', inference_sha256=self.signature,
            phase_update=phase_record, phase_moment_seconds=moment_seconds,
            phase_posterior_model=posterior.model, conditional_runs=2,
            conditional_iterations=[initial_record['iterations'], record['iterations']],
            initial_conditional_seconds=initial_record['seconds'],
            incremental_seconds=time.perf_counter()-started,
            conditional_seconds=initial_record['seconds']+record['seconds'],
            phase_covariance_offdiagonal_norm=float(np.linalg.norm(covariance_gram-
                np.eye(len(slopes))[None]*covariance_gram)),
            stopping_reason_outer='ONE_UPDATE_BUDGET',
            phase_output_scope='Updated slope; no final absolute physical Doppler inferred',
            truth_used_in_inference=False)
        moments = dict(gram=gram, matched=matched, covariance_gram=covariance_gram)
        return arrays, record, moments

    def infer(self, inputs):
        started = time.perf_counter()
        phase, phase_record = phase_estimation.estimate(inputs, self.initial_controls)
        _, initial_record, posterior = self.initial(inputs, phase['phase_slopes'])
        arrays, record, _ = self.refine(inputs, phase['phase_slopes'], initial_record, posterior)
        record.update(initial_phase_estimation=phase_record, phase_seconds=phase_record['seconds'],
                      seconds=time.perf_counter()-started)
        return arrays, record

    def run(self, input_path, output_path):
        output = Path(output_path)
        if output.suffix != '.npz' or output.exists() or output.with_suffix('.json').exists():
            raise ValueError('Fresh .npz output required')
        output.parent.mkdir(parents=True, exist_ok=True)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always', RuntimeWarning)
            arrays, record = self.infer(load_input(input_path))
        np.savez_compressed(output, **arrays)
        record.update(input_sha256=sha256(input_path), output_sha256=sha256(output),
                      warnings=[str(w.message) for w in caught])
        write_json(output.with_suffix('.json'), record)
        return record
