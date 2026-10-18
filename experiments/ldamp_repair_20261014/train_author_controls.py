"""Matched AFDM training controls informed by the checked author reference.

These are development experiments, not an exact MATLAB optimizer reproduction.
PyTorch BatchNorm/Adam are retained and their differences are recorded.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
from torch import nn
import numpy as np
import torch
from author_reference import AuthorDnCNN

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from afdm_jadcedd.algorithm.baselines.ldamp.network import DnCNN
from representation import Representation,beam_transform

REPRESENTATION=Representation()

spec=importlib.util.spec_from_file_location('training',ROOT/'scripts/train_ldamp.py')
training=importlib.util.module_from_spec(spec);spec.loader.exec_module(training)


class DirectAuthorCNN(nn.Module):
    """Same convolutional backbone, predicting clean signal directly.

    This is a declared AFDM denoiser adaptation, not original DnCNN residual
    training. It tests whether low-SNR identity cancellation impedes learning.
    """
    def __init__(self,channels):
        super().__init__()
        self.backbone=AuthorDnCNN(channels=channels)
        with torch.no_grad():
            self.backbone.noise[-1].weight.zero_()
            self.backbone.noise[-1].bias.zero_()

    def forward(self,value):return self.backbone.noise(value)


def save(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n')


def batch(bank,indices,rng,recipe,scale,channels):
    x,target,active=training.make_batch(bank,indices,rng,recipe,scale)
    if recipe.get('representation')=='beam_time_lag_dft':
        transformed=[]
        for value in (x,target):
            complex_value=value[:,:16].numpy()+1j*value[:,16:].numpy()
            beam=beam_transform(complex_value)
            transformed.append(torch.from_numpy(np.concatenate([beam.real,beam.imag],axis=1).astype(np.float32)))
        x,target=transformed
    antenna=np.arange(len(indices))%16
    if channels==2:
        rows=np.arange(len(indices))
        x=torch.stack([x[rows,antenna],x[rows,antenna+16]],dim=1)
        target=torch.stack([target[rows,antenna],target[rows,antenna+16]],dim=1)
    if recipe.get('representation') in ('time_lag_dft','beam_time_lag_dft'):
        x=torch.from_numpy(REPRESENTATION.pack_transform(x))
        target=torch.from_numpy(REPRESENTATION.pack_transform(target))
    return x,target,active


@torch.inference_mode()
def validate(model,bank,recipe,scale,channels,device):
    model.eval();rng=np.random.default_rng(recipe['validation_seed'])
    error=power=active_error=inactive_error=coordinates=0
    count=recipe.get('validation_count',512)
    for start in range(0,count,recipe['batch_size']):
        indices=np.arange(start,min(start+recipe['batch_size'],count))
        x,target,active=batch(bank,indices,rng,recipe,scale,channels)
        pred=model(x.to(device)).cpu().double();target=target.double()
        errors=(pred-target).square().sum(dim=(1,2,3)).numpy()
        error+=errors.sum();power+=float(target.square().sum());coordinates+=target.numel()
        active_error+=errors[active].sum();inactive_error+=errors[~active].sum()
    return dict(mse=float(error/coordinates),zero_mse=power/coordinates,
                error_over_zero=float(error/power),active_nmse_db=float(10*np.log10(active_error/power)),
                inactive_error_fraction_of_signal=float(inactive_error/power))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--config',type=Path,default=ROOT/'configs/training/ldamp.json')
    parser.add_argument('--steps',type=int,default=500)
    parser.add_argument('--extended',action='store_true')
    parser.add_argument('--representation',choices=['afdm','time_lag_dft','beam_time_lag_dft'],default='afdm')
    parser.add_argument('--only',default=None,help='Comma-separated declared variant names')
    parser.add_argument('--validation-users',type=int,default=512)
    parser.add_argument('--device',choices=['cpu','mps'],default='mps')
    parser.add_argument('--seed',type=int,default=202610146101)
    parser.add_argument('--validation-seed',type=int,default=202610146102)
    parser.add_argument('--batch-size',type=int,default=32)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(1);device=args.device
    recipe=json.loads(args.config.read_text())
    config=json.loads((ROOT/recipe['receiver_config']).read_text())
    if args.batch_size<16 or args.batch_size%16:raise ValueError('Batch size must cover all 16 spatial coordinates evenly')
    recipe.update(batch_size=args.batch_size,noise_complex_variance=[1.,10.],network_input_scale=float(np.sqrt(1+np.sqrt(10.))),
                  validation_seed=args.validation_seed,representation=args.representation,validation_count=args.validation_users,
                  population_scale=config['scale'])
    variants=[dict(name='default32_mean',kind='default',channels=32,objective='mean'),
              dict(name='author32_mean',kind='author',channels=32,objective='mean'),
              dict(name='author32_sum',kind='author',channels=32,objective='sum'),
              dict(name='author2_sum',kind='author',channels=2,objective='sum')]
    if args.extended:
        variants=[dict(name='author2_residual_extended',kind='author',channels=2,objective='sum'),
                  dict(name='author32_direct_extended',kind='direct',channels=32,objective='sum'),
                  dict(name='author2_direct_extended',kind='direct',channels=2,objective='sum')]
    if args.only:
        requested=args.only.split(',')
        variants=[v for v in variants if v['name'] in requested]
        if len(variants)!=len(requested):raise ValueError('Unknown or repeated variant')
    plan=dict(steps=args.steps,variants=variants,seed=args.seed,recipe=recipe,validation_samples=args.validation_users,device=device,
              learning_rate=1e-3,scope=__doc__,
              differences_from_matlab=['PyTorch batch variance running estimator rather than stored mean/std moments',
                'PyTorch Adam epsilon/bias correction convention',f'Batch {args.batch_size} without subbatches',
                'Fixed AFDM scales, activity mixture and log-uniform complex variance retained for matched controls'],
              comparison='32-channel controls share complete data/noise streams. Two-channel control selects one antenna from the same queries; it is not matched in per-update information.',
              source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(__file__).with_name('author_reference.py'),Path(__file__).with_name('representation.py'),ROOT/'scripts/train_ldamp.py']})
    save(args.output/'PLAN.json',plan)
    banks={split:np.load(ROOT/recipe[split+'_path'],mmap_mode='r') for split in ['train','validation']}
    ids={split:np.load(ROOT/recipe[split+'_identities']) for split in banks}
    assert not np.intersect1d(ids['train'][:,0],ids['validation'][:,0]).size
    history=[];summary=[];started=time.time()
    for variant in variants:
        torch.manual_seed(plan['seed']);rng=np.random.default_rng(plan['seed'])
        if variant['kind']=='default':model=DnCNN()
        elif variant['kind']=='direct':model=DirectAuthorCNN(variant['channels'])
        else:model=AuthorDnCNN(channels=variant['channels'])
        model=model.to(device)
        optimizer=torch.optim.Adam(model.parameters(),lr=plan['learning_rate'])
        scheduler=torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer,patience=4,factor=.5,min_lr=1e-5)
        best=float('inf');chosen=None;state=None
        for step in range(args.steps+1):
            if step:
                model.train()
                indices=rng.integers(len(banks['train']),size=recipe['batch_size'])
                x,target,_=batch(banks['train'],indices,rng,recipe,config['scale'],variant['channels'])
                optimizer.zero_grad(set_to_none=True)
                residual=model(x.to(device))-target.to(device)
                loss=residual.square().mean() if variant['objective']=='mean' else residual.square().sum()/2
                if not torch.isfinite(loss):raise FloatingPointError('Nonfinite training loss')
                loss.backward();optimizer.step()
            if step%100==0 or step==args.steps:
                metrics=validate(model,banks['validation'],recipe,config['scale'],variant['channels'],device)
                row=dict(variant=variant['name'],step=step,metrics=metrics,seconds=time.time()-started,
                         learning_rate=optimizer.param_groups[0]['lr'])
                history.append(row)
                if metrics['mse']<best:
                    best=metrics['mse'];chosen=row;state=training.cpu_state(model.state_dict())
                save(args.output/'HISTORY.json',history)
                save(args.output/'STATUS.json',dict(status='TRAINING',variant=variant['name'],step=step))
                print(json.dumps(row),flush=True)
                if args.extended and step:scheduler.step(metrics['mse'])
        torch.save(dict(model=state,chosen=chosen,variant=variant,recipe=recipe),args.output/(variant['name']+'.pt'))
        summary.append(chosen);save(args.output/'SUMMARY.json',summary)
    save(args.output/'STATUS.json',dict(status='COMPLETE',elapsed_seconds=time.time()-started,
         receiver_validated=False,mainline_installed=False))


if __name__=='__main__':main()
