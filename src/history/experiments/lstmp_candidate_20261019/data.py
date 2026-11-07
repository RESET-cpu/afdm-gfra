"""New scene-separated physical data. Labels never enter receiver.forward."""
import time, json
import inspect
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
import torch
from .common import CONFIG, OUT, save_json, status, real_tensor, check_budget, sha
from afdm_jadcedd.system.scenario.geometry_consistent import draw_scene
from afdm_jadcedd.system.scenario.continuous import user_channel
from afdm_jadcedd.experiment.generate import generate_case
from afdm_jadcedd.system.pilot import PartialDFTPilot


def build_prior(start):
    folder = OUT / 'data'; folder.mkdir(parents=True, exist_ok=True)
    settings = CONFIG['prior']
    for split in ('train', 'validation'):
        count, base = settings[f'{split}_samples'], settings[f'{split}_seed']
        path, receipt = folder / f'prior_{split}.npy', folder / f'prior_{split}.json'
        check_budget(start)
        if receipt.exists():
            saved = json.loads(receipt.read_text())
            if (saved['samples'] != count or saved['seed_base'] != base or
                    saved['candidates_per_scene'] != settings['candidates_per_scene'] or saved['sha256'] != sha(path)):
                raise ValueError(f'Prior receipt or data changed: {split}')
            continue
        cursor_path = folder / f'prior_{split}_cursor.json'
        cursor = 0
        if path.exists():
            cursor = json.loads(cursor_path.read_text())['samples'] if cursor_path.exists() else 0
            bank = np.lib.format.open_memmap(path, mode='r+')
            assert bank.shape == (count, 16, 16, 16)
        else:
            bank = np.lib.format.open_memmap(path, mode='w+', dtype=np.complex64, shape=(count, 16, 16, 16))
        per_scene = settings['candidates_per_scene']
        for index in range(cursor // per_scene, (count + per_scene - 1) // per_scene):
            check_budget(start)
            seed = base + index
            scene, _ = draw_scene(seed, n_users=CONFIG['users'], spread_range_s=(30e-9, 50e-9))
            users = np.random.default_rng(np.random.SeedSequence([seed, 81])).choice(CONFIG['users'], per_scene, replace=False)
            for j, user in enumerate(users):
                position = index * per_scene + j
                if position >= count: break
                h = user_channel(scene.paths_of(int(user)))
                if not np.isfinite(h).all(): raise FloatingPointError(f'Nonfinite channel {seed}/{user}; no sample discarded')
                bank[position] = h
            if index % 32 == 0 or position + 1 == count:
                bank.flush()
                save_json(cursor_path, dict(samples=position + 1))
                status('GENERATING_PRIOR', split=split, samples=position + 1, total=count)
        bank.flush()
        power = float(np.mean(np.abs(bank.astype(np.complex128))**2))
        save_json(receipt, dict(samples=count, seed_base=base, scenes=(count+per_scene-1)//per_scene,
                               candidates_per_scene=per_scene, selection='uniform before activity masking',
                               physical_mean_element_power=power, sha256=sha(path)))
        del bank
    power = json.loads((folder/'prior_train.json').read_text())['physical_mean_element_power']
    scale = float(np.sqrt(power))
    normalization = dict(scale=scale, source='training bank only', per_sample=False)
    if (folder/'normalization.json').exists():
        if json.loads((folder/'normalization.json').read_text()) != normalization:
            raise ValueError('Training normalization changed')
    else:
        save_json(folder/'normalization.json', normalization)
    return scale


def pack(x):
    users, components, antennas, samples, inputs = x.shape
    if components != 2:
        raise ValueError('Expected real/imaginary channel components')
    return x.permute(1, 0, 4, 2, 3).reshape(2*users*inputs, antennas*samples)


def unpack(x, shape):
    users, components, antennas, samples, inputs = shape
    if components != 2 or x.shape != (2*users*inputs, antennas*samples):
        raise ValueError('Packed channel and requested dimensions disagree')
    return x.reshape(2, users, inputs, antennas, samples).permute(1, 0, 3, 4, 2)


def block(a, device):
    return torch.tensor(np.block([[a.real, -a.imag], [a.imag, a.real]]), dtype=torch.float32, device=device)


def case_path(split, index):
    source = CONFIG['receiver'].get('case_sources', {}).get(split)
    root = Path(source['run_directory']) if source else OUT
    return root / 'data' / 'receiver' / f'{split}_{index:04d}.npz'


def case_indices(split):
    """Dataset positions map to unchanged scene indices in a read-only pool."""
    count = CONFIG['receiver'][f'{split}_scenes']
    source = CONFIG['receiver'].get('case_sources', {}).get(split)
    indices = list(source['indices']) if source else list(range(count))
    limit = source['pool_count'] if source else count
    if (len(indices) != count or len(set(indices)) != count or
            any(type(i) is not int or not 0 <= i < limit for i in indices)):
        raise ValueError(f'Invalid fixed scene selection: {split}')
    return indices


def case_identity(split, scale):
    settings = CONFIG['receiver']
    identity = dict(schema='receiver-cases-v3', count=settings[f'{split}_scenes'],
                base_seed=settings[f'{split}_seed'], snr_db=settings['snr_db'],
                conditions=settings['conditions'][split],
                generator_sha256=sha(Path(inspect.getfile(generate_case))),
                scale=float(scale), phase=settings['phase_mode'], noise=settings['noise_mode'])
    source = settings.get('case_sources', {}).get(split)
    if source:
        identity['read_only_source'] = source
    return identity


def condition_for(split, index):
    settings = CONFIG['receiver']
    profiles = settings['conditions'][split]
    snrs = settings['snr_db']
    # Cycle through the Cartesian product, avoiding correlated K/Q/SNR schedules.
    return dict(profiles[(index//len(snrs)) % len(profiles)], snr_db=snrs[index % len(snrs)])


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
    source = CONFIG['receiver'].get('case_sources', {}).get(split)
    if source:
        source_receipt = Path(source['run_directory'])/'data'/f'receiver_{split}.json'
        if sha(source_receipt) != source['receipt_sha256']:
            raise ValueError(f'Source scene receipt changed: {split}')
        original = json.loads(source_receipt.read_text(encoding='utf-8'))
        expected = {k:v for k,v in identity.items() if k != 'read_only_source'}
        expected['count'] = source['pool_count']
        if original['identity'] != expected:
            raise ValueError(f'Source scene generation settings differ: {split}')
        indices = case_indices(split)
        receipt = dict(identity=identity,files={})
        for position,index in enumerate(indices,1):
            check_budget(start)
            path = case_path(split,index)
            digest = original['files'].get(path.name)
            if digest is None or sha(path) != digest:
                raise ValueError(f'Selected source scene changed: {path.name}')
            with np.load(path) as z: validate_case(dict(z),split,index)
            receipt['files'][path.name] = digest
            if position % 256 == 0 or position == len(indices):
                status('VERIFYING_FIXED_SCENES',split=split,scenes=position,total=len(indices))
        if receipt_path.exists() and json.loads(receipt_path.read_text(encoding='utf-8')) != receipt:
            raise ValueError(f'Fixed selection receipt changed: {split}')
        save_json(receipt_path,receipt)
        return receipt
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


def prepare_public(values, scale, device, *, phase_mode, noise_mode):
    """Select public fields before frontend work. Truth arrays are never read here."""
    from afdm_jadcedd.algorithm.baselines.noise_estimation import estimate_spatial_noise
    from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput
    from afdm_jadcedd.system.observation import ReceiverInput,array_sha256
    from afdm_jadcedd.algorithm import phase_estimation_optimized as phase
    y, rho = np.asarray(values['y']),float(values['rho'])
    record = dict(phase_mode=phase_mode,noise_mode=noise_mode,truth_used_in_inference=False)
    if noise_mode=='estimated':
        noise,record['noise_estimation']=estimate_spatial_noise(y)
    elif noise_mode=='known':
        noise=float(values['noise'])
    else:
        raise ValueError('noise_mode must be known or estimated')
    if phase_mode=='estimated':
        inputs=UnknownPhaseInput(y,np.asarray(values['pilot']),noise,rho)
        fitted,record['phase_estimation']=phase.estimate(inputs,phase.Controls())
        operator=inputs.at_estimated_phase(fitted['phase_slopes']).operator
    elif phase_mode=='known':
        operator=np.asarray(values['a'])
    else:
        raise ValueError('phase_mode must be known or estimated')
    record['oracle_phase_supplied']=phase_mode=='known'
    record['oracle_noise_supplied']=noise_mode=='known'
    record['used_noise_variance']=noise
    record['observation_sha256']=array_sha256(y)
    record['operator_sha256']=array_sha256(operator)
    frames,users,inputs=operator.shape
    if y.shape[0]!=frames or y.shape[1:]!=(16,16) or inputs!=16:
        raise ValueError('K and Q may vary; the score channel block must remain 16 x 16 x 16')
    if not np.isfinite(scale) or scale<=0 or not np.isfinite(noise) or noise<=0:
        raise ValueError('Positive scale and noise variance required')
    a=operator.reshape(frames,users*inputs)
    u,s,vh=np.linalg.svd(a,full_matrices=False)
    normalized=y.reshape(frames,-1)/scale
    public=dict(a=block(a,device),uh=block(u.conj().T,device),vv=block(vh.conj().T,device),
        s=torch.tensor(s,dtype=torch.float32,device=device),
        y=torch.tensor(np.concatenate((normalized.real,normalized.imag)),dtype=torch.float32,device=device),
        noise=noise/scale**2,rho=rho,channel_shape=(users,2,*y.shape[1:],inputs),
        physical_input=ReceiverInput(y,operator,noise,rho))
    return public,record
