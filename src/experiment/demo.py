"""One small synthetic AFDM example, independent of pretrained weights."""
import argparse
import json
from pathlib import Path
import time

import numpy as np
from threadpoolctl import threadpool_limits
from channel.observation import ReceiverInput
from scenario.generate import generate_case


def least_squares(inputs):
    """Known-phase channel LS; no activity truth or path parameters are used."""
    q, users, n = inputs.operator.shape
    antennas, outputs = inputs.observation.shape[1:]
    design = inputs.operator.reshape(q, users * n)
    received = inputs.observation.reshape(q, -1)
    value, _, rank, singular = np.linalg.lstsq(design, received, rcond=None)
    if rank != users * n:
        raise ValueError('The diagnostic pilot must identify the complete channel')
    estimate = value.reshape(users, n, antennas, outputs).transpose(0, 2, 3, 1)
    return estimate, float(singular[0] / singular[-1])


def run(seed=2026110701):
    start = time.perf_counter()
    with threadpool_limits(limits=1):
        public, truth, _ = generate_case(seed, 30., 1., users=2, frames=32,
                                         m_z=2, m_y=2, activity_probability=.5)
        inputs = ReceiverInput(**{k: public[k] for k in
                               ('observation', 'operator', 'noise_variance', 'activity_prior')})
        estimate, condition = least_squares(inputs)
        channel = truth['channel']
        energy = float(np.sum(abs(channel) ** 2))
        nmse = float(np.sum(abs(estimate - channel) ** 2) / energy)
    report = dict(status='PASS', purpose='installation and numerical smoke example only',
                  receiver='least squares, known phase; not GP-MP or an activity detector',
                  seed=seed, users=2, frames=32, antennas=4, symbols=16,
                  snr_db=30., nmse_db=float(10 * np.log10(max(nmse, np.finfo(float).tiny))),
                  pilot_condition_number=condition, channel_shape=list(channel.shape),
                  seconds=time.perf_counter() - start, weights_loaded=False,
                  training_started=False, formal_experiment_started=False,
                  truth_usage='simulation and final error scoring only')
    return report, channel, estimate


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=2026110701)
    parser.add_argument('--output', type=Path, help='New directory for SUMMARY.json and channel.png')
    args = parser.parse_args(argv)
    if args.seed < 0:
        parser.error('seed must be nonnegative')
    if args.output and args.output.exists() and any(args.output.iterdir()):
        parser.error('choose a new output directory; existing results are preserved')
    report, truth, estimate = run(args.seed)
    if args.output:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from fileio import write_json
        args.output.mkdir(parents=True, exist_ok=True)
        figure, axes = plt.subplots(1, 2, figsize=(7, 3), constrained_layout=True)
        user = int(np.argmax(np.sum(abs(truth) ** 2, axis=(1, 2, 3))))
        vmax = float(np.max(abs(truth[user, 0])))
        for axis, values, title in zip(axes, (truth, estimate), ('Simulated channel', 'Known-phase LS')):
            axis.imshow(abs(values[user, 0]), origin='lower', vmin=0, vmax=vmax)
            axis.set(title=title, xlabel='Input symbol', ylabel='Output symbol')
        figure.suptitle('Synthetic installation example (not a paper result)')
        figure.savefig(args.output / 'channel.png', dpi=120)
        plt.close(figure)
        write_json(args.output / 'SUMMARY.json', report)
    print(json.dumps(report, indent=2))
    return 0
