"""Independent CPU oracles for matrix preconditioning and unchanged DSM.

Dense reference matrices use real/imaginary block coordinates and do not call
the candidate's covariance application. Network checks use a reduced-width
backbone or a tiny known linear trunk; no training run or receiver is started.
"""
import numpy as np
import pytest
import torch
from torch import nn

from networks.score import DirectCaiConfig, DirectCaiNetwork
from training.colored_score_20261024.noise import Covariance
from training.colored_preconditioned_20261024.model import PreconditionedScore
from training.colored_preconditioned_20261024.operators import Spectral, from_covariance


def _problem(batch=2, antennas=3, outputs=2, columns=2, seed=1924):
    """Complex, non-diagonal factors with independent antenna/column bases."""
    rng = np.random.default_rng(seed)
    matrices = []
    for size in (antennas, columns):
        g = rng.standard_normal((batch, size, size)) + 1j*rng.standard_normal((batch, size, size))
        gram = g @ g.conj().transpose(0, 2, 1)
        gram *= (size / np.trace(gram, axis1=1, axis2=2).real)[:, None, None]
        matrices.append(torch.from_numpy(.4*np.eye(size) + .6*gram))
    variance = torch.linspace(.07, 9., batch, dtype=torch.float64)
    covariance = Covariance(variance, *matrices)
    shape = (batch, 2, antennas, outputs, columns)
    x = torch.from_numpy(rng.standard_normal(shape))
    return covariance, x


def _dense(covariance, outputs):
    complex_matrices, real_matrices = [], []
    for v, a, c in zip(covariance.variance, covariance.antenna, covariance.column):
        eye = torch.eye(outputs, dtype=a.dtype)
        full = v*torch.kron(torch.kron(a.contiguous(), eye), c.contiguous())
        sigma = .5*torch.cat((torch.cat((full.real, -full.imag), dim=1),
                               torch.cat((full.imag, full.real), dim=1)), dim=0)
        complex_matrices.append(full)
        real_matrices.append(sigma)
    return torch.stack(complex_matrices), torch.stack(real_matrices)


def _function(matrix, function):
    eigenvalues, vectors = torch.linalg.eigh(matrix)
    return (vectors * function(eigenvalues).unsqueeze(-2)) @ vectors.mT


def _apply(matrix, packed):
    return torch.bmm(matrix, packed.flatten(1).unsqueeze(-1)).reshape_as(packed)


def _small_model(antennas=3, side=2, reference=.5, dtype=torch.float64):
    base = DirectCaiNetwork(DirectCaiConfig(antennas=antennas, side=side, base_channels=8))
    return PreconditionedScore(base, reference_real_variance=reference).to(dtype=dtype)


def test_spectral_matches_dense_complex_and_real_covariance():
    covariance, x = _problem()
    spectral = from_covariance(covariance)
    full, sigma = _dense(covariance, x.shape[3])
    torch.testing.assert_close(spectral.apply(x, spectral.variance_eigenvalues), _apply(sigma, x),
                               atol=2e-12, rtol=2e-11)
    # Multiplying the real covariance by two recovers the complex covariance.
    z = torch.complex(x[:, 0], x[:, 1]).flatten(1)
    actual = spectral.apply(x, 2*spectral.variance_eigenvalues)
    actual_complex = torch.complex(actual[:, 0], actual[:, 1]).flatten(1)
    torch.testing.assert_close(actual_complex, torch.bmm(full, z.unsqueeze(-1)).squeeze(-1),
                               atol=4e-12, rtol=2e-11)
    for power in (-1., -.5, .5):
        expected = _apply(_function(sigma, lambda values: values.pow(power)), x)
        torch.testing.assert_close(spectral.apply(x, spectral.variance_eigenvalues.pow(power)),
                                   expected, atol=3e-11, rtol=3e-11)


