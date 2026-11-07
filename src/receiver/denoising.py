"""Pretrained first-score denoising only; genie uses explicitly supplied truth."""
from dataclasses import replace
import numpy as np
from scenario.geometry_consistent import draw_scene
from scenario.continuous import user_channel
from training.organized.stmp.data import candidate_indices
from channel import config as physical_config

class FirstChannelMean:
    """Use the same first-score Tweedie mean as the complete receiver."""
    def __init__(self, scale, path, *, device, batch_size=8):
        from networks.score import load_direct_checkpoint
        self.first, blob = load_direct_checkpoint(path, device)
        if blob['order'] != 1 or blob.get('normalization') != 'population_rms':
            raise ValueError('Population-coordinate first score required')
        self.scale_ratio = scale/blob['global_complex_rms']
        self.noise_support = (.001/self.scale_ratio**2, 100./self.scale_ratio**2)
        self.device, self.batch_size = device, batch_size

    def infer(self, observation, variance):
        import torch
        from receiver.stmp.moments import convert_moments
        from receiver.stmp.moments import MatrixMomentEstimate
        query = np.asarray(observation, complex)
        variances = np.broadcast_to(np.asarray(variance, float), (len(query),))
        means = []
        with torch.inference_mode():
            for start in range(0, len(query), self.batch_size):
                block = query[start:start+self.batch_size]
                vb = variances[start:start+self.batch_size]
                packed = self.scale_ratio*np.stack((block.real, block.imag), axis=1)
                x = torch.tensor(packed, dtype=torch.float32, device=self.device)
                v = torch.tensor(vb*self.scale_ratio**2, dtype=torch.float32, device=self.device)
                score = self.first(x, v).cpu().numpy().astype(float)
                # The shared conversion's mean does not depend on the second score.
                mean = convert_moments(block, vb, score, np.zeros_like(score), self.scale_ratio).mean
                means.append(mean)
        return MatrixMomentEstimate(np.concatenate(means), None)


def clean_channels(seed, users, candidates, *, genie_scale=None):
    """Uniform candidate selection before activity masking, as in training."""
    scene, _ = draw_scene(seed, n_users=users)
    selected = candidate_indices(seed, users, candidates)
    channels = np.stack([user_channel(scene.paths_of(int(u))) for u in selected])
    if genie_scale is None:
        return channels, selected
    return channels, selected, [genie_prior(scene.paths_of(int(u)), genie_scale) for u in selected]


def genie_prior(paths, scale):
    """True path geometry/powers and LOS gain; diffuse gains remain unknown.

    Given this side information h = m + B g, g ~ CN(0,I). The frozen LOS
    gain has random phase and fixed amplitude, so geometry-only LMMSE is
    not an MMSE lower bound for this channel distribution.
    """
    los, columns = [], []
    for path in paths:
        kind = physical_config.NTN_TDL_D_FADING[path.path_id]
        if kind == 'los':
            los.append(path)
        elif kind == 'rayleigh':
            power = 10.**(physical_config.NTN_TDL_D_POWER_DB[path.path_id]/10)
            atom = user_channel([replace(path, gain=1., legacy_gain=1.)])/scale
            columns.append(np.sqrt(power)*atom.reshape(-1))
        else:
            raise ValueError('Genie bound requires conditionally Gaussian diffuse gains')
    mean = user_channel(los)/scale
    basis, singular, _ = np.linalg.svd(np.stack(columns, axis=1), full_matrices=False)
    return dict(mean=mean, basis=basis, eigenvalues=singular**2)


def genie_mmse(query, variance, priors):
    """Conditional posterior mean and analytic Bayes MSE, in training units."""
    means, risks = [], []
    for received, prior in zip(query, priors, strict=True):
        basis, eigenvalues, known = prior['basis'], prior['eigenvalues'], prior['mean']
        residual = (received-known).reshape(-1)
        update = basis@((eigenvalues/(eigenvalues+variance))*(basis.conj().T@residual))
        means.append(known+update.reshape(known.shape))
        risks.append(float(np.sum(variance*eigenvalues/(eigenvalues+variance))))
    return np.stack(means), np.asarray(risks)


def denoising_metrics(mean, truth, predicted_variance=None):
    axes = tuple(range(1, truth.ndim))
    error = np.sum(abs(mean-truth)**2, axis=axes)
    energy = np.sum(abs(truth)**2, axis=axes)
    arrays = dict(error=error, energy=energy)
    if predicted_variance is not None:
        arrays['predicted_error'] = np.asarray(predicted_variance)*int(np.prod(truth.shape[1:]))
    if not all(np.isfinite(a).all() for a in arrays.values()):
        raise FloatingPointError('Nonfinite denoising output or error prediction')
    return arrays


class NoisyQuery:
    def __init__(self, *, device='cpu'):
        pass

    def infer(self, query, variance, *, priors):
        return query, {}


class GaussianMean:
    def __init__(self, configuration, *, device='cpu'):
        self.power = configuration['initialization']['normalized_training_second_moment']

    def infer(self, query, variance, *, priors):
        return self.power/(self.power+variance)*query, {}


class GenieMean:
    def __init__(self, *, device='cpu'):
        pass

    def infer(self, query, variance, *, priors):
        mean, risk = genie_mmse(query, variance, priors)
        return mean, {'analytic_error': risk}


class PretrainedFirst:
    def __init__(self, configuration, *, device='cpu'):
        from workspace import ROOT
        self.first = FirstChannelMean(configuration['scale'], ROOT/configuration['first_checkpoint'],
                                      device=device, batch_size=4)

    def infer(self, query, variance, *, priors):
        return self.first.infer(query, variance).mean, {}
