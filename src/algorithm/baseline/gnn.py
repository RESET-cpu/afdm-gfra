"""Ding GNN-ASPL, with declared complex AMP and continuous-label adaptations.

Source: Ding et al., TVT 2026, pp. 3--5, Eqs. (12)--(28).
The accepted manuscript contains index/self-reference typos in (12)--(13).
The executable choices and project settings are recorded in
results/baseline_revision_20261008/phase2_sources/GNN_ASPL_SOURCE.md.
This module is a reimplementation; it does not contain author weights.
"""
from dataclasses import asdict, dataclass
from pathlib import Path
import hashlib
import json
import time

import numpy as np
import torch
from torch import nn

from algorithm.baseline._common import coefficient_activity
from system.dictionary import AFDMGrid
from system.observation import ReceiverInput, load_input
from utils import sha256, state_sha, write_json


METHOD = 'gnn_aspl_ding2026'
CHECKPOINT_SCHEMA = 'ding-gnn-aspl-project-v1'
INTEGER_GRID = dict(delay_step=1., doppler_points=None, doppler_step_hz=30000.)
PAPER_SHA256 = '22dceda0036c892f44e961ce9ab6d094930e610befe0d51c18c3357aa1890ec5'


@dataclass(frozen=True)
class GNNASPLSettings:
    layers: int = 10
    attention_width: int = 32
    hidden_width: int = 32
    negative_slope: float = .2
    initial_damping: float = .2
    initial_theta: float = .5
    variance_floor: float = 1e-12

    def __post_init__(self):
        if any(isinstance(x, bool) or not isinstance(x, int) or x < 1
               for x in (self.layers, self.attention_width, self.hidden_width)):
            raise ValueError('positive integer layer and hidden dimensions required')
        if (not np.isfinite([self.negative_slope, self.initial_damping,
                            self.initial_theta, self.variance_floor]).all()
                or not 0 < self.initial_damping < 1
                or not 0 < self.initial_theta < 1
                or self.negative_slope < 0 or self.variance_floor <= 0):
            raise ValueError('finite valid graph, damping, prior and variance settings required')


def complex_bg_posterior(r, phi, theta, gamma, mu=None):
    """Joint-antenna row probability and Eqs. (16)--(18), before mean damping.

    r/phi have shape [..., row, antenna], theta [..., row].  A proper complex
    Gaussian density has no real-Gaussian half factor in its log likelihood.
    The four returned real node features are precisely Ding Eq. (21).
    """
    if mu is None:
        mu = torch.zeros((), dtype=r.dtype, device=r.device)
    if torch.any(phi <= 0) or torch.any(gamma <= 0):
        raise ValueError('positive pseudo-observation and slab variances required')
    phi_plus_gamma = phi + gamma
    u1 = -(torch.abs(r - mu).square() / phi_plus_gamma).sum(dim=-1)
    u2 = (torch.abs(r).square() / phi).sum(dim=-1)
    u3 = -torch.log1p(gamma / phi).sum(dim=-1)
    eps = torch.finfo(phi.dtype).eps
    prior = theta.clamp(eps, 1 - eps)
    pi = torch.sigmoid(torch.logit(prior) + u1 + u2 + u3)
    slab_variance = gamma * phi / phi_plus_gamma
    slab_mean = slab_variance * (mu / gamma + r / phi)
    mean = pi[..., None] * slab_mean
    variance = (pi * (1 - pi))[..., None] * torch.abs(slab_mean).square()
    variance = variance + pi[..., None] * slab_variance
    features = torch.stack((u1, u2, u3, pi), dim=-1)
    return dict(mean=mean, variance=variance, probability=pi,
                slab_mean=slab_mean, slab_variance=slab_variance,
                features=features)


