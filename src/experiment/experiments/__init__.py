"""Each experiment owns its condition definitions and runnable entry point."""
from importlib import import_module
from pathlib import Path

NAMES = tuple(p.stem for p in sorted(Path(__file__).parent.glob('*.py'))
              if not p.name.startswith('_'))


def get(name):
    if name not in NAMES:
        raise ValueError('Unknown experiment: '+name)
    return import_module('.'+name, __name__)
