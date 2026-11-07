"""Frozen user-count paper rendering. Only input/output paths may vary."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
METHODS = ['C_STMP', 'offgrid_sbl', 'gnn', 'gamp', 'somp']
USERS = [20, 40, 60, 80, 100]
DAMPING = {str(k): .2 if k == 100 else .4 for k in USERS}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, help='Audited SUMMARY.json or its directory')
    parser.add_argument('--output', type=Path, help='New output directory')
    args = parser.parse_args(argv)
    freeze = read(HERE / 'FROZEN.json')
    for relative, expected in freeze['files'].items():
        if sha(HERE / relative) != expected:
            raise ValueError(f'Frozen plot dependency changed: {relative}')
    cfg = read(HERE / 'CONFIG.json')
    source = (args.input or Path(cfg['input'])).resolve()
    if source.is_dir():
        source /= 'SUMMARY.json'
    summary = read(source)
    seal = read(source.parent / 'COMPLETE.json')
    if seal.get('status') != 'COMPLETE':
        raise ValueError('Use an audited complete snapshot; never plot partial conditions')
    # This checks the saved completion outputs, not the running receiver or GPU.
    for name, expected in seal['files'].items():
        path = Path(name)
        if not path.is_absolute():
            path = source.parent / path
        if sha(path) != expected:
            raise ValueError(f'Completed snapshot output changed: {path}')
    if summary['methods'] != METHODS or summary['damping_by_users'] != DAMPING:
        raise ValueError('This fixed figure requires the approved five methods and damping by users')
    if sorted({row['users'] for row in summary['rows']}) != USERS:
        raise ValueError('All five user-count conditions are required')
    if summary['scene_ids'] != list(range(summary['scene_count'])):
        raise ValueError('Use the fixed first-N paired scenes')
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    sys.path.insert(0, str(HERE / 'engine'))
    from configurable import execute_config
    arguments = ['--config', str(HERE / 'CONFIG.json'), '--input', str(source)]
    if args.output is not None:
        arguments += ['--output', str(args.output)]
    result = execute_config('user_count', arguments)
    if result == 0:
        out = (args.output or Path(cfg['output'])).resolve()
        (out / 'FROZEN_RENDERER.json').write_text(json.dumps({
            'entry': str(HERE / 'render.py'),
            'freeze_sha256': sha(HERE / 'FROZEN.json'),
            'config_sha256': sha(HERE / 'CONFIG.json'),
            'complete_sha256': sha(source.parent / 'COMPLETE.json'),
            'source_summary_sha256': sha(source),
            'scene_count': summary['scene_count'],
            'damping_by_users': DAMPING,
            'input_only_changes': True,
            'inference_started': False,
        }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    raise SystemExit(main())
