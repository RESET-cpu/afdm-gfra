"""Reuse the first candidate's noise family and checked CUDA graph convention."""
import numpy as np
import torch

from training.colored_score_20261024.noise import Covariance
from training.colored_preconditioned_20261024.operators import Spectral
from training.colored_preconditioned_20261024.formal_batches import draw_arrays, validate_arrays
from .model import trace_loss


def context(tensors):
    return Covariance(tensors[2], tensors[3], tensors[4]), Spectral(*tensors[8:])


def loss_unchecked(second, first, tensors):
    covariance, spectral = context(tensors)
    with torch.no_grad():
        mean = first(tensors[1], covariance, spectral)
    output = second(tensors[1], covariance, spectral)
    return trace_loss(output, mean, tensors[0], spectral)


def batches(bank, chosen, rng, shape_rng, cfg):
    draw = cfg['second']['microbatch_size']
    parts = [draw_arrays(np.asarray(bank[chosen[i:i+draw]]), rng, shape_rng,
                        cfg['scale'], cfg['noise']) for i in range(0, len(chosen), draw)]
    return tuple(np.concatenate([p[j] for p in parts], axis=0) for j in range(len(parts[0])))


class BatchGraph:
    def __init__(self, second, first, batch_size=64):
        if first.training or any(p.requires_grad for p in first.parameters()):
            raise ValueError('First teacher must be eval and completely frozen')
        self.second, self.first, self.batch_size = second, first, batch_size
        self.device = next(second.parameters()).device
        self.graph = None

    def backward(self, arrays, *, use_graph=True):
        validate_arrays(self.second, arrays)
        if not use_graph or len(arrays[0]) != self.batch_size or self.device.type != 'cuda':
            tensors = [torch.as_tensor(a, device=self.device) for a in arrays]
            loss = loss_unchecked(self.second, self.first, tensors)
            loss.backward()
        else:
            if self.graph is None:
                self.inputs = [torch.as_tensor(a, device=self.device).clone() for a in arrays]
                stream = torch.cuda.Stream(device=self.device)
                stream.wait_stream(torch.cuda.current_stream(self.device))
                with torch.cuda.stream(stream):
                    for _ in range(3):
                        self.second.zero_grad(set_to_none=True)
                        loss_unchecked(self.second, self.first, self.inputs).backward()
                torch.cuda.current_stream(self.device).wait_stream(stream)
                self.second.zero_grad(set_to_none=True)
                self.graph = torch.cuda.CUDAGraph()
                with torch.cuda.graph(self.graph, stream=stream):
                    self.loss = loss_unchecked(self.second, self.first, self.inputs)
                    self.loss.backward()
                self.gradients = [p.grad for p in self.second.parameters()]
            for destination, source in zip(self.inputs, arrays):
                destination.copy_(torch.from_numpy(source))
            self.graph.replay()
            for parameter, gradient in zip(self.second.parameters(), self.gradients):
                parameter.grad = gradient
            loss = self.loss
        value = float(loss.detach().cpu())
        if not np.isfinite(value):
            raise FloatingPointError('Nonfinite second-score trace loss')
        if any(p.grad is not None for p in self.first.parameters()):
            raise AssertionError('Frozen first accumulated gradients')
        return value * len(arrays[0])
