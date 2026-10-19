from pathlib import Path
import os, sys, json, hashlib, time
import numpy as np
import torch

ROOT = Path(os.environ.get('AFDM_LSTMP_ROOT', Path(__file__).resolve().parents[2]))
CONFIG = json.loads((Path(__file__).parent / 'config.json').read_text())
OUT = ROOT / CONFIG['run_directory']
PROJECT_SOURCE = OUT / 'source_project'
sys.path.insert(0, str(PROJECT_SOURCE if PROJECT_SOURCE.exists() else ROOT / 'src'))
# The copied package must still resolve read-only baseline assets in the workspace.
import afdm_jadcedd.project as project_paths
project_paths.ROOT = ROOT


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as file:
        for chunk in iter(lambda: file.read(2**20), b''):
            h.update(chunk)
    return h.hexdigest()


def save_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))
    temp.replace(path)


def save_torch(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    torch.save(value, temp); temp.replace(path)


def cpu_state(model):
    return {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}


def status(stage, **fields):
    row = dict(stage=stage, pid=os.getpid(), updated_unix=time.time(), **fields)
    save_json(OUT / 'STATUS.json', row)
    print(json.dumps(row, ensure_ascii=False, allow_nan=False), flush=True)


def real_tensor(x, device):
    return torch.as_tensor(np.stack((x.real, x.imag), axis=1).copy(), dtype=torch.float32, device=device)


def log_event(row):
    with (OUT / 'history.jsonl').open('a') as file:
        file.write(json.dumps(dict(time=time.time(), **row), allow_nan=False) + '\n')


def check_budget(start):
    if (OUT / 'pause.request').exists():
        raise InterruptedError('User pause.request; checkpoint preserved')
    if time.time() - start > CONFIG['hard_time_budget_hours'] * 3600:
        raise TimeoutError('Declared wall-clock budget reached; checkpoint preserved')
