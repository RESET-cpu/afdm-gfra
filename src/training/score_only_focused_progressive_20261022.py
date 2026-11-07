"""Fresh score-only progressive training at one fixed K/Q configuration."""
from __future__ import annotations
import argparse
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
sys.path.insert(0, str(ROOT/'src'))
from algorithm.candidates.score_only_progressive_20261022 import Receiver, conditional_loss
from algorithm.STMP.activity import Config, EvidenceNetwork, SCHEMA, FEATURE_DEFINITION_FROZEN
from algorithm.proposed.inputs import prepare_public
from evaluation.observations import observation
from evaluation.receivers import setup
from system.phase import phase_operator
from utils import read_json, write_json, sha256, state_sha

OUT = ROOT/'result/candidates/score_only_focused_progressive_20261022'
SOURCE = ROOT/'src/algorithm/candidates/score_only_progressive_20261022.py'
SNRS = [-4, -2, 0, 2, 4, 6]
BASES = dict(train=202610228100001, validation=202610228200001, test=202610228300001, preflight=202610228400001)
COUNTS = dict(train=3000, validation=600, test=2000)
SEEDS = [202610228700001, 202610228700002, 202610228700003]
PARAMETERS = dict(users=40, frames=16, activity_probability=.1, snr_db=0.)
EPOCHS, DEPTH, LR, TIMEOUT = 2, 10, 2e-6, 96*3600


def utc():
    return datetime.now(timezone.utc).isoformat()


def status(stage, **values):
    row = dict(stage=stage, utc=utc(), pid=os.getpid(), **values)
    write_json(OUT/'STATUS.json', row)
    return row


