"""Independent Gaussian-message algebra candidate; no trained receiver binding."""

from .messages import ColumnLinear, GaussianMessage, extrinsic, gaussian_posterior

__all__ = ['ColumnLinear', 'GaussianMessage', 'extrinsic', 'gaussian_posterior']