def test_spectral_basis_phase_and_output_axis_do_not_change_operator():
    covariance, x = _problem()
    spectral = Spectral.from_covariance(covariance)
    # Arbitrary eigenvector phases must cancel between analysis and synthesis.
    pa = torch.exp(1j*torch.linspace(.2, 1.1, x.shape[2], dtype=torch.float64))
    pc = torch.exp(1j*torch.linspace(-.7, .3, x.shape[4], dtype=torch.float64))
    changed = Spectral(spectral.antenna_vectors*pa, spectral.column_vectors*pc,
                       spectral.variance_eigenvalues)
    multiplier = (.5 + spectral.variance_eigenvalues).rsqrt()
    torch.testing.assert_close(changed.apply(x, multiplier), spectral.apply(x, multiplier),
                               atol=2e-12, rtol=2e-11)
    # An identity output factor must not mix two different output rows.
    only_first = x.clone(); only_first[:, :, :, 1:] = 0
    assert torch.count_nonzero(spectral.apply(only_first, multiplier)[:, :, :, 1:]) == 0


@pytest.mark.parametrize('reference', [.2, .5, 1.3])
def test_from_raw_matches_dense_matrix_functions_and_reference_linear_mean(reference):
    covariance, observation = _problem()
    spectral = from_covariance(covariance)
    model = _small_model(reference=reference)
    full, sigma = _dense(covariance, observation.shape[3])
    k = _function(sigma, lambda values: reference/(reference+values))
    o = _function(sigma, lambda values: (reference*values/(reference+values)).sqrt())
    raw = torch.cos(observation)
    expected = _apply(k, observation) + _apply(o, raw)
    torch.testing.assert_close(model.from_raw(raw, observation, spectral), expected,
                               atol=3e-12, rtol=2e-11)
    zero_mean = model.from_raw(torch.zeros_like(raw), observation, spectral)
    torch.testing.assert_close(zero_mean, _apply(k, observation), atol=3e-12, rtol=2e-11)
    if reference == .5:
        z = torch.complex(observation[:, 0], observation[:, 1]).flatten(1)
        expected_complex = torch.linalg.solve(torch.eye(full.shape[-1], dtype=full.dtype)+full,
                                             z.unsqueeze(-1)).squeeze(-1)
        actual_complex = torch.complex(zero_mean[:, 0], zero_mean[:, 1]).flatten(1)
        torch.testing.assert_close(actual_complex, expected_complex, atol=3e-12, rtol=2e-11)


def test_white_noise_reduces_to_scalar_coefficients_and_stable_dsm():
    variance = torch.tensor([.004, 1.7, 80.], dtype=torch.float64)
    covariance = Covariance(variance,
        torch.eye(2, dtype=torch.complex128).expand(3, -1, -1),
        torch.eye(3, dtype=torch.complex128).expand(3, -1, -1))
    spectral = from_covariance(covariance)
    reference = .7
    model = _small_model(antennas=2, side=3, reference=reference)
    generator = torch.Generator().manual_seed(1925)
    clean, epsilon, raw = [torch.randn(3, 2, 2, 3, 3, dtype=torch.float64, generator=generator)
                           for _ in range(3)]
    lam = (variance/2)[:, None, None, None, None]
    observation = clean + lam.sqrt()*epsilon
    k = reference/(reference+lam)
    o = (reference*lam/(reference+lam)).sqrt()
    torch.testing.assert_close(spectral.apply(observation, (reference+spectral.variance_eigenvalues).rsqrt()),
                               observation/(reference+lam).sqrt(), atol=1e-13, rtol=1e-12)
    mean = model.from_raw(raw, observation, spectral)
    torch.testing.assert_close(mean, k*observation+o*raw, atol=1e-13, rtol=1e-12)
    residual = model.stable_residual(raw, clean, epsilon, spectral)
    expected = k.sqrt()*raw-lam.sqrt()/(reference+lam)*clean+k*epsilon
    torch.testing.assert_close(residual, expected, atol=1e-13, rtol=1e-12)
    torch.testing.assert_close(residual, (mean-clean)/lam.sqrt(), atol=3e-13, rtol=1e-11)


