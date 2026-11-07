"""Training-only BatchNorm moment calibration, scored over all held-out antennas.

No optimizer update or validation example enters the calibration pass. Original
and recalibrated outputs are both retained. This is a training adaptation,
not the author's last-mini-batch inference moment convention.
"""
import argparse
import json
from pathlib import Path
import sys
import time
import numpy as np
import torch
from author_reference import AuthorDnCNN
from train_author_controls import DirectAuthorCNN,batch,training

ROOT=Path(__file__).resolve().parents[2]


def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')


@torch.inference_mode()
def evaluate_all(model,bank,recipe,scale,device):
    model.eval();rng=np.random.default_rng(recipe['validation_seed'])
    error=power=active_error=inactive_error=0.;coordinates=0
    count=recipe.get('validation_count',512)
    for start in range(0,count,recipe['batch_size']):
        indices=np.arange(start,min(start+recipe['batch_size'],count))
        # Keep all 16 coordinates, then apply the same network to each antenna/beam.
        x,target,active=batch(bank,indices,rng,recipe,scale,32)
        b,_,r,n=x.shape
        x=torch.stack([x[:,:16],x[:,16:]],dim=2).reshape(b*16,2,r,n)
        target=torch.stack([target[:,:16],target[:,16:]],dim=2).reshape(b*16,2,r,n)
        pred=model(x.to(device)).cpu().double();target=target.double();active=np.repeat(active,16)
        errors=(pred-target).square().sum(dim=(1,2,3)).numpy()
        error+=errors.sum();power+=float(target.square().sum());coordinates+=target.numel()
        active_error+=errors[active].sum();inactive_error+=errors[~active].sum()
    return dict(mse=float(error/coordinates),zero_mse=power/coordinates,error_over_zero=float(error/power),
                active_nmse_db=float(10*np.log10(active_error/power)),inactive_error_fraction_of_signal=float(inactive_error/power),
                scope=f'{count} held-out physical user channels, all 16 antennas/beams; identical query noise and activity streams across representations')


@torch.inference_mode()
def calibrate(model,bank,recipe,scale,device,batches=256,seed=202610146401):
    model.train();rng=np.random.default_rng(seed)
    for layer in model.modules():
        if isinstance(layer,torch.nn.BatchNorm2d):
            layer.reset_running_stats();layer.momentum=None
    for _ in range(batches):
        indices=rng.integers(len(bank),size=recipe['batch_size'])
        x,_,_=batch(bank,indices,rng,recipe,scale,2)
        model(x.to(device))
    model.eval()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--sources',type=Path,nargs='+',required=True)
    p.add_argument('--calibration-batches',type=int,default=256);p.add_argument('--device',choices=['cpu','mps'],default='mps')
    p.add_argument('--seed',type=int,default=202610146401)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(1);device=args.device;scale=json.loads((ROOT/'configs/ldamp.json').read_text())['scale']
    plan=dict(scope=__doc__,sources=[str(s) for s in args.sources],calibration_batches=args.calibration_batches,
              calibration_seed=args.seed,validation_coordinates='all 16 antennas or all 16 beams',device=device)
    save(args.output/'PLAN.json',plan);rows=[];start=time.time()
    for source in args.sources:
        saved=torch.load(source,map_location='cpu',weights_only=False)
        v=saved['variant'];assert v['channels']==2
        model=(DirectAuthorCNN(2) if v['kind']=='direct' else AuthorDnCNN(channels=2)).to(device)
        model.load_state_dict(saved['model']);recipe=saved['recipe']
        scale=recipe.get('population_scale',scale)
        train=np.load(ROOT/recipe['train_path'],mmap_mode='r');val=np.load(ROOT/recipe['validation_path'],mmap_mode='r')
        before=evaluate_all(model,val,recipe,scale,device)
        calibrate(model,train,recipe,scale,device,batches=args.calibration_batches,seed=args.seed)
        after=evaluate_all(model,val,recipe,scale,device)
        row=dict(source=str(source),variant=v,representation=recipe.get('representation','afdm'),before=before,after=after)
        rows.append(row)
        name=f'{len(rows):02d}_calibrated.pt'
        torch.save(dict(model=training.cpu_state(model.state_dict()),variant=v,recipe=recipe,
                        calibration=plan,validation=after,source=str(source)),args.output/name)
        save(args.output/'RESULTS.json',rows);print(json.dumps(row),flush=True)
    save(args.output/'STATUS.json',dict(status='COMPLETE',seconds=time.time()-start,receiver_validated=False))


if __name__=='__main__':main()
