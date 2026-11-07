"""Check information boundaries and paired formal subsets without model fitting."""
from dataclasses import replace
from itertools import product
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from algorithm import registry
from algorithm.proposed import inference
from evaluation import suite
from evaluation.scenes import BASE_SEED, DEFAULT
from evaluation.storage import save_arrays, arrays
from system.phase import phase_operator
from system.receiver.unknown_phase import UnknownPhaseInput
from utils import read_json, write_json


@pytest.mark.parametrize('phase_mode,noise_mode', tuple(product(('known', 'estimated'), repeat=2)))
def test_formal_500_plan_and_mode_selection(tmp_path, monkeypatch, phase_mode, noise_mode):
    monkeypatch.setattr(suite, 'assets', lambda *args: {})
    output = tmp_path/'plan'
    suite.main('snr_comparison', ['plan', '--scenes', '500', '--phase-mode', phase_mode,
        '--noise-mode', noise_mode, '--output', str(output)])
    plan = read_json(output/'PLAN.json')
    assert plan['scene_count'] == 500 and plan['base_seed'] == BASE_SEED
    assert plan['mode'] == 'FORMAL_SUBSET'
    assert plan['scene_selection'] == 'fixed_registry_prefix'
    assert (plan['phase_mode'], plan['noise_mode']) == (phase_mode, noise_mode)
    assert plan['methods'] == ['proposed', 'offgrid_sbl', 'gnn', 'gamp', 'somp']
    assert not plan['include_stmp']
    specs = plan['algorithm_specs']
    if noise_mode == 'known':
        assert specs['proposed']['kwargs']['noise_mode'] == 'known'
        assert specs['gamp']['factory'] == 'evaluation.receivers:known_noise_baseline'
        assert specs['gnn']['parameter_modules'] == ['native.model']
    else:
        assert 'kwargs' not in specs['proposed']
        assert specs['gamp']['factory'] == 'algorithm.baseline._base:EstimatedNoiseBaselineReceiver'


def test_default_modes_and_custom_config_subset(tmp_path, monkeypatch):
    monkeypatch.setattr(suite, 'assets', lambda *args: {})
    suite.main('snr_comparison', ['plan', '--output', str(tmp_path/'default')])
    default = read_json(tmp_path/'default/PLAN.json')
    assert (default['phase_mode'], default['noise_mode'], default['scene_count']) == ('estimated', 'estimated', 1000)
    assert default['mode'] == 'FORMAL_1000'
    _, config = suite.experiment_config('snr_comparison')
    config.update(scenes=500, phase_mode='known', noise_mode='estimated')
    write_json(tmp_path/'config.json', config)
    suite.main('snr_comparison', ['plan', '--config', str(tmp_path/'config.json'),
                                '--output', str(tmp_path/'configured')])
    custom = read_json(tmp_path/'configured/PLAN.json')
    assert (custom['phase_mode'], custom['noise_mode'], custom['scene_count']) == ('known', 'estimated', 500)
    assert custom['input_identity'] != default['input_identity']
    suite.main('snr_comparison', ['plan', '--smoke', '--scenes', '2', '--output', str(tmp_path/'smoke')])
    smoke = read_json(tmp_path/'smoke/PLAN.json')
    assert smoke['base_seed'] == suite.SMOKE_SEED and smoke['mode'] == 'SMOKE_ONLY'


def test_evaluation_scene_limit_applies_to_snr_and_runtime(tmp_path, monkeypatch):
    monkeypatch.setattr(suite, 'assets', lambda *args: {})
    for name in ['snr_comparison', 'runtime_comparison']:
        with pytest.raises(ValueError, match='Scene count'):
            suite.main(name, ['plan', '--scenes', '1001', '--output', str(tmp_path/name/'too_many')])
        suite.main(name, ['plan', '--output', str(tmp_path/name/'default')])
        assert read_json(tmp_path/name/'default/PLAN.json')['scene_count'] == 1000


