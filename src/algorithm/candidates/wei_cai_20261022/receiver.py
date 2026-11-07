"""Independent heads and feedback experiments; the supplied base model is frozen."""
import copy
import math
import torch
from torch import nn
from torch.nn import functional as F
from algorithm.proposed import components as base
from algorithm.proposed.configuration import CONFIG
from algorithm.proposed.inputs import pack


def energy(value):
    """Mean squared magnitude per complex coefficient, from real/imaginary storage."""
    return 2*value.square().flatten(1).mean(1)


def activity_features(head, query, variance, mean, rho):
    x, f = query.flatten(1, 2), mean.flatten(1, 2)
    maps = torch.cat((x, f), dim=1)/torch.sqrt(1+variance)[:, None, None, None]
    scalars = torch.stack((torch.log(variance), torch.log1p(energy(x)/variance),
        torch.log1p(energy(f)/variance), torch.log1p(energy(x-f)/variance),
        torch.full_like(variance, math.log(rho/(1-rho)))), dim=1)
    return torch.cat((head.maps(maps).flatten(1), scalars), dim=1)


class ErrorHead(nn.Module):
    def __init__(self, initial_ratio=0.1):
        super().__init__()
        self.network = nn.Sequential(nn.Linear(69, 32), nn.SiLU(), nn.Linear(32, 1))
        nn.init.zeros_(self.network[-1].weight)
        nn.init.constant_(self.network[-1].bias, math.log(math.expm1(initial_ratio)))

    def forward(self, features, variance):
        return variance*(1e-6+F.softplus(self.network(features.detach())[:, 0]))


class Branches(nn.Module):
    def __init__(self, frozen_model, variant, initial_ratios=None):
        super().__init__()
        if variant not in ('activity', 'joint_error', 'mixture'):
            raise ValueError(variant)
        self.variant = variant
        self.activity = nn.ModuleList([copy.deepcopy(layer.activity) for layer in frozen_model.layers])
        self.activity.requires_grad_(True)
        self.error = nn.ModuleList()
        if variant != 'activity':
            ratios = initial_ratios or [0.1]*len(self.activity)
            self.error.extend(ErrorHead(value) for value in ratios)

    def local(self, index, query, variance, mean, rho):
        nv = variance.expand(len(query))
        head = self.activity[index]
        phi = activity_features(head, query, nv, mean, rho)
        logits = head.head(phi)[:, 0]+math.log(rho/(1-rho))
        probability = torch.sigmoid(logits)
        estimate = probability[:, None, None, None, None]*mean
        scale = self.error[index](phi, nv) if len(self.error) else None
        return dict(query=query, query_variance=variance, conditional=mean, logits=logits,
                    probability=probability, estimate=estimate, error_scale=scale)


class Candidate:
    def __init__(self, frozen_model):
        self.base = frozen_model.eval().requires_grad_(False)

    @staticmethod
    def detach(row):
        return {key: value.detach() if isinstance(value, torch.Tensor) else value for key, value in row.items()}

    def teacher(self, public):
        with torch.no_grad():
            outputs, diagnostics, messages = self.base(public, return_messages=True)
        return [(message['query'], public['y'].new_tensor(diagnostic['query_variance']), output['conditional'])
                for output, diagnostic, message in zip(outputs, diagnostics, messages)]

    def forward(self, public, branches=None, update=None):
        y, a, rho = public['y'], public['a'], public['rho']
        prior = y.new_zeros(public['channel_shape'])
        reference = y.new_tensor(rho*CONFIG['normalized_training_second_moment'])
        variance = reference
        rows = []
        for index, layer in enumerate(self.base.layers):
            with torch.no_grad():
                query, v, _ = base.linear_query(public, prior, variance, layer.c_gamma)
                conditional = query+torch.exp(layer.c_alpha)*v/2*self.base.score_call(
                    layer.score, query, v.expand(len(query)))
            with torch.set_grad_enabled(update is not None):
                if branches is None:
                    logits = layer.activity(query, v.expand(len(query)), conditional, rho)
                    probability = torch.sigmoid(logits)
                    row = dict(query=query, query_variance=v, conditional=conditional, logits=logits,
                        probability=probability, estimate=probability[:, None, None, None, None]*conditional,
                        error_scale=None)
                else:
                    row = branches.local(index, query, v, conditional, rho)
            if update is not None:
                update(index, row)
            row = self.detach(row)
            with torch.no_grad():
                residual = y-a@pack(row['estimate'])
                frames, columns = y.shape[0]//2, y.shape[1]
                residual_scale = (residual.square().sum()-frames*columns*public['noise'])/(columns*a.square().sum()/2)
                if branches is None or branches.variant == 'activity':
                    raw = residual_scale
                elif branches.variant == 'joint_error':
                    raw = row['error_scale'].mean()
                else:
                    p = row['probability']
                    raw = (p*row['error_scale']+p*(1-p)*energy(conditional)).mean()
                post_v, ratio = base.feedback_variance(raw, v, layer.c_beta,
                                                       order=self.base.variance_calibration_order)
                next_mean = (row['estimate']-ratio*query)/(1-ratio)
                next_variance = post_v/(1-ratio)
                prior, variance, damping = base.damp_gaussian(prior, variance, next_mean, next_variance, reference)
                row.update(raw_scale=raw, feedback_scale=post_v, residual_scale=residual_scale,
                           feedback_ratio=ratio, damping=damping)
            rows.append(row)
        return rows


class LocalTrainer:
    """Independent per-layer objectives; no gradient through trajectories or score."""
    def __init__(self, branches, mean_users, mean_active, activity_lr=1e-5, error_lr=1e-3):
        self.branches = branches
        self.mean_users, self.mean_active = mean_users, mean_active
        self.optimizers = []
        for index, head in enumerate(branches.activity):
            groups = [dict(params=head.parameters(), lr=activity_lr)]
            if len(branches.error):
                groups.append(dict(params=branches.error[index].parameters(), lr=error_lr))
            self.optimizers.append(torch.optim.Adam(groups, betas=(.9, .999), eps=1e-8))

    def update(self, index, row, truth, active):
        optimizer = self.optimizers[index]
        optimizer.zero_grad(set_to_none=True)
        activity_loss = F.binary_cross_entropy_with_logits(row['logits'], active, reduction='sum')/self.mean_users
        loss = activity_loss
        variance_loss = activity_loss.detach()*0
        if len(self.branches.error):
            if self.branches.variant == 'joint_error':
                target = energy(truth-row['estimate'].detach())
                loss_values = torch.log(row['error_scale'])+target/row['error_scale']
                variance_loss = loss_values.sum()/self.mean_users
            else:
                mask = active.bool()
                target = energy(truth-row['conditional'].detach())
                loss_values = torch.log(row['error_scale'][mask])+target[mask]/row['error_scale'][mask]
                variance_loss = loss_values.sum()/self.mean_active
            loss = loss+variance_loss
        if not torch.isfinite(loss):
            raise FloatingPointError('Nonfinite local training loss; retain failure')
        loss.backward()
        activity_norm = torch.nn.utils.clip_grad_norm_(self.branches.activity[index].parameters(), 1.0, error_if_nonfinite=True)
        if len(self.branches.error):
            torch.nn.utils.clip_grad_norm_(self.branches.error[index].parameters(), 1.0, error_if_nonfinite=True)
        optimizer.step()
        return dict(activity_loss=float(activity_loss.detach()), error_loss=float(variance_loss.detach()),
                    activity_gradient_norm=float(activity_norm))
