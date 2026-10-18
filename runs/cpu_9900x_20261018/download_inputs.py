"""Download and verify the fixed 9900X inputs from the private GitHub release."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def restore(archive_path, destination):
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise ValueError(f'Unexpected archive path: {member.filename}')
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if target.exists():
                with archive.open(member) as source:
                    expected = hashlib.file_digest(source, 'sha256').hexdigest()
                if target.stat().st_size != member.file_size or sha(target) != expected:
                    raise ValueError(f'Existing file differs; preserved without overwrite: {target}')
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + '.downloading')
            with archive.open(member) as source, temporary.open('wb') as output:
                shutil.copyfileobj(source, output, 8 * 1024 * 1024)
            temporary.replace(target)

def main():
    manifest = json.loads((ROOT / 'GITHUB_ASSETS.json').read_text())
    cache = ROOT / 'download_cache'
    package = ROOT / 'package'
    cache.mkdir(exist_ok=True)
    for asset in manifest['assets']:
        path = cache / asset['name']
        if not (path.exists() and path.stat().st_size == asset['bytes'] and sha(path) == asset['sha256']):
            print(f'Downloading {asset["name"]}', flush=True)
            subprocess.run(['gh', 'release', 'download', manifest['tag'], '--repo', manifest['repository'],
                            '--pattern', asset['name'], '--dir', str(cache), '--clobber'], check=True)
        if path.stat().st_size != asset['bytes'] or sha(path) != asset['sha256']:
            raise ValueError(f'Incomplete download or SHA-256 mismatch: {path}')
        print(f'Verified {path.name}; extracting fixed inputs', flush=True)
        restore(path, package)
    print(f'All fixed inputs ready: {package}')
    print('Follow README_9900X.md: create CPU environment, check both experiments, smoke, then run.')

if __name__ == '__main__':
    main()
