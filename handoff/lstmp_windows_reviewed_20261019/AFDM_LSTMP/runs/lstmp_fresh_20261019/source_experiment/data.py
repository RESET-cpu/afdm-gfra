"""New scene-separated physical data. Labels never enter receiver.forward."""
import time, json
import numpy as np
import torch
from common import CONFIG, OUT, save_json, status, real_tensor, check_budget, sha
from afdm_jadcedd.system.scenario.geometry_consistent import draw_scene
from afdm_jadcedd.system.scenario.continuous import user_channel
from afdm_jadcedd.experiment.generate import generate_case


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
            import json
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
    import json
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
    return x.permute(1, 0, 4, 2, 3).reshape(1280, 256)


def unpack(x):
    return x.reshape(2, 40, 16, 16, 16).permute(1, 0, 3, 4, 2)


def block(a, device):
    return torch.tensor(np.block([[a.real, -a.imag], [a.imag, a.real]]), dtype=torch.float32, device=device)


def case_path(split, index):
    return OUT / 'data' / 'receiver' / f'{split}_{index:04d}.npz'


def case_identity(split, scale):
    settings = CONFIG['receiver']
    return dict(schema='receiver-cases-v2', count=settings[f'{split}_scenes'],
                base_seed=settings[f'{split}_seed'], snr_db=settings['snr_db'],
                scale=float(scale), phase='known oracle', noise='known')


def validate_case(values, split, index):
    settings = CONFIG['receiver']
    expected = dict(y=(16,16,16), a=(16,40,16), x=(40,16,16,16), active=(40,),
                    noise=(), rho=(), seed=(), snr=())
    if set(values) != set(expected) or any(np.shape(values[k]) != shape for k,shape in expected.items()):
        raise ValueError(f'Invalid scene fields or shape: {split}/{index}')
    if not all(np.isfinite(v).all() for v in values.values()):
        raise FloatingPointError(f'Nonfinite scene: {split}/{index}; no sample discarded')
    if (int(values['seed']) != settings[f'{split}_seed']+index or
            float(values['snr']) != settings['snr_db'][index%len(settings['snr_db'])] or
            float(values['noise']) <= 0 or not 0 < float(values['rho']) < 1 or
            not np.isin(values['active'],[0,1]).all() or not np.any(values['active'])):
        raise ValueError(f'Scene identity or physical metadata changed: {split}/{index}')


def generate_arrays(split, index, scale):
    settings = CONFIG['receiver']
    seed = settings[f'{split}_seed']+index
    snr = settings['snr_db'][index%len(settings['snr_db'])]
    inp, truth, _ = generate_case(seed, snr, scale)
    arrays = dict(y=inp['observation'], a=inp['operator'], noise=inp['noise_variance'],
                  rho=inp['activity_prior'], x=truth['channel'], active=truth['activity'], seed=seed, snr=snr)
    validate_case(arrays,split,index)
    return arrays


def build_cases(split, scale, start):
    identity = case_identity(split,scale)
    receipt_path = OUT/'data'/f'receiver_{split}.json'
    receipt = dict(identity=identity,files={})
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        if receipt.get('identity') != identity: raise ValueError(f'Scene receipt identity changed: {split}')
    expected_names = {case_path(split,i).name for i in range(identity['count'])}
    if set(receipt['files'])-expected_names: raise ValueError(f'Unexpected scene receipt entries: {split}')
    for index in range(identity['count']):
        check_budget(start)
        path = case_path(split,index)
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.name in receipt['files']:
            if not path.exists() or sha(path) != receipt['files'][path.name]:
                raise ValueError(f'Recorded scene missing or changed: {path.name}')
            with np.load(path) as z: validate_case(dict(z),split,index)
            continue
        expected = generate_arrays(split,index,scale)
        if path.exists():
            # Recover only an orphan left between atomic scene save and receipt save.
            # It must exactly match deterministic regeneration, never merely be rehashed.
            with np.load(path) as z: actual = dict(z)
            validate_case(actual,split,index)
            if any(not np.array_equal(actual[k],expected[k]) for k in expected):
                raise ValueError(f'Unrecorded scene differs from deterministic regeneration: {path.name}')
        else:
            temp = path.with_suffix('.tmp.npz'); np.savez_compressed(temp,**expected); temp.replace(path)
        receipt['files'][path.name] = sha(path)
        save_json(receipt_path,receipt)
        if index%8 == 0 or index+1 == identity['count']:
            status('GENERATING_RECEIVER_DATA',split=split,scenes=index+1,total=identity['count'])
    return receipt


class Cases:
    def __init__(self, split, scale, device):
        self.split, self.scale, self.device = split, scale, device
        self.cache = {}
        self.receipt = json.loads((OUT/'data'/f'receiver_{split}.json').read_text())
        if self.receipt.get('identity') != case_identity(split,scale):
            raise ValueError(f'Scene receipt identity changed: {split}')

    def __len__(self):
        return CONFIG['receiver'][f'{self.split}_scenes']

    def __getitem__(self, index):
        # Small CPU cache; don't retain all scenes or labels on the GPU.
        if index not in self.cache:
            path = case_path(self.split,index)
            if sha(path) != self.receipt['files'].get(path.name):
                raise ValueError(f'Scene changed after receipt verification: {path.name}')
            with np.load(path) as z: values = dict(z)
            validate_case(values,self.split,index)
            a = values['a'].reshape(16, 640)
            u, s, vh = np.linalg.svd(a, full_matrices=False)
            self.cache[index] = (values, u, s, vh)
            if len(self.cache) > 16: self.cache.pop(next(iter(self.cache)))
        values, u, s, vh = self.cache[index]
        device, scale = self.device, self.scale
        y = values['y'].reshape(16,256) / scale
        public = dict(a=block(values['a'].reshape(16,640),device), uh=block(u.conj().T,device),
                      vv=block(vh.conj().T,device), s=torch.tensor(s,dtype=torch.float32,device=device),
                      y=torch.tensor(np.concatenate((y.real,y.imag)),dtype=torch.float32,device=device),
                      noise=float(values['noise'])/scale**2, rho=float(values['rho']))
        labels = dict(x=real_tensor(values['x']/scale,device),
                      active=torch.tensor(values['active'],dtype=torch.float32,device=device))
        return public, labels, dict(seed=int(values['seed']), snr=float(values['snr']))
