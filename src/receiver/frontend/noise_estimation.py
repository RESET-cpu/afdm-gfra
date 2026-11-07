"""Observation-only white-noise estimate from a spatial sample covariance.

Wax--Kailath MDL, as stated in Nadakuditi--Edelman (2008), Sec. I-B,
Eqs. (5)--(7). The mean of the selected trailing eigenvalues estimates the
common complex noise variance. Its use before SOMP/GNN-ASPL is an explicit
AFDM adaptation; neither original receiver paper supplies this front end.
"""
import numpy as np

from channel.observation import ReceiverInput
from channel.unknown_phase import UnknownPhaseInput


def estimate_spatial_noise(observation):
    y = np.asarray(observation, dtype=np.complex128)
    if y.ndim != 3 or not all(y.shape) or not np.isfinite(y).all():
        raise ValueError('Finite observation[frame,antenna,sample] required')
    samples = y.transpose(0, 2, 1).reshape(-1, y.shape[1])
    count, antennas = samples.shape
    if count <= antennas or antennas < 2:
        raise ValueError('Spatial noise estimation requires at least two antennas and more samples than antennas')
    eigenvalues = np.linalg.svd(samples, compute_uv=False)**2/count
    if eigenvalues[0] <= 0:
        raise ValueError('Positive received energy required to estimate a noise scale')
    floor = np.finfo(float).eps*eigenvalues[0]
    eigenvalues = np.maximum(eigenvalues, floor)
    ranks = np.arange(antennas)
    trailing_mean = np.array([np.mean(eigenvalues[k:]) for k in ranks])
    log_geometric = np.array([np.mean(np.log(eigenvalues[k:])) for k in ranks])
    mdl = count*(antennas-ranks)*(np.log(trailing_mean)-log_geometric)
    mdl += .5*ranks*(2*antennas-ranks)*np.log(count)
    rank = int(np.argmin(mdl))
    noise = float(trailing_mean[rank])
    return noise, dict(method='Wax_Kailath_MDL', noise_variance_estimate=noise,
        estimated_signal_rank=rank, samples=count, antennas=antennas,
        eigenvalues=eigenvalues.tolist(), mdl=mdl.tolist(),
        rank_scope='Spatial covariance rank; not a detected active-user count',
        model='Spatially white noise plus a lower-rank received signal',
        supplied_noise_variance_used=False)


def load_unknown_noise_input(path, *, phase_mode):
    """Accept three public fields; never read a legacy noise_variance value."""
    matrix = 'pilot' if phase_mode == 'estimated' else 'operator'
    required = {'observation', matrix, 'activity_prior'}
    with np.load(path, allow_pickle=False) as saved:
        if not required <= set(saved.files) or set(saved.files)-required-{'noise_variance'}:
            raise ValueError('Unknown-noise input requires observation, '+matrix+', activity_prior')
        y, p, prior = saved['observation'], saved[matrix], float(saved['activity_prior'])
    noise, _ = estimate_spatial_noise(y)
    model = UnknownPhaseInput if phase_mode == 'estimated' else ReceiverInput
    return model(y, p, noise, prior)
