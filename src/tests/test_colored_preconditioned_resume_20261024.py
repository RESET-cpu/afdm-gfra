"""Check exact mid-epoch resume using a tiny CPU probe, not a research run."""
from copy import deepcopy
from dataclasses import dataclass
import json

import numpy as np
import torch
from torch import nn

from project import ROOT
from training.colored_preconditioned_20261024 import formal
from training.colored_preconditioned_20261024.model import PreconditionedScore


@dataclass
class ProbeConfig:
    antennas: int = 16
    side: int = 16


class Probe(PreconditionedScore):
    config = ProbeConfig()

    def __init__(self):
        nn.Module.__init__(self)
        self.reference_real_variance = .5
        self.gain = nn.Parameter(torch.tensor(-.01))
        self.bias = nn.Parameter(torch.tensor(.02))

    def raw(self, observation, covariance, spectral):
        return self.gain * observation + self.bias


def test_mid_epoch_resume_preserves_rng_optimizer_ema_and_short_final_batch(tmp_path, monkeypatch):
    cfg = json.loads(formal.DEFAULT.read_text(encoding='utf-8'))
    cfg = deepcopy(cfg)
    cfg['runtime']['device'] = 'cpu'
    cfg['first']['maximum_epochs'] = 2
    random = np.random.default_rng(20261024)
    shape = (67, 16, 16, 16)
    channels = (random.standard_normal(shape)+1j*random.standard_normal(shape)).astype(np.complex64)
    data = dict(train=channels, validation=channels[:3])

    def load(*_):
        return Probe(), dict(order=1, global_complex_rms=cfg['scale'],
            config=dict(snr_db_min=-20, snr_db_max=30))

    monkeypatch.setattr(formal, 'load_direct_checkpoint', load)
    monkeypatch.setattr(formal, 'PreconditionedScore', lambda base, reference: base)
    complete, resumed = tmp_path/'complete', tmp_path/'resumed'
    complete.mkdir(); resumed.mkdir()
    formal.Trainer(complete, cfg, 'probe-only').run(data)
    paused = formal.Trainer(resumed, cfg, 'probe-only')
    original_graph = formal.BatchGraph

    class StopAfterFirstBatch(original_graph):
        def backward(self, *args, **kwargs):
            value = super().backward(*args, **kwargs)
            paused.stop = True
            return value

    monkeypatch.setattr(formal, 'BatchGraph', StopAfterFirstBatch)
    paused.run(data)
    state = torch.load(resumed/'last.pt', weights_only=False)
    assert (state['epoch'], state['cursor'], state['steps']) == (1, 64, 1)
    monkeypatch.setattr(formal, 'BatchGraph', original_graph)
    formal.Trainer(resumed, cfg, 'probe-only').run(data)
    first = torch.load(complete/'last.pt', weights_only=False)
    second = torch.load(resumed/'last.pt', weights_only=False)
    for key in ('rng', 'shape_rng', 'epoch', 'cursor', 'steps', 'best', 'selected_epoch'):
        assert first[key] == second[key]
    assert first['steps'] == 4
    for key in ('model', 'ema'):
        for name in first[key]:
            torch.testing.assert_close(first[key][name], second[key][name], rtol=0, atol=0)
    for index, row in first['optimizer']['state'].items():
        for name, value in row.items():
            torch.testing.assert_close(value, second['optimizer']['state'][index][name], rtol=0, atol=0)
    for a, b in zip(first['history'], second['history']):
        assert a['train_loss'] == b['train_loss']
        assert a['validation'] == b['validation']
