"""Check the evidence intervention, its feedback, and paired analysis."""
from pathlib import Path
from types import SimpleNamespace
import sys

import numpy as np
import pytest
from scipy.special import expit, logit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiment'))
from _support.density_ratio.denoiser import Denoiser as GaussianDenoiser
from afdm_jadcedd.algorithm.proposed.denoiser import Denoiser as LearnedDenoiser
from afdm_jadcedd.algorithm.proposed.iterations import run_spatial_score
from afdm_jadcedd.algorithm.proposed.records import SpatialConfig
from afdm_jadcedd.system.observation import ReceiverInput
from _support.storage import save, read
from density_ratio_ablation import paired_statistics


class Moments:
    noise_support = (.01, 100.)

    def __init__(self):
        self.samples = 0
        self.fraction = .3

    def infer(self, r, v):
        self.samples += len(r)
        return SimpleNamespace(mean=.6*r, variance=self.fraction*v)


class Evidence:
    noise_support = Moments.noise_support
    training_class_prior = .5

    def infer(self, r, v, mean):
        return np.zeros(len(r))  # A controlled, deliberately different likelihood ratio.


def make_pair():
    options = dict(activity_prior=.2, conditional_variance_floor=1e-4)
    return (LearnedDenoiser(Moments(), Evidence(), **options),
            GaussianDenoiser(Moments(), None, **options))


def test_evidence_only_changes_joint_moments_and_respects_site_reuse():
    rng = np.random.default_rng(12)
    r = rng.normal(size=(3, 2, 2, 2)) + 1j*rng.normal(size=(3, 2, 2, 2))
    learned, gaussian = make_pair()
    for fraction, variance in [(.3, 1.), (1.2, .8), (.3, 1000.)]:
        learned.model.fraction = gaussian.model.fraction = fraction
        left, right = learned(r, variance*np.eye(2)), gaussian(r, variance*np.eye(2))
        np.testing.assert_allclose(learned.site_mean, gaussian.site_mean, rtol=1e-14)
        np.testing.assert_allclose(learned.site_variance, gaussian.site_variance, rtol=1e-14)
        np.testing.assert_allclose(left.conditional_mean, right.conditional_mean, rtol=1e-14)
        np.testing.assert_allclose(left.conditional_spatial_covariance, right.conditional_spatial_covariance, rtol=1e-14)
        # Independent complex Gaussian log densities, including normalization constants.
        c = gaussian.site_variance[:, None, None, None]
        log_active = (-np.log(np.pi*(variance+c))-abs(r-gaussian.site_mean)**2/(variance+c)).sum(axis=(1, 2, 3))
        log_idle = (-np.log(np.pi*variance)-abs(r)**2/variance).sum(axis=(1, 2, 3))
        expected = expit(logit(.2)+log_active-log_idle)
        np.testing.assert_allclose(right.activity, expected, rtol=1e-12, atol=1e-15)
        np.testing.assert_allclose(right.mean, expected[:, None, None, None]*right.conditional_mean)
        if variance <= 100:
            assert not np.allclose(left.activity, right.activity)
        else:
            np.testing.assert_allclose(left.mean, right.mean)
    assert gaussian.classifier_calls == 0
    assert gaussian.model.samples == 6  # No score query outside training support.


def test_activity_evidence_changes_next_mp_query():
    rng = np.random.default_rng(43)
    operator = (rng.normal(size=(6, 3, 2))+1j*rng.normal(size=(6, 3, 2)))/np.sqrt(6)
    y = rng.normal(size=(6, 2, 2))+1j*rng.normal(size=(6, 2, 2))
    inputs = ReceiverInput(y, operator, .2, .2)
    cfg = SpatialConfig(iterations=3, min_iterations=3, covariance_mode='isotropic')
    queries = []
    for denoiser in make_pair():
        observed = []
        run_spatial_score(inputs, denoiser, scale=1., initial_variance=.2, config=cfg,
                          observer=lambda row, state, r, *rest: observed.append(r.copy()))
        queries.append(observed)
    np.testing.assert_array_equal(queries[0][0], queries[1][0])
    assert not np.allclose(queries[0][1], queries[1][1])


def test_paired_statistics_keeps_scene_pairs_and_pooled_energies(tmp_path):
    spec = dict(scenes=3, values=[0], methods=['proposed', 'gaussian_site'],
                bootstrap_seed=7, bootstrap_replicates=50)
    for scene in range(3):
        for method, errors, misses in [('proposed', 1., 0), ('gaussian_site', 2., 1)]:
            save(tmp_path/f'scene{scene:03d}'/'condition00'/f'{method}.json',
                 dict(status='COMPLETE', input_array_sha256={'observation':str(scene)},
                      metrics=dict(active=2, inactive=8, signal_energy=3.+scene,
                                   full_error=errors*(scene+1), misses=misses, false_alarms=0)))
    row = paired_statistics(tmp_path, spec)[0]
    assert row['delta_aer'] == pytest.approx(-.1)
    assert row['delta_nmse_db'] == pytest.approx(10*np.log10(.5))
    assert row['delta_nmse_db_ci95_high'] == pytest.approx(row['delta_nmse_db'])
    path = tmp_path/'scene001'/'condition00'/'gaussian_site.json'
    failed = read(path); failed['status'] = 'FAILED'; save(path, failed)
    with pytest.raises(ValueError, match='every planned result'):
        paired_statistics(tmp_path, spec)
