from types import SimpleNamespace
import numpy as np
from scipy.special import expit, logit
from algorithm.STMP.records import SpatialConfig
from algorithm.STMP.denoiser import Denoiser as LearnedDenoiser
from algorithm.C_STMP_ablation_20261028.denoiser import GaussianPriorDenoiser, GaussianSiteDenoiser


def query():
    rng = np.random.default_rng(713)
    return (rng.normal(size=(3, 2, 2, 2))+1j*rng.normal(size=(3, 2, 2, 2)))*.4


def test_analytic_gaussian_prior_matches_independent_log_density_and_moments():
    r, v, gamma, rho = query(), .7, 1.3, .2
    model = GaussianPriorDenoiser(variance=gamma, activity_prior=rho, controls=SpatialConfig())
    state = model(r, v*np.eye(2))
    d = np.prod(r.shape[1:])
    energy = abs(r.reshape(3, -1))**2
    active_logpdf = -d*np.log(np.pi*(gamma+v))-energy.sum(1)/(gamma+v)
    inactive_logpdf = -d*np.log(np.pi*v)-energy.sum(1)/v
    p = expit(logit(rho)+active_logpdf-inactive_logpdf)
    mu, tau = gamma/(gamma+v)*r, gamma*v/(gamma+v)
    np.testing.assert_allclose(state.activity, p, rtol=1e-12)
    np.testing.assert_allclose(state.conditional_mean, mu, rtol=1e-12)
    np.testing.assert_allclose(state.mean, p[:, None, None, None]*mu, rtol=1e-12)
    gram = np.stack([x.reshape(2,-1)@x.reshape(2,-1).conj().T/4 for x in mu])
    np.testing.assert_allclose(state.spatial_covariance,
        p[:, None, None]*tau*np.eye(2)+(p*(1-p))[:, None, None]*gram, rtol=1e-12)


class Moments:
    noise_support = (.001, 10.)
    samples = 0
    def infer(self, r, v):
        self.samples += len(r)
        return SimpleNamespace(mean=.6*r, variance=np.full(len(r), .2))


class Evidence:
    noise_support = Moments.noise_support
    training_class_prior = .5
    def infer(self, r, v, mean):
        return np.ones(len(r))*2


def test_gaussian_evidence_retains_learned_conditional_moments_but_updates_joint_feedback():
    kwargs = dict(activity_prior=.1, conditional_variance_floor=1e-4)
    learned = LearnedDenoiser(Moments(), Evidence(), **kwargs)
    ablated = GaussianSiteDenoiser(Moments(), None, **kwargs)
    for scale, v in ((1., .7), (.8, .5)):
        a, b = learned(scale*query(), v*np.eye(2)), ablated(scale*query(), v*np.eye(2))
        np.testing.assert_array_equal(a.conditional_mean, b.conditional_mean)
        np.testing.assert_array_equal(a.conditional_spatial_covariance, b.conditional_spatial_covariance)
        assert not np.allclose(a.activity, b.activity)
        assert not np.allclose(a.mean, b.mean)
        assert not np.allclose(a.spatial_covariance, b.spatial_covariance)
    assert ablated.classifier_calls == 0 and ablated.model.samples == 6


def test_fixed_gaussian_site_allows_original_stopping_and_keeps_activity_prior():
    controls = SpatialConfig(activity_weight_residual_tolerance=1e-3)
    low = GaussianPriorDenoiser(variance=1., activity_prior=.1, controls=controls)
    high = GaussianPriorDenoiser(variance=1., activity_prior=.4, controls=controls)
    r = query()
    for _ in range(80):
        a = low(r, np.eye(2))
    b = high(r, np.eye(2))
    assert low.message_fresh and np.all(b.activity > a.activity)
    assert low.last['raw_site_residual'] == 0


def input_adapter():
    import importlib.util
    from project import ROOT
    path=ROOT/'result/snr_comparison/data/c_stmp_ablation_1000_20261028/run.py'
    spec=importlib.util.spec_from_file_location('ablation_runner_test',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.receiver_input


def test_main_snr_archive_input_adapter_uses_existing_field_names_and_ignores_noise_truth():
    public=dict(y=np.ones((3,2,2),complex),a=np.ones((3,4,2),complex),rho=np.asarray(.1),noise_variance=np.asarray(999.))
    current=input_adapter()(public)
    np.testing.assert_array_equal(current.observation,public['y'])
    np.testing.assert_array_equal(current.operator,public['a'])
    assert current.noise_variance == 1. and current.activity_prior == .1


def test_phase_input_adapter_uses_original_pilot_instead_of_known_phase_operator():
    from system.receiver.unknown_phase import UnknownPhaseInput
    public=dict(y=np.ones((3,2,2),complex),a=np.ones((3,4,2),complex)*1j,rho=np.asarray(.1),noise_variance=np.asarray(999.))
    raw=dict(y=public['y'],pilot=np.ones((3,4,2),complex),rho=public['rho'])
    current=input_adapter()(public,raw)
    assert isinstance(current,UnknownPhaseInput) and current.noise_variance == 1.
    np.testing.assert_array_equal(current.pilot,raw['pilot'])
    assert not np.array_equal(current.pilot,public['a'])
