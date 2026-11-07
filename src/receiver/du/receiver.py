"""Final inference module: independent scores and activity heads, ten fixed layers.

Numerical methods are taken from the completed run. Training orchestration and
CUDA graph capture remain in that run's immutable reproduction snapshot.
"""
import torch
from torch import nn
from torch.utils.checkpoint import checkpoint
from receiver.du import components as base
from receiver.du.components import damp_gaussian
from receiver.du.configuration import CONFIG
from receiver.du.backbone import make_score
from receiver.du.inputs import pack

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


class Receiver(nn.Module):
    def __init__(self, *, variance_calibration_order='after_positive'):
        super().__init__(); self.layers = nn.ModuleList()
        self.use_checkpoint = True
        self.checkpoint_first_layers = 0
        self.checkpoint_min_users = 0
        self.variance_calibration_order = variance_calibration_order


    def score_call(self, model, x, v):
        values = []
        selected = (self.checkpoint_first_layers > 0 and len(x) >= self.checkpoint_min_users and
                    any(model is layer.score for layer in self.layers[:self.checkpoint_first_layers]))
        recompute = self.use_checkpoint or selected
        for begin in range(0,len(x),CONFIG['receiver']['microbatch']):
            args = (x[begin:begin+CONFIG['receiver']['microbatch']],v[begin:begin+CONFIG['receiver']['microbatch']])
            values.append(checkpoint(model,*args,use_reentrant=False) if recompute and torch.is_grad_enabled() else model(*args))
        return torch.cat(values)

    def add_layer(self, initial_score):
        self.layers.append(Layer(initial_score))


    @property
    def score_evaluations(self):
        return sum(layer.score_evaluations for layer in self.layers)

    def forward(self, public, *, return_messages=False, collect_diagnostics=None):
        if collect_diagnostics is None:
            collect_diagnostics = not self.training or return_messages
        y, a, rho = public['y'], public['a'], public['rho']
        prior = y.new_zeros(public['channel_shape'])
        reference = y.new_tensor(rho * CONFIG['normalized_training_second_moment'])
        variance = reference
        outputs, diagnostic_tensors, messages = [], [], []
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
            outputs.append(dict(estimate=estimate, logits=logits, conditional=conditional))
            if collect_diagnostics:
                diagnostic_tensors.append(torch.stack(
                    (v, raw, post_v, ratio, proposed_variance, variance, amount, analytical_v)).detach())
            if return_messages:
                messages.append(dict(query=r.detach(), next_prior=prior.detach()))
        diagnostics = []
        if diagnostic_tensors:
            names = ('query_variance', 'raw_residual_variance', 'feedback_variance',
                     'feedback_ratio', 'proposed_variance', 'next_variance', 'damping', 'linear_variance')
            for values in torch.stack(diagnostic_tensors).cpu().tolist():
                row = dict(zip(names, values))
                row['out_of_pretraining_support'] = not (
                    CONFIG['complex_variance_support'][0] <= row['query_variance']
                    <= CONFIG['complex_variance_support'][1])
                diagnostics.append(row)
        return (outputs, diagnostics, messages) if return_messages else (outputs, diagnostics)
