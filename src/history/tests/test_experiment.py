"""Pairing and pooled metrics that directly affect the paper's conclusions."""
import importlib.util
from pathlib import Path
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('paper_experiment', ROOT / 'experiment/_common.py')
experiment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(experiment)


def test_snr_generation_matches_completed_batch_and_has_no_supplied_noise(tmp_path):
    spec = importlib.util.spec_from_file_location('frozen_batch', ROOT / 'experiments/baseline_comparison_600_20261017/run.py')
    batch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(batch)
    batch.OUT = tmp_path
    scale = experiment.read(ROOT / 'configs/proposed.json')['scale']
    seed = 202610172000001
    folder = batch.prepare_scene(0, dict(seeds=[seed], scale=scale))
    for snr in (-4, 8):
        expected = batch.public_input(folder, snr)
        actual, truth, _ = experiment.observation(seed, dict(snr_db=snr, frames=16, users=40, activity_probability=.1), scale)
        np.testing.assert_array_equal(actual.observation, expected.observation)
        np.testing.assert_array_equal(actual.pilot, expected.pilot)
        np.testing.assert_array_equal(truth['channel'], batch.arrays(folder / 'truth.npz')['channel'])
        assert actual.noise_variance == 1.  # Placeholder, never the generated variance.
        assert actual.activity_prior == expected.activity_prior


def test_pooled_metrics_and_failures_cannot_be_reported_as_complete():
    spec = dict(values=[0], methods=['proposed'], scenes=2)
    records = [dict(condition=0, method='proposed', status='COMPLETE', receiver_seconds=1.,
                    metrics=dict(active=1, inactive=1, misses=0, false_alarms=1, full_error=11., signal_energy=4.)),
               dict(condition=0, method='proposed', status='COMPLETE', receiver_seconds=2.,
                    metrics=dict(active=1, inactive=1, misses=1, false_alarms=0, full_error=1., signal_energy=8.))]
    row = experiment.aggregate(spec, records)[0]
    assert row['nmse_db'] == pytest.approx(0.)  # Energy pooling, not mean dB.
    assert row['aer'] == .5
    records[1] = dict(condition=0, method='proposed', status='FAILED')
    row = experiment.aggregate(spec, records)[0]
    assert row['status'] == 'INCOMPLETE' and row['failed'] == 1
    assert 'nmse_db' not in row and 'aer' not in row


def test_plan_cannot_overwrite_existing_results(tmp_path):
    (tmp_path / 'evidence.json').write_text('keep')
    with pytest.raises(FileExistsError):
        experiment.main(dict(description='test', scenes=1, seed=1, values=[0]), ['plan', '--output', str(tmp_path)])
    assert (tmp_path / 'evidence.json').read_text() == 'keep'


def test_convergence_keeps_stopped_scenes_in_pooled_energy(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'experiment'))
    import convergence
    records = [dict(iterations=1, points=[dict(full_error=1., signal_energy=1.),
                                         dict(full_error=.1, signal_energy=1.)]),
               dict(iterations=2, points=[dict(full_error=9., signal_energy=9.),
                                         dict(full_error=4., signal_energy=9.),
                                         dict(full_error=1., signal_energy=9.)])]
    rows = convergence.pooled_curve(records)
    assert rows[-1]['full_error'] == pytest.approx(1.1)
    assert rows[-1]['signal_energy'] == 10.
    assert rows[-1]['nmse_db'] == pytest.approx(10*np.log10(.11))
    assert rows[-1]['stopped_scenes'] == 1 and rows[-1]['scenes'] == 2


