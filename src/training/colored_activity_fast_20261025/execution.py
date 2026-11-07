"""One-batch prefetch with checkpoint-exact NumPy RNG and pinned transfers."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import dataclass

import numpy as np
import torch

from training.colored_activity_20261025.batches import ActivityGraph
from training.scores.cuda_graph_auxiliary import query_parts


@dataclass
class Prepared:
    arrays: list
    pinned: list
    rng_state: dict


class Prefetch:
    def __init__(self, bank, indices, cursor, rng, prior, settings, validator):
        self.bank, self.indices, self.prior, self.settings = bank, indices, prior, settings
        self.validator = validator
        self.rng = np.random.default_rng()
        self.rng.bit_generator.state = deepcopy(rng.bit_generator.state)
        self.pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='activity_queries')
        self.future = self.pool.submit(self.prepare, cursor)

    def prepare(self, cursor):
        chosen = self.indices[cursor:cursor+self.settings['batch_size']]
        arrays = query_parts(self.bank, chosen, self.rng, self.prior, self.settings, 'activity')
        self.validator(arrays)
        pinned = [tuple(torch.empty(a.shape, dtype=torch.float32, pin_memory=True).copy_(torch.from_numpy(a))
                        for a in p) for p in arrays]
        return Prepared(arrays, pinned, deepcopy(self.rng.bit_generator.state))

    def next(self, cursor, rng):
        batch = self.future.result()
        # Save only the RNG after the consumed batch, never the prefetched one.
        rng.bit_generator.state = deepcopy(batch.rng_state)
        next_cursor = cursor+self.settings['batch_size']
        self.future = self.pool.submit(self.prepare, next_cursor) if next_cursor < len(self.indices) else None
        return batch

    def close(self):
        self.pool.shutdown(wait=True, cancel_futures=True)


class PinnedActivityGraph(ActivityGraph):
    def backward(self, batch, *, use_graph=True):
        if not isinstance(batch, Prepared):
            return super().backward(batch, use_graph=use_graph)
        parts = batch.arrays
        count = sum(len(p[0]) for p in parts)//2
        if not use_graph or self.graph is None or count != self.batch_size:
            return super().backward(parts, use_graph=use_graph)
        if [tuple(a.shape for a in p) for p in parts] != [tuple(a.shape for a in p) for p in self.inputs]:
            raise ValueError('Captured query shapes changed')
        for destination, source in zip(self.inputs, batch.pinned):
            for tensor, host in zip(destination, source):
                tensor.copy_(host, non_blocking=True)
        self.graph.replay()
        for parameter, gradient in zip(self.model.parameters(), self.gradients):
            parameter.grad = gradient
        values = self.losses.cpu().numpy().astype(float)
        if not np.isfinite(values).all():
            raise FloatingPointError('Nonfinite activity loss')
        return [(float(value), len(p[0])//2) for value,p in zip(values,parts)]
