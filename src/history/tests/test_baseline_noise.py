"""Noise likelihood, posterior uncertainty, and public information boundary."""
import json
from types import SimpleNamespace

import numpy as np
import pytest

from afdm_jadcedd.algorithm.baselines.noise_estimation import estimate_spatial_noise, load_unknown_noise_input
from afdm_jadcedd.algorithm.baselines.offgrid_noise import expected_residual_energy
from afdm_jadcedd.algorithm.baselines.offgrid.sbl import posterior
from afdm_jadcedd.algorithm.baselines.gamp_sbl_mmv import MMVControls, solve_mmv
from afdm_jadcedd.algorithm.registry import ALGORITHMS
from afdm_jadcedd.experiment import run as cli


def complex_normal(rng, shape):
    return (rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)


@pytest.mark.parametrize('rank', [0, 2])
def test_spatial_noise_on_white_noise_and_unknown_low_rank_signal(rank):
    rng = np.random.default_rng(814+rank)
    count, antennas, variance = 4096, 8, 1.7
    basis, _ = np.linalg.qr(complex_normal(rng, (antennas, antennas)))
    samples = np.sqrt(variance)*complex_normal(rng, (count, antennas))
    if rank:
        samples += 5*complex_normal(rng, (count, rank))@basis[:, :rank].conj().T
    observation = samples.reshape(256, 16, antennas).transpose(0, 2, 1)
    estimated, record = estimate_spatial_noise(observation)
    assert record['estimated_signal_rank'] == rank
    assert abs(estimated/variance-1) < .08  # finite sample accuracy, not zero error
    scaled, scaled_record = estimate_spatial_noise(3.2j*observation)
    np.testing.assert_allclose(scaled, 3.2**2*estimated, rtol=1e-12)
    assert scaled_record['estimated_signal_rank'] == rank


def test_offgrid_noise_expectation_includes_full_covariance_and_mmv_factor():
    rng = np.random.default_rng(37)
    a = complex_normal(rng, (7, 11))
    y = complex_normal(rng, (7, 3))
    alpha, noise = rng.uniform(.1, 2., 11), .7
    mean, diagonal, _ = posterior(a, y, alpha, noise)
    sigma = np.linalg.inv(a.conj().T@a/noise+np.diag(1/alpha))
    expected = np.linalg.norm(y-a@mean)**2+3*np.trace(a@sigma@a.conj().T).real
    np.testing.assert_allclose(expected_residual_energy(a, y, mean, diagonal, alpha, noise),
                               expected, rtol=1e-12)
    # Independently maximize the fixed-posterior Gamma log density in precision.
    shape, rate = 1e-4, 1e-4
    precision = (y.size+shape-1)/(expected+rate)
    def q(beta):
        return (y.size+shape-1)*np.log(beta)-(expected+rate)*beta
    assert q(precision) > max(q(precision*.9), q(precision*1.1))


def test_gamp_noise_update_matches_complex_identity_channel_output_posterior():
    rng = np.random.default_rng(43)
    y = complex_normal(rng, (8, 3))
    controls = MMVControls(iterations=1, stopping_rule='fixed', noise_shape=1., noise_rate=1e-12)
    # First output posterior with A=I, prior CN(0,.9 received power).
    power = np.mean(abs(y)**2)
    v, noise = .9*power, .1*power
    u = v/(v+noise)*y
    posterior_v = v*noise/(v+noise)
    expected = (np.sum(abs(y-u)**2)+y.size*posterior_v+controls.noise_rate)/y.size
    result = solve_mmv(np.eye(8), y, controls)
    np.testing.assert_allclose(result['noise_variance'], expected, rtol=1e-12)


