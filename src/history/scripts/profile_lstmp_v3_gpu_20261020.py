"""Profile disposable updates from the paused run; never save trained weights."""
import json
import time

import numpy as np
import torch

import check_lstmp_training_v3_implementation_20261020 as check


def main():
    target = check.TARGET
    assert check.read(target / 'STATUS.json')['stage'] == 'PAUSED'
    assert not (target / 'RUNNING.lock').exists()
    folder = check.ROOT / 'results/lstmp_v3_gpu_optimization_20261020'
    folder.mkdir(exist_ok=True)
    torch.set_num_threads(4)
    check.threadpool_limits(4)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = True
    statistics = check.read(target / 'protocol/TRAINING_STATISTICS.json')
    path = target / 'checkpoints/depth_1/last.pt'
    digest = check.sha(path)
    saved = torch.load(path, map_location='cpu', weights_only=False, mmap=True)
    model = check.Receiver()
    for _ in range(saved['depth']):
        model.add_layer(None)
    model.load_state_dict(saved['state'])
    model.cuda().train()
    eligible = set(saved['eligible'])
    optimizer = check.make_optimizer(model, check.common.CONFIG['receiver'], eligible, fused=True)
    optimizer.load_state_dict(saved['optimizer'])
    check.configure_execution(model, optimizer, check.common.CONFIG['execution'], 'cuda')
    check.set_phase(model, optimizer, eligible, saved['epoch'])
    cases = check.data.Cases('train', check.common.CONFIG['pretrained_score']['global_complex_rms'], 'cuda')
    positions = saved['order'][saved['cursor']:saved['cursor'] + 32].tolist()
    assert len(positions) == 32
    rows = []

    def step(position):
        torch.cuda.synchronize()
        before = time.perf_counter()
        with torch.profiler.record_function('scene_prepare_and_copy'):
            public, labels, info = cases[position]
        torch.cuda.synchronize()
        ready = time.perf_counter()
        optimizer.zero_grad(set_to_none=True)
        with torch.profiler.record_function('receiver_forward_loss'):
            outputs, diagnostics = model(public)
            components = check.loss_components(outputs, labels, statistics)
            assert bool(torch.isfinite(components['total']))
        with torch.profiler.record_function('receiver_backward'):
            check.assign_gradients(model, components)
        with torch.profiler.record_function('gradient_clip'):
            norm = float(check.clip_gradient_norm(model.parameters(), 1.))
        with torch.profiler.record_function('adam_update'):
            optimizer.step()
        losses = [float(components[k].detach()) for k in ('total', 'channel', 'activity')]
        torch.cuda.synchronize()
        done = time.perf_counter()
        return dict(position=int(position), users=info['users'], frames=info['frames'],
                    data_seconds=ready-before, update_seconds=done-ready,
                    total_seconds=done-before, loss=losses[0], gradient_norm=norm)

    for position in positions[:8]:
        step(position)
    for position in positions[8:]:
        rows.append(step(position))
    check.write(folder / 'BASELINE_TIMING.json', dict(
        source=str(path), source_sha256=digest, depth=saved['depth'], epoch=saved['epoch'],
        cursor=saved['cursor'], updates_discarded=True, positions=positions, rows=rows,
        mean_data_seconds=float(np.mean([r['data_seconds'] for r in rows])),
        mean_update_seconds=float(np.mean([r['update_seconds'] for r in rows])),
        mean_total_seconds=float(np.mean([r['total_seconds'] for r in rows]))))
    with torch.profiler.profile(activities=[
            torch.profiler.ProfilerActivity.CPU, torch.profiler.ProfilerActivity.CUDA]) as prof:
        step(positions[-1])
    (folder / 'PROFILE_CPU.txt').write_text(
        prof.key_averages().table(sort_by='self_cpu_time_total', row_limit=35), encoding='utf-8')
    (folder / 'PROFILE_CUDA.txt').write_text(
        prof.key_averages().table(sort_by='self_cuda_time_total', row_limit=25), encoding='utf-8')
    assert check.sha(path) == digest
    summary = check.read(folder / 'BASELINE_TIMING.json')
    print(json.dumps({k: v for k, v in summary.items() if k not in ('rows', 'positions')}), flush=True)
    print((folder / 'PROFILE_CPU.txt').read_text(encoding='utf-8'), flush=True)


if __name__ == '__main__':
    main()
