"""Fresh 100-epoch classifier; no changes to any receiver or frozen run.

PYTHONPATH=src python -m training.gp_mp.activity prepare|preflight|train
"""
import argparse
from copy import deepcopy
from dataclasses import asdict
import json
import math
import os
from pathlib import Path
import shutil
import signal
import time
import traceback

import numpy as np
import torch

from workspace import ROOT, repository_path
from fileio import sha256
from receiver.stmp.activity import Config, EvidenceNetwork, FrozenEvidence
from training.stmp.auxiliary import Trainer as OriginalTrainer
from training.stmp.auxiliary import atomic_json, atomic_torch, cpu_state, draw_queries
from training.scores.cuda_graph_auxiliary import query_parts, activity_forward
from training.scores.device import capture_device_rng, restore_device_rng
from .data import assets
from receiver.gp_mp.model import load_checkpoint
from .activity_batches import ActivityGraph, conditional_mean

DEFAULT = ROOT/'src/configs/training/gp_mp_activity.json'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def check_hashes(records):
    for name, expected in records.items():
        if sha256(repository_path(name)) != expected:
            raise ValueError('Protected input changed: '+name)


def prepare(cfg, out):
    if cfg['schema'] != 'white-mean-activity-training-v1':
        raise ValueError('Independent classifier recipe required')
    if not out.is_relative_to(ROOT/'result/snr_comparison/data'):
        raise ValueError('Use an independent output below snr_comparison/data')
    if cfg['query_covariance'] != 'vI':
        raise ValueError('White Gaussian classifier queries required')
    s = cfg['activity']
    if s['maximum_epochs'] != 100 or s['minimum_epochs'] != 100 or s['validation_patience'] <= 100:
        raise ValueError('Exactly 100 full epochs, without early stopping, required')
    original_path = repository_path(cfg['original_training'])
    if sha256(original_path) != cfg['original_training_sha256']:
        raise ValueError('Original activity specification changed')
    original = read(original_path)['configuration']['activity']
    for key in ('seed', 'validation_seed', 'batch_size', 'microbatch_size', 'learning_rate',
                'minimum_learning_rate', 'ema_decay', 'gradient_clip', 'checkpoint_seconds',
                'maximum_epochs', 'minimum_epochs', 'validation_patience', 'training_class_prior'):
        if s[key] != original[key]:
            raise ValueError('Matched original setting differs: '+key)
    check_hashes({cfg['first_checkpoint']: cfg['first_checkpoint_sha256'],
                  cfg['first_training_record']: cfg['first_training_record_sha256']})
    record = read(repository_path(cfg['first_training_record']))
    if record['status'] != 'COMPLETED' or record['weight_sha256'] != cfg['first_checkpoint_sha256']:
        raise ValueError('Completed, selected first checkpoint required')
    binding, _, paths, _, _, data_hashes = assets(cfg)
    prior_path = repository_path(binding['prior_definition'])
    prior = read(prior_path)
    if (prior['train_samples'], prior['validation_samples'], prior['shape'], prior['noise_support']) != (50000, 5000, [16,16,16], [.001,100.]):
        raise ValueError('Original full channel bank and noise support required')
    moments = repository_path(read(original_path)['configuration']['moments_file'])
    if sha256(moments) != prior['moments_sha256']:
        raise ValueError('Prior moments changed')
    out.mkdir(parents=True, exist_ok=True)
    initial_path = out/'initialization.pt'
    # Random construction only: no existing trained classifier is loaded.
    torch.manual_seed(s['seed'])
    initial = EvidenceNetwork(Config())
    initial_state = cpu_state(initial)
    if initial_path.exists():
        existing = torch.load(initial_path, map_location='cpu', weights_only=False)
        if existing['initialization'] != 'random' or any(not torch.equal(v, existing['state_dict'][k]) for k,v in initial_state.items()):
            raise ValueError('Saved random initialization differs')
    else:
        atomic_torch(initial_path, dict(initialization='random', optimizer_steps=0,
            pretrained_classifier=None, seed=s['seed'], config=asdict(initial.config), state_dict=initial_state))
    protected = cfg.get('protected_files', {})
    check_hashes(protected)
    source_paths = [ROOT/'src/workspace.py', ROOT/'src/fileio.py', ROOT/'src/receiver/stmp/activity.py',
        ROOT/'src/training/stmp/auxiliary.py',
        ROOT/'src/training/scores/cuda_graph_auxiliary.py', ROOT/'src/training/scores/device.py']
    # Bind the actual trainer and shared training/score dependencies.
    for folder in ('src/training/gp_mp', 'src/training/stmp', 'src/training/scores',
                   'src/receiver/gp_mp', 'src/receiver/stmp', 'src/networks'):
        directory = ROOT/folder
        if not directory.is_dir():
            raise FileNotFoundError(directory)
        source_paths.extend(directory.rglob('*.py'))
    sources = {p.relative_to(ROOT).as_posix(): sha256(p) for p in sorted(set(source_paths))}
    specification = dict(schema=cfg['schema'], configuration=cfg,
        data_paths={k: str(v.relative_to(ROOT)) for k,v in paths.items()}, data_hashes=data_hashes,
        prior_definition=str(prior_path.relative_to(ROOT)), prior_definition_sha256=sha256(prior_path),
        moments_file=str(moments.relative_to(ROOT)), moments_sha256=sha256(moments),
        initialization_sha256=sha256(initial_path), initialization='random', pretrained_classifier=None,
        source_hashes=sources, protected=protected)
    spec_path = out/'specification.json'
    if spec_path.exists():
        if read(spec_path) != specification:
            raise ValueError('Existing training specification differs; use a separate run')
    else:
        atomic_json(spec_path, specification)
        atomic_json(out/'recipe.json', cfg)
        for name in sources:
            dest = out/'source'/name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT/name, dest)
    return specification