def test_gamp_spatial_prior_map_and_update_bound():
    rng = np.random.default_rng(51)
    y = complex_normal(rng, (8, 3))
    spatial = .73
    controls = MMVControls(iterations=1, stopping_rule='fixed', noise_shape=1+y.size,
                           noise_rate=y.size*spatial)
    # Exact first-step output posterior for an identity sensing matrix.
    power = np.mean(abs(y)**2)
    v, noise = .9*power, .1*power
    u = v/(v+noise)*y
    expected_energy = np.sum(abs(y-u)**2)+y.size*v*noise/(v+noise)
    expected_noise = (expected_energy/y.size+spatial)/2
    result = solve_mmv(np.eye(8), y, controls)
    np.testing.assert_allclose(result['noise_variance'], expected_noise, rtol=1e-12)
    # Check the stationary precision against the independent Gamma log density.
    precision = 1/expected_noise
    def q(beta):
        return (y.size+controls.noise_shape-1)*np.log(beta)-(expected_energy+controls.noise_rate)*beta
    assert q(precision) > max(q(.9*precision), q(1.1*precision))
    # Overcomplete sensing cannot drive an update below the prior-induced bound.
    a = complex_normal(rng, (8, 40))/np.sqrt(8)
    result = solve_mmv(a, y, MMVControls(iterations=40, stopping_rule='fixed',
        noise_shape=1+y.size, noise_rate=y.size*spatial))
    assert min(r['noise_variance'] for r in result['trace']) >= spatial/2


def test_gamp_receiver_uses_observation_estimated_prior_scale(monkeypatch):
    from afdm_jadcedd.algorithm.baselines import baseline_noise
    from afdm_jadcedd.system.observation import ReceiverInput
    rng = np.random.default_rng(52)
    inputs = ReceiverInput(complex_normal(rng, (4, 3, 16)),
                           complex_normal(rng, (4, 2, 16)), 1e20, .1)
    expected_noise, _ = estimate_spatial_noise(inputs.observation)
    captured = []
    def solve(a, y, controls):
        captured.append(controls)
        assert controls.noise_shape == 1+y.size
        assert controls.noise_rate == y.size*expected_noise
        assert controls.initial_noise_fraction == .1
        return dict(mean=np.zeros((a.shape[1], y.shape[1]),complex), noise_variance=expected_noise,
                    iterations=1, stopping_reason='TEST', trace=[dict(noise_variance=expected_noise)])
    monkeypatch.setattr(baseline_noise, 'solve_mmv', solve)
    receiver = baseline_noise.EstimatedNoiseBaselineReceiver('gamp', device='cpu')
    arrays, record = receiver.infer(inputs)
    assert len(captured) == 1
    assert record['noise_prior_reference_variance'] == expected_noise
    assert not record['supplied_noise_variance_used']


def test_offgrid_spatial_prior_with_independent_full_posterior():
    from afdm_jadcedd.algorithm.baselines import offgrid_noise
    from afdm_jadcedd.algorithm.baselines.offgrid.atoms import coarse_dictionary, stack_observation
    from afdm_jadcedd.algorithm.baselines.offgrid.sbl import Settings
    from afdm_jadcedd.system.observation import ReceiverInput
    rng = np.random.default_rng(53)
    inputs = ReceiverInput(complex_normal(rng, (4, 3, 16)),
                           complex_normal(rng, (4, 2, 16)), 1e20, .1)
    settings = Settings(iterations=1, candidates_per_user=2, offset_candidates=1)
    spatial, _ = estimate_spatial_noise(inputs.observation)
    y = stack_observation(inputs.observation)
    coarse, _, coordinates, _ = coarse_dictionary(inputs.operator, settings.doppler_step)
    scores = np.sum(abs(coarse.conj().T@y)**2, axis=1).reshape(2, -1)
    indices = np.concatenate([u*len(coordinates)+np.argsort(-scores[u], kind='stable')[:2]
                              for u in range(2)])
    a = coarse[:, indices]
    noise0 = .01*np.mean(abs(y)**2)
    alpha = (np.sum(abs(y)**2)-y.size*noise0)/(y.shape[1]*a.shape[1])
    # Direct coefficient-space inverse, independent of the Woodbury trace path.
    sigma = np.linalg.inv(a.conj().T@a/noise0+np.eye(a.shape[1])/alpha)
    mean = sigma@a.conj().T@y/noise0
    expected = np.linalg.norm(y-a@mean)**2+y.shape[1]*np.trace(a@sigma@a.conj().T).real
    result = offgrid_noise.solve(inputs, settings, noise_shape=1+y.size,
                                  noise_rate=y.size*spatial)
    expected_noise = (expected/y.size+spatial)/2
    np.testing.assert_allclose(result['noise_variance'], expected_noise, rtol=1e-12)
    assert result['noise_variance'] >= spatial/2
    precision = 1/expected_noise
    def q(beta):
        return 2*y.size*np.log(beta)-(expected+y.size*spatial)*beta
    assert q(precision) > max(q(.9*precision), q(1.1*precision))


