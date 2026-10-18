#!/usr/bin/env python3
"""Estimate initial phase, then one posterior phase update with a selected baseline."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from threadpoolctl import threadpool_limits
from afdm_jadcedd.algorithm.baselines.baseline_phase import BaselinePhaseReceiver


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--method', choices=['gamp', 'offgrid_sbl'], required=True)
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--phase-weight', type=float, default=1.)
    args = parser.parse_args()
    with threadpool_limits(1):
        record = BaselinePhaseReceiver(args.method, args.phase_weight).run(args.input, args.output)
    print(json.dumps({k:record[k] for k in ['status', 'method', 'seconds', 'conditional_iterations']}))


if __name__ == '__main__':
    main()
