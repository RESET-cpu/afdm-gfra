"""Analytic density, author-code parity and Gaussian-message algebra checks."""
import ast
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from experiments.lstmp_cai_activity_candidate_20261019.evidence import (
    GaussianPriorActivity, gaussian_site_log_odds, site_from_conditional_moments,
)


def test_general_site_matches_complex_normal_density():
    rng = np.random.default_rng(81)
    r = rng.normal(size=(4, 2, 3)) + 1j * rng.normal(size=(4, 2, 3))
    e = rng.normal(size=r.shape) + 1j * rng.normal(size=r.shape)
    v, c, rho = np.array([.2, 1., 3., 10.]), np.array([2., .4, 1., 5.]), .13
    pack = lambda a: torch.tensor(np.stack((a.real, a.imag), axis=1))
    actual = gaussian_site_log_odds(pack(r), v, pack(e), c, rho).numpy()
    log_pdf = lambda x, variance: -6*np.log(np.pi*variance) - (abs(x)**2).sum((1, 2))/variance
    expected = math.log(rho/(1-rho)) + log_pdf(r-e, v+c) - log_pdf(r, v)
    np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-12)


def test_matches_archived_author_activity_function():
    path = Path(__file__).resolve().parents[1] / 'references/known_phase_iteration_review_20260928/cai_official_main_stmp_jadce.py.txt'
    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'lambda_post_gaussian')
    module = ast.Module(body=[fn], type_ignores=[])
    namespace = {'torch': torch}
    exec(compile(ast.fix_missing_locations(module), str(path), 'exec'), namespace)
    gen = torch.Generator().manual_seed(11)
    packed = torch.randn((5, 2, 2, 3), generator=gen, dtype=torch.float64)
    complex_values = torch.complex(packed[:, 0], packed[:, 1]).transpose(1, 2).reshape(15, 2)
    owner = SimpleNamespace(K=5, N=3, M=2, var_h=1., lamda=.1, device='cpu')
    # Author constructs float32 site tensors; use float32 inputs for parity.
    expected, _ = namespace['lambda_post_gaussian'](owner, complex_values.cfloat(), torch.full((2,), 2.), 0)
    actual = torch.sigmoid(GaussianPriorActivity(1.)(packed.float(), torch.full((5,), 2.), packed.float(), .1))
    torch.testing.assert_close(actual, expected, rtol=2e-6, atol=2e-7)


def test_posterior_to_extrinsic_recovers_gaussian_prior():
    gen = torch.Generator().manual_seed(21)
    r = torch.randn((3, 2, 4), generator=gen, dtype=torch.float64)
    e = torch.randn((3, 2, 4), generator=gen, dtype=torch.float64)
    v, c = torch.tensor([.2, 1., 8.], dtype=torch.float64), torch.tensor([1., 3., .4], dtype=torch.float64)
    tau = 1 / (1/v + 1/c)
    mu = tau[:, None, None] * (r/v[:, None, None] + e/c[:, None, None])
    restored_e, restored_c = site_from_conditional_moments(r, v, mu, tau)
    torch.testing.assert_close(restored_e, e, rtol=1e-12, atol=1e-12)
    torch.testing.assert_close(restored_c, c, rtol=1e-12, atol=1e-12)


def test_invalid_conditional_variance_is_not_silently_repaired():
    r = torch.zeros((2, 2, 3))
    for tau in [0., 1., 2., float('nan')]:
        with pytest.raises(ValueError, match='positive extrinsic precision'):
            site_from_conditional_moments(r, 1., r, tau)
