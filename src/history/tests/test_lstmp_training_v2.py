"""Scientific loss, gradient-routing and optimizer-state regressions for v2."""
import copy
import io
import math
import random
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from experiments.lstmp_training_v2_20261020.objectives import (
    layer_terms, loss_components, assign_gradients, selected_epoch)
from experiments.lstmp_training_v2_20261020.optimization import (
    eligible_parameters, make_optimizer, set_phase, rng_state, restore_rng)


def test_true_activity_mask_and_fixed_denominators():
    mean = torch.tensor([[3., 5.], [1e4, -2e4]], requires_grad=True)
    logits = torch.tensor([-20., 3.], requires_grad=True)
    labels = dict(x=torch.tensor([[1., 2.], [0., 0.]]), active=torch.tensor([1., 0.]))
    stats = dict(mean_scene_energy=17., mean_users_per_scene=53.333333333333336)
    output = dict(conditional=mean, logits=logits)
    h, a = layer_terms(output, labels, stats)
    torch.testing.assert_close(h, torch.tensor(13. / 17.))
    torch.testing.assert_close(a, F.binary_cross_entropy_with_logits(
        logits, labels['active'], reduction='sum') / stats['mean_users_per_scene'])
    h.backward()
    torch.testing.assert_close(mean.grad[0], torch.tensor([4., 6.]) / 17.)
    assert torch.equal(mean.grad[1], torch.zeros(2))
    assert logits.grad is None  # Low probability must not suppress conditional supervision.


def test_scene_sampling_matches_finite_dataset_risk():
    stats = dict(mean_scene_energy=11., mean_users_per_scene=3.)
    losses = []
    raw_h, raw_a = 0., 0.
    for users in (2, 4):
        active = torch.arange(users).remainder(2).float()
        truth = active[:, None] * torch.tensor([[3., 4.]])
        mean = torch.arange(users * 2).reshape(users, 2).float()
        logits = torch.linspace(-1., 1., users)
        h, a = layer_terms(dict(conditional=mean, logits=logits),
                           dict(x=truth, active=active), stats)
        losses.append(h + a)
        raw_h += ((mean - truth).square() * active[:, None]).sum()
        raw_a += F.binary_cross_entropy_with_logits(logits, active, reduction='sum')
    torch.testing.assert_close(torch.stack(losses).mean(), raw_h / 22. + raw_a / 6.)


def test_all_earlier_layers_have_point_two_weight_and_selection_uses_final():
    outputs = [dict(conditional=torch.tensor([[float(i)]]), logits=torch.tensor([0.]))
               for i in range(1, 8)]
    labels = dict(x=torch.zeros(1, 1), active=torch.ones(1))
    result = loss_components(outputs, labels, dict(mean_scene_energy=1., mean_users_per_scene=1.))
    expected_h = (.2 * sum(i * i for i in range(1, 7)) + 49.) / 2.2
    torch.testing.assert_close(result['channel'], torch.tensor(expected_h))
    torch.testing.assert_close(result['selection'], torch.tensor(49.) + torch.log(torch.tensor(2.)))
    assert selected_epoch([dict(epoch=0, selection_loss=1., aer=.8),
                           dict(epoch=1, selection_loss=2., aer=.1)]) == 0
    assert selected_epoch([dict(epoch=0, selection_loss=1.),
                           dict(epoch=1, selection_loss=1.)]) == 0


class TinyLayer(nn.Module):
    def __init__(self):
        super().__init__()
        self.score = nn.Linear(1, 1)
        self.activity = nn.Linear(1, 1)
        self.c_gamma = nn.Parameter(torch.tensor(.2))
        self.c_alpha = nn.Parameter(torch.tensor(.1))
        self.c_beta = nn.Parameter(torch.tensor(.3))


