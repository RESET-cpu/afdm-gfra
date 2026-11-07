"""Protect accelerator random streams across training checkpoint resume."""
from copy import deepcopy
import pytest
import torch
from afdm_jadcedd.experiment.training.scores.device import capture_device_rng, restore_device_rng


def test_legacy_cpu_checkpoint_and_cross_device_rejection():
    restore_device_rng('cpu', {'mps_rng': None})
    with pytest.raises(ValueError, match='original device'):
        restore_device_rng('cuda', {'mps_rng': None})
    with pytest.raises(ValueError, match='original device'):
        restore_device_rng('cpu', {'mps_rng': None, 'cuda_rng': [torch.zeros(1)]})


@pytest.mark.skipif(not torch.cuda.is_available(), reason='CUDA device required')
def test_cuda_optimizer_and_random_stream_resume():
    torch.manual_seed(173)
    model = torch.nn.Sequential(torch.nn.Linear(8, 8), torch.nn.Dropout(.3)).cuda()
    optimizer = torch.optim.Adam(model.parameters(), lr=.001)

    def step():
        optimizer.zero_grad(set_to_none=True)
        loss = model(torch.randn(4, 8, device='cuda')).square().mean()
        loss.backward()
        optimizer.step()
        return loss.detach().cpu().clone()

    step()
    saved_model = deepcopy(model.state_dict())
    saved_optimizer = deepcopy(optimizer.state_dict())
    random_state = capture_device_rng('cuda')
    expected_loss = step()
    expected_model = deepcopy(model.state_dict())
    model.load_state_dict(saved_model)
    optimizer.load_state_dict(saved_optimizer)
    restore_device_rng('cuda', random_state)
    assert torch.equal(step(), expected_loss)
    assert all(torch.equal(value, expected_model[key]) for key, value in model.state_dict().items())
