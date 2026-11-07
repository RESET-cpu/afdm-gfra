"""Explicit prepare/preflight/train commands for the independent second score."""
import argparse
from copy import deepcopy
from dataclasses import asdict
import json
import math
import os
from pathlib import Path
import platform
import signal
import time
import traceback

import numpy as np
import torch
from threadpoolctl import threadpool_limits

from project import ROOT, repository_path
from utils import sha256, write_json
from networks.score import load_direct_checkpoint
from training.STMP.first import learning_rate
from training.scores.trainer import cpu_state
from training.scores.device import capture_device_rng, restore_device_rng
from training.colored_score_20261024.run import assets
from training.colored_preconditioned_20261024.model import load_checkpoint as load_first
from .model import ColoredSecondScore, conditional_error, noise_power, variance_from_trace
from .batches import BatchGraph, batches, context

DEFAULT = ROOT/'src/configs/training/colored_second_20261025.json'


def source_files():
    paths = []
    for directory in ('src/training/colored_second_20261025',
                      'src/training/colored_preconditioned_20261024',
                      'src/training/colored_score_20261024', 'src/networks',
                      'src/training/scores'):
        paths.extend((ROOT/directory).rglob('*.py'))
    paths += [ROOT/'src/training/STMP/first.py', ROOT/'src/project.py', ROOT/'src/utils.py',
              ROOT/'src/tests/test_colored_second_20261025.py']
    return sorted(set(paths))


def prepare(cfg, config_path):
    if cfg['schema'] != 'colored-second-score-training-v1':
        raise ValueError('Independent second-score recipe required')
    out = repository_path(cfg['output']).resolve()
    allowed = (ROOT/'result/channel_denoising/data').resolve()
    if not out.is_relative_to(allowed) or out == allowed:
        raise ValueError('Use a separate channel_denoising candidate directory')
    for key in ('first_checkpoint', 'first_training_record', 'initial_checkpoint'):
        record = cfg['second'] if key == 'initial_checkpoint' else cfg
        if sha256(repository_path(record[key])) != record[key+'_sha256']:
            raise ValueError('Required fixed asset changed: '+key)
    complete = json.loads(repository_path(cfg['first_training_record']).read_text())
    if complete['status'] != 'COMPLETED' or complete['weight_sha256'] != cfg['first_checkpoint_sha256']:
        raise ValueError('Completed frozen first required')
    first_recipe = json.loads(repository_path(cfg['first_recipe']).read_text())
    for key in ('noise', 'scale', 'train_samples', 'validation_samples'):
        if cfg[key] != first_recipe[key]:
            raise ValueError('Second must match first training distribution: '+key)
    original = repository_path(cfg['original_training'])
    if sha256(original) != cfg['original_training_sha256']:
        raise ValueError('Original recipe changed')
    original_record = json.loads(original.read_text())
    old = original_record.get('configuration', original_record)['second']
    matched = ('seed', 'validation_seed', 'batch_size', 'microbatch_size', 'learning_rate',
               'minimum_learning_rate', 'ema_decay', 'gradient_clip', 'maximum_epochs',
               'minimum_epochs', 'validation_patience', 'meaningful_relative_improvement',
               'initial_checkpoint_sha256')
    if any(cfg['second'][k] != old[k] for k in matched):
        raise ValueError('Preserve the declared old second training settings')
    binding, _, paths, _, _, records = assets(cfg)
    data = {s:np.load(p, mmap_mode='r', allow_pickle=False) for s,p in paths.items()}
    if binding['scale'] != cfg['scale'] or any(len(data[s]) != cfg[s+'_samples'] for s in data):
        raise ValueError('Training prior/scale mismatch')
    protected = [ROOT/'FINAL.json', ROOT/'MAINLINE.json', repository_path(cfg['base_config']),
                 repository_path(cfg['first_checkpoint'])]
    protected += [repository_path(binding[k]) for k in
                  ('first_checkpoint', 'second_checkpoint', 'evidence_checkpoint')]
    protected += list((ROOT/'src/algorithm/C_STMP').glob('*.py'))
    protected += list((ROOT/'src/algorithm/STMP').glob('*.py'))
    protected += list((ROOT/'src/algorithm/proposed').rglob('*.py'))
    protected += list((ROOT/'result/models/proposed_10').glob('*.pt'))
    spec = dict(schema=cfg['schema'], configuration=cfg, configuration_sha256=sha256(config_path),
        data_sha256=records, prior_definition_sha256=binding['prior_definition_sha256'],
        source_sha256={str(p.relative_to(ROOT)):sha256(p) for p in source_files()},
        protected_sha256={str(p.relative_to(ROOT)):sha256(p) for p in sorted(set(protected))},
        matched_original_second_settings=list(matched),
        environment=dict(python=platform.python_version(), torch=str(torch.__version__),
            numpy=np.__version__, cuda=torch.version.cuda,
            gpu=torch.cuda.get_device_name() if torch.cuda.is_available() else None,
            matmul_precision=torch.get_float32_matmul_precision(),
            cudnn_allow_tf32=torch.backends.cudnn.allow_tf32,
            matmul_allow_tf32=torch.backends.cuda.matmul.allow_tf32),
        validation_scope='5000 held-out internal channels; fixed colored draws for selection; '
                         'same channels with fixed white draws for deployment-boundary diagnosis only.',
        target_scope='Frozen-first conditional squared risk; equals covariance trace only with exact conditional mean.',
        maximum_optimizer_steps=math.ceil(cfg['train_samples']/cfg['second']['batch_size'])*cfg['second']['maximum_epochs'])
    out.mkdir(parents=True, exist_ok=True)
    path = out/'specification.json'
    if path.exists():
        if json.loads(path.read_text(encoding='utf-8')) != spec:
            raise ValueError('Existing specification differs; preserve this run and use a new output')
    else:
        write_json(path, spec)
        (out/'recipe.json').write_bytes(config_path.read_bytes())
        for p in source_files():
            dest = out/'source'/p.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(p.read_bytes())
    return out, data, sha256(path)


