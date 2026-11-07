"""Ding Eq. (27): physical coefficient energy and activity decisions."""
import numpy as np


def coefficient_activity(coefficients, users):
    """Eq. (27): physical coefficient block energy divided by its maximum."""
    z = np.asarray(coefficients)
    if (z.ndim != 2 or not z.size or users < 1 or z.shape[0] % users
            or not np.isfinite(z).all()):
        raise ValueError('finite coefficient blocks and positive user count required')
    energy = np.mean(abs(z.reshape(users, -1, z.shape[1]))**2, axis=(1, 2))
    maximum = float(energy.max())
    score = energy/maximum if maximum > 0 else np.zeros(users)
    return score, energy



def activity_decisions(scores, energies, threshold):
    """Ding uses >=. An all-zero estimate has no defined relative energy."""
    if not np.isfinite(threshold) or threshold < 0:
        raise ValueError('finite nonnegative activity threshold required')
    return (np.asarray(scores) >= threshold) & (np.max(energies) > 0)

