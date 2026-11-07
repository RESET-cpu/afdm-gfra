"""Train the selected first score, second score and activity classifier."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import signal

import torch
from threadpoolctl import threadpool_limits

from receiver.stmp.configuration import verify
from receiver.stmp.receiver import Receiver
from fileio import sha256
from fileio import write_json
from training.organized.stmp import auxiliary
from training.organized.stmp.common import DEFAULT_CONFIG
from training.organized.stmp.common import load_data
from training.organized.stmp.common import load_prior
from training.organized.stmp.common import load_recipe
from training.organized.stmp.common import relative
from training.organized.stmp.common import resolve
from training.organized.stmp.common import source_hashes
from training.organized.stmp.common import training_record
from training.organized.stmp.common import with_output
from training.organized.stmp.data import build_bank
from training.organized.stmp.first import SharedFirstTrainer


def inspect_assets(config, prior):
    data = load_data(config, prior)
    checkpoints = {}
    for stage in ('first', 'second', 'activity'):
        path = resolve(config[stage]['initial_checkpoint'])
        checkpoints[stage] = sha256(path)
        if checkpoints[stage] != config[stage]['initial_checkpoint_sha256']:
            raise ValueError('Initialization checkpoint changed: ' + stage)
    auxiliary.first_record(config)
    teachers = {stage: training_record(config, stage)['weight_sha256'] for stage in ('first', 'second')}
    return dict(status='PASS', samples={s:len(a) for s,a in data.items()},
                initialization_sha256=checkpoints, selected_teacher_sha256=teachers)


def run_first(config, prior, configuration_path):
    data = load_data(config, prior)
    output = resolve(config['first']['output'])
    output.mkdir(parents=True, exist_ok=True)
    specification = dict(configuration=config, configuration_sha256=sha256(configuration_path),
                         prior_definition_sha256=config['prior_definition_sha256'],
                         source_sha256=source_hashes(), device=config['runtime']['device'])
    path = output/'specification.json'
    if path.exists():
        if json.loads(path.read_text()) != specification:
            raise ValueError('Existing first-stage training specification differs')
    else:
        write_json(path, specification)
    trainer = SharedFirstTrainer(output, device=config['runtime']['device'])
    signal.signal(signal.SIGINT, trainer.request_stop)
    signal.signal(signal.SIGTERM, trainer.request_stop)
    return trainer.run(config, prior, data, sha256(path))


def run_auxiliary(config, prior, stage):
    auxiliary.first_record(config)
    if stage == 'activity':
        training_record(config, 'second')
    trainer = auxiliary.Trainer(config, prior, stage, device=config['runtime']['device'])
    signal.signal(signal.SIGINT, trainer.request_stop)
    signal.signal(signal.SIGTERM, trainer.request_stop)
    return trainer.train() is not None


def bind(config, prior):
    """Write a receiver configuration for the newly trained classifier pair."""
    auxiliary.first_record(config)
    training_record(config, 'second')
    output = resolve(config['output'])
    paths = dict(first_checkpoint=resolve(config['first_checkpoint']),
                 second_checkpoint=resolve(config['second_checkpoint']),
                 evidence_checkpoint=output/'activity/evidence_best.pt')
    activity = json.loads((output/'activity/complete.json').read_text())
    if (activity['status'] != 'COMPLETED' or activity['optimizer_steps'] < 1
            or activity['weight_sha256'] != sha256(paths['evidence_checkpoint'])
            or activity['specification_sha256'] != sha256(output/'activity/specification.json')
            or activity['prior_definition_sha256'] != config['prior_definition_sha256']
            or activity['first_sha256'] != sha256(paths['first_checkpoint'])
            or activity['second_sha256'] != sha256(paths['second_checkpoint'])):
        raise ValueError('Completed activity training and identical teachers required')
    configuration = deepcopy(json.loads(resolve(config['receiver_template']).read_text()))
    configuration['prior_definition'] = config['prior_definition']
    configuration['prior_definition_sha256'] = config['prior_definition_sha256']
    configuration['scale'] = prior['global_complex_rms']
    configuration['initialization']['normalized_training_second_moment'] = prior['normalized_mean_element_power']
    configuration['initialization']['training_sha256'] = prior['sample_files_sha256']['train']
    for key, path in paths.items():
        configuration[key] = relative(path)
        configuration[key+'_sha256'] = sha256(path)
    verify(configuration)
    Receiver(configuration, device='cpu')
    destination = output/'receiver.json'
    if destination.exists() and json.loads(destination.read_text()) != configuration:
        raise ValueError('Existing receiver configuration differs')
    write_json(destination, configuration)
    print(json.dumps(dict(status='BOUND', receiver_configuration=relative(destination),
                          receiver_performance_evaluated=False)))
    return configuration


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    parser.add_argument('--stage', choices=('data', 'first', 'second', 'activity', 'bind', 'all'))
    parser.add_argument('--output', type=Path, help='Separate run directory; rerun the same command to resume.')
    parser.add_argument('--teachers', choices=('selected', 'run'), default='selected',
                        help='Use selected teachers, or completed first/second stages in --output. All uses run.')
    parser.add_argument('--prior', type=Path, help='Explicit replacement prior for a newly generated bank.')
    parser.add_argument('--data-dir', type=Path, help='Directory containing matching physical banks and moments.')
    parser.add_argument('--device', choices=('cpu', 'mps', 'cuda'))
    parser.add_argument('--inspect', action='store_true', help='Read recipe and prior without training.')
    parser.add_argument('--check-assets', action='store_true', help='Hash-check banks, initial weights and teacher records.')
    args = parser.parse_args(argv)
    config = load_recipe(args.config, prior_path=args.prior, data_directory=args.data_dir, device=args.device)
    prior = None if args.stage == 'data' else load_prior(config)
    if args.inspect or args.check_assets:
        report = dict(status='INSPECTED', configuration=relative(args.config),
                      stages=['first', 'second', 'activity'], runtime=config['runtime'],
                      samples={s:config['bank'][s+'_samples'] for s in ('train', 'validation')},
                      optimizer_updates=0)
        if args.check_assets:
            report['assets'] = inspect_assets(config, load_prior(config))
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    if args.stage is None or args.output is None:
        parser.error('--stage and --output are required for data generation or training')
    config = with_output(config, args.output, teachers='run' if args.stage == 'all' else args.teachers)
    if args.stage == 'data':
        build_bank(config, args.output, args.config)
        return 0
    device = config['runtime']['device']
    if device == 'mps' and not torch.backends.mps.is_available():
        raise RuntimeError('MPS unavailable; select --device cpu')
    if device == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('CUDA unavailable; install a compatible PyTorch CUDA build')
    torch.set_num_threads(config['runtime']['threads'])
    stages = ('first', 'second', 'activity', 'bind') if args.stage == 'all' else (args.stage,)
    with threadpool_limits(limits=config['runtime']['threads']):
        for stage in stages:
            if stage == 'first':
                completed = run_first(config, prior, args.config)
            elif stage == 'bind':
                bind(config, prior)
                completed = True
            else:
                completed = run_auxiliary(config, prior, stage)
            if not completed:
                return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
