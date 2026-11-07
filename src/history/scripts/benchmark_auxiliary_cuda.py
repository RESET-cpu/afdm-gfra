"""Paired numerical checks and timings for auxiliary CUDA graph execution."""
import argparse
from copy import deepcopy
import gc
import json
import os
from pathlib import Path
import sys
import time
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from afdm_jadcedd.algorithm.proposed.network import load_direct_checkpoint
from afdm_jadcedd.algorithm.proposed.activity import Config, EvidenceNetwork
from afdm_jadcedd.experiment.training.proposed.auxiliary import complete_mean
from afdm_jadcedd.experiment.training.scores.direct_objectives import direct_second_loss
from afdm_jadcedd.experiment.training.scores.cuda_graph_auxiliary import AuxiliaryGraph, query_parts
from afdm_jadcedd.utils import sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--run', type=Path, default=ROOT/'runs/proposed_auxiliary_200_cuda_20261018')
    args = parser.parse_args()
    args.output.mkdir(exist_ok=False, parents=True)
    os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
    torch.set_num_threads(1)
    torch.backends.cudnn.benchmark = False
    config = json.loads((args.run/'n50000.json').read_text())
    prior = json.loads((ROOT/config['prior_definition']).read_text())
    data = np.load(ROOT/config['data_files']['train'], mmap_mode='r')
    state = torch.load(args.run/'n50000/second/last.pt', map_location='cpu', weights_only=False)
    first, _ = load_direct_checkpoint(ROOT/config['first_checkpoint'], 'cuda')
    first.eval().requires_grad_(False)
    report = dict(source_checkpoint_sha256=sha256(args.run/'n50000/second/last.pt'),
        first_sha256=sha256(ROOT/config['first_checkpoint']), numerical={}, timing=[],
        criteria=dict(loss_relative=1e-5, gradient_relative=1e-3, update_relative=1e-2, ema_relative=1e-5),
        original_microbatches=True, precision='float32; existing float64 activity mean retained')
    def save():
        (args.output/'BENCHMARK.json').write_text(json.dumps(report, indent=2))
    save()

    def setup(stage):
        settings = config[stage]
        if stage == 'second':
            model, _ = load_direct_checkpoint(ROOT/settings['initial_checkpoint'], 'cuda')
            model.load_state_dict(state['model'])
        else:
            blob = torch.load(ROOT/settings['initial_checkpoint'], map_location='cpu', weights_only=False)
            model = EvidenceNetwork(Config(**blob['config'])).cuda()
            model.load_state_dict(blob['state_dict'])
        model.train()
        ema = deepcopy(model).eval().requires_grad_(False)
        optimizer = torch.optim.Adam(model.parameters(), lr=settings['learning_rate'])
        if stage == 'second':
            ema.load_state_dict(state['ema'])
            optimizer.load_state_dict(deepcopy(state['optimizer']))
        rng = np.random.default_rng(settings['seed'])
        if stage == 'second':
            rng.bit_generator.state = deepcopy(state['rng'])
        return model, ema, optimizer, rng, AuxiliaryGraph(model, first, stage, settings['batch_size'])

    def step(bundle, stage, index, count, variant, collect=False):
        model, ema, optimizer, rng, graph = bundle
        settings = config[stage]
        chosen = np.arange(index*64, index*64+count)
        parts = query_parts(data, chosen, rng, prior, settings, stage)
        optimizer.zero_grad(set_to_none=True)
        if variant == 'graph':
            rows = graph.backward(parts)
        else:
            rows = []
            for part in parts:
                r, v = [torch.as_tensor(a, device='cuda') for a in part[:2]]
                if stage == 'second':
                    h = torch.as_tensor(part[2], device='cuda')
                    with torch.no_grad():
                        score = first(r, v)
                    loss = direct_second_loss(model(r, v), score, r, h, v[:, None, None, None])
                    n = len(r)
                else:
                    mean, _ = complete_mean(first, part[0], part[1], 'cuda')
                    features = torch.as_tensor(mean, device='cuda')
                    n = len(r)//2
                    labels = torch.cat((torch.ones(n, device='cuda'), torch.zeros(n, device='cuda')))
                    loss = torch.nn.functional.binary_cross_entropy_with_logits(model(r, v, features), labels)
                value = float(loss.detach().cpu())
                (loss*n/count).backward()
                rows.append((value, n))
        gradients = [p.grad.detach().cpu().clone() for p in model.parameters()] if collect else None
        before = [p.detach().cpu().clone() for p in model.parameters()] if collect else None
        torch.nn.utils.clip_grad_norm_(model.parameters(), settings['gradient_clip'], error_if_nonfinite=True)
        optimizer.step()
        with torch.no_grad():
            if variant == 'graph':
                torch._foreach_lerp_(list(ema.parameters()), list(model.parameters()), 1-settings['ema_decay'])
            else:
                for a, b in zip(ema.parameters(), model.parameters()):
                    a.lerp_(b, 1-settings['ema_decay'])
        assert all(p.grad is None for p in first.parameters())
        if collect:
            return (sum(v*n for v,n in rows)/count, gradients,
                    [p.detach().cpu()-b for p,b in zip(model.parameters(), before)],
                    [p.detach().cpu().clone() for p in ema.parameters()], deepcopy(rng.bit_generator.state))

    def relative(a, b):
        return float(np.sqrt(sum(float((x-y).double().square().sum()) for x,y in zip(a,b)) /
            max(sum(float(y.double().square().sum()) for y in b), 1e-30)))

    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.deterministic = True
    for stage in ('second', 'activity'):
        reference = []
        counts = [config[stage]['batch_size'], 16, 8, config[stage]['batch_size']]
        report['numerical'][stage] = {}
        for variant in ('reference', 'repeat', 'graph'):
            bundle = setup(stage)
            checks = []
            for index, count in enumerate(counts):
                actual = step(bundle, stage, index, count, variant, True)
                if variant == 'reference':
                    reference.append(actual)
                expected = reference[index]
                row = dict(batch=count, loss=actual[0],
                    loss_relative=abs(actual[0]-expected[0])/max(abs(expected[0]), 1e-30),
                    gradient_relative=relative(actual[1], expected[1]),
                    update_relative=relative(actual[2], expected[2]), ema_relative=relative(actual[3], expected[3]),
                    rng_equal=actual[4] == expected[4])
                row['pass'] = row['rng_equal'] and all(row[k] <= v for k,v in report['criteria'].items())
                checks.append(row)
                print(stage, variant, row, flush=True)
            report['numerical'][stage][variant] = checks
            save()
            del bundle, actual
            gc.collect(); torch.cuda.empty_cache()
        del reference
        gc.collect()

    torch.use_deterministic_algorithms(False)
    torch.backends.cudnn.deterministic = False
    for stage in ('second', 'activity'):
        for round_index in range(2):
            for variant in (('reference', 'graph') if round_index == 0 else ('graph', 'reference')):
                bundle = setup(stage)
                for index in range(3):
                    step(bundle, stage, index, config[stage]['batch_size'], variant)
                torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
                started = time.perf_counter()
                for index in range(20):
                    step(bundle, stage, index+3, config[stage]['batch_size'], variant)
                torch.cuda.synchronize()
                row = dict(stage=stage, variant=variant, round=round_index,
                    seconds_per_update=(time.perf_counter()-started)/20,
                    peak_allocated_mib=torch.cuda.max_memory_allocated()/2**20)
                report['timing'].append(row); save(); print(row, flush=True)
                del bundle
                gc.collect(); torch.cuda.empty_cache()
    report['all_numerical_checks_pass'] = all(row['pass'] for variants in report['numerical'].values()
        for rows in variants.values() for row in rows)
    report['frozen_first_unchanged'] = sha256(ROOT/config['first_checkpoint']) == report['first_sha256']
    save()
    if not report['all_numerical_checks_pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