class BlockAttentionGRU(nn.Module):
    """Ding Eqs. (22)--(26), all nodes of each user including its self edge."""
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.projection = nn.Linear(4, settings.attention_width, bias=False)
        self.attention = nn.Parameter(torch.empty(2 * settings.attention_width))
        nn.init.xavier_uniform_(self.attention.view(1, -1))
        self.gru = nn.GRUCell(4, settings.hidden_width)
        self.readout = nn.Linear(settings.hidden_width, 1)

    def forward(self, features, hidden, users, *, return_attention=False):
        batch, nodes, feature_size = features.shape
        if feature_size != 4 or users < 1 or nodes % users:
            raise ValueError('four features and complete same-user node blocks required')
        atoms = nodes // users
        raw = features.reshape(batch, users, atoms, 4)
        transformed = self.projection(raw)
        width = self.settings.attention_width
        # a^T [W u_n || W u_j], computed without materializing concatenations.
        left = (transformed * self.attention[:width]).sum(dim=-1)
        right = (transformed * self.attention[width:]).sum(dim=-1)
        logits = torch.nn.functional.leaky_relu(
            left[..., :, None] + right[..., None, :],
            negative_slope=self.settings.negative_slope)
        attention = torch.softmax(logits, dim=-1)
        # Eq. (24) sends original four-dimensional u_j, not projected W u_j.
        aggregate = (attention @ raw).reshape(batch * nodes, 4)
        if hidden is None:
            hidden = torch.zeros(batch * nodes, self.settings.hidden_width,
                                 dtype=features.dtype, device=features.device)
        else:
            hidden = hidden.reshape(batch * nodes, self.settings.hidden_width)
        next_hidden = self.gru(aggregate, hidden)
        theta = torch.sigmoid(self.readout(next_hidden)).reshape(batch, nodes)
        result = (theta, next_hidden.reshape(batch, nodes, -1))
        return (*result, attention) if return_attention else result


class AMPParameters(nn.Module):
    def __init__(self, initial_damping):
        super().__init__()
        value = float(np.log(initial_damping / (1 - initial_damping)))
        self.beta_logit = nn.Parameter(torch.tensor(value, dtype=torch.float32))
        self.xi_logit = nn.Parameter(torch.tensor(value, dtype=torch.float32))

    def damping(self):
        return torch.sigmoid(self.beta_logit), torch.sigmoid(self.xi_logit)


