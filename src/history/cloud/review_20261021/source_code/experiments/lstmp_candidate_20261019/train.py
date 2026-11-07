"""Explicit training entry, followed by progressive five-layer receiver training.

Resume only this run's checkpoints. Explicit pretrained-score configuration
reuses the completed first score without overwriting any source checkpoint.
"""
import argparse, copy, json, math, os, time, traceback, warnings, platform
from pathlib import Path
import numpy as np
import torch
import psutil
from torch import nn
from threadpoolctl import threadpool_limits
from .common import ROOT, OUT, CONFIG, PROJECT_SOURCE, save_json, save_torch, cpu_state, status, log_event, check_budget, sha, real_tensor
from .backbone import FreshScore, score_config_dict
from .data import build_prior, build_cases, Cases, case_path
from .receiver import Receiver, loss, evaluate, synchronize, summarize_rows
from .optimization import clip_gradient_norm
from .fixed_budget import epochs_for_depth, epoch_order, plateau_reached, prepare_continuation
from .execution import configure_execution


def score_batch(bank, indices, scale, device, seed, fixed=False):
    generator = torch.Generator().manual_seed(seed)
    h = real_tensor(np.asarray(bank[indices])/scale,'cpu')
    lo,hi=CONFIG['complex_variance_support']
    if fixed:
        v=torch.tensor([.001,.01,.1,1.,10.,100.])[torch.as_tensor(indices)%6]
    else:
        v=torch.exp(math.log(lo)+(math.log(hi)-math.log(lo))*torch.rand(len(indices),generator=generator))
    epsilon=torch.randn(h.shape,generator=generator)
    noisy=h+torch.sqrt(v/2)[:,None,None,None,None]*epsilon
    return noisy.to(device),v.to(device),epsilon.to(device),h.to(device)


def validate_score(model, bank, scale, device, started=None):
    sums=np.zeros(4); count=0
    model.eval()
    with torch.no_grad():
        for begin in range(0,len(bank),CONFIG['pretraining']['microbatch']):
            if started is not None: check_budget(started)
            indices=np.arange(begin,min(begin+CONFIG['pretraining']['microbatch'],len(bank)))
            r,v,epsilon,h=score_batch(bank,indices,scale,device,CONFIG['seed']+90000+begin,True)
            score=model(r,v); sigma=torch.sqrt(v/2)[:,None,None,None,None]
            value=(sigma*score+epsilon).square().flatten(1).mean(1)
            mean=r+v[:,None,None,None,None]/2*score
            sums+=np.array([float(value.sum()),float((mean-h).square().sum()),float(h.square().sum()),float((r-h).square().sum())])
            count+=len(indices)
    if not np.isfinite(sums).all(): raise FloatingPointError('Nonfinite score validation')
    return dict(loss=sums[0]/count,nmse_db=10*np.log10(sums[1]/sums[2]),
                noisy_nmse_db=10*np.log10(sums[3]/sums[2]),samples=count)


def completed_checkpoint(folder):
    receipt = folder/'COMPLETE.json'
    if not receipt.exists(): return False
    saved = json.loads(receipt.read_text())
    if saved.get('status') != 'COMPLETE' or saved.get('checkpoint_sha256') != sha(folder/'best.pt'):
        raise ValueError(f'Completed stage checkpoint changed: {folder.name}')
    return True