def test_cross_channel_d_exact_and_profiles_keep_public_geometry(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'experiment'))
    import cross_channel
    scale = experiment.read(ROOT / 'configs/proposed.json')['scale']
    seed = 202610180600001
    kwargs = dict(users=2, frames=8, activity_probability=.1)
    original, original_truth, _ = experiment.generate_case(seed, 0., scale, **kwargs)
    d, d_truth, _ = cross_channel.generate_profile_case(seed, 0., scale, profile='D', **kwargs)
    for key in original:
        np.testing.assert_array_equal(d[key], original[key])
    for key in original_truth:
        np.testing.assert_array_equal(d_truth[key], original_truth[key])
    expected_total = sum(10**(db/10) for _, db, _ in cross_channel.PROFILES['D'])
    for profile in 'ABCD':
        public, truth, metadata = cross_channel.generate_profile_case(seed, 0., scale, profile=profile, **kwargs)
        np.testing.assert_array_equal(public['pilot'], d['pilot'])
        np.testing.assert_array_equal(truth['activity'], d_truth['activity'])
        np.testing.assert_array_equal(truth['phase_slopes'], d_truth['phase_slopes'])
        assert metadata['expected_tap_power_scale']*sum(10**(db/10) for _,db,_ in cross_channel.PROFILES[profile]) == pytest.approx(expected_total)
        clean = np.einsum('qkn,kmrn->qmr', experiment.phase_operator(public['pilot'], truth['phase_slopes']), truth['channel'], optimize=False)
        assert np.mean(abs(clean)**2) == pytest.approx(public['noise_variance'])
        noise = (public['observation']-clean)/np.sqrt(public['noise_variance'])
        if profile == 'A':
            reference_noise = noise
        else:
            np.testing.assert_allclose(noise, reference_noise, atol=1e-14, rtol=1e-14)
        scene, _ = cross_channel.profile_scene(seed, profile, users=2)
        assert [p.normalized_delay for p in scene.paths_of(0)] == [r[0] for r in cross_channel.PROFILES[profile]]
        if profile != 'D':
            assert not np.array_equal(truth['channel'], d_truth['channel'])


def test_denoising_keeps_negative_predictions_and_pools_energy(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'experiment'))
    import channel_denoising as denoise
    truth = np.ones((2, 1, 1, 2), complex)
    metrics = denoise.denoising_metrics(np.zeros_like(truth), truth, [-.2, .4])
    np.testing.assert_allclose(metrics['predicted_error'], [-.4, .8])
    spec = dict(values=[1.], methods=['proposed'], scenes=2)
    rows = [dict(condition=0, method='proposed', status='COMPLETE', samples=2,
                 error=1., energy=2., predicted_error=-.5, negative_variance_samples=1),
            dict(condition=0, method='proposed', status='COMPLETE', samples=2,
                 error=3., energy=6., predicted_error=2.5, negative_variance_samples=0)]
    row = denoise.aggregate(spec, rows)[0]
    assert row['nmse_db'] == pytest.approx(10*np.log10(.5))
    assert row['predicted_to_observed_mse'] == .5 and row['negative_variance_samples'] == 1
    rows[1] = dict(condition=0, method='proposed', status='FAILED')
    row = denoise.aggregate(spec, rows)[0]
    assert row['status'] == 'INCOMPLETE' and 'nmse_db' not in row


def test_small_data_option_only_in_snr_and_denoising(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'experiment'))
    import pilot_frames, user_count, activity_probability, convergence, cross_channel
    for entry in (pilot_frames, user_count, activity_probability):
        with pytest.raises(SystemExit) as error:
            experiment.main(entry.EXPERIMENT, ['plan', '--output', str(tmp_path), '--small-config', 'missing.json'])
        assert error.value.code == 2
    for entry in (convergence, cross_channel):
        with pytest.raises(SystemExit) as error:
            entry.main(['plan', '--output', str(tmp_path), '--small-config', 'missing.json'])
        assert error.value.code == 2


def test_small_data_cannot_relabel_full_weights(tmp_path, monkeypatch):
    # Metadata-only fixture: isolate the experiment's anti-relabel check.
    from afdm_jadcedd.algorithm.proposed import configuration
    monkeypatch.setattr(configuration, 'verify', lambda _: None)
    config = experiment.read(ROOT / 'configs/proposed.json')
    prior = experiment.read(ROOT / config['prior_definition'])
    prior['train_samples'] = 5000
    experiment.save(tmp_path / 'prior.json', prior)
    config['prior_definition'] = str(tmp_path / 'prior.json')
    experiment.save(tmp_path / 'receiver.json', config)
    with pytest.raises(ValueError, match='independently trained complete weights'):
        experiment.proposed_bundles(tmp_path / 'receiver.json')


def test_denoising_rejects_training_scene_overlap(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'experiment'))
    import channel_denoising
    config = experiment.read(ROOT / 'configs/proposed.json')
    with pytest.raises(ValueError, match='overlap'):
        channel_denoising.validate_test_seeds(dict(seed=2026100601000000, scenes=1),
                                             dict(proposed=dict(configuration=config)))