class GNNASPLNetwork(nn.Module):
    """Ten AMP updates with nine effective, independently parameterized GNNs.

    gamma is a frozen, training-only fitted physical coefficient second moment.
    A is the raw physical design. Neither labels nor activity truth are inputs.
    A/Y may be unbatched [L,D]/[L,M] or batched [B,L,D]/[B,L,M].
    """
    def __init__(self, gamma, settings=None):
        super().__init__()
        self.settings = settings or GNNASPLSettings()
        if not np.isfinite(gamma) or gamma <= 0:
            raise ValueError('positive scalar training-fitted slab variance required')
        self.register_buffer('gamma', torch.tensor(float(gamma), dtype=torch.float32))
        self.amp = nn.ModuleList(AMPParameters(self.settings.initial_damping)
                                 for _ in range(self.settings.layers))
        self.gnn = nn.ModuleList(BlockAttentionGRU(self.settings)
                                 for _ in range(self.settings.layers - 1))

    def forward(self, design, observation, noise_variance, users, *,
                layers=None, collect_trace=False):
        count = self.settings.layers if layers is None else layers
        if not isinstance(count, int) or not 1 <= count <= self.settings.layers:
            raise ValueError('valid AMP prefix layer count required')
        if not isinstance(users, int) or users < 1:
            raise ValueError('positive integer users required')
        if design.device.type != 'cpu' or observation.device.type != 'cpu':
            raise ValueError('the verified GNN-ASPL runtime is CPU only')
        dtype = torch.complex128 if self.gamma.dtype == torch.float64 else torch.complex64
        design, observation = design.to(dtype=dtype), observation.to(dtype=dtype)
        unbatched = design.ndim == 2
        if unbatched:
            design, observation = design[None], observation[None]
        if (design.ndim != 3 or observation.ndim != 3
                or design.shape[:2] != observation.shape[:2]
                or design.shape[2] % users):
            raise ValueError('compatible physical design, observations and user blocks required')
        if not torch.isfinite(design).all() or not torch.isfinite(observation).all():
            raise ValueError('finite physical design and observations required')
        batch, observations, nodes = design.shape
        antennas = observation.shape[-1]
        noise = torch.as_tensor(noise_variance, dtype=self.gamma.dtype,
                                device=design.device)
        if noise.numel() not in (1, batch) or not torch.isfinite(noise).all() or torch.any(noise <= 0):
            raise ValueError('positive supplied noise variance per sample required')
        noise = noise.reshape(-1, 1, 1)
        z = torch.zeros(batch, nodes, antennas, dtype=dtype, device=design.device)
        theta = torch.full((batch, nodes), self.settings.initial_theta,
                           dtype=self.gamma.dtype, device=design.device)
        variance = torch.ones_like(z.real) * (self.settings.initial_theta * self.gamma)
        psi = torch.zeros(batch, observations, antennas, dtype=self.gamma.dtype)
        residual_message = torch.zeros_like(observation)  # s^0=0, no initial Onsager term.
        hidden = None
        squared_design = torch.abs(design).square()
        conjugate_design = design.conj().transpose(-1, -2)
        variance_backprojection = squared_design.transpose(-1, -2)
        trace = []
        for index in range(count):
            beta, xi = self.amp[index].damping()
            psi = beta * (squared_design @ variance) + (1 - beta) * psi
            output_mean = design @ z - psi * residual_message
            output_variance = (noise + psi).clamp_min(self.settings.variance_floor)
            residual_message = (observation - output_mean) / output_variance
            precision = variance_backprojection @ output_variance.reciprocal()
            phi = precision.clamp_min(self.settings.variance_floor).reciprocal()
            r = z + phi * (conjugate_design @ residual_message)
            posterior = complex_bg_posterior(r, phi, theta, self.gamma)
            z = xi * posterior['mean'] + (1 - xi) * z
            variance = posterior['variance']  # Eq. (18b) has no extra variance damping.
            if not torch.isfinite(z).all() or not torch.isfinite(variance).all():
                raise FloatingPointError(f'nonfinite GNN-ASPL posterior in AMP layer {index + 1}')
            if collect_trace:
                trace.append(dict(layer=index + 1, beta=float(beta.detach()), xi=float(xi.detach()),
                    coefficient_energy=float(torch.abs(z).square().mean().detach()),
                    probability_min=float(posterior['probability'].min().detach()),
                    probability_max=float(posterior['probability'].max().detach()),
                    pseudo_variance_min=float(phi.min().detach()),
                    message_variance_min=float(psi.min().detach())))
            if index + 1 < count:
                theta, hidden = self.gnn[index](posterior['features'], hidden, users)
        result = dict(mean=z, variance=variance, probability=posterior['probability'],
                      trace=trace, iterations=count)
        if unbatched:
            for key in ('mean', 'variance', 'probability'):
                result[key] = result[key][0]
        return result

    def phase_parameters(self, layers, phase):
        """Section III-C: GNN(t-1), AMP(t), then joint layers 1..t."""
        if not isinstance(layers, int) or not 1 <= layers <= self.settings.layers:
            raise ValueError('valid layerwise training stage required')
        for parameter in self.parameters():
            parameter.requires_grad_(False)
        if phase == 'gnn':
            selected = [] if layers == 1 else list(self.gnn[layers - 2].parameters())
        elif phase == 'damping':
            selected = list(self.amp[layers - 1].parameters())
        elif phase == 'joint':
            selected = [p for module in list(self.amp[:layers]) + list(self.gnn[:layers - 1])
                        for p in module.parameters()]
        else:
            raise ValueError('phase must be gnn, damping or joint')
        for parameter in selected:
            parameter.requires_grad_(True)
        return selected


