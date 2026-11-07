"""Numerical changes of observable contributions, not phase-error estimates."""
import numpy as np


def trial_changes(projected, feedback, frames, previous_beta, beta, angle, *, gram, variance, noise):
    """Avoid unidentifiable inactive phases and cancellation between users.

    projected[k,l,m] is the current physical per-user predicted contribution.
    A zero-energy contribution has zero weight. No truth/activity gate is used.
    """
    delta = np.angle(np.exp(1j * (beta - previous_beta)))
    rotation = np.exp(1j * (delta[:, None] * frames + angle[:, None]))
    signal_energy = float(np.sum(abs(projected)**2))
    feedback_energy = float(np.sum(abs(feedback)**2))
    prediction = (np.sqrt(float(np.sum(abs(projected * (rotation - 1)[..., None])**2))
                          / signal_energy) if signal_energy > 0 else 0.)
    slope_rotation = np.exp(1j*delta[:,None]*frames)
    slope = (np.sqrt(float(np.sum(abs(projected*(slope_rotation-1)[...,None])**2))
                     / signal_energy) if signal_energy > 0 else 0.)
    channel = (np.sqrt(float(np.sum(abs(feedback * (np.exp(1j*angle)-1)[:, None, None, None])**2))
                       / feedback_energy) if feedback_energy > 0 else 0.)
    # Even a zero mean can carry phase information in its Gaussian covariance.
    # Include public noise so vanishing uncertainty has vanishing weight.
    if noise <= 0 or variance < 0:
        raise ValueError('Positive noise and nonnegative feedback variance required')
    covariances = []
    for slopes in (previous_beta, beta):
        phi = np.exp(1j*slopes[:,None]*frames)
        covariances.append(noise*np.eye(len(frames)) + variance*np.sum(
            gram*phi[:,:,None]*phi[:,None,:].conj(), axis=0))
    covariance = float(np.linalg.norm(covariances[1]-covariances[0]) /
                       max(np.linalg.norm(covariances[0]), np.linalg.norm(covariances[1])))
    return dict(prediction_change=float(prediction), channel_rotation_change=float(channel),
                slope_prediction_change=float(slope),
                observation_covariance_change=covariance, zero_mean_contribution=signal_energy == 0,
                contribution_energy=signal_energy, feedback_energy=feedback_energy,
                maximum_wrapped_slope_change_diagnostic=float(np.max(abs(delta))))