def event(stage, **values):
    row = status(stage, **values)
    with (OUT/'events.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(row, allow_nan=False)+'\n')
    print(json.dumps(row, allow_nan=False), flush=True)


def protect_paths():
    config = read_json(ROOT/'src/configs/final/STMP.json')
    paths = [ROOT/'FINAL.json', ROOT/'MAINLINE.json']
    paths += sorted((ROOT/'src/configs/final').glob('*.json'))
    paths += sorted((ROOT/'src/algorithm/proposed').glob('*.py'))
    paths += sorted((ROOT/'src/algorithm/STMP').glob('*.py'))
    paths += [ROOT/config[key] for key in
              ('first_checkpoint', 'second_checkpoint', 'evidence_checkpoint')]
    paths += [Path(read_json(ROOT/'src/configs/final/models.json')['proposed']['checkpoint'])]
    return {str(path.relative_to(ROOT)).replace('\\', '/'): sha256(path) for path in paths}


def prepare():
    if (OUT/'PLAN.json').exists():
        raise FileExistsError('Preserve the existing trial plan')
    config = read_json(ROOT/'src/configs/final/STMP.json')
    binding = {key: config[key] for key in ('scale', 'first_checkpoint',
        'first_checkpoint_sha256', 'evidence_checkpoint', 'evidence_checkpoint_sha256')}
    for key in ('first_checkpoint', 'evidence_checkpoint'):
        assert sha256(ROOT/binding[key]) == binding[key+'_sha256']
    scenes = {split: [BASES[split]+i for i in range(count)]
              for split,count in dict(**COUNTS,preflight=1).items()}
    flattened = [seed for group in scenes.values() for seed in group]
    assert len(set(flattened)) == len(flattened)
    for name in ('score_only_progressive_20261022', 'score_only_mixed_progressive_20261022'):
        old = read_json(ROOT/'result/candidates'/name/'PLAN.json')
        previous = {old['scene_base_seeds'][split]+i
                    for split,count in old['scene_counts'].items() for i in range(count)}
        assert not previous.intersection(flattened)
    write_json(OUT/'SCENES.json',dict(parameters=PARAMETERS,seeds=scenes,
        diversity='Independent physical geometry, fading, activity, and pilot draws within one fixed system configuration; SNR and noise are resampled per presentation.'))
    plan = dict(schema='score-only-focused-progressive-v1', created_utc=utc(),
        authorization='User authorized fresh Wei-style training and then rejected the scattered 30-condition design; fix K40/Q16/rho0.1 and increase independent physical realizations. Preserve score-only and frozen-classifier constraints.',
        binding=binding, physical_parameters=PARAMETERS, scene_counts=COUNTS,
        scene_base_seeds=BASES, random_seeds=SEEDS,
        scene_manifest_sha256=sha256(OUT/'SCENES.json'),
        diversity='One K40/Q16/rho0.1/off-grid NTN-TDL-D configuration; 3000 independent physical realizations, not a K/Q condition grid.',
        training=dict(maximum_depth=DEPTH, epochs_per_depth=EPOCHS,
            updates_per_seed=COUNTS['train']*EPOCHS*DEPTH,
            total_updates=COUNTS['train']*EPOCHS*DEPTH*len(SEEDS), learning_rate=LR,
            optimizer='Adam', betas=[.9,.999], eps=1e-8, weight_decay=0., max_gradient_norm=1.,
            batch='one complete 40-user physical scene; neural microbatches do not cause optimizer steps',
            trainable='all score parameters in all currently available layers from the first update at that depth',
            initialization='each newly added score is an independent copy of the original pretrained first-score checkpoint',
            classifier='one shared pretrained STMP evidence network, frozen weights, unchanged forward features; input gradient through its mean is enabled',
            scalars='alpha=beta=gamma=1 at every depth, fixed; no old learned calibration is loaded',
            objective='sum_l w_l * sum_active ||mu_l-h||^2 / sum_active ||h||^2; w_new=1, w_previous=.2; no BCE',
            snr_db='Uniform[-4,6] independently at each training presentation',
            noise='fresh proper complex Gaussian draw per presentation',
            optimizer_state='retain Adam moments for existing layers; add new score parameters at each depth',
            checkpoints='Every 500 updates and epoch boundary, plus completed depths; no intermediate performance evaluation.',
            independent_repetitions='shuffle, SNR, and training-noise seeds; identical pretrained initialization',
            activation_checkpointing=True, tf32=False),
        phase_mode='known (oracle phase supplied to isolate the conditional receiver)',
        noise_mode='estimated from observations in both training and evaluation',
        evaluation=dict(depth=DEPTH, snr_db=SNRS,
            policy='after all three final-depth trainings; no intermediate validation, best-epoch or best-seed selection',
            comparison='three final candidates vs the same ten-layer receiver with all scores left at original pretraining',
            pairing='same physical scenes and standardized noise across SNR and methods',
            metrics=['full NMSE','active conditional NMSE','AER','misses','false alarms'],
            validation='600 held-out scenes, descriptive only, no subsequent adaptation',
            test='2000 held-out scenes, generated after training, 12000 inputs per method'),
        literature=dict(wei='https://arxiv.org/html/2610.17785v1#S3.SS4',
            supported='progressive depth; joint training with preceding layers; auxiliary weighted normalized error',
            project_choices='10 layers, frozen shared classifier, active conditional loss, fixed scalars, scene counts, SNR range, epochs, optimizer and learning rate; these are not author-reported hyperparameters'),
        timeout_seconds=TIMEOUT,
        frozen_assets=protect_paths(),
        source_sha256={str(path.relative_to(ROOT)).replace('\\','/'):sha256(path)
            for path in [Path(__file__), SOURCE, ROOT/'src/evaluation/observations.py',
                         ROOT/'src/evaluation/receivers.py', ROOT/'src/utils.py',
                         *sorted((ROOT/'src/networks').rglob('*.py')),
                         *sorted((ROOT/'src/system').rglob('*.py'))]},
        old_trial='The single-condition 400-scene run remains interrupted; the 30-condition proposal was superseded before training. Neither set of weights is resumed.',
        material_passport=dict(origin='academic-research-suite / experiment-agent', mode='run', status='prospective'))
    write_json(OUT/'PLAN.json', plan)
    event('PREPARED', updates=plan['training']['total_updates'], counts=COUNTS)


def verify_sources(plan):
    if sha256(OUT/'SCENES.json') != plan['scene_manifest_sha256']:
        raise ValueError('Scene manifest changed')
    for key, expected in plan['source_sha256'].items():
        if sha256(ROOT/key) != expected:
            raise ValueError('Candidate source changed: '+key)
    # Numerical dependencies must match. Unrelated concurrent metadata changes
    # are recorded separately instead of interrupting an independent training.
    for key, expected in plan['frozen_assets'].items():
        if key.startswith('src/algorithm/proposed/') or key in (
                'src/algorithm/STMP/activity.py', 'src/configs/final/receiver.json',
                plan['binding']['first_checkpoint'], plan['binding']['evidence_checkpoint']):
            if sha256(ROOT/key) != expected:
                raise ValueError('Bound numerical dependency changed: '+key)


def load_sources(plan):
    binding = plan['binding']
    first = torch.load(ROOT/binding['first_checkpoint'], map_location='cpu', weights_only=False)
    evidence = torch.load(ROOT/binding['evidence_checkpoint'], map_location='cpu', weights_only=False)
    assert first['order'] == 1 and first['normalization'] == 'population_rms'
    assert evidence['schema'] == SCHEMA and evidence['feature_definition'] == FEATURE_DEFINITION_FROZEN
    assert evidence['training_class_prior'] == .5
    assert evidence['first_sha256'] == binding['first_checkpoint_sha256']
    assert first['global_complex_rms'] == evidence['scale'] == binding['scale']
    return first, evidence


def scene_path(split, index):
    return OUT/'data'/split/f'{index:04d}.npz'


def make_scene(split, index, scale):
    path = scene_path(split, index)
    if path.exists():
        with np.load(path, allow_pickle=False) as saved:
            values = dict(saved)
        assert int(values['seed']) == BASES[split]+index
        return values
    inputs, truth, metadata = observation(BASES[split]+index, PARAMETERS, scale)
    operator = phase_operator(inputs.pilot, truth['phase_slopes'])
    clean = np.einsum('qkn,kmrn->qmr', operator, truth['channel'], optimize=False)
    values = dict(seed=np.array(BASES[split]+index), a=operator, clean=clean,
        epsilon=(inputs.observation-clean)/np.sqrt(metadata['generated_noise_variance']),
        rho=np.array(inputs.activity_prior), channel=truth['channel'], activity=truth['activity'])
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    with temporary.open('wb') as stream:
        np.savez(stream, **values)
    temporary.replace(path)
    write_json(path.with_suffix('.json'), dict(seed=BASES[split]+index,
        sha256=sha256(path), physical_metadata=metadata))
    return values


def inputs_for(values, scale, snr, rng=None):
    clean = values['clean']
    power = float(np.mean(abs(clean)**2))
    noise = power*10**(-snr/10)
    epsilon = values['epsilon'] if rng is None else (
        rng.normal(size=clean.shape)+1j*rng.normal(size=clean.shape))/np.sqrt(2)
    public, preparation = prepare_public(dict(y=clean+np.sqrt(noise)*epsilon,
        a=values['a'], rho=values['rho']), scale, 'cuda', phase_mode='known', noise_mode='estimated')
    channel = values['channel']/scale
    truth = torch.tensor(np.stack((channel.real, channel.imag), axis=1), dtype=torch.float32, device='cuda')
    activity = torch.tensor(values['activity'], dtype=torch.float32, device='cuda')
    assert bool(activity.sum() > 0)
    return public, truth, activity, preparation


def parameters(model):
    selected = [p for name,p in model.named_parameters() if p.requires_grad]
    assert selected and all('.score.' in name for name,p in model.named_parameters() if p.requires_grad)
    return selected


def optimizer(selected):
    return torch.optim.Adam(selected, lr=LR, betas=(.9,.999), eps=1e-8,
                            weight_decay=0., fused=True)


def clip(selected):
    # Accumulation in float64 avoids a float32 norm overflow on finite gradients.
    norm = torch.stack([torch.linalg.vector_norm(p.grad, dtype=torch.float64)
                        for p in selected if p.grad is not None]).norm()
    if not bool(torch.isfinite(norm)):
        raise FloatingPointError('Nonfinite training gradient')
    with torch.no_grad():
        coefficient = (1/(norm+1e-6)).clamp(max=1.)
        torch._foreach_mul_([p.grad for p in selected if p.grad is not None], coefficient.to(torch.float32))
    return float(norm)


def save_checkpoint(path, model, opt=None, **metadata):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    # Synchronous torch.save completes before any subsequent parameter update.
    torch.save(dict(schema='score-only-focused-progressive-v1', depth=len(model.layers),
        state=model.state_dict(), optimizer=None if opt is None else opt.state_dict(),
        **metadata), temporary)
    temporary.replace(path)
    return sha256(path)


def preflight():
    if (OUT/'PREFLIGHT.json').exists():
        raise FileExistsError('Preserve preflight evidence')
    plan = read_json(OUT/'PLAN.json'); verify_sources(plan)
    setup('cuda'); threadpool_limits(4); torch.manual_seed(SEEDS[0])
    first, evidence = load_sources(plan)
    started = time.monotonic()
    values = make_scene('preflight', 0, plan['binding']['scale'])
    generation_seconds = time.monotonic()-started
    public, truth, active, _ = inputs_for(values, plan['binding']['scale'], 0.)
    model = Receiver(evidence)
    for _ in range(DEPTH):
        model.add_layer(first['state_dict'])
    assert all(layer.activity is model.evidence for layer in model.layers)
    assert len({next(layer.score.parameters()).data_ptr() for layer in model.layers}) == DEPTH
    assert all(all(torch.equal(value, first['state_dict'][key])
                   for key,value in layer.score.state_dict().items()) for layer in model.layers)
    assert all(torch.equal(layer.calibration, torch.zeros(3)) for layer in model.layers)
    model.cuda().train(); before = state_sha(model.evidence)
    original = EvidenceNetwork(Config(**evidence['config'])).cuda().eval()
    original.load_state_dict(evidence['state_dict']); original.requires_grad_(False)
    # Check both feature equality and the restored derivative using a real query.
    from algorithm.proposed import components
    prior = public['y'].new_zeros(public['channel_shape'])
    from algorithm.proposed.configuration import CONFIG
    variance = public['y'].new_tensor(public['rho']*CONFIG['normalized_training_second_moment'])
    q,v,_ = components.linear_query(public, prior, variance, model.layers[0].c_gamma)
    with torch.no_grad():
        mu = q+v/2*model.layers[0].score(q,v.expand(len(q)))
    mu.requires_grad_(True)
    actual = model.evidence(q,v.expand(len(q)),mu,public['rho'])
    expected = original(q,v.expand(len(q)),mu)+math.log(public['rho']/(1-public['rho']))
    assert torch.equal(actual, expected), 'Classifier forward changed'
    derivative = torch.autograd.grad(actual.sum(), mu)[0]
    assert bool(torch.isfinite(derivative).all() & (derivative.abs().max()>0))
    selected = parameters(model); opt = optimizer(selected)
    torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); started = time.monotonic()
    outputs,_ = model(public, collect_diagnostics=False)
    loss,terms = conditional_loss(outputs,truth,active)
    loss.backward()
    norms = [float(torch.stack([torch.linalg.vector_norm(p.grad, dtype=torch.float64)
             for p in layer.score.parameters() if p.grad is not None]).norm()) for layer in model.layers]
    assert all(np.isfinite(n) and n>0 for n in norms)
    assert all(p.grad is None for name,p in model.named_parameters() if '.score.' not in name)
    norm = clip(selected)
    probes = [(next(layer.score.parameters()),next(layer.score.parameters()).detach().clone()) for layer in model.layers]
    opt.step(); torch.cuda.synchronize()
    assert all(not torch.equal(p.detach(),saved) for p,saved in probes)
    assert state_sha(model.evidence) == before
    assert all(torch.equal(layer.calibration.detach().cpu(),torch.zeros(3)) for layer in model.layers)
    report = dict(status='PASS', utc=utc(), plan_sha256=sha256(OUT/'PLAN.json'),
        ten_layer_seconds=time.monotonic()-started, generation_seconds=generation_seconds,
        peak_allocated_mib=torch.cuda.max_memory_allocated()/2**20,
        original_pretrained_scores_exact=True, independent_score_parameters=True,
        shared_classifier_exact_forward=True, shared_classifier_unchanged=True,
        classifier_input_gradient_max=float(derivative.abs().max()),
        all_ten_score_gradient_norms=norms, gradient_norm_before_clipping=norm,
        all_ten_scores_updated=True, all_calibrations_one_and_frozen=True,
        preflight_update_discarded=True, performance_evaluation=False,
        loss=float(loss.detach()), conditional_loss_terms=[float(t.detach()) for t in terms])
    verify_sources(plan); write_json(OUT/'PREFLIGHT.json', report)
    event('PREFLIGHT_PASS', seconds=report['ten_layer_seconds'], peak_allocated_mib=report['peak_allocated_mib'])


