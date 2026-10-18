"""Run the recorded joint L-DAMP training stages with explicit output paths.

The stage implementations retain their original seeds, data sampling, losses,
checkpoint selection and full optimizer/RNG resume state. The low and refine
stages use MPS, matching the recorded experiments. See docs/LDAMP_JOINT.md.
"""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def command(args):
    folder = ROOT / 'experiments/ldamp_complete_20261015'
    script = {'prepare': 'train.py', 'high': 'train.py',
              'refine': 'refine.py', 'low': 'train_residual_noise.py'}[args.stage]
    result = [sys.executable, '-B', str(folder / script), '--cache', str(args.cache.resolve())]
    if args.stage == 'prepare':
        return result + ['--prepare']
    if args.output is None:
        raise ValueError('--output is required for training')
    result += ['--output', str(args.output.resolve())]
    steps = args.steps if args.steps is not None else {'high': 3000, 'refine': 10000, 'low': 5000}[args.stage]
    result += ['--steps', str(steps)]
    if args.stage == 'high':
        result += ['--mode', 'moment_skip', '--seed', '202610150101', '--device', 'mps']
    if args.stage == 'low':
        result += ['--bank', str(args.base_bank.resolve())]
    if args.stage == 'refine':
        if args.checkpoint is None:
            raise ValueError('--checkpoint is required for refinement')
        result += ['--checkpoint', str(args.checkpoint.resolve()), '--lr', '.001']
    if args.resume:
        result += ['--resume']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['prepare', 'high', 'refine', 'low'], required=True)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--checkpoint', type=Path)
    parser.add_argument('--base-bank', type=Path, default=ROOT/'models/ldamp_joint/v1/base',
                        help='Frozen five-interval base bank used by low-stage training')
    parser.add_argument('--steps', type=int)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--show-command', action='store_true')
    args = parser.parse_args()
    cmd = command(args)
    if args.show_command:
        import shlex
        print(shlex.join(cmd))
        return 0
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == '__main__':
    raise SystemExit(main())
