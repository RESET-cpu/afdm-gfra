"""Keep the original balanced queries; replace only the frozen mean teacher."""
import torch
from torch.nn import functional as F

from training.colored_score_20261024.noise import Covariance
from training.colored_preconditioned_20261024.operators import Spectral
from training.scores.cuda_graph_auxiliary import AuxiliaryGraph, activity_forward


def conditional_mean(first, observation, variance):
    # This is the C=vI conditional-mean call in algorithm.C_STMP.moments.
    identity = torch.eye(16, dtype=torch.complex64, device=observation.device).expand(len(observation), -1, -1)
    covariance = Covariance(variance, identity, identity)
    spectral = Spectral(identity, identity, (variance[:, None, None]/2).expand(-1, 16, 16))
    return first(observation, covariance, spectral)


class ActivityGraph(AuxiliaryGraph):
    def losses_backward(self, parts):
        total = sum(len(p[0]) for p in parts)
        losses = []
        for r, v in parts:
            with torch.no_grad():
                mean = conditional_mean(self.first, r, v)
            labels = torch.cat((torch.ones(len(r)//2, device=r.device),
                                torch.zeros(len(r)//2, device=r.device)))
            loss = F.binary_cross_entropy_with_logits(activity_forward(self.model, r, v, mean), labels)
            (loss*len(r)/total).backward()
            losses.append(loss.detach())
        return torch.stack(losses)
