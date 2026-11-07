"""Atomic result files and immutable source/weight identities."""
from pathlib import Path
import hashlib
import json
import os
import gzip
import numpy as np
from . import ROOT


def read(path):
    path = Path(path)
    if path.suffix == ".gz":
        with gzip.open(path, "rt") as f:
            return json.load(f)
    return json.loads(path.read_text())


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f'.{os.getpid()}.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    temp.replace(path)


def save_arrays(path, arrays):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f'.{os.getpid()}.tmp')
    with temp.open('wb') as f:
        np.savez_compressed(f, **arrays)
    temp.replace(path)


def identities():
    files = [ROOT / 'MAINLINE.json']
    for directory, pattern in [('src', '*.py'), ('configs', '*.json'), ('experiment', '*.py'),
                               ('models/proposed', '*'), ('models/gnn', '*')]:
        files.extend(p for p in (ROOT / directory).rglob(pattern) if p.is_file())
    return {str(p.relative_to(ROOT)): sha(p) for p in files}


def verify_sources(plan):
    for name, expected in plan['source_and_weight_sha256'].items():
        if sha(ROOT / name) != expected:
            raise ValueError('Experiment source or weight changed: ' + name)


def arrays(path):
    with np.load(path, allow_pickle=False) as values:
        return dict(values)


def pending_methods(folder, methods, hash_key="compact_sha256"):
    pending = []
    for method in methods:
        path = folder / f"{method}.json"
        if not path.exists():
            pending.append(method)
            continue
        record = read(path)
        if record["status"] != "COMPLETE" or sha(path.with_suffix(".npz")) != record[hash_key]:
            raise ValueError("Preserved failure or changed result requires inspection: " + str(path))
    return pending
