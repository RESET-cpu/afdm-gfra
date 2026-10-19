"""Fresh NCSN++ score for AFDM blocks, independent of all existing weights.

The vendored architecture is from Song et al.'s official score-SDE repository.
Input coordinates are centered real/imaginary channel coefficients.  A complex
noise variance v means real-coordinate standard deviation sqrt(v / 2), and the
returned score is the gradient with respect to those real coordinates. Thus
Tweedie's conditional mean uses x + (v / 2) * score(x, v).

Architecture dimensions and fir=False are local AFDM/CPU/MPS choices; the L-STMP
paper does not specify all these settings. See vendor/PROVENANCE.json.
"""

from types import SimpleNamespace

import torch
from torch import nn

try:
    from .vendor.score_sde_pytorch.models.ncsnpp import NCSNpp
except ImportError:  # Direct execution/import from the experiment directory.
    from vendor.score_sde_pytorch.models.ncsnpp import NCSNpp


def score_config(width: int = 64) -> SimpleNamespace:
    """Return all explicit upstream NCSN++ settings used by this experiment."""
    if width < 32 or width % 32:
        raise ValueError("width must be a positive multiple of 32")
    return SimpleNamespace(
        training=SimpleNamespace(continuous=True),
        data=SimpleNamespace(image_size=16, num_channels=32, centered=True),
        model=SimpleNamespace(
            name="ncsnpp", nf=width, ch_mult=(1, 2, 2), num_res_blocks=2,
            attn_resolutions=(4,), dropout=0.0, resamp_with_conv=True,
            conditional=True, fir=False, fir_kernel=(1, 3, 3, 1),
            skip_rescale=True, resblock_type="biggan", progressive="none",
            progressive_input="none", embedding_type="fourier",
            progressive_combine="sum", init_scale=0.0, fourier_scale=16.0,
            nonlinearity="swish", normalization="GroupNorm",
            scale_by_sigma=True, sigma_min=(0.001 / 2) ** 0.5,
            sigma_max=(100.0 / 2) ** 0.5, num_scales=1000,
        ),
    )


def score_config_dict(width: int = 64) -> dict:
    """JSON-serializable configuration for provenance and checkpoint metadata."""
    return {name: vars(value).copy() for name, value in vars(score_config(width)).items()}


class FreshScore(nn.Module):
    """Randomly initialized NCSN++; initialization never reads a checkpoint."""

    def __init__(self, width: int = 64):
        super().__init__()
        self.width = width
        self.config = score_config(width)
        # Upstream sigma schedule is float64 by default. Cast the model/buffers
        # on CPU before device placement since MPS does not support float64.
        self.network = NCSNpp(self.config).float()

    def forward(self, x: torch.Tensor, complex_variance: torch.Tensor) -> torch.Tensor:
        if x.ndim != 5 or tuple(x.shape[1:]) != (2, 16, 16, 16):
            raise ValueError("Expected x with shape [batch, 2, 16, 16, 16]")
        variance = torch.as_tensor(complex_variance, dtype=x.dtype, device=x.device)
        if variance.ndim != 1 or variance.shape[0] != x.shape[0]:
            raise ValueError("Expected complex_variance with shape [batch]")
        # No silent clipping: positivity is the caller's model constraint.
        sigma = torch.sqrt(variance / 2)
        flat = x.reshape(x.shape[0], 32, 16, 16)
        return self.network(flat, sigma).reshape_as(x)
