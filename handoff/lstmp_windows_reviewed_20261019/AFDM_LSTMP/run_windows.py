"""Portable handoff entry point. --check never resumes or saves trained weights.

Examples: python run_windows.py --check --device cuda
          python run_windows.py --resume --device cuda
          python run_windows.py --pause
          python run_windows.py --status
"""
import argparse
import contextlib
import gc
import hashlib
import json
import importlib.metadata
import os
from pathlib import Path
import platform
import signal
import sys
import time
import traceback

# Archived project helpers use Path.read_text() without an explicit encoding.
# Their immutable JSON contains Unicode; select UTF-8 before importing helpers.
# Re-exec only on Windows, before any lock, metadata, or training operation.
if os.name == 'nt' and not sys.flags.utf8_mode:
    os.execv(sys.executable, [sys.executable, '-X', 'utf8', str(Path(__file__).resolve()), *sys.argv[1:]])

ROOT = Path(__file__).resolve().parent
RUN = ROOT/'runs'/'lstmp_fresh_20261019'
SOURCE = RUN/'source_experiment'
os.environ['AFDM_LSTMP_ROOT'] = str(ROOT)
sys.path.insert(0, str(SOURCE))


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as file:
        for chunk in iter(lambda: file.read(2**20), b''): result.update(chunk)
    return result.hexdigest()


def write_json(path, value):
    path = Path(path)
    temp = path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')
    temp.replace(path)


def verify_files():
    manifest = json.loads((RUN/'MANIFEST.json').read_text(encoding='utf-8'))
    checked = {}
    for prefix, base, mapping in (
            ('snapshot', RUN, manifest['snapshot_hashes']),
            ('protected', ROOT, manifest['protected_assets']),
            ('package', ROOT, manifest.get('fixed_package_assets', {}))):
        for relative, expected in mapping.items():
            actual = digest(base/relative)
            if actual != expected: raise ValueError(f'Hash mismatch: {prefix}/{relative}')
            checked[f'{prefix}/{relative}'] = actual
    for relative, expected in manifest.get('fixed_data_metadata', {}).items():
        actual = digest(RUN/relative)
        if actual != expected: raise ValueError(f'Fixed data metadata changed: {relative}')
        checked[f'fixed_data_metadata/{relative}'] = actual
    for split in ('train', 'validation'):
        receipt = json.loads((RUN/'data'/f'prior_{split}.json').read_text(encoding='utf-8'))
        actual = digest(RUN/'data'/f'prior_{split}.npy')
        if actual != receipt['sha256']: raise ValueError(f'Prior data changed: {split}')
        checked[f'prior/{split}'] = actual
    return checked


def checkpoint_hashes():
    return {str(path.relative_to(RUN)): digest(path) for path in sorted((RUN/'checkpoints').rglob('*.pt'))}


def runtime(device, action):
    import torch
    if device == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('CUDA is unavailable. Install a CUDA-capable PyTorch build or explicitly use --device cpu.')
    torch.set_num_threads(1)
    from threadpoolctl import threadpool_limits
    threadpool_limits(1)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.set_float32_matmul_precision('highest')
    from common import CONFIG
    configured_device = CONFIG['device']
    CONFIG['device'] = device  # Runtime override only; immutable config.json stays unchanged.
    row = dict(action=action, device=device, configured_device=configured_device,
               time=time.time(), pid=os.getpid(), platform=platform.platform(), python=sys.version,
               torch_version=torch.__version__, cuda_build=torch.version.cuda,
               cuda_available=torch.cuda.is_available(), tf32=False, precision='float32',
               package_root=str(ROOT), config_sha256=digest(SOURCE/'config.json'),
               cuda_requested=device == 'cuda',
               dependencies={name: importlib.metadata.version(name) for name in
                             ('numpy','scipy','threadpoolctl','PyYAML','matplotlib','psutil')})
    if device == 'cuda': row['gpu_name'] = torch.cuda.get_device_name(0)
    write_json(RUN/'RUNTIME.json', row)
    with (RUN/'runtime_history.jsonl').open('a', encoding='utf-8') as file:
        file.write(json.dumps(row, ensure_ascii=False)+'\n')
    return row


def finite_gradients(module):
    import torch
    gradients = [p.grad for p in module.parameters() if p.grad is not None]
    if not gradients or not all(bool(torch.isfinite(g).all()) for g in gradients):
        raise FloatingPointError('Missing or nonfinite gradients')
    norm = float(sum(g.detach().square().sum() for g in gradients).sqrt())
    if not norm > 0: raise AssertionError('All parameter gradients are zero')
    return norm


