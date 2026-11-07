"""Full channel score with all complex beams packed into real input channels.

The UPA Fourier basis follows the existing array transform. Channel packing
and AFDM-plane residual convolutions are project choices, not a reproduction
of Fesl, Artemasov or DeepRx. A dense input/output projection can absorb the
fixed unitary transform; this model does not assume independent beams.
"""
from dataclasses import dataclass
import math
import numpy as np
import torch
from torch import nn
from .array_transforms import spatial_matrix, packed_transform


@dataclass(frozen=True)
class ChannelScoreConfig:
    rows: int = 4
    columns: int = 4
    side: int = 16
    width: int = 64
    blocks: int = 6
    conditioning_width: int = 128
    representation: str = 'beam'
    snr_db_min: int = -45
    snr_db_max: int = 40
    noise_conditioning: str = 'continuous'

    @property
    def antennas(self):
        return self.rows*self.columns

    def __post_init__(self):
        if min(self.rows,self.columns,self.side,self.width,self.blocks,self.conditioning_width)<1:
            raise ValueError('positive model dimensions required')
        if self.representation not in ('beam','antenna'):
            raise ValueError('representation must be beam or antenna')
        if self.noise_conditioning!='continuous' or self.snr_db_min>=self.snr_db_max:
            raise ValueError('continuous noise range required')


class ChannelResidualBlock(nn.Module):
    def __init__(self, width, conditioning_width, dilation, residual_scale):
        super().__init__()
        self.modulation = nn.Linear(conditioning_width, 2*width)
        self.first = nn.Conv2d(width, width, 3, padding=dilation, dilation=dilation)
        self.second = nn.Conv2d(width, width, 3, padding=1)
        self.residual_scale = residual_scale

    def forward(self, x, condition):
        scale, bias = self.modulation(condition).chunk(2, dim=1)
        h = torch.nn.functional.silu(x*(1+scale[:, :, None, None])+bias[:, :, None, None])
        h = self.first(h)
        h = self.second(torch.nn.functional.silu(h))
        return x+self.residual_scale*h


class ChannelScoreNetwork(nn.Module):
    checkpoint_schema = 'afdm-channel-unit-power-score-v1'

    def __init__(self, config=ChannelScoreConfig(), *, order=1):
        super().__init__()
        if order != 1:
            raise ValueError('Channel network currently implements first-order score only')
        self.config, self.order = config, order
        f = spatial_matrix(config.rows, config.columns)
        self.register_buffer('transform_real', torch.tensor(f.real, dtype=torch.float32), persistent=False)
        self.register_buffer('transform_imag', torch.tensor(f.imag, dtype=torch.float32), persistent=False)
        axis = np.linspace(-1, 1, config.side)
        coordinates = np.stack(np.meshgrid(axis, axis, indexing='ij'))
        self.register_buffer('coordinates', torch.tensor(coordinates, dtype=torch.float32)[None], persistent=False)
        self.input_projection = nn.Conv2d(2*config.antennas, config.width, 1)
        self.coordinate_projection = nn.Conv2d(2, config.width, 1, bias=False)
        self.condition = nn.Sequential(nn.Linear(1, config.conditioning_width), nn.SiLU(),
            nn.Linear(config.conditioning_width, config.conditioning_width), nn.SiLU())
        self.blocks = nn.ModuleList(ChannelResidualBlock(config.width, config.conditioning_width,
            (1, 2, 4)[i % 3], 1/math.sqrt(config.blocks)) for i in range(config.blocks))
        self.output_projection = nn.Conv2d(config.width, 2*config.antennas, 1)
        nn.init.zeros_(self.output_projection.weight)
        nn.init.zeros_(self.output_projection.bias)

    def _check(self, x, v):
        c = self.config
        if x.shape != (len(x), 2, c.antennas, c.side, c.side) or v.shape != (len(x),):
            raise ValueError('Full channel input or variance shape mismatch')
        if not v.is_floating_point() or not bool(torch.all(torch.isfinite(v) & (v > 0))):
            raise ValueError('Finite positive complex variance required')

    def to_representation(self, x):
        if self.config.representation == 'antenna':
            return x
        return packed_transform(x, self.transform_real, self.transform_imag)

    def to_antenna(self, x):
        if self.config.representation == 'antenna':
            return x
        return packed_transform(x, self.transform_real, self.transform_imag, inverse=True)

    def predict_noise(self, observation, variance):
        """Input is already in the configured representation, unit sample power."""
        self._check(observation, variance)
        c = self.config
        x = observation.reshape(len(observation), 2*c.antennas, c.side, c.side)
        x = x/torch.sqrt(1+variance[:, None, None, None])
        x = self.input_projection(x)+self.coordinate_projection(self.coordinates)
        condition = self.condition(torch.log(variance)[:, None]/5)
        for block in self.blocks:
            x = block(x, condition)
        return self.output_projection(torch.nn.functional.silu(x)).reshape_as(observation)

    def score_in_representation(self, observation, variance):
        return -self.predict_noise(observation, variance)/torch.sqrt(variance[:, None, None, None, None]/2)

    def forward(self, observation, variance):
        """The receiver-facing input and output are always antenna-domain scores."""
        return self.to_antenna(self.score_in_representation(self.to_representation(observation), variance))
