"""Scene-separated data for the explicit union of the formal sweeps."""
import time, json, inspect
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
import torch
from experiments.lstmp_candidate_20261019.common import (
    CONFIG, OUT, save_json, status, real_tensor, check_budget, sha)
from experiments.lstmp_candidate_20261019.data import prepare_public
from .generation import generate_case
from afdm_jadcedd.system.pilot import PartialDFTPilot


def case_path(split, index):
    return OUT / 'data' / 'receiver' / f'{split}_{index:04d}.npz'


def case_indices(split):
    """Every independently generated scene is visited once per epoch."""
    count = CONFIG['receiver'][f'{split}_scenes']
    return list(range(count))


def case_identity(split, scale):
    settings = CONFIG['receiver']
    identity = dict(schema='receiver-explicit-conditions-v3', count=settings[f'{split}_scenes'],
                base_seed=settings[f'{split}_seed'], snr_db=settings['snr_db'],
                conditions=settings['conditions'][split],
                generator_sha256=sha(Path(inspect.getfile(generate_case))),
                scale=float(scale), phase=settings['phase_mode'], noise=settings['noise_mode'])
    return identity


def condition_for(split, index):
    # Every entry is a complete (K, Q, sampling probability, SNR) condition.
    # The explicit union must never be expanded into a Cartesian product.
    profiles = CONFIG['receiver']['conditions'][split]
    return dict(profiles[index % len(profiles)])


def validate_case(values, split, index):
    settings = CONFIG['receiver']
    condition = condition_for(split,index)
    users, frames = condition['users'], condition['frames']
    sampling_prior=condition['activity_probability']
    marginal_prior=condition.get('fixed_active_users',0)/users if 'fixed_active_users' in condition else (
        sampling_prior/(-np.expm1(users*np.log1p(-sampling_prior))))
    expected = dict(y=(frames,16,16), a=(frames,users,16), pilot=(frames,users,16),
                    x=(users,16,16,16), active=(users,),
                    noise=(), rho=(), seed=(), snr=())
    if set(values) != set(expected) or any(np.shape(values[k]) != shape for k,shape in expected.items()):
        raise ValueError(f'Invalid scene fields or shape: {split}/{index}')
    if not all(np.isfinite(v).all() for v in values.values()):
        raise FloatingPointError(f'Nonfinite scene: {split}/{index}; no sample discarded')
    if (int(values['seed']) != settings[f'{split}_seed']+index or
            float(values['snr']) != condition['snr_db'] or
            float(values['noise']) <= 0 or not 0 < float(values['rho']) < 1 or
            not np.isclose(float(values['rho']),marginal_prior,rtol=1e-12,atol=1e-14) or
            not np.isin(values['active'],[0,1]).all() or not np.any(values['active'])):
        raise ValueError(f'Scene identity or physical metadata changed: {split}/{index}')


def generate_arrays(split, index, scale):
    settings = CONFIG['receiver']
    seed = settings[f'{split}_seed']+index
    condition = condition_for(split,index)
    snr = condition.pop('snr_db')
    inp, truth, _ = generate_case(seed, snr, scale, **condition)
    pilot = PartialDFTPilot(condition['users'],condition['frames'],seed+10**12,
                            input_size=16).dense().reshape(condition['frames'],condition['users'],16)
    arrays = dict(y=inp['observation'], a=inp['operator'], noise=inp['noise_variance'],
                  pilot=pilot, rho=inp['activity_prior'], x=truth['channel'],
                  active=truth['activity'], seed=seed, snr=snr)
    validate_case(arrays,split,index)
    return arrays


def _generation_worker_init():
    from threadpoolctl import threadpool_limits
    torch.set_num_threads(1)
    threadpool_limits(1)


def _write_case(job):
    split,index,scale = job
    expected = generate_arrays(split,index,scale)
    path = case_path(split,index)
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        with np.load(path) as z: actual = dict(z)
        validate_case(actual,split,index)
        if any(not np.array_equal(actual[k],expected[k]) for k in expected):
            raise ValueError(f'Unrecorded scene differs from deterministic regeneration: {path.name}')
    else:
        temp = path.with_suffix('.tmp.npz'); np.savez_compressed(temp,**expected); temp.replace(path)
    return index,path.name,sha(path)