class GNNASPLMPSNetwork(GNNASPLNetwork):
    """Opt-in float32 Metal execution of the same proper-complex equations.

    Real/imaginary components implement each complex product with four real
    matrix products. No complex tensor is placed on MPS. Checkpoint parameters
    and buffer names match the CPU network; physical atoms are not parameters.
    """
    def __init__(self, gamma, settings=None):
        if not torch.backends.mps.is_available():
            raise ValueError('mps_real requires an available PyTorch MPS backend')
        super().__init__(gamma, settings)
        self.to('mps')

    def _parts(self, tensor):
        return (tensor.real.to(device='mps', dtype=torch.float32),
                tensor.imag.to(device='mps', dtype=torch.float32))

    def forward_operator(self, operator, observation, noise_variance, users, *, layers=None, collect_trace=False):
        """Construct the raw physical dictionary directly from public inputs."""
        from system.dictionary import physical_atoms
        unbatched = operator.ndim == 3
        if unbatched:
            operator, observation = operator[None], observation[None]
        if operator.ndim != 4 or operator.shape[-2] != users or operator.shape[-1] != 16:
            raise ValueError('operator[batch,frame,user,N=16] required')
        atoms, _, _ = physical_atoms(**INTEGER_GRID)
        if not hasattr(self, '_physical_atom_parts'):
            self._physical_atom_parts = self._parts(torch.tensor(np.array(atoms)))
        gr, gi = self._physical_atom_parts
        pr, pi = self._parts(operator)
        b, q, k, n = pr.shape
        gr, gi = gr.reshape(-1, n).T, gi.reshape(-1, n).T
        raw_r = pr.reshape(-1, n) @ gr - pi.reshape(-1, n) @ gi
        raw_i = pr.reshape(-1, n) @ gi + pi.reshape(-1, n) @ gr
        shape = (b, q, k, len(atoms), n)
        ar = raw_r.reshape(shape).permute(0, 1, 4, 2, 3).reshape(b, q*n, k*len(atoms))
        ai = raw_i.reshape(shape).permute(0, 1, 4, 2, 3).reshape(b, q*n, k*len(atoms))
        return self._forward_real(ar, ai, observation, noise_variance, users,
            unbatched=unbatched, layers=layers, collect_trace=collect_trace)

    def forward(self, design, observation, noise_variance, users, *, layers=None, collect_trace=False):
        unbatched = design.ndim == 2
        if unbatched:
            design, observation = design[None], observation[None]
        ar, ai = self._parts(design)
        return self._forward_real(ar, ai, observation, noise_variance, users,
            unbatched=unbatched, layers=layers, collect_trace=collect_trace)

    def _forward_real(self, ar, ai, observation, noise_variance, users, *, unbatched, layers, collect_trace):
        count = self.settings.layers if layers is None else layers
        if not isinstance(count, int) or not 1 <= count <= self.settings.layers:
            raise ValueError('valid AMP prefix layer count required')
        if (ar.ndim != 3 or observation.ndim != 3 or ar.shape[:2] != observation.shape[:2]
                or not isinstance(users, int) or users < 1 or ar.shape[2] % users):
            raise ValueError('compatible design, observations and user blocks required')
        yr, yi = self._parts(observation)
        batch, _, nodes = ar.shape
        antennas = yr.shape[-1]
        noise = torch.as_tensor(noise_variance, dtype=torch.float32, device='mps')
        if noise.numel() not in (1, batch) or not torch.isfinite(noise).all() or torch.any(noise <= 0):
            raise ValueError('positive supplied noise variance per sample required')
        noise = noise.reshape(-1, 1, 1)
        zr = torch.zeros(batch, nodes, antennas, device='mps'); zi = torch.zeros_like(zr)
        theta = torch.full((batch, nodes), self.settings.initial_theta, device='mps')
        variance = torch.ones_like(zr) * (self.settings.initial_theta * self.gamma)
        psi = torch.zeros_like(yr); sr = torch.zeros_like(yr); si = torch.zeros_like(yr)
        squared = ar.square() + ai.square()
        atr, ati = ar.transpose(-1, -2), ai.transpose(-1, -2)
        hidden = None; trace = []
        for index in range(count):
            beta, xi = self.amp[index].damping()
            psi = beta * (squared @ variance) + (1-beta) * psi
            mr = ar @ zr - ai @ zi - psi * sr
            mi = ar @ zi + ai @ zr - psi * si
            output_variance = (noise+psi).clamp_min(self.settings.variance_floor)
            sr, si = (yr-mr)/output_variance, (yi-mi)/output_variance
            phi = (squared.transpose(-1, -2) @ output_variance.reciprocal()).clamp_min(self.settings.variance_floor).reciprocal()
            rr = zr + phi * (atr @ sr + ati @ si)
            ri = zi + phi * (atr @ si - ati @ sr)
            r2 = rr.square() + ri.square(); plus = phi+self.gamma
            u1, u2 = -(r2/plus).sum(-1), (r2/phi).sum(-1)
            u3 = -torch.log1p(self.gamma/phi).sum(-1)
            eps = torch.finfo(phi.dtype).eps
            pi = torch.sigmoid(torch.logit(theta.clamp(eps, 1-eps))+u1+u2+u3)
            slab_variance = self.gamma*phi/plus
            slab_r, slab_i = slab_variance*(rr/phi), slab_variance*(ri/phi)
            zr = xi*pi[..., None]*slab_r+(1-xi)*zr
            zi = xi*pi[..., None]*slab_i+(1-xi)*zi
            variance = (pi*(1-pi))[..., None]*(slab_r.square()+slab_i.square())+pi[..., None]*slab_variance
            if collect_trace:
                trace.append(dict(layer=index+1, beta=float(beta.detach()), xi=float(xi.detach()),
                    coefficient_energy=float((zr.square()+zi.square()).mean().detach()),
                    probability_min=float(pi.min().detach()), probability_max=float(pi.max().detach()),
                    pseudo_variance_min=float(phi.min().detach()), message_variance_min=float(psi.min().detach())))
            if index+1 < count:
                theta, hidden = self.gnn[index](torch.stack((u1, u2, u3, pi), -1), hidden, users)
        mean = torch.complex(zr.to('cpu'), zi.to('cpu'))
        variance, pi = variance.to('cpu'), pi.to('cpu')
        if not torch.isfinite(mean).all() or not torch.isfinite(variance).all():
            raise FloatingPointError('nonfinite MPS GNN-ASPL posterior')
        if unbatched:
            mean, variance, pi = mean[0], variance[0], pi[0]
        return dict(mean=mean, variance=variance, probability=pi, iterations=count, trace=trace)