def check_run(start):
    if time.monotonic()-start > TIMEOUT:
        raise TimeoutError('Declared 96-hour bound reached; checkpoints retained')
    if (OUT/'STOP_REQUESTED').exists():
        raise InterruptedError('User-requested stop; checkpoints retained')


def train_one(plan, first, evidence, repetition, seed, start):
    torch.manual_seed(seed)
    folder = OUT/f'seed{repetition}'
    folder.mkdir(exist_ok=False)
    model = Receiver(evidence)
    original_classifier = state_sha(model.evidence)
    opt = None; completed = 0; stage_log = []
    for depth in range(1, DEPTH+1):
        model.add_layer(first['state_dict']); model.cuda().train()
        if opt is None:
            opt = optimizer(parameters(model))
        else:
            opt.add_param_group(dict(params=list(model.layers[-1].score.parameters()),lr=LR))
        selected = parameters(model)
        assert {id(p) for group in opt.param_groups for p in group['params']} == {id(p) for p in selected}
        event('TRAINING', repetition=repetition, depth=depth, epoch=1, completed_updates=completed)
        for epoch in range(1,EPOCHS+1):
            order = np.random.default_rng(np.random.SeedSequence([seed,depth,epoch,1])).permutation(COUNTS['train'])
            write_json(folder/f'ORDER_depth{depth}_epoch{epoch}.json', order.tolist())
            for position,index in enumerate(order,1):
                try:
                    check_run(start)
                except (TimeoutError, InterruptedError):
                    save_checkpoint(folder/'resume.pt',model,opt,seed=seed,depth_stage=depth,
                        epoch=epoch,position=position-1,completed_updates=completed,
                        plan_sha256=sha256(OUT/'PLAN.json'))
                    raise
                values = make_scene('train',int(index),plan['binding']['scale'])
                rng = np.random.default_rng(np.random.SeedSequence([seed,depth,epoch,int(index),2]))
                snr = float(rng.uniform(-4,6))
                public,truth,active,_ = inputs_for(values,plan['binding']['scale'],snr,rng)
                opt.zero_grad(set_to_none=True)
                outputs,_ = model(public,collect_diagnostics=False)
                loss,terms = conditional_loss(outputs,truth,active)
                if not bool(torch.isfinite(loss)):
                    raise FloatingPointError('Nonfinite objective; no sample is skipped')
                loss.backward(); norm=clip(selected); opt.step(); completed+=1
                row=dict(depth=depth,epoch=epoch,position=position,index=int(index),snr_db=snr,
                    completed_updates=completed,loss=float(loss.detach()),
                    last_layer_conditional_loss=float(terms[-1].detach()),gradient_norm=norm)
                with (folder/'TRAINING.jsonl').open('a',encoding='utf-8') as stream:
                    stream.write(json.dumps(row,allow_nan=False)+'\n')
                if position%500 == 0 or position == COUNTS['train']:
                    save_checkpoint(folder/'resume.pt',model,opt,seed=seed,depth_stage=depth,
                        epoch=epoch,position=position,completed_updates=completed,plan_sha256=sha256(OUT/'PLAN.json'))
                if position%20 == 0:
                    event('TRAINING',repetition=repetition,**row)
            assert state_sha(model.evidence)==original_classifier
        digest=save_checkpoint(folder/f'depth_{depth}.pt',model,seed=seed,
            completed_updates=completed,plan_sha256=sha256(OUT/'PLAN.json'))
        stage_log.append(dict(depth=depth,updates=completed,weight_sha256=digest))
        write_json(folder/'STAGES.json',stage_log)
    event('TRAINING_COMPLETE',repetition=repetition,updates=completed)
    del model,opt,selected,outputs,loss,terms
    gc.collect(); torch.cuda.empty_cache()
    return str(folder/f'depth_{DEPTH}.pt')


