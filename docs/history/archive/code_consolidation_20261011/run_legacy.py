"""Execute an archived relative script with its matching source and configuration."""
from pathlib import Path
import os
import subprocess
import sys

WORKSPACE = Path(__file__).resolve().parent/'workspace'


def main():
    if len(sys.argv) < 2:
        print('Usage: python run_legacy.py RELATIVE_SCRIPT [ARGUMENTS...]')
        return 2
    relative = Path(sys.argv[1])
    script = WORKSPACE/relative
    if relative.is_absolute() or '..' in relative.parts or not script.is_file():
        raise ValueError('An existing script relative to the snapshot workspace is required')
    env = dict(os.environ, PYTHONPATH=str(WORKSPACE/'src'), PYTHONDONTWRITEBYTECODE='1')
    return subprocess.call([sys.executable, '-B', str(script), *sys.argv[2:]], cwd=WORKSPACE, env=env)


if __name__ == '__main__':
    raise SystemExit(main())