def initialize(cfg, device):
    torch.manual_seed(cfg['second']['seed'])
    first, fb = load_first(repository_path(cfg['first_checkpoint']), device)
    first.eval().requires_grad_(False)
    base, sb = load_direct_checkpoint(repository_path(cfg['second']['initial_checkpoint']), device)
    if fb['global_complex_rms'] != cfg['scale'] or sb['global_complex_rms'] != cfg['scale']:
        raise ValueError('Teacher/student coordinate scales differ')
    if asdict(base.config) != fb['config']:
        raise ValueError('Keep the original matched RefineNet backbone')
    second = ColoredSecondScore(base, cfg['reference_real_variance']).to(device)
    return first, second


def summarize(predicted, risk, nu, signal):
    p,e,v,s = (np.asarray(x, dtype=float) for x in (predicted,risk,nu,signal))
    if not all(np.isfinite(x).all() for x in (p,e,v,s)):
        raise FloatingPointError('Nonfinite validation statistics')
    return dict(samples=len(p), loss=float(np.mean(((p-e)/v)**2)),
        mean_predicted_variance=float(p.mean()), mean_realized_squared_error=float(e.mean()),
        aggregate_prediction_to_error_ratio=float(p.sum()/e.sum()),
        relative_bias=float((p.sum()-e.sum())/e.sum()),
        normalized_mse_against_realized_error=float(np.sum((p-e)**2)/np.sum(e**2)),
        nonpositive_fraction=float(np.mean(p <= 0)), above_input_noise_fraction=float(np.mean(p >= v)),
        first_nmse_db=float(10*np.log10(e.sum()/s.sum())),
        minimum_raw_variance=float(p.min()), maximum_raw_variance=float(p.max()))


@torch.inference_mode()
def validation(second, first, bank, cfg, device, *, white=False):
    run_cfg = deepcopy(cfg)
    if white:
        run_cfg['noise']['max_strength'] = 0.
    rng = np.random.default_rng(cfg['second']['validation_seed'])
    shape_rng = np.random.default_rng(cfg['validation_shape_seed'])
    second.eval()
    values = [[] for _ in range(4)]
    for start in range(0,len(bank),cfg['second']['batch_size']):
        chosen = np.arange(start,min(start+cfg['second']['batch_size'],len(bank)))
        arrays = batches(bank,chosen,rng,shape_rng,run_cfg)
        ts = [torch.as_tensor(a,device=device) for a in arrays]
        cov,spec = context(ts)
        mean = first(ts[1],cov,spec)
        u = second(ts[1],cov,spec)
        outputs = (variance_from_trace(u,spec),conditional_error(mean,ts[0]),noise_power(spec),
                   2*ts[0].square().flatten(1).mean(1))
        for accum,x in zip(values,outputs):
            accum.append(x.cpu().numpy())
    values = [np.concatenate(x) for x in values]
    result = summarize(*values)
    group = np.floor(-10*np.log10(values[2].astype(float))/5)*5
    result['bands'] = {f'snr_{int(g)}_to_{int(g)+5}_db':
                      summarize(*(x[group==g] for x in values)) for g in np.unique(group)}
    result['reference'] = 'Single-realization squared error, not oracle posterior variance'
    return result