def metrics(output, truth, active):
    truth=truth.double(); mask=active.bool()
    full=(output['estimate'].double()-truth).square().flatten(1).sum(1)
    conditional=(output['conditional'].double()-truth).square().flatten(1).sum(1)
    p=output['logits'].sigmoid(); decisions=p>=.5
    return dict(full_error=float(full.sum()),conditional_error=float(conditional[mask].sum()),
        signal_energy=float(truth.square().sum()),inactive_error=float(full[~mask].sum()),
        misses=int((mask & ~decisions).sum()),false_alarms=int((~mask & decisions).sum()),
        active=int(mask.sum()),users=len(mask))


def aggregate(rows):
    result=[]
    for snr in SNRS:
        group=[row for row in rows if row['snr_db']==snr]
        totals={key:sum(row['metrics'][key] for row in group) for key in group[0]['metrics']}
        result.append(dict(snr_db=snr,physical_scenes=len(group),
            full_nmse_db=10*math.log10(totals['full_error']/totals['signal_energy']),
            conditional_nmse_db=10*math.log10(totals['conditional_error']/totals['signal_energy']),
            aer_percent=100*(totals['misses']+totals['false_alarms'])/totals['users'],**totals))
    return result


def evaluate(plan,first,evidence,checkpoints,start):
    for split in ('validation','test'):
        for index in range(COUNTS[split]):
            check_run(start); make_scene(split,index,plan['binding']['scale'])
            if (index+1)%20==0:
                event('GENERATING_EVALUATION',split=split,completed=index+1,total=COUNTS[split])
    for name,checkpoint_path in [('pretrained',None)]+[(f'seed{i}',path) for i,path in enumerate(checkpoints,1)]:
        model=Receiver(evidence)
        for _ in range(DEPTH): model.add_layer(first['state_dict'])
        if checkpoint_path:
            blob=torch.load(checkpoint_path,map_location='cpu',weights_only=False)
            assert blob['plan_sha256']==sha256(OUT/'PLAN.json')
            model.load_state_dict(blob['state'],strict=True)
            del blob
        model.cuda().eval().requires_grad_(False)
        for split in ('validation','test'):
            rows=[]
            with torch.inference_mode():
                for index in range(COUNTS[split]):
                    values=make_scene(split,index,plan['binding']['scale'])
                    for snr in SNRS:
                        check_run(start)
                        public,truth,active,preparation=inputs_for(values,plan['binding']['scale'],snr)
                        outputs,_=model(public,collect_diagnostics=False)
                        rows.append(dict(scene=index,seed=BASES[split]+index,snr_db=snr,
                            metrics=metrics(outputs[-1],truth,active),noise_used=preparation['used_noise_variance']))
                    if (index+1)%10==0:
                        write_json(OUT/f'{split.upper()}_{name}_partial.json',dict(rows=rows))
                        event('EVALUATING',model=name,split=split,scenes=index+1,total=COUNTS[split])
            write_json(OUT/f'{split.upper()}_{name}.json',dict(model=name,depth=DEPTH,
                rows=rows,aggregate=aggregate(rows),checkpoint=checkpoint_path))
        del model,outputs
        gc.collect(); torch.cuda.empty_cache()