class TinyReceiver(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.ModuleList([TinyLayer(), TinyLayer()])

    def forward(self):
        query = torch.ones(1, 1)
        outputs = []
        for layer in self.layers:
            mean = layer.score(query) + layer.c_alpha + layer.c_gamma * query
            logit = layer.activity(mean).flatten()
            estimate = torch.sigmoid(logit).reshape(1, 1) * mean
            outputs.append(dict(conditional=mean, logits=logit, estimate=estimate))
            query = estimate + layer.c_beta
        return outputs


SETTINGS = dict(learning_rate=2e-5, activity_learning_rate=1e-4, calibration_learning_rate=1e-3)
STATS = dict(mean_scene_energy=1., mean_users_per_scene=1.)
LABELS = dict(x=torch.tensor([[1.]]), active=torch.ones(1))


def tiny_step(model, optimizer):
    optimizer.zero_grad(set_to_none=True)
    loss_components(model(), LABELS, STATS)['total'].backward()
    optimizer.step()


def test_independent_calibration_steps_and_phase_state():
    model = TinyReceiver()
    eligible = eligible_parameters(model)
    optimizer = make_optimizer(model, SETTINGS, eligible)
    before = copy.deepcopy(model.state_dict())
    set_phase(model, optimizer, eligible, 1)
    tiny_step(model, optimizer)
    for name, value in model.state_dict().items():
        if name.startswith('layers.0.') and name != 'layers.0.c_beta':
            assert torch.equal(value, before[name])
    first, last = model.layers
    assert first.c_gamma not in optimizer.state
    assert last.c_beta not in optimizer.state
    assert optimizer.state[first.c_beta]['step'] == 1
    beta_moment = optimizer.state[first.c_beta]['exp_avg'].clone()
    set_phase(model, optimizer, eligible, 2)
    assert torch.equal(optimizer.state[first.c_beta]['exp_avg'], beta_moment)
    assert all(math.isclose(group['lr'], expected, rel_tol=1e-15)
               for group, expected in zip(optimizer.param_groups, (2e-6, 1e-5, 1e-4)))
    tiny_step(model, optimizer)
    assert optimizer.state[first.c_gamma]['step'] == 1
    assert optimizer.state[first.c_beta]['step'] == 2
    assert last.c_beta not in optimizer.state and not last.c_beta.requires_grad
    assert first.c_gamma.data_ptr() != first.c_beta.data_ptr()


def test_gradient_control_excludes_all_score_bce_paths_only():
    torch.manual_seed(73)
    model = TinyReceiver()
    components = loss_components(model(), LABELS, STATS)
    named = list(model.named_parameters())
    parameters = [p for _, p in named]
    gh = torch.autograd.grad(components['channel'], parameters, retain_graph=True, allow_unused=True)
    ga = torch.autograd.grad(components['activity'], parameters, retain_graph=True, allow_unused=True)
    assert any(float(g.abs().sum()) > 0 for (n, _), g in zip(named, ga)
               if n.startswith('layers.0.score') and g is not None)
    assign_gradients(model, components, bce_updates_score=False)
    for (name, p), h, a in zip(named, gh, ga):
        expected = h if '.score.' in name else (
            a if h is None else h if a is None else h + a)
        if expected is None:
            assert p.grad is None
        else:
            torch.testing.assert_close(p.grad, expected)


def test_checkpoint_restores_adam_rng_and_next_update():
    torch.manual_seed(27)
    model = TinyReceiver()
    eligible = eligible_parameters(model)
    optimizer = make_optimizer(model, SETTINGS, eligible)
    set_phase(model, optimizer, eligible, 1)
    tiny_step(model, optimizer)
    set_phase(model, optimizer, eligible, 2)
    buffer = io.BytesIO()
    torch.save(dict(model=model.state_dict(), optimizer=optimizer.state_dict(), rng=rng_state(),
                    order=np.array([4, 1, 2, 0, 3]), cursor=2), buffer)
    expected_random = (random.random(), np.random.rand(), torch.rand(2))
    tiny_step(model, optimizer)
    expected_state = copy.deepcopy(model.state_dict())
    expected_optimizer = copy.deepcopy(optimizer.state_dict())
    buffer.seek(0)
    saved = torch.load(buffer, weights_only=False)
    model.load_state_dict(saved['model'])
    optimizer.load_state_dict(saved['optimizer'])
    restore_rng(saved['rng'])
    assert random.random() == expected_random[0]
    assert np.random.rand() == expected_random[1]
    assert torch.equal(torch.rand(2), expected_random[2])
    assert saved['order'][saved['cursor']:].tolist() == [2, 0, 3]
    tiny_step(model, optimizer)
    for name, value in model.state_dict().items():
        assert torch.equal(value, expected_state[name])
    for index, state in optimizer.state_dict()['state'].items():
        for key, value in state.items():
            assert torch.equal(value, expected_optimizer['state'][index][key])