def test_stable_residual_preserves_dsm_raw_weight_and_gradient():
    covariance, clean = _problem()
    spectral = from_covariance(covariance)
    _, sigma = _dense(covariance, clean.shape[3])
    reference = .6
    model = _small_model(reference=reference)
    epsilon = torch.sin(clean*1.7)
    observation = clean+_apply(_function(sigma, torch.sqrt), epsilon)
    raw = torch.cos(clean).requires_grad_()
    k = _function(sigma, lambda values: reference/(reference+values))
    o = _function(sigma, lambda values: (reference*values/(reference+values)).sqrt())
    inverse_root = _function(sigma, torch.rsqrt)
    mean = _apply(k, observation)+_apply(o, raw)
    dense_residual = _apply(inverse_root, mean-clean)
    stable = model.stable_residual(raw, clean, epsilon, spectral)
    torch.testing.assert_close(stable, dense_residual, atol=3e-12, rtol=3e-11)

    target = torch.linalg.solve(o, (clean-_apply(k, observation)).flatten(1).unsqueeze(-1)).reshape_as(raw)
    difference = raw-target
    raw_weighted = (difference*_apply(k, difference)).mean()
    score = torch.linalg.solve(sigma, (mean-observation).flatten(1).unsqueeze(-1)).reshape_as(raw)
    direct_dsm = (_apply(_function(sigma, torch.sqrt), score)+epsilon).square().mean()
    losses = [stable.square().mean(), dense_residual.square().mean(), raw_weighted, direct_dsm]
    gradients = [torch.autograd.grad(loss, raw, retain_graph=True)[0] for loss in losses]
    for loss, gradient in zip(losses[1:], gradients[1:]):
        torch.testing.assert_close(loss, losses[0], atol=2e-12, rtol=2e-11)
        torch.testing.assert_close(gradient, gradients[0], atol=3e-12, rtol=3e-11)
    # Unweighted raw MSE is a different objective: DSM + MSE/reference.
    torch.testing.assert_close(difference.square().mean(),
        losses[0]+(mean-clean).square().mean()/reference, atol=3e-12, rtol=3e-11)
    assert not torch.isclose(difference.square().mean(), losses[0], rtol=.01, atol=0)


class _DenseTrunk(nn.Module):
    """Known non-diagonal linear raw map, replacing only the expensive trunk."""
    def __init__(self, matrix, bias):
        super().__init__()
        self.matrix = nn.Parameter(matrix)
        self.bias = nn.Parameter(bias)

    def forward(self, packed, condition):
        return (packed.flatten(1)@self.matrix.mT+self.bias).reshape_as(packed)


def test_observation_jacobian_includes_skip_input_and_output_operators(monkeypatch):
    covariance, observation = _problem(batch=1)
    spectral = from_covariance(covariance)
    _, sigma = _dense(covariance, observation.shape[3])
    reference = .8
    model = _small_model(reference=reference)
    size = observation[0].numel()
    generator = torch.Generator().manual_seed(1926)
    matrix = torch.randn(size, size, dtype=torch.float64, generator=generator)/size**.5
    bias = torch.randn(size, dtype=torch.float64, generator=generator)
    model.backbone.trunk = _DenseTrunk(matrix, bias)
    b = _function(sigma, lambda values: (reference+values).rsqrt())
    k = _function(sigma, lambda values: reference/(reference+values))
    o = _function(sigma, lambda values: (reference*values/(reference+values)).sqrt())
    expected_raw = (_apply(b, observation).flatten(1)@matrix.mT+bias).reshape_as(observation)
    expected_mean = _apply(k, observation)+_apply(o, expected_raw)
    # Supplying the spectral cache must avoid hidden eigendecompositions.
    def forbidden_eigh(*args, **kwargs):
        raise AssertionError('A supplied spectral cache must be reused')
    monkeypatch.setattr(torch.linalg, 'eigh', forbidden_eigh)
    variable = observation.detach().clone().requires_grad_()
    raw = model.raw(variable, covariance, spectral)
    mean = model(variable, covariance, spectral)
    torch.testing.assert_close(raw, expected_raw, atol=3e-12, rtol=3e-11)
    torch.testing.assert_close(mean, expected_mean, atol=3e-12, rtol=3e-11)
    torch.testing.assert_close(model.mean(variable, covariance, spectral), mean, atol=0, rtol=0)
    score = model.score(variable, covariance, spectral)
    expected_score = torch.linalg.solve(sigma, (mean-variable).flatten(1).unsqueeze(-1)).reshape_as(variable)
    torch.testing.assert_close(score, expected_score, atol=3e-11, rtol=3e-11)
    probe = torch.cos(observation)
    gradient = torch.autograd.grad((mean*probe).sum(), variable)[0]
    jacobian = k + o@matrix@b
    expected_gradient = _apply(jacobian.mT, probe)
    torch.testing.assert_close(gradient, expected_gradient, atol=4e-12, rtol=4e-11)


