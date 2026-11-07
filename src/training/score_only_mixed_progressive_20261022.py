"""Fresh progressive score-only training over a balanced K/Q condition grid."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import gc
import json
import math
import os
from pathlib import Path
import sys
import time
import traceback

import numpy as np
import torch
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from training import score_only_progressive_20261022 as common
from algorithm.candidates.score_only_progressive_20261022 import Receiver, conditional_loss
from evaluation.observations import observation
from evaluation.receivers import setup
from system.phase import phase_operator
from utils import read_json, write_json, sha256, state_sha

OUT = ROOT / 'result/candidates/score_only_mixed_progressive_20261022'
OLD = ROOT / 'result/candidates/score_only_progressive_20261022'
USERS = [20, 40, 60, 80, 100]
FRAMES = [8, 16, 24, 32, 40, 48]
NEW_USERS = [30, 50, 70, 90]
NEW_FRAMES = [12, 20, 28, 36, 44]
SNRS = [-4, -2, 0, 2, 4, 6]
BASES = dict(train=202610220100001, validation=202610220200001,
             test=202610220300001, preflight=202610220500001)
SEEDS = [202610220700001, 202610220700002, 202610220700003]
COUNTS = dict(train=3000, validation=600, test=2000)
DEPTH, EPOCHS, LR, TIMEOUT = 10, 2, 2e-6, 96 * 3600


def utc():
    return datetime.now(timezone.utc).isoformat()


def event(stage, **values):
    row = dict(stage=stage, utc=utc(), pid=os.getpid(), **values)
    write_json(OUT / 'STATUS.json', row)
    with (OUT / 'events.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(row, allow_nan=False) + '\n')
    print(json.dumps(row, allow_nan=False), flush=True)


def scene_specs(split):
    specs = []
    if split == 'preflight':
        groups = [('structural_check', [(20, 8), (100, 8), (20, 48), (100, 48), (40, 16), (30, 12)], 1)]
    else:
        groups = [('trained_condition', [(k, q) for k in USERS for q in FRAMES],
                   dict(train=100, validation=20, test=50)[split])]
        if split == 'test':
            groups.append(('untrained_intermediate_condition',
                           [(k, q) for k in NEW_USERS for q in NEW_FRAMES], 25))
    for kind, conditions, count in groups:
        for users, frames in conditions:
            for _ in range(count):
                index = len(specs)
                specs.append(dict(index=index, seed=BASES[split] + index,
                    condition=f'K{users}_Q{frames}', coverage=kind,
                    parameters=dict(users=users, frames=frames, activity_probability=.1, snr_db=0.)))
    return specs


SPECS = {split: scene_specs(split) for split in BASES}


def prepare():
    if (OUT / 'PLAN.json').exists():
        raise FileExistsError('Preserve the existing mixed-condition plan')
    config = read_json(ROOT / 'src/configs/final/STMP.json')
    binding = {key: config[key] for key in ('scale', 'first_checkpoint',
        'first_checkpoint_sha256', 'evidence_checkpoint', 'evidence_checkpoint_sha256')}
    for key in ('first_checkpoint', 'evidence_checkpoint'):
        assert sha256(ROOT / binding[key]) == binding[key + '_sha256']
    assert all(len(SPECS[s]) == count for s, count in COUNTS.items())
    all_seeds = [x['seed'] for rows in SPECS.values() for x in rows]
    assert len(set(all_seeds)) == len(all_seeds)
    prior = read_json(OLD / 'PLAN.json')
    previous_seeds = {prior['scene_base_seeds'][s] + i for s, n in prior['scene_counts'].items() for i in range(n)}
    assert not previous_seeds.intersection(all_seeds)
    train_conditions = {x['condition'] for x in SPECS['train']}
    intermediate = {x['condition'] for x in SPECS['test'] if x['coverage'].startswith('untrained')}
    assert len(train_conditions) == 30 and len(intermediate) == 20
    assert not train_conditions.intersection(intermediate)
    manifest = dict(schema='mixed-condition-scenes-v1', splits=SPECS)
    write_json(OUT / 'SCENES.json', manifest)
    sources = [Path(__file__), Path(common.__file__),
        ROOT / 'src/algorithm/candidates/score_only_progressive_20261022.py',
        ROOT / 'src/evaluation/observations.py', ROOT / 'src/evaluation/receivers.py', ROOT / 'src/utils.py',
        *sorted((ROOT / 'src/networks').rglob('*.py')), *sorted((ROOT / 'src/system').rglob('*.py'))]
    plan = dict(schema='score-only-mixed-progressive-v1', created_utc=utc(),
        authorization='User explicitly requested starting Wei-style training with more scene types for generalization; preserve earlier score-only and frozen-classifier decisions.',
        binding=binding, scene_counts=COUNTS, scene_base_seeds=BASES, random_seeds=SEEDS,
        scene_manifest_sha256=sha256(OUT / 'SCENES.json'),
        conditions=dict(users=USERS, pilot_frames=FRAMES, combinations=30,
            scenes_per_training_combination=100, snr_db=[-4, 6],
            fixed=dict(activity_probability=.1, receive_antennas=16, channel='NTN-TDL-D', grid='off_grid'),
            sampling='Each depth/epoch visits all 3000 scenes once in a seeded random order; each K/Q pair has equal scene weight. SNR is continuous uniform and noise is freshly sampled per presentation.'),
        phase_mode='known: oracle phase supplied to isolate the conditional receiver',
        noise_mode='estimated from observations in training and evaluation',
        training=dict(maximum_depth=DEPTH, epochs_per_depth=EPOCHS, learning_rate=LR,
            updates_per_seed=COUNTS['train'] * EPOCHS * DEPTH,
            total_updates=COUNTS['train'] * EPOCHS * DEPTH * len(SEEDS),
            optimizer='Adam, betas=(.9,.999), eps=1e-8, weight_decay=0, gradient norm clipped at 1',
            batch='One complete physical scene; each scene has equal objective weight regardless of K.',
            schedule='Depth 1 to 10; jointly update all existing scores immediately after adding each new layer; retain existing Adam moments.',
            initialization='Independent original pretrained first-score copy for each layer; no old ten-layer or partial single-condition weights loaded.',
            trainable='Only score-network parameters; shared original STMP evidence classifier frozen with differentiable inputs; alpha=beta=gamma=1 fixed.',
            loss='Sum of true-active conditional scene NMSE; newest layer weight 1, earlier layers .2; no activity BCE.',
            checkpoint='Every 500 updates and epoch end, plus each completed depth; no intermediate performance evaluation.',
            automatic_retry=False, activation_checkpointing=True, tf32=False),
        evaluation=dict(depth=10, snr_db=SNRS, after='all three repetitions complete depth 10',
            validation='600 independent scenes, 20 per trained condition; descriptive, no model selection or further tuning.',
            test='2000 independent scenes: 1500 at trained K/Q combinations, 500 at 20 untrained intermediate K/Q combinations.',
            untrained_users=NEW_USERS, untrained_frames=NEW_FRAMES,
            pairing='Same physical scene and standardized noise across six SNR values and all models.',
            reference='Same 10-layer architecture, frozen original classifier and fixed scalars, all scores unchanged from original pretraining; not 600-iteration STMP.',
            reporting='Every K/Q/SNR and all three seeds; aggregate groups reported separately; no best-seed selection or automatic promotion.',
            metrics=['full NMSE', 'active conditional NMSE', 'AER', 'misses', 'false alarms']),
        literature=dict(url='https://arxiv.org/html/2610.17785v1#S3.SS4',
            source='Wei and Yuan, III-D and V-A: progressive depth with joint preceding-layer training and auxiliary supervision.',
            differences='Wei also learns calibration scalars and uses a single-user five-layer model; current frozen classifier, fixed scalars, ten layers and all data/optimizer settings are project choices.'),
        timeout_seconds=TIMEOUT, frozen_assets=common.protect_paths(),
        source_sha256={str(p.relative_to(ROOT)).replace('\\', '/'): sha256(p) for p in sources},
        previous_candidate='Single-condition candidate stopped with its checkpoint retained; no continuation from those weights.',
        material_passport=dict(origin='academic-research-suite / experiment-agent', mode='run', status='prospective'))
    write_json(OUT / 'PLAN.json', plan)
    event('PREPARED', scene_counts=COUNTS, conditions=30, total_updates=plan['training']['total_updates'])


def verify(plan):
    common.verify_sources(plan)
    assert plan['scene_manifest_sha256'] == sha256(OUT / 'SCENES.json')
    assert read_json(OUT / 'SCENES.json')['splits'] == SPECS


def scene_path(split, index):
    return OUT / 'data' / split / f'{index:04d}.npz'


def make_scene(split, index, scale):
    spec = SPECS[split][index]
    path = scene_path(split, index)
    if path.exists():
        with np.load(path, allow_pickle=False) as saved:
            values = dict(saved)
        assert int(values['seed']) == spec['seed']
        assert int(values['users']) == spec['parameters']['users']
        assert int(values['frames']) == spec['parameters']['frames']
        return values
    inputs, truth, metadata = observation(spec['seed'], spec['parameters'], scale)
    operator = phase_operator(inputs.pilot, truth['phase_slopes'])
    clean = np.einsum('qkn,kmrn->qmr', operator, truth['channel'], optimize=False)
    values = dict(seed=np.array(spec['seed']), users=np.array(spec['parameters']['users']),
        frames=np.array(spec['parameters']['frames']), a=operator, clean=clean,
        epsilon=(inputs.observation-clean)/np.sqrt(metadata['generated_noise_variance']),
        rho=np.array(inputs.activity_prior), channel=truth['channel'], activity=truth['activity'])
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    with temporary.open('wb') as stream:
        np.savez(stream, **values)
    temporary.replace(path)
    write_json(path.with_suffix('.json'), dict(spec=spec, sha256=sha256(path), physical_metadata=metadata))
    return values


def preflight():
    if (OUT / 'PREFLIGHT.json').exists():
        raise FileExistsError('Preserve preflight evidence')
    plan = read_json(OUT / 'PLAN.json'); verify(plan)
    setup('cuda'); threadpool_limits(4); torch.manual_seed(SEEDS[0])
    first, evidence = common.load_sources(plan)
    model = Receiver(evidence)
    for _ in range(DEPTH):
        model.add_layer(first['state_dict'])
    assert len({next(x.score.parameters()).data_ptr() for x in model.layers}) == DEPTH
    assert all(all(torch.equal(v, first['state_dict'][k]) for k, v in layer.score.state_dict().items()) for layer in model.layers)
    model.cuda().train(); classifier_hash = state_sha(model.evidence)
    selected = common.parameters(model); opt = common.optimizer(selected)
    checks = []
    for index, snr in enumerate([-4., 6., 6., -4., 0., 2.]):
        values = make_scene('preflight', index, plan['binding']['scale'])
        public, truth, active, _ = common.inputs_for(values, plan['binding']['scale'], snr)
        assert public['channel_shape'][0] == int(values['users'])
        opt.zero_grad(set_to_none=True); torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize(); started = time.monotonic()
        outputs, _ = model(public, collect_diagnostics=False)
        loss, terms = conditional_loss(outputs, truth, active)
        assert bool(torch.isfinite(loss))
        loss.backward()
        norms = [float(torch.stack([torch.linalg.vector_norm(p.grad, dtype=torch.float64)
                 for p in layer.score.parameters() if p.grad is not None]).norm()) for layer in model.layers]
        assert all(np.isfinite(n) and n > 0 for n in norms)
        assert all(p.grad is None for name, p in model.named_parameters() if '.score.' not in name)
        probes = [(next(layer.score.parameters()), next(layer.score.parameters()).detach().clone()) for layer in model.layers]
        gradient_norm = common.clip(selected); opt.step(); torch.cuda.synchronize()
        assert all(not torch.equal(p, old) for p, old in probes)
        assert state_sha(model.evidence) == classifier_hash
        assert all(torch.equal(layer.calibration.detach().cpu(), torch.zeros(3)) for layer in model.layers)
        checks.append(dict(condition=SPECS['preflight'][index]['condition'], snr_db=snr,
            seconds=time.monotonic()-started, peak_allocated_mib=torch.cuda.max_memory_allocated()/2**20,
            loss=float(loss.detach()), gradient_norm=gradient_norm, all_layer_gradient_norms=norms))
        event('PREFLIGHT_CHECK', condition=checks[-1]['condition'], seconds=checks[-1]['seconds'],
              peak_allocated_mib=checks[-1]['peak_allocated_mib'])
        del outputs, loss, terms, probes, public, truth, active
    del model, selected, opt; gc.collect(); torch.cuda.empty_cache()
    # Check optimizer state retention and final-layer gradient to the preceding score.
    model = Receiver(evidence); model.add_layer(first['state_dict']); model.cuda().train()
    opt = common.optimizer(common.parameters(model))
    values = make_scene('preflight', 4, plan['binding']['scale'])
    public, truth, active, _ = common.inputs_for(values, plan['binding']['scale'], 0.)
    outputs, _ = model(public, collect_diagnostics=False)
    loss, _ = conditional_loss(outputs, truth, active); loss.backward()
    common.clip(common.parameters(model)); opt.step(); opt.zero_grad(set_to_none=True)
    p0 = next(model.layers[0].score.parameters())
    parameter_before, moment_before = p0.detach().clone(), opt.state[p0]['exp_avg'].clone()
    model.add_layer(first['state_dict']); model.cuda().train()
    opt.add_param_group(dict(params=list(model.layers[-1].score.parameters()), lr=LR))
    assert torch.equal(p0, parameter_before) and torch.equal(opt.state[p0]['exp_avg'], moment_before)
    assert all(torch.equal(v.cpu(), first['state_dict'][k]) for k, v in model.layers[-1].score.state_dict().items())
    outputs, _ = model(public, collect_diagnostics=False)
    _, terms = conditional_loss(outputs, truth, active)
    derivative = torch.autograd.grad(terms[-1], p0)[0]
    assert bool(torch.isfinite(derivative).all() & (derivative.abs().max() > 0))
    verify(plan)
    write_json(OUT / 'PREFLIGHT.json', dict(status='PASS', utc=utc(),
        plan_sha256=sha256(OUT / 'PLAN.json'), checks=checks, splits_disjoint=True,
        balanced_training_counts=dict(Counter(x['condition'] for x in SPECS['train'])),
        independent_original_initialization=True, frozen_classifier_unchanged=True,
        calibrations_fixed_one=True, all_score_layers_updated=True,
        optimizer_state_retained_on_growth=True,
        last_layer_to_first_layer_gradient_max=float(derivative.abs().max()),
        preflight_updates_discarded=True, performance_evaluation=False))
    event('PREFLIGHT_PASS', conditions_checked=len(checks))


def check_run(start):
    if time.monotonic()-start > TIMEOUT:
        raise TimeoutError('Declared 96-hour bound reached; checkpoints retained')
    if (OUT / 'STOP_REQUESTED').exists():
        raise InterruptedError('Stop requested; checkpoints retained')


def train_one(plan, first, evidence, repetition, seed, start):
    torch.manual_seed(seed)
    folder = OUT / f'seed{repetition}'; folder.mkdir(exist_ok=False)
    model = Receiver(evidence); original_classifier = state_sha(model.evidence)
    opt = None; completed = 0; stage_log = []
    for depth in range(1, DEPTH+1):
        model.add_layer(first['state_dict']); model.cuda().train()
        if opt is None:
            opt = common.optimizer(common.parameters(model))
        else:
            opt.add_param_group(dict(params=list(model.layers[-1].score.parameters()), lr=LR))
        selected = common.parameters(model)
        assert {id(p) for g in opt.param_groups for p in g['params']} == {id(p) for p in selected}
        event('TRAINING', repetition=repetition, depth=depth, epoch=1, completed_updates=completed)
        for epoch in range(1, EPOCHS+1):
            order = np.random.default_rng(np.random.SeedSequence([seed, depth, epoch, 1])).permutation(COUNTS['train'])
            write_json(folder / f'ORDER_depth{depth}_epoch{epoch}.json', order.tolist())
            for position, index in enumerate(order, 1):
                try:
                    check_run(start)
                except (TimeoutError, InterruptedError):
                    common.save_checkpoint(folder / 'resume.pt', model, opt, seed=seed, depth_stage=depth,
                        epoch=epoch, position=position-1, completed_updates=completed,
                        plan_sha256=sha256(OUT / 'PLAN.json'))
                    raise
                index = int(index); spec = SPECS['train'][index]
                values = make_scene('train', index, plan['binding']['scale'])
                rng = np.random.default_rng(np.random.SeedSequence([seed, depth, epoch, index, 2]))
                snr = float(rng.uniform(-4, 6))
                public, truth, active, _ = common.inputs_for(values, plan['binding']['scale'], snr, rng)
                opt.zero_grad(set_to_none=True)
                outputs, _ = model(public, collect_diagnostics=False)
                loss, terms = conditional_loss(outputs, truth, active)
                if not bool(torch.isfinite(loss)):
                    raise FloatingPointError('Nonfinite objective; no scene is skipped')
                loss.backward(); norm = common.clip(selected); opt.step(); completed += 1
                row = dict(depth=depth, epoch=epoch, position=position, index=index,
                    condition=spec['condition'], users=spec['parameters']['users'], frames=spec['parameters']['frames'],
                    snr_db=snr, completed_updates=completed, total_updates=COUNTS['train']*EPOCHS*DEPTH,
                    loss=float(loss.detach()), last_layer_conditional_loss=float(terms[-1].detach()), gradient_norm=norm)
                with (folder / 'TRAINING.jsonl').open('a', encoding='utf-8') as stream:
                    stream.write(json.dumps(row, allow_nan=False)+'\n')
                if position % 500 == 0 or position == COUNTS['train']:
                    common.save_checkpoint(folder / 'resume.pt', model, opt, seed=seed, depth_stage=depth,
                        epoch=epoch, position=position, completed_updates=completed,
                        plan_sha256=sha256(OUT / 'PLAN.json'))
                if position % 20 == 0:
                    event('TRAINING', repetition=repetition, **row)
            assert state_sha(model.evidence) == original_classifier
        digest = common.save_checkpoint(folder / f'depth_{depth}.pt', model, seed=seed,
            completed_updates=completed, plan_sha256=sha256(OUT / 'PLAN.json'))
        stage_log.append(dict(depth=depth, updates=completed, weight_sha256=digest))
        write_json(folder / 'STAGES.json', stage_log)
    event('TRAINING_COMPLETE', repetition=repetition, updates=completed)
    del model, opt, selected, outputs, loss, terms; gc.collect(); torch.cuda.empty_cache()
    return str(folder / f'depth_{DEPTH}.pt')


def aggregate(rows):
    groups = {}
    for row in rows:
        key = (row['coverage'], row['users'], row['frames'], row['snr_db'])
        if key not in groups:
            groups[key] = dict(physical_scenes=0, **{name: 0 for name in row['metrics']})
        groups[key]['physical_scenes'] += 1
        for name, value in row['metrics'].items():
            groups[key][name] += value
    result = []
    for (coverage, users, frames, snr), totals in sorted(groups.items()):
        totals['user_decisions'] = totals.pop('users')
        result.append(dict(coverage=coverage, users=users, frames=frames, snr_db=snr,
            full_nmse_db=10*math.log10(totals['full_error']/totals['signal_energy']),
            conditional_nmse_db=10*math.log10(totals['conditional_error']/totals['signal_energy']),
            aer_percent=100*(totals['misses']+totals['false_alarms'])/totals['user_decisions'], **totals))
    return result


def evaluate(plan, first, evidence, checkpoints, start):
    for name, checkpoint_path in [('pretrained', None)]+[(f'seed{i}', p) for i, p in enumerate(checkpoints, 1)]:
        model = Receiver(evidence)
        for _ in range(DEPTH):
            model.add_layer(first['state_dict'])
        if checkpoint_path:
            blob = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
            assert blob['plan_sha256'] == sha256(OUT / 'PLAN.json')
            model.load_state_dict(blob['state'], strict=True); del blob
        model.cuda().eval().requires_grad_(False)
        for split in ('validation', 'test'):
            rows = []
            with torch.inference_mode():
                for index, spec in enumerate(SPECS[split]):
                    check_run(start); values = make_scene(split, index, plan['binding']['scale'])
                    for snr in SNRS:
                        check_run(start)
                        public, truth, active, preparation = common.inputs_for(values, plan['binding']['scale'], snr)
                        outputs, _ = model(public, collect_diagnostics=False)
                        row = dict(scene=index, seed=spec['seed'], condition=spec['condition'], coverage=spec['coverage'],
                            users=spec['parameters']['users'], frames=spec['parameters']['frames'], snr_db=snr,
                            metrics=common.metrics(outputs[-1], truth, active), noise_used=preparation['used_noise_variance'])
                        rows.append(row)
                        with (OUT / f'{split.upper()}_{name}.jsonl').open('a', encoding='utf-8') as stream:
                            stream.write(json.dumps(row, allow_nan=False)+'\n')
                    if (index+1) % 10 == 0:
                        event('EVALUATING', model=name, split=split, scenes=index+1, total=COUNTS[split])
            write_json(OUT / f'{split.upper()}_{name}.json', dict(model=name, depth=DEPTH,
                rows=rows, aggregate=aggregate(rows), checkpoint=checkpoint_path))
        del model, outputs; gc.collect(); torch.cuda.empty_cache()


def report():
    names = ['pretrained']+[f'seed{i}' for i in range(1, 4)]
    results = {n: read_json(OUT / f'TEST_{n}.json') for n in names}
    lines = ['# Mixed-condition progressive score-only training', '',
        'Material Passport: academic-research-suite / experiment-agent; completed conditional-receiver training.', '',
        'Known phase (oracle), estimated noise; only final depth-10 outputs are evaluated. '
        'The reference has identical message equations and the original frozen classifier with unchanged pretrained scores. '
        'It is not 600-iteration STMP. All three repetitions are reported; no automatic model selection or promotion.', '',
        '| Coverage | K | Q | SNR | Model | Full NMSE dB | AER % | Conditional NMSE dB |',
        '|---|---:|---:|---:|---|---:|---:|---:|']
    for name in names:
        for row in results[name]['aggregate']:
            lines.append(f"| {row['coverage']} | {row['users']} | {row['frames']} | {row['snr_db']} | {name} | "
                f"{row['full_nmse_db']:.4f} | {row['aer_percent']:.4f} | {row['conditional_nmse_db']:.4f} |")
    lines += ['', 'Descriptive results only. Intermediate unseen K/Q conditions test interpolation within the declared '
              'physical model; they do not establish transfer to different phase, activity or channel distributions.']
    (OUT / 'REPORT.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def run():
    if (OUT / 'RUN_START.json').exists():
        raise FileExistsError('Preserve the existing attempt; no automatic restart')
    plan = read_json(OUT / 'PLAN.json'); pre = read_json(OUT / 'PREFLIGHT.json')
    assert pre['status'] == 'PASS' and pre['plan_sha256'] == sha256(OUT / 'PLAN.json')
    verify(plan); setup('cuda'); threadpool_limits(4)
    start = time.monotonic()
    write_json(OUT / 'RUN_START.json', dict(pid=os.getpid(), utc=utc(), plan_sha256=sha256(OUT / 'PLAN.json')))
    try:
        first, evidence = common.load_sources(plan)
        checkpoints = [train_one(plan, first, evidence, i, seed, start) for i, seed in enumerate(SEEDS, 1)]
        write_json(OUT / 'TRAINING_DATA.json', dict(physical_scenes=COUNTS['train'],
            files={str(scene_path('train', i).relative_to(OUT)).replace('\\', '/'): sha256(scene_path('train', i))
                   for i in range(COUNTS['train'])}))
        verify(plan); evaluate(plan, first, evidence, checkpoints, start); report()
        current = common.protect_paths()
        changes = {k: dict(before=v, after=current.get(k)) for k, v in plan['frozen_assets'].items() if current.get(k) != v}
        write_json(OUT / 'FROZEN_AFTER.json', dict(files=current, changes=changes,
            note='This candidate writes only its independent output directory; concurrent changes are disclosed.'))
        event('COMPLETE', seconds=time.monotonic()-start, checkpoints=checkpoints, frozen_asset_changes=list(changes))
    except BaseException as error:
        write_json(OUT / 'FAILURE.json', dict(utc=utc(), error=repr(error), traceback=traceback.format_exc(),
            automatic_restart=False, elapsed_seconds=time.monotonic()-start))
        event('INTERRUPTED' if isinstance(error, InterruptedError) else 'FAILED', error=repr(error))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('action', choices=['prepare', 'preflight', 'run', 'report'])
    globals()[parser.parse_args().action]()