def perform_check(device, report):
    import numpy as np
    import torch
    from common import CONFIG, real_tensor
    from backbone import FreshScore
    from train import score_batch
    before = checkpoint_hashes()
    scale = json.loads((RUN/'data'/'normalization.json').read_text(encoding='utf-8'))['scale']
    saved = torch.load(RUN/'checkpoints'/'pretrain'/'last.pt', map_location='cpu', weights_only=False)
    report['resume_position'] = {key: saved[key] for key in ('epoch', 'steps', 'cursor')}
    torch.manual_seed(CONFIG['seed']+81000000)
    model = FreshScore(CONFIG['width']).to(device)
    ema = FreshScore(CONFIG['width']).to(device).eval().requires_grad_(False)
    model.load_state_dict(saved['model']); ema.load_state_dict(saved['ema'])
    optimizer = torch.optim.Adam(model.parameters(), lr=CONFIG['pretraining']['learning_rate'])
    optimizer.load_state_dict(saved['optimizer'])
    bank = np.load(RUN/'data'/'prior_train.npy', mmap_mode='r')
    r, v, epsilon, _ = score_batch(bank, np.arange(4), scale, device, CONFIG['seed']+82000000)
    value = (torch.sqrt(v/2)[:,None,None,None,None]*model(r,v)+epsilon).square().mean()
    if not bool(torch.isfinite(value)): raise FloatingPointError('Nonfinite resumed DSM loss')
    value.backward()
    gradient_norm = finite_gradients(model)
    torch.nn.utils.clip_grad_norm_(model.parameters(), CONFIG['pretraining']['gradient_clip'], error_if_nonfinite=True)
    chosen = next(p for p in model.parameters() if p.requires_grad and p.grad is not None and bool((p.grad != 0).any()))
    previous = chosen.detach().clone()
    optimizer.step()  # In-memory compatibility check; never checkpointed.
    update = float((chosen.detach()-previous).abs().max())
    if update == 0 or not all(bool(torch.isfinite(p).all()) for p in model.parameters()):
        raise FloatingPointError('Optimizer restore produced no finite parameter update')
    with torch.no_grad():
        if not bool(torch.isfinite(ema(r,v)).all()): raise FloatingPointError('Nonfinite EMA output')
    report['dsm'] = dict(loss=float(value.detach()), gradient_norm=gradient_norm,
                         optimizer_parameter_max_update=update, ema_finite=True, optimizer_step_saved=False)
    del model, ema, optimizer, bank, r, v, epsilon, value, chosen, previous
    gc.collect()
    if device == 'cuda': torch.cuda.empty_cache()

    from receiver import Receiver, loss
    from data import block
    from afdm_jadcedd.experiment.generate import generate_case
    debug_seed = CONFIG['seed']+83000000
    inputs, truth, _ = generate_case(debug_seed, 0., scale)
    a = inputs['operator'].reshape(16,640)
    u, s, vh = np.linalg.svd(a, full_matrices=False)
    y = inputs['observation'].reshape(16,256)/scale
    public = dict(a=block(a,device), uh=block(u.conj().T,device), vv=block(vh.conj().T,device),
                  s=torch.tensor(s,dtype=torch.float32,device=device),
                  y=torch.tensor(np.concatenate((y.real,y.imag)),dtype=torch.float32,device=device),
                  noise=float(inputs['noise_variance'])/scale**2, rho=float(inputs['activity_prior']))
    labels = dict(x=real_tensor(truth['channel']/scale,device),
                  active=torch.tensor(truth['activity'],dtype=torch.float32,device=device))
    receiver = Receiver()
    for _ in range(CONFIG['receiver']['maximum_depth']): receiver.add_layer(saved['ema'])
    receiver.to(device).train()
    if device == 'cuda':
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
    calibration = [layer.calibration for layer in receiver.layers]
    networks = [p for name,p in receiver.named_parameters() if not name.endswith('calibration') and p.requires_grad]
    optimizer = torch.optim.Adam([
        dict(params=networks,lr=CONFIG['receiver']['learning_rate']),
        dict(params=calibration,lr=CONFIG['receiver']['calibration_learning_rate'])])
    pointers = [set(p.data_ptr() for p in layer.parameters()) for layer in receiver.layers]
    if any(pointers[i]&pointers[j] for i in range(len(pointers)) for j in range(i)):
        raise AssertionError('Unfolded layers unexpectedly share parameter storage')
    started = time.monotonic()
    outputs, diagnostics = receiver(public)
    objective = loss(outputs,labels)
    if not bool(torch.isfinite(objective)): raise FloatingPointError('Nonfinite physical receiver loss')
    objective.backward()
    gradients = {f'layer_{i+1}_{name}': finite_gradients(module)
                 for i, layer in enumerate(receiver.layers)
                 for name, module in (('score', layer.score), ('activity', layer.activity))}
    if not all(0 < d['feedback_variance'] < d['query_variance'] for d in diagnostics):
        raise AssertionError('Invalid feedback precision in physical check')
    torch.nn.utils.clip_grad_norm_(receiver.parameters(),1.,error_if_nonfinite=True)
    optimizer.step()  # Allocate actual Adam states; never persist these debug weights.
    if not all(bool(torch.isfinite(p).all()) for p in receiver.parameters()):
        raise FloatingPointError('Nonfinite five-layer optimizer update')
    if device == 'cuda': torch.cuda.synchronize()
    report['physical_receiver'] = dict(depth=len(receiver.layers), debug_seed=debug_seed,
        optimizer_step_saved=False, adam_state_parameters=len(optimizer.state),
        peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated() if device == 'cuda' else None,
        loss=float(objective.detach()), gradient_norms=gradients, diagnostics=diagnostics,
        independent_layers=True, seconds=time.monotonic()-started,
        scope='One diagnostic scene outside every training/validation/test interval; no scene file saved')
    del receiver, saved, outputs, objective, public, labels, optimizer, networks, calibration
    gc.collect()
    if device == 'cuda': torch.cuda.empty_cache()

    from afdm_jadcedd.algorithm.proposed.configuration import verify
    baseline = json.loads((ROOT/'configs'/'proposed.json').read_text(encoding='utf-8'))
    report['original_receiver_assets'] = verify(baseline)
    if checkpoint_hashes() != before: raise AssertionError('Check modified a checkpoint')
    report['immutable_files_verified_after'] = len(verify_files())
    report['checkpoints_unchanged'] = before
    report['status'] = 'PASS'
    report['actual_cuda_test'] = device == 'cuda'


