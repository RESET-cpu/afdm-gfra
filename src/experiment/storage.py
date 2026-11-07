"""NumPy result arrays shared by all experiment entrypoints."""
import os
import numpy as np


def save_arrays(path, arrays):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f'.{os.getpid()}.tmp')
    with temp.open('wb') as f:
        np.savez_compressed(f, **arrays)
    temp.replace(path)


def arrays(path):
    with np.load(path, allow_pickle=False) as values:
        return dict(values)
