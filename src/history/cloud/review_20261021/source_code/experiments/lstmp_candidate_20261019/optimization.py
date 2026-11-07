"""Gradient clipping with a stable reduction for very large finite gradients."""
import torch


@torch.no_grad()
def clip_gradient_norm(parameters, maximum=1.):
    parameters=list(parameters)
    try:
        return torch.nn.utils.clip_grad_norm_(parameters,maximum,error_if_nonfinite=True)
    except RuntimeError:
        gradients=[p.grad for p in parameters if p.grad is not None]
        # Float32 squared-norm reduction can overflow even when every gradient
        # is finite. Change only reduction precision, not the clipping threshold.
        norm=torch.stack([torch.linalg.vector_norm(g,ord=2,dtype=torch.float64) for g in gradients]).norm()
        if not bool(torch.isfinite(norm)):
            raise FloatingPointError('Nonfinite gradient; optimizer update rejected')
        coefficient=(maximum/(norm+1e-6)).clamp(max=1.)
        for gradient in gradients:gradient.mul_(coefficient.to(gradient.dtype))
        return norm
