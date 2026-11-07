"""Original full-channel DSM batch draws in population-RMS coordinates."""
import numpy as np
import torch


def scalar_real_variance(complex_variance):
    flat = complex_variance.flatten(1)
    if not bool(torch.all(flat == flat[:, :1])):
        raise ValueError('Cai scalar-noise objectives require one variance per sample')
    if not bool(torch.all(torch.isfinite(flat[:, 0]) & (flat[:, 0] > 0))):
        raise ValueError('invalid scalar noise variance')
    return flat[:, 0]/2


def make_cai_batch(channels, rng, scale, *, normalization='population_rms',
                   snr_db_min=-20, snr_db_max=30, noise_conditioning='continuous'):
    """Preserve the original uniform-SNR then float64-normal RNG draw order."""
    channels = np.asarray(channels)
    if channels.ndim != 4 or not np.isfinite(scale) or scale <= 0:
        raise ValueError('expected physical H samples and positive fixed RMS')
    if normalization != 'population_rms' or noise_conditioning != 'continuous':
        raise ValueError('original full-score population-RMS continuous-noise recipe required')
    if (type(snr_db_min) is not int or type(snr_db_max) is not int
            or snr_db_min >= snr_db_max):
        raise ValueError('integer SNR endpoints in increasing order required')
    clean = np.stack((channels.real, channels.imag), axis=1).astype(np.float32)/scale
    levels = np.power(10., -rng.uniform(snr_db_min, snr_db_max, len(clean))/10)
    labels = levels.astype(np.float32)
    variance = np.broadcast_to(levels[:, None, None, None],
                              (len(clean), *clean.shape[2:])).astype(np.float32).copy()
    epsilon = rng.standard_normal(clean.shape).astype(np.float32)
    noisy = clean+np.sqrt(variance[:, None]/2)*epsilon
    return clean, noisy, variance, labels