class Trainer(OriginalTrainer):
    def __init__(self, cfg, out, spec):
        self.config, self.output, self.stage = cfg, out, 'activity'
        self.device, self.stop = cfg['runtime']['device'], False
        self.settings = dict(cfg['activity'], initial_checkpoint_sha256=spec['initialization_sha256'])
        self.specification_hash = sha256(out/'specification.json')
        self.prior = read(repository_path(spec['prior_definition']))
        self.prior_hash = spec['prior_definition_sha256']
        self.first_path = repository_path(cfg['first_checkpoint'])
        self.first_hash, self.second_hash = cfg['first_checkpoint_sha256'], None
        self.first, _ = load_checkpoint(self.first_path, self.device)
        self.first.eval().requires_grad_(False)
        with np.load(repository_path(spec['moments_file']), allow_pickle=False) as data:
            self.prior_mean = data['prior_mean'].copy()
            self.prior_second_moment = float(data['prior_second_moment'])
        self.data = {k: np.load(repository_path(p), mmap_mode='r', allow_pickle=False)
                     for k,p in spec['data_paths'].items()}
        for split, bank in self.data.items():
            if bank.shape != (self.prior[split+'_samples'],16,16,16) or bank.dtype != np.complex64:
                raise ValueError('Full channel bank shape/dtype mismatch')
        self.spec = spec

    def model(self):
        path = self.output/'initialization.pt'
        if sha256(path) != self.settings['initial_checkpoint_sha256']:
            raise ValueError('Random initialization changed')
        blob = torch.load(path, map_location='cpu', weights_only=False)
        model = EvidenceNetwork(Config(**blob['config']))
        model.load_state_dict(blob['state_dict'], strict=True)
        return model.to(self.device)

    def validation_cache(self):
        # Stream the original RNG draw order into mmap files to keep RAM bounded
        # without changing the fixed validation draws. No noise resampling.
        folder = self.output/'validation_cache'
        folder.mkdir(exist_ok=True)
        complete = folder/'COMPLETE.json'
        names = ('positive','negative','positive_mean','negative_mean','variance')
        if complete.exists():
            record = read(complete)
            if record['specification_sha256'] != self.specification_hash:
                raise ValueError('Fixed validation identity changed')
            for name in names:
                if sha256(folder/(name+'.npy')) != record['hashes'][name]:
                    raise ValueError('Fixed validation file changed: '+name)
        else:
            bank = self.data['validation']; n = len(bank)
            rng = np.random.default_rng(self.settings['validation_seed'])
            lo, hi = self.prior['noise_support']
            variance = np.exp(rng.uniform(np.log(lo), np.log(hi), n)).astype(np.float32)
            np.save(folder/'variance.npy', variance, allow_pickle=False)
            for label in ('positive','negative'):
                obs = np.lib.format.open_memmap(folder/(label+'.npy'), mode='w+', dtype=np.float32, shape=(n,2,16,16,16))
                means = np.lib.format.open_memmap(folder/(label+'_mean.npy'), mode='w+', dtype=np.float32, shape=obs.shape)
                for start in range(0,n,self.settings['microbatch_size']):
                    stop = min(start+self.settings['microbatch_size'], n)
                    v = variance[start:stop]
                    query = np.sqrt(v[:,None,None,None,None]/2)*rng.standard_normal((stop-start,2,16,16,16)).astype(np.float32)
                    if label == 'positive':
                        z = bank[start:stop]
                        query += np.stack((z.real,z.imag),1).astype(np.float32)/self.prior['global_complex_rms']
                    with torch.inference_mode():
                        mean = conditional_mean(self.first, torch.as_tensor(query,device=self.device),
                                                torch.as_tensor(v,device=self.device)).cpu().numpy()
                    if not np.isfinite(mean).all():
                        raise FloatingPointError('Nonfinite fixed teacher mean')
                    obs[start:stop] = query; means[start:stop] = mean
                    if start % 320 == 0:
                        self.status('PREPARING_FIXED_VALIDATION', class_name=label, samples=stop, validation_samples=n)
                obs.flush(); means.flush()
                del obs, means
            atomic_json(complete, dict(specification_sha256=self.specification_hash,
                hashes={name:sha256(folder/(name+'.npy')) for name in names}))
        cache = {name:np.load(folder/(name+'.npy'), mmap_mode='r', allow_pickle=False) for name in names}
        cache['means'] = [cache.pop('positive_mean'), cache.pop('negative_mean')]
        return cache

    def train(self):
        completed = self.output/'complete.json'
        if completed.exists():
            record = read(completed)
            if record['specification_sha256'] != self.specification_hash or record['weight_sha256'] != sha256(self.selected_path()):
                raise ValueError('Completed training identity changed')
            self.status('ALREADY_COMPLETED', epochs=record['epochs'])
            return
        torch.manual_seed(self.settings['seed'])
        rng = np.random.default_rng(self.settings['seed'])
        model = self.model(); ema = deepcopy(model).eval().requires_grad_(False)
        optimizer = torch.optim.Adam(model.parameters(), lr=self.settings['learning_rate'])
        epoch, cursor, steps, indices = 1, 0, 0, None
        best, selected_epoch, history, loss_sum, seen = math.inf, 0, [], 0., 0
        last = self.output/'last.pt'
        if last.exists():
            state = torch.load(last,map_location='cpu',weights_only=False)
            if state['specification_sha256'] != self.specification_hash:
                raise ValueError('Resume identity changed')
            model.load_state_dict(state['model']); ema.load_state_dict(state['ema'])
            optimizer.load_state_dict(state['optimizer'])
            rng.bit_generator.state = state['rng']; torch.set_rng_state(state['torch_rng'])
            restore_device_rng(self.device,state)
            epoch,cursor,steps,indices,best,selected_epoch,history,loss_sum,seen = (
                state[k] for k in ('epoch','cursor','steps','indices','best','selected_epoch','history','loss_sum','seen'))
            del state
        self.status('PREPARING_VALIDATION', resume=last.exists(), maximum_epochs=100,
                    parameters=sum(p.numel() for p in model.parameters()), initialization='random')
        cache = self.validation_cache()
        last_saved = time.time()

        def checkpoint():
            nonlocal last_saved
            atomic_torch(last, dict(schema='colored-mean-activity-resume-v1', specification_sha256=self.specification_hash,
                model=cpu_state(model), ema=cpu_state(ema), optimizer=optimizer.state_dict(),
                rng=rng.bit_generator.state, torch_rng=torch.get_rng_state(), **capture_device_rng(self.device),
                epoch=epoch,cursor=cursor,steps=steps,indices=indices,best=best,selected_epoch=selected_epoch,
                history=history,loss_sum=loss_sum,seen=seen))
            last_saved = time.time()

        if not last.exists():
            baseline = self.validation(ema,cache); best = baseline['loss']
            history.append(dict(epoch=0,optimizer_steps=0,validation=baseline))
            atomic_json(self.output/'baseline.json',baseline)
            self.save_selected(ema,0,0,baseline); checkpoint()
        graph = ActivityGraph(model,self.first,'activity',self.settings['batch_size'])
        started = time.time()
        while epoch <= 100:
            epoch_started = time.time()
            rate = self.settings['minimum_learning_rate']+.5*(self.settings['learning_rate']-self.settings['minimum_learning_rate'])*(1+math.cos(math.pi*(epoch-1)/99))
            for group in optimizer.param_groups:
                group['lr'] = rate
            model.train()
            if indices is None:
                indices = rng.permutation(len(self.data['train']))
            while cursor < len(indices):
                if self.stop or (self.output/'pause.request').exists():
                    checkpoint()
                    self.status('PAUSED',epoch=epoch,samples=cursor,optimizer_steps=steps,resumable=True)
                    return
                chosen = indices[cursor:cursor+self.settings['batch_size']]
                parts = query_parts(self.data['train'],chosen,rng,self.prior,self.settings,'activity')
                optimizer.zero_grad(set_to_none=True)
                for value,count in graph.backward(parts,use_graph=self.config['runtime']['cuda_graph']):
                    loss_sum += value*count; seen += count
                if any(p.grad is not None for p in self.first.parameters()):
                    raise AssertionError('Frozen first received gradients')
                norm = torch.nn.utils.clip_grad_norm_(model.parameters(),self.settings['gradient_clip'],error_if_nonfinite=True)
                optimizer.step()
                with torch.no_grad():
                    torch._foreach_lerp_(list(ema.parameters()),list(model.parameters()),1-self.settings['ema_decay'])
                cursor += len(chosen); steps += 1
                if time.time()-last_saved >= self.settings['checkpoint_seconds']:
                    checkpoint()
                if steps % 50 == 0:
                    self.status('TRAINING',epoch=epoch,maximum_epochs=100,samples=cursor,train_samples=len(indices),
                        optimizer_steps=steps,loss=loss_sum/seen,learning_rate=rate,
                        gradient_norm_before_clip=float(norm.cpu()),elapsed_epoch_seconds=time.time()-epoch_started)
            if sha256(self.first_path) != self.first_hash:
                raise ValueError('Frozen first changed')
            self.status('VALIDATING',epoch=epoch,optimizer_steps=steps)
            measured = self.validation(ema,cache)
            history.append(dict(epoch=epoch,optimizer_steps=steps,train_loss=loss_sum/seen,validation=measured,
                                learning_rate=rate,elapsed_epoch_seconds=time.time()-epoch_started))
            atomic_json(self.output/'history.json',history)
            if measured['loss'] < best:
                best,selected_epoch = measured['loss'],epoch
                self.save_selected(ema,epoch,steps,measured)
            self.status('EPOCH_COMPLETE',epoch=epoch,maximum_epochs=100,optimizer_steps=steps,
                validation_bce=measured['loss'],validation_aer_at_rho_0_1=measured['deployments']['0.1']['aer'],
                selected_epoch=selected_epoch,elapsed_invocation_seconds=time.time()-started)
            epoch += 1; cursor=0; indices=None; loss_sum=0.; seen=0
            checkpoint()
        if steps != 100*math.ceil(len(self.data['train'])/self.settings['batch_size']):
            raise AssertionError('Full 100-epoch budget incomplete')
        check_hashes(self.spec['protected'])
        self.save_selected(ema,100,steps,history[-1]['validation'],destination=self.output/'evidence_final.pt')
        atomic_json(completed,dict(status='COMPLETED',epochs=100,optimizer_steps=steps,selected_epoch=selected_epoch,
            stopping_reason='EXACTLY_100_FULL_EPOCHS',initialization='random',pretrained_classifier=None,
            specification_sha256=self.specification_hash,initialization_sha256=self.spec['initialization_sha256'],
            first_sha256=self.first_hash,second_sha256=None,weight_sha256=sha256(self.selected_path()),
            final_weight_sha256=sha256(self.output/'evidence_final.pt'),train_samples=50000,validation_samples=5000,
            samples_processed=5000000,examples_processed=10000000,protected_verified=True,
            receiver_performance_verified=False))
        self.status('COMPLETED',epochs=100,optimizer_steps=steps,selected_epoch=selected_epoch)


