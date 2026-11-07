"""Actual receiver checks; all updates are discarded, no performance claims."""
import gc
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
from threadpoolctl import threadpool_limits
from prepare_lstmp_training_v2_20261020 import ROOT, TARGET, PACKAGE, read, write, sha

os.environ['AFDM_LSTMP_ROOT'] = str(ROOT)
os.environ['AFDM_LSTMP_CONFIG'] = str(TARGET / f'source_code/experiments/{PACKAGE}/config.json')
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
sys.path.insert(0, str(TARGET / 'source_code'))
from experiments.lstmp_candidate_20261019 import receiver as legacy
from experiments.lstmp_candidate_20261019 import common, data
from experiments.lstmp_candidate_20261019.execution import configure_execution
from experiments.lstmp_candidate_20261019.optimization import clip_gradient_norm
from experiments.lstmp_training_v2_20261020.receiver import Receiver
from experiments.lstmp_training_v2_20261020.objectives import loss_components, assign_gradients
from experiments.lstmp_training_v2_20261020.optimization import (
    eligible_parameters, set_phase, make_optimizer, gradient_diagnostics, restore_rng)
from experiments.lstmp_training_v2_20261020.train import save_resume
from experiments.lstmp_training_v2_20261020.evaluation import evaluate


def main():
    started = time.time()
    if (TARGET / 'TRAINING_LAUNCH.json').exists() or (TARGET / 'RUNNING.lock').exists():
        raise RuntimeError('Checks must run before formal training')
    folder = TARGET / 'preflight'
    folder.mkdir(exist_ok=True)
    unit = subprocess.run([sys.executable, '-m', 'pytest', '-q',
                          str(ROOT / 'tests/test_lstmp_training_v2.py')],
                         cwd=ROOT, capture_output=True, text=True)
    (folder / 'unit_tests.txt').write_text(unit.stdout + unit.stderr, encoding='utf-8')
    if unit.returncode:
        raise RuntimeError(unit.stdout + unit.stderr)
    torch.set_num_threads(4)
    threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32 = common.CONFIG['allow_tf32']
    torch.backends.cudnn.allow_tf32 = common.CONFIG['allow_tf32']
    # Repeated derivative comparisons isolate implementation from parallel
    # reduction order. Capacity checks below use the production execution mode.
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(common.CONFIG['seed'])
    statistics = read(TARGET / 'protocol/TRAINING_STATISTICS.json')
    prior = torch.load(TARGET / 'initialization/first_50000.pt',
                       map_location='cpu', weights_only=False, mmap=True)
    cases = data.Cases('train', prior['scale'], 'cuda')
    positions = [next(i for i, index in enumerate(cases.indices) if index % 24 == group)
                 for group in (0, 4, 8, 12, 16, 20)]
    write(folder / 'PLAN.json', dict(training_positions=positions,
        source_indices=[cases.indices[i] for i in positions],
        maximum_depth=7, control_updates_discarded=True,
        scope='Formula, gradients, optimizer, checkpoint, forward parity and GPU capacity; no trained accuracy claim',
        independent_test_data_used=False, activity_head_perturbation_for_gradient_checks=.01))

    def make(depth):
        model = Receiver()
        for _ in range(depth):
            model.add_layer(prior['state'])
        return model.cuda()

    def setup(model, epoch):
        eligible = eligible_parameters(model)
        optimizer = make_optimizer(model, common.CONFIG['receiver'], eligible, fused=True)
        configure_execution(model, optimizer, common.CONFIG['execution'], 'cuda')
        set_phase(model, optimizer, eligible, epoch)
        return optimizer, eligible

    def step(model, optimizer, position):
        public, labels, info = cases[position]
        optimizer.zero_grad(set_to_none=True)
        torch.cuda.synchronize()
        before = time.perf_counter()
        calls_before = model.score_evaluations
        outputs, diagnostics = model(public)
        components = loss_components(outputs, labels, statistics)
        assert torch.isfinite(components['total'])
        assign_gradients(model, components)
        norm = float(clip_gradient_norm(model.parameters(), 1.))
        optimizer.step()
        torch.cuda.synchronize()
        return dict(loss=float(components['total'].detach()), gradient_norm=norm,
                    score_forward_calls=model.score_evaluations - calls_before,
                    seconds=time.perf_counter() - before, info=info, diagnostics=diagnostics)

    model = make(2)
    assert all(a.data_ptr() != b.data_ptr() for a, b in zip(
        model.layers[0].parameters(), model.layers[1].parameters()))
    for layer in model.layers:
        for name, value in layer.score.state_dict().items():
            assert torch.equal(value.cpu(), prior['state'][name])
        assert torch.equal(layer.calibration, torch.zeros(3, device='cuda'))
    public, labels, info = cases[positions[0]]
    assert 'active' not in public and 'x' not in public
    model.eval()
    with torch.no_grad():
        outputs, _ = model(public)
        for output in outputs:
            torch.testing.assert_close(torch.sigmoid(output['logits']),
                torch.full_like(output['logits'], public['rho']), rtol=1e-6, atol=1e-7)
        # The zero final classifier weights initially block its input gradients.
        # Perturb only disposable check models to test the connected paths.
        for layer in model.layers:
            layer.activity.head[-1].weight.fill_(.01)
    old = legacy.Receiver()
    for _ in range(2):
        old.add_layer(prior['state'])
    converted = {name: value for name, value in model.state_dict().items()
                 if name.rsplit('.', 1)[-1] not in ('c_gamma', 'c_alpha', 'c_beta')}
    for index, layer in enumerate(model.layers):
        converted[f'layers.{index}.calibration'] = layer.calibration.detach()
    old.load_state_dict(converted, strict=True)
    old.cuda().eval()
    parity = []
    with torch.no_grad():
        for position in positions:
            public, labels, info = cases[position]
            outputs, diagnostics = model(public)
            previous, previous_diagnostics, previous_messages = old(public, return_messages=True)
            for output, (estimate, logit), message in zip(outputs, previous, previous_messages):
                torch.testing.assert_close(output['estimate'], estimate, rtol=1e-6, atol=1e-6)
                torch.testing.assert_close(output['logits'], logit, rtol=1e-6, atol=1e-6)
                torch.testing.assert_close(output['conditional'], message['conditional'], rtol=1e-6, atol=1e-6)
            parity.append(dict(position=position, info=info,
                maximum_error=float((outputs[-1]['estimate'] - previous[-1][0]).abs().max())))
    del old, previous, previous_messages, previous_diagnostics, converted, outputs
    gc.collect()
    torch.cuda.empty_cache()
    print('Actual two-layer forward parity passed on all six training profiles.', flush=True)

    optimizer, eligible = setup(model, 2)
    model.train()
    public, labels, _ = cases[positions[0]]
    outputs, _ = model(public)
    assert outputs[-1]['conditional'].requires_grad
    final_components = loss_components(outputs, labels, statistics, earlier_weight=0.)
    gradients = gradient_diagnostics(model, final_components)
    assert gradients['activity']['0:score']['norm'] > 0
    assert gradients['activity']['1:score']['norm'] > 0
    assert gradients['channel']['0:activity']['norm'] > 0
    assert gradients['channel']['1:activity']['norm'] == 0
    # Verify the exact control gradient against autograd for every parameter.
    named = [(n, p) for n, p in model.named_parameters() if p.requires_grad]
    components = loss_components(outputs, labels, statistics)
    gh = torch.autograd.grad(components['channel'], [p for _, p in named],
                            retain_graph=True, allow_unused=True)
    ga = torch.autograd.grad(components['activity'], [p for _, p in named],
                            retain_graph=True, allow_unused=True)
    assign_gradients(model, components, bce_updates_score=False)
    control_errors = []
    for (name, p), h, a in zip(named, gh, ga):
        expected = h if '.score.' in name else (a if h is None else h if a is None else h + a)
        if expected is None:
            assert p.grad is None
        else:
            torch.testing.assert_close(p.grad, expected, rtol=1e-5, atol=1e-7)
            control_errors.append(float((p.grad - expected).abs().max()))
    del gh, ga, components, final_components, outputs, named
    optimizer.zero_grad(set_to_none=True)

    before = common.cpu_state(model)
    set_phase(model, optimizer, eligible, 1)
    adaptation = step(model, optimizer, positions[0])
    for name, value in model.state_dict().items():
        if name.startswith('layers.0.') and name != 'layers.0.c_beta':
            assert torch.equal(value.cpu(), before[name]), name
    assert optimizer.state[model.layers[0].c_beta]['step'] == 1
    assert model.layers[0].c_gamma not in optimizer.state
    assert model.layers[-1].c_beta not in optimizer.state
    del before
    set_phase(model, optimizer, eligible, 2)
    joint = step(model, optimizer, positions[0])
    assert optimizer.state[model.layers[0].c_gamma]['step'] == 1
    assert optimizer.state[model.layers[0].c_beta]['step'] == 2
    assert model.layers[-1].c_beta not in optimizer.state
    print('Actual cross-layer gradients, T10 routing and independent Adam steps passed.', flush=True)

    resume_folder = folder / 'discarded_resume_check'
    resume_folder.mkdir(exist_ok=True)
    # Exercise the real save routine, then compare the very next fused-Adam update.
    order = np.arange(len(cases))
    save_resume(resume_folder, model, optimizer, eligible, 2, 2, 1, order,
                dict(total=joint['loss']), [dict(epoch=0, selection_loss=1.)], 0, started)
    uninterrupted = step(model, optimizer, positions[1])
    expected = common.cpu_state(model)
    expected_steps = {n: float(optimizer.state[p]['step']) for n, p in model.named_parameters()
                      if p in optimizer.state}
    saved = torch.load(resume_folder / 'last.pt', map_location='cpu', weights_only=False, mmap=True)
    model.load_state_dict(saved['state'])
    optimizer.load_state_dict(saved['optimizer'])
    configure_execution(model, optimizer, common.CONFIG['execution'], 'cuda')
    set_phase(model, optimizer, set(saved['eligible']), saved['epoch'])
    restore_rng(saved['rng'])
    resumed = step(model, optimizer, positions[1])
    resume_max = 0.
    for name, value in model.state_dict().items():
        torch.testing.assert_close(value.cpu(), expected[name], rtol=1e-6, atol=1e-7)
        resume_max = max(resume_max, float((value.cpu() - expected[name]).abs().max()))
    assert {n: float(optimizer.state[p]['step']) for n, p in model.named_parameters()
            if p in optimizer.state} == expected_steps
    assert saved['cursor'] == 1 and np.array_equal(saved['order'], order)
    del saved, expected
    # Exercise complete evaluation serialization and final-only selection.
    class Subset:
        device = 'cuda'
        def __len__(self):
            return len(positions)
        def __getitem__(self, index):
            return cases[positions[index]]
    evaluated = evaluate(model, Subset(), statistics)
    assert abs(evaluated['summary']['selection_loss'] -
               evaluated['layer_summary'][-1]['selection_loss']) < 1e-8
    write(folder / 'evaluation_smoke.json', evaluated)
    del model, optimizer, public, labels, evaluated
    gc.collect()
    torch.cuda.empty_cache()
    print('Actual checkpoint/next-update equivalence and evaluation passed.', flush=True)

    torch.use_deterministic_algorithms(False)
    torch.backends.cudnn.benchmark = True
    model = make(7)
    optimizer, eligible = setup(model, 1)
    model.train()
    profiles = []
    torch.cuda.reset_peak_memory_stats()
    # All six physical profiles, including both maximum-K/Q combinations.
    for phase_epoch in (1, 2):
        set_phase(model, optimizer, eligible, phase_epoch)
        for position in positions:
            result = step(model, optimizer, position)
            profiles.append(dict(epoch=phase_epoch, **result))
        assert model.layers[-1].c_beta not in optimizer.state
        if phase_epoch == 2:
            assert any(r['score_forward_calls'] > 7 for r in profiles if r['epoch'] == 2)
        print(json.dumps(dict(stage='CAPACITY_CHECK', depth=7, phase=phase_epoch,
            peak_allocated_gib=torch.cuda.max_memory_allocated() / 2**30)), flush=True)
    memory = dict(peak_allocated_gib=torch.cuda.max_memory_allocated() / 2**30,
                  peak_reserved_gib=torch.cuda.max_memory_reserved() / 2**30,
                  free_gib=torch.cuda.mem_get_info()[0] / 2**30)
    assert memory['free_gib'] > .5
    del model, optimizer
    gc.collect()
    torch.cuda.empty_cache()
    manifest = read(TARGET / 'MANIFEST.json')
    for key in ('snapshot_hashes', 'bound_assets'):
        for path, digest in manifest[key].items():
            assert sha(path) == digest, path
    report = dict(status='PASSED', manifest_sha256=sha(TARGET / 'MANIFEST.json'),
        elapsed_seconds=time.time() - started, unit_test_output=unit.stdout.strip(),
        independent_layer_storage=True, common_awgn_initialization_verified=True,
        initial_probability_equals_public_prior=True, forward_parity=parity,
        actual_final_loss_gradients=gradients, gradient_control_max_error=max(control_errors),
        adaptation_update=adaptation, joint_update=joint,
        independent_calibration_adam_steps_verified=True,
        terminal_feedback_not_updated=True, resume_max_parameter_error=resume_max,
        resume_losses=[uninterrupted['loss'], resumed['loss']],
        scene_order_and_rng_restored=True, capacity_profiles=profiles, memory=memory,
        derivative_and_resume_comparison_execution='deterministic CUDA; production may differ in reduction roundoff',
        capacity_execution='production cuDNN benchmark and fused Adam',
        optimizer_updates_used_for_training=0, independent_test_used=False,
        actual_score_forward_calls_include_checkpoint_recomputation=True,
        scope='Implementation/capacity verification only; all updated models discarded.')
    write(folder / 'REPORT.json', report)
    write(TARGET / 'protocol/PREFLIGHT.json', dict(status='PASSED',
        manifest_sha256=sha(TARGET / 'MANIFEST.json'), report=str(folder / 'REPORT.json'),
        report_sha256=sha(folder / 'REPORT.json')))
    print(json.dumps(dict(status='PASSED', seconds=time.time() - started,
                          report=str(folder / 'REPORT.json'), memory=memory)), flush=True)


if __name__ == '__main__':
    main()
