"""Prepare existing scenes on one CPU worker without changing visitation order."""
from concurrent.futures import ThreadPoolExecutor

import torch

from experiments.lstmp_training_v3_20261020.data import Cases as ReferenceCases


class Cases:
    def __init__(self, split, scale, device):
        self.device = device
        self.source = ReferenceCases(split, scale, 'cpu')
        self.indices = self.source.indices
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix=f'{split}-data')
        self.pending = {}
        self.sequential = split == 'validation'

    def __len__(self):
        return len(self.source)

    def prefetch(self, indices):
        for index in indices:
            index = int(index)
            if index not in self.pending:
                self.pending[index] = self.executor.submit(self.source.__getitem__, index)

    def __getitem__(self, index):
        index = int(index)
        self.prefetch([index])
        if self.sequential:
            self.prefetch(range(index + 1, min(index + 4, len(self))))
        public, labels, info = self.pending.pop(index).result()
        move = lambda values: {
            key: value.to(self.device) if isinstance(value, torch.Tensor) else value
            for key, value in values.items()}
        return move(public), move(labels), info

    def close(self):
        self.executor.shutdown(wait=True)
        self.pending.clear()
