"""Measure unchanged receiver inference and check optional CUDA graph execution."""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import cProfile
import json
from pathlib import Path
import pstats
import time
import numpy as np
import torch
from threadpoolctl import threadpool_limits
import evaluate_saved_baseline_inputs as paired


class GraphForward:
    """Cache the original frozen network forward by input shape, without padding."""
    def __init__(self, network):
        self.network = network
        self.cache = {}

    def __call__(self, x, variance):
        c = self.network.config
        expected = (len(x), 2, c.antennas, c.side, c.side)
        if tuple(x.shape) != expected or tuple(variance.shape) != (len(x),):
            raise ValueError('direct Cai AFDM score shape mismatch')
        if not variance.is_floating_point() or not bool(torch.all(torch.isfinite(variance) & (variance > 0))):
            raise ValueError('continuous scores require actual positive complex variances')
        # Keep the original validation before capture; capture only its unchanged tensor operations.
        def forward(a, v):
            return self.network.network(a.reshape(len(a), 2*c.antennas, c.side, c.side), v).reshape(expected)
        key = (tuple(x.shape), tuple(variance.shape), x.dtype)
        if key not in self.cache:
            sx, sv = x.clone(), variance.clone()
            stream = torch.cuda.Stream()
            stream.wait_stream(torch.cuda.current_stream())
            with torch.cuda.stream(stream):
                for _ in range(3):
                    forward(sx, sv)
            torch.cuda.current_stream().wait_stream(stream)
            graph = torch.cuda.CUDAGraph()
            with torch.cuda.graph(graph):
                output = forward(sx, sv)
            self.cache[key] = (sx, sv, graph, output)
        sx, sv, graph, output = self.cache[key]
        sx.copy_(x); sv.copy_(variance)
        graph.replay()
        return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('original', 'graph'), required=True)
    parser.add_argument('--job', default='cross_channel')
    parser.add_argument('--condition', type=int, default=0)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(1)
    plan = paired.read(paired.ROOT/'results/new_models_paired_20261019_v2'/args.job/'PLAN.json')
    paired.verify_sources(plan)
    index = paired.read(Path(plan['input_package'])/'inputs/INDEX.json')['experiments'][args.job]['cases']
    inputs, truth, hashes, proof, generation, phase = paired.load_case(plan, index, 0, args.condition)
    model = paired.EstimatedNoiseProposedReceiver(plan['experiment']['proposed_bundles']['proposed']['configuration'], device='cuda')
    if args.mode == 'graph':
        model.base.model.first = GraphForward(model.base.model.first)
        model.base.model.second = GraphForward(model.base.model.second)
    profile = cProfile.Profile()
    start = time.time()
    with threadpool_limits(1):
        profile.enable()
        prediction, record = model.infer(inputs)
        profile.disable()
    reference = paired.arrays(paired.ROOT/'results/new_models_paired_20261019_v2'/args.job/'scene000'/f'condition{args.condition:02d}'/'proposed.prediction.npz')
    checks = {}
    for name, value in prediction.items():
        ref = reference[name]
        checks[name] = dict(exact=bool(np.array_equal(value, ref)),
            max_absolute_error=float(np.max(np.abs(value.astype(complex)-ref.astype(complex)))))
    report = dict(mode=args.mode, job=args.job, condition=args.condition, seconds=record['seconds'],
        wall_seconds=time.time()-start, iterations=record['iterations'], stopping_reason=record['stopping_reason'],
        checks=checks, exact=all(c['exact'] for c in checks.values()),
        timing={key:sum(row[key] for row in record['trace']) for key in ('linear_seconds','score_seconds','classifier_seconds','prior_seconds')},
        peak_allocated_mib=torch.cuda.max_memory_allocated()/2**20)
    paired.save(args.output/'REPORT.json', report)
    paired.save(args.output/'record.json', record)
    paired.save_arrays(args.output/'prediction.npz', prediction)
    profile.dump_stats(str(args.output/'profile.pstats'))
    with (args.output/'profile.txt').open('w', encoding='utf-8') as stream:
        pstats.Stats(profile, stream=stream).strip_dirs().sort_stats('cumtime').print_stats(35)
    print(json.dumps(report), flush=True)
    if not report['exact']:
        raise ValueError('Candidate outputs differ from preserved reference; inspect before adoption')


if __name__ == '__main__':
    main()
