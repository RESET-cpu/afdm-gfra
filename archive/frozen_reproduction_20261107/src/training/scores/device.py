"""Device random streams for resumable CPU, MPS and CUDA training."""
import torch


def capture_device_rng(device):
    kind = torch.device(device).type
    return dict(
        mps_rng=torch.mps.get_rng_state().cpu() if kind == 'mps' else None,
        cuda_rng=torch.cuda.get_rng_state_all() if kind == 'cuda' else None,
    )


def restore_device_rng(device, state):
    kind = torch.device(device).type
    for name in ('mps', 'cuda'):
        saved = state.get(name + '_rng')
        if (saved is not None) != (kind == name):
            raise ValueError('Resume on the original device to preserve the random stream')
        if saved is not None:
            if name == 'mps':
                torch.mps.set_rng_state(saved)
            else:
                if len(saved) != torch.cuda.device_count():
                    raise ValueError('CUDA device count changed since checkpoint')
                torch.cuda.set_rng_state_all(saved)
