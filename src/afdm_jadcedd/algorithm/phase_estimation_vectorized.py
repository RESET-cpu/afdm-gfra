"""Candidate implementation of the shared observation-only phase estimator.

A single physical AFDM path per candidate user approximates the dominant path.
Coarse frame-phase correlations initialize a search over all Doppler aliases.
Physical delay/Doppler refinement minimizes a separable nonlinear least-squares
objective with complex antenna gains eliminated analytically. Two cyclic sweeps
and joint gain refits account for multiuser interference. The final receivers
retain their own full channel model; only estimated frame slopes are passed on.

This is a project adaptation, not Shen's EM receiver or the MNOMP algorithm.
Variable projection: O'Leary & Rust, Sec.1 Eqs.(2)-(3), Sec.2 Eqs.(5)-(7).
"""
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from scipy.optimize import minimize

from afdm_jadcedd.algorithm.baselines.offgrid.atoms import sampling_grid, delay_bounds, ORDER
from afdm_jadcedd.system import config as cfg
from afdm_jadcedd.system.phase import wrap
from afdm_jadcedd.utils import sha256
from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput, FRAME_DURATION_S
from afdm_jadcedd.algorithm.phase_candidate_atoms import sensed_atom
from afdm_jadcedd.project import ROOT


@dataclass(frozen=True)
class Controls:
    phase_bins: int = 128
    screening_doppler_step: float = .5
    candidates: int = 3
    alias_refinements: int = 12
    sweeps: int = 2
    refinement_iterations: int = 25
    batched_correlations: bool = False
    local_second_sweep: bool = False


def signature(controls):
    sources = [Path(__file__), ROOT/'src/afdm_jadcedd/algorithm/unknown_phase_model.py',
               ROOT/'src/afdm_jadcedd/algorithm/phase_candidate_atoms.py',
               ROOT/'src/afdm_jadcedd/algorithm/phase_candidate_screening.py',
               ROOT/'src/afdm_jadcedd/algorithm/baselines/offgrid/atoms.py',
               ROOT/'src/afdm_jadcedd/system/config.py', ROOT/'src/afdm_jadcedd/system/phase.py']
    payload = dict(controls=asdict(controls), sources={p.name: sha256(p) for p in sources},
                   model='One dominant physical path per candidate user; complex antenna gains unconstrained')
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def coarse_scores(raw, received, phase_bins, batched=False):
    """Squared matched-filter correlations for exp(+j q beta), via FFT."""
    if batched:
        c = (raw.transpose(1, 0, 2).conj() @ received).transpose(1, 0, 2)
    else:
        c = np.einsum('gqr,qrm->gqm', raw.conj(), received, optimize=False)
    spectrum = np.fft.fft(c, n=phase_bins, axis=1)
    norms = np.sum(abs(raw)**2, axis=(1, 2))
    return np.sum(abs(spectrum)**2, axis=2)/norms[:, None]


def objective(position, pilot, user, received):
    """Exact gradient of min_gain ||received - atom(position) gain||_F^2."""
    atom, first, _ = sensed_atom(pilot, user, position, derivatives=True)
    norm = np.vdot(atom, atom).real
    gain = np.einsum('l,lm->m', atom.conj(), received, optimize=False)/norm
    residual = received - atom[:, None]*gain[None]
    gradient = np.array([-2*np.vdot(d[:, None]*gain[None], residual).real for d in first])
    return float(np.sum(abs(residual)**2)), gradient


def refine(pilot, user, received, position, controls):
    lo, hi = delay_bounds(position[0])
    frequency_step = 1/(controls.phase_bins*cfg.DELTA_F_HZ*FRAME_DURATION_S)
    limit = cfg.NU_MAX_HZ/cfg.DELTA_F_HZ
    bounds = [(lo, hi), (max(-limit, position[1]-2*frequency_step), min(limit, position[1]+2*frequency_step))]
    scale = np.array([1/ORDER, frequency_step])
    center = np.asarray(position, float)
    energy = max(float(np.sum(abs(received)**2)), np.finfo(float).tiny)

    def function(z):
        loss, gradient = objective(center+scale*z, pilot, user, received)
        return loss/energy, gradient*scale/energy

    scaled_bounds = [(float((low-center[j])/scale[j]), float((high-center[j])/scale[j]))
                     for j, (low, high) in enumerate(bounds)]
    fitted = minimize(function, np.zeros(2), jac=True, bounds=scaled_bounds, method='L-BFGS-B',
                      options=dict(maxiter=controls.refinement_iterations, ftol=1e-12, gtol=1e-8))
    position = center+scale*fitted.x
    atom = sensed_atom(pilot, user, position)
    gain = np.einsum('l,lm->m', atom.conj(), received, optimize=False)/np.vdot(atom, atom).real
    return position, atom, gain, dict(success=bool(fitted.success), status=int(fitted.status),
                                    message=str(fitted.message), iterations=int(fitted.nit))