def test_backbone_copy_condition_gradient_and_checkpoint_roundtrip(tmp_path):
    from training.colored_preconditioned_20261024.formal import Trainer
    from training.colored_preconditioned_20261024.model import load_checkpoint
    torch.manual_seed(1927)
    config = DirectCaiConfig(antennas=2, side=16, base_channels=8)
    base = DirectCaiNetwork(config).eval()
    original = {name: value.detach().clone() for name, value in base.network.state_dict().items()}
    model = PreconditionedScore(base, reference_real_variance=.5).eval()
    current = model.backbone.state_dict()
    for name, before in original.items():
        if name == 'condition.0.weight':
            torch.testing.assert_close(current[name][:, :1], before, atol=0, rtol=0)
            assert torch.count_nonzero(current[name][:, 1:]) == 0
        else:
            torch.testing.assert_close(current[name], before, atol=0, rtol=0)
        assert current[name].data_ptr() != base.network.state_dict()[name].data_ptr()
    assert torch.count_nonzero(current['trunk.end_conv.weight']) > 0
    covariance, observation = _problem(batch=1, antennas=2, outputs=16, columns=16)
    covariance = Covariance(covariance.variance.float(), covariance.antenna.to(torch.complex64),
                            covariance.column.to(torch.complex64))
    observation = observation.float()
    spectral = from_covariance(covariance)
    raw = model.raw(observation, covariance, spectral)
    clean, epsilon = .1*observation, torch.sin(observation)
    model.stable_residual(raw, clean, epsilon, spectral).square().mean().backward()
    gradient = model.backbone.condition[0].weight.grad[:, 1:]
    assert torch.isfinite(gradient).all() and gradient.norm() > 0
    for name, before in original.items():
        torch.testing.assert_close(base.network.state_dict()[name], before, atol=0, rtol=0)
    assert all(parameter.grad is None for parameter in base.parameters())

    path = tmp_path/'preconditioned.pt'
    recipe = dict(scale=.2647966452702405,
        first=dict(initial_checkpoint_sha256='test-initializer'),
        noise=dict(snr_db=[-20, 30], rank=4, max_strength=.5), scope='CPU test only',
        parameterization=dict(reference_real_variance=.5, output='conditional_mean',
                              objective='original_covariance_weighted_DSM'))
    trainer = Trainer(tmp_path, recipe, 'test-specification')
    trainer.save_weight(path, model, dict(loss=1.), 0)
    restored, saved = load_checkpoint(path, 'cpu')
    assert saved['metadata']['initialization_sha256'] == 'test-initializer'
    assert saved['output'] == 'conditional_mean'
    with torch.inference_mode():
        torch.testing.assert_close(restored(observation, covariance, spectral),
                                   model(observation, covariance, spectral), atol=0, rtol=0)
    for field, value in [('schema', 'colored-first-score-matched-v1'), ('output', 'score')]:
        altered = dict(saved, **{field: value})
        torch.save(altered, path)
        with pytest.raises(ValueError, match='conditional-mean'):
            load_checkpoint(path, 'cpu')