def pretrain(scale, device, started):
    folder=OUT/'checkpoints'/'pretrain'; folder.mkdir(parents=True,exist_ok=True)
    check_budget(started)
    if completed_checkpoint(folder): return folder/'best.pt'
    s=CONFIG['pretraining']
    train=np.load(OUT/'data/prior_train.npy',mmap_mode='r')
    validation=np.load(OUT/'data/prior_validation.npy',mmap_mode='r')
    torch.manual_seed(CONFIG['seed'])
    model=FreshScore(width=CONFIG['width']).to(device)
    ema=copy.deepcopy(model).eval().requires_grad_(False)
    optimizer=torch.optim.Adam(model.parameters(),lr=s['learning_rate'])
    epoch,cursor,steps,best,stale=1,0,0,math.inf,0
    history=[]; loss_sum=0.; samples=0; selected_epoch=0
    resume=folder/'last.pt'
    if resume.exists():
        state=torch.load(resume,map_location='cpu',weights_only=False)
        model.load_state_dict(state['model']);ema.load_state_dict(state['ema']);optimizer.load_state_dict(state['optimizer'])
        epoch,cursor,steps,best,stale,history,loss_sum,samples,selected_epoch=(state[k] for k in
            ('epoch','cursor','steps','best','stale','history','loss_sum','samples','selected_epoch'))
    else:
        baseline=validate_score(model,validation,scale,device,started)
        best=baseline['loss'];history=[dict(epoch=0,validation=baseline,selected=True)]
        save_torch(folder/'initial_random.pt',dict(state=cpu_state(model),scale=scale,architecture=score_config_dict(CONFIG['width']),initialization='random'))
        save_torch(folder/'best.pt',dict(state=cpu_state(ema),scale=scale,epoch=0,validation=baseline))
        log_event(dict(stage='PRETRAIN_BASELINE',**baseline))

    def checkpoint():
        save_torch(resume,dict(model=cpu_state(model),ema=cpu_state(ema),optimizer=optimizer.state_dict(),
             epoch=epoch,cursor=cursor,steps=steps,best=best,stale=stale,history=history,
             loss_sum=loss_sum,samples=samples,selected_epoch=selected_epoch))
    try:
        while epoch<=s['epochs']:
            if epoch-1>=s['minimum_epochs'] and stale>=s['patience']:break
            order=np.random.default_rng(CONFIG['seed']+epoch).permutation(len(train))
            lr=s['minimum_learning_rate']+.5*(s['learning_rate']-s['minimum_learning_rate'])*(1+math.cos(math.pi*(epoch-1)/max(1,s['epochs']-1)))
            for group in optimizer.param_groups:group['lr']=lr
            model.train()
            while cursor<len(order):
                check_budget(started); optimizer.zero_grad(set_to_none=True)
                batch=order[cursor:cursor+s['batch_size']]; total=0.
                for offset in range(0,len(batch),s['microbatch']):
                    check_budget(started)
                    ids=batch[offset:offset+s['microbatch']]
                    r,v,epsilon,h=score_batch(train,ids,scale,device,CONFIG['seed']+steps*100+offset)
                    value=(torch.sqrt(v/2)[:,None,None,None,None]*model(r,v)+epsilon).square().mean()
                    if not bool(torch.isfinite(value)):raise FloatingPointError('Nonfinite pretraining loss')
                    (value*len(ids)/len(batch)).backward();total+=float(value.detach())*len(ids)/len(batch)
                norm=nn.utils.clip_grad_norm_(model.parameters(),s['gradient_clip'],error_if_nonfinite=True)
                optimizer.step()
                with torch.no_grad():
                    for target,source in zip(ema.parameters(),model.parameters()):
                        if source.requires_grad:target.lerp_(source,1-s['ema_decay'])
                    for target,source in zip(ema.buffers(),model.buffers()):target.copy_(source)
                steps+=1;cursor+=len(batch);samples+=len(batch);loss_sum+=total*len(batch)
                if steps%s['checkpoint_steps']==0:checkpoint()
                if steps%10==0 or steps==1:
                    status('SCORE_PRETRAINING',epoch=epoch,max_epochs=s['epochs'],samples=cursor,total=len(train),steps=steps,
                           loss=total,gradient_norm=float(norm),learning_rate=lr,elapsed_seconds=time.time()-started)
            result=validate_score(ema,validation,scale,device,started)
            selected=result['loss']<best
            significant=result['loss']<best*(1-s['relative_improvement'])
            if selected:
                best=result['loss'];selected_epoch=epoch
                save_torch(folder/'best.pt',dict(state=cpu_state(ema),scale=scale,epoch=epoch,validation=result))
            stale=0 if significant else stale+1
            row=dict(epoch=epoch,train_loss=loss_sum/samples,validation=result,selected=selected)
            history.append(row);save_json(folder/'history.json',history);log_event(dict(stage='PRETRAIN_VALIDATION',**row))
            epoch+=1;cursor=0;loss_sum=0.;samples=0;checkpoint()
            if epoch-1>=s['minimum_epochs'] and stale>=s['patience']:break
        save_json(folder/'COMPLETE.json',dict(status='COMPLETE',selected_epoch=selected_epoch,steps=steps,
            reason='VALIDATION_PLATEAU' if epoch-1<s['epochs'] else 'MAXIMUM_BUDGET',best_validation_loss=best,
            checkpoint_sha256=sha(folder/'best.pt')))
    except BaseException:
        checkpoint();raise
    return folder/'best.pt'


