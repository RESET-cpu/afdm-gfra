"""Prior channel samples and explicitly truth-conditioned benchmark priors."""
from dataclasses import replace
import numpy as np
from scenario.geometry_consistent import draw_scene
from scenario.continuous import user_channel
from channel import config as physical_config

def candidate_indices(seed, users, count):
    rng = np.random.default_rng(np.random.SeedSequence([seed, 20261006, 81]))
    return rng.choice(users, size=count, replace=False)

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
