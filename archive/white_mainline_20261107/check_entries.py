from pathlib import Path
import sys,inspect
sys.path.insert(0,str(Path('src').resolve()))
from algorithm import registry
from utils import read_json,write_json,sha256
root=Path.cwd();archive=root/'archive/white_mainline_20261107'
sys.path.insert(0,str(root))
d=registry.load_catalog()
assert 'pretrained_colored_first' not in d
for m in ('GP_MP','GP_MP_EP','C_STMP','pretrained_white_first'):
    assert d[m]['factory'].startswith('algorithm.GP_MP.')
    registry.source_files(d[m],{},'cpu')
assert inspect.signature(registry.build_receiver).parameters['algorithm'].default=='GP_MP'
for name in ('snr_comparison','pilot_frames','user_count','activity_probability','cross_channel'):
    c=read_json(root/f'src/configs/experiments/{name}.json')
    assert c['methods'][0]=='GP_MP' and c['reference_method']=='GP_MP'
    assert c['scenes']==(1000 if name=='snr_comparison' else 500)
import run_experiments
assert run_experiments.suite.DEFAULT_OUTPUT==root/'result/white_mainline_default_20261107'
assert not any(n.startswith(('algorithm.C_STMP','training.colored')) for n in sys.modules)
files=['run_experiments.py','src/evaluation/cli.py','src/algorithm/registry.py','src/algorithm/__init__.py','README.md','src/README.md','src/algorithm/README.md','src/evaluation/README.md']
write_json(archive/'ENTRYPOINT_VALIDATION.json',dict(status='PASS',current_factories_white=True,legacy_catalog_preserved=True,
    default_plan_isolated=True,default_receiver='GP_MP',imported_colored_implementation=False,
    files={p:sha256(root/p) for p in files}))
print('PASS: default registry, factory signatures, isolated output and import graph')
