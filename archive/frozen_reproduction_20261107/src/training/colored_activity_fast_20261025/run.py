"""Resume the same classifier with overlapped data preparation and pinned H2D."""
from copy import deepcopy
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
from project import ROOT
from utils import sha256
from training.STMP.auxiliary import atomic_json, atomic_torch, cpu_state
from training.scores.device import capture_device_rng, restore_device_rng
from training.colored_activity_20261025.run import Trainer as BaseTrainer, read, check_hashes
from .execution import Prefetch, PinnedActivityGraph


class Trainer(BaseTrainer):
    def __init__(self,cfg,out,spec,execution_hash):
        super().__init__(cfg,out,spec)
        self.execution_hash=execution_hash

    def status(self,status,**values):
        super().status(status,execution='prefetch_pinned_same_batch',**values)

    def save_selected(self,model,epoch,steps,measured,*,destination=None):
        super().save_selected(model,epoch,steps,measured,destination=destination)
        path=self.selected_path() if destination is None else destination
        blob=torch.load(path,map_location='cpu',weights_only=False)
        blob['metadata']['execution_plan_sha256']=self.execution_hash
        atomic_torch(path,blob)

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
            atomic_torch(last, dict(schema='colored-mean-activity-resume-v1', specification_sha256=self.specification_hash, execution_plan_sha256=self.execution_hash,
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
        graph = PinnedActivityGraph(model,self.first,'activity',self.settings['batch_size'])
        started = time.time()
        while epoch <= 100:
            epoch_started = time.time()
            rate = self.settings['minimum_learning_rate']+.5*(self.settings['learning_rate']-self.settings['minimum_learning_rate'])*(1+math.cos(math.pi*(epoch-1)/99))
            for group in optimizer.param_groups:
                group['lr'] = rate
            model.train()
            if indices is None:
                indices = rng.permutation(len(self.data['train']))
            prefetch = Prefetch(self.data['train'],indices,cursor,rng,self.prior,self.settings,graph.validate)
            try:
                while cursor < len(indices):
                    if self.stop or (self.output/'pause.request').exists():
                        checkpoint()
                        self.status('PAUSED',epoch=epoch,samples=cursor,optimizer_steps=steps,resumable=True)
                        return
                    chosen = indices[cursor:cursor+self.settings['batch_size']]
                    parts = prefetch.next(cursor,rng)
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
            finally:
                prefetch.close()
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
        atomic_json(completed,dict(status='COMPLETED',execution_plan_sha256=self.execution_hash,epochs=100,optimizer_steps=steps,selected_epoch=selected_epoch,
            stopping_reason='EXACTLY_100_FULL_EPOCHS',initialization='random',pretrained_classifier=None,
            specification_sha256=self.specification_hash,initialization_sha256=self.spec['initialization_sha256'],
            first_sha256=self.first_hash,second_sha256=None,weight_sha256=sha256(self.selected_path()),
            final_weight_sha256=sha256(self.output/'evidence_final.pt'),train_samples=50000,validation_samples=5000,
            samples_processed=5000000,examples_processed=10000000,protected_verified=True,
            receiver_performance_verified=False))
        self.status('COMPLETED',epochs=100,optimizer_steps=steps,selected_epoch=selected_epoch)


def main():
    torch.set_num_threads(1)
    cfg=read(ROOT/'src/configs/training/colored_activity_20261025.json')
    out=ROOT/cfg['output']; folder=out/'acceleration_20261025'
    folder.mkdir(exist_ok=True)
    try:
        spec=read(out/'specification.json'); benchmark=read(folder/'BENCHMARK.json')
        if benchmark['status']!='PASS' or benchmark['speedup']<1.05:
            raise ValueError('Verified meaningful execution speedup required')
        if benchmark['original_specification_sha256']!=sha256(out/'specification.json'):
            raise ValueError('Original training specification differs')
        check_hashes(benchmark['source_hashes'])
        check_hashes(spec['source_hashes']);check_hashes(spec['protected']);check_hashes(spec['data_hashes'])
        parent=folder/'parent_last.pt'
        if not parent.exists():
            if sha256(out/'last.pt')!=benchmark['parent_checkpoint_sha256']:
                raise ValueError('The benchmarked parent checkpoint differs')
            shutil.copy2(out/'last.pt',parent)
            for name in ('evidence_best.pt','history.json','status.json'):
                shutil.copy2(out/name,folder/('parent_'+name))
        if sha256(parent)!=benchmark['parent_checkpoint_sha256']:
            raise ValueError('Saved parent checkpoint changed')
        execution=dict(schema='activity-execution-continuation-v1',
            original_specification_sha256=sha256(out/'specification.json'),
            benchmark_sha256=sha256(folder/'BENCHMARK.json'),parent_checkpoint_sha256=sha256(parent),
            source_hashes={str(p.relative_to(ROOT)):sha256(p) for p in Path(__file__).parent.glob('*.py')},
            changes=['One background batch producer with its own cloned NumPy RNG',
                     'Checkpoint RNG refers to the last consumed query, not speculative prefetch',
                     'Pinned host buffers and asynchronous H2D copies before unchanged CUDA graph'],
            unchanged=['Samples and order','Noise draws','Effective batch 32 and microbatch 16',
                'Float32 and TF32 settings','First teacher','BCE, gradient clip, Adam, EMA',
                'Validation and selection','100 cumulative epochs'],
            starting_epoch=benchmark['checkpoint_epoch'],starting_cursor=benchmark['checkpoint_cursor'])
        path=folder/'EXECUTION.json'
        if path.exists():
            if read(path)!=execution:raise ValueError('Execution continuation changed')
        else:
            atomic_json(path,execution)
            for name in execution['source_hashes']:
                dest=folder/'source'/name;dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(ROOT/name,dest)
        trainer=Trainer(cfg,out,spec,sha256(path))
        signal.signal(signal.SIGINT,trainer.request_stop);signal.signal(signal.SIGTERM,trainer.request_stop)
        trainer.train()
    except Exception:
        atomic_json(folder/'FAILED.json',dict(status='FAILED',pid=os.getpid(),updated_unix=time.time(),error=traceback.format_exc()))
        raise


if __name__=='__main__':main()
