"""Paired CUDA execution benchmarks from one saved training checkpoint."""
import argparse
from copy import deepcopy
import gc
import json
from pathlib import Path
import sys
import time
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from afdm_jadcedd.algorithm.proposed.network import load_direct_checkpoint
from afdm_jadcedd.experiment.training.scores.score_matching import make_cai_batch
from afdm_jadcedd.experiment.training.scores.direct_objectives import direct_first_loss


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    config = json.loads((args.run / 'training.json').read_text(encoding='utf-8'))
    state = torch.load(args.run / 'model/first/last.pt', map_location='cpu', weights_only=False)
    data = np.load(ROOT / config['data_files']['train'], mmap_mode='r')
    first = config['first']
    variants = [dict(name='original16', chunk=16, foreach=False, benchmark=False, threads=1),
                dict(name='batch32', chunk=32, foreach=True, benchmark=False, threads=1),
                dict(name='batch64', chunk=64, foreach=True, benchmark=False, threads=1),
                dict(name='batch64_autotune', chunk=64, foreach=True, benchmark=True, threads=1),
                dict(name='batch64_threads4', chunk=64, foreach=True, benchmark=True, threads=4)]
    report = dict(checkpoint=str(args.run / 'model/first/last.pt'),
        epoch=state['epoch'], steps=state['steps'], effective_batch=64, rng_chunk=16,
        precision='float32', criteria=dict(loss_relative=1e-5, gradient_relative=1e-3,
            optimizer_update_relative=1e-2), numerical={}, timing=[])
    (args.output/'CRITERIA.json').write_text(json.dumps(report, indent=2))

    def setup(variant):
        torch.set_num_threads(variant['threads'])
        torch.backends.cudnn.benchmark = variant['benchmark']
        model, _ = load_direct_checkpoint(ROOT / first['initial_checkpoint'], 'cuda')
        model.load_state_dict(state['model']); model.train()
        ema = deepcopy(model).eval()
        ema.load_state_dict(state['ema'])
        optimizer = torch.optim.Adam(model.parameters(), lr=first['learning_rate'])
        optimizer.load_state_dict(deepcopy(state['optimizer']))
        return model, ema, optimizer

    def draw(rng, step):
        offset = (state['cursor'] + step * 64) % (len(data)-64)
        selected = state['indices'][offset:offset+64]
        parts = [make_cai_batch(data[selected[i:i+16]], rng, config['scale']) for i in range(0,64,16)]
        return parts

    def update(model, ema, optimizer, variant, parts, collect=False):
        optimizer.zero_grad(set_to_none=True)
        losses = []
        for i in range(0, 64, variant['chunk']):
            group = parts[i//16:(i+variant['chunk'])//16]
            arrays = [np.concatenate([p[k] for p in group]) for k in range(4)]
            h, r, v, labels = [torch.as_tensor(a, device='cuda') for a in arrays]
            loss = direct_first_loss(model(r, labels), r, h, v)
            value = float(loss.detach().cpu())
            if not np.isfinite(value):
                raise FloatingPointError('Nonfinite benchmark loss')
            (loss * len(h)/64).backward()
            losses.append(value*len(h)/64)
        gradients = [p.grad.detach().cpu().clone() for p in model.parameters()] if collect else None
        torch.nn.utils.clip_grad_norm_(model.parameters(), first['gradient_clip'], error_if_nonfinite=True)
        optimizer.step()
        with torch.no_grad():
            if variant['foreach']:
                torch._foreach_lerp_(list(ema.parameters()), list(model.parameters()), 1-first['ema_decay'])
            else:
                for a, b in zip(ema.parameters(), model.parameters()):
                    a.lerp_(b, 1-first['ema_decay'])
        return sum(losses), gradients

    reference = None
    for variant in variants:
        model, ema, optimizer = setup(variant)
        rng = np.random.default_rng(); rng.bit_generator.state = deepcopy(state['rng'])
        value, gradients = update(model, ema, optimizer, variant, draw(rng,0), collect=True)
        params = [p.detach().cpu().clone() for p in model.parameters()]
        initial = [state['model'][name] for name, _ in model.named_parameters()]
        updates = [p-q for p,q in zip(params, initial)]
        if reference is None:
            reference = (value, gradients, updates)
        relative = lambda a,b: float(np.sqrt(sum(float((x-y).double().square().sum()) for x,y in zip(a,b)) / max(sum(float(y.double().square().sum()) for y in b), 1e-30)))
        measured = dict(loss=value, loss_relative=abs(value-reference[0])/abs(reference[0]),
            gradient_relative=relative(gradients, reference[1]), optimizer_update_relative=relative(updates, reference[2]))
        measured['pass'] = all(measured[k] <= limit for k,limit in report['criteria'].items())
        report['numerical'][variant['name']] = measured
        print(variant['name'], measured, flush=True)
        del model, ema, optimizer, gradients, params, updates
        gc.collect(); torch.cuda.empty_cache()

    for round_index in range(2):
        for variant in variants if round_index == 0 else list(reversed(variants)):
            model, ema, optimizer = setup(variant)
            rng = np.random.default_rng(); rng.bit_generator.state = deepcopy(state['rng'])
            for step in range(3):
                update(model, ema, optimizer, variant, draw(rng, step))
            torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
            started = time.perf_counter()
            for step in range(20):
                update(model, ema, optimizer, variant, draw(rng, step+3))
            torch.cuda.synchronize()
            row = dict(variant=variant, round=round_index,
                seconds_per_step=(time.perf_counter()-started)/20,
                peak_allocated_mib=torch.cuda.max_memory_allocated()/2**20)
            report['timing'].append(row)
            (args.output/'BENCHMARK.json').write_text(json.dumps(report, indent=2))
            print(json.dumps(row), flush=True)
            del model, ema, optimizer
            gc.collect(); torch.cuda.empty_cache()
    print('COMPLETE', flush=True)


if __name__ == '__main__':
    main()
