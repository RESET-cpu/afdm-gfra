"""Information boundaries, timing and Gaussian phase-update algebra."""
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from algorithm import registry
from algorithm.proposed import inference, phase_initialization, phase_layers, phase_update
from algorithm.proposed.phase_math import observed_covariances
from evaluation import suite
from evaluation.scenes import DEFAULT
from evaluation.storage import arrays, save_arrays
from system.receiver.unknown_phase import UnknownPhaseInput
from utils import read_json, write_json


@pytest.mark.parametrize('noise_mode', ['known', 'estimated'])
def test_proposed_raw_input_bypasses_shared_phase_and_excludes_truth(tmp_path, monkeypatch, noise_mode):
    raw = UnknownPhaseInput(np.ones((2, 1, 1), complex), np.ones((2, 2, 1), complex), 1., .5)
    truth = dict(phase_slopes=np.array([.2, -.3]), channel=np.ones((2, 1, 1, 1)), activity=[True, False])
    monkeypatch.setattr(suite, 'observation', lambda *a, **k: (raw, truth, dict(generated_noise_variance=.125)))
    monkeypatch.setattr(suite, 'estimated_phase', lambda *a, **k: pytest.fail('External phase called for proposed'))
    specs = registry.select(['proposed', 'somp'], registry.load_catalog(), 'receiver', noise_mode=noise_mode)
    plan = dict(base_seed=1, cache=str(tmp_path), input_identity='synthetic', algorithm_specs=specs,
                model_binding=registry.load_models(), phase_mode='estimated', noise_mode=noise_mode)
    public, _, receipt, folder = suite.method_case(plan, 0, DEFAULT, 'proposed')
    assert isinstance(public, UnknownPhaseInput)
    np.testing.assert_array_equal(public.pilot, raw.pilot)
    assert public.noise_variance == (.125 if noise_mode == 'known' else 1.)
    assert set(public.arguments()) == {'observation', 'pilot', 'noise_variance', 'activity_prior'}
    assert receipt['phase_seconds'] == 0 and receipt['identity']['phase_input'] == 'raw'
    assert not read_json(folder/'PHASE.json')['initialized']
    cached, _, saved, _ = suite.method_case(plan, 0, DEFAULT, 'proposed')
    assert isinstance(cached, UnknownPhaseInput) and receipt == saved
    np.testing.assert_array_equal(cached.pilot, raw.pilot)
    assert specs['somp']['phase_input'] == 'operator'
    known = registry.select(['proposed'], registry.load_catalog(), 'receiver', phase_mode='known')
    assert known['proposed']['phase_input'] == 'operator'


def test_internal_phase_uses_selected_noise_once_and_never_placeholder(monkeypatch):
    receiver = object.__new__(inference.ProposedReceiver)
    receiver.phase_moment = np.eye(1)
    receiver.device, receiver.parameters = 'cpu', 0
    receiver.binding = dict(proposed=dict(phase_moment_sha256='fixture', phase_config_sha256='fixture'))
    observed = []
    monkeypatch.setattr(inference, 'estimate_spatial_noise', lambda y: (.25, dict(source='synthetic')))
    def initialize(y, pilot, noise, moment, rho):
        observed.append(('initial', noise))
        return dict(phase_slopes=np.zeros(2)), dict(seconds=.2, initializer={}, optimization={})
    def layers(model, public, noise, noise_record, beta):
        observed.append(('layers', noise))
        model.last_layers = [np.ones((2, 1, 1, 1))*noise]*10
        return dict(estimate=model.last_layers[-1], probabilities=np.ones(2)), dict(steps=[])
    monkeypatch.setattr(phase_initialization, 'estimate', initialize)
    monkeypatch.setattr(phase_layers, 'infer', layers)
    raw = UnknownPhaseInput(np.ones((2, 1, 1), complex), np.ones((2, 2, 1), complex), .125, .5)
    receiver.noise_mode = 'estimated'
    first, _ = receiver.infer(raw)
    poisoned, record = receiver.infer(replace(raw, noise_variance=12345.))
    np.testing.assert_array_equal(first['estimate'], poisoned['estimate'])
    assert observed == [('initial', .25), ('layers', .25)]*2
    assert not record['truth_used_in_inference']
    receiver.noise_mode = 'known'
    known, record = receiver.infer(raw)
    assert observed[-2:] == [('initial', .125), ('layers', .125)]
    assert record['supplied_noise_variance_used'] and record['truth_used_in_inference']
    assert not np.array_equal(known['estimate'], first['estimate'])


