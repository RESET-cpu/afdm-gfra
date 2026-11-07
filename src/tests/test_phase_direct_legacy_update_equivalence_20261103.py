"""Separate the exact Q-dimensional reduction from M-step budget changes.

Both paths use the legacy max-ten-sweep, 1e-7-tolerance rotation solver.
Synthetic Gaussian messages only; no receiver, network or truth input.
"""
import json
import time

import numpy as np
import pytest
from threadpoolctl import threadpool_limits

from algorithm.C_STMP_phase_direct_20261103.moments import conditional_quadratic, marginal_value
from algorithm.C_STMP_phase_direct_20261103.phase import update as direct_update
from algorithm.proposed.phase_math import observed_covariances
from algorithm.proposed.phase_update import update, update_rotations


def _case(seed, q, k, n, m, rows):
    rng = np.random.default_rng(seed)
    normal = lambda shape: (rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)
    observation, pilot = normal((q, m, rows)), normal((q, k, n))/np.sqrt(n)
    mean, beta = normal((k, m, rows, n))*.7, rng.uniform(-np.pi, np.pi, k)
    return observation, pilot, mean, .37, .21, beta


def _legacy_arguments(case):
    y, pilot, mean, variance, noise, beta = case
    q, k, n = pilot.shape
    m, rows = y.shape[1:]
    gram = observed_covariances(pilot, np.eye(rows*n))
    frames = np.repeat(np.arange(q), rows)
    projected = np.einsum('qkn,kmrn->kqrm', pilot, mean).reshape(k, q*rows, m)
    projected *= np.exp(1j*beta[:, None]*frames)[:, :, None]
    return gram, projected, y.transpose(0, 2, 1).reshape(q*rows, m), noise, frames, beta, variance


def _legacy(case):
    return update(*_legacy_arguments(case))


def _reduced_with_legacy_solver(case):
    y, pilot, mean, variance, noise, beta = case
    gram, matched, details = conditional_quadratic(*case)
    next_beta, angle, solver = update_rotations(beta, gram, matched,
                                               max_sweeps=10, relative_tolerance=1e-7)
    before = marginal_value(*case)
    after = marginal_value(y, pilot, mean*np.exp(1j*angle)[:, None, None, None],
                           variance, noise, next_beta)
    return next_beta, angle, dict(before=before, after=after, conditional_quadratic=solver,
                                  moments=details)


@pytest.mark.parametrize('seed,q,k,n,m,rows', [(67, 5, 3, 4, 3, 2), (101, 8, 5, 4, 2, 6)])
def test_q_reduction_matches_full_update_with_identical_legacy_m_step(seed, q, k, n, m, rows):
    case = _case(seed, q, k, n, m, rows)
    with threadpool_limits(limits=1):
        old_beta, old_angle, old = _legacy(case)
        beta, angle, reduced = _reduced_with_legacy_solver(case)
        production_beta, production_angle, production = direct_update(
            *case, solver_kind='legacy_coordinate', fit_offset=True)
    np.testing.assert_allclose(np.angle(np.exp(1j*(beta-old_beta))), 0., atol=2e-10, rtol=0.)
    np.testing.assert_allclose(np.angle(np.exp(1j*(angle-old_angle))), 0., atol=2e-10, rtol=0.)
    old_solver, solver = old['conditional_quadratic'], reduced['conditional_quadratic']
    assert solver['sweeps'] == old_solver['sweeps']
    assert solver['converged'] == old_solver['converged']
    np.testing.assert_allclose(solver['objectives'], old_solver['objectives'], rtol=2e-11, atol=2e-10)
    np.testing.assert_allclose(solver['normalized_gains'], old_solver['normalized_gains'], rtol=2e-8, atol=2e-12)
    for key in ('before', 'after'):
        np.testing.assert_allclose(old[key], rows*reduced[key], rtol=2e-11, atol=2e-10)
    np.testing.assert_allclose(old['before']-old['after'],
        rows*(reduced['before']-reduced['after']), rtol=2e-10, atol=2e-10)
    assert reduced['after'] <= reduced['before']+1e-10
    np.testing.assert_allclose(np.angle(np.exp(1j*(production_beta-old_beta))), 0., atol=2e-10, rtol=0.)
    np.testing.assert_allclose(np.angle(np.exp(1j*(production_angle-old_angle))), 0., atol=2e-10, rtol=0.)
    np.testing.assert_allclose(production['conditional_quadratic']['objectives'], old_solver['objectives'],
                               rtol=2e-11, atol=2e-10)
    assert production['conditional_quadratic']['sweeps'] == old_solver['sweeps']
    for key in ('before', 'after'):
        np.testing.assert_allclose(old[key], rows*production[key], rtol=2e-11, atol=2e-10)


def test_informal_warm_kernel_timing_is_recorded_without_a_speed_threshold(record_property):
    # This is not a receiver benchmark. Cache the legacy observation Gram as
    # its receiver does. Both timed paths include posterior projected moments,
    # the identical legacy M-step, and before/after NLL checks.
    dimensions = dict(q=8, k=5, n=4, m=3, rows=6)
    case = _case(409, **dimensions)
    seconds = dict(full_qr=[], reduced_q=[])
    with threadpool_limits(limits=1):
        cached_arguments = _legacy_arguments(case)
        old_call = lambda unused: update(*cached_arguments)
        old_call(case)
        _reduced_with_legacy_solver(case)
        for _ in range(3):
            for name, function in [('full_qr', old_call), ('reduced_q', _reduced_with_legacy_solver)]:
                started = time.perf_counter()
                function(case)
                seconds[name].append(time.perf_counter()-started)
    result = dict(dimensions=dimensions, repeats=3, blas_threads=1,
                  matrix_orders=dict(full_qr=48, reduced_q=8),
                  legacy_observation_gram_cached=True,
                  m_step='Identical legacy max_sweeps=10, relative_tolerance=1e-7',
                  seconds=seconds, median_seconds={name:float(np.median(value)) for name,value in seconds.items()},
                  scope='Informal synthetic warm-kernel timing, not end-to-end receiver speed')
    print(json.dumps(result, sort_keys=True))
    record_property('informal_kernel_timing', json.dumps(result, sort_keys=True))
    assert all(np.isfinite(value).all() and min(value) > 0 for value in seconds.values())
