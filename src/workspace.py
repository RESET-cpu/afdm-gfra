"""Workspace locations and explicit resolution of paths in frozen metadata."""
from pathlib import Path, PureWindowsPath
import json
from functools import lru_cache

SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parent
CONFIGS = SOURCE / 'configs'
RESULT = ROOT / 'result'
SOURCE_PACKAGES = ('scenario', 'waveform', 'channel', 'receiver', 'experiment', 'plotting', 'networks')


def source_files():
    """Organized source files recorded by new experiment plans."""
    base = SOURCE
    files = [base/'workspace.py', base/'fileio.py']
    for name in SOURCE_PACKAGES:
        files.extend((base/name).rglob('*.py'))
    return sorted(files)


@lru_cache(maxsize=4)
def _frozen_sources(manifest):
    return json.loads(manifest.read_text(encoding='utf-8'))['files'] if manifest.exists() else {}


def frozen_read_path(value):
    """Locate exact archived source bytes referenced by a frozen record.

    Only declared original paths are redirected, and only for reading. Current
    implementations, model assets, experiment outputs and write paths are not
    substituted. The manifest distinguishes original STMP from current stmp.
    """
    path = repository_path(value)
    try:
        name = path.relative_to(ROOT).as_posix()
    except ValueError:
        return path
    entry = _frozen_sources(ROOT/'archive/frozen_reproduction_20261107/MANIFEST.json').get(name)
    if entry is None:
        return path
    destination = (ROOT/entry['archive']).resolve()
    archive = (ROOT/'archive/frozen_reproduction_20261107').resolve()
    if not destination.is_relative_to(archive):
        raise ValueError('Frozen source must remain inside its declared archive')
    return destination


def physical_source_files():
    """Scene and observation dependencies, independent of receiver selection."""
    base = SOURCE
    return sorted(p for name in ('scenario', 'waveform', 'channel', 'receiver/frontend')
                  for p in (base / name).rglob('*.py'))


# Frozen JSON files keep their original bytes and asset hashes. Resolve their
# old locations only at the I/O boundary. Only the known former checkout root
# is relocated; unrelated external paths are never silently redirected.
RELOCATIONS = {
    'paper/literature': 'reference/literature',
    'paper/writing_profile': 'reference/writing_profile',
    'configs': 'src/configs', 'results': 'result',
    'models': 'result/models', 'data': 'result/data', 'runs': 'result/runs',
    'output': 'result/output', 'tmp': 'result/tmp',
    'docs': 'paper/docs', 'references': 'reference',
    'scripts': 'src/history/scripts', 'cloud': 'src/history/cloud',
    'experiment': 'src/history/experiment', 'experiments': 'src/history/experiments',
    'tests': 'src/history/tests', 'run.py': 'src/history/run.py',
}


def repository_path(value):
    """Locate an old or current repository path without changing its contents."""
    name = str(value).replace('\\', '/')
    explicit = Path(name)
    if explicit.is_absolute() and explicit.is_relative_to(ROOT):
        # An explicit path in this checkout is already resolved. In particular,
        # a checkout nested below the former root must not gain its prefix twice.
        return explicit
    old_root = 'D:/afdm-gfra'
    if name.casefold().startswith(old_root.casefold() + '/'):
        name = name[len(old_root) + 1:]
    path = Path(name)
    if path.is_absolute():
        try:
            path = path.relative_to(ROOT)
        except ValueError:
            return path
    elif PureWindowsPath(name).is_absolute():
        # Leave another machine's external path explicit, including on POSIX.
        return path
    name = path.as_posix()
    if name == 'src' or name.startswith('src/'):
        return SOURCE / name.removeprefix('src').lstrip('/')
    for previous, current in RELOCATIONS.items():
        if name == previous or name.startswith(previous + '/'):
            return repository_path(current + name[len(previous):])
    return ROOT / path


def configuration_paths(value):
    """Copy configuration and resolve declared asset paths, preserving SHA fields."""
    fields = {'path', 'checkpoint_path', 'first_checkpoint', 'second_checkpoint',
              'evidence_checkpoint', 'prior_definition', 'bank_path', 'bundle_path'}
    if isinstance(value, dict):
        return {key: str(repository_path(item)) if key in fields and isinstance(item, str)
                else configuration_paths(item) for key, item in value.items()}
    if isinstance(value, list):
        return [configuration_paths(item) for item in value]
    return value
