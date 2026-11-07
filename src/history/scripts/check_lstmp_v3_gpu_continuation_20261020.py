"""Verify an execution continuation on actual shallow/deep receiver updates."""
import gc
import json
import os
import subprocess
import sys
import time

from prepare_lstmp_v3_gpu_continuation_20261020 import ROOT, SOURCE, TARGET, PACKAGE, read, write, sha

os.environ['AFDM_LSTMP_ROOT'] = str(ROOT)
os.environ['AFDM_LSTMP_CONFIG'] = str(TARGET / f'source_code/experiments/{PACKAGE}/config.json')
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
sys.path.insert(0, str(TARGET / 'source_code'))

import numpy as np
import torch
from threadpoolctl import threadpool_limits
from experiments.lstmp_candidate_20261019.common import CONFIG, cpu_state
from experiments.lstmp_candidate_20261019.execution import configure_execution
from experiments.lstmp_candidate_20261019.optimization import clip_gradient_norm
from experiments.lstmp_training_v2_20261020.optimization import (
    eligible_parameters, make_optimizer, set_phase, restore_rng, gradient_diagnostics)
from experiments.lstmp_training_v2_20261020.objectives import loss_components, assign_gradients
from experiments.lstmp_training_v2_20261020.receiver import Receiver as ReferenceReceiver
from experiments.lstmp_training_v2_20261020.evaluation import evaluate
from experiments.lstmp_training_v3_20261020.data import Cases as ReferenceCases
from experiments.lstmp_execution_v3_20261020.receiver import Receiver
from experiments.lstmp_execution_v3_20261020.data import Cases
from experiments.lstmp_execution_v3_20261020.train import save_resume


def make(saved, fast, epoch=None):
    model = Receiver() if fast else ReferenceReceiver()
    for _ in range(saved['depth']):
        model.add_layer(None)
    model.load_state_dict(saved['state'])
    model.cuda().train()
    eligible = set(saved['eligible'])
    optimizer = make_optimizer(model, CONFIG['receiver'], eligible, fused=True)
    optimizer.load_state_dict(saved['optimizer'])
    configure_execution(model, optimizer, CONFIG['execution'], 'cuda')
    set_phase(model, optimizer, eligible, saved['epoch'] if epoch is None else epoch)
    if fast:
        model.graphs_enabled = True
    restore_rng(saved['rng'])
    return model, optimizer, eligible


def step(model, optimizer, case, statistics, gradients=False):
    public, labels, info = case
    optimizer.zero_grad(set_to_none=True)
    outputs, _ = model(public)
    components = loss_components(outputs, labels, statistics)
    assert bool(torch.isfinite(components['total']))
    assign_gradients(model, components)
    copied = ({n: p.grad.detach().cpu().clone() if p.grad is not None else None
               for n, p in model.named_parameters()} if gradients else None)
    norm = float(clip_gradient_norm(model.parameters(), 1.))
    optimizer.step()
    return dict(loss=float(components['total'].detach()), gradient_norm=norm, info=info), copied


def dispose(model, optimizer):
    if isinstance(model, Receiver):
        model.clear_graphs()
    optimizer.zero_grad(set_to_none=True)