def test_offgrid_receiver_uses_estimated_prior_and_final_noise_for_readout(monkeypatch):
    from afdm_jadcedd.algorithm.baselines import baseline_noise
    from afdm_jadcedd.system.observation import ReceiverInput
    rng = np.random.default_rng(54)
    inputs = ReceiverInput(complex_normal(rng, (4, 3, 16)),
                           complex_normal(rng, (4, 2, 16)), 1e20, .1)
    spatial, _ = estimate_spatial_noise(inputs.observation)
    final_noise = .8*spatial
    def solve(arg, settings, **controls):
        assert arg.noise_variance == spatial
        assert controls == dict(noise_shape=1+arg.observation.size,
            noise_rate=arg.observation.size*spatial, initial_noise_fraction=.01)
        return dict(estimate=np.zeros((2,3,16,16), complex), user_ids=np.array([0]),
            positions=np.zeros((1,2)), gains=np.zeros((1,3), complex),
            noise_variance=final_noise, initial_noise_variance=.01,
            trace=[dict(noise_variance=final_noise)], iterations=1, stopping_reason='TEST')
    monkeypatch.setattr(baseline_noise.offgrid_noise, 'solve', solve)
    receiver = baseline_noise.EstimatedNoiseBaselineReceiver('offgrid_sbl', device='cpu')
    arrays, record = receiver.infer(inputs)
    snr = 10*np.log10(max(np.mean(abs(inputs.observation)**2)/final_noise-1, 1e-12))
    np.testing.assert_allclose(record['public_estimated_snr_db'], snr, rtol=1e-12)
    assert arrays['noise_variance_estimate'] == final_noise
    assert record['noise_prior_reference_variance'] == spatial
    assert not record['supplied_noise_variance_used']


@pytest.mark.parametrize('method', ['somp', 'gnn', 'ldamp'])
def test_other_baselines_receive_observation_noise_not_legacy_field(method, monkeypatch):
    from afdm_jadcedd.algorithm.baselines import baseline_noise
    from afdm_jadcedd.system.observation import ReceiverInput
    rng = np.random.default_rng(55)
    inputs = ReceiverInput(complex_normal(rng, (4, 3, 16)),
                           complex_normal(rng, (4, 2, 16)), 1e20, .1)
    spatial, _ = estimate_spatial_noise(inputs.observation)
    def infer(arg, **unused):
        assert arg.noise_variance == spatial
        return dict(estimate=np.zeros((2,3,16,16))), dict(trace=[dict(effective_complex_variance=.37)])
    monkeypatch.setattr(baseline_noise, 'build_receiver',
        lambda *args, **kwargs: SimpleNamespace(configuration={}, signature='test', infer=infer))
    arrays, record = baseline_noise.EstimatedNoiseBaselineReceiver(method).infer(inputs)
    assert arrays['noise_variance_estimate'] == spatial
    assert not record['supplied_noise_variance_used']
    if method == 'ldamp':
        assert arrays['effective_noise_variance_history_normalized'][0] == .37
        assert record['physical_noise_estimate_role'] == 'diagnostic_only'


