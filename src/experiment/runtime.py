"""Evaluation adapters; the frozen receiver equations and weights are unchanged."""
import torch


def known_noise_baseline(method, *, config=None, device='cpu'):
    """Use the existing supplied-noise solver without its noise-estimation frontend."""
    from receiver.baseline._base import EstimatedNoiseBaselineReceiver
    return EstimatedNoiseBaselineReceiver(method, config=config, device=device).base


def synchronize(device):
    if device == 'cuda':
        torch.cuda.synchronize()


def setup(device):
    if device == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    if device == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('CUDA is unavailable')
    torch.set_num_threads(4)
    if torch.get_num_interop_threads() != 1:
        torch.set_num_interop_threads(1)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    return device

def network_modules(model):
    return _modules(model, 'device_modules')


def _modules(model, key):
    modules = []
    for path in model._experiment_spec.get(key, []):
        value = model
        for part in path.split('.'):
            value = getattr(value, part)
        if not isinstance(value, torch.nn.Module):
            raise TypeError('Configured network is not a torch module: '+path)
        modules.append(value)
    return modules


def backend(model, device):
    return device if model._experiment_spec['backend'] == 'device' else 'cpu'


def activate(models, selected, device):
    """Only the measured receiver occupies CUDA memory; loading is outside timing."""
    for name, model in models.items():
        if name != selected:
            release = getattr(model, 'release_runtime_cache', None)
            if release is not None:
                release()
        for module in network_modules(model):
            module.to(backend(model, device) if name == selected else 'cpu')
    if device == 'cuda':
        torch.cuda.empty_cache()


def parameter_count(model):
    modules = _modules(model, 'parameter_modules') if 'parameter_modules' in model._experiment_spec else network_modules(model)
    return sum(p.numel() for module in modules for p in module.parameters())
