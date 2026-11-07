"""Original full-channel Cai DSM and global-trace second-score training.

This entry point creates a separate training run. It does not update the
selected receiver checkpoints. Data paths may be relocated with --data-dir.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import signal
import time
import numpy as np
import torch
from threadpoolctl import threadpool_limits
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.utils import sha256, write_json
from .original_training.trainer import ScoreTrainer
from .original_training.direct_objectives import direct_first_loss, direct_second_loss
from .original_training.score_matching import make_cai_batch

DEFAULT_CONFIG = ROOT/'configs/training.json'


def loss_check():
    """Check both score losses against equivalent posterior-moment formulas."""
    rng = np.random.default_rng(202610020021)
    shape = (2, 2, 3, 4)
    channels = (rng.standard_normal(shape)+1j*rng.standard_normal(shape)).astype(np.complex64)
    clean, noisy, variance, labels = make_cai_batch(channels, rng, .2647966452702405)
    h, r, nu = (torch.as_tensor(value, dtype=torch.float64) for value in (clean, noisy, variance))
    s1 = torch.as_tensor(rng.standard_normal(clean.shape), dtype=torch.float64)
    s2 = torch.as_tensor(rng.standard_normal(clean.shape), dtype=torch.float64)
    v = nu[:, None]/2
    first = direct_first_loss(s1, r, h, nu)
    second = direct_second_loss(s2, s1, r, h, nu)
    mean = r+v*s1
    reported = v+v.square()*s2
    first_reference = ((mean-h).square()/v).mean()
    second_reference = ((reported-(mean-h).square())/v).flatten(1).mean(1).square().mean()
    torch.testing.assert_close(first, first_reference, rtol=1e-12, atol=1e-12)
    torch.testing.assert_close(second, second_reference, rtol=1e-12, atol=1e-12)
    if not bool(torch.isfinite(first) & torch.isfinite(second)):
        raise FloatingPointError('nonfinite synthetic score losses')
    return dict(status='PASS', first_loss=float(first), second_loss=float(second),
                real_coordinate_noise_variance='complex variance / 2',
                network_forward_calls=0, optimizer_updates=0, selected_weights_loaded=False)


def load_recipe(path, data_dir=None, device=None):
    cfg = json.loads(Path(path).read_text())
    if cfg.get('version') != 'original_full_score_training_v1':
        raise ValueError('original full-score recipe required')
    cfg = deepcopy(cfg)
    if data_dir:
        for split in ('train', 'validation'):
            cfg['training']['data_files'][split] = str(Path(data_dir).resolve()/f'{split}_channel.npy')
    if device:
        cfg['runtime']['device'] = device
    if cfg['scores']['normalization'] != 'population_rms':
        raise ValueError('training population RMS must be preserved')
    if (cfg['training']['first_objective'] != 'direct_cai_dsm'
            or cfg['training']['second_objective'] != 'direct_cai_global_trace'
            or cfg['training']['architecture']['noise_conditioning'] != 'continuous'):
        raise ValueError('original two-score objectives and continuous noise required')
    return cfg


def load_data(cfg):
    data = {}
    for split in ('train', 'validation'):
        path = Path(cfg['training']['data_files'][split])
        registered = cfg['datasets'][split]
        if sha256(path) != registered['sha256']:
            raise ValueError(f'original {split} full-channel dataset changed')
        array = np.load(path, mmap_mode='r', allow_pickle=False)
        if list(array.shape) != registered['shape'] or str(array.dtype) != registered['dtype']:
            raise ValueError(f'original {split} shape or dtype changed')
        data[split] = array
    return data


def source_records():
    package = Path(__file__).parent/'original_training'
    paths = [Path(__file__).resolve(), ROOT/'scripts/train_scores.py']
    paths += sorted(package.glob('*.py'))+[package/'PROVENANCE.json']
    model = ROOT/'src/afdm_jadcedd/algorithm/mainline'
    paths += [model/'__init__.py', model/'network.py']
    paths += sorted((model/'cai_models').rglob('*.py'))
    return {str(path.relative_to(ROOT)): sha256(path) for path in paths}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    parser.add_argument('--output', type=Path, help='Required new training directory; existing paths are refused.')
    parser.add_argument('--data-dir', type=Path, help='Relocated directory with original train_channel.npy and validation_channel.npy.')
    parser.add_argument('--device', choices=('cpu', 'mps'))
    parser.add_argument('--inspect', action='store_true', help='Read the recipe without loading weights, data, or training.')
    parser.add_argument('--check-losses', action='store_true', help='Run a tiny synthetic loss identity check without training.')
    args = parser.parse_args(argv)
    if args.check_losses:
        print(json.dumps(loss_check(), ensure_ascii=False, indent=2))
        return 0
    cfg = load_recipe(args.config, args.data_dir, args.device)
    if args.inspect:
        print(json.dumps(dict(configuration=str(args.config), training=cfg['training'],
            global_complex_rms=cfg['scores']['global_complex_rms'],
            runtime=cfg['runtime'], selected_weights_updated=False), ensure_ascii=False, indent=2))
        return 0
    if args.output is None:
        parser.error('--output is required for training')
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f'new output directory required: {output}')
    selected = [ROOT/path for path in cfg['provenance']['selected_checkpoint_paths'].values()]
    if any(output == path or output in path.parents or path.parent in output.parents for path in selected):
        raise ValueError('training output must be separate from the selected receiver checkpoint directory')
    device = cfg['runtime']['device']
    if device == 'mps' and not torch.backends.mps.is_available():
        raise RuntimeError('MPS unavailable; select --device cpu')
    data = load_data(cfg)
    output.mkdir(parents=True, exist_ok=False)
    specification = dict(configuration=cfg, configuration_sha256=sha256(args.config),
        datasets={split: dict(path=cfg['training']['data_files'][split],
            sha256=cfg['datasets'][split]['sha256']) for split in ('train', 'validation')},
        sources=source_records(), created_unix=time.time(),
        reproduction_scope=cfg['provenance']['reproduction_scope'],
        selected_receiver_weights_updated=False)
    write_json(output/'training_specification.json', specification)
    trainer = ScoreTrainer(output, device=device)
    signal.signal(signal.SIGINT, trainer.request_stop)
    signal.signal(signal.SIGTERM, trainer.request_stop)
    torch.set_num_threads(cfg['runtime']['threads'])
    with threadpool_limits(limits=cfg['runtime']['threads']):
        for stage in ('first', 'second'):
            if not trainer.train_stage(stage, cfg, data, sha256(output/'training_specification.json')):
                return 0
    trainer.status('TRAINING_COMPLETED', selected_receiver_weights_updated=False,
                   receiver_evaluation_completed=False)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
