#!/usr/bin/env python3
"""Run independent AMP with query and output damping and matched history."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
import torch
from threadpoolctl import threadpool_limits
from afdm_jadcedd.algorithm.score_amp_query_damped.receiver import QueryDampedScoreAMPReceiver, load_configuration


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--config')
    p.add_argument('--device', choices=['auto', 'cpu', 'mps'], default='auto')
    p.add_argument('--damping', type=float)
    p.add_argument('--query-damping', type=float)
    p.add_argument('--iterations', type=int)
    p.add_argument('--without-onsager', action='store_true')
    args = p.parse_args()
    c = load_configuration(args.config)
    for field in ('damping', 'query_damping', 'iterations'):
        value = getattr(args, field)
        if value is not None:
            c['solver'][field] = value
    if args.without_onsager:
        c['solver']['onsager'] = False
    torch.set_num_threads(1)
    with threadpool_limits(limits=1):
        record = QueryDampedScoreAMPReceiver(c, device=args.device).run(args.input, args.output)
    print(json.dumps({key:record[key] for key in
        ('method','status','iterations','stopping_reason','error','seconds','joint_denoiser_evaluations')}, indent=2))
    return 0 if record['status'] == 'COMPLETE' else 2


if __name__ == '__main__':
    raise SystemExit(main())
