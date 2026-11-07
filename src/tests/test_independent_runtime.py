"""Current execution assets must not need an old project directory or junction."""
from pathlib import Path
import sys

from project import ROOT
from algorithm.registry import load_models
from utils import read_json


def test_selected_inference_assets_are_inside_project():
    binding = load_models()
    for key in ('run', 'checkpoint'):
        path = Path(binding['proposed'][key])
        assert path.exists()
        assert path.resolve().is_relative_to(ROOT)
    for key in ('first_checkpoint', 'second_checkpoint', 'evidence_checkpoint', 'prior_definition'):
        path = ROOT / binding['STMP'][key]
        assert path.exists()
        assert path.resolve().is_relative_to(ROOT)


def test_active_plans_and_saved_results_use_local_files():
    root = ROOT / 'result/final2000'
    plans = sorted(root.glob('*/PLAN.json'))
    assert len(plans) == 8
    for filename in plans:
        plan = read_json(filename)
        for name in (*plan['assets'], plan['cache'], plan['scene_registry'], plan['configuration_file']):
            path = Path(name)
            assert path.exists(), name
            assert path.resolve().is_relative_to(ROOT), name
        assert not Path(plan['cache']).is_junction()
        for pointer in filename.parent.glob('scene*/condition*/*.json'):
            path = Path(read_json(pointer)['result'])
            assert path.is_file()
            assert path.resolve().is_relative_to(ROOT)


def test_windows_python_base_is_project_local():
    if sys.platform == 'win32':
        assert Path(sys.executable).resolve().is_relative_to(ROOT)
        assert Path(sys.base_prefix).resolve() == ROOT / '.venv/base'
