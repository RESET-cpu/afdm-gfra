"""Train the complete noise-interval bank for the beam-coordinate AFDM denoiser.

The architecture and residual objective follow the checked author reference.
Fixed unitary representations, two real channels, population normalization,
complex noise intervals, and EMA BatchNorm are declared project adaptations.
Only the existing disjoint training/validation channel banks are accessed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import time
import numpy as np
import torch
from author_reference import AuthorDnCNN
from train_author_controls import batch,training,ROOT
from check_population_bn import evaluate_all,calibrate


def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--steps',type=int,default=5000)
    p.add_argument('--initial',type=Path,default=ROOT/'results/ldamp_implementation_20261014/beam_population_bn_controls/01_calibrated.pt')
    p.add_argument('--edges',type=float,nargs='+',default=[.001,.01,.1,1.,10.,100.,1000.])
    p.add_argument('--validation-users',type=int,default=512)
    p.add_argument('--calibration-batches',type=int,default=256)
    p.add_argument('--device',choices=['cpu','mps'],default='mps')
    p.add_argument('--seed',type=int,default=202610146501)
    p.add_argument('--validation-seed',type=int,default=202610146502)
    args=p.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(1);device=args.device;seed=args.seed
    base=ROOT/args.initial
    initial=torch.load(base,map_location='cpu',weights_only=False)
    scale=initial['recipe'].get('population_scale',json.loads((ROOT/'configs/ldamp.json').read_text())['scale'])
    banks={s:np.load(ROOT/initial['recipe'][s+'_path'],mmap_mode='r') for s in ['train','validation']}
    ids={s:np.load(ROOT/initial['recipe'][s+'_identities']) for s in banks}
    assert not np.intersect1d(ids['train'][:,0],ids['validation'][:,0]).size
    edges=args.edges
    if edges not in ([.001,.01,.1,1.,10.,100.],[.001,.01,.1,1.,10.,100.,1000.]):
        raise ValueError('The declared five- or six-interval physical-noise recipe is required')
    plan=dict(scope=__doc__,seed=seed,steps=args.steps,edges=edges,scale=scale,
        initialization=str(base),initialization_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),device=device,
        batch_size=initial['recipe']['batch_size'],batchnorm_momentum=.1,learning_rate=3e-4,minimum_learning_rate=1e-5,
        validation=f'{args.validation_users} held-out user channels, all 16 beams; fixed AWGN and activity streams',
        selection='Minimum full-coordinate validation MSE, including final training-only BN calibration',
        bank_1_to_10='Reuses the already validated independently trained residual network',
        training_order=[i for i in [4,5,2,1,0] if i<len(edges)-1],mainline_installed=False,receiver_validated=False)
    (out/'sources').mkdir()
    for name in ['train_beam_bank.py','author_reference.py','train_author_controls.py','representation.py','check_population_bn.py']:
        shutil.copy2(Path(__file__).with_name(name),out/'sources'/name)
    save(out/'PLAN.json',plan)
    shutil.copy2(base,out/'band03.pt');entries={3:dict(path='band03.pt',bounds=edges[3:5],validation=initial['validation'])}
    history=[];start=time.time()
    def manifest():
        save(out/'BANK.json',dict(schema='beam-dncnn-bank-development-v1',scale=scale,
            representation='beam_time_lag_dft',edges=edges,complete=len(entries)==len(edges)-1,
            entries=[dict(index=i,**entries[i],sha256=hashlib.sha256((out/entries[i]['path']).read_bytes()).hexdigest()) for i in sorted(entries)]))
    manifest()
    for band in plan['training_order']:
        torch.manual_seed(seed+band);rng=np.random.default_rng(seed+band)
        model=AuthorDnCNN(channels=2).to(device);model.load_state_dict(initial['model'])
        for layer in model.modules():
            if isinstance(layer,torch.nn.BatchNorm2d):layer.momentum=.1
        recipe=dict(initial['recipe'],noise_complex_variance=edges[band:band+2],
            network_input_scale=float(np.sqrt(1+np.sqrt(edges[band]*edges[band+1]))),validation_seed=args.validation_seed,
            validation_count=args.validation_users)
        optimizer=torch.optim.Adam(model.parameters(),lr=plan['learning_rate'])
        scheduler=torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer,patience=2,factor=.5,min_lr=1e-5)
        best=float('inf');chosen=None;state=None
        for step in range(args.steps+1):
            if step:
                model.train();indices=rng.integers(len(banks['train']),size=recipe['batch_size'])
                x,target,_=batch(banks['train'],indices,rng,recipe,scale,2)
                optimizer.zero_grad(set_to_none=True)
                loss=(model(x.to(device))-target.to(device)).square().sum()/2
                if not torch.isfinite(loss):raise FloatingPointError('Nonfinite training objective')
                loss.backward();optimizer.step()
            if step%500==0 or step==args.steps:
                metrics=evaluate_all(model,banks['validation'],recipe,scale,device)
                row=dict(band=band,step=step,metrics=metrics,seconds=time.time()-start,
                         learning_rate=optimizer.param_groups[0]['lr'])
                history.append(row);save(out/'HISTORY.json',history)
                if metrics['mse']<best:best=metrics['mse'];chosen=row;state=training.cpu_state(model.state_dict())
                save(out/'STATUS.json',dict(status='TRAINING',band=band,step=step,seconds=time.time()-start))
                print(json.dumps(row),flush=True)
                if step:scheduler.step(metrics['mse'])
        model.load_state_dict(state)
        calibrate(model,banks['train'],recipe,scale,device,batches=args.calibration_batches,seed=seed+100+band)
        after=evaluate_all(model,banks['validation'],recipe,scale,device)
        recalibrated=after['mse']<best
        if recalibrated:state=training.cpu_state(model.state_dict())
        validation=after if recalibrated else chosen['metrics']
        payload=dict(model=state,recipe=recipe,variant=dict(name='beam_residual',kind='author',channels=2,objective='sum'),
                     chosen=chosen,calibration=after,calibration_selected=recalibrated,validation=validation)
        torch.save(payload,out/f'band{band:02d}.pt')
        entries[band]=dict(path=f'band{band:02d}.pt',bounds=edges[band:band+2],validation=validation)
        manifest()
    save(out/'STATUS.json',dict(status='COMPLETE',seconds=time.time()-start,receiver_validated=False,mainline_installed=False))


if __name__=='__main__':main()
