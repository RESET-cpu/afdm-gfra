"""Opt-in CUDA graph for the unchanged first-score forward/backward operations.

Host checks mirror DirectCaiNetwork and scalar_real_variance before transfer.
Adam, clipping, EMA, query generation and checkpointing remain outside capture.
"""
import numpy as np
import torch


def validate_arrays(model, arrays):
    h, r, v, labels = arrays
    expected = (len(r), 2, model.config.antennas, model.config.side, model.config.side)
    if r.shape != expected or h.shape != expected or labels.shape != (len(r),):
        raise ValueError('direct Cai AFDM score shape mismatch')
    if not np.issubdtype(labels.dtype, np.floating) or not np.all(np.isfinite(labels) & (labels > 0)):
        raise ValueError('continuous scores require actual positive complex variances')
    flat = v.reshape(len(v), -1)
    if not np.all(flat == flat[:, :1]):
        raise ValueError('Cai scalar-noise objectives require one variance per sample')
    if not np.all(np.isfinite(flat[:, 0]) & (flat[:, 0] > 0)):
        raise ValueError('invalid scalar noise variance')


def loss_unchecked(model, tensors):
    h, r, variance, labels = tensors
    c = model.config
    score = model.network(r.reshape(len(r), 2*c.antennas, c.side, c.side), labels).reshape(r.shape)
    v = (variance.flatten(1)[:, 0]/2)[:, None, None, None, None]
    return (v.sqrt()*score+(r-h)/v.sqrt()).square().mean()


class FirstGraph:
    def __init__(self, model, batch_size):
        self.model, self.batch_size = model, batch_size
        self.graph = None

    def backward(self, arrays, *, use_graph=True):
        validate_arrays(self.model, arrays)
        if not use_graph or len(arrays[0]) != self.batch_size:
            tensors = [torch.as_tensor(a, device='cuda') for a in arrays]
            loss = loss_unchecked(self.model, tensors)
            (loss * 1.).backward()
        else:
            if self.graph is None:
                self.inputs = [torch.as_tensor(a, device='cuda').clone() for a in arrays]
                stream = torch.cuda.Stream()
                stream.wait_stream(torch.cuda.current_stream())
                with torch.cuda.stream(stream):
                    for _ in range(3):
                        self.model.zero_grad(set_to_none=True)
                        (loss_unchecked(self.model, self.inputs) * 1.).backward()
                torch.cuda.current_stream().wait_stream(stream)
                self.model.zero_grad(set_to_none=True)
                self.graph = torch.cuda.CUDAGraph()
                with torch.cuda.graph(self.graph):
                    self.loss = loss_unchecked(self.model, self.inputs)
                    (self.loss * 1.).backward()
                self.gradients = [p.grad for p in self.model.parameters()]
            for destination, source in zip(self.inputs, arrays):
                destination.copy_(torch.from_numpy(source))
            self.graph.replay()
            for parameter, gradient in zip(self.model.parameters(), self.gradients):
                parameter.grad = gradient
            loss = self.loss
        value = float(loss.detach().cpu())
        if not np.isfinite(value):
            raise FloatingPointError('Nonfinite DSM loss; saved checkpoint preserved')
        return value * len(arrays[0])