def test_ldamp_equivalent_noise_units_and_supplied_noise_independence():
    from dataclasses import replace
    from afdm_jadcedd.algorithm.baselines.ldamp.matrix import solve, Controls, from_matrix
    from afdm_jadcedd.system.observation import ReceiverInput
    rng = np.random.default_rng(56)
    inputs = ReceiverInput(complex_normal(rng, (5,2,3)),
                           3*complex_normal(rng, (5,2,4)), .9, .1)
    gain = np.sqrt(np.sum(abs(inputs.operator)**2)/8)
    y = inputs.observation.reshape(5,6)/(2.3*gain)
    expected_covariance = sum(np.outer(v,v.conj()) for v in y)/5
    a = inputs.operator.reshape(5,8)/gain
    expected_query = from_matrix(a.conj().T@y, (2,2,3,4))
    class Denoiser:
        def linearize(self, query, covariance):
            np.testing.assert_allclose(query, expected_query, rtol=1e-12, atol=1e-14)
            np.testing.assert_allclose(covariance, expected_covariance, rtol=1e-12, atol=1e-14)
            return np.zeros_like(query), lambda values: np.zeros_like(values)
    outputs = [solve(replace(inputs, noise_variance=noise), Denoiser(), scale=2.3,
        controls=Controls(iterations=2, probes=1)) for noise in [.9, 1e20]]
    assert outputs[0]['trace'] == outputs[1]['trace']
    assert outputs[0]['trace'][0]['effective_complex_variance'] == pytest.approx(np.mean(abs(y)**2))


@pytest.mark.parametrize('phase_mode,matrix', [('estimated','pilot'), ('known','operator')])
def test_public_loader_never_reads_legacy_noise_or_accepts_truth(tmp_path, phase_mode, matrix):
    rng = np.random.default_rng(9)
    fields = dict(observation=complex_normal(rng, (4, 3, 16)), activity_prior=.1)
    fields[matrix] = complex_normal(rng, (4, 2, 16))
    path = tmp_path/'input.npz'
    np.savez(path, **fields)
    reference = load_unknown_noise_input(path, phase_mode=phase_mode)
    for forbidden_value in (np.nan, -1., 1e99, np.array(['not a variance'])):
        np.savez(path, **fields, noise_variance=forbidden_value)
        loaded = load_unknown_noise_input(path, phase_mode=phase_mode)
        assert loaded.noise_variance == reference.noise_variance
    np.savez(path, **fields, phase_slopes=np.zeros(2))
    with pytest.raises(ValueError, match='Unknown-noise input'):
        load_unknown_noise_input(path, phase_mode=phase_mode)


@pytest.mark.parametrize('method', ALGORITHMS[1:])
def test_known_phase_still_defaults_to_estimated_noise(method, tmp_path, monkeypatch):
    calls = []
    def factory(name, *, config, device):
        calls.append(name)
        return SimpleNamespace(run=lambda *_: dict(status='COMPLETE', method=name, iterations=1, seconds=0.))
    monkeypatch.setattr(cli, 'EstimatedNoiseBaselineReceiver', factory)
    assert cli.main(['run', '--method', method, '--phase-mode', 'known',
                     '--input', str(tmp_path/'i.npz'), '--output', str(tmp_path/'o.npz')]) == 0
    assert calls == [method]


def test_simulation_can_omit_noise_and_keeps_it_only_in_truth(tmp_path):
    out = tmp_path/'case'
    assert cli.main(['simulate', '--seed', '202610159103', '--users', '3',
                     '--noise-mode', 'estimated', '--output', str(out)]) == 0
    with np.load(out/'input.npz') as saved:
        assert set(saved.files) == {'observation', 'pilot', 'activity_prior'}
    with np.load(out/'truth.npz') as saved:
        assert float(saved['noise_variance']) > 0
    assert json.loads((out/'generation.json').read_text())['noise_mode'] == 'estimated'


@pytest.mark.parametrize('noise_mode', ['estimated', 'known'])
def test_proposed_noise_scope_is_explicit(tmp_path, monkeypatch, noise_mode):
    calls = []
    def factory(method, *, config, device, noise_mode):
        calls.append((method, noise_mode))
        return SimpleNamespace(run=lambda *_: dict(
            status='COMPLETE', method=method, iterations=1, seconds=0.))
    monkeypatch.setattr(cli, 'build_estimated_phase_receiver', factory)
    assert cli.main(['run', '--noise-mode', noise_mode, '--input', str(tmp_path/'i.npz'),
                     '--output', str(tmp_path/'o.npz')]) == 0
    assert calls == [('proposed', noise_mode)]
