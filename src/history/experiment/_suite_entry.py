"""Dispatch the public CLI to the current ten-layer/shared-2000 protocol."""
from pathlib import Path
import sys


def dispatch(filename):
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'experiments/lstmp_evaluation_2000_20261021'))
    from suite import main
    return main(Path(filename).stem)