def make_gnn_aspl_network(gamma, settings=None, backend='cpu'):
    if backend == 'cpu':
        return GNNASPLNetwork(gamma, settings)
    if backend == 'mps_real':
        return GNNASPLMPSNetwork(gamma, settings)
    raise ValueError('GNN-ASPL backend must be cpu or mps_real')


def coefficient_nmse(estimate, target):
    """Eq. (28): mean of per-sample coefficient NMSE, not a pooled ratio."""
    if estimate.shape != target.shape or estimate.ndim not in (2, 3):
        raise ValueError('matching coefficient matrices or batches required')
    if estimate.ndim == 2:
        estimate, target = estimate[None], target[None]
    denominator = torch.abs(target).square().sum(dim=(-2, -1))
    if torch.any(denominator <= 0):
        raise ValueError('Eq. (28) requires nonzero coefficient labels')
    numerator = torch.abs(estimate - target).square().sum(dim=(-2, -1))
    return (numerator / denominator).mean()


def project_channel_coefficients(channel, atoms, *, verify_orthogonality=True):
    """Training-only oracle full-H projection into orthogonal physical atoms."""
    h, g = np.asarray(channel), np.asarray(atoms)
    if (h.ndim != 4 or g.ndim != 3 or h.shape[-2:] != g.shape[-2:]
            or g.shape[-2] != g.shape[-1]
            or not np.isfinite(h).all() or not np.isfinite(g).all()):
        raise ValueError('finite square full channels and physical atoms required')
    n = g.shape[-1]
    if verify_orthogonality:
        gram = np.einsum('grn,hrn->gh', g.conj(), g, optimize=True)
        if not np.allclose(gram, n * np.eye(len(g)), rtol=1e-10, atol=1e-10):
            raise ValueError('the projection formula requires Gram=N I')
    coefficients = np.einsum('grn,kmrn->kgm', g.conj(), h, optimize=True) / n
    return coefficients.reshape(h.shape[0] * len(g), h.shape[1])


