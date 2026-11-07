"""CPU checks for independent white GP-MP extraction and public phase inputs."""
import ast
from copy import deepcopy
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from project import ROOT

PACKAGE = ROOT / 'src/algorithm/GP_MP'
WHITE = ROOT / 'src/configs/candidates/GP_MP_white_preconditioned_matched_20261104.json'
PHASE = ROOT / 'src/configs/candidates/GP_MP_white_phase_frontend_marginal_20261106.json'


def parsed(path):
    return ast.parse((ROOT / path).read_text(encoding='utf-8'))


def definition(tree, name):
    return next(n for n in tree.body if getattr(n, 'name', None) == name)


class NormalizeNames(ast.NodeTransformer):
    """Only mechanical class renames and docstrings are ignored."""
    names = {'ColoredScore': 'CovarianceConditionedNetwork',
             'PreconditionedScore': 'PreconditionedMean', 'ColoredMoments': 'Moments'}

    def visit_Name(self, node):
        node.id = self.names.get(node.id, node.id)
        return node

    def visit_ClassDef(self, node):
        node.name = self.names.get(node.name, node.name)
        return self.generic_visit(node)

    def generic_visit(self, node):
        if hasattr(node, 'body') and isinstance(node.body, list) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                node.body = node.body[1:]
        return super().generic_visit(node)


def normalized(node):
    return ast.dump(NormalizeNames().visit(deepcopy(node)), include_attributes=False)


def test_numeric_functions_preserved():
    for old, new in (
        ('src/algorithm/C_STMP_variance_em_20261025/iterations.py', 'iterations.py'),
        ('src/algorithm/C_STMP_phase_init_marginal_20261104/initialization.py', 'initialization.py'),
        ('src/training/colored_preconditioned_20261024/operators.py', 'operators.py'),
    ):
        assert normalized(parsed(old)) == normalized(parsed(PACKAGE / new))
    for old, new, old_name, new_name in (
        ('src/training/colored_score_20261024/model.py', 'model.py', 'ColoredScore', 'CovarianceConditionedNetwork'),
        ('src/training/colored_preconditioned_20261024/model.py', 'model.py', 'PreconditionedScore', 'PreconditionedMean'),
        ('src/training/colored_score_20261024/noise.py', 'covariance.py', 'Covariance', 'Covariance'),
        ('src/algorithm/C_STMP/moments.py', 'moments.py', 'ColoredMoments', 'Moments'),
        ('src/algorithm/C_STMP/moments.py', 'moments.py', 'trace_variance', 'trace_variance'),
    ):
        assert normalized(definition(parsed(old), old_name)) == normalized(definition(parsed(PACKAGE / new), new_name))
    old = definition(definition(parsed('src/algorithm/C_STMP_variance_em_20261025/receiver.py'), 'Receiver'), 'infer')
    new = definition(definition(parsed(PACKAGE / 'receiver.py'), 'Receiver'), 'infer')
    assert normalized(old) == normalized(new)


def test_frozen_phase_numeric_body_preserved_without_known_phase_branch():
    old = definition(definition(parsed('src/algorithm/C_STMP_phase_frontend_marginal_20261104/receiver.py'), 'Receiver'), 'infer')
    new = definition(definition(parsed(PACKAGE / 'phase_receiver.py'), 'PhaseReceiver'), 'infer')
    assert ast.dump(ast.Module(body=old.body[2:], type_ignores=[]), include_attributes=False) == ast.dump(
        ast.Module(body=new.body[1:], type_ignores=[]), include_attributes=False)


