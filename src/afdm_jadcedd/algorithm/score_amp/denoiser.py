"""Frozen active-channel Tweedie mean times the learned activity probability."""
from pathlib import Path
import numpy as np
import torch
from scipy.special import expit
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.utils import sha256
from afdm_jadcedd.algorithm.proposed.network import load_direct_checkpoint
from afdm_jadcedd.algorithm.proposed.activity import FrozenEvidence
from .core import UnsupportedVariance


class FrozenJointDenoiser:
    def __init__(self, binding, *, device='cpu', batch_size=40):
        for key in ('first_checkpoint', 'evidence_checkpoint', 'prior_definition'):
            if sha256(ROOT/binding[key]) != binding[key+'_sha256']:
                raise ValueError('Frozen asset changed: '+key)
        self.first, metadata = load_direct_checkpoint(ROOT/binding['first_checkpoint'], device)
        self.first.requires_grad_(False)
        self.evidence = FrozenEvidence(ROOT/binding['evidence_checkpoint'], device=device)
        self.scale = float(binding['scale'])
        if (metadata['order'] != 1 or metadata.get('normalization') != 'population_rms'
                or metadata['global_complex_rms'] != self.scale
                or self.evidence.scale != self.scale
                or self.evidence.first_sha256 != binding['first_checkpoint_sha256']
                or self.evidence.second_sha256 != binding['second_checkpoint_sha256']):
            raise ValueError('Same frozen score, feature scale and classifier required')
        self.noise_support = tuple(self.evidence.noise_support)
        if self.noise_support != (0.001, 100.0):
            raise ValueError('Unexpected frozen AWGN training support')
        self.device, self.batch_size = device, batch_size
        if not isinstance(batch_size, int) or batch_size < 1:
            raise ValueError('Positive network batch size required')
        self.evaluations = self.samples = self.first_batches = self.activity_batches = 0

    def infer(self, observation, variance, activity_prior):
        r = np.asarray(observation, complex)
        v = float(variance)
        if r.ndim != 4 or r.shape[1:] != (16, 16, 16) or not np.isfinite(r).all():
            raise ValueError('Finite K x 16 x 16 x 16 channel query required')
        if not self.noise_support[0] <= v <= self.noise_support[1]:
            raise UnsupportedVariance(f'Query variance {v:.12g} outside {self.noise_support}')
        if not 0 < activity_prior < 1:
            raise ValueError('Activity prior strictly between zero and one required')
        means, probabilities = [], []
        for start in range(0, len(r), self.batch_size):
            block = r[start:start+self.batch_size]
            vb = np.full(len(block), v)
            packed = np.stack((block.real, block.imag), axis=1)
            with torch.inference_mode():
                x = torch.as_tensor(packed, dtype=torch.float32, device=self.device)
                nv = torch.as_tensor(vb, dtype=torch.float32, device=self.device)
                score = self.first(x, nv).cpu().numpy().astype(float)
            f = block+(v/2)*(score[:, 0]+1j*score[:, 1])
            logits = self.evidence.infer(block, vb, f)
            probability = expit(logits+np.log(activity_prior)-np.log1p(-activity_prior))
            if not np.isfinite(f).all() or not np.isfinite(probability).all():
                raise FloatingPointError('Nonfinite score/activity output')
            means.append(f)
            probabilities.append(probability)
            self.first_batches += 1
            self.activity_batches += 1
        self.evaluations += 1
        self.samples += len(r)
        conditional = np.concatenate(means)
        probability = np.concatenate(probabilities)
        return dict(mean=probability[:, None, None, None]*conditional,
                    conditional_mean=conditional, probabilities=probability)