class Trainer:
    def __init__(self,out,cfg,specification_hash):
        self.out,self.cfg,self.specification_hash = out,cfg,specification_hash
        self.stop = False

    def status(self,status,**kwargs):
        row = dict(status=status,pid=os.getpid(),updated_unix=time.time(),**kwargs)
        write_json(self.out/'status.json',row)
        print(json.dumps(row),flush=True)

    def request_stop(self,*_):
        self.stop = True

    def save_weight(self,path,model,metrics,epoch):
        blob = dict(schema='colored-second-score-trace-v1',order=2,
            output='normalized_covariance_weighted_hessian_trace',config=asdict(model.config),
            reference_real_variance=model.reference_real_variance,
            global_complex_rms=self.cfg['scale'],normalization='population_rms',
            first_sha256=self.cfg['first_checkpoint_sha256'],state_dict=cpu_state(model),
            metadata=dict(epoch=epoch,validation=metrics,specification_sha256=self.specification_hash,
                noise=self.cfg['noise'],initialization_sha256=self.cfg['second']['initial_checkpoint_sha256'],
                training_scope=self.cfg['scope']))
        tmp = path.with_suffix('.tmp')
        torch.save(blob,tmp)
        tmp.replace(path)

    def run(self,data):
        cfg,settings = self.cfg,self.cfg['second']
        device = cfg['runtime']['device']
        if (self.out/'complete.json').exists():
            complete = json.loads((self.out/'complete.json').read_text())
            if (complete['specification_sha256'] != self.specification_hash or
                    sha256(self.out/'second_best.pt') != complete['weight_sha256']):
                raise ValueError('Completed run identity changed')
            self.status('COMPLETED',epochs=complete['epochs'],selected_epoch=complete['selected_epoch'])
            return
        first,model = initialize(cfg,device)
        ema = deepcopy(model).eval()
        optimizer = torch.optim.Adam(model.parameters(),lr=settings['learning_rate'])
        rng = np.random.default_rng(settings['seed'])
        shape_rng = np.random.default_rng(cfg['shape_seed'])
        epoch,cursor,steps,best,selected_epoch = 1,0,0,math.inf,0
        meaningful_best,last_improvement = math.inf,0
        indices,history,loss_sum,seen = None,[],0.,0
        last_saved = time.time()
        last = self.out/'last.pt'

        def checkpoint():
            nonlocal last_saved
            state = dict(schema='colored-second-score-resume-v1',specification_sha256=self.specification_hash,
                model=cpu_state(model),ema=cpu_state(ema),optimizer=optimizer.state_dict(),
                rng=rng.bit_generator.state,shape_rng=shape_rng.bit_generator.state,
                torch_rng=torch.get_rng_state(),**capture_device_rng(device),
                epoch=epoch,cursor=cursor,steps=steps,indices=indices,history=history,
                loss_sum=loss_sum,seen=seen,best=best,selected_epoch=selected_epoch,
                meaningful_best=meaningful_best,last_improvement=last_improvement)
            tmp = last.with_suffix('.tmp')
            torch.save(state,tmp)
            tmp.replace(last)
            last_saved = time.time()

        if last.exists():
            state = torch.load(last,map_location='cpu',weights_only=False)
            if state['schema'] != 'colored-second-score-resume-v1' or state['specification_sha256'] != self.specification_hash:
                raise ValueError('Resume identity mismatch')
            model.load_state_dict(state['model']); ema.load_state_dict(state['ema'])
            optimizer.load_state_dict(state['optimizer'])
            rng.bit_generator.state = state['rng']; shape_rng.bit_generator.state = state['shape_rng']
            torch.set_rng_state(state['torch_rng']); restore_device_rng(device,state)
            epoch,cursor,steps,indices = (state[k] for k in ('epoch','cursor','steps','indices'))
            history,loss_sum,seen,best,selected_epoch,meaningful_best,last_improvement = (state[k] for k in
                ('history','loss_sum','seen','best','selected_epoch','meaningful_best','last_improvement'))
            del state
            self.status('RESUMED',epoch=epoch,samples=cursor,optimizer_steps=steps)
        else:
            self.status('VALIDATING_INITIALIZATION',samples=len(data['validation']))
            measured = {name:validation(ema,first,data['validation'],cfg,device,white=white)
                        for name,white in (('colored',False),('white',True))}
            best = meaningful_best = measured['colored']['loss']
            write_json(self.out/'baseline.json',measured)
            self.save_weight(self.out/'second_best.pt',ema,measured,0)
            checkpoint()
            self.status('INITIALIZATION_VALIDATED',colored_loss=best,white_loss=measured['white']['loss'])

        graph = BatchGraph(model,first,settings['batch_size'])
        started = time.time()
        stopping_reason = 'MAXIMUM_EPOCHS'
        while epoch <= settings['maximum_epochs']:
            start = time.time()
            rate = learning_rate(settings,epoch)
            for group in optimizer.param_groups:
                group['lr'] = rate
            model.train()
            if indices is None:
                indices = rng.permutation(len(data['train']))
            while cursor < len(indices):
                timeout = time.time()-started >= cfg['runtime']['maximum_invocation_seconds']
                if self.stop or (self.out/'pause.request').exists() or timeout:
                    checkpoint()
                    self.status('PAUSED',epoch=epoch,samples=cursor,optimizer_steps=steps,resumable=True,
                                reason='TIME_LIMIT' if timeout else 'STOP_REQUEST')
                    return
                chosen = indices[cursor:cursor+settings['batch_size']]
                arrays = batches(data['train'],chosen,rng,shape_rng,cfg)
                optimizer.zero_grad(set_to_none=True)
                loss_sum += graph.backward(arrays,use_graph=cfg['runtime']['cuda_graph'])
                norm = torch.nn.utils.clip_grad_norm_(model.parameters(),settings['gradient_clip'],error_if_nonfinite=True)
                optimizer.step()
                with torch.no_grad():
                    torch._foreach_lerp_(list(ema.parameters()),list(model.parameters()),1-settings['ema_decay'])
                cursor += len(chosen); seen += len(chosen); steps += 1
                if time.time()-last_saved >= settings['checkpoint_seconds']:
                    checkpoint()
                if steps % 50 == 0:
                    self.status('TRAINING',epoch=epoch,maximum_epochs=settings['maximum_epochs'],samples=cursor,
                        training_samples=len(indices),optimizer_steps=steps,loss=loss_sum/seen,learning_rate=rate,
                        gradient_norm_before_clip=float(norm.cpu()),elapsed_epoch_seconds=time.time()-start)
            if sha256(repository_path(cfg['first_checkpoint'])) != cfg['first_checkpoint_sha256']:
                raise ValueError('Frozen first file changed during training')
            self.status('VALIDATING',epoch=epoch,optimizer_steps=steps)
            measured = {name:validation(ema,first,data['validation'],cfg,device,white=white)
                        for name,white in (('colored',False),('white',True))}
            history.append(dict(epoch=epoch,optimizer_steps=steps,train_loss=loss_sum/seen,
                                validation=measured,learning_rate=rate,seconds_this_invocation=time.time()-start))
            write_json(self.out/'history.json',history)
            if measured['colored']['loss'] < best:
                best,selected_epoch = measured['colored']['loss'],epoch
                self.save_weight(self.out/'second_best.pt',ema,measured,epoch)
            if measured['colored']['loss'] < meaningful_best*(1-settings['meaningful_relative_improvement']):
                meaningful_best,last_improvement = measured['colored']['loss'],epoch
            plateau = epoch >= settings['minimum_epochs'] and epoch-last_improvement >= settings['validation_patience']
            self.status('EPOCH_COMPLETE',epoch=epoch,optimizer_steps=steps,selected_epoch=selected_epoch,
                colored_loss=measured['colored']['loss'],white_loss=measured['white']['loss'],
                colored_variance_ratio=measured['colored']['aggregate_prediction_to_error_ratio'],
                white_variance_ratio=measured['white']['aggregate_prediction_to_error_ratio'],
                colored_nonpositive_fraction=measured['colored']['nonpositive_fraction'],
                white_nonpositive_fraction=measured['white']['nonpositive_fraction'])
            epoch += 1; cursor,indices,loss_sum,seen = 0,None,0.,0
            checkpoint()
            if plateau:
                stopping_reason = 'VALIDATION_PLATEAU'
                break
        self.save_weight(self.out/'second_final.pt',ema,history[-1]['validation'],epoch-1)
        chosen = torch.load(self.out/'second_best.pt',map_location='cpu',weights_only=False)
        record = dict(status='COMPLETED',epochs=epoch-1,optimizer_steps=steps,selected_epoch=selected_epoch,
            stopping_reason=stopping_reason,validation=chosen['metadata']['validation'],
            specification_sha256=self.specification_hash,first_sha256=cfg['first_checkpoint_sha256'],
            weight_sha256=sha256(self.out/'second_best.pt'),final_weight_sha256=sha256(self.out/'second_final.pt'),
            receiver_evaluation_completed=False,receiver_binding_modified=False)
        write_json(self.out/'complete.json',record)
        self.status('COMPLETED',epochs=epoch-1,optimizer_steps=steps,selected_epoch=selected_epoch)