def report():
    names=['pretrained']+[f'seed{i}' for i in range(1,4)]
    results={name:read_json(OUT/f'TEST_{name}.json') for name in names}
    lines=['# Fixed-condition progressive score-only training', '',
        'Material Passport: academic-research-suite / experiment-agent; completed fixed-condition receiver training.', '',
        'Known phase (oracle), estimated noise. Only depth-10 outputs are evaluated. '
        'The reference uses the same shared frozen STMP classifier and unchanged pretrained scores. '
        'It is not the 600-iteration STMP baseline. No candidate is promoted automatically.', '',
        '| SNR (dB) | Model | Full NMSE (dB) | AER (%) | Conditional NMSE (dB) |',
        '|---:|---|---:|---:|---:|']
    for snr in SNRS:
        for name in names:
            row=next(r for r in results[name]['aggregate'] if r['snr_db']==snr)
            lines.append(f"| {snr} | {name} | {row['full_nmse_db']:.4f} | {row['aer_percent']:.4f} | {row['conditional_nmse_db']:.4f} |")
    lines+=['', 'All three repetitions are retained. These descriptive values do not establish a general stability guarantee. '
            'Report generation performs no model selection or further training.']
    (OUT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def run():
    if (OUT/'RUN_START.json').exists():
        raise FileExistsError('Preserve the prior attempt; no automatic restart')
    plan=read_json(OUT/'PLAN.json'); pre=read_json(OUT/'PREFLIGHT.json')
    assert pre['status']=='PASS' and pre['plan_sha256']==sha256(OUT/'PLAN.json')
    verify_sources(plan); setup('cuda'); threadpool_limits(4)
    start=time.monotonic()
    write_json(OUT/'RUN_START.json',dict(pid=os.getpid(),utc=utc(),plan_sha256=sha256(OUT/'PLAN.json')))
    try:
        first,evidence=load_sources(plan)
        checkpoints=[train_one(plan,first,evidence,i,seed,start) for i,seed in enumerate(SEEDS,1)]
        write_json(OUT/'TRAINING_DATA.json',dict(physical_scenes=COUNTS['train'],
            files={str(scene_path('train',i).relative_to(OUT)).replace('\\','/'):
                   sha256(scene_path('train',i)) for i in range(COUNTS['train'])}))
        verify_sources(plan)
        evaluate(plan,first,evidence,checkpoints,start)
        report()
        current=protect_paths()
        changes={key:dict(before=value,after=current.get(key)) for key,value in plan['frozen_assets'].items() if current.get(key)!=value}
        write_json(OUT/'FROZEN_AFTER.json',dict(files=current,changes=changes,
            note='Independent concurrent tasks may change mainline metadata; this candidate never writes any frozen path.'))
        event('COMPLETE',seconds=time.monotonic()-start,checkpoints=checkpoints,
              frozen_asset_changes=list(changes))
    except BaseException as error:
        write_json(OUT/'FAILURE.json',dict(utc=utc(),error=repr(error),traceback=traceback.format_exc(),
            automatic_restart=False,elapsed_seconds=time.monotonic()-start))
        event('INTERRUPTED' if isinstance(error,InterruptedError) else 'FAILED',error=repr(error))
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('action',choices=['prepare','preflight','run','report'])
    globals()[parser.parse_args().action]()
