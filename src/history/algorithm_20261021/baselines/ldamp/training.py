"""Reproduce the declared two-channel, five-interval DnCNN training workflow.

The checked research scripts implement initialization, physical sampling,
interval training, and training-only BN moment calibration. This entry point
runs them into one fresh artifact, snapshots their sources, verifies disjoint
physical scene identities, and writes a configuration awaiting receiver tests.
It never changes the installed default or fits an activity threshold.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import numpy as np
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.utils import sha256,write_json


def run(args):
    recipe=json.loads(Path(args.config).read_text())
    if recipe.get('schema')!='ldamp-beam-dncnn-training-v2':raise ValueError('Two-channel beam training recipe required')
    if recipe['noise_boundaries']!=[.001,.01,.1,1.,10.,100.]:raise ValueError('Declared five noise intervals required')
    output=Path(args.output).resolve();output.mkdir(parents=True,exist_ok=False)
    script_dir=ROOT/'experiments/ldamp_repair_20261014'
    helpers=['train_author_controls.py','check_population_bn.py','train_beam_bank.py','author_reference.py','representation.py']
    source_files=[script_dir/name for name in helpers]+[ROOT/'scripts/train_ldamp.py',Path(__file__)]
    sources={str(p.relative_to(ROOT)):sha256(p) for p in source_files}
    (output/'sources').mkdir()
    for source in source_files:shutil.copy2(source,output/'sources'/source.name)
    prior=json.loads((ROOT/recipe['prior_definition']).read_text())
    data_hashes={split:sha256(ROOT/recipe[split+'_path']) for split in ['train','validation']}
    if data_hashes!=prior['sample_files_sha256']:raise ValueError('Physical channel bank hash mismatch')
    ids={split:np.load(ROOT/recipe[split+'_identities']) for split in ['train','validation']}
    if np.intersect1d(ids['train'][:,0],ids['validation'][:,0]).size:raise ValueError('Overlapping physical training and validation scenes')
    for split in ids:
        data=np.load(ROOT/recipe[split+'_path'],mmap_mode='r')
        if data.shape[1:]!=(16,16,16) or len(data)!=len(ids[split]):raise ValueError('Incomplete full-channel training bank')
    smoke=bool(args.smoke);start=time.time()
    base_steps=2 if smoke else recipe['pretraining_steps'];interval_steps=2 if smoke else recipe['interval_steps']
    validation_users=64 if smoke else recipe['validation_users'];bn_batches=2 if smoke else recipe['population_bn_batches']
    plan=dict(scope=__doc__,recipe=recipe,smoke=smoke,device=args.device,source_sha256=sources,data_sha256=data_hashes,
        steps=dict(pretraining=base_steps,per_interval=interval_steps),validation_users=validation_users,population_bn_batches=bn_batches,
        selection='The base interval uses one fixed spatial coordinate per validation user during training, followed by all-coordinate validation after population BN. Further intervals select on all 16 coordinates.',
        mainline_installed=False,receiver_validated=False)
    write_json(output/'PLAN.json',plan);write_json(output/'training_recipe.json',recipe)
    resume=Path(args.resume_from).resolve() if args.resume_from else None
    if resume:
        old=json.loads((resume/'PLAN.json').read_text())
        if old['recipe']!=recipe or old['smoke']!=smoke or old['source_sha256']!=sources:
            raise ValueError('Stage resume requires the same recipe, mode and source hashes')
    commands=[
        ('base',[sys.executable,str(script_dir/'train_author_controls.py'),'--config',str(output/'training_recipe.json'),
            '--output',str(output/'base'),'--extended','--only','author2_residual_extended','--representation','beam_time_lag_dft',
            '--steps',str(base_steps),'--validation-users',str(validation_users),'--device',args.device,
            '--seed',str(recipe['seed']),'--validation-seed',str(recipe['validation_seed']),'--batch-size',str(recipe['batch_size'])]),
        ('base_population',[sys.executable,str(script_dir/'check_population_bn.py'),'--output',str(output/'base_population'),
            '--sources',str(output/'base/author2_residual_extended.pt'),'--calibration-batches',str(bn_batches),
            '--seed',str(recipe['population_bn_seed']),'--device',args.device]),
        ('bank',[sys.executable,str(script_dir/'train_beam_bank.py'),'--output',str(output/'bank'),
            '--initial',str(output/'base_population/01_calibrated.pt'),'--steps',str(interval_steps),
            '--edges',*[str(v) for v in recipe['noise_boundaries']],'--validation-users',str(validation_users),
            '--calibration-batches',str(bn_batches),'--device',args.device,
            '--seed',str(recipe['interval_seed']),'--validation-seed',str(recipe['interval_validation_seed'])])]
    for name,command in commands:
        if resume and (resume/name/'STATUS.json').is_file() and json.loads((resume/name/'STATUS.json').read_text())['status']=='COMPLETE':
            shutil.copytree(resume/name,output/name)
            write_json(output/(name+'_REUSED.json'),dict(source=str(resume/name),status='COMPLETE'))
            continue
        write_json(output/'STATUS.json',dict(status='TRAINING',stage=name,seconds=time.time()-start,smoke=smoke))
        print(json.dumps(dict(stage=name,status='TRAINING')),flush=True)
        with (output/(name+'.log')).open('w') as log:
            result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        if result.returncode:
            write_json(output/'STATUS.json',dict(status='FAILED',stage=name,returncode=result.returncode,log=str(output/(name+'.log'))))
            raise RuntimeError(f'L-DAMP training stage {name} failed; see {output/(name+".log")}')
    manifest_path=output/'bank/BANK.json';bank=json.loads(manifest_path.read_text())
    receiver=dict(schema='afdm-ldamp-beam-v2',validation_status='SMOKE_ONLY' if smoke else 'TRAINED_NOT_RECEIVER_VALIDATED',
        bank_path=str(manifest_path),bank_sha256=sha256(manifest_path),scale=bank['scale'],batch_size=128,
        solver=dict(iterations=10,probes=8,divergence_seed=202610146201),readout=None,receiver_validation_passed=False,
        training_plan=str(output/'PLAN.json'),training_plan_sha256=sha256(output/'PLAN.json'),
        adaptation='Shared two-real-channel residual DnCNNs in fixed beam and invertible temporal coordinates; complex matrix L-DAMP with Monte Carlo partial traces.')
    write_json(output/'receiver.json',receiver)
    write_json(output/'STATUS.json',dict(status='COMPLETE_SMOKE' if smoke else 'COMPLETE',seconds=time.time()-start,
        mainline_installed=False,receiver_validated=False,receiver_configuration=str(output/'receiver.json')))
    return 0