def preflight(trainer):
    from receiver.gp_mp.moments import Moments
    rng = np.random.default_rng(2026102509)
    parts = query_parts(trainer.data['train'],np.arange(32),rng,trainer.prior,trainer.settings,'activity')
    model = trainer.model()
    original_state = cpu_state(model)
    first_before = cpu_state(trainer.first)
    r,v = (torch.as_tensor(a,device=trainer.device) for a in parts[0])
    with torch.no_grad():
        mean = conditional_mean(trainer.first,r,v)
        assert torch.count_nonzero(model(r,v,mean)) == 0
    # Exercise all classifier gradients in this disposable test model.
    with torch.no_grad():
        model.readout[-1].weight.normal_(std=.01)
    with torch.no_grad():
        torch.testing.assert_close(model(r,v,mean),activity_forward(model,r,v,mean),rtol=1e-5,atol=1e-6)
    graph = ActivityGraph(model,trainer.first,'activity',32)
    losses_eager = graph.backward(parts,use_graph=False)
    grads = [p.grad.clone() for p in model.parameters()]
    model.zero_grad(set_to_none=True)
    losses_graph = graph.backward(parts,use_graph=True)
    np.testing.assert_allclose(np.array(losses_graph)[:,0],np.array(losses_eager)[:,0],rtol=2e-5,atol=2e-6)
    max_difference=0.
    for p,g in zip(model.parameters(),grads):
        torch.testing.assert_close(p.grad,g,rtol=5e-4,atol=3e-6)
        max_difference=max(max_difference,float((p.grad-g).abs().max()))
    optimizer=torch.optim.Adam(model.parameters(),lr=trainer.settings['learning_rate'])
    optimizer.step()
    # A second replay must use updated parameters and new inputs, not stale data.
    next_parts=query_parts(trainer.data['train'],np.arange(32,64),rng,trainer.prior,trainer.settings,'activity')
    model.zero_grad(set_to_none=True)
    next_graph=graph.backward(next_parts,use_graph=True)
    next_grads=[p.grad.clone() for p in model.parameters()]
    model.zero_grad(set_to_none=True)
    next_eager=graph.backward(next_parts,use_graph=False)
    np.testing.assert_allclose(np.array(next_graph)[:,0],np.array(next_eager)[:,0],rtol=2e-5,atol=2e-6)
    for p,g in zip(model.parameters(),next_grads):
        torch.testing.assert_close(p.grad,g,rtol=5e-4,atol=3e-6)
    assert all(p.grad is None for p in trainer.first.parameters())
    assert all(torch.equal(v,first_before[k]) for k,v in cpu_state(trainer.first).items())
    assert any(not torch.equal(v,original_state[k]) for k,v in cpu_state(model).items())
    # Compare the actual receiver path at the SAME batch size. TF32 convolution
    # kernel choices across batch sizes have a separately recorded ~0.6% effect.
    runtime=Moments(trainer.first_path,device=trainer.device,batch_size=len(r))
    rr=parts[0][0]; vv=parts[0][1]
    receiver=runtime.infer(rr[:,0]+1j*rr[:,1],vv).mean
    expected=mean.cpu().numpy()
    np.testing.assert_array_equal(receiver,expected[:,0].astype(float)+1j*expected[:,1].astype(float))
    # Verify exact RNG/packing equivalence of streamed fixed validation queries.
    seed=trainer.settings['validation_seed']; bank=trainer.data['validation'][:19]
    full=draw_queries(bank,np.random.default_rng(seed),trainer.prior['global_complex_rms'],trainer.prior['noise_support'],paired=True)
    vrng=np.random.default_rng(seed)
    lo,hi=trainer.prior['noise_support']
    vstream=np.exp(vrng.uniform(np.log(lo),np.log(hi),len(bank))).astype(np.float32)
    np.testing.assert_array_equal(vstream,full['variance'])
    for label in ('positive','negative'):
        for start in range(0,len(bank),7):
            stop=min(start+7,len(bank)); vv=vstream[start:stop]
            x=np.sqrt(vv[:,None,None,None,None]/2)*vrng.standard_normal((stop-start,2,16,16,16)).astype(np.float32)
            if label=='positive':
                z=bank[start:stop]
                x+=np.stack((z.real,z.imag),1).astype(np.float32)/trainer.prior['global_complex_rms']
            np.testing.assert_array_equal(x,full[label][start:stop])
    # Saved activity checkpoint can be read by the existing inference interface.
    trial=trainer.output/'preflight_evidence.pt'
    trainer.save_selected(model,0,1,dict(loss=float(next_eager[0][0])),destination=trial)
    loaded=FrozenEvidence(trial,device=trainer.device)
    with torch.no_grad():
        torch.testing.assert_close(loaded.network(r,v,mean),model(r,v,mean),rtol=0,atol=0)
    check_hashes(trainer.spec['protected'])
    result=dict(status='PASS',specification_sha256=trainer.specification_hash,
        random_initialization=True,trained_classifier_loaded=False,teacher_unchanged=True,
        eager_graph_max_gradient_difference=max_difference,second_replay_matches_eager=True,
        receiver_mean_matches=True,fixed_validation_rng_matches=True,checkpoint_reload_matches=True,
        inference_binding_changed=False,formal_receiver_evaluation_used=False,
        training_initialization_untouched=sha256(trainer.output/'initialization.pt')==trainer.spec['initialization_sha256'])
    atomic_json(trainer.output/'PREFLIGHT.json',result)
    print(json.dumps(result),flush=True)


def main(argv=None):
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('command',choices=('prepare','preflight','train'))
    parser.add_argument('--config',type=Path,default=DEFAULT)
    args=parser.parse_args(argv); cfg=read(args.config)
    out=repository_path(cfg['output']).resolve()
    torch.set_num_threads(cfg['runtime']['threads'])
    try:
        spec=prepare(cfg,out)
        if args.command=='prepare':
            print(json.dumps(dict(status='PREPARED',output=str(out),epochs=100,initialization='random')),flush=True)
            return
        trainer=Trainer(cfg,out,spec)
        if args.command=='preflight':
            preflight(trainer)
        else:
            checks=read(out/'PREFLIGHT.json')
            if checks['status']!='PASS' or checks['specification_sha256']!=trainer.specification_hash:
                raise ValueError('Matching preflight required')
            signal.signal(signal.SIGINT,trainer.request_stop)
            signal.signal(signal.SIGTERM,trainer.request_stop)
            trainer.train()
    except Exception:
        out.mkdir(parents=True,exist_ok=True)
        atomic_json(out/('FAILED_'+args.command+'.json'),dict(status='FAILED',pid=os.getpid(),
            updated_unix=time.time(),error=traceback.format_exc()))
        raise


if __name__=='__main__':
    main()
