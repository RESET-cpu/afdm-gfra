#!/usr/bin/env python3
"""Run the independent frozen-score AMP with matched mean/residual damping."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
import torch
from threadpoolctl import threadpool_limits
from afdm_jadcedd.algorithm.score_amp_damped.receiver import DampedScoreAMPReceiver, load_configuration


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--config')
    p.add_argument('--device', choices=['auto', 'cpu', 'mps'], default='auto')
    p.add_argument('--damping', type=float)
    p.add_argument('--iterations', type=int)
    p.add_argument('--without-onsager', action='store_true')
    args = p.parse_args()
    c = load_configuration(args.config)
    if args.damping is not None:
        c['solver']['damping'] = args.damping
    if args.iterations is not None:
        c['solver']['iterations'] = args.iterations
    if args.without_onsager:
        c['solver']['onsager'] = False
    torch.set_num_threads(1)
    with threadpool_limits(limits=1):
        record = DampedScoreAMPReceiver(c, device=args.device).run(args.input, args.output)
    print(json.dumps({k:record[k] for k in ('method', 'status', 'iterations', 'stopping_reason',
        'error', 'seconds', 'joint_denoiser_evaluations')}, indent=2))
    return 0 if record['status'] == 'COMPLETE' else 2


if __name__ == '__main__':
    raise SystemExit(main())
