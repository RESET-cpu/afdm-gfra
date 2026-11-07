"""Small, explicit runtime helpers; scientific operations live in the receivers."""
import json
import os
from pathlib import Path
import time

import psutil
from workspace import ROOT
from fileio import read_json, write_json, sha256

OUT = ROOT / 'result/white_followup_20261107'
ARCHIVE = ROOT / 'archive/white_mainline_20261107'
CONFIG = ROOT / 'src/configs/candidates/GP_MP_white_preconditioned_matched_20261104.json'
PHASE_CONFIG = ROOT / 'src/configs/candidates/GP_MP_white_phase_frontend_marginal_20261106.json'


def checked(path, digest):
    path = Path(path)
    if sha256(path) != digest:
        raise ValueError('Changed bound file: ' + str(path))
    return path


def publish(path, value):
    """Only advisory mutable status gets bounded Windows sharing retries."""
    path = Path(path)
    if path.name not in ('STATUS.json', 'STATE.json'):
        return write_json(path, value)
    for attempt in range(11):
        try:
            return write_json(path, value)
        except PermissionError:
            if attempt == 10:
                raise
            time.sleep(.05)


def identity():
    p = psutil.Process()
    return dict(pid=p.pid, created_unix=p.create_time(), command=p.cmdline())


def setup():
    import torch
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA is required for the authorized learned receiver runs')
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)


def acquire(folder):
    folder = Path(folder)
    for name in ('FAILURE.json', 'STOP.json', 'COMPLETION.json'):
        if (folder / name).exists():
            raise RuntimeError('Inspect existing ' + str(folder / name))
    token = identity()
    lock = folder / 'RUNNING.lock'
    with lock.open('x', encoding='utf-8') as f:
        json.dump(token, f)
    return lock, token


def verify_plan(folder):
    folder = Path(folder)
    checked(folder / 'PLAN.json', read_json(folder / 'PLAN_HASH.json')['sha256'])
    plan = read_json(folder / 'PLAN.json')
    for path, digest in plan['assets'].items():
        checked(ROOT / path, digest)
    return plan