def test_denoising_rejects_noncontiguous_training_scene_overlap(tmp_path, monkeypatch):
    import channel_denoising
    path = tmp_path/'prior.json'
    experiment.save(path, dict(dataset_identities=dict(train=dict(scene_seeds=[100, 900], scenes=2))))
    bundle = dict(proposed=dict(configuration=dict(prior_definition=str(path))))
    with pytest.raises(ValueError, match='overlap'):
        channel_denoising.validate_test_seeds(dict(seed=899, scenes=2), bundle)
    channel_denoising.validate_test_seeds(dict(seed=101, scenes=2), bundle)


def test_first_only_denoising_matches_complete_receiver_mean():
    import torch
    import channel_denoising
    torch.set_num_threads(1)
    config = experiment.read(ROOT/'configs/proposed.json')
    first = channel_denoising.FirstChannelMean(config['scale'], ROOT/config['first_checkpoint'], device='cpu')
    complete = channel_denoising.FullChannelMoments(config['scale'], ROOT/config['first_checkpoint'],
                         ROOT/config['second_checkpoint'], device='cpu')
    rng = np.random.default_rng(8244)
    query = rng.normal(size=(2,16,16,16)) + 1j*rng.normal(size=(2,16,16,16))
    actual = first.infer(query, .1)
    expected = complete.infer(query, .1)
    np.testing.assert_array_equal(actual.mean, expected.mean)
    assert actual.variance is None


def test_training_subset_keeps_complete_physical_scenes():
    spec = importlib.util.spec_from_file_location('training_sizes', ROOT/'scripts/train_proposed_sizes.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    identities = np.column_stack((np.repeat(np.arange(20), 4), np.tile(np.arange(4), 20)))
    rows = module.selected_rows(identities, 20, 99)
    assert len(rows) == 20 and len(np.unique(rows)) == 20
    _, counts = np.unique(identities[rows, 0], return_counts=True)
    np.testing.assert_array_equal(counts, np.full(5,4))
    np.testing.assert_array_equal(rows, module.selected_rows(identities, 20, 99))
    with pytest.raises(ValueError, match='groups'):
        module.selected_rows(identities, 19, 99)


def test_extended_frames_keep_truth_pilot_noise_prefix_and_received_snr():
    scale = experiment.read(ROOT / 'configs/proposed.json')['scale']
    parameters = dict(users=40, frames=32, activity_probability=.1, snr_db=4.)
    seed = 202610181100001
    previous = None
    for frames in (32, 40, 48):
        inputs, truth, metadata = experiment.observation(seed, dict(parameters, frames=frames), scale)
        clean = np.einsum('qkn,kmrn->qmr', experiment.phase_operator(inputs.pilot, truth['phase_slopes']),
                          truth['channel'], optimize=False)
        variance = metadata['generated_noise_variance']
        assert np.mean(abs(clean)**2)/variance == pytest.approx(10**.4)
        epsilon = (inputs.observation-clean)/np.sqrt(variance)
        assert inputs.observation.shape == (frames, 16, 16)
        flat = inputs.pilot.reshape(frames, -1)
        np.testing.assert_allclose(flat@flat.conj().T, 40*np.eye(frames), atol=2e-11)
        if previous is not None:
            old, old_truth, old_epsilon = previous
            for key in truth:
                np.testing.assert_array_equal(truth[key], old_truth[key])
            np.testing.assert_array_equal(inputs.pilot[:len(old.pilot)], old.pilot)
            np.testing.assert_allclose(epsilon[:len(old.pilot)], old_epsilon, atol=1e-14, rtol=1e-14)
            assert metadata['physical_clean_power'] == pytest.approx(np.mean(abs(clean)**2))
            assert metadata['frames'] == frames
        previous = inputs, truth, epsilon
    with pytest.raises(ValueError, match='frames'):
        experiment.observation(seed, dict(parameters, users=2, frames=48), scale)


def test_genie_prior_does_not_use_unknown_diffuse_gains(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'experiment'))
    from dataclasses import replace
    import channel_denoising as denoise
    scene, _ = denoise.draw_scene(202610181100002, n_users=2)
    paths = scene.paths_of(0)
    scale = experiment.read(ROOT / 'configs/proposed.json')['scale']
    prior = denoise.genie_prior(paths, scale)
    changed = [p if p.path_id == 0 else replace(p, gain=100+300j) for p in paths]
    other = denoise.genie_prior(changed, scale)
    for key in prior:
        np.testing.assert_array_equal(prior[key], other[key])
    mean = denoise.user_channel([paths[0]])/scale
    np.testing.assert_array_equal(prior['mean'], mean)
    truth = denoise.user_channel(paths)/scale
    delta = (truth-mean).reshape(-1)
    np.testing.assert_allclose(prior['basis']@(prior['basis'].conj().T@delta), delta, atol=1e-13)