class Tee:
    def __init__(self, console, file): self.console, self.file = console, file
    def write(self, text):
        self.console.write(text); self.file.write(text); self.flush()
        return len(text)
    def flush(self): self.console.flush(); self.file.flush()
    def isatty(self): return False


def resume(device):
    import train
    identity = train.lock_identity()
    if identity['state'] in ('live','unverified'):
        raise RuntimeError(f'Cannot resume while another run may be active: {identity}')
    verify_files()
    runtime(device,'resume')
    # Only this explicit action clears the user-requested pause marker.
    (RUN/'pause.request').unlink(missing_ok=True)
    interrupts = 0
    def pause_on_interrupt(signum, frame):
        nonlocal interrupts
        interrupts += 1
        (RUN/'pause.request').write_text('Requested by keyboard interrupt\n',encoding='utf-8')
        if interrupts > 1: raise KeyboardInterrupt
        print('Pause requested. Finishing the current step and saving its checkpoint...',flush=True)
    previous = signal.signal(signal.SIGINT,pause_on_interrupt)
    previous_break = signal.signal(signal.SIGBREAK,pause_on_interrupt) if hasattr(signal,'SIGBREAK') else None
    old_argv = sys.argv
    try:
        with (RUN/'run.log').open('a',encoding='utf-8',buffering=1) as file:
            with contextlib.redirect_stdout(Tee(sys.stdout,file)), contextlib.redirect_stderr(Tee(sys.stderr,file)):
                print(f'Portable resume: device={device}, time={time.time()}',flush=True)
                sys.argv = [str(SOURCE/'train.py'),'--resume']
                try: train.main()
                except (InterruptedError,KeyboardInterrupt):
                    print('Training paused; the latest safe checkpoint is preserved.',flush=True)
    finally:
        sys.argv = old_argv
        signal.signal(signal.SIGINT,previous)
        if previous_break is not None: signal.signal(signal.SIGBREAK,previous_break)


def main():
    parser = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    action = parser.add_mutually_exclusive_group(required=True)
    for name in ('check','resume','pause','status'): action.add_argument('--'+name,action='store_true')
    parser.add_argument('--device',choices=('cuda','cpu'),default='cuda')
    args = parser.parse_args()
    if args.pause:
        (RUN/'pause.request').write_text('User requested pause via run_windows.py\n',encoding='utf-8')
        print('Pause requested. An active trainer will checkpoint and stop at the next safe boundary.')
        return 0
    if args.status:
        import train
        state = json.loads((RUN/'STATUS.json').read_text(encoding='utf-8')) if (RUN/'STATUS.json').exists() else {}
        print(json.dumps(dict(status=state,lock=train.lock_identity(),pause_requested=(RUN/'pause.request').exists()),indent=2,ensure_ascii=False))
        return 0
    if args.resume:
        resume(args.device)
        return 0
    report = dict(status='STARTED',device=args.device,time=time.time(),actual_cuda_test=False)
    try:
        import train
        identity = train.lock_identity()
        if identity['state'] in ('live','unverified'):
            raise RuntimeError(f'Check requires an idle run: {identity}')
        report['immutable_files_verified_before'] = len(verify_files())
        report['runtime'] = runtime(args.device,'check')
        perform_check(args.device,report)
    except BaseException as error:
        report.update(status='FAIL',error=repr(error),traceback=traceback.format_exc())
        write_json(RUN/f'check_{args.device}.json',report)
        raise
    write_json(RUN/f'check_{args.device}.json',report)
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
