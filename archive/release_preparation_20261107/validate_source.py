"""Check downloaded-source usage, with no project installation or research assets."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import sysconfig
import tempfile
import time
import venv

ROOT = Path(__file__).resolve().parents[2]
AREA = Path(tempfile.mkdtemp(prefix='source_download_', dir=ROOT/'tmp'))
COPY = AREA/'downloaded source'
COPY.mkdir()
for name in ('README.md', 'REPRODUCING.md', 'RIGHTS.md', 'CITATION.cff', 'requirements.txt',
             'requirements-tested.txt', 'ENVIRONMENT.json', 'pyproject.toml', 'run_experiments.py'):
    shutil.copy2(ROOT/name, COPY/name)
for path in (ROOT/'src').rglob('*'):
    if not path.is_file() or any(p in ('history', '__pycache__') for p in path.relative_to(ROOT/'src').parts):
        continue
    if path.suffix not in ('.py', '.json', '.md') and path.name not in ('LICENSE', 'LICENSE.cai'):
        continue
    target = COPY/path.relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)

# No editable/project install. Reuse observed dependency files without
# processing their editable-project .pth hooks. This isolates source imports,
# not package-index availability or fresh dependency resolution.
environment = AREA/'dependencies'
venv.EnvBuilder(with_pip=False).create(environment)
python = environment/'Scripts/python.exe' if os.name == 'nt' else environment/'bin/python'
library = environment/'Lib/site-packages' if os.name == 'nt' else environment/f'lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages'
library.mkdir(parents=True, exist_ok=True)
(library/'dependencies.pth').write_text(sysconfig.get_path('purelib')+'\n', encoding='utf-8')
checks = []


def check(name, arguments, expected=0, cwd=COPY):
    start = time.perf_counter()
    result = subprocess.run([str(python), '-I', '-B', *map(str, arguments)], cwd=cwd,
                            capture_output=True, text=True, encoding='utf-8', errors='replace',
                            env=dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8'))
    (AREA/(name+'.log')).write_text(result.stdout+'\n'+result.stderr, encoding='utf-8')
    checks.append(dict(check=name, exit_code=result.returncode, expected_exit=expected,
                       seconds=time.perf_counter()-start))
    assert result.returncode == expected, result.stdout[-1200:]+result.stderr[-1500:]
    print(name, 'PASS', flush=True)


report = dict(status='RUNNING', artifact_directory=str(AREA),
              project_installed=False, weights_or_raw_data_copied=False,
              dependency_environment='existing verified dependencies, isolated source imports; not a fresh network installation',
              training_started=False, formal_experiment_started=False)
try:
    probe = 'import importlib.util;assert importlib.util.find_spec("workspace") is None'
    check('no_project_install', ['-c', probe], cwd=AREA)
    check('list', [COPY/'run_experiments.py', 'list'])
    check('help', [COPY/'run_experiments.py', 'snr_comparison', '--help'])
    check('demo', [COPY/'run_experiments.py', 'demo', '--output', AREA/'demo'])
    check('plot_list', [COPY/'run_experiments.py', 'plot', '--list'])
    check('missing_assets', [COPY/'run_experiments.py', 'assets', '--scope', 'gp-mp'], expected=1)
    check('public_tests', ['-m', 'pytest', '-q'])
    assert not (COPY/'result/models').exists()
    report['status'] = 'PASS'
finally:
    report['checks'] = checks
    (Path(__file__).parent/'SOURCE_VALIDATION.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
