"""Preserve a paused auxiliary run and continue with verified execution changes."""
from copy import deepcopy
import argparse
import json
from pathlib import Path
import shutil
import time
import torch

import train_auxiliary_200 as runner
from afdm_jadcedd.experiment.training.proposed.auxiliary import atomic_json, atomic_torch, first_record
from afdm_jadcedd.experiment.training.proposed.common import load_data, load_prior, relative, resolve, source_hashes
from afdm_jadcedd.utils import sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parent', type=Path, default=runner.DEFAULT)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--benchmark', type=Path, required=True)
    args = parser.parse_args()
    parent, output = args.parent.resolve(), args.output.resolve()
    report = runner.read(args.benchmark)
    plan = runner.read(parent/'PLAN.json')
    if not report['all_numerical_checks_pass'] or not report['frozen_first_unchanged']:
        raise ValueError('Successful paired numerical checks required')
    if runner.read(parent/'STATUS.json')['status'] != 'PAUSED' or output.exists():
        raise ValueError('Paused parent and a new output directory required')
    source = parent/'n50000/second'
    if report['source_checkpoint_sha256'] != sha256(source/'last.pt'):
        raise ValueError('Benchmark did not use this paused checkpoint')
    old_sources = plan['source_sha256']
    changed = [path for path, digest in old_sources.items() if sha256(resolve(path)) != digest]
    allowed = relative(runner.ROOT/'src/afdm_jadcedd/experiment/training/proposed/auxiliary.py')
    if changed != [allowed] or sha256(runner.ROOT/'MAINLINE.json') != plan['mainline_sha256']:
        raise ValueError('Unexpected source or frozen mainline changes')
    old_aux = args.benchmark.parent.parent/'source_before/auxiliary.py'
    if sha256(old_aux) != old_sources[allowed]:
        raise ValueError('Original training source must remain available')
    if sha256(runner.__file__) != plan['script_sha256']:
        raise ValueError('Supervisor changed')
    output.mkdir(parents=True)
    configs = {}
    for size in (50000, 5000):
        entry = plan['configs'][str(size)]
        if sha256(resolve(entry['path'])) != entry['sha256']:
            raise ValueError('Parent configuration changed')
        old = runner.read(resolve(entry['path']))
        config = deepcopy(old)
        config['output'] = relative(output/f'n{size}')
        for key, name in (('checkpoint', 'second_best.pt'), ('training_record', 'complete.json'),
                          ('training_specification', 'specification.json')):
            config['second_'+key] = relative(output/f'n{size}/second'/name)
        for stage in ('second', 'activity'):
            config.setdefault('cuda_execution', {})[stage] = dict(cuda_graph=True, foreach_ema=True,
                original_microbatches=True, optimizer_batch_unchanged=True)
            assert config[stage] == old[stage]
        config['execution_continuation'] = dict(parent=relative(parent),
            benchmark=relative(args.benchmark), benchmark_sha256=sha256(args.benchmark),
            objective_and_schedule_unchanged=True)
        first_record(config)
        load_data(config, load_prior(config))
        atomic_json(output/f'n{size}.json', config)
        configs[str(size)] = dict(path=relative(output/f'n{size}.json'),
            sha256=sha256(output/f'n{size}.json'), first_sha256=entry['first_sha256'])
        if size != 50000:
            continue
        old_spec = runner.read(source/'specification.json')
        assert old_spec['configuration'] == old
        spec = deepcopy(old_spec)
        spec.update(configuration=config, source_sha256=source_hashes())
        target = output/'n50000/second'
        atomic_json(target/'specification.json', spec)
        spec_hash = sha256(target/'specification.json')
        state = torch.load(source/'last.pt', map_location='cpu', weights_only=False)
        assert state['specification_sha256'] == sha256(source/'specification.json')
        assert state['stage'] == 'second' and state['epoch'] <= config['second']['maximum_epochs']
        moved = dict(state, specification_sha256=spec_hash)
        atomic_torch(target/'last.pt', moved)
        restored = torch.load(target/'last.pt', map_location='cpu', weights_only=False)
        restored['specification_sha256'] = state['specification_sha256']
        assert runner.same(state, restored)
        selected = torch.load(source/'second_best.pt', map_location='cpu', weights_only=False)
        assert selected['metadata']['specification_sha256'] == state['specification_sha256']
        revised = deepcopy(selected)
        revised['metadata']['specification_sha256'] = spec_hash
        atomic_torch(target/'second_best.pt', revised)
        check = torch.load(target/'second_best.pt', map_location='cpu', weights_only=False)
        check['metadata']['specification_sha256'] = state['specification_sha256']
        assert runner.same(selected, check)
        for name in ('history.json', 'baseline.json'):
            if (source/name).exists():
                shutil.copy2(source/name, target/name)
        atomic_json(target/'MIGRATION.json', dict(source=relative(source),
            source_sha256={name:sha256(source/name) for name in ('last.pt', 'second_best.pt', 'specification.json')},
            destination_specification_sha256=spec_hash, epoch=state['epoch'], cursor=state['cursor'],
            optimizer_steps=state['steps'], exact_resume_state_comparison='PASS',
            selected_checkpoint_preserved=True, protocol_change=False,
            original_training_source=relative(old_aux), original_training_source_sha256=sha256(old_aux)))
    plan.update(configs=configs, source_sha256=source_hashes(), created_unix=time.time(),
        parent=relative(parent), benchmark=relative(args.benchmark), benchmark_sha256=sha256(args.benchmark))
    atomic_json(output/'PLAN.json', plan)
    atomic_json(output/'STATUS.json', dict(status='PREPARED', queue=plan['queue']))
    snapshot = output/'source_snapshot'
    for path in [*plan['source_sha256'], relative(Path(__file__)), relative(Path(runner.__file__)),
                 'scripts/benchmark_auxiliary_cuda.py']:
        destination = snapshot/path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(resolve(path), destination)
    runner.verify(output)
    print(json.dumps(dict(status='PREPARED', output=str(output), resume_epoch=state['epoch'],
        resume_samples=state['cursor'], optimizer_steps=state['steps'], all_resume_state_equal=True)))


if __name__ == '__main__':
    main()
