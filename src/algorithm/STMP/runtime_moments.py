"""Reuse CUDA launch graphs for the unchanged two score networks.

The NumPy Tweedie conversion, network weights, float32 operations and batching
are unchanged. Only full configured batches use a graph; tails use eager calls.
See PyTorch 2.7 CUDA semantics, CUDA Graphs / Constraints.
"""
import time
import numpy as np
import torch

from networks.score import DirectCaiNetwork
from .moments import FullChannelMoments, MatrixMomentEstimate, convert_moments


class GraphedMoments(FullChannelMoments):
    def __init__(self, original):
        self.__dict__.update(original.__dict__)
        self.graph = None
        self.graph_setup_seconds = 0.0
        self.graph_replays = 0
        self.graph_enabled = (str(self.device).startswith('cuda')
            and isinstance(self.first, DirectCaiNetwork)
            and isinstance(self.second, DirectCaiNetwork))

    def _forward_pair(self):
        # DirectCaiNetwork.forward's tensor operations, after the same input
        # validation on the CPU. The wrapper's GPU bool check cannot be captured.
        packed = self.static_x.reshape(self.batch_size, 32, 16, 16)
        shape = self.static_x.shape
        return (self.first.network(packed, self.static_v).reshape(shape),
                self.second.network(packed, self.static_v).reshape(shape))

    def _prepare_graph(self, x, variance):
        started = time.perf_counter()
        self.static_x = x.clone()
        self.static_v = variance.clone()
        stream = torch.cuda.Stream(device=self.device)
        stream.wait_stream(torch.cuda.current_stream(self.device))
        with torch.cuda.stream(stream):
            for _ in range(3):
                self.static_first, self.static_second = self._forward_pair()
        torch.cuda.current_stream(self.device).wait_stream(stream)
        self.graph = torch.cuda.CUDAGraph()
        with torch.cuda.graph(self.graph, stream=stream):
            self.static_first, self.static_second = self._forward_pair()
        torch.cuda.synchronize(self.device)
        self.graph_setup_seconds += time.perf_counter() - started

    def infer(self, observation, variance):
        r = np.asarray(observation, complex)
        v = np.broadcast_to(np.asarray(variance, float), (len(r),))
        if (r.shape[1:] != (16, 16, 16) or not np.isfinite(r).all()
                or not np.isfinite(v).all() or np.any(v <= 0)):
            raise ValueError('Finite full-channel shape and positive variance required')
        means, variances = [], []
        with torch.inference_mode():
            for start in range(0, len(r), self.batch_size):
                block = r[start:start + self.batch_size]
                vb = v[start:start + self.batch_size]
                packed = self.scale_ratio * np.stack((block.real, block.imag), axis=1)
                x = torch.tensor(packed, dtype=torch.float32, device=self.device)
                nv = torch.tensor(vb * self.scale_ratio**2, dtype=torch.float32, device=self.device)
                if self.graph_enabled and len(block) == self.batch_size:
                    if self.graph is None:
                        self._prepare_graph(x, nv)
                    self.static_x.copy_(x)
                    self.static_v.copy_(nv)
                    self.graph.replay()
                    s1 = self.static_first.cpu().numpy().astype(float)
                    s2 = self.static_second.cpu().numpy().astype(float)
                    self.graph_replays += 1
                else:
                    s1 = self.first(x, nv).cpu().numpy().astype(float)
                    s2 = self.second(x, nv).cpu().numpy().astype(float)
                moment = convert_moments(block, vb, s1, s2, self.scale_ratio)
                means.append(moment.mean)
                variances.append(moment.variance)
                self.first_calls += 1
                self.second_calls += 1
        self.samples += len(r)
        moment = MatrixMomentEstimate(np.concatenate(means), np.concatenate(variances))
        self.last = dict(raw_network_variance=moment.variance.copy(), tweedie_ratio=moment.variance / v)
        return moment
