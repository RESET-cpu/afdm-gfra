"""Workspace locations and explicit resolution of paths in frozen metadata."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ROOT / 'src/configs'
RESULT = ROOT / 'result'
SOURCE_PACKAGES = ('algorithm', 'evaluation', 'networks', 'system', 'training')


def source_files():
    """Current Python sources, excluding configuration, tests and historical copies."""
    files = [ROOT/'src/project.py', ROOT/'src/utils.py']
    for name in SOURCE_PACKAGES:
        files.extend((ROOT/'src'/name).rglob('*.py'))
    return sorted(files)

# Frozen JSON files keep their original bytes and asset hashes. Resolve their
# old locations only at the I/O boundary; external D: training assets stay put.
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
    path = Path(str(value).replace('\\', '/'))
    if path.is_absolute():
        try:
            path = path.relative_to(ROOT)
        except ValueError:
            return path
    name = path.as_posix()
    for previous, current in RELOCATIONS.items():
        if name == previous or name.startswith(previous + '/'):
            return ROOT / (current + name[len(previous):])
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
