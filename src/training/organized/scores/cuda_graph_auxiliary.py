"""CUDA graph execution of the existing auxiliary microbatch operations.

Keep the original query draws, microbatch reductions and gradient accumulation.
Host guards replace only tensor-to-host validity checks inside captured forward
calls. Optimizer, clipping, validation and checkpoint selection stay unchanged.
"""
import numpy as np
import torch
from torch.nn import functional as F


def score_forward(model, r, v):
    c = model.config
    return model.network(r.reshape(len(r), 2*c.antennas, c.side, c.side), v).reshape(r.shape)


def activity_forward(model, r, v, mean):
    # EvidenceNetwork.inputs/forward, with its variance guard performed on host.
    c = model.config
    x = r.reshape(len(r), 2*c.antennas, c.side, c.side)
    f = mean.detach().reshape_as(x)
    factor = torch.sqrt(2/(1+v))[:, None, None, None]
    maps = torch.cat((factor*x, factor*f), dim=1)
    rx = 2*x.square().flatten(1).mean(1)/v
    ff = 2*f.square().flatten(1).mean(1)/v
    rf = 2*(x*f).flatten(1).mean(1)/v
    residual = 2*(x-f).square().flatten(1).mean(1)/v
    scalar = torch.stack((torch.log(v)/5, torch.log1p(rx), torch.log1p(ff),
        torch.sign(rf)*torch.log1p(abs(rf)), torch.log1p(residual)), dim=1)
    condition = model.condition(scalar[:, :1])
    for block, bias in zip(model.blocks, model.biases):
        maps = block(maps)+bias(condition)[:, :, None, None]
    return model.readout(torch.cat((maps.flatten(1), scalar), dim=1))[:, 0]


def query_parts(data, chosen, rng, prior, settings, stage):
    from training.organized.stmp.auxiliary import draw_queries
    parts = []
    for offset in range(0, len(chosen), settings['microbatch_size']):
        micro = chosen[offset:offset+settings['microbatch_size']]
        batch = draw_queries(data[micro], rng, prior['global_complex_rms'],
                             prior['noise_support'], paired=stage == 'activity')
        if stage == 'second':
            parts.append((batch['observation'], batch['variance'], batch['clean']))
        else:
            parts.append((np.concatenate((batch['positive'], batch['negative'])),
                          np.tile(batch['variance'], 2)))
    return parts


class AuxiliaryGraph:
    def __init__(self, model, first, stage, batch_size):
        if stage not in ('second', 'activity') or (stage == 'activity' and not model.config.use_score_mean):
            raise ValueError('Frozen full-mean auxiliary stages required')
        self.model, self.first, self.stage, self.batch_size = model, first, stage, batch_size
        self.graph = None

    def validate(self, parts):
        for part in parts:
            r, v = part[:2]
            c = self.first.config
            expected = (len(r), 2, c.antennas, c.side, c.side)
            if r.shape != expected or v.shape != (len(r),) or any(a.dtype != np.float32 for a in part):
                raise ValueError('Full float32 observation/variance shapes required')
            if not all(np.isfinite(a).all() for a in part) or not np.all(v > 0):
                raise ValueError('Finite queries and positive scalar noise variance required')
            if self.stage == 'second' and part[2].shape != expected:
                raise ValueError('Clean-channel shape differs')
            if self.stage == 'activity' and len(r) % 2:
                raise ValueError('Balanced positive/negative queries required')

    def losses_backward(self, parts):
        total = sum(len(p[0]) for p in parts)
        losses = []
        for part in parts:
            r, v = part[:2]
            with torch.no_grad():
                first_score = score_forward(self.first, r, v)
            if self.stage == 'second':
                variance = (v/2)[:, None, None, None, None]
                b = variance.sqrt()*first_score.detach()+(r-part[2])/variance.sqrt()
                residual = variance*score_forward(self.model, r, v)-b.square()+1
                loss = residual.flatten(1).mean(1).square().mean()
            else:
                # Same separate float64 multiply/add operations as NumPy complete_mean.
                with torch.no_grad():
                    mean = (r.double()+(.5*v.double())[:, None, None, None, None]*first_score.double()).float()
                labels = torch.cat((torch.ones(len(r)//2, device=r.device),
                                    torch.zeros(len(r)//2, device=r.device)))
                loss = F.binary_cross_entropy_with_logits(activity_forward(self.model, r, v, mean), labels)
            (loss*len(r)/total).backward()
            losses.append(loss.detach())
        return torch.stack(losses)

    def backward(self, parts, *, use_graph=True):
        self.validate(parts)
        count = sum(len(p[0]) for p in parts)//(2 if self.stage == 'activity' else 1)
        if not use_graph or count != self.batch_size:
            tensors = [tuple(torch.as_tensor(a, device='cuda') for a in p) for p in parts]
            losses = self.losses_backward(tensors)
        else:
            if self.graph is None:
                self.inputs = [tuple(torch.as_tensor(a, device='cuda').clone() for a in p) for p in parts]
                stream = torch.cuda.Stream()
                stream.wait_stream(torch.cuda.current_stream())
                with torch.cuda.stream(stream):
                    for _ in range(3):
                        self.model.zero_grad(set_to_none=True)
                        self.losses_backward(self.inputs)
                torch.cuda.current_stream().wait_stream(stream)
                self.model.zero_grad(set_to_none=True)
                self.graph = torch.cuda.CUDAGraph()
                with torch.cuda.graph(self.graph):
                    self.losses = self.losses_backward(self.inputs)
                self.gradients = [p.grad for p in self.model.parameters()]
            if [tuple(a.shape for a in p) for p in parts] != [tuple(a.shape for a in p) for p in self.inputs]:
                raise ValueError('Captured microbatch shapes changed')
            for destination, source in zip(self.inputs, parts):
                for tensor, array in zip(destination, source):
                    tensor.copy_(torch.from_numpy(array))
            self.graph.replay()
            for parameter, gradient in zip(self.model.parameters(), self.gradients):
                parameter.grad = gradient
            losses = self.losses
        values = losses.cpu().numpy().astype(float)
        if not np.isfinite(values).all():
            raise FloatingPointError('Nonfinite auxiliary objective; saved state preserved')
        divisor = 2 if self.stage == 'activity' else 1
        return [(float(value), len(p[0])//divisor) for value, p in zip(values, parts)]
