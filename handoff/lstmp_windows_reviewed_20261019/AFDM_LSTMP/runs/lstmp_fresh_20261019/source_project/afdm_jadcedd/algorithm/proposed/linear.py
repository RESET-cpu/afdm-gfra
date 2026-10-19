"""SVD linear observation updates, independent of the nonlinear prior."""

import numpy as np
from scipy.linalg import eigh, svd
from scipy.linalg.blas import zgemm
from .gaussian import hermitian, spatial_apply


class MMVLinear:
    """MMV observation operator with cached SVD and antenna packing."""

    def __init__(self, pilot, antennas, noise_variance):
        p = np.asarray(pilot, complex)
        if (
            p.ndim != 3
            or not all(p.shape)
            or antennas < 1
            or not np.isfinite(p).all()
            or not np.isfinite(noise_variance)
            or noise_variance <= 0
        ):
            raise ValueError("finite pilot, antenna count and positive noise required")
        self.frames, self.users, self.columns = p.shape
        self.antennas, self.noise = int(antennas), float(noise_variance)
        self.a = np.asfortranarray(p.reshape(self.frames, -1))
        u, self.s, vh = svd(self.a, full_matrices=False, check_finite=True)
        self.uh, self.v = np.asfortranarray(u.conj().T), np.asfortranarray(vh.conj().T)
        self.power = float(np.sum(abs(self.a) ** 2) / self.frames)
        if self.power <= 0:
            raise ValueError("observation operator has no sensitivity")

    def pack(self, value):
        x = np.asarray(value, complex)
        if x.ndim != 4 or x.shape[:2] != (self.users, self.antennas) or x.shape[-1] != self.columns:
            raise ValueError("channel blocks must be [users, antennas, rows, columns]")
        return np.asfortranarray(x.transpose(0, 3, 1, 2).reshape(self.a.shape[1], -1))

    def unpack(self, value):
        return value.reshape(self.users, self.columns, self.antennas, -1).transpose(0, 2, 3, 1)

    def forward(self, value):
        return zgemm(1.0, self.a, self.pack(value)).reshape(self.frames, self.antennas, -1)

    def adjoint(self, observation):
        y = np.asarray(observation, complex).reshape(self.frames, -1)
        return self.unpack(zgemm(1.0, self.a, y, trans_a=2))


class SpatialLinear(MMVLinear):
    """Exact common-antenna-covariance LMMSE, followed by a moment projection."""

    def update(self, observation, mean, covariance):
        # Diagonalize the common antenna covariance before the LMMSE update.
        c, u = eigh(hermitian(np.asarray(covariance, complex)), check_finite=True)
        if c.min() <= 0:
            raise FloatingPointError("positive linear prior required")
        rotated = spatial_apply(u.conj().T, mean)
        y = np.einsum("ml,qlr->qmr", u.conj().T, observation, optimize=False)
        x = self.pack(rotated)
        y = y.reshape(self.frames, -1)
        # Apply the scalar response in each antenna eigenmode (THEORY.md T3).
        gain = self.s[:, None] * c[None] / (self.noise + self.s[:, None] ** 2 * c[None])
        fraction = np.sum(self.s[:, None] * gain, axis=0) / len(x)
        if np.any((fraction <= 0) | (fraction >= 1)):
            raise FloatingPointError("invalid linear response")
        residual = y - zgemm(1.0, self.a, x)
        projected = zgemm(1.0, self.uh, residual).reshape(len(self.s), self.antennas, -1)
        correction = zgemm(1.0, self.v, (gain[:, :, None] * projected).reshape(len(self.s), -1))
        correction = self.unpack(correction)
        # Return posterior and extrinsic moments in the original antenna coordinates.
        post = spatial_apply(u, rotated + correction)
        r = spatial_apply(u, rotated + correction / fraction[None, :, None, None])
        post_c = np.einsum("mi,i,ni->mn", u, c * (1 - fraction), u.conj(), optimize=False)
        cavity = np.einsum(
            "mi,i,ni->mn", u, c * (1 - fraction) / fraction, u.conj(), optimize=False
        )
        return post, hermitian(post_c), r, hermitian(cavity)
