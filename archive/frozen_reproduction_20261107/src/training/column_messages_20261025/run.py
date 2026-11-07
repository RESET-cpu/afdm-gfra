"""Explicitly authorized first -> activity -> paired receiver evaluation pipeline."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import math
import os
from pathlib import Path
import platform
import time
import traceback
import numpy as np
import torch
from torch.nn import functional as F
from threadpoolctl import threadpool_limits

from project import ROOT
from utils import read_json, write_json, sha256
from networks.score import load_direct_checkpoint
from training.colored_score_20261024.run import assets
from training.scores.trainer import cpu_state
from training.STMP.first import learning_rate
from .data import build_pool, draw
from .interface import First, Activity, training_query, save_weight, load_weight, unpack, pack, information_query

DEFAULT = ROOT/'src/configs/training/column_messages_20261025.json'


def atomic_torch(path, value):
    temp = path.with_suffix('.tmp'); torch.save(value, temp); temp.replace(path)


def status(out, stage, **values):
    row = dict(stage=stage, pid=os.getpid(), updated_unix=time.time(), **values)
    write_json(out/'STATUS.json', row)
    print(row, flush=True)


def source_paths():
    folders = ['src/training/column_messages_20261025', 'src/algorithm/C_STMP_column_20261025',
               'src/algorithm/C_STMP_column_messages', 'src/networks']
    return sorted(set(p for f in folders for p in (ROOT/f).rglob('*.py')))


def check_sources(spec):
    for name, digest in {**spec['sources'], **spec['protected']}.items():
        if sha256(ROOT/name) != digest:
            raise ValueError('Frozen input/source changed: '+name)


def prepare(cfg, out):
    out.mkdir(parents=True, exist_ok=True)
    if (out/'SPECIFICATION.json').exists():
        spec = read_json(out/'SPECIFICATION.json')
        assert spec['configuration'] == cfg
        check_sources(spec)
        return spec
    status(out, 'PREPARING')
    binding, _, paths, _, _, data_hashes = assets(cfg)
    initial = ROOT/cfg['first']['initial_checkpoint']
    assert sha256(initial) == cfg['first']['initial_checkpoint_sha256']
    pool_files = {}
    for split in ('train', 'validation'):
        target = out/(split+'_precision_pool.npz')
        if target.exists():
            raise ValueError('Uncommitted pool exists; inspect before continuing')
        pool = build_pool(cfg['pool'][split+'_seed'], cfg['pool'][split+'_operators'])
        np.savez_compressed(target, **pool)
        pool_files[split] = dict(path=str(target), sha256=sha256(target), samples=len(pool['values']))
        status(out, 'PREPARING_POOLS', split=split, samples=len(pool['values']))
    protected = read_json(ROOT/'result/snr_comparison/data/c_stmp_column_messages_20261025/PLAN.json')['protected']
    spec = dict(schema='unified-column-training-v1', configuration=cfg,
        data_paths={k:str(v) for k,v in paths.items()}, data_hashes=data_hashes,
        prior_definition_sha256=binding['prior_definition_sha256'], pools=pool_files,
        protected=protected, sources={str(p.relative_to(ROOT)):sha256(p) for p in source_paths()},
        environment=dict(python=platform.python_version(), torch=str(torch.__version__),
                         gpu=torch.cuda.get_device_name(), precision='float32', cuda_graph=True),
        evaluation='10 existing error inputs plus 4 independent physical scenes x 3 SNR; full 1000-scene run remains paused')
    check_sources(spec)
    write_json(out/'SPECIFICATION.json', spec)
    for name in spec['sources']:
        target = out/'source'/name; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT/name).read_bytes())
    (out/'recipe.json').write_bytes(DEFAULT.read_bytes())
    return spec


def initial_model(cfg, stage):
    torch.manual_seed(cfg[stage]['seed'])
    if stage == 'first':
        base, _ = load_direct_checkpoint(ROOT/cfg['first']['initial_checkpoint'], 'cpu')
        model = First(base)
    else:
        model = Activity()
    return model.to('cuda')


def objective(model, teacher, stage, tensors):
    clean, positive, negative, u, lam = tensors
    x, z = training_query(clean, positive, u, lam)
    if stage == 'first':
        raw = model.raw(x, u, lam)
        loss = model.dsm_loss(raw, clean, positive, u, lam)
        return loss, model.from_raw(raw, z, u, lam), None
    negative_x, negative_z = training_query(torch.zeros_like(clean), negative, u, lam)
    both_x = torch.cat((x, negative_x)); both_z = torch.cat((z, negative_z))
    both_u, both_lam = torch.cat((u,u)), torch.cat((lam,lam))
    with torch.no_grad():
        mean = teacher(both_x, both_z, both_u, both_lam)
    scores = model(both_x, both_u, both_lam, mean)
    labels = torch.cat((torch.ones(len(x), device=x.device), torch.zeros(len(x), device=x.device)))
    return F.binary_cross_entropy_with_logits(scores, labels), mean, scores


class Graph:
    def __init__(self, model, teacher, stage, batch_size):
        self.model, self.teacher, self.stage, self.batch_size = model, teacher, stage, batch_size
        self.graph = None

    def backward(self, arrays):
        if len(arrays[0]) != self.batch_size:
            tensors = tuple(x.to('cuda', non_blocking=True) for x in arrays)
            loss = objective(self.model, self.teacher, self.stage, tensors)[0]
            loss.backward(); return float(loss.detach())
        if self.graph is None:
            self.inputs = tuple(x.to('cuda').clone() for x in arrays)
            stream = torch.cuda.Stream(); stream.wait_stream(torch.cuda.current_stream())
            with torch.cuda.stream(stream):
                for _ in range(3):
                    self.model.zero_grad(set_to_none=True)
                    objective(self.model, self.teacher, self.stage, self.inputs)[0].backward()
            torch.cuda.current_stream().wait_stream(stream)
            self.model.zero_grad(set_to_none=True)
            self.graph = torch.cuda.CUDAGraph()
            with torch.cuda.graph(self.graph):
                self.loss = objective(self.model, self.teacher, self.stage, self.inputs)[0]
                self.loss.backward()
            self.gradients = [p.grad for p in self.model.parameters()]
        for dst, src in zip(self.inputs, arrays): dst.copy_(src, non_blocking=True)
        self.graph.replay()
        for parameter, gradient in zip(self.model.parameters(), self.gradients): parameter.grad = gradient
        return float(self.loss.detach())


def validation(model, teacher, stage, bank, pool, cfg):
    rng = np.random.default_rng(cfg[stage]['validation_seed'])
    loss = error = signal = count = correct = total_labels = 0
    batch = cfg[stage]['batch_size']
    with torch.inference_mode():
        for begin in range(0, len(bank), batch):
            ids = np.arange(begin, min(begin+batch, len(bank)))
            arrays = draw(bank, ids, pool, rng, cfg['scale'], cfg['precision_range'])
            tensors = tuple(torch.as_tensor(x, device='cuda') for x in arrays)
            value, mean, logits = objective(model, teacher, stage, tensors)
            loss += float(value)*len(ids); count += len(ids)
            if stage == 'first':
                error += float((mean-tensors[0]).square().sum()); signal += float(tensors[0].square().sum())
            else:
                correct += int((logits[:len(ids)]>=0).sum()+(logits[len(ids):]<0).sum())
                total_labels += 2*len(ids)
    result = dict(loss=loss/count, samples=count)
    if stage == 'first': result.update(error=error, signal=signal, nmse_db=10*np.log10(error/signal))
    else: result.update(balanced_accuracy=correct/total_labels, labels=total_labels)
    if not all(np.isfinite(v) for v in result.values()): raise FloatingPointError('Nonfinite validation')
    return result


def preflight(cfg, out, spec):
    """Paired shared-input, GPU graph, serialization and short complete-loop checks."""
    folder = out/'preflight'; folder.mkdir(exist_ok=True)
    bank = np.load(spec['data_paths']['train'], mmap_mode='r')
    with np.load(spec['pools']['train']['path']) as z: pool = dict(z)
    rng = np.random.default_rng(202610251901)
    reports = []
    teacher = initial_model(cfg, 'first').eval().requires_grad_(False)
    for stage in ('first', 'activity'):
        model = initial_model(cfg, stage)
        b = cfg[stage]['batch_size']
        arrays = draw(bank, np.arange(b), pool, rng, cfg['scale'], cfg['precision_range'])
        tensors = tuple(torch.as_tensor(a, device='cuda') for a in arrays)
        value = objective(model, teacher, stage, tensors)[0]; value.backward()
        reference = [p.grad.detach().clone() for p in model.parameters()]
        # Use a fresh identical module for capture: a previous eager backward on
        # the legacy stream attaches cross-stream AccumulateGrad dependencies.
        model = initial_model(cfg, stage)
        graph = Graph(model, teacher, stage, b)
        inputs = tuple(torch.from_numpy(a).pin_memory() for a in arrays)
        captured = graph.backward(inputs)
        max_error = max(float((p.grad-g).abs().max()) for p,g in zip(model.parameters(),reference))
        max_gradient = max(float(g.abs().max()) for g in reference)
        assert abs(captured-float(value)) <= 2e-5*max(1,abs(float(value)))
        assert max_error <= 2e-4*max(1e-3,max_gradient)
        # Exercise Adam/EMA and graph reuse, using a disposable model only.
        opt = torch.optim.Adam(model.parameters(), lr=cfg[stage]['learning_rate'], fused=True)
        for _ in range(4):
            opt.zero_grad(set_to_none=True); graph.backward(inputs)
            torch.nn.utils.clip_grad_norm_(model.parameters(), cfg[stage]['gradient_clip'])
            opt.step()
        assert all(bool(torch.isfinite(p).all()) for p in model.parameters())
        fresh = initial_model(cfg, stage)
        path = folder/(stage+'_random.pt')
        save_weight(path, fresh, stage, dict(epoch=0, optimizer_steps=0, specification_sha256=sha256(out/'SPECIFICATION.json')))
        restored, _ = load_weight(path)
        with torch.inference_mode():
            a = objective(fresh, teacher, stage, tensors)[0]
            bvalue = objective(restored, teacher, stage, tensors)[0]
        assert torch.equal(a, bvalue)
        reports.append(dict(stage=stage, loss=captured, max_gradient_difference=max_error,
                            relative_gradient_difference=max_error/max(max_gradient,1e-30), disposable_updates=4))
        del model, graph, fresh, restored, opt, tensors, reference
        torch.cuda.empty_cache()
    # Train/inference identity with the exact same eta, no ground-truth path at inference.
    arrays = draw(bank, np.arange(4), pool, rng, cfg['scale'], cfg['precision_range'])
    clean, eps, _, u, lam = [torch.as_tensor(a,device='cuda') for a in arrays]
    x,z = training_query(clean, eps, u, lam)
    from .interface import column
    eta = column(clean,u,lam)+column(eps,u,(lam/2).sqrt())
    xi, zi = information_query(eta,u,lam)
    relative = float(torch.linalg.vector_norm(x-xi)/torch.linalg.vector_norm(x))
    assert relative < 2e-4
    from algorithm.C_STMP_column_20261025.receiver import Receiver
    from system.observation import ReceiverInput
    receiver_cfg = deepcopy(cfg['receiver'])
    receiver_cfg.update(scale=cfg['scale'], first_checkpoint=str(folder/'first_random.pt'),
                        activity_checkpoint=str(folder/'activity_random.pt'))
    receiver_cfg['ep']['iterations']=3
    receiver = Receiver(receiver_cfg, verify=False)
    a = (rng.normal(size=(16,3,16))+1j*rng.normal(size=(16,3,16)))/4
    y = (rng.normal(size=(16,16,16))+1j*rng.normal(size=(16,16,16)))*cfg['scale']
    prediction, record = receiver.infer(ReceiverInput(y,a,1.,.1))
    assert record['iterations']==3 and all(np.isfinite(x).all() for x in prediction.values())
    write_json(folder/'receiver_smoke.json',record)
    write_json(out/'PREFLIGHT.json',dict(status='PASSED', reports=reports,
        train_inference_relative_difference=relative, random_weight_receiver_iterations=3,
        random_smoke_is_not_performance=True, specification_sha256=sha256(out/'SPECIFICATION.json')))
    status(out,'PREFLIGHT_PASSED',reports=reports,train_inference_relative_difference=relative)


def train_stage(cfg, out, spec, stage):
    folder = out/stage; folder.mkdir(exist_ok=True)
    complete = folder/'COMPLETE.json'
    if complete.exists():
        done=read_json(complete); assert done['weight_sha256']==sha256(folder/'best.pt'); return
    settings = cfg[stage]
    bank = {s:np.load(p,mmap_mode='r') for s,p in spec['data_paths'].items()}
    pools = {}
    for s,r in spec['pools'].items():
        assert sha256(r['path'])==r['sha256']
        with np.load(r['path']) as z: pools[s]=dict(z)
    teacher = None
    first_hash = None
    if stage=='activity':
        first_hash=sha256(out/'first/best.pt'); teacher,_=load_weight(out/'first/best.pt')
    model = initial_model(cfg,stage); ema=deepcopy(model).eval().requires_grad_(False)
    optimizer=torch.optim.Adam(model.parameters(),lr=settings['learning_rate'],fused=True)
    rng=np.random.default_rng(settings['seed'])
    epoch=1;cursor=steps=0;indices=None;best=math.inf;selected=0;history=[];loss_sum=0.;seen=0
    last=folder/'last.pt'; last_saved=time.time(); start=time.time()
    spec_hash=sha256(out/'SPECIFICATION.json')
    if last.exists():
        saved=torch.load(last,map_location='cpu',weights_only=False)
        assert saved['specification_sha256']==spec_hash
        model.load_state_dict(saved['model']);ema.load_state_dict(saved['ema']);optimizer.load_state_dict(saved['optimizer'])
        rng.bit_generator.state=saved['rng']
        epoch,cursor,steps,indices,best,selected,history,loss_sum,seen=(saved[k] for k in
            ('epoch','cursor','steps','indices','best','selected','history','loss_sum','seen'))
        del saved

    def save_checkpoint():
        nonlocal last_saved
        atomic_torch(last,dict(specification_sha256=spec_hash,model=cpu_state(model),ema=cpu_state(ema),
            optimizer=optimizer.state_dict(),rng=rng.bit_generator.state,epoch=epoch,cursor=cursor,
            steps=steps,indices=indices,best=best,selected=selected,history=history,loss_sum=loss_sum,seen=seen))
        last_saved=time.time()

    def weight(path, score, selected_epoch):
        save_weight(path,ema,stage,dict(epoch=selected_epoch,validation=score,
            first_sha256=first_hash,specification_sha256=spec_hash,scale=cfg['scale'],
            objective='original_covariance_weighted_DSM' if stage=='first' else 'balanced_BCE',
            clean_training_samples=50000,training_class_prior=.5))

    if not last.exists():
        status(out,'VALIDATING_INITIALIZATION',network=stage)
        score=validation(ema,teacher,stage,bank['validation'],pools['validation'],cfg)
        best=score['loss'];weight(folder/'best.pt',score,0)
        write_json(folder/'BASELINE.json',score);save_checkpoint()
    graph=Graph(model,teacher,stage,settings['batch_size'])
    model_params=list(model.parameters());ema_params=list(ema.parameters())
    while epoch<=settings['maximum_epochs']:
        epoch_start=time.time()
        if indices is None: indices=rng.permutation(len(bank['train']))
        lr=learning_rate(settings,epoch)
        for group in optimizer.param_groups: group['lr']=lr
        batch_rng=np.random.default_rng();batch_rng.bit_generator.state=deepcopy(rng.bit_generator.state)
        def produce(begin):
            chosen=indices[begin:begin+settings['batch_size']]
            arrays=draw(bank['train'],chosen,pools['train'],batch_rng,cfg['scale'],cfg['precision_range'])
            return tuple(torch.from_numpy(a).pin_memory() for a in arrays),deepcopy(batch_rng.bit_generator.state)
        last_status=0.
        with ThreadPoolExecutor(max_workers=1) as executor:
            future=executor.submit(produce,cursor)
            while cursor<len(indices):
                arrays,after=future.result();batch_count=len(arrays[0])
                next_cursor=cursor+batch_count
                if next_cursor<len(indices): future=executor.submit(produce,next_cursor)
                optimizer.zero_grad(set_to_none=True)
                loss=graph.backward(arrays)
                if not np.isfinite(loss): raise FloatingPointError('Nonfinite training loss')
                torch.nn.utils.clip_grad_norm_(model_params,settings['gradient_clip'],error_if_nonfinite=True)
                optimizer.step()
                with torch.no_grad(): torch._foreach_lerp_(ema_params,model_params,1-settings['ema_decay'])
                cursor=next_cursor;steps+=1;seen+=batch_count;loss_sum+=loss*batch_count
                rng.bit_generator.state=after
                if time.time()-last_status>30:
                    status(out,'TRAINING',network=stage,epoch=epoch,epochs=settings['maximum_epochs'],
                        samples=cursor,train_samples=len(indices),optimizer_steps=steps,training_loss=loss_sum/seen,
                        last_validation=history[-1]['validation'] if history else None)
                    last_status=time.time()
                if time.time()-last_saved>settings['checkpoint_seconds']: save_checkpoint()
                if (out/'STOP.json').exists():
                    save_checkpoint();status(out,'STOPPED_BY_USER',network=stage,epoch=epoch,samples=cursor);return False
        score=validation(ema,teacher,stage,bank['validation'],pools['validation'],cfg)
        if score['loss']<best:
            best=score['loss'];selected=epoch;weight(folder/'best.pt',score,epoch)
        row=dict(epoch=epoch,seconds=time.time()-epoch_start,training_loss=loss_sum/seen,
                 validation=score,learning_rate=lr,optimizer_steps=steps)
        history.append(row);write_json(folder/'HISTORY.json',history)
        status(out,'EPOCH_COMPLETE',network=stage,**row,selected_epoch=selected)
        epoch+=1;cursor=0;indices=None;loss_sum=0.;seen=0;save_checkpoint()
        if (out/'STOP.json').exists(): status(out,'STOPPED_BY_USER',network=stage,epoch=epoch);return False
    weight(folder/'final.pt',score,settings['maximum_epochs'])
    write_json(complete,dict(status='COMPLETE',epochs=settings['maximum_epochs'],optimizer_steps=steps,
        selected_epoch=selected,validation_loss=best,weight_sha256=sha256(folder/'best.pt'),
        final_sha256=sha256(folder/'final.pt'),specification_sha256=spec_hash,elapsed_seconds=time.time()-start))
    del graph,model,ema,optimizer,teacher;torch.cuda.empty_cache()
    return True


def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['prepare','preflight','pipeline'])
    parser.add_argument('--config',type=Path,default=DEFAULT);args=parser.parse_args()
    cfg=read_json(args.config);out=ROOT/cfg['output']
    torch.set_num_threads(cfg['runtime']['threads'])
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    try:
        with threadpool_limits(cfg['runtime']['threads']):
            spec=prepare(cfg,out)
            if args.command=='prepare': return
            if args.command=='preflight': preflight(cfg,out,spec);return
            receipt=read_json(out/'PREFLIGHT.json')
            assert receipt['status']=='PASSED' and receipt['specification_sha256']==sha256(out/'SPECIFICATION.json')
            if (out/'STOP.json').exists(): status(out,'STOPPED_BY_USER');return
            for stage in ('first','activity'):
                check_sources(spec)
                if train_stage(cfg,out,spec,stage) is False:return
            check_sources(spec)
            from .evaluate import run_evaluation
            if run_evaluation(cfg,out,spec) is False:return
            check_sources(spec)
            status(out,'COMPLETE',first_epochs=cfg['first']['maximum_epochs'],activity_epochs=cfg['activity']['maximum_epochs'])
    except BaseException:
        status(out,'FAILED',error=traceback.format_exc());raise


if __name__=='__main__': main()
