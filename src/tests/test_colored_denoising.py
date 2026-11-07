"""Check AWGN units and the direct-mean contract with an analytic Gaussian fixture."""
from copy import deepcopy

import numpy as np
import pytest
import torch

from algorithm import registry
from evaluation import colored_denoising as adapter
from utils import sha256


def gaussian_fixture(tmp_path, monkeypatch, *, scale=2.):
    checkpoint = tmp_path/'fixture.pt'
    checkpoint.write_bytes(b'analytic Gaussian fixture, not learned weights')

    class Gaussian(torch.nn.Module):
        def forward(self, x, covariance, spectral):
            # Unit complex Gaussian prior: D=x/(1+v), Sigma=vI/2.
            torch.testing.assert_close(spectral.variance_eigenvalues[:, 0, 0], covariance.variance/2)
            return x/(1+covariance.variance[:, None, None, None, None])

    blob = dict(order=1, normalization='population_rms', global_complex_rms=1.,
                metadata={'epoch': 200},
                config=dict(antennas=16, side=16, snr_db_min=-20, snr_db_max=30))
    monkeypatch.setattr(adapter, 'load_checkpoint', lambda *args: (Gaussian(), blob))
    return adapter.PretrainedColoredFirst({'scale': scale}, checkpoint, sha256(checkpoint), batch_size=2)


@pytest.mark.parametrize('variance', [.1, np.array([.01, .1, 1.])])
def test_direct_mean_and_scale_conversion(tmp_path, monkeypatch, variance):
    model = gaussian_fixture(tmp_path, monkeypatch)
    rng = np.random.default_rng(7)
    query = rng.normal(size=(3, 16, 16, 16))+1j*rng.normal(size=(3, 16, 16, 16))
    before = query.copy()
    actual, metadata = model.infer(query, variance, priors=None)
    v = np.broadcast_to(variance, (len(query),))
    expected = query/(1+4*v[:, None, None, None])
    np.testing.assert_allclose(actual, expected, atol=2e-7, rtol=2e-7)
    np.testing.assert_array_equal(query, before)
    assert metadata == {}


def test_checkpoint_hash_checked_before_loading(tmp_path, monkeypatch):
    path = tmp_path/'changed.pt'
    path.write_bytes(b'changed')
    monkeypatch.setattr(adapter, 'load_checkpoint', lambda *a: pytest.fail('Changed weights loaded'))
    with pytest.raises(ValueError, match='checkpoint changed'):
        adapter.PretrainedColoredFirst({'scale': 1.}, path, 'not-the-hash')


def test_selected_denoiser_has_no_second_or_classifier_dependency():
    catalog = registry.load_catalog()
    spec = catalog['pretrained_colored_first']
    binding = deepcopy(registry.load_models())
    for key in ('first_checkpoint', 'second_checkpoint', 'evidence_checkpoint'):
        binding['STMP'][key] = 'missing_'+key+'.pt'
    files = registry.source_files(spec, binding, 'cpu')
    assert [path.name for path in files if path.suffix == '.pt'] == ['first_best.pt']
    assert not spec.get('uses_truth', False)
