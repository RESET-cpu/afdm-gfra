"""Synthetic numerical checks only; no trained networks or formal batch runs."""
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from algorithm.STMP.iterations import run_spatial_score
from algorithm.STMP.records import SpatialConfig
from algorithm.C_STMP_variance_em_20261025.iterations import run_spatial_score as gp_loop
from evaluation.convergence_20261105.adapters import fixed_loop, bind_fixed_infer
from evaluation.convergence_20261105.metrics import Collector, aggregate
from evaluation.convergence_20261105.run import CONFIG, METHODS
from system.observation import ReceiverInput
from utils import read_json


class GaussianFixture:
    message_fresh = True
    last = {}

    def __call__(self, query, covariance):
        mean = .3 * query
        cov = np.broadcast_to(.3 * covariance, (len(query), *covariance.shape)).copy()
        return SimpleNamespace(mean=mean, conditional_mean=mean, spatial_covariance=cov,
                               activity=np.full(len(query), .6))


def small_input():
    rng = np.random.default_rng(211)
    return ReceiverInput(rng.normal(size=(3, 2, 2)) + 1j*rng.normal(size=(3, 2, 2)),
                         rng.normal(size=(3, 2, 2)) + 1j*rng.normal(size=(3, 2, 2)), .8, .1)


def controls():
    return SpatialConfig(iterations=300, min_iterations=2, convergence_patience=1,
                         convergence_tolerance=1e6, covariance_mode='isotropic')


@pytest.mark.parametrize('native', [run_spatial_score, gp_loop], ids=['STMP', 'GP-MP'])
def test_mp_real_loops_keep_prefix_and_execute_300(native):
    observations, saved = [], []
    kwargs = dict(scale=1., initial_variance=.5, config=controls())
    before = native(small_input(), GaussianFixture(), **kwargs,
                    observer=lambda row, state, *args: observations.append(state.mean.copy()))
    modified = fixed_loop(native)
    after = modified(small_input(), GaussianFixture(), **kwargs,
                     observer=lambda row, state, *args: saved.append(state.mean.copy()))
    assert len(before.trace) == 2
    assert len(after.trace) == len(saved) == 300
    assert after.trace[1]['converged']
    assert after.stopping_reason == 'MAX_ITERATIONS'
    for original, current in zip(observations, saved):
        np.testing.assert_array_equal(original, current)
    for a, b in zip(before.trace, after.trace):
        assert {k: v for k, v in a.items() if k != 'linear_seconds'} == {
            k: v for k, v in b.items() if k != 'linear_seconds'}
    assert len(native(small_input(), GaussianFixture(), **kwargs).trace) == 2


class ReceiverFixture:
    def __init__(self):
        self.controls = replace(controls(), iterations=600)
        self.configuration = {'ep': {'iterations': 600}}

    def infer(self, inputs, *, observer=None):
        return run_spatial_score(inputs, GaussianFixture(), scale=1., initial_variance=.5,
                                 config=self.controls, observer=observer)


def test_binding_only_changes_one_instance():
    changed, original = ReceiverFixture(), ReceiverFixture()
    bind_fixed_infer(changed, 300)
    assert changed.infer.__func__.__globals__['run_spatial_score'] is not run_spatial_score
    assert ReceiverFixture.infer.__globals__['run_spatial_score'] is run_spatial_score
    assert len(changed.infer(small_input()).trace) == 300
    assert len(original.infer(small_input()).trace) == 2
    assert original.configuration['ep']['iterations'] == 600