def validate_receiver(model, cases, depth, epoch, started):
    def progress(rows):
        if len(rows)%64==0 or len(rows)==len(cases):
            status('RECEIVER_VALIDATION',depth=depth,epoch=epoch,scenes=len(rows),total=len(cases),
                   elapsed_seconds=time.time()-started)
    return evaluate(model,cases,started=started,on_row=progress)


def train_receiver(pretrained, scale, device, started):
    s=CONFIG['receiver']
    build_cases('train',scale,started);build_cases('validation',scale,started)
    training,validation=Cases('train',scale,device),Cases('validation',scale,device)
    initial=torch.load(pretrained,map_location='cpu',weights_only=False)['state']
    model=Receiver()
    for depth in range(1,s['maximum_depth']+1):
        maximum_epochs=epochs_for_depth(depth)
        torch.manual_seed(CONFIG['seed']+depth)
        model.add_layer(initial);model.to(device)
        folder=OUT/'checkpoints'/f'depth_{depth}';folder.mkdir(parents=True,exist_ok=True)
        check_budget(started)
        if completed_checkpoint(folder):
            model.load_state_dict(torch.load(folder/'best.pt',map_location=device,weights_only=False)['state']);continue
        calibration=[layer.calibration for layer in model.layers]
        scores=[p for layer in model.layers for p in layer.score.parameters() if p.requires_grad]
        activity=[p for layer in model.layers for p in layer.activity.parameters() if p.requires_grad]
        optimizer=torch.optim.Adam([dict(params=scores,lr=s['learning_rate']),
            dict(params=activity,lr=s.get('activity_learning_rate',s['learning_rate'])),
            dict(params=calibration,lr=s['calibration_learning_rate'])],foreach=False)
        epoch,cursor,steps,best,stale=1,0,0,math.inf,0
        history=[];loss_sum=0.;samples=0;selected_epoch=0
        resume=folder/'last.pt'
        if resume.exists():
            state=torch.load(resume,map_location='cpu',weights_only=False)
            model.load_state_dict(state['state']);optimizer.load_state_dict(state['optimizer'])
            epoch,cursor,steps,best,stale,history,loss_sum,samples,selected_epoch=(state[k] for k in
                ('epoch','cursor','steps','best','stale','history','loss_sum','samples','selected_epoch'))
        else:
            status('INITIAL_VALIDATION',depth=depth,scenes=len(validation),elapsed_seconds=time.time()-started)
            result=validate_receiver(model,validation,depth,0,started);best=result['summary']['loss']
            save_json(folder/'initial_validation.json',result)
            save_torch(folder/'best.pt',dict(state=cpu_state(model),depth=depth,scale=scale,epoch=0))
            history=[dict(epoch=0,validation=result['summary'],selected=True)]

        configure_execution(model,optimizer,CONFIG.get('execution',{}),device)

        def checkpoint():
            save_torch(resume,dict(state=cpu_state(model),optimizer=optimizer.state_dict(),depth=depth,
                epoch=epoch,cursor=cursor,steps=steps,best=best,stale=stale,history=history,
                loss_sum=loss_sum,samples=samples,selected_epoch=selected_epoch))
            save_json(OUT/'ACTIVE_TIME.json',dict(consumed_seconds=time.time()-started))
        try:
            while epoch<=maximum_epochs:
                if plateau_reached(epoch,stale):break
                order=epoch_order(training.indices,depth,epoch)
                model.train()
                while cursor<len(order):
                    check_budget(started);optimizer.zero_grad(set_to_none=True)
                    public,labels,info=training[int(order[cursor])]
                    outputs,diag=model(public);value=loss(outputs,labels)
                    if not bool(torch.isfinite(value)):raise FloatingPointError(f'Nonfinite receiver loss {info}')
                    value.backward();norm=clip_gradient_norm(model.parameters(),1.)
                    optimizer.step();steps+=1;cursor+=1;samples+=1;loss_sum+=float(value.detach())
                    if steps%s['checkpoint_steps']==0 or steps==1:checkpoint()
                    if steps%8==0 or steps==1:
                        status('PROGRESSIVE_RECEIVER_TRAINING',depth=depth,epoch=epoch,scene=cursor,total=len(order),steps=steps,
                               max_epochs=maximum_epochs,
                               loss=float(value.detach()),gradient_norm=float(norm),diagnostics=diag,
                               selected_epoch=selected_epoch,best_validation_loss=best,
                               gpu_memory_allocated_bytes=torch.cuda.memory_allocated() if str(device).startswith('cuda') else 0,
                               elapsed_seconds=time.time()-started)
                result=validate_receiver(model,validation,depth,epoch,started);score=result['summary']['loss'];selected=score<best
                significant=score<best*.999
                if selected:
                    best=score;selected_epoch=epoch
                    save_torch(folder/'best.pt',dict(state=cpu_state(model),depth=depth,scale=scale,epoch=epoch))
                    save_json(folder/'best_validation.json',result)
                stale=0 if significant else stale+1
                row=dict(epoch=epoch,train_loss=loss_sum/samples,validation=result['summary'],selected=selected)
                history.append(row);save_json(folder/'history.json',history);log_event(dict(stage='RECEIVER_VALIDATION',depth=depth,**row))
                epoch+=1;cursor=0;loss_sum=0.;samples=0;checkpoint()
                if plateau_reached(epoch,stale):break
            if selected_epoch==0:
                raise RuntimeError(f'Depth {depth} did not improve its initial validation loss; later depths were not started')
            save_json(folder/'COMPLETE.json',dict(status='COMPLETE',selected_epoch=selected_epoch,steps=steps,
                reason='VALIDATION_PLATEAU' if epoch-1<maximum_epochs else 'MAXIMUM_BUDGET',best_validation_loss=best,
                checkpoint_sha256=sha(folder/'best.pt')))
        except BaseException:
            checkpoint();raise
        model.load_state_dict(torch.load(folder/'best.pt',map_location=device,weights_only=False)['state'])
    return model


