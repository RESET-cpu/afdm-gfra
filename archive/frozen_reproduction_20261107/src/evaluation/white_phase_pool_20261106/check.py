"""CPU checks of execution guards; no model import or inference."""
import ast
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from . import run


class Guards(unittest.TestCase):
    def test_legacy_module_is_detected(self):
        own=SimpleNamespace(pid=20,parents=lambda:[SimpleNamespace(pid=10)])
        with patch.object(run.psutil,'Process',return_value=own), patch.object(run.g,'live_processes',
                return_value=[{'pid':20},{'pid':10},{'pid':30}]):
            with self.assertRaisesRegex(RuntimeError,'Existing'):
                run.no_other_execution()

    def test_own_launcher_is_not_duplicate(self):
        own=SimpleNamespace(pid=20,parents=lambda:[SimpleNamespace(pid=10)])
        with patch.object(run.psutil,'Process',return_value=own), patch.object(run.g,'live_processes',
                return_value=[{'pid':20},{'pid':10}]):
            run.no_other_execution()

    def test_stop_blocks_coordinate_before_gpu(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'STOP.json').write_text('{}')
            with patch.object(run,'OUT',root),patch.object(run.g,'require_ready'),patch.object(run,'verify'),\
                    patch.object(run.g,'verify'),patch.object(run,'no_other_execution'),\
                    patch.object(run,'initialize') as gpu:
                with self.assertRaisesRegex(RuntimeError,'STOP'):
                    run.coordinate()
                gpu.assert_not_called()

    def test_missing_prerequisite_blocks_before_gpu(self):
        with patch.object(run.g,'require_ready',side_effect=RuntimeError('prerequisite')),\
                patch.object(run,'initialize') as gpu:
            with self.assertRaisesRegex(RuntimeError,'prerequisite'):
                run.worker('dummy',0)
            gpu.assert_not_called()

    def test_validation_gate_blocks_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(run,'OUT',Path(directory)),patch.object(run.g,'require_ready'),\
                    patch.object(run,'verify'),patch.object(run.g,'verify'),\
                    patch.object(run,'no_other_execution'),\
                    patch.object(run.g,'read_json',return_value={'status':'FAILED'}),\
                    patch.object(run,'launch') as launch:
                with self.assertRaises(AssertionError):run.coordinate()
                launch.assert_not_called()

    def test_saving_precedes_truth_and_no_known_input(self):
        tree=ast.parse(Path(run.__file__).read_text())
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='execute_case')
        source=ast.unparse(function)
        self.assertIn('UnknownPhaseInput',source)
        self.assertNotIn('ReceiverInput(',source)
        self.assertLess(source.index('save_arrays('),source.index("'truth.npz'"))
        self.assertIn('exist_ok=False',source)
        self.assertIn('Refusing to rerun',source)


if __name__=='__main__':unittest.main()
