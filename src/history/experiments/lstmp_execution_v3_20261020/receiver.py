"""Same receiver equations; fewer host synchronizations and reusable CUDA work."""
from contextlib import contextmanager

import torch

from experiments.lstmp_training_v2_20261020.receiver import Receiver as ReferenceReceiver
from experiments.lstmp_training_v2_20261020.receiver import base, CONFIG, pack, damp_gaussian


class Receiver(ReferenceReceiver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graphs_enabled = False
        self.graphs = {}
        self.graph_replays = 0
        self.graph_capture_count = 0

    def clear_graphs(self):
        for index, entry in self.graphs.items():
            self.layers[index].score.network.forward = entry['original']
        self.graphs.clear()

    @contextmanager
    def eager(self):
        enabled = self.graphs_enabled
        self.graphs_enabled = False
        try:
            yield
        finally:
            self.graphs_enabled = enabled

    def score_call(self, model, x, v):
        settings = CONFIG.get('execution_acceleration', {})
        shallow_limit = settings.get('graph_all_layers_through_depth', 5)
        limit = len(self.layers) if len(self.layers) <= shallow_limit else settings.get('graph_deep_layers', 3)
        users = settings.get('graph_users', 40)
        index = next(i for i, layer in enumerate(self.layers) if layer.score is model)
        if (self.graphs_enabled and self.training and torch.is_grad_enabled()
                and len(x) == users and index < limit):
            flags = (x.requires_grad, v.requires_grad)
            if index not in self.graphs:
                network = model.network
                original = network.forward
                sample_x = x.detach().reshape(users, 32, 16, 16).clone().requires_grad_(flags[0])
                sample_v = v.detach().clone().requires_grad_(flags[1])
                torch.cuda.make_graphed_callables(
                    network, (sample_x, sample_v), num_warmup_iters=3, allow_unused_input=True)
                graphed = network.forward

                def dispatch(a, b, original=original, graphed=graphed, flags=flags):
                    if (self.graphs_enabled and self.training and torch.is_grad_enabled()
                            and len(a) == users and (a.requires_grad, b.requires_grad) == flags):
                        self.graph_replays += 1
                        return graphed(a, b)
                    return original(a, b)

                network.forward = dispatch
                self.graphs[index] = dict(original=original, flags=flags)
                self.graph_capture_count += 1
            if self.graphs[index]['flags'] != flags:
                raise RuntimeError('Training phase changed without clearing captured graphs')
            # Captured forward/backward retains its own intermediates. Other
            # shapes/layers still use the frozen activation-checkpoint rule.
            return model(x, v)
        return super().score_call(model, x, v)

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