def test_real_sbl_loop_prefix_observer_and_final_reconstruction():
    from algorithm.baseline import offgrid_sbl as kernel
    rng = np.random.default_rng(212)
    inputs = ReceiverInput(rng.normal(size=(2, 2, 16)) + 1j*rng.normal(size=(2, 2, 16)),
                           rng.normal(size=(2, 1, 16)) + 1j*rng.normal(size=(2, 1, 16)), .8)
    settings = kernel.Settings(iterations=300, warmup=1, tolerance=1e6,
                               candidates_per_user=1, offset_candidates=1)
    before = kernel.solve_estimated_noise(inputs, settings)
    images, stopping = [], []

    def observe(state, would_stop):
        a = (state['a0'] + state['derivatives'][0]*state['offsets'][:, 0]
             + state['derivatives'][1]*state['offsets'][:, 1])
        mean, _, _ = kernel.posterior(a, state['y'], state['variance'], state['noise'])
        images.append(kernel.reconstruct(1, 2, state['users'], state['centers'] + state['offsets'],
                                          mean/state['scales'][:, None]))
        stopping.append(would_stop)

    after = fixed_loop(kernel.solve_estimated_noise, observe)(inputs, settings)
    unobserved = fixed_loop(kernel.solve_estimated_noise)(inputs, settings)
    assert before['iterations'] == 2 and after['iterations'] == len(images) == 300
    assert stopping[1]
    assert before['trace'] == after['trace'][:2]
    assert after['trace'] == unobserved['trace']
    np.testing.assert_array_equal(before['estimate'], images[1])
    np.testing.assert_array_equal(after['estimate'], images[-1])
    np.testing.assert_array_equal(after['estimate'], unobserved['estimate'])


def test_collector_rejects_padding_and_checks_final():
    truth = dict(channel=np.ones((2, 1, 1, 1), complex), activity=np.array([True, True]))
    c = Collector(truth, 2)
    h = .5 * truth['channel']
    decision = np.array([True, False])
    for iteration in (1, 2):
        c.add(iteration, h, decision, {}, probability=np.array([.8, .2]), native_would_stop=True)
    c.verify_final(dict(estimate=h, activity_decision=decision))
    with pytest.raises(ValueError, match='no padding'):
        c.add(3, h, decision, {}, probability=np.array([.8, .2]), native_would_stop=True)
    with pytest.raises(AssertionError):
        c.verify_final(dict(estimate=2*h, activity_decision=decision))
    assert c.rows[-1]['nmse_db'] == pytest.approx(10*np.log10(.25))
    assert c.rows[-1]['aer'] == .5


def make_trace(error, energy, decision):
    return dict(iteration=np.arange(1, 301), per_user_error=np.full((300, 2), error),
                decisions=np.broadcast_to(np.array(decision, bool), (300, 2)).copy(),
                truth_activity=np.array([True, False]), signal_energy=np.asarray(energy))


def test_pooled_50_scene_metrics_and_missing_coverage():
    traces = {s: make_trace(1. if s < 25 else 9., 10. if s < 25 else 90., [True, True]) for s in range(50)}
    result = aggregate(traces, list(range(50)), 300)
    np.testing.assert_allclose(result['nmse_db'], 10*np.log10(.2))
    np.testing.assert_array_equal(result['aer'], np.full(300, .5))
    assert result['users'] == 100 and len(result['iteration']) == 300
    with pytest.raises(ValueError, match='paired scenes'):
        aggregate({s: t for s, t in traces.items() if s != 49}, list(range(50)), 300)
    traces[49] = dict(traces[49], iteration=np.arange(1, 300))
    with pytest.raises(ValueError, match='iteration coverage'):
        aggregate(traces, list(range(50)), 300)


def test_energy_weighting_is_not_mean_of_scene_db():
    result = aggregate({0: make_trace(.5, 1., [True, False]), 1: make_trace(.5, 100., [True, False])}, [0, 1], 300)
    np.testing.assert_allclose(result['nmse_db'], 10*np.log10(2/101))
    assert result['nmse_db'][0] != pytest.approx(-10.)


def test_declared_default_protocol():
    config = read_json(CONFIG)
    assert config['scene_count'] == 50 and config['iterations'] == 300 and config['first_scene'] == 0
    assert config['methods'] == METHODS and len(METHODS) == 5
    assert config['runtime']['tf32'] is False and config['early_stopping'] is False
    assert config['phase_mode'] == 'known' and config['noise_mode'] == 'estimated' and config['snr_db'] == 0