def test_fixed_message_gradient_and_update_reduce_same_likelihood():
    rng = np.random.default_rng(628)
    normal = lambda shape: rng.normal(size=shape)+1j*rng.normal(size=shape)
    pilot = normal((4, 3, 2))
    gram = observed_covariances(pilot, np.eye(4))
    y, projected = normal((8, 5)), normal((3, 8, 5))
    beta, frames = rng.normal(size=3), np.repeat(np.arange(4), 2)
    args = (gram, projected, y, .8, frames, beta, .3)
    x = rng.normal(size=6)*.05
    value, gradient = phase_update.objective(x, *args)
    h = 1e-5
    numerical = [(phase_update.objective(x+np.eye(6)[i]*h, *args)[0]-
                  phase_update.objective(x-np.eye(6)[i]*h, *args)[0])/(2*h) for i in range(6)]
    np.testing.assert_allclose(gradient, numerical, rtol=2e-6, atol=1e-7)
    _, _, record = phase_update.update(*args)
    assert record['after'] <= record['before']+1e-9
    assert 2 <= record['conditional_quadratic']['sweeps'] <= 10


def test_internal_phase_timing_is_not_added_twice(tmp_path):
    class Model:
        _experiment_spec = dict(backend='cpu')
        def infer(self, inputs):
            assert isinstance(inputs, UnknownPhaseInput)
            return dict(estimate=np.ones((2,1,1,1)), activity_decision=np.array([True, True])), dict(
                iterations=10, stopping_reason='FIXED_DEPTH', phase_method='message_gem', phase_updates=9)
    public = UnknownPhaseInput(np.ones((2,1,1)), np.ones((2,2,1)), 1., .5)
    truth = dict(channel=np.ones((2,1,1,1)), activity=np.array([True, True]))
    plan = dict(runtime_identity='synthetic', algorithm_specs={'proposed':dict(phase_input='raw')},
                phase_mode='estimated', noise_mode='estimated', device='cpu', timing_repeats=1,
                base_seed=1, cache=str(tmp_path))
    case = dict(files={'truth':'synthetic'}, phase_seconds=0.)
    row, path = suite.receiver_result(plan, Model(), 'proposed', 0, DEFAULT, public, truth, case,
                                      {('proposed', public.pilot.shape)})
    assert row['end_to_end_seconds'] == row['receiver_seconds']
    assert row['phase_method'] == 'message_gem'
    assert 'including internal phase' in row['timing_scope']
    assert row['rescoring'] == 'PASSED'


def test_paired_timing_includes_both_algorithms_phase_cost():
    from evaluation.reporting import pair_intervals
    metrics = dict(full_error=1., signal_energy=2., misses=1, false_alarms=0,
                   active=2, inactive=2, nmse_db=-3.)
    a = [dict(metrics=metrics, receiver_seconds=1., end_to_end_seconds=1.)]*3
    b = [dict(metrics=metrics, receiver_seconds=.5, end_to_end_seconds=10.5)]*3
    pair = pair_intervals(a, b, dict(bootstrap_seed=7, bootstrap_replicates=100))
    assert pair['mean_receiver_time_ratio'] == 2.
    assert pair['mean_end_to_end_time_ratio'] == 1/10.5
    assert pair['mean_end_to_end_seconds_difference_ci95'] == [-9.5, -9.5]
