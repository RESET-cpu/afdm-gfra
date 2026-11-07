"""Compare execution paths from a saved checkpoint, without changing that run."""
from copy import deepcopy
import argparse
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
from afdm_jadcedd.experiment.training.scores.cuda_execution import execution_batches
from afdm_jadcedd.experiment.training.scores.cuda_graph_first import FirstGraph
from afdm_jadcedd.experiment.training.scores.score_matching import make_cai_batch
from afdm_jadcedd.experiment.training.scores.direct_objectives import direct_first_loss


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--deterministic', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(exist_ok=True, parents=True)
    config = json.loads((args.run/'training.json').read_text())
    settings = config['first']
    state = torch.load(args.run/'model/first/last.pt', map_location='cpu', weights_only=False)
    data = np.load(ROOT/config['data_files']['train'], mmap_mode='r')
    torch.set_num_threads(1)
    if args.deterministic:
        os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
        torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = args.deterministic
    report = dict(checkpoint=str(args.run/'model/first/last.pt'), epoch=state['epoch'], steps=state['steps'],
        criteria=dict(loss_relative=1e-5, gradient_relative=1e-3, optimizer_update_relative=1e-2, ema_relative=1e-5),
        numerical={}, timing=[], effective_batch=64, draw_size=16, precision='unchanged',
        deterministic_validation=args.deterministic)
    save = lambda: (args.output/'BENCHMARK.json').write_text(json.dumps(report, indent=2))
    save()

    def setup():
        model, _ = load_direct_checkpoint(ROOT/settings['initial_checkpoint'], 'cuda')
        model.load_state_dict(state['model']); model.train()
        ema = deepcopy(model).eval(); ema.load_state_dict(state['ema'])
        optimizer = torch.optim.Adam(model.parameters(), lr=settings['learning_rate'])
        optimizer.load_state_dict(deepcopy(state['optimizer']))
        rng = np.random.default_rng(); rng.bit_generator.state = deepcopy(state['rng'])
        return model, ema, optimizer, rng, FirstGraph(model, 64)

    def update(bundle, variant, step, count=64, collect=False):
        model, ema, optimizer, rng, graph = bundle
        offset = (state['cursor'] + step*64) % (len(data)-64)
        chosen = state['indices'][offset:offset+count]
        arrays = next(execution_batches(data, chosen, rng, config['scale'],
            make_cai_batch, draw_size=16, execution_size=64))
        optimizer.zero_grad(set_to_none=True)
        if variant.startswith('current'):
            h, r, v, labels = [torch.as_tensor(a, device='cuda') for a in arrays]
            loss = direct_first_loss(model(r, labels), r, h, v)
            value = float(loss.detach().cpu())
            (loss*len(h)/len(chosen)).backward()
        else:
            value = graph.backward(arrays, use_graph=variant=='graph')/count
        gradients = [p.grad.detach().cpu().clone() for p in model.parameters()] if collect else None
        torch.nn.utils.clip_grad_norm_(model.parameters(), settings['gradient_clip'], error_if_nonfinite=True)
        optimizer.step()
        with torch.no_grad():
            torch._foreach_lerp_(list(ema.parameters()), list(model.parameters()), 1-settings['ema_decay'])
        if not collect:
            return
        initial = [state['model'][n] for n,p in model.named_parameters()]
        updates = [p.detach().cpu()-q for p,q in zip(model.parameters(), initial)]
        return value, gradients, updates, [p.detach().cpu().clone() for p in ema.parameters()]

    def relative(a,b):
        return float(np.sqrt(sum(float((x-y).double().square().sum()) for x,y in zip(a,b)) /
            max(sum(float(y.double().square().sum()) for y in b), 1e-30)))

    reference = []
    for variant in ('current','current_repeat','host_checks','graph'):
        bundle = setup()
        checks = []
        for step, count in enumerate([64,64,64,16,64]):
            actual = update(bundle, variant, step, count, True)
            if variant == 'current':
                reference.append(actual)
            expected = reference[step]
            row = dict(step=step, batch=count, loss=actual[0],
                loss_relative=abs(actual[0]-expected[0])/abs(expected[0]),
                gradient_relative=relative(actual[1],expected[1]),
                optimizer_update_relative=relative(actual[2],expected[2]), ema_relative=relative(actual[3],expected[3]))
            row['pass'] = all(row[k] <= limit for k,limit in report['criteria'].items())
            checks.append(row)
        report['numerical'][variant] = checks
        print(variant, checks, flush=True); save()
        del bundle, actual
        gc.collect(); torch.cuda.empty_cache()
    for round_index in range(2):
        variants = ('current','host_checks','graph') if round_index == 0 else ('graph','host_checks','current')
        for variant in variants:
            bundle = setup()
            for step in range(3):
                update(bundle,variant,step)
            torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
            start = time.perf_counter()
            for step in range(30):
                update(bundle,variant,step+3)
            torch.cuda.synchronize()
            row = dict(variant=variant, round=round_index, seconds_per_step=(time.perf_counter()-start)/30,
                peak_allocated_mib=torch.cuda.max_memory_allocated()/2**20)
            report['timing'].append(row); print(row,flush=True); save()
            del bundle
            gc.collect(); torch.cuda.empty_cache()


if __name__ == '__main__':
    main()