def test_genie_mmse_matches_direct_posterior_and_sampled_mse(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'experiment'))
    import channel_denoising as denoise
    rng = np.random.default_rng(1829)
    noise = lambda shape: (rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)
    b = noise((4, 3)); known = noise((4,)); variance = .7
    u, s, _ = np.linalg.svd(b, full_matrices=False)
    prior = dict(mean=known, basis=u, eigenvalues=s*s)
    query = noise((1, 4))
    estimate, risk = denoise.genie_mmse(query, variance, [prior])
    expected = known+b@np.linalg.solve(b.conj().T@b+variance*np.eye(3), b.conj().T@(query[0]-known))
    np.testing.assert_allclose(estimate[0], expected, atol=1e-13)
    covariance = variance*b@np.linalg.solve(b.conj().T@b+variance*np.eye(3), b.conj().T)
    assert risk[0] == pytest.approx(np.trace(covariance).real)
    # Independent Monte Carlo verifies the risk's complex-noise convention.
    truth = known[:, None]+b@noise((3, 20000))
    received = truth+np.sqrt(variance)*noise(truth.shape)
    posterior = known[:, None]+u@((s*s/(s*s+variance))[:, None]*(u.conj().T@(received-known[:, None])))
    error = np.sum(abs(posterior-truth)**2, axis=0)
    assert abs(error.mean()-risk[0]) < 5*error.std(ddof=1)/np.sqrt(len(error))


def test_offgrid_budget_matches_frozen_calibration_and_tolerance():
    frozen = experiment.EstimatedNoiseBaselineReceiver('offgrid_sbl', config=ROOT/'configs/offgrid_baselines.json')
    selected = experiment.solver('offgrid_sbl', dict(device='cpu'))
    assert frozen.base.settings.iterations == selected.base.settings.iterations == 120
    assert frozen.base.settings.tolerance == selected.base.settings.tolerance == 1e-4
    np.testing.assert_array_equal(frozen.base.thresholds, selected.base.thresholds)
    assert frozen.signature == selected.signature
    assert selected.base.signature == selected.base.policy['methods']['offgrid_sbl']['inference_sha256']
    calibration = selected.base.policy['calibration']
    assert experiment.sha(ROOT/calibration['records']) == calibration['records_sha256']


def test_snr_reuses_five_saved_results_without_any_inference(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'experiment'))
    import snr_comparison

    def forbidden(*args, **kwargs):
        raise AssertionError('Matching historical result or phase was recomputed')

    monkeypatch.setattr(experiment.phase, 'estimate', forbidden)
    monkeypatch.setattr(experiment.EstimatedNoiseProposedReceiver, 'infer', forbidden)
    monkeypatch.setattr(experiment.EstimatedNoiseBaselineReceiver, 'infer', forbidden)
    experiment.main(snr_comparison.EXPERIMENT, ['plan', '--output', str(tmp_path), '--scenes', '1', '--values', '0'])
    plan = experiment.read(tmp_path/'PLAN.json')
    assert plan['experiment']['offgrid_budget'] == 120
    assert experiment.run(tmp_path, plan) == 0
    summary = experiment.read(tmp_path/'SUMMARY.json')
    assert summary['reused_results'] == 5 and summary['newly_computed_results'] == 0
    offgrid = next(r for r in summary['rows'] if r['method'] == 'offgrid_sbl')
    assert offgrid['stopping_condition_met'] == 0 and offgrid['maximum_iterations_reached'] == 1
    assert experiment.read(tmp_path/'scene000/condition00/PHASE_CACHE.json')['reused']
    assert experiment.read(tmp_path/'scene000/condition00/offgrid_sbl.json')['iterations'] == 120
    assert experiment.read(tmp_path/'scene000/condition00/proposed.json')['reused_execution_device'] == 'mps'
    before = experiment.sha(tmp_path/'scene000/condition00/proposed.npz')
    assert experiment.run(tmp_path, plan) == 0
    assert before == experiment.sha(tmp_path/'scene000/condition00/proposed.npz')


