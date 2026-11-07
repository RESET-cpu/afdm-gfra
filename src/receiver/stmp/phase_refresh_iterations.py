"""Candidate: update feedback phase and recompute the paired linear query."""
import time

import numpy as np

from receiver.frontend.phase_math import observed_covariances
from receiver.frontend.phase_update import update as update_phase
from channel.phase import phase_operator
from receiver.stmp.gaussian import gaussian_extrinsic
from receiver.stmp.gaussian import hermitian
from receiver.stmp.iterations import moment_damp
from receiver.stmp.iterations import _iteration_changes
from receiver.stmp.iterations import _stopping_step
from receiver.stmp.iterations import _message_diagnostics
from receiver.stmp.linear import SpatialLinear
from receiver.stmp.records import SpatialResult
from receiver.stmp.phase_stopping import CycleStopping


def infer(inputs, denoiser, *, scale, initial_variance, controls,
          phase_configuration, initial_slopes, observer=None, decision_threshold=.5):
    if phase_configuration["stopping"].get("allow_original_stopping") is not True:
        raise ValueError("Combined stopping must retain the original exit")
    if phase_configuration.get("state_update") != "feedback_and_new_query":
        raise ValueError("This candidate refreshes the linear query after phase changes")
    controls.validate_stopping()
    if controls.covariance_mode != "isotropic":
        raise ValueError("Phase updates require the isotropic STMP configuration")
    schedule = phase_configuration["periodic_update"]
    start, interval = schedule["start"], schedule["interval"]
    settle = phase_configuration["minimum_iterations_after_last_update"]
    if (any(type(i) is not int or i < 1 for i in (start, interval, settle))
            or settle > interval or start + settle > controls.iterations):
        raise ValueError("Periodic phase updates require positive start/interval and final conditional refinement")
    q, k, n = inputs.pilot.shape
    m, rows = inputs.observation.shape[1:]
    beta = np.asarray(initial_slopes, float).copy()
    if beta.shape != (k,) or not np.isfinite(beta).all():
        raise ValueError("Finite initial phase slope per user required")
    y, noise = inputs.observation / scale, inputs.noise_variance / scale**2
    physical_y = inputs.observation.transpose(0, 2, 1).reshape(q * rows, m)
    frames = np.repeat(np.arange(q), rows)
    started = time.perf_counter()
    gram = observed_covariances(inputs.pilot, np.eye(rows * n))
    linear = SpatialLinear(phase_operator(inputs.pilot, beta), m, noise)
    setup = time.perf_counter() - started
    started = time.perf_counter()
    prior = np.zeros((k, m, rows, n), complex)
    prior_cov = np.eye(m) * max(float(initial_variance), 1e-12)
    old_r = old_v = old_out = old_out_v = old_mean = old_p = None
    stable = fresh = decision_stable = 0
    old_decision = None
    trace, steps = [], []
    reason = "MAX_ITERATIONS"
    last_update = 0
    stopping = CycleStopping(phase_configuration["stopping"],
                             minimum_iterations=controls.min_iterations)

    for iteration in range(1, controls.iterations + 1):
        tick = time.perf_counter()
        _, _, r, v = linear.update(y, prior, prior_cov)
        linear_seconds = time.perf_counter() - tick
        r, v = moment_damp(old_r, old_v, r, v, controls.damping)
        state = denoiser(r, v)
        posterior = hermitian(state.spatial_covariance.mean(axis=0))
        posterior = np.eye(m) * np.trace(posterior).real / m
        out, out_v, fraction, used = gaussian_extrinsic(state.mean, posterior, r, v,
            controls.variance_fraction_floor, controls.variance_fraction_ceiling)
        out, out_v = moment_damp(old_out, old_out_v, out, out_v, controls.damping)
        if not np.isfinite(out).all() or not np.isfinite(out_v).all():
            raise FloatingPointError("Invalid extrinsic output")
        changes = _iteration_changes(state, old_mean, old_p, v, old_v)
        change, estimate_change, activity_change, covariance_change = changes
        stable, fresh, decision_stable, old_decision, converged = _stopping_step(
            controls, iteration, *changes, denoiser.message_fresh, state.activity,
            decision_threshold, stable, fresh, decision_stable, old_decision)
        # Retain the original exit at every iteration and add full-cycle checks
        # in physical coordinates, including the intervening phase update.
        legacy_converged = bool(converged and steps and iteration >= last_update + settle)
        due = iteration >= start and (iteration - start) % interval == 0
        stopping.observe_decisions(state.activity, decision_threshold,
            current_moments=(denoiser.last.get("site_accepted", True)
                             and denoiser.last.get("unsupported_users", 0) == 0))
        check = None
        cycle_converged = False
        converged = legacy_converged
        if due:
            check = stopping.check(iteration, state.mean, state.activity,
                linear.forward(state.mean), v, out_v, noise_energy=noise*y.size)
            cycle_converged = bool(check["stop"] and steps and iteration >= last_update + settle)
            converged = legacy_converged or cycle_converged
        row = dict(iteration=iteration, convergence_change=change, converged=converged,
            estimate_change=estimate_change, activity_change=activity_change,
            input_covariance_change=covariance_change, stable_iterations=stable,
            fresh_iterations=fresh, decision_stable_iterations=decision_stable,
            linear_seconds=linear_seconds, phase_update_due=due,
            phase_updates_completed=len(steps), legacy_converged=legacy_converged,
            cycle_stopping=check,
            stopping_trigger=("original_and_cycle" if legacy_converged and cycle_converged
                else "original" if legacy_converged else "cycle" if cycle_converged else None),
            iterations_since_last_phase_update=iteration-last_update,
            **_message_diagnostics(linear, y, state.mean, v, posterior, fraction, used, noise),
            **denoiser.last)
        trace.append(row)
        if observer is not None:
            observer(row, state, r, v, prior, prior_cov, out, out_v, posterior)
        old_r, old_v, old_out, old_out_v = r, v, out, out_v
        old_mean, old_p = state.mean.copy(), state.activity.copy()

        # Leave a full conditional refinement before the hard iteration limit.
        # Returned channel and phase must describe the same operator.
        if due and not converged and iteration + settle <= controls.iterations:
            tick = time.perf_counter()
            scalar = float(np.trace(out_v).real / m)
            if not np.allclose(out_v, scalar * np.eye(m), rtol=1e-10, atol=1e-12 * scalar):
                raise ValueError("Only the actual isotropic feedback covariance may enter phase fitting")
            physical = out * scale
            projected = np.einsum("qkn,kmrn->kqrm", inputs.pilot, physical,
                                  optimize=True).reshape(k, q * rows, m)
            projected *= np.exp(1j * beta[:, None] * frames)[:, :, None]
            previous_beta = beta.copy()
            beta, angle, step = update_phase(gram, projected, physical_y,
                inputs.noise_variance, frames, beta, scalar * scale**2)
            # Absorb the fitted intercept into this outgoing Gaussian message.
            # Old likelihood queries and neural-site caches were computed in
            # physical H coordinates; they are not transformed along with it.
            old_out = old_out * np.exp(1j * angle)[:, None, None, None]
            # A new operator invalidates the damped likelihood-query history.
            # The next linear update supplies a matched mean/covariance pair;
            # ordinary query damping resumes after that single fresh query.
            old_r = None
            # moment_damp skips both interpolations when old_r is None.
            # Retain old_v only for the physical covariance-change diagnostic.
            rebuild = time.perf_counter()
            linear = SpatialLinear(phase_operator(inputs.pilot, beta), m, noise)
            rebuild_seconds = time.perf_counter() - rebuild
            # These are legacy per-iteration diagnostics. CycleStopping retains
            # full-cycle endpoints and explicitly checks the new operator.
            stable = fresh = decision_stable = 0
            old_decision = None
            denoiser.message_fresh = False
            step["conditional_quadratic"].pop("users", None)
            step.update(after_iteration=iteration, message_variance=scalar * scale**2,
                before_slopes=previous_beta.tolist(), after_slopes=beta.tolist(),
                seconds=time.perf_counter() - tick, linear_rebuild_seconds=rebuild_seconds,
                rotated_cached_means=["feedback"], physical_query_history_retained=False, query_damping_history_reset=True,
                stopping_windows_reset=True)
            steps.append(step)
            last_update = iteration
            row.update(converged=False, phase_update_index=len(steps), stopping_windows_reset=True)
            converged = False
        elif due:
            row["phase_update_skipped"] = ("stopping_criterion_met" if converged
                                           else "final_conditional_refinement")
        prior, prior_cov = old_out, old_out_v
        if converged:
            reason = "CONVERGED"
            break

    result = SpatialResult(state.mean * scale, state.conditional_mean * scale,
        state.activity, state.spatial_covariance * scale**2, tuple(trace), reason,
        setup, time.perf_counter() - started - sum(s["seconds"] for s in steps))
    return result, beta, steps