def candidates(raw, received, coordinates, controls):
    scores = coarse_scores(raw, received, controls.phase_bins, controls.batched_correlations)
    delays = np.unique(coordinates[:, 0]); frequencies = len(coordinates)//len(delays)
    # The within-frame coarse Doppler is used only for screening. The next
    # stage enforces the physical Doppler/frame-phase relationship exactly.
    combined = scores.reshape(len(delays), frequencies, controls.phase_bins).max(axis=1)
    selected = []
    for _ in range(controls.candidates):
        d, phase = np.unravel_index(np.argmax(combined), combined.shape)
        selected.append((float(delays[d]), 2*np.pi*phase/controls.phase_bins, float(combined[d, phase])))
        combined[d, (phase+np.arange(-2, 3)) % controls.phase_bins] = -np.inf
    return selected


from afdm_jadcedd.algorithm.phase_candidate_screening import physical_candidates


def estimate(inputs, controls=Controls(), observer=None):
    if not isinstance(inputs, UnknownPhaseInput):
        raise TypeError('UnknownPhaseInput required; no effective operator or truth accepted')
    if (controls.phase_bins < inputs.pilot.shape[0]
            or min(controls.sweeps, controls.candidates, controls.alias_refinements, controls.refinement_iterations) < 1):
        raise ValueError('Positive search budgets and sufficient phase bins required')
    start = time.monotonic()
    pilot = inputs.pilot
    frames, users, _ = pilot.shape
    y3 = inputs.observation.transpose(0, 2, 1)
    y = y3.reshape(-1, y3.shape[-1])
    atoms, coordinates, _ = sampling_grid(controls.screening_doppler_step)
    # Cache only the raw-pilot, within-frame coarse atoms, about 128 MB at K40.
    raw = np.einsum('qkn,grn->kgqr', pilot, atoms, optimize=False)
    initial_scores = []
    for user in range(users):
        initial_scores.append(float(coarse_scores(raw[user], y3, controls.phase_bins,
                                                controls.batched_correlations).max()))
    order = np.argsort(-np.asarray(initial_scores), kind='stable')
    positions = np.zeros((users, 2)); gains = np.zeros((users, y.shape[1]), complex)
    design = np.zeros((len(y), users), complex)
    prediction = np.zeros_like(y)
    trace, refinements = [], []
    for sweep in range(controls.sweeps):
        before = float(np.sum(abs(y-prediction)**2))
        for user in order:
            old = design[:, user, None]*gains[user, None, :]
            residual = y-prediction+old
            if sweep and controls.local_second_sweep:
                starts = [positions[user].copy()]
            else:
                peaks = candidates(raw[user], residual.reshape(y3.shape), coordinates, controls)
                starts = physical_candidates(pilot, int(user), residual, peaks, controls,
                                             positions[user] if sweep else None)
            best, optimization_status = None, []
            for initial in starts:
                result = refine(pilot, int(user), residual, initial, controls)
                loss = float(np.sum(abs(residual-result[1][:, None]*result[2][None])**2))
                optimization_status.append(result[3])
                if best is None or loss < best[0]:
                    best = (loss, result)
            position, atom, gain, status = best[1]
            old_error = float(np.sum(abs(residual-old)**2))
            fitted = atom[:, None]*gain[None]
            new_error = float(np.sum(abs(residual-fitted)**2))
            accepted = new_error <= old_error + 1e-12*max(1., old_error)
            if accepted:
                prediction += fitted-old
                design[:, user] = atom; gains[user] = gain; positions[user] = position
            refinements.append(dict(sweep=sweep, user=int(user), accepted=accepted,
                                    attempted_candidates=len(starts), candidate_status=optimization_status, **status))
        gains, _, rank, singular = np.linalg.lstsq(design, y, rcond=None)
        prediction = np.einsum('lk,km->lm', design, gains, optimize=False)
        after = float(np.sum(abs(y-prediction)**2))
        if not after <= before+1e-10*max(1., before):
            raise FloatingPointError('Phase fitting increased the observation objective')
        row = dict(sweep=sweep+1, residual_energy=after, previous_residual_energy=before,
                   dictionary_rank=int(rank), seconds=time.monotonic()-start)
        trace.append(row)
        if observer is not None:
            observer(row)
    doppler = positions[:, 1]*cfg.DELTA_F_HZ
    slopes = wrap(2*np.pi*doppler*FRAME_DURATION_S)
    if not np.isfinite(slopes).all() or not np.isfinite(gains).all():
        raise FloatingPointError('Nonfinite phase estimator output')
    arrays = dict(phase_slopes=slopes, doppler_hz=doppler, folded_delay_samples=positions[:, 0],
                  path_gains=gains, fitted_observation=prediction.reshape(y3.shape).transpose(0, 2, 1))
    record = dict(status='COMPLETE', seconds=time.monotonic()-start, controls=asdict(controls),
                  inference_sha256=signature(controls), input_fields=list(inputs.arguments()),
                  truth_used_in_inference=False, known_activity_used=False, shared_between_methods=True,
                  phase_model='one physical Doppler per candidate user',
                  channel_approximation='one dominant path per candidate user for phase fitting only',
                  phase_for_inactive_users='not identifiable; estimates retained without oracle filtering',
                  trace=trace, refinements=refinements,
                  final_residual_to_public_noise_energy=trace[-1]['residual_energy']/(y.size*inputs.noise_variance))
    return arrays, record
