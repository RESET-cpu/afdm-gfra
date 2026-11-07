"""Change the remaining auxiliary epoch budget in a separate, resumable run."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import shutil
import time
import torch
import train_auxiliary_200 as runner
from afdm_jadcedd.experiment.training.proposed.auxiliary import atomic_json, atomic_torch, first_record
from afdm_jadcedd.experiment.training.proposed.common import source_hashes, resolve, relative, load_prior
from afdm_jadcedd.utils import sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parent', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--epochs', type=int, required=True)
    args = parser.parse_args()
    parent, output = args.parent.resolve(), args.output.resolve()
    plan = runner.read(parent/'PLAN.json')
    if output.exists() or runner.read(parent/'STATUS.json')['status'] != 'PAUSED' or args.epochs < 1:
        raise ValueError('Paused parent, new output and positive epoch budget required')
    if plan['source_sha256'] != source_hashes() or plan['mainline_sha256'] != sha256(runner.ROOT/'MAINLINE.json'):
        raise ValueError('Training source or frozen mainline changed')
    prior_runner = parent/'source_snapshot/scripts/train_auxiliary_200.py'
    if sha256(prior_runner) != plan['script_sha256']:
        raise ValueError('Original supervisor snapshot is required')
    source = parent/'n50000/second'
    state = torch.load(source/'last.pt', map_location='cpu', weights_only=False)
    if state['epoch'] > args.epochs or state['stage'] != 'second':
        raise ValueError('Budget must include all already processed epochs')
    if state['specification_sha256'] != sha256(source/'specification.json'):
        raise ValueError('Checkpoint specification mismatch')
    if any((parent/f'n{n}/{s}/complete.json').exists() for n,s in ((50000,'activity'),(5000,'second'),(5000,'activity'))):
        raise ValueError('This continuation expects the other auxiliary jobs to be pending')
    output.mkdir(parents=True)
    configs = {}
    for size in (50000,5000):
        entry = plan['configs'][str(size)]
        if sha256(resolve(entry['path'])) != entry['sha256']:
            raise ValueError('Parent configuration changed')
        old = runner.read(resolve(entry['path']))
        config = deepcopy(old)
        config['output'] = relative(output/f'n{size}')
        for key, name in (('checkpoint','second_best.pt'),('training_record','complete.json'),
                          ('training_specification','specification.json')):
            config['second_'+key] = relative(output/f'n{size}/second'/name)
        for stage in ('second','activity'):
            config[stage].update(maximum_epochs=args.epochs, minimum_epochs=args.epochs,
                validation_patience=args.epochs+1,
                stopping=f'Exactly {args.epochs} complete data epochs; no validation early stop')
        config['budget_revision'] = dict(parent=relative(parent), old_epochs=plan['total_epochs'],
            new_epochs=args.epochs, cumulative=True, learning_rate_schedule='Cosine schedule now ends at the new final epoch; past updates preserved')
        first_record(config)
        load_prior(config)
        atomic_json(output/f'n{size}.json', config)
        configs[str(size)] = dict(path=relative(output/f'n{size}.json'), sha256=sha256(output/f'n{size}.json'),
            first_sha256=entry['first_sha256'])
        if size != 50000:
            continue
        spec = runner.read(source/'specification.json')
        assert spec['configuration'] == old
        spec['configuration'] = config
        target = output/'n50000/second'
        atomic_json(target/'specification.json', spec)
        new_hash = sha256(target/'specification.json')
        atomic_torch(target/'last.pt', dict(state, specification_sha256=new_hash))
        restored = torch.load(target/'last.pt', map_location='cpu', weights_only=False)
        restored['specification_sha256'] = state['specification_sha256']
        assert runner.same(state, restored)
        best = torch.load(source/'second_best.pt', map_location='cpu', weights_only=False)
        assert best['metadata']['specification_sha256'] == state['specification_sha256']
        revised = deepcopy(best)
        revised['metadata']['specification_sha256'] = new_hash
        atomic_torch(target/'second_best.pt', revised)
        restored_best = torch.load(target/'second_best.pt', map_location='cpu', weights_only=False)
        restored_best['metadata']['specification_sha256'] = state['specification_sha256']
        assert runner.same(best, restored_best)
        for name in ('baseline.json','history.json'):
            if (source/name).exists():
                shutil.copy2(source/name,target/name)
        atomic_json(target/'MIGRATION.json', dict(source=relative(source),
            source_sha256={name:sha256(source/name) for name in ('last.pt','second_best.pt','specification.json')},
            destination_specification_sha256=new_hash, exact_resume_state_comparison='PASS',
            selected_checkpoint_preserved=True, epoch=state['epoch'], cursor=state['cursor'],
            optimizer_steps=state['steps'], protocol_change=config['budget_revision']))
    plan.update(configs=configs, parent=relative(parent), total_epochs=args.epochs,
        script_sha256=sha256(runner.__file__), created_unix=time.time())
    atomic_json(output/'PLAN.json',plan)
    atomic_json(output/'STATUS.json',dict(status='PREPARED',queue=plan['queue'],total_epochs=args.epochs))
    for path in [*plan['source_sha256'],relative(Path(runner.__file__)),relative(Path(__file__))]:
        destination=output/'source_snapshot'/path
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(resolve(path),destination)
    runner.verify(output)
    print(json.dumps(dict(status='PREPARED',epochs=args.epochs,resume_epoch=state['epoch'],
        resume_samples=state['cursor'],optimizer_steps=state['steps'],exact_resume_state_comparison='PASS')))


if __name__ == '__main__':
    main()
