"""Run the independent full-user D-AMP receiver on public input only."""
import argparse
from pathlib import Path
import sys
import json
import torch
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from afdm_jadcedd.algorithm.joint_amp.receiver import JointAMPReceiver, load_configuration


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--config')
    parser.add_argument('--device', default='auto', choices=['auto', 'cpu', 'mps'])
    args = parser.parse_args()
    torch.set_num_threads(1)
    with threadpool_limits(limits=1):
        result = JointAMPReceiver(load_configuration(args.config), device=args.device).run(args.input, args.output)
    print(json.dumps({key: result[key] for key in ('method', 'status', 'iterations', 'seconds', 'failure')}, ensure_ascii=False))
    if result['status'] != 'COMPLETE':
        raise SystemExit(2)


if __name__ == '__main__':
    main()
