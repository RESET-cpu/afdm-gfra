"""CPU-only checks of dependency gates and frozen phase/white-backend wiring."""
import json
import sys
from pathlib import Path
import numpy as np
import pytest
from utils import write_json, sha256
from evaluation.white_phase_frontend_20261106 import common


def make_completed(folder, methods, count, *, ablation=False):
    folder.mkdir()
    summary = dict(status='VERIFIED', methods={m:{str(s):dict(inputs=count, decisions=count*40)
                   for s in common.SNRS} for m in methods})
    write_json(folder/'PLAN.json', {})
    summary['plan_sha256'] = sha256(folder/'PLAN.json')
    write_json(folder/'SUMMARY.json', summary)
    (folder/'PAIRED_CASES.csv').write_text('test receipt\n', encoding='utf-8')
    receipt = dict(status='PASS', summary_sha256=sha256(folder/'SUMMARY.json'),
                   paired_sha256=sha256(folder/'PAIRED_CASES.csv'))
    if ablation:
        receipt.update(new_inferences=6000, reused_inferences=6000, all_activity_predictions_rescored=True,
                       new_channel_predictions_rescored=True, paired_coverage_verified=True)
    else:
        receipt.update(inputs=6000, saved_arrays_rescored=True, input_and_output_hashes_verified=True)
    write_json(folder/'COMPLETION.json', receipt)
    write_json(folder/'STATUS.json', dict(stage='COMPLETE', active_workers=0))


def test_gate_requires_ablation_receipt_and_process_exit(tmp_path, monkeypatch):
    white, ablation = tmp_path/'white', tmp_path/'ablation'
    monkeypatch.setattr(common, 'WHITE', white); monkeypatch.setattr(common, 'ABLATION', ablation)
    monkeypatch.setattr(common, 'live_processes', lambda tokens: [])
    make_completed(white, ('GP-MP','CGP-MP'), 1000)
    assert common.dependencies()['status'] == 'WAITING'
    make_completed(ablation, ('STMP-Gaussian','STMP-LR','GP-MP-Gaussian','GP-MP-LR'), 500, ablation=True)
    assert common.dependencies()['status'] == 'PASS'
    monkeypatch.setattr(common, 'live_processes', lambda tokens: [dict(pid=123, command='test predecessor')])
    assert common.dependencies()['status'] == 'WAITING'
    monkeypatch.setattr(common, 'live_processes', lambda tokens: [])
    (ablation/'PAIRED_CASES.csv').write_text('tampered\n', encoding='utf-8')
    with pytest.raises(ValueError, match='Changed asset'):
        common.dependencies()


def test_worker_is_blocked_before_torch_or_plan_access(tmp_path, monkeypatch):
    from evaluation.white_phase_frontend_20261106 import run
    monkeypatch.setattr(common, 'WHITE', tmp_path/'missing-white')
    monkeypatch.setattr(common, 'ABLATION', tmp_path/'missing-ablation')
    monkeypatch.setattr(common, 'live_processes', lambda tokens: [])
    monkeypatch.setitem(sys.modules, 'torch', None)
    with pytest.raises(RuntimeError, match='Predecessors incomplete'):
        run.worker(0, preflight=True)


def test_white_checkpoint_loader_on_cpu():
    import torch
    from evaluation.white_phase_frontend_20261106.receiver import Receiver
    assert not torch.cuda.is_initialized()
    torch.set_num_threads(1)
    receiver = Receiver(common.BINDING, device='cpu')
    assert receiver.configuration['schema'] == 'white-matched-receiver-binding-v1'
    assert receiver.configuration['classifier_policy'] == 'matched_white_mean_vI'
    assert receiver.context()['denoiser_training_noise'] == 'white Gaussian'
    assert all(p.device.type == 'cpu' and p.dtype == torch.float32
               for model in (receiver.model.network, receiver.evidence.network) for p in model.parameters())
    assert not torch.cuda.is_initialized()


def test_frozen_frontend_passes_only_estimated_phase_to_conditional_receiver(monkeypatch):
    from dataclasses import asdict
    from evaluation.white_phase_frontend_20261106.receiver import Receiver
    from algorithm.C_STMP_phase_frontend_marginal_20261104 import receiver as phase_module
    from algorithm.C_STMP_variance_em_20261025.receiver import Receiver as NumericalReceiver
    from algorithm.STMP.records import SpatialConfig
    from system.receiver.unknown_phase import UnknownPhaseInput
    from system.observation import ReceiverInput
    from system.phase import phase_operator
    # Synthetic arrays test dispatch and provenance only; they are not experiment results.
    pilot = np.ones((2, 2, 16), dtype=complex)
    observation = np.zeros((2, 16, 16), dtype=complex)
    inputs = UnknownPhaseInput(observation, pilot, 1., .1)
    slopes = np.array([.2, -.1])
    receiver = object.__new__(Receiver)
    receiver.phase_controls = phase_module.initialization.Controls()
    receiver.controls = SpatialConfig()
    receiver.frontend_binding = {'test': True}
    receiver.last_trace = []
    calls = []
    def noise(y):
        assert y is observation
        return .3, {'source': 'synthetic test'}
    def phase(raw, controls, observer=None):
        assert isinstance(raw, UnknownPhaseInput) and raw.noise_variance == .3
        return dict(phase_slopes=slopes, gains='must not be forwarded'), dict(truth_used_in_inference=False)
    def conditional(self, conditional_input, observer=None):
        assert isinstance(conditional_input, ReceiverInput)
        np.testing.assert_allclose(conditional_input.operator, phase_operator(pilot, slopes), rtol=0, atol=0)
        assert conditional_input.noise_variance == .3 and conditional_input.activity_prior == .1
        calls.append(conditional_input)
        return dict(noise_variance_estimate=np.asarray(.3)), dict(seconds=0., phase_initialization={})
    monkeypatch.setattr(phase_module, 'estimate_spatial_noise', noise)
    monkeypatch.setattr(phase_module.initialization, 'estimate', phase)
    monkeypatch.setattr(NumericalReceiver, 'infer', conditional)
    prediction, record = receiver.infer(inputs)
    assert len(calls) == 1
    common.check_phase_record(record, prediction)
    assert record['actual_iteration_controls'] == asdict(receiver.controls)
    with pytest.raises(TypeError, match='requires raw observation'):
        receiver.infer(ReceiverInput(observation, pilot, 1., .1))
