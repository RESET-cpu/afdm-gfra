"""The accepted damped receiver, with graph-connected conditional outputs.

The preparation script freezes the historical implementation beside this
package. Its linear update, activity head and variance map are reused verbatim.
"""
import torch
from torch import nn
from experiments.lstmp_candidate_20261019 import receiver as base
from experiments.lstmp_candidate_20261019.backbone import make_score
from experiments.lstmp_candidate_20261019.common import CONFIG
from experiments.lstmp_candidate_20261019.data import pack
from experiments.lstmp_candidate_20261019.message_damping import damp_gaussian


class Layer(nn.Module):
    def __init__(self, initial_score):
        super().__init__()
        self.score = make_score()
        if initial_score is not None:
            self.score.load_state_dict(initial_score, strict=True)
        self.activity = base.ActivityHead()
        self.c_gamma = nn.Parameter(torch.zeros(()))
        self.c_alpha = nn.Parameter(torch.zeros(()))
        self.c_beta = nn.Parameter(torch.zeros(()))
        self.score_evaluations = 0
        self.score.register_forward_pre_hook(self._count_score_evaluation)

    def _count_score_evaluation(self, module, inputs):
        # Includes activation-checkpoint recomputation, even with early stopping.
        self.score_evaluations += 1

    @property
    def calibration(self):
        return torch.stack((self.c_gamma, self.c_alpha, self.c_beta))


class Receiver(base.Receiver):
    def add_layer(self, initial_score):
        self.layers.append(Layer(initial_score))

    @property
    def score_evaluations(self):
        return sum(layer.score_evaluations for layer in self.layers)

    def forward(self, public, *, return_messages=False):
        y, a, rho = public['y'], public['a'], public['rho']
        prior = y.new_zeros(public['channel_shape'])
        reference = y.new_tensor(rho * CONFIG['normalized_training_second_moment'])
        variance = reference
        outputs, diagnostics, messages = [], [], []
        for layer in self.layers:
            r, v, analytical_v = base.linear_query(public, prior, variance, layer.c_gamma)
            nv = v.expand(len(r))
            conditional = r + torch.exp(layer.c_alpha) * v / 2 * self.score_call(layer.score, r, nv)
            logits = layer.activity(r, nv, conditional, rho)
            probability = torch.sigmoid(logits)
            estimate = probability[:, None, None, None, None] * conditional
            residual = y - a @ pack(estimate)
            frames, columns = y.shape[0] // 2, y.shape[1]
            raw = (residual.square().sum() - frames * columns * public['noise']) / (
                columns * a.square().sum() / 2)
            post_v, ratio = base.feedback_variance(raw, v, layer.c_beta,
                                                   order=self.variance_calibration_order)
            proposed_mean = (estimate - ratio * r) / (1 - ratio)
            proposed_variance = post_v / (1 - ratio)
            prior, variance, amount = damp_gaussian(
                prior, variance, proposed_mean, proposed_variance, reference)
            # Conditional output must retain its graph for T8 and T9.
            outputs.append(dict(estimate=estimate, logits=logits, conditional=conditional))
            diagnostics.append(dict(query_variance=float(v.detach()),
                raw_residual_variance=float(raw.detach()), feedback_variance=float(post_v.detach()),
                feedback_ratio=float(ratio.detach()), proposed_variance=float(proposed_variance.detach()),
                next_variance=float(variance.detach()), damping=float(amount.detach()),
                linear_variance=float(analytical_v.detach()),
                out_of_pretraining_support=not (
                    CONFIG['complex_variance_support'][0] <= float(v.detach()) <=
                    CONFIG['complex_variance_support'][1])))
            if return_messages:
                messages.append(dict(query=r.detach(), next_prior=prior.detach()))
        return (outputs, diagnostics, messages) if return_messages else (outputs, diagnostics)
