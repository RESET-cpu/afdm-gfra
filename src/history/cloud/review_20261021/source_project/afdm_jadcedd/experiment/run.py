"""Run, inspect and evaluate the selected AFDM JADCE algorithms."""
import argparse
import json
from pathlib import Path

import numpy as np

from afdm_jadcedd.algorithm.registry import ALGORITHMS, build_receiver, verify_algorithms
from afdm_jadcedd.algorithm.baselines.unknown_phase_baselines import build_estimated_phase_receiver, default_noise_mode
from afdm_jadcedd.algorithm.baselines.baseline_noise import EstimatedNoiseBaselineReceiver
from afdm_jadcedd.algorithm import research
from afdm_jadcedd.algorithm.proposed.configuration import load_configuration
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.system.observation import ReceiverInput


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('info', 'verify', 'report', 'test'):
        commands.add_parser(name)
    for name in ('run', 'baseline', 'research'):
        infer = commands.add_parser(name)
        infer.add_argument('--input', type=Path, required=True)
        infer.add_argument('--output', type=Path, required=True)
        choices = research.ALGORITHMS if name == 'research' else (
            ALGORITHMS if name == 'run' else ALGORITHMS[1:])
        infer.add_argument('--method', choices=choices,
                           default='proposed' if name == 'run' else None, required=name != 'run')
        infer.add_argument('--config', type=Path)
        infer.add_argument('--device', choices=('auto', 'cpu', 'mps'), default='auto',
                           help='Neural receiver device; GNN uses its configured backend')
        if name != 'research':
            infer.add_argument('--phase-mode', choices=('estimated', 'known'), default='estimated',
                               help='Estimate phase from original pilots (default), or use a supplied known-phase operator')
            infer.add_argument('--noise-mode', choices=('estimated', 'known'),
                               help='Defaults to the selected method noise policy in MAINLINE.json')
    generate = commands.add_parser('simulate')
    generate.add_argument('--seed', type=int, required=True)
    generate.add_argument('--snr', type=float, default=0.)
    generate.add_argument('--users', type=int, default=40)
    generate.add_argument('--output', type=Path, required=True)
    generate.add_argument('--phase-mode', choices=('estimated', 'known'), default='estimated')
    generate.add_argument('--noise-mode', choices=('estimated', 'known'), default='known',
                          help='Estimated omits public noise variance; known supplies it')
    evaluate = commands.add_parser('evaluate')
    evaluate.add_argument('--estimate', type=Path, required=True)
    evaluate.add_argument('--truth', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == 'test':
        import subprocess
        import sys
        return subprocess.call([sys.executable, '-B', '-m', 'pytest', str(ROOT/'tests')], cwd=ROOT)
    if args.command == 'info':
        print((ROOT/'MAINLINE.json').read_text())
        return 0
    if args.command == 'report':
        print((ROOT/'docs/CURRENT_STAGE.md').read_text())
        return 0
    if args.command == 'evaluate':
        from afdm_jadcedd.experiment.evaluation.metrics import score_arrays
        with np.load(args.estimate, allow_pickle=False) as saved:
            arrays = {key: saved[key] for key in saved.files}
        with np.load(args.truth, allow_pickle=False) as saved:
            truth = {key: saved[key] for key in saved.files}
        if 'activity_decision' not in arrays:
            if 'probabilities' not in arrays:
                parser.error('Prediction contains scores only; a matching frozen activity rule is required')
            arrays['activity_decision'] = arrays['probabilities'] >= .5
        metrics = score_arrays(arrays, truth)
        metrics['aer'] = (metrics['misses']+metrics['false_alarms'])/len(truth['activity'])
        print(json.dumps(metrics, ensure_ascii=False))
        return 0
    import torch
    from threadpoolctl import threadpool_limits
    torch.set_num_threads(1)
    with threadpool_limits(1):
        if args.command == 'verify':
            print(json.dumps(verify_algorithms(), ensure_ascii=False, indent=2))
            return 0
        if args.command == 'simulate':
            if args.phase_mode == 'estimated':
                from afdm_jadcedd.experiment.unknown_phase import generate_case
            else:
                from afdm_jadcedd.experiment.generate import generate_case
            if args.output.exists():
                raise FileExistsError(args.output)
            c = load_configuration()
            inputs, truth, metadata = generate_case(args.seed, args.snr, c['scale'], users=args.users,
                                                     require_active_user=True, grid_mode='off_grid')
            if args.phase_mode == 'estimated':
                public = inputs
            else:
                public = {key: inputs[key] for key in ReceiverInput.__dataclass_fields__}
                metadata.update(phase_mode='known', phase_scope='Ideal reference: exact cross-frame phase supplied in operator')
            truth = dict(truth, noise_variance=np.asarray(public['noise_variance']))
            if args.noise_mode == 'estimated':
                public = {key: value for key, value in public.items() if key != 'noise_variance'}
            metadata.update(noise_mode=args.noise_mode,
                noise_scope=('Noise variance omitted from receiver input' if args.noise_mode == 'estimated'
                             else 'Noise variance supplied; estimated-noise receivers ignore this field'))
            args.output.mkdir(parents=True)
            np.savez_compressed(args.output/'input.npz', **public)
            np.savez_compressed(args.output/'truth.npz', **truth)
            (args.output/'generation.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n')
            print(json.dumps(dict(status='GENERATED', input=str(args.output/'input.npz'),
                                  phase_scope=metadata['phase_scope']), ensure_ascii=False))
            return 0
        if args.command == 'research':
            receiver = research.build_receiver(args.method, config=args.config, device=args.device)
        else:
            noise_mode = args.noise_mode or default_noise_mode(args.method)
            if args.phase_mode == 'estimated':
                receiver = build_estimated_phase_receiver(args.method, config=args.config,
                    device=args.device, noise_mode=noise_mode)
            else:
                if args.config is not None:
                    schema = json.loads(args.config.read_text()).get('schema', '')
                    if schema.startswith(('afdm-proposed-estimated-phase-', 'afdm-proposed-iterative-phase-')):
                        raise ValueError('Known-phase mode requires a conditional receiver configuration')
                if args.method == 'proposed' and noise_mode == 'estimated':
                    from afdm_jadcedd.algorithm.proposed_noise_public import EstimatedNoiseProposedPublicReceiver
                    receiver = EstimatedNoiseProposedPublicReceiver(load_configuration(args.config), device=args.device)
                else:
                    factory = EstimatedNoiseBaselineReceiver if noise_mode == 'estimated' else build_receiver
                    receiver = factory(args.method, config=args.config, device=args.device)
        record = receiver.run(args.input, args.output)
    summary = {key: record[key] for key in ('status', 'method', 'iterations', 'seconds')}
    for key in ('stopping_reason', 'validation_status', 'noise_mode', 'noise_variance_estimate'):
        if key in record:
            summary[key] = record[key]
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if record['status'] == 'COMPLETE' else 1


if __name__ == '__main__':
    raise SystemExit(main())
