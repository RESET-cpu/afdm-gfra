"""Numerical checks of the Gaussian activity integral and unchanged site rules."""
import unittest
from types import SimpleNamespace
import numpy as np
from scipy.special import expit, logit
from scipy.stats import multivariate_normal
from algorithm.STMP.posterior import full_posterior
from algorithm.C_STMP_analytic.denoiser import Denoiser


class GaussianActivity(unittest.TestCase):
    def test_complex_density_and_posterior_identity(self):
        rng = np.random.default_rng(2506)
        r = .2*(rng.normal(size=(4, 2, 2, 3))+1j*rng.normal(size=(4, 2, 2, 3)))
        e = .1*(rng.normal(size=r.shape)+1j*rng.normal(size=r.shape))
        c, v, rho = np.array([.05, .1, .2, .4]), .7, .2
        result = full_posterior(r, v, e, c, rho)
        n = r[0].size
        pack = lambda z: np.r_[z.real.ravel(), z.imag.ravel()]
        ell = []
        for k in range(len(r)):
            active = multivariate_normal.logpdf(pack(r[k]), mean=pack(e[k]), cov=(v+c[k])/2*np.eye(2*n))
            inactive = multivariate_normal.logpdf(pack(r[k]), mean=np.zeros(2*n), cov=v/2*np.eye(2*n))
            ell.append(active-inactive)
        np.testing.assert_allclose(result.log_evidence_bound, ell, atol=3e-14, rtol=1e-13)
        np.testing.assert_allclose(result.activity, expit(logit(rho)+ell), atol=1e-14)
        tau = c*v/(c+v)
        mu = result.conditional_mean
        recovered_c = 1/(1/tau-1/v)
        recovered_e = recovered_c[:, None, None, None]*(mu/tau[:, None, None, None]-r/v)
        np.testing.assert_allclose(recovered_c, c, rtol=1e-14)
        np.testing.assert_allclose(recovered_e, e, atol=1e-15)
        identity = np.sum(abs(r)**2, axis=(1,2,3))/v
        identity -= np.sum(abs(r-mu)**2, axis=(1,2,3))/(v-tau)
        identity += n*np.log1p(-tau/v)
        np.testing.assert_allclose(identity, ell, atol=3e-14, rtol=1e-13)
        changed = full_posterior(r, v, e, c, .35)
        np.testing.assert_allclose(logit(changed.activity)-logit(result.activity), logit(.35)-logit(rho), atol=1e-14)

    def test_site_rejection_floor_and_no_classifier(self):
        class Model:
            samples = 0
            noise_support = (.01, 10.)
            raw = .2
            def infer(self, r, v):
                self.samples += len(r)
                return SimpleNamespace(mean=.7*r, variance=np.full(len(r), self.raw))
        model = Model()
        d = Denoiser(model, activity_prior=.1, conditional_variance_floor=1e-4)
        r = np.full((3, 2, 2, 3), .1+.2j)
        d(r, np.eye(2)); self.assertTrue(d.last['site_accepted'])
        site = d.site_mean.copy(), d.site_variance.copy()
        model.raw = 1.1
        d(r, np.eye(2)); self.assertFalse(d.last['site_accepted'])
        np.testing.assert_array_equal(d.site_mean, site[0]); np.testing.assert_array_equal(d.site_variance, site[1])
        model.raw = -.1
        d(r, np.eye(2)); self.assertTrue(d.last['conditional_variance_floored'])
        self.assertAlmostEqual(d.last['used_conditional_variance_per_user'][0], 1e-4)
        samples = model.samples
        d(r, 20*np.eye(2)); self.assertEqual(samples, model.samples)
        self.assertEqual(d.classifier_calls, 0); self.assertFalse(hasattr(d, 'evidence'))


if __name__ == '__main__':
    unittest.main()