def test_paired_inputs_cache_and_truth_boundaries(tmp_path, monkeypatch):
    # Synthetic inputs test the transport contract, not receiver accuracy.
    raw = UnknownPhaseInput(np.ones((2, 1, 1), complex), np.ones((2, 2, 1), complex), 1., .5)
    slopes = np.array([.2, -.3])
    truth = dict(phase_slopes=slopes, channel=np.ones((2, 1, 1, 1), complex), activity=np.array([True, False]))
    calls = []
    def observation(*args, **kwargs):
        return raw, truth, dict(generated_noise_variance=.125)
    def estimate(inputs, folder, controls):
        calls.append(inputs)
        result = dict(phase_slopes=np.zeros(2))
        record = dict(seconds=.25)
        save_arrays(folder/'phase.npz', result)
        write_json(folder/'PHASE.json', record)
        return result, record
    monkeypatch.setattr(suite, 'observation', observation)
    monkeypatch.setattr(suite, 'estimated_phase', estimate)
    folders = set()
    for phase_mode, noise_mode in product(('known', 'estimated'), repeat=2):
        plan = dict(base_seed=BASE_SEED, cache=str(tmp_path), input_identity='same_test_sources',
                    model_binding=registry.load_models(), phase_mode=phase_mode, noise_mode=noise_mode)
        public, actual_truth, receipt, folder = suite.prepared_case(plan, 0, DEFAULT)
        np.testing.assert_array_equal(public.observation, raw.observation)
        np.testing.assert_array_equal(actual_truth['channel'], truth['channel'])
        expected_slopes = slopes if phase_mode == 'known' else np.zeros(2)
        np.testing.assert_array_equal(public.operator, phase_operator(raw.pilot, expected_slopes))
        assert public.noise_variance == (.125 if noise_mode == 'known' else 1.)
        assert receipt['phase_seconds'] == (0. if phase_mode == 'known' else .25)
        assert float(arrays(folder/'public.npz')['noise_variance']) == public.noise_variance
        cached, _, saved, _ = suite.prepared_case(plan, 0, DEFAULT)
        assert saved == receipt and cached.noise_variance == public.noise_variance
        np.testing.assert_array_equal(cached.operator, public.operator)
        folders.add(folder)
    assert len(folders) == 4 and len(calls) == 2


def test_proposed_noise_mode_ignores_placeholder_or_uses_supplied_variance(monkeypatch):
    class Model:
        score_evaluations = 0
        def __call__(self, public):
            return [dict(estimate=torch.full((2, 2, 1, 1, 1), public['noise']),
                         logits=torch.zeros(2))], []
    calls = []
    def estimate(y):
        calls.append(y)
        return .25, dict(source='synthetic observation estimate')
    monkeypatch.setattr(inference, 'estimate_spatial_noise', estimate)
    model = object.__new__(inference.ProposedReceiver)
    model.device, model.scale, model.parameters = 'cpu', 1., 0
    model.model = Model()
    model.data = SimpleNamespace(prepare_public=lambda values, *a, **k: (values, {}))
    model.configuration = dict(checkpoint_sha256='synthetic fixture')
    inputs = UnknownPhaseInput(np.ones((2, 1, 1), complex), np.ones((2, 2, 1), complex), .125, .5).at_estimated_phase(np.zeros(2))
    model.noise_mode = 'estimated'
    first, record = model.infer(inputs)
    poisoned, _ = model.infer(replace(inputs, noise_variance=12345.))
    np.testing.assert_array_equal(first['estimate'], poisoned['estimate'])
    assert not record['supplied_noise_variance_used'] and len(calls) == 2
    model.noise_mode = 'known'
    known, record = model.infer(inputs)
    assert len(calls) == 2 and record['supplied_noise_variance_used']
    assert float(known['noise_variance_estimate']) == .125
    assert not np.array_equal(known['estimate'], first['estimate'])


def test_unregistered_known_noise_and_denoising_flags_rejected(tmp_path):
    specs = {'custom': dict(kind='receiver', factory='unused:Receiver', backend='cpu')}
    with pytest.raises(ValueError, match='Known-noise receiver is not registered'):
        registry.select(['custom'], specs, 'receiver', noise_mode='known')
    with pytest.raises(ValueError, match='applies to receivers'):
        suite.main('channel_denoising', ['plan', '--noise-mode', 'estimated', '--output', str(tmp_path/'bad')])
    with pytest.raises(SystemExit):
        suite.main('snr_comparison', ['run', '--phase-mode', 'known'])


@pytest.mark.parametrize('method', ('somp', 'gamp', 'offgrid_sbl'))
def test_known_baseline_uses_existing_conditional_receiver(method):
    specs = registry.select([method], registry.load_catalog(), 'receiver', noise_mode='known')
    model = registry.build_algorithm(method, binding=registry.load_models(), device='cpu', definitions=specs)
    assert model.__class__.__name__ in ('ConditionalReceiver', 'OffGridReceiver')
    assert model._experiment_spec['factory'] == 'evaluation.receivers:known_noise_baseline'