def test_float32_stable_loss_matches_old_dsm_at_noise_range_endpoints():
    from training.colored_score_20261024.formal_batches import (
        draw_arrays, loss_from_score)
    rng = np.random.default_rng(1932)
    channels = (rng.standard_normal((3, 16, 16, 16)) +
                1j*rng.standard_normal((3, 16, 16, 16))).astype(np.complex64)
    arrays = list(draw_arrays(channels, rng, np.random.default_rng(1933), 1.,
        dict(snr_db=[-20, 30], rank=4, max_strength=.5)))
    # Exact -20, 0, +30 dB endpoints, retaining the same shape factors/epsilon.
    arrays[2] = np.array([100., 1., .001], dtype=np.float32)
    epsilon = arrays[7][:, 0] + 1j*arrays[7][:, 1]
    colored = np.einsum('baj,bjok,bik->baoi', arrays[5], epsilon, arrays[6], optimize=True)
    transformed = np.stack((colored.real, colored.imag), axis=1)
    arrays[1] = arrays[0] + np.sqrt(arrays[2][:, None, None, None, None]/2)*transformed
    tensors = tuple(torch.from_numpy(value) for value in arrays)
    covariance = Covariance(tensors[2], tensors[3], tensors[4])
    spectral = from_covariance(covariance)
    torch.manual_seed(1934)
    model = PreconditionedScore(DirectCaiNetwork(DirectCaiConfig(base_channels=8))).eval()
    with torch.inference_mode():
        raw = model.raw(tensors[1], covariance, spectral)
        scores = model.score(tensors[1], covariance, spectral)
        stable = model.stable_residual(raw, tensors[0], tensors[7], spectral)
        # Check each endpoint separately, so one cannot be hidden by pooling.
        for i in range(3):
            part = tuple(value[i:i+1] for value in tensors)
            old_loss = loss_from_score(scores[i:i+1], part)
            new_loss = stable[i].square().mean()
            torch.testing.assert_close(new_loss, old_loss, atol=3e-6, rtol=3e-5)
        mean = model.from_raw(raw, tensors[1], spectral)
        torch.testing.assert_close(mean, tensors[1]+covariance.apply_real(scores),
                                   atol=5e-5, rtol=5e-5)


def test_formal_draw_preserves_original_arrays_and_both_rng_streams():
    from training.colored_score_20261024.formal_batches import draw_arrays as original_draw
    from training.colored_preconditioned_20261024.formal_batches import draw_arrays
    rng = np.random.default_rng(1928)
    channels = (rng.standard_normal((3, 16, 16, 16)) +
                1j*rng.standard_normal((3, 16, 16, 16))).astype(np.complex64)
    primary1, primary2 = np.random.default_rng(1930), np.random.default_rng(1930)
    shape1, shape2 = np.random.default_rng(1931), np.random.default_rng(1931)
    noise = dict(snr_db=[-20, 30], rank=4, max_strength=.5)
    original = original_draw(channels, primary1, shape1, .2647966452702405, noise)
    candidate = draw_arrays(channels, primary2, shape2, .2647966452702405, noise)
    assert len(candidate) == 11
    for before, after in zip(original, candidate[:8]):
        np.testing.assert_array_equal(after, before)
    assert primary1.bit_generator.state == primary2.bit_generator.state
    assert shape1.bit_generator.state == shape2.bit_generator.state
    covariance = Covariance(*(torch.from_numpy(candidate[index]) for index in (2, 3, 4)))
    spectral = Spectral(*(torch.from_numpy(value) for value in candidate[8:]))
    # A small principal subproblem is not substituted: check all 16x16 axes.
    x = torch.from_numpy(candidate[7])
    torch.testing.assert_close(spectral.apply(x, spectral.variance_eigenvalues),
                               covariance.apply_real(x), atol=2e-5, rtol=2e-5)