def test_snr_reuse_rejects_changed_budget_or_parameters(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'experiment'))
    from _support.reuse import HistoricalSNR
    spec = dict(experiment.DEFAULTS, reuse_plan=experiment.HISTORICAL_SNR)
    cache = HistoricalSNR(spec)
    parameters = dict(users=40, frames=16, activity_probability=.1, snr_db=2.)
    case = cache.case(202610172000001, parameters)
    receiver = experiment.solver('offgrid_sbl', spec)
    assert cache.result(case, 'offgrid_sbl', receiver)['iterations'] == 120
    native = experiment.read(case['folder']/'offgrid_sbl.record.json.gz')
    native['configuration']['base_configuration']['methods']['offgrid_sbl']['solver']['iterations'] += 1
    assert not cache.matches('offgrid_sbl', receiver, native, case['inputs'].activity_prior)
    assert cache.case(202610172000001, dict(parameters, frames=24)) is None
    assert cache.case(202610172000001, dict(parameters, activity_probability=.2)) is None


def test_phase_cache_requires_identical_inputs_and_controls(tmp_path, monkeypatch):
    inputs = experiment.UnknownPhaseInput(np.ones((2, 16, 16), complex),
                                          np.ones((2, 2, 16), complex), 1., .1)
    controls = experiment.phase.Controls()
    values = dict(phase_slopes=np.zeros(2))
    calls = []

    def estimate(*args):
        calls.append(1)
        return values, dict(seconds=0.)

    monkeypatch.setattr(experiment.phase, 'estimate', estimate)
    experiment.estimated_phase(inputs, tmp_path, controls)
    experiment.estimated_phase(inputs, tmp_path, controls)
    assert len(calls) == 1
    with pytest.raises(ValueError, match='Saved phase'):
        experiment.estimated_phase(inputs, tmp_path, experiment.phase.Controls(sweeps=1))


def test_hadamard_supports_original_640_columns_and_equal_user_power(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'experiment'))
    import convergence
    from afdm_jadcedd.system.pilot import PartialDFTPilot
    for users in (2, 40):
        pilot = convergence.hadamard_pilot(users, 16, 17)
        dft = PartialDFTPilot(users, 16, 17).dense().reshape(pilot.shape)
        assert set(np.unique(pilot.real)) == {-.25, .25} and not pilot.imag.any()
        np.testing.assert_allclose(np.sum(abs(pilot)**2, axis=2), np.sum(abs(dft)**2, axis=2), atol=1e-14)
        flat = pilot.reshape(16, -1)
        np.testing.assert_allclose(flat@flat.conj().T, users*np.eye(16), atol=1e-12)
    with pytest.raises(ValueError, match='Hadamard orders'):
        convergence.hadamard_pilot(3, 16, 17)


def test_pilot_replacement_regenerates_observation_and_keeps_truth(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'experiment'))
    import convergence
    scale = experiment.read(ROOT / 'configs/proposed.json')['scale']
    parameters = dict(users=2, frames=8, snr_db=0., activity_probability=.1)
    seed = 202610180700001
    original, truth, _ = experiment.observation(seed, parameters, scale)
    dft, dt, dm = convergence.pilot_observation(seed, parameters, scale, 'dft')
    had, ht, hm = convergence.pilot_observation(seed, parameters, scale, 'hadamard')
    for key, value in original.arguments().items():
        np.testing.assert_array_equal(value, dft.arguments()[key])
    for key in truth:
        np.testing.assert_array_equal(truth[key], ht[key])
        np.testing.assert_array_equal(truth[key], dt[key])
    assert not np.array_equal(dft.observation, had.observation)
    assert had.noise_variance == 1. and hm['pilot_sha256'] == experiment.array_sha256(had.pilot)
    noises = []
    for inputs, metadata in ((dft, dm), (had, hm)):
        clean = np.einsum('qkn,kmrn->qmr', experiment.phase_operator(inputs.pilot, truth['phase_slopes']), truth['channel'], optimize=False)
        assert metadata['generated_noise_variance'] == pytest.approx(np.mean(abs(clean)**2))
        noises.append((inputs.observation-clean)/np.sqrt(metadata['generated_noise_variance']))
    np.testing.assert_allclose(noises[0], noises[1], atol=2e-14, rtol=2e-14)


def test_convergence_pilot_panel_reuses_proposed_dft_and_excludes_other_variants(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'experiment'))
    import convergence
    conditions = list(convergence.pilot_conditions(convergence.EXPERIMENT))
    assert len(conditions) == 6
    for _, _, pilot, methods in conditions:
        assert methods == (experiment.METHODS if pilot == 'dft' else ['proposed'])
    legacy = dict(convergence.EXPERIMENT)
    del legacy['pilots']
    assert all(p == 'dft' for _, _, p, _ in convergence.pilot_conditions(legacy))
