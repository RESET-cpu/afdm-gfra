"""Selected ten-layer inference, including observation-only noise estimation."""
import time
import numpy as np
import torch
from workspace import ROOT
from receiver.frontend.noise_estimation import estimate_spatial_noise
from channel.unknown_phase import UnknownPhaseInput


def synchronize(device):
    if device == 'cuda':
        torch.cuda.synchronize()


class ProposedReceiver:
    """Load the selected depth-10 checkpoint into the consolidated implementation."""
    def __init__(self, binding, device, noise_mode='estimated'):
        if noise_mode not in ('known', 'estimated'):
            raise ValueError('noise_mode must be known or estimated')
        self.noise_mode = noise_mode
        self.binding, self.device = binding, device
        spec = binding['proposed']
        from receiver.du import receiver as module
        from receiver.du import inputs as data
        from receiver.du.configuration import CONFIG_PATH
        from fileio import sha256 as sha
        if ((ROOT / spec['config']).resolve() != CONFIG_PATH.resolve()
                or sha(CONFIG_PATH) != spec['config_sha256']
                or sha(spec['checkpoint']) != spec['checkpoint_sha256']):
            raise ValueError('Final configuration or selected checkpoint changed')
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
        self.scale = binding['STMP']['scale']
        self.configuration = dict(spec, decision_threshold=.5)
        self.parameters = sum(p.numel() for p in self.model.parameters())
        self.last_layers = []
        self.phase_moment = None

    def infer(self, inputs, *, observer=None):
        # Raw pilots select the accepted joint phase/channel path. A supplied
        # operator retains the conditional ten-layer path (e.g. known phase).
        if isinstance(inputs, UnknownPhaseInput):
            return self._infer_unknown_phase(inputs, observer=observer)
        start = time.perf_counter()
        if self.noise_mode == 'estimated':
            noise, noise_record = estimate_spatial_noise(inputs.observation)
        else:
            noise = float(inputs.noise_variance)
            noise_record = dict(source='supplied_noise_variance', noise_variance=noise)
        public, _ = self.data.prepare_public(
            dict(y=inputs.observation, a=inputs.operator, noise=noise, rho=inputs.activity_prior),
            self.scale, self.device, phase_mode='known', noise_mode='known')
        # prepare_public receives the already selected operator and noise variance.
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
            noise_mode=self.noise_mode, supplied_noise_variance_used=self.noise_mode == 'known',
            noise_truth_used=self.noise_mode == 'known', truth_used_in_inference=self.noise_mode == 'known',
            checkpoint_sha256=self.configuration['checkpoint_sha256'], selected_epoch=1)

    def _infer_unknown_phase(self, inputs, *, observer=None):
        from fileio import read_json
        from fileio import sha256
        from receiver.du import phase_initialization
        from receiver.du import phase_layers
        if self.phase_moment is None:
            spec = self.binding['proposed']
            for key in ('phase_config', 'phase_moment'):
                if sha256(ROOT / spec[key]) != spec[key+'_sha256']:
                    raise ValueError('Accepted phase asset changed: '+key)
            self.phase_configuration = read_json(ROOT / spec['phase_config'])
            if self.phase_configuration['method'] != 'message_gem':
                raise ValueError('Expected the accepted message_gem phase configuration')
            with np.load(ROOT / spec['phase_moment'], allow_pickle=False) as saved:
                self.phase_moment = np.array(saved['second_moment'], copy=True)
        expected = inputs.pilot.shape[2]*inputs.observation.shape[2]
        if self.phase_moment.shape != (expected, expected):
            raise ValueError('Training second moment and channel dimensions disagree')
        start = time.perf_counter()
        if self.noise_mode == 'estimated':
            noise, noise_record = estimate_spatial_noise(inputs.observation)
        else:
            noise = float(inputs.noise_variance)
            noise_record = dict(source='supplied_noise_variance', noise_variance=noise)
        initial, initialization = phase_initialization.estimate(inputs.observation, inputs.pilot,
            noise, self.phase_moment, inputs.activity_prior)
        arrays, record = phase_layers.infer(self, inputs, noise, noise_record, initial['phase_slopes'])
        synchronize(self.device)
        elapsed = time.perf_counter()-start
        if observer is not None:
            for index, estimate in enumerate(self.last_layers, 1):
                observer(index, estimate)
        # Keep objective traces and iteration counts; full coordinate traces
        # already exist in the frozen development record and are not needed
        # for every point of a 2000-scene sweep.
        initialization['initializer'].pop('coordinates', None)
        for step in record['steps']:
            step['conditional_quadratic'].pop('users', None)
        arrays['initial_phase_slopes'] = initial['phase_slopes']
        record.update(seconds=elapsed, phase_method='message_gem', phase_mode='estimated',
            phase_initialization=initialization, phase_updates=9,
            phase_initialization_seconds=initialization['seconds'],
            phase_update_seconds=sum(s['seconds'] for s in record['steps']),
            parameter_count=self.parameters, noise_mode=self.noise_mode,
            noise_estimation=noise_record,
            supplied_noise_variance_used=self.noise_mode == 'known',
            noise_truth_used=self.noise_mode == 'known',
            truth_used_in_inference=self.noise_mode == 'known',
            phase_moment_sha256=self.binding['proposed']['phase_moment_sha256'],
            phase_config_sha256=self.binding['proposed']['phase_config_sha256'],
            diagnostics=record['steps'])
        return arrays, record

    @staticmethod
    def to_complex(value):
        a = value.detach().cpu().numpy().astype(np.float64)
        return a[:, 0] + 1j*a[:, 1]