def load_test_progress(path, identity, count):
    if not path.exists(): return []
    saved=json.loads(path.read_text())
    if saved.get('identity') != identity: raise ValueError(f'Test result identity changed: {path.name}')
    rows=saved['rows']
    if len(rows)>count or any(row['case_index']!=index or
            row['case_sha256']!=identity['case_hashes'][index] for index,row in enumerate(rows)):
        raise ValueError(f'Invalid test result cursor or scene binding: {path.name}')
    if saved.get('status')=='COMPLETE' and len(rows)!=count:
        raise ValueError(f'Incomplete rows marked complete: {path.name}')
    if any((row['nmse'] is not None and not math.isfinite(row['nmse'])) or
            not math.isfinite(row['total_seconds']) for row in rows):
        raise ValueError(f'Nonfinite recorded test results: {path.name}')
    return rows


def final_test(scale,device,started):
    # Test generation starts only after training and selection at every depth.
    receipt=build_cases('test',scale,started)
    count=CONFIG['receiver']['test_scenes']
    common_identity=dict(device=str(device),scale=float(scale),
        timing_runtime=dict(torch_version=torch.__version__,platform=platform.platform(),
            processor=platform.processor() or platform.machine(),
            gpu_name=torch.cuda.get_device_name(torch.device(device)) if torch.device(device).type=='cuda' else None),
        case_receipt_sha256=sha(OUT/'data'/'receiver_test.json'),
        case_hashes=[receipt['files'][case_path('test',i).name] for i in range(count)],
        source_manifest_sha256=sha(OUT/'MANIFEST.json'),
        timing_scope='Device-synchronized wall time: scene loading, preparation and inference; model loading and metric computation excluded; first case includes backend warm-up; no cache reused across methods/depths')
    for depth in range(1,CONFIG['receiver']['maximum_depth']+1):
        check_budget(started)
        checkpoint=OUT/'checkpoints'/f'depth_{depth}'/'best.pt'
        identity=dict(common_identity,method='fresh',experiment='depth_ablation',depth=depth,
            phase_mode=CONFIG['receiver']['phase_mode'],noise_mode=CONFIG['receiver']['noise_mode'],
            checkpoint_sha256=sha(checkpoint))
        path=OUT/'results'/f'test_depth_{depth}.json'
        rows=load_test_progress(path,identity,count)
        if len(rows)==count:
            saved=json.loads(path.read_text())
            if saved['status']!='COMPLETE':
                save_json(path,dict(status='COMPLETE',identity=identity,rows=rows,summary=summarize_rows(rows)))
            continue
        model=Receiver()
        for _ in range(depth): model.add_layer(None)
        model.to(device)
        model.load_state_dict(torch.load(checkpoint,map_location=device,weights_only=False)['state'])
        cases=Cases('test',scale,device)
        def persist(current):
            for index,row in enumerate(current): row['case_sha256']=identity['case_hashes'][index]
            save_json(path,dict(status='PARTIAL',identity=identity,rows=current))
        result=evaluate(model,cases,started=started,rows=rows,on_row=persist)
        save_json(path,dict(status='COMPLETE',identity=identity,**result))
        status('FINAL_TEST',depth=depth,**result['summary'])
        del model,cases
    depth=CONFIG['receiver']['maximum_depth']
    selected=json.loads((OUT/'results'/f'test_depth_{depth}.json').read_text(encoding='utf-8'))
    rows=selected['rows']
    save_json(OUT/'results'/'convergence_depth_5.json',dict(
        identity=selected['identity'],scope='Intermediate outputs of ONE selected five-layer checkpoint',
        layer_summary=[dict(layer=i+1,**summarize_rows([r['layer_metrics'][i] for r in rows]))
                       for i in range(depth)]))
    from .baseline_evaluation import evaluate_baselines
    evaluate_baselines(scale,device,started,common_identity,load_test_progress)