def build_cases(split, scale, start):
    identity = case_identity(split,scale)
    receipt_path = OUT/'data'/f'receiver_{split}.json'
    receipt = dict(identity=identity,files={})
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        if receipt.get('identity') != identity: raise ValueError(f'Scene receipt identity changed: {split}')
    expected_names = {case_path(split,i).name for i in range(identity['count'])}
    if set(receipt['files'])-expected_names: raise ValueError(f'Unexpected scene receipt entries: {split}')
    pending=[]
    for index in range(identity['count']):
        check_budget(start)
        path = case_path(split,index)
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.name in receipt['files']:
            if not path.exists() or sha(path) != receipt['files'][path.name]:
                raise ValueError(f'Recorded scene missing or changed: {path.name}')
            with np.load(path) as z: validate_case(dict(z),split,index)
            continue
        pending.append((split,index,scale))
    workers=CONFIG['receiver'].get('generation_workers',1)
    pool=ProcessPoolExecutor(max_workers=workers,initializer=_generation_worker_init) if workers>1 and pending else None
    try:
        results=pool.map(_write_case,pending,chunksize=4) if pool else map(_write_case,pending)
        for index,name,digest in results:
            receipt['files'][name]=digest
            count=len(receipt['files'])
            if count%32==0 or count==identity['count']:
                save_json(receipt_path,receipt)
                status('GENERATING_RECEIVER_DATA',split=split,scenes=count,total=identity['count'],workers=workers)
            check_budget(start)
    finally:
        save_json(receipt_path,receipt)
        if pool:pool.shutdown(wait=True,cancel_futures=True)
    return receipt


class Cases:
    def __init__(self, split, scale, device):
        self.split, self.scale, self.device = split, scale, device
        self.cache = {}
        self.indices = case_indices(split)
        self.receipt = json.loads((OUT/'data'/f'receiver_{split}.json').read_text())
        if self.receipt.get('identity') != case_identity(split,scale):
            raise ValueError(f'Scene receipt identity changed: {split}')

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, index):
        index = self.indices[index]
        # Small CPU cache; don't retain all scenes or labels on the GPU.
        if index not in self.cache:
            path = case_path(self.split,index)
            if sha(path) != self.receipt['files'].get(path.name):
                raise ValueError(f'Scene changed after receipt verification: {path.name}')
            with np.load(path) as z: values = dict(z)
            validate_case(values,self.split,index)
            public, frontend = prepare_public(values,self.scale,'cpu',
                phase_mode=CONFIG['receiver']['phase_mode'],noise_mode=CONFIG['receiver']['noise_mode'])
            labels = dict(x=real_tensor(values['x']/self.scale,'cpu'),
                active=torch.tensor(values['active'],dtype=torch.float32),physical_scale=self.scale)
            info = dict(seed=int(values['seed']),snr=float(values['snr']),
                source_pool_index=index,
                users=len(values['active']),frames=len(values['y']),
                condition=condition_for(self.split,index),frontend=frontend)
            self.cache[index] = public,labels,info
            if len(self.cache)>CONFIG['receiver'].get('cpu_cache_scenes',16):
                self.cache.pop(next(iter(self.cache)))
        public,labels,info=self.cache[index]
        move=lambda values:{k:v.to(self.device) if isinstance(v,torch.Tensor) else v for k,v in values.items()}
        return move(public),move(labels),info



def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate', action='store_true', required=True)
    parser.parse_args()
    if (OUT / 'TRAINING_LAUNCH.json').exists():
        raise RuntimeError('Dataset generation is closed after training starts')
    started = time.time()
    scale = CONFIG['pretrained_score']['global_complex_rms']
    for split in ('train', 'validation'):
        build_cases(split, scale, started)
    status('DATA_GENERATED_PENDING_FREEZE', elapsed_seconds=time.time() - started)


if __name__ == '__main__':
    main()
