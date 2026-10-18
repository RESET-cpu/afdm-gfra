#!/usr/bin/env python3
"""Run the separate frozen-score AMP candidate or its Onsager ablation."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
import torch
from threadpoolctl import threadpool_limits
from afdm_jadcedd.algorithm.score_amp.receiver import ScoreAMPReceiver, load_configuration


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--config')
    p.add_argument('--device', choices=['auto', 'cpu', 'mps'], default='auto')
    p.add_argument('--without-onsager', action='store_true')
    args = p.parse_args()
    configuration = load_configuration(args.config)
    if args.without_onsager:
        configuration['solver']['onsager'] = False
    torch.set_num_threads(1)
    with threadpool_limits(limits=1):
        record = ScoreAMPReceiver(configuration, device=args.device).run(args.input, args.output)
    print(json.dumps({k: record[k] for k in ('method', 'status', 'iterations', 'stopping_reason',
        'error', 'seconds', 'joint_denoiser_evaluations')}, indent=2))
    return 0 if record['status'] == 'COMPLETE' else 2


if __name__ == '__main__':
    raise SystemExit(main())
