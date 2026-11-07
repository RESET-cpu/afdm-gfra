"""Explicitly run an archived module against this checkout's original assets."""
from pathlib import Path
import argparse
import hashlib
import importlib
import json
import runpy
import sys

ARCHIVE = Path(__file__).resolve().parent
ROOT = ARCHIVE.parents[1]


def load_environment():
    """Relocate reads only; do not rewrite historical code, plans or outputs."""
    manifest = json.loads((ARCHIVE/'MANIFEST.json').read_text(encoding='utf-8'))
    for original, entry in manifest['files'].items():
        path = ROOT/entry['archive']
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError('Archived source changed: ' + original)
    sys.path.insert(0, str(ROOT/'src'))
    import workspace
    import fileio
    sys.path.insert(0, str(ARCHIVE/'src'))
    project = importlib.import_module('project')
    project.ROOT, project.CONFIGS, project.RESULT = ROOT, ROOT/'src/configs', ROOT/'result'
    project.repository_path = workspace.repository_path
    project.configuration_paths = workspace.configuration_paths
    project.source_files = lambda: sorted(
        [ROOT/name for name in manifest['files'] if name.endswith('.py')]
        + list((ROOT/'src/networks').rglob('*.py')))
    utilities = importlib.import_module('utils')
    utilities.read_json, utilities.sha256 = fileio.read_json, fileio.sha256
    # The archive's training subpackages precede the maintained training tree.
    training = importlib.import_module('training')
    training.__path__.insert(0, str(ARCHIVE/'src/training'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('module', help='Original module, e.g. evaluation.white_followup_20261107.run')
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.module.split('.')[0] not in ('evaluation', 'training', 'algorithm', 'system'):
        parser.error('Choose a module in the recorded frozen source tree')
    load_environment()
    sys.argv = [args.module, *args.arguments]
    runpy.run_module(args.module, run_name='__main__')


if __name__ == '__main__':
    main()