def preflight(out,data,cfg,specification_hash):
    first,model = initialize(cfg,cfg['runtime']['device'])
    teacher_before = cpu_state(first)
    arrays = batches(data['train'],np.arange(cfg['second']['batch_size']),
        np.random.default_rng(cfg['second']['seed']),np.random.default_rng(cfg['shape_seed']),cfg)
    optimizer = torch.optim.Adam(model.parameters(),lr=cfg['second']['learning_rate'])
    if cfg['runtime']['device'] == 'cuda':
        torch.cuda.reset_peak_memory_stats()
    graph = BatchGraph(model,first,cfg['second']['batch_size'])
    before = graph.backward(arrays,use_graph=False)/len(arrays[0])
    gradients = [p.grad.detach().clone() for p in model.parameters()]
    optimizer.zero_grad(set_to_none=True)
    captured = graph.backward(arrays)/len(arrays[0])
    num = sum(float((p.grad-g).double().square().sum().cpu()) for p,g in zip(model.parameters(),gradients))
    den = sum(float(g.double().square().sum().cpu()) for g in gradients)
    relative = math.sqrt(num/max(den,1e-30))
    assert abs(before-captured) < 1e-5*max(1,abs(before)) and relative < 1e-4
    del gradients
    norm = torch.nn.utils.clip_grad_norm_(model.parameters(),cfg['second']['gradient_clip'],error_if_nonfinite=True)
    optimizer.step()
    optimizer.zero_grad(set_to_none=True)
    after = graph.backward(arrays)/len(arrays[0])
    assert np.isfinite(after) and all(p.grad is None for p in first.parameters())
    assert all(torch.equal(t,first.state_dict()[k].cpu()) for k,t in teacher_before.items())
    result = dict(status='PASS',specification_sha256=specification_hash,execution_batch=len(arrays[0]),
        initial_loss=before,captured_loss=captured,updated_loss=after,
        graph_gradient_relative_difference=relative,gradient_norm_before_clip=float(norm.cpu()),
        teacher_state_unchanged=True,teacher_gradients_absent=True,training_steps_saved=0,
        max_allocated_bytes=torch.cuda.max_memory_allocated() if torch.cuda.is_available() else None,
        max_reserved_bytes=torch.cuda.max_memory_reserved() if torch.cuda.is_available() else None)
    write_json(out/'PREFLIGHT.json',result)
    print(json.dumps(result),flush=True)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('command',choices=('prepare','preflight','train'))
    parser.add_argument('--config',type=Path,default=DEFAULT)
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text(encoding='utf-8'))
    torch.set_num_threads(cfg['runtime']['threads'])
    with threadpool_limits(limits=cfg['runtime']['threads']):
        out,data,digest = prepare(cfg,args.config)
        if args.command == 'prepare':
            print(json.dumps(dict(status='PREPARED',output=str(out))))
            return
        if args.command == 'preflight':
            preflight(out,data,cfg,digest)
            return
        checked = json.loads((out/'PREFLIGHT.json').read_text())
        if checked['status'] != 'PASS' or checked['specification_sha256'] != digest:
            raise ValueError('Pass preflight for this exact specification first')
        trainer = Trainer(out,cfg,digest)
        signal.signal(signal.SIGINT,trainer.request_stop)
        signal.signal(signal.SIGTERM,trainer.request_stop)
        try:
            trainer.run(data)
        except Exception:
            write_json(out/'FAILURE.json',dict(status='FAILED',traceback=traceback.format_exc(),
                       pid=os.getpid(),updated_unix=time.time(),automatic_retry=False))
            trainer.status('FAILED',details='FAILURE.json; last complete checkpoint preserved')
            raise


if __name__ == '__main__':
    main()