def main():
    started = time.time()
    assert not (TARGET / 'TRAINING_LAUNCH.json').exists()
    folder = TARGET / 'preflight' / time.strftime('attempt_%Y%m%d_%H%M%S')
    folder.mkdir(parents=True)
    unit = subprocess.run([sys.executable, '-m', 'pytest', '-q',
                           str(ROOT / 'tests/test_lstmp_training_v2.py'),
                           str(ROOT / 'tests/test_lstmp_training_v3.py')],
                          cwd=ROOT, capture_output=True, text=True)
    (folder / 'unit_tests.txt').write_text(unit.stdout + unit.stderr, encoding='utf-8')
    assert unit.returncode == 0, unit.stdout + unit.stderr
    torch.set_num_threads(CONFIG['cpu_threads'])
    threadpool_limits(CONFIG['cpu_threads'])
    torch.backends.cuda.matmul.allow_tf32 = CONFIG['allow_tf32']
    torch.backends.cudnn.allow_tf32 = CONFIG['allow_tf32']
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)
    statistics = read(TARGET / 'protocol/TRAINING_STATISTICS.json')
    scale = CONFIG['pretrained_score']['global_complex_rms']
    current = TARGET / 'checkpoints/depth_1/last.pt'
    original_digest = sha(current)
    saved = torch.load(current, map_location='cpu', weights_only=False, mmap=True)
    assert saved['cursor'] == saved['completed_updates'] == 3159
    assert saved['epoch'] == saved['depth'] == 1
    assert original_digest == CONFIG['execution_continuation']['source_checkpoint_sha256']
    parent_config = read(SOURCE / 'MANIFEST.json')['configuration']
    comparison = dict(CONFIG)
    comparison['run_directory'] = parent_config['run_directory']
    del comparison['execution_acceleration'], comparison['execution_continuation']
    assert comparison == parent_config
    cases, prefetched = ReferenceCases('train', scale, 'cuda'), Cases('train', scale, 'cuda')
    order = list(range(19))
    for cursor, position in enumerate(order):
        prefetched.prefetch(order[cursor:cursor+4])
        reference, actual = cases[position], prefetched[position]
        assert reference[2] == actual[2]
        for a, b in zip(reference[:2], actual[:2]):
            assert set(a) == set(b)
            for key in a:
                if isinstance(a[key], torch.Tensor):
                    assert torch.equal(a[key], b[key]), key
                elif key != 'physical_input':
                    assert a[key] == b[key]
    prefetched.close()
    print('All nineteen prefetched scenes exactly match the frozen data loader.', flush=True)

    def paired(saved_state, positions, key):
        expected_state = expected_gradients = None
        comparison = {}
        for fast in (False, True):
            model, optimizer, _ = make(saved_state, fast)
            rows = []
            for index, position in enumerate(positions):
                row, gradients = step(model, optimizer, cases[position], statistics,
                                      gradients=index == len(positions)-1)
                rows.append(row)
            state = cpu_state(model)
            if not fast:
                expected_state, expected_gradients = state, gradients
                expected_rows = rows
                comparison['reference'] = rows
            else:
                max_parameter_error = max_gradient_error = 0.
                for name in state:
                    torch.testing.assert_close(state[name], expected_state[name], rtol=1e-6, atol=1e-7)
                    max_parameter_error = max(max_parameter_error,
                        float((state[name]-expected_state[name]).abs().max()))
                for name, actual in gradients.items():
                    expected = expected_gradients[name]
                    if expected is None:
                        assert actual is None
                    else:
                        torch.testing.assert_close(actual, expected, rtol=1e-5, atol=1e-7)
                        max_gradient_error = max(max_gradient_error, float((actual-expected).abs().max()))
                torch.testing.assert_close(torch.tensor([r['loss'] for r in rows]),
                    torch.tensor([r['loss'] for r in expected_rows]), rtol=1e-6, atol=1e-7)
                assert model.graph_replays > 0
                comparison.update(accelerated=rows, maximum_parameter_error=max_parameter_error,
                    maximum_gradient_error=max_gradient_error, graph_replays=model.graph_replays)
            dispose(model, optimizer)
            del model, optimizer, state, gradients
            gc.collect()
            torch.cuda.empty_cache()
        write(folder / f'{key}.json', comparison)
        print(json.dumps(dict(stage='NUMERICAL', case=key,
            parameter_error=comparison['maximum_parameter_error'],
            gradient_error=comparison['maximum_gradient_error'])), flush=True)
        return comparison

    # Exact next scene order from the real saved training checkpoint.
    shallow = paired(saved, saved['order'][3159:3165].tolist(), 'six_next_updates')
    parent_preflight = read(SOURCE / 'protocol/PREFLIGHT.json')
    depth10_path = Path(parent_preflight['report']).parent / 'discarded_depth10_checkpoint/last.pt'
    deep = torch.load(depth10_path, map_location='cpu', weights_only=False, mmap=True)
    deep_comparison = paired(deep, [2], 'depth10_joint_update')
    torch.use_deterministic_algorithms(False)
    torch.backends.cudnn.benchmark = True
    model, optimizer, eligible = make(deep, True, epoch=1)
    torch.cuda.reset_peak_memory_stats()
    capacity = []
    for epoch in (1, 2):
        model.clear_graphs()
        optimizer.zero_grad(set_to_none=True)
        gc.collect()
        torch.cuda.empty_cache()
        set_phase(model, optimizer, eligible, epoch)
        model.train()
        for position in range(19):
            row, _ = step(model, optimizer, cases[position], statistics)
            capacity.append(dict(epoch=epoch, **row))
        print(json.dumps(dict(stage='CAPACITY', depth=10, epoch=epoch,
            graph_replays=model.graph_replays,
            peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30)), flush=True)
    optimizer.zero_grad(set_to_none=True)
    with model.eager():
        public, labels, _ = cases[9]
        outputs, _ = model(public)
        measured = gradient_diagnostics(model, loss_components(outputs, labels, statistics))
        del outputs, public, labels
    optimizer.zero_grad(set_to_none=True)

    class Subset:
        device = 'cuda'
        def __len__(self):
            return 19
        def __getitem__(self, index):
            return cases[index]

    replay_before = model.graph_replays
    evaluation = evaluate(model, Subset(), statistics)
    assert model.graph_replays == replay_before
    assert np.isfinite(evaluation['summary']['selection_loss'])
    write(folder / 'depth10_evaluation.json', evaluation)
    checkpoint_dir = folder / 'discarded_checkpoint'
    checkpoint_dir.mkdir()
    inherited_active_time = read(TARGET / 'ACTIVE_TIME.json')
    try:
        save_resume(checkpoint_dir, model, optimizer, eligible, 10, 2, 1,
                    np.arange(len(cases)), dict(total=capacity[-1]['loss']),
                    [dict(epoch=0, selection_loss=1.)], 0, started)
    finally:
        # The real save routine also writes run-level time. A disposable
        # capacity checkpoint must not replace the inherited training clock.
        write(TARGET / 'ACTIVE_TIME.json', inherited_active_time)
    memory = dict(peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,
                  peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30,
                  free_gib=torch.cuda.mem_get_info()[0]/2**30)
    write(folder / 'CAPACITY.json', dict(memory=memory, rows=capacity))
    assert memory['free_gib'] > .5
    dispose(model, optimizer)
    del model, optimizer, deep, saved, cases
    gc.collect()
    torch.cuda.empty_cache()
    manifest = read(TARGET / 'MANIFEST.json')
    for group in ('snapshot_hashes', 'bound_assets'):
        for path, digest in manifest[group].items():
            assert sha(path) == digest, path
    assert sha(current) == original_digest
    assert sha(SOURCE / 'checkpoints/depth_1/last.pt') == original_digest
    report = dict(status='PASSED', manifest_sha256=sha(TARGET / 'MANIFEST.json'),
        elapsed_seconds=time.time()-started, unit_test_output=unit.stdout.strip(),
        source_checkpoint_preserved=True, source_updates=3159,
        training_plan_and_optimizer_preserved=True, prefetched_data_exact_all_conditions=True,
        next_six_updates=shallow, depth10_joint_update=deep_comparison,
        depth10_capacity=capacity, memory=memory, per_loss_gradients=measured,
        evaluation_uses_original_score_forward=True, full_depth_checkpoint_saved=True,
        numerical_checks='deterministic CUDA; capacity uses original production settings',
        benchmark_updates_used_for_training=0, formal_test_used=False)
    write(folder / 'REPORT.json', report)
    write(TARGET / 'preflight/REPORT.json', report)
    write(TARGET / 'protocol/PREFLIGHT.json', dict(status='PASSED',
        manifest_sha256=sha(TARGET / 'MANIFEST.json'), report=str(folder/'REPORT.json'),
        report_sha256=sha(folder/'REPORT.json')))
    print(json.dumps(dict(status='PASSED', memory=memory, report=str(folder/'REPORT.json'))), flush=True)


if __name__ == '__main__':
    from pathlib import Path
    main()
