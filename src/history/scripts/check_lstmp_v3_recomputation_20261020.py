"""Pair actual receiver outputs/gradients with checkpointing off/on; no updates."""
import gc
import shutil
import time
from collections import Counter
from pathlib import Path

import torch

import check_lstmp_training_v3_implementation_20261020 as check


def main():
    target = check.TARGET
    if (target / 'TRAINING_LAUNCH.json').exists():
        raise RuntimeError('Run this verification before launching training')
    report = check.read(target / 'preflight/REPORT.json')
    assert report['status'] == 'PASSED'
    assert report['manifest_sha256'] == check.sha(target / 'MANIFEST.json')
    preflight = check.read(target / 'protocol/PREFLIGHT.json')
    saved_path = Path(preflight['report']).parent / 'discarded_depth10_checkpoint/last.pt'
    saved = torch.load(saved_path, map_location='cpu', weights_only=False, mmap=True)
    output = target / 'preflight' / time.strftime('recomputation_%Y%m%d_%H%M%S')
    output.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, output / Path(__file__).name)
    statistics = check.read(target / 'protocol/TRAINING_STATISTICS.json')
    cases = check.data.Cases('train', check.common.CONFIG['pretrained_score']['global_complex_rms'], 'cuda')
    torch.set_num_threads(4)
    check.threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32 = check.common.CONFIG['allow_tf32']
    torch.backends.cudnn.allow_tf32 = check.common.CONFIG['allow_tf32']
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)
    results = []
    for depth, positions in ((6, [9]), (10, [2, 14])):
        model = check.Receiver()
        for _ in range(depth):
            model.add_layer(None)
        model.load_state_dict({name: value for name, value in saved['state'].items()
                               if int(name.split('.')[1]) < depth})
        model.cuda()
        model.layers[-1].c_beta.requires_grad_(False)
        eligible = check.eligible_parameters(model)
        optimizer = check.make_optimizer(model, check.common.CONFIG['receiver'], eligible, fused=True)
        check.configure_execution(model, optimizer, check.common.CONFIG['execution'], 'cuda')
        check.set_phase(model, optimizer, eligible, 2)
        stochastic_or_running_stats = [
            name for name, module in model.named_modules()
            if getattr(module, 'track_running_stats', False)
            or (isinstance(module, torch.nn.modules.dropout._DropoutNd) and module.p > 0)
        ]
        assert not stochastic_or_running_stats, stochastic_or_running_stats
        buffers = {name: value.detach().cpu().clone() for name, value in model.named_buffers()}
        for position in positions:
            public, labels, info = cases[position]
            reference = None
            record = dict(depth=depth, position=position, condition=info,
                          stateful_or_stochastic_modules=stochastic_or_running_stats,
                          module_types=dict(Counter(type(m).__name__ for m in model.modules())))
            for recompute in (False, True):
                model.use_checkpoint = False
                model.checkpoint_first_layers = depth if recompute else 0
                model.checkpoint_min_users = 1
                model.zero_grad(set_to_none=True)
                torch.cuda.empty_cache()
                torch.cuda.reset_peak_memory_stats()
                model.train()
                rng = torch.cuda.get_rng_state().clone()
                calls = model.score_evaluations
                outputs, _ = model(public)
                components = check.loss_components(outputs, labels, statistics)
                values = [{key: value.detach().cpu() for key, value in row.items()} for row in outputs]
                losses = {key: float(components[key].detach()) for key in ('channel', 'activity', 'total')}
                check.assign_gradients(model, components)
                assert torch.equal(rng, torch.cuda.get_rng_state())
                for name, value in model.named_buffers():
                    assert torch.equal(value.cpu(), buffers[name]), name
                if not recompute:
                    reference = {name: p.grad.detach().cpu().clone() if p.grad is not None else None
                                 for name, p in model.named_parameters()}
                    reference_values, reference_losses = values, losses
                else:
                    max_output_error = 0.
                    for actual_row, expected_row in zip(values, reference_values):
                        for key in actual_row:
                            torch.testing.assert_close(actual_row[key], expected_row[key],
                                                       rtol=1e-6, atol=1e-7)
                            max_output_error = max(max_output_error,
                                float((actual_row[key] - expected_row[key]).abs().max()))
                    assert losses == reference_losses
                    max_gradient_error, delta_sq, reference_sq = 0., 0., 0.
                    for name, parameter in model.named_parameters():
                        expected = reference[name]
                        if expected is None:
                            assert parameter.grad is None
                            continue
                        actual = parameter.grad.detach().cpu()
                        torch.testing.assert_close(actual, expected, rtol=1e-5, atol=1e-7,
                                                   msg=lambda msg, n=name: f'{n}: {msg}')
                        delta = actual.double() - expected.double()
                        max_gradient_error = max(max_gradient_error, float(delta.abs().max()))
                        delta_sq += float(delta.square().sum())
                        reference_sq += float(expected.double().square().sum())
                    record.update(maximum_output_error=max_output_error,
                        maximum_gradient_error=max_gradient_error,
                        relative_gradient_l2=(delta_sq / max(reference_sq, 1e-30)) ** .5,
                        losses=losses, buffers_unchanged=True, rng_unchanged=True)
                record['on' if recompute else 'off'] = dict(
                    score_calls_including_backward=model.score_evaluations - calls,
                    peak_allocated_gib=torch.cuda.max_memory_allocated() / 2**30)
                del outputs, components, values
                model.zero_grad(set_to_none=True)
            # Inference has no backward pass and must call each score once.
            model.eval()
            inference_reference = None
            inference_max = 0.
            with torch.no_grad():
                for recompute in (False, True):
                    model.checkpoint_first_layers = depth if recompute else 0
                    calls = model.score_evaluations
                    outputs, _ = model(public)
                    assert model.score_evaluations - calls == depth
                    values = [{key: value.cpu() for key, value in row.items()} for row in outputs]
                    if inference_reference is None:
                        inference_reference = values
                    else:
                        for actual, expected in zip(values, inference_reference):
                            for key in actual:
                                torch.testing.assert_close(actual[key], expected[key], rtol=0., atol=0.)
                                inference_max = max(inference_max, float((actual[key] - expected[key]).abs().max()))
                    del outputs
            record.update(inference_maximum_error=inference_max, inference_score_calls=depth)
            results.append(record)
            check.write(output / 'PROGRESS.json', results)
            print(f'Checkpoint equivalence passed: depth={depth}, position={position}, '
                  f'output_error={record["maximum_output_error"]}, '
                  f'gradient_error={record["maximum_gradient_error"]}', flush=True)
            del reference, reference_values, public, labels
            gc.collect()
        del model, optimizer
        gc.collect()
        torch.cuda.empty_cache()
    result = dict(status='PASSED', manifest_sha256=check.sha(target / 'MANIFEST.json'),
        source_checkpoint=str(saved_path), source_checkpoint_sha256=check.sha(saved_path),
        script_sha256=check.sha(Path(__file__)), cases=results, parameter_updates=0,
        scope='Paired outputs, all parameter gradients, buffer/RNG state and inference call count. '
              'Deterministic CUDA with configured TF32; no long-run accuracy claim.',
        numerical_tolerance=dict(outputs_rtol=1e-6, outputs_atol=1e-7,
                                 gradients_rtol=1e-5, gradients_atol=1e-7))
    check.write(output / 'REPORT.json', result)
    check.write(target / 'preflight/RECOMPUTATION_EQUIVALENCE.json', result)
    print(f'All paired checks passed: {output / "REPORT.json"}', flush=True)


if __name__ == '__main__':
    main()
