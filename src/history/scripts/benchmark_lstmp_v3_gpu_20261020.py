"""Check and time the proposed execution on a disposable paused checkpoint."""
import gc
import json
import time

import numpy as np
import torch
import check_lstmp_training_v3_implementation_20261020 as B
import experiments

experiments.__path__.append(str(B.ROOT / 'experiments'))
from experiments.lstmp_execution_v3_20261020.receiver import Receiver
from experiments.lstmp_execution_v3_20261020.data import Cases

OUT = B.ROOT / 'results/lstmp_v3_gpu_optimization_20261020'


def create(saved, fast, graphs, epoch=None):
    model = Receiver() if fast else B.Receiver()
    for _ in range(saved['depth']):
        model.add_layer(None)
    model.load_state_dict(saved['state'])
    model.cuda().train()
    eligible = set(saved['eligible'])
    optimizer = B.make_optimizer(model, B.common.CONFIG['receiver'], eligible, fused=True)
    optimizer.load_state_dict(saved['optimizer'])
    B.configure_execution(model, optimizer, B.common.CONFIG['execution'], 'cuda')
    B.set_phase(model, optimizer, eligible, saved['epoch'] if epoch is None else epoch)
    if fast:
        model.graphs_enabled = graphs
    return model, optimizer


def perform(model, optimizer, case, statistics, capture_grad=False):
    public, labels, _ = case
    optimizer.zero_grad(set_to_none=True)
    outputs, _ = model(public)
    terms = B.loss_components(outputs, labels, statistics)
    assert bool(torch.isfinite(terms['total']))
    B.assign_gradients(model, terms)
    gradients = ({n: p.grad.detach().cpu().clone() if p.grad is not None else None
                  for n, p in model.named_parameters()} if capture_grad else None)
    norm = float(B.clip_gradient_norm(model.parameters(), 1.))
    optimizer.step()
    return float(terms['total'].detach()), norm, gradients


def destroy(model, optimizer, cases=None):
    if isinstance(model, Receiver):
        model.clear_graphs()
    if isinstance(cases, Cases):
        cases.close()
    optimizer.zero_grad(set_to_none=True)


def main():
    assert B.read(B.TARGET / 'STATUS.json')['stage'] == 'PAUSED'
    source = B.TARGET / 'checkpoints/depth_1/last.pt'
    saved = torch.load(source, map_location='cpu', weights_only=False, mmap=True)
    statistics = B.read(B.TARGET / 'protocol/TRAINING_STATISTICS.json')
    scale = B.common.CONFIG['pretrained_score']['global_complex_rms']
    torch.set_num_threads(4)
    B.threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)
    numerical = {}
    cases = B.data.Cases('train', scale, 'cuda')
    fixed = cases[2]
    reference_state = reference_gradients = None
    for name, fast, graphs in (('reference', False, False), ('cuda_graph', True, True)):
        model, optimizer = create(saved, fast, graphs)
        loss, norm, gradients = perform(model, optimizer, fixed, statistics, True)
        state = B.common.cpu_state(model)
        if reference_state is None:
            reference_state, reference_gradients = state, gradients
            errors = dict(parameter_error=0., gradient_error=0.)
        else:
            errors = dict(parameter_error=0., gradient_error=0.)
            for key in state:
                torch.testing.assert_close(state[key], reference_state[key], rtol=1e-6, atol=1e-7)
                errors['parameter_error'] = max(errors['parameter_error'],
                    float((state[key] - reference_state[key]).abs().max()))
            for key, value in gradients.items():
                expected = reference_gradients[key]
                if expected is None:
                    assert value is None
                else:
                    torch.testing.assert_close(value, expected, rtol=1e-5, atol=1e-7)
                    errors['gradient_error'] = max(errors['gradient_error'], float((value-expected).abs().max()))
        numerical[name] = dict(loss=loss, gradient_norm=norm, **errors)
        destroy(model, optimizer)
        del model, optimizer, state, gradients
        gc.collect()
        torch.cuda.empty_cache()
        print(json.dumps(dict(stage='NUMERICAL', variant=name, **numerical[name])), flush=True)
    del reference_state, reference_gradients, fixed, cases
    gc.collect()
    torch.cuda.empty_cache()
    torch.use_deterministic_algorithms(False)
    torch.backends.cudnn.benchmark = True
    positions = saved['order'][saved['cursor']:saved['cursor']+32].tolist()
    variants = {}
    for name, fast, graphs, prefetch in (
        ('reference', False, False, False),
        ('fewer_host_transfers', True, False, False),
        ('cuda_graph', True, True, False),
        ('cuda_graph_prefetch', True, True, True),
        ('reference_repeat', False, False, False),
    ):
        model, optimizer = create(saved, fast, graphs)
        cases = Cases('train', scale, 'cuda') if prefetch else B.data.Cases('train', scale, 'cuda')
        rows = []
        torch.cuda.reset_peak_memory_stats()
        for cursor, position in enumerate(positions):
            torch.cuda.synchronize()
            start = time.perf_counter()
            if prefetch:
                cases.prefetch(positions[cursor:cursor+4])
            case = cases[position]
            ready = time.perf_counter()
            loss, norm, _ = perform(model, optimizer, case, statistics)
            torch.cuda.synchronize()
            end = time.perf_counter()
            if cursor >= 8:
                rows.append(dict(position=int(position), seconds=end-start, data_seconds=ready-start,
                                 users=case[2]['users'], frames=case[2]['frames'], loss=loss))
        variants[name] = dict(mean_seconds=float(np.mean([r['seconds'] for r in rows])),
            mean_data_seconds=float(np.mean([r['data_seconds'] for r in rows])),
            peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,
            graph_replays=getattr(model, 'graph_replays', 0),
            graph_captures=getattr(model, 'graph_capture_count', 0), rows=rows)
        B.write(OUT / 'ACCELERATION_PROGRESS.json', dict(numerical=numerical, variants=variants))
        print(json.dumps(dict(stage='TIMING', variant=name,
            **{k:v for k,v in variants[name].items() if k!='rows'})), flush=True)
        destroy(model, optimizer, cases)
        del model, optimizer, cases, case
        gc.collect()
        torch.cuda.empty_cache()
    B.write(OUT / 'ACCELERATION_BENCHMARK.json', dict(status='PASSED',
        source=str(source), source_sha256=B.sha(source), numerical=numerical, variants=variants,
        weights_discarded=True, updates_used_for_training=0, measured_depth=saved['depth']))


if __name__ == '__main__':
    main()