class GNNASPLReceiver:
    def __init__(self, configuration):
        self.configuration = configuration
        settings = configuration['methods'][METHOD]
        self.settings = settings
        path = settings.get('checkpoint_path')
        expected_sha = settings.get('checkpoint_sha256')
        if not path or not expected_sha:
            raise ValueError('an explicit trained checkpoint path and SHA256 are required')
        self.checkpoint_path = Path(path)
        if not self.checkpoint_path.is_file() or sha256(self.checkpoint_path) != expected_sha:
            raise ValueError('checkpoint is missing or its SHA256 does not match')
        payload = torch.load(self.checkpoint_path, map_location='cpu', weights_only=True)
        if payload.get('schema') != CHECKPOINT_SCHEMA or payload.get('method') != METHOD:
            raise ValueError('verified GNN-ASPL checkpoint schema and method required')
        self.training = payload['training']
        if not self.training.get('training_completed'):
            raise ValueError('checkpoint must record completed training')
        status = self.training.get('status')
        if status not in ('SMOKE_ONLY', 'PRELIMINARY_TRAINED', 'TRAINED_UNQUALIFIED'):
            raise ValueError('a recognized completed GNN-ASPL training status is required')
        if status == 'SMOKE_ONLY' and not settings.get('allow_smoke_checkpoint', False):
            raise ValueError('a smoke checkpoint requires explicit allow_smoke_checkpoint=True')
        if status == 'PRELIMINARY_TRAINED' and not settings.get('allow_preliminary_checkpoint', False):
            raise ValueError('a preliminary checkpoint requires explicit allow_preliminary_checkpoint=True')
        self.checkpoint_source = payload.get('source', {})
        self.training_recipe_sha256 = payload.get('training_recipe_sha256')
        if status != 'SMOKE_ONLY':
            preliminary = status == 'PRELIMINARY_TRAINED'
            mixed_training = self.training.get('training_mode') == 'mixed_snr_grid'
            samples = self.training.get('training_samples', 0)
            valid_count = 128 <= samples <= 10000 if preliminary else samples > 10000
            if (not valid_count
                    or self.training.get('effective_batch_size') != 128
                    or (self.training.get('separate_model_per_snr') is not False if mixed_training
                        else not self.training.get('separate_model_per_snr'))
                    or not self.training_recipe_sha256):
                raise ValueError('completed checkpoint must record the per-SNR paper training recipe and declared sample budget')
            from ._validation import verify_current_sources
            verify_current_sources()
            recorded_recipe = payload.get('training_recipe')
            if not isinstance(recorded_recipe, dict):
                raise ValueError('full checkpoint must include its recorded training recipe')
            recipe_bytes = json.dumps(recorded_recipe, sort_keys=True, separators=(',', ':'),
                                      allow_nan=False).encode()
            if hashlib.sha256(recipe_bytes).hexdigest() != self.training_recipe_sha256:
                raise ValueError('full checkpoint training recipe content does not match its SHA256')
            if (recorded_recipe.get('smoke') is not False
                    or recorded_recipe.get('preliminary', False) is not preliminary
                    or recorded_recipe.get('train_samples') != self.training['training_samples']
                    or recorded_recipe.get('batch_size') != self.training['effective_batch_size']
                    or (not mixed_training and recorded_recipe.get('snr_db') != self.training.get('snr_db'))
                    or recorded_recipe.get('architecture') != payload['architecture']
                    or recorded_recipe.get('dictionary') != payload['dictionary']):
                raise ValueError('full checkpoint metadata differs from its non-smoke training recipe')
            if mixed_training:
                dataset = payload.get('dataset', {})
                assignments = dataset.get('assignments')
                expected_epochs = (9 * recorded_recipe.get('gnn_epochs', 0)
                    + 10 * recorded_recipe.get('damping_epochs', 0)
                    + 10 * recorded_recipe.get('joint_epochs', 0))
                final_joint_epochs = self.training.get('final_joint_epochs', recorded_recipe.get('joint_epochs', 0))
                adaptive = recorded_recipe.get('adaptive_final_joint', False)
                if adaptive:
                    if not recorded_recipe.get('joint_epochs', 0) <= final_joint_epochs <= recorded_recipe.get('max_final_joint_epochs', 0):
                        raise ValueError('mixed final joint epochs differ from the declared extension rule')
                    expected_epochs += final_joint_epochs - recorded_recipe['joint_epochs']
                elif final_joint_epochs != recorded_recipe.get('joint_epochs', 0):
                    raise ValueError('mixed checkpoint has undeclared extra joint training')
                if (recorded_recipe.get('training_mode') != 'mixed_snr_grid'
                        or not self.training.get('shared_model_across_snr_and_grid')
                        or recorded_recipe.get('snr_range') != self.training.get('snr_range')
                        or recorded_recipe.get('on_grid_probability') != self.training.get('on_grid_probability')
                        or recorded_recipe.get('validation_samples') != self.training.get('validation_samples')
                        or self.training.get('completed_training_phases') != 29
                        or self.training.get('completed_epochs') != expected_epochs
                        or self.training.get('selection', {}).get('layer') != 10
                        or self.training.get('selection', {}).get('phase') != 'joint'
                        or self.training.get('backend', 'cpu') != recorded_recipe.get('backend', 'cpu')
                        or self.training.get('cache_mode', 'dense') != recorded_recipe.get('cache_mode', 'dense')
                        or not isinstance(assignments, dict)
                        or len(assignments.get('train', [])) != samples
                        or len(assignments.get('validation', [])) != self.training.get('validation_samples')
                        or dataset.get('condition_spec') != recorded_recipe.get('condition_spec')
                        or not dataset.get('seed_sets_disjoint')
                        or payload['gamma_fit'].get('conditioning') !=
                           'lambda_n=1; physical active-user path coordinates with collisions merged'
                        or payload['gamma_fit'].get('assumed_slab_mean') != 0.
                        or payload['gamma_fit'].get('on_grid_training_cases', 0) < 1
                        or payload['gamma_fit'].get('calibration_or_validation_or_test_truth_used') is not False):
                    raise ValueError('mixed checkpoint requires its complete declared data, slab fit and layerwise training contract')
                assignment_sha = hashlib.sha256(json.dumps(assignments, sort_keys=True,
                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()
                if (assignment_sha != dataset.get('assignment_sha256')
                        or assignment_sha != self.training.get('dataset_assignment_sha256')
                        or [item['seed'] for item in assignments['train']] != self.training.get('train_seeds')
                        or [item['seed'] for item in assignments['validation']] != self.training.get('validation_seeds')
                        or set(self.training['train_seeds']) & set(self.training['validation_seeds'])):
                    raise ValueError('mixed checkpoint data assignments differ from their bound identity')
        declared_recipe = settings.get('training_recipe_sha256')
        if declared_recipe is not None and declared_recipe != self.training_recipe_sha256:
            raise ValueError('checkpoint training recipe SHA256 does not match configuration')
        architecture = GNNASPLSettings(**payload['architecture'])
        if architecture.layers != 10 or architecture.initial_theta != .5:
            raise ValueError('Ding baseline requires ten AMP steps and theta0=0.5')
        self.backend = settings.get('device', 'cpu')
        self.model = make_gnn_aspl_network(float(payload['gamma_fit']['physical_variance']), architecture, self.backend)
        self.model.load_state_dict(payload['state_dict'], strict=True)
        self.model.eval()
        self.model.requires_grad_(False)
        if not all(torch.isfinite(x).all() for x in self.model.state_dict().values()):
            raise ValueError('finite checkpoint parameters required')
        if (float(self.model.gamma) <= 0 or not np.isclose(float(self.model.gamma),
                float(payload['gamma_fit']['physical_variance']), rtol=1e-6, atol=0)):
            raise ValueError('checkpoint slab variance differs from the frozen training fit')
        declared_state = self.training.get('final_state_sha256')
        if ((status != 'SMOKE_ONLY' and not declared_state)
                or (declared_state is not None and declared_state != state_sha(self.model))):
            raise ValueError('checkpoint model state does not match the completed training state')
        self.dictionary = settings.get('dictionary', configuration['dictionary'])
        if self.dictionary != payload['dictionary'] or self.dictionary != INTEGER_GRID:
            raise ValueError('training and inference require the same declared integer grid')
        if configuration['channel_output'] != 'dictionary_reconstruction':
            raise ValueError('dictionary reconstruction required')
        if settings.get('noise_mode', 'supplied') != 'supplied':
            raise ValueError('GNN-ASPL uses fixed supplied generation noise variance')
        if settings.get('activity_statistic', 'reconstructed_channel_energy') != 'reconstructed_channel_energy':
            raise ValueError('the common comparison uses reconstructed channel energy')
        if settings.get('activity_comparator', '>') != '>':
            raise ValueError('channel-energy readout requires the common strict > comparator')
        self.threshold = settings.get('activity_threshold')
        if self.threshold is not None and (not np.isfinite(self.threshold) or self.threshold < 0):
            raise ValueError('finite nonnegative calibrated threshold required')
        self.gamma_fit = payload['gamma_fit']

    def infer(self, inputs, *, observer=None):
        if not isinstance(inputs, ReceiverInput):
            raise TypeError('ReceiverInput required; truth is not an inference input')
        if observer is not None:
            raise ValueError('per-iteration channel observer is not supported for the unfolded network')
        start = time.perf_counter()
        grid = AFDMGrid.from_operator(inputs.operator, **self.dictionary)
        design = np.ascontiguousarray(grid.design * grid.norms[None, :])
        received = grid.stack(inputs.observation)
        dictionary_seconds = time.perf_counter() - start
        with torch.no_grad():
            result = self.model(torch.as_tensor(design), torch.as_tensor(received),
                                inputs.noise_variance, grid.users, collect_trace=True)
        coefficients = result['mean'].cpu().numpy()
        estimate = grid.reconstruct(coefficients * grid.norms[:, None])
        relative_score, energy = coefficient_activity(coefficients, grid.users)
        channel_energy = np.mean(abs(estimate)**2, axis=(1, 2, 3))
        arrays = dict(estimate=estimate, coefficients=coefficients,
            coefficient_variance=result['variance'].cpu().numpy(),
            row_probability=result['probability'].cpu().numpy(),
            activity_score=channel_energy, coefficient_energy=energy,
            relative_coefficient_score=relative_score, channel_energy=channel_energy,
            noise_variance_estimate=np.asarray(inputs.noise_variance))
        if self.threshold is not None:
            arrays['activity_decision'] = channel_energy > self.threshold
        if not all(np.isfinite(value).all() for value in arrays.values()):
            raise FloatingPointError('nonfinite GNN-ASPL receiver output')
        fitted_observation = np.einsum('ld,dm->lm', design, coefficients, optimize=False)
        residual = float(np.sum(abs(received - fitted_observation)**2)
                         / max(np.sum(abs(received)**2), 1e-30))
        record = dict(method=METHOD, status='COMPLETE', stopping_reason='fixed_unfolding_depth',
            iterations=result['iterations'], effective_gnn_updates=9, trace=result['trace'],
            seconds=time.perf_counter() - start, dictionary_seconds=dictionary_seconds,
            truth_loaded=False, supplied_noise_variance_used=True, noise_mode='supplied',
            noise_variance_fixed=True, supplied_activity_prior_used=False,
            design_column_normalization=False, estimate_kind='dictionary_reconstruction',
            activity_statistic='reconstructed_channel_energy', activity_comparator='>',
            activity_threshold=self.threshold, threshold_status=self.settings.get('threshold_status', 'uncalibrated'),
            activity_decision_available=self.threshold is not None,
            formal_qualification=False, training_status=self.training['status'],
            preliminary_training=self.training['status'] == 'PRELIMINARY_TRAINED',
            training_budget_scope=self.training.get('training_budget_scope'),
            checkpoint_path=str(self.checkpoint_path), checkpoint_sha256=sha256(self.checkpoint_path),
            checkpoint_source=self.checkpoint_source, architecture=asdict(self.model.settings),
            training_recipe_sha256=self.training_recipe_sha256,
            training_snr_db=self.training.get('snr_db'),
            training_mode=self.training.get('training_mode', 'separate_snr'),
            training_snr_range=self.training.get('snr_range'),
            shared_model_across_snr_and_grid=self.training.get('shared_model_across_snr_and_grid', False),
            execution_backend=self.backend, training_backend=self.training.get('backend', 'cpu'),
            training_samples=self.training.get('training_samples'),
            validation_samples=self.training.get('validation_samples'),
            gamma_fit=self.gamma_fit, slab_mean=0., slab_variance_fixed=True,
            graph_adjacency='same-user fully connected including self',
            amp_equation_corrections=['12a previous psi index', '12b previous residual and negative Onsager',
                                      '13b phi in place of undefined zeta', 'proper complex likelihood'],
            initialization='z0=0;s0=0;psi0=0;theta0=.5;V0=theta0*gamma;g0=0',
            input_scope=self.configuration.get('scope'), relative_residual_energy=residual,
            configuration=self.configuration)
        return arrays, record

    def run(self, input_path, output_path):
        output = Path(output_path)
        if output.suffix != '.npz' or output.exists() or output.with_suffix('.json').exists():
            raise ValueError('fresh .npz output required')
        arrays, record = self.infer(load_input(input_path))
        output.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(output, **arrays)
        record.update(input_sha256=sha256(input_path), output_sha256=sha256(output))
        write_json(output.with_suffix('.json'), record)
        return record


def create_native(self):
    from copy import deepcopy
    native_cfg = deepcopy(self.configuration)
    setting = native_cfg['methods'][METHOD]
    setting.update(activity_threshold=None,
                   activity_statistic='reconstructed_channel_energy', activity_comparator='>')
    return GNNASPLReceiver(native_cfg)


def infer_known(self, inputs, *, observer=None):
    return self.native.infer(inputs, observer=observer)
