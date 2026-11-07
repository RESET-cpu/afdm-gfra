"""Read-only asset inventory; this command never downloads or loads checkpoints."""
import argparse
import hashlib
import json
from pathlib import Path

from workspace import CONFIGS, ROOT, repository_path


def digest(path):
    checksum = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            checksum.update(block)
    return checksum.hexdigest()


def inspect(scope='gp-mp', *, verify=False):
    manifest = json.loads((CONFIGS / 'release/assets.json').read_text(encoding='utf-8'))
    rows = []
    for asset in manifest['assets']:
        if scope != 'all' and scope not in asset['scopes']:
            continue
        path = repository_path(asset['path'])
        state = 'PRESENT' if path.is_file() else 'MISSING'
        if state == 'PRESENT':
            with path.open('rb') as stream:
                if stream.read(43).startswith(b'version https://git-lfs.github.com/spec/v1'):
                    state = 'LFS_POINTER'
        if verify and state == 'PRESENT':
            state = 'VERIFIED' if digest(path) == asset['sha256'] else 'HASH_MISMATCH'
        rows.append(dict(asset, resolved_path=str(path), status=state))
    missing = sum(r['status'] in ('MISSING', 'LFS_POINTER') for r in rows)
    changed = sum(r['status'] == 'HASH_MISMATCH' for r in rows)
    return dict(scope=scope, root=str(ROOT), checked=len(rows), missing=missing,
                hash_mismatches=changed, hashes_verified=verify,
                status='READY' if not missing and not changed else 'INCOMPLETE',
                scope_note=manifest['scope_notes'][scope], assets=rows,
                inference_started=False, training_started=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scope', choices=('gp-mp', 'models', 'figures', 'training', 'all'), default='gp-mp')
    parser.add_argument('--verify', action='store_true', help='Stream SHA-256 checks, including large weights')
    parser.add_argument('--report', type=Path, help='Save the full inventory, including expected hashes')
    args = parser.parse_args(argv)
    report = inspect(args.scope, verify=args.verify)
    for row in report['assets']:
        print(f"{row['status']:14} {row['path']}")
    if any(row['status'] == 'LFS_POINTER' for row in report['assets']):
        print('Weights were not downloaded: run git lfs pull in a Git clone; see REPRODUCING.md.')
    print(json.dumps({k: v for k, v in report.items() if k != 'assets'}, indent=2))
    if args.report:
        from fileio import write_json
        write_json(args.report, report)
    return 0 if report['status'] == 'READY' else 1
