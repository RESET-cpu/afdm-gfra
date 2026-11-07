"""Evaluation adapters; the frozen receiver equations and weights are unchanged."""
from pathlib import Path
import importlib
import os
import sys
import time

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'experiment'))
from afdm_jadcedd.algorithm.baselines.noise_estimation import estimate_spatial_noise
from afdm_jadcedd.algorithm.proposed_noise_candidate import EstimatedNoiseProposedReceiver
from afdm_jadcedd.algorithm.baselines.baseline_noise import EstimatedNoiseBaselineReceiver
from _support.density_ratio import GaussianSiteReceiver
from afdm_jadcedd.algorithm.baselines import receiver as baseline_module
from afdm_jadcedd.algorithm.baselines.offgrid import receiver as offgrid_module

# Original readout signatures were frozen with POSIX relative paths. Match that
# serialization on Windows, retaining every actual source hash and numeric rule.
_baseline_sources = baseline_module.inference_sources
_offgrid_sources = offgrid_module.inference_sources
baseline_module.inference_sources = lambda method: {k.replace('\\', '/'):v for k,v in _baseline_sources(method).items()}
offgrid_module.inference_sources = lambda: {k.replace('\\', '/'):v for k,v in _offgrid_sources().items()}

LABELS = dict(ten_layer='L-STMP (10 layers)', legacy='Legacy three-network',
              legacy_gaussian='Legacy Gaussian-site evidence', offgrid_sbl='Off-grid SBL',
              gnn='GNN-ASPL', gamp='GAMP-SBL', somp='SOMP')


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


class TenLayer:
    """Load only the completed depth-10 checkpoint from its immutable source tree."""
    def __init__(self, binding, device):
        self.binding, self.device = binding, device
        spec = binding['ten_layer']
        run = Path(spec['run'])
        os.environ['AFDM_LSTMP_ROOT'] = str(ROOT)
        os.environ['AFDM_LSTMP_CONFIG'] = spec['config']
        sys.path.insert(0, str(run / 'source_code'))
        from experiments.lstmp_candidate_20261019 import common, data
        if common.OUT.resolve() != run.resolve():
            raise RuntimeError('Another L-STMP configuration was already imported')
        module = importlib.import_module('experiments.' + spec['package'] + '.receiver')
        if not Path(module.__file__).resolve().is_relative_to(run / 'source_code'):
            raise RuntimeError('Receiver did not load from the frozen training source')
        checkpoint = torch.load(spec['checkpoint'], map_location='cpu', weights_only=False, mmap=True)
        if (checkpoint['depth'] != 10 or checkpoint['epoch'] != spec['selected_epoch']
                or checkpoint['manifest_sha256'] != spec['manifest_sha256']):
            raise ValueError('Depth, selection epoch or training identity mismatch')
        self.model = module.Receiver()
        for _ in range(10):
            self.model.add_layer(None)
        self.model.load_state_dict(checkpoint['state'], strict=True)
        self.model.to(device).eval()
        self.model.use_checkpoint = False
        self.model.graphs_enabled = False
        self.data = data
        self.scale = binding['legacy_configuration']['scale']
        self.configuration = dict(spec, decision_threshold=.5)
        self.parameters = sum(p.numel() for p in self.model.parameters())
        self.last_layers = []

    def infer(self, inputs, *, observer=None):
        # The input is public observation + estimated-phase operator + prior.
        # The physical noise field is ignored, exactly as for the old receiver.
        start = time.perf_counter()
        noise, noise_record = estimate_spatial_noise(inputs.observation)
        public, _ = self.data.prepare_public(
            dict(y=inputs.observation, a=inputs.operator, noise=noise, rho=inputs.activity_prior),
            self.scale, self.device, phase_mode='known', noise_mode='known')
        # "known" here means the supplied estimates, never simulator truth.
        before = self.model.score_evaluations
        with torch.inference_mode():
            outputs, diagnostics = self.model(public)
        synchronize(self.device)
        conditional_seconds = time.perf_counter() - start
        self.last_layers = [self.to_complex(row['estimate'])*self.scale for row in outputs]
        probabilities = torch.sigmoid(outputs[-1]['logits']).detach().cpu().numpy().astype(float)
        if observer is not None:
            for index, estimate in enumerate(self.last_layers, 1):
                observer(index, estimate)
        arrays = dict(estimate=self.last_layers[-1], probabilities=probabilities,
                      activity_decision=probabilities >= .5, noise_variance_estimate=np.asarray(noise))
        return arrays, dict(status='COMPLETE', iterations=10, stopping_reason='FIXED_DEPTH',
            seconds=conditional_seconds, score_calls=self.model.score_evaluations-before,
            parameter_count=self.parameters, diagnostics=diagnostics, noise_estimation=noise_record,
            supplied_noise_variance_used=False, truth_used_in_inference=False,
            checkpoint_sha256=self.configuration['checkpoint_sha256'], selected_epoch=1)

    @staticmethod
    def to_complex(value):
        a = value.detach().cpu().numpy().astype(np.float64)
        return a[:, 0] + 1j*a[:, 1]


def network_modules(model):
    if isinstance(model, TenLayer):
        return [model.model]
    if isinstance(model, EstimatedNoiseProposedReceiver):
        modules = [model.base.model.first, model.base.model.second]
        if model.base.evidence is not None:
            modules.append(model.base.evidence.network)
        return modules
    return []  # Existing numerical baselines retain their native CPU backend.


def activate(models, selected, device):
    """Only the measured receiver occupies CUDA memory; loading is outside timing."""
    for name, model in models.items():
        for module in network_modules(model):
            module.to(device if name == selected else 'cpu')
    if device == 'cuda':
        torch.cuda.empty_cache()


def parameter_count(model):
    modules = network_modules(model)
    if not modules:
        native = getattr(getattr(model, 'base', None), 'native', None)
        network = getattr(native, 'model', None)
        modules = [network] if isinstance(network, torch.nn.Module) else []
    return sum(p.numel() for module in modules for p in module.parameters())


def build(method, binding, device):
    if method == 'ten_layer':
        return TenLayer(binding, device)
    if method in ('legacy', 'legacy_gaussian'):
        cls = EstimatedNoiseProposedReceiver if method == 'legacy' else GaussianSiteReceiver
        return cls(binding['legacy_configuration'], device=device)
    if method not in ('offgrid_sbl', 'gnn', 'gamp', 'somp'):
        raise ValueError('Unsupported method: ' + method)
    config = 'offgrid_baselines.json' if method == 'offgrid_sbl' else 'baselines.json'
    return EstimatedNoiseBaselineReceiver(method, config=ROOT / 'configs' / config, device=device)