def test_no_runtime_import_of_retired_packages():
    script = """
import sys, torch
torch.set_num_threads(1)
from algorithm.GP_MP import Receiver, PhaseReceiver, Denoiser
r = Receiver(sys.argv[1], device='cpu')
assert not torch.cuda.is_initialized()
bad = [n for n in sys.modules if n.startswith(('algorithm.C_STMP', 'training.colored', 'evaluation.white_'))]
assert not bad, bad
assert r.context()['denoiser_training_noise'] == 'white Gaussian'
"""
    result = subprocess.run([sys.executable, '-X', 'utf8', '-B', '-c', script, str(WHITE)],
                            cwd=ROOT, text=True, capture_output=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture(scope='module')
def receiver():
    import torch
    from algorithm.GP_MP import Receiver
    torch.set_num_threads(1)
    return Receiver(WHITE, device='cpu')


def test_white_loader_and_context(receiver):
    import torch
    assert receiver.configuration['classifier_policy'] == 'matched_white_mean_vI'
    assert receiver.context()['phase_mode'] == 'known'
    assert receiver.context()['oracle_phase_supplied'] is True
    assert all(p.device.type == 'cpu' and p.dtype == torch.float32
               for model in (receiver.model.network, receiver.evidence.network) for p in model.parameters())
    assert not torch.cuda.is_initialized()


def test_phase_constructor_reports_estimated_mode():
    import torch
    from algorithm.GP_MP import PhaseReceiver
    receiver = PhaseReceiver(PHASE, device='cpu')
    context = receiver.context()
    assert context['method'] == 'GP-MP-EP'
    assert context['phase_mode'] == 'estimated'
    assert context['oracle_phase_supplied'] is False
    assert context['supplied_phase_operator_used'] is False
    assert context['denoiser_training_noise'] == 'white Gaussian'
    assert context['input_fields'] == ['observation', 'pilot', 'activity_prior']
    assert not torch.cuda.is_initialized()


@pytest.mark.parametrize('change', ['colored_noise', 'schema', 'parameterization'])
def test_loader_rejects_wrong_provenance_before_construction(monkeypatch, change):
    from algorithm.GP_MP import model
    blob = dict(schema='colored-preconditioned-first-v1', output='conditional_mean',
                metadata={'noise': {'max_strength': 0.0}},
                parameterization=dict(reference_real_variance=.5, output='conditional_mean',
                                      objective='original_covariance_weighted_DSM'))
    if change == 'colored_noise':
        blob['metadata']['noise']['max_strength'] = .5
    elif change == 'schema':
        blob['schema'] = 'made-up-white-schema'
    else:
        blob['parameterization']['reference_real_variance'] = 1.
    monkeypatch.setattr(model.torch, 'load', lambda *a, **kw: blob)
    with pytest.raises(ValueError):
        model.load_checkpoint('unused.pt')


def test_extracted_network_cpu_output_and_checkpoint_keys_match(receiver):
    import torch
    from training.colored_preconditioned_20261024.model import load_checkpoint
    from algorithm.GP_MP.covariance import Covariance
    from algorithm.GP_MP.operators import Spectral
    old, _ = load_checkpoint(ROOT / receiver.configuration['first_checkpoint'], 'cpu')
    new = receiver.model.network
    assert old.state_dict().keys() == new.state_dict().keys()
    assert all(torch.equal(v, new.state_dict()[k]) for k, v in old.state_dict().items())
    generator = torch.Generator().manual_seed(17007)
    x = torch.randn((2, 2, 16, 16, 16), generator=generator)
    power = torch.tensor([.1, 1.], dtype=torch.float32)
    identity = torch.eye(16, dtype=torch.complex64).expand(2, -1, -1)
    covariance = Covariance(power, identity, identity)
    spectral = Spectral(identity, identity, (power[:, None, None] / 2).expand(-1, 16, 16))
    with torch.inference_mode():
        assert torch.equal(old(x, covariance, spectral), new(x, covariance, spectral))


def test_denoising_mean_matches_receiver_mean_without_variance_probes(receiver):
    from algorithm.GP_MP.denoising import Denoiser
    model = object.__new__(Denoiser)
    model.configuration, model.checkpoints = receiver.configuration, receiver.checkpoints
    model.network, model.batch_size = receiver.model.network, receiver.model.batch_size
    model.device, model.noise_support = 'cpu', receiver.model.noise_support
    rng = np.random.default_rng(17008)
    query = rng.normal(size=(2,16,16,16)) + 1j*rng.normal(size=(2,16,16,16))
    mean, record = model.infer(query, np.array([.1, 1.]))
    np.testing.assert_array_equal(mean, receiver.model.infer(query, np.array([.1, 1.])).mean)
    assert record['truth_used'] is False
    with pytest.raises(ValueError, match='truth-dependent'):
        model.infer(query, .1, priors=['oracle'])


@pytest.mark.parametrize('batch_size', [0, -1, 1.5, True])
def test_denoising_rejects_nonpositive_or_noninteger_batch(batch_size):
    from algorithm.GP_MP.denoising import Denoiser
    with pytest.raises(ValueError, match='positive integer'):
        Denoiser('unused', device='cpu', batch_size=batch_size)


def test_phase_frontend_forwards_only_estimated_phase(monkeypatch):
    from algorithm.GP_MP import phase_receiver as module
    from algorithm.GP_MP.receiver import Receiver
    from algorithm.STMP.records import SpatialConfig
    from system.observation import ReceiverInput
    from system.receiver.unknown_phase import UnknownPhaseInput
    from system.phase import phase_operator
    pilot = np.ones((2,2,16), complex)
    observation = np.zeros((2,16,16), complex)
    raw = UnknownPhaseInput(observation, pilot, 1., .1)
    slopes = np.array([.2, -.1])
    receiver = object.__new__(module.PhaseReceiver)
    receiver.phase_controls = module.initialization.Controls()
    receiver.controls = SpatialConfig()
    receiver.frontend_binding, receiver.last_trace = {'synthetic_wiring_test': True}, []
    calls = []
    monkeypatch.setattr(module, 'estimate_spatial_noise', lambda y: (.3, {'source': 'synthetic test'}))
    def phase(inputs, controls, observer=None):
        assert inputs.noise_variance == .3
        return {'phase_slopes': slopes, 'gains': 'must not be forwarded'}, {'truth_used_in_inference': False}
    def conditional(self, inputs, observer=None):
        assert isinstance(inputs, ReceiverInput)
        np.testing.assert_array_equal(inputs.operator, phase_operator(pilot, slopes))
        calls.append(inputs)
        return {'noise_variance_estimate': np.asarray(.3)}, {'seconds': 0.}
    monkeypatch.setattr(module.initialization, 'estimate', phase)
    monkeypatch.setattr(Receiver, 'infer', conditional)
    arrays, record = receiver.infer(raw)
    assert len(calls) == 1 and record['phase_mode'] == 'estimated'
    assert record['oracle_phase_supplied'] is False and record['receiver_truth_used'] is False
    assert record['phase_updates_inside_receiver'] == 0
    np.testing.assert_array_equal(arrays['phase_slopes'], slopes)
    with pytest.raises(TypeError, match='requires raw observation'):
        receiver.infer(ReceiverInput(observation, pilot, 1., .1))