def lock_identity(lock=None):
    """Inspect a lock without sending signals (os.kill(pid, 0) is unsafe on Windows).

    A reused PID belonging to another command is stale. An inaccessible live
    process is conservatively unverified and must not be replaced automatically.
    """
    lock = OUT/'RUNNING.lock' if lock is None else Path(lock)
    if not lock.exists(): return dict(state='absent')
    try:
        pid = int(lock.read_text(encoding='utf-8').strip())
    except (ValueError, OSError):
        return dict(state='unverified', reason='Lock is unreadable or its PID is invalid')
    try:
        process = psutil.Process(pid)
        if not process.is_running() or process.status() == psutil.STATUS_ZOMBIE:
            return dict(state='stale', pid=pid, reason='Process has exited or is a zombie')
        command = process.cmdline()
        cwd = Path(process.cwd())
        expected = {(ROOT/'run_windows.py').resolve(), Path(__file__).resolve()}
        matches = []
        if '-m' in command and '--train' in command:
            module_index=command.index('-m')+1
            if module_index<len(command) and command[module_index]=='experiments.lstmp_candidate_20261019.train':
                matches.append('experiments.lstmp_candidate_20261019.train')
        for argument in command:
            if Path(argument).name.lower() not in ('run_windows.py', 'train.py'):
                continue
            if Path(argument).name.lower() == 'run_windows.py' and '--resume' not in command:
                continue
            candidate = Path(argument)
            if not candidate.is_absolute(): candidate = cwd/candidate
            if candidate.resolve() in expected: matches.append(str(candidate.resolve()))
        return dict(state='live' if matches else 'stale', pid=pid,
                    command=command, identity_matches=matches,
                    reason='Matching package training command' if matches else 'PID belongs to a different command')
    except (psutil.NoSuchProcess, psutil.ZombieProcess):
        return dict(state='stale', pid=pid, reason='Process no longer exists')
    except psutil.AccessDenied:
        return dict(state='unverified', pid=pid, reason='Cannot inspect live process identity')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--train',action='store_true',help='Explicitly start optimization; never implied by checks')
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--device',default=CONFIG['device'])
    args=parser.parse_args()
    if not args.train:
        parser.error('No work started. Training requires explicit --train.')
    if CONFIG['receiver']['maximum_depth'] != CONFIG['depth_extension']['target_depth']:
        raise ValueError('Depth differs from the authorized extension block')
    OUT.mkdir(parents=True,exist_ok=True)
    lock=OUT/'RUNNING.lock'
    try:
        descriptor=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:
        identity=lock_identity(lock)
        if identity['state'] in ('live','unverified'):
            raise RuntimeError(f'Run lock cannot be replaced: {identity}')
        if not args.resume:raise RuntimeError('Stale lock; explicit --resume required')
        lock.unlink(missing_ok=True)
        descriptor=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    os.write(descriptor,str(os.getpid()).encode());os.close(descriptor)
    usage_path=OUT/'ACTIVE_TIME.json'
    consumed=json.loads(usage_path.read_text(encoding='utf-8'))['consumed_seconds'] if usage_path.exists() else CONFIG.get('prior_training_seconds',0.)
    started=time.time()-consumed
    try:
        threads=CONFIG.get('cpu_threads',4)
        torch.set_num_threads(threads);threadpool_limits(threads)
        if str(args.device).startswith('cuda'):
            torch.backends.cuda.matmul.allow_tf32=CONFIG.get('allow_tf32',False)
            torch.backends.cudnn.allow_tf32=CONFIG.get('allow_tf32',False)
            torch.backends.cudnn.benchmark=True
        manifest_path=OUT/'MANIFEST.json'
        if not manifest_path.exists():
            if args.resume or (OUT/'checkpoints').exists():
                raise ValueError('Cannot resume without a matching candidate manifest')
            active_project_source=PROJECT_SOURCE/'afdm_jadcedd' if PROJECT_SOURCE.exists() else ROOT/'src/afdm_jadcedd'
            sources=[p for directory in (Path(__file__).parent,active_project_source)
                     for p in directory.rglob('*') if p.is_file() and p.suffix in ('.py','.json')]
            protected=['MAINLINE.json','configs/proposed.json','models/proposed/first.pt',
                       'models/proposed/second.pt','models/proposed/activity.pt']
            if 'pretrained_score' in CONFIG:
                protected.extend(CONFIG['protected_assets'])
                sources.append(Path(__file__).parent/'reuse_50000.json')
            save_json(manifest_path,dict(schema='afdm-lstmp-candidate-run-v2',configuration=CONFIG,
                snapshot_hashes={str(p.resolve()):sha(p) for p in sources},
                protected_assets={p:sha(ROOT/p) for p in protected}))
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest['configuration']!=CONFIG:
            raise ValueError('Candidate run configuration changed; use a new run directory')
        for path,value in manifest['snapshot_hashes'].items():
            if sha(Path(path))!=value:raise ValueError(f'Run source changed: {path}')
        if not args.resume and (OUT/'checkpoints').exists():raise RuntimeError('Existing checkpoints require --resume')
        prepare_continuation()
        device=args.device
        status('STARTING',device=device,initialization=CONFIG['initialization'])
        if 'pretrained_score' in CONFIG:
            from .reuse import prepare_initialization
            pretrained,scale=prepare_initialization()
            status('PRETRAINED_SCORE_LOADED',checkpoint=str(pretrained),scale=scale,pretraining_skipped=True)
        else:
            scale=build_prior(started)
            pretrained=pretrain(scale,device,started)
            if torch.load(pretrained,map_location='cpu',weights_only=False)['epoch']==0:
                raise RuntimeError('Score pretraining did not improve validation over random initialization; receiver training not started')
        from .extension import train_receiver as extend_receiver
        extend_receiver(pretrained,scale,device,started)
        if CONFIG.get('run_final_evaluation',True):final_test(scale,device,started)
        manifest=json.loads((OUT/'MANIFEST.json').read_text())
        preserved={path:sha(ROOT/path)==value for path,value in manifest['protected_assets'].items()}
        if not all(preserved.values()):raise RuntimeError('A protected asset changed during training')
        save_json(OUT/'COMPLETE.json',dict(status='COMPLETE',seconds=time.time()-started,protected_assets_preserved=preserved,
            held_out_test_completed=CONFIG.get('run_final_evaluation',True)))
        status('COMPLETE',elapsed_seconds=time.time()-started)
    except (InterruptedError,TimeoutError,KeyboardInterrupt) as error:
        status('TIME_BUDGET_REACHED' if isinstance(error,TimeoutError) else 'PAUSED',
               reason=str(error) or 'Keyboard interrupt; latest safe checkpoint preserved');raise
    except BaseException as error:
        save_json(OUT/'FAILURE.json',dict(error=repr(error),traceback=traceback.format_exc(),time=time.time()))
        status('FAILED',error=repr(error));raise
    finally:
        save_json(usage_path,dict(consumed_seconds=time.time()-started))
        lock.unlink(missing_ok=True)


if __name__=='__main__':main()
