"""Run the independent, newly trained score D-AMP receiver."""
import argparse
import json
from pathlib import Path
import sys
import torch
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from afdm_jadcedd.algorithm.diffusion_amp.receiver import DiffusionAMPReceiver, load_configuration


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--device', default='auto', choices=('auto', 'cpu', 'mps', 'cuda'))
    args = parser.parse_args()
    torch.set_num_threads(1)
    with threadpool_limits(1):
        receiver = DiffusionAMPReceiver(load_configuration(args.config), device=args.device)
        record = receiver.run(args.input, args.output)
    print(json.dumps({key: record[key] for key in ('status', 'method', 'iterations', 'seconds', 'inference_sha256')}))
    return 0 if record['status'] == 'COMPLETE' else 2


if __name__ == '__main__':
    raise SystemExit(main())
