"""Same-prior activity evidence with full r and its frozen score mean."""

from dataclasses import dataclass
import numpy as np
import torch
from torch import nn


@dataclass(frozen=True)
class PriorSummary:
    mean: np.ndarray
    second_moment: float
    moments_exact: bool = False

    def __post_init__(self):
        if (
            not np.isfinite(self.mean).all()
            or not np.isfinite(self.second_moment)
            or self.second_moment <= 0
            or np.vdot(self.mean, self.mean).real > self.second_moment * (1 + 1e-12)
        ):
            raise ValueError("Consistent finite prior mean and positive second moment required")


SCHEMA = "afdm-score-mp-evidence-score-input-v1"
FEATURE_DEFINITION = "complete_r_and_same_query_old_full_mean; common_RMS; complex_v; maps_sqrt_2_over_1plusv; five_scalars_v1"
FEATURE_DEFINITION_FROZEN = "complete_r_and_same_query_frozen_full_mean; common_RMS; complex_v; maps_sqrt_2_over_1plusv; five_scalars_v1"


@dataclass(frozen=True)
class Config:
    antennas: int = 16
    side: int = 16
    width: int = 64
    use_score_mean: bool = True


class EvidenceNetwork(nn.Module):
    def __init__(self, config=Config()):
        super().__init__()
        self.config = config
        self.condition = nn.Sequential(nn.Linear(1, 64), nn.SiLU())
        self.blocks, self.biases = nn.ModuleList(), nn.ModuleList()
        channels = 4 * config.antennas
        for i, width in enumerate((config.width, 2 * config.width, 2 * config.width)):
            self.blocks.append(
                nn.Sequential(
                    nn.Conv2d(channels, width, 3, stride=1 if i == 0 else 2, padding=1),
                    nn.SiLU(),
                    nn.Conv2d(width, width, 3, padding=1),
                    nn.SiLU(),
                )
            )
            self.biases.append(nn.Linear(64, width))
            channels = width
        side = (config.side + 3) // 4
        self.readout = nn.Sequential(
            nn.Linear(channels * side * side + 5, 128), nn.SiLU(), nn.Linear(128, 1)
        )
        nn.init.zeros_(self.readout[-1].weight)
        nn.init.zeros_(self.readout[-1].bias)

    def inputs(self, observation, variance, mean):
        expected = (len(observation), 2, self.config.antennas, self.config.side, self.config.side)
        if (
            observation.shape != expected
            or mean.shape != expected
            or variance.shape != (len(observation),)
        ):
            raise ValueError(
                "Matching full observations, score means, and scalar variances required"
            )
        if not bool(torch.all(torch.isfinite(variance) & (variance > 0))):
            raise ValueError("Positive finite complex variances required")
        # Features never update the frozen score; both classes use this same operation.
        f = mean.detach() if self.config.use_score_mean else torch.zeros_like(mean)
        x = observation.reshape(
            len(observation), 2 * self.config.antennas, self.config.side, self.config.side
        )
        f = f.reshape_as(x)
        factor = torch.sqrt(2 / (1 + variance))[:, None, None, None]
        maps = torch.cat((factor * x, factor * f), dim=1)
        # Two times the average over real coordinates is squared complex norm / D.
        rx = 2 * x.square().flatten(1).mean(1) / variance
        ff = 2 * f.square().flatten(1).mean(1) / variance
        rf = 2 * (x * f).flatten(1).mean(1) / variance
        residual = 2 * (x - f).square().flatten(1).mean(1) / variance
        lv = torch.log(variance) / 5
        scalar = torch.stack(
            (
                lv,
                torch.log1p(rx),
                torch.log1p(ff),
                torch.sign(rf) * torch.log1p(abs(rf)),
                torch.log1p(residual),
            ),
            dim=1,
        )
        return maps, scalar

    def forward(self, observation, variance, mean):
        x, scalar = self.inputs(observation, variance, mean)
        condition = self.condition(scalar[:, :1])
        for block, bias in zip(self.blocks, self.biases):
            x = block(x) + bias(condition)[:, :, None, None]
        return self.readout(torch.cat((x.flatten(1), scalar), dim=1))[:, 0]


class FrozenEvidence:
    def __init__(self, path, *, device="mps"):
        blob = torch.load(path, map_location="cpu", weights_only=False)
        if (
            blob.get("schema") != SCHEMA
            or blob["training_class_prior"] != 0.5
            or blob.get("feature_definition") not in (FEATURE_DEFINITION, FEATURE_DEFINITION_FROZEN)
        ):
            raise ValueError("Dedicated balanced same-prior evidence checkpoint required")
        self.network = EvidenceNetwork(Config(**blob["config"]))
        self.network.load_state_dict(blob["state_dict"])
        self.network.to(device).eval().requires_grad_(False)
        self.device, self.scale = device, float(blob["scale"])
        self.prior_definition = blob["prior_definition"]
        if self.prior_definition["global_complex_rms"] != self.scale:
            raise ValueError("Feature scale and target prior scale differ")
        self.prior = PriorSummary(
            np.asarray(blob["prior_mean"], complex), float(blob["prior_second_moment"])
        )
        self.noise_support, self.training_class_prior = tuple(blob["noise_support"]), 0.5
        self.first_sha256, self.second_sha256 = blob["first_sha256"], blob["second_sha256"]

    def infer(self, observation, variance, mean):
        r, v, f = (
            np.asarray(observation, complex),
            np.asarray(variance, float),
            np.asarray(mean, complex),
        )
        if (
            v.shape != (len(r),)
            or f.shape != r.shape
            or not all(np.isfinite(a).all() for a in (r, v, f))
            or np.any(v < self.noise_support[0])
            or np.any(v > self.noise_support[1])
        ):
            raise ValueError("Supported finite query and same-query score mean required")
        with torch.inference_mode():
            x = torch.tensor(
                np.stack((r.real, r.imag), axis=1), dtype=torch.float32, device=self.device
            )
            m = torch.tensor(
                np.stack((f.real, f.imag), axis=1), dtype=torch.float32, device=self.device
            )
            nv = torch.tensor(v, dtype=torch.float32, device=self.device)
            return self.network(x, nv, m).cpu().numpy().astype(float)
