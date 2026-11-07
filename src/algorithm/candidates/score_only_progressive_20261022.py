"""Fresh progressive score training with the original shared STMP evidence net.

Wei--Yuan, arXiv:2610.17785v1, III-D supplies the progressive joint schedule.
The multiuser conditional objective and frozen classifier are project choices.
No parameter is read from the previously trained ten-layer checkpoint.
"""
import math
import torch

from algorithm.STMP.activity import Config, EvidenceNetwork
from algorithm.proposed.receiver import Receiver as FrozenEquations, Layer


class FixedEvidence(EvidenceNetwork):
    """Identical evidence features, with derivatives through the score mean."""

    def __init__(self, blob):
        super().__init__(Config(**blob['config']))
        self.load_state_dict(blob['state_dict'], strict=True)
        self.requires_grad_(False)
        self.eval()
        self.training_prior = float(blob['training_class_prior'])

    def inputs(self, observation, variance, mean):
        expected = (len(observation), 2, self.config.antennas,
                    self.config.side, self.config.side)
        if (observation.shape != expected or mean.shape != expected
                or variance.shape != (len(observation),)):
            raise ValueError('Matching full observations, means and variances required')
        if not bool(torch.all(torch.isfinite(variance) & (variance > 0))):
            raise ValueError('Positive finite complex variances required')
        # This is the sole feature change from EvidenceNetwork: no mean.detach().
        f = mean if self.config.use_score_mean else torch.zeros_like(mean)
        x = observation.reshape(len(observation), 2*self.config.antennas,
                                self.config.side, self.config.side)
        f = f.reshape_as(x)
        factor = torch.sqrt(2/(1+variance))[:, None, None, None]
        maps = torch.cat((factor*x, factor*f), dim=1)
        rx = 2*x.square().flatten(1).mean(1)/variance
        ff = 2*f.square().flatten(1).mean(1)/variance
        rf = 2*(x*f).flatten(1).mean(1)/variance
        residual = 2*(x-f).square().flatten(1).mean(1)/variance
        scalar = torch.stack((torch.log(variance)/5, torch.log1p(rx),
            torch.log1p(ff), torch.sign(rf)*torch.log1p(abs(rf)),
            torch.log1p(residual)), dim=1)
        return maps, scalar

    def forward(self, observation, variance, mean, rho):
        evidence = super().forward(observation, variance, mean)
        return (evidence - math.log(self.training_prior/(1-self.training_prior))
                + math.log(rho/(1-rho)))


class Receiver(FrozenEquations):
    def __init__(self, evidence_blob):
        super().__init__(variance_calibration_order='after_positive')
        self.evidence = FixedEvidence(evidence_blob)

    def add_layer(self, pretrained_state):
        layer = Layer(pretrained_state)
        layer.activity = self.evidence
        layer.requires_grad_(False)
        layer.score.requires_grad_(True)
        self.layers.append(layer)

    def train(self, mode=True):
        super().train(mode)
        self.evidence.eval()
        return self


def conditional_loss(outputs, truth, activity):
    """Scene-normalized active conditional error; no probability/BCE weighting."""
    mask = activity[:, None, None, None, None]
    denominator = (truth.square()*mask).sum()
    if not bool(torch.isfinite(denominator) & (denominator > 0)):
        raise ValueError('A nonempty active scene with positive energy is required')
    terms = [((row['conditional']-truth).square()*mask).sum()/denominator
             for row in outputs]
    # Auxiliary outputs are supervised during training, never separately tested.
    weights = [.2]*(len(terms)-1)+[1.]
    return sum(weight*term for weight, term in zip(weights, terms)), terms
