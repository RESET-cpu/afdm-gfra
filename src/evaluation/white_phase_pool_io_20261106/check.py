"""No inference: fault injection for the narrow state-read adapter."""
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from . import run


class StateRead(unittest.TestCase):
    def setUp(self):
        self.state = run.pool.REV / 'sessions/123/worker0/STATE.json'

    def test_transient_read_returns_fresh_value(self):
        reader = Mock(side_effect=[PermissionError(13, 'busy'), {'stage': 'COMPLETE'}])
        with patch.object(run, 'READ', reader), patch.object(run.time, 'sleep') as sleep, \
                patch.object(run, 'log_retry') as log:
            self.assertEqual(run.read_state_retry(self.state), {'stage': 'COMPLETE'})
            self.assertEqual(reader.call_count, 2)
            sleep.assert_called_once_with(0.05)
            log.assert_called_once_with(self.state, 1, 'RECOVERED')

    def test_persistent_permission_error_is_not_hidden(self):
        reader = Mock(side_effect=PermissionError(13, 'busy'))
        with patch.object(run, 'READ', reader), patch.object(run.time, 'sleep') as sleep, \
                patch.object(run, 'log_retry') as log:
            with self.assertRaises(PermissionError):
                run.read_state_retry(self.state)
            self.assertEqual(reader.call_count, 11)
            self.assertEqual(sleep.call_count, 10)
            log.assert_called_once_with(self.state, 11, 'EXHAUSTED')

    def test_result_and_manifest_errors_are_not_retried(self):
        for path in (self.state.with_name('RESULT.json'), run.pool.OUT / 'PLAN.json',
                     run.pool.REV / 'sessions/123/worker0/nested/STATE.json'):
            reader = Mock(side_effect=PermissionError(13, 'busy'))
            with patch.object(run, 'READ', reader), patch.object(run.time, 'sleep') as sleep:
                with self.assertRaises(PermissionError):
                    run.read_state_retry(path)
                self.assertEqual(reader.call_count, 1)
                sleep.assert_not_called()

    def test_invalid_json_and_missing_state_propagate(self):
        for error in (json.JSONDecodeError('invalid', '', 0), FileNotFoundError('missing')):
            reader = Mock(side_effect=error)
            with patch.object(run, 'READ', reader), patch.object(run.time, 'sleep') as sleep:
                with self.assertRaises(type(error)):
                    run.read_state_retry(self.state)
                self.assertEqual(reader.call_count, 1)
                sleep.assert_not_called()

    def test_real_windows_sharing_denial_then_release(self):
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        create = kernel.CreateFileW
        create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                           ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        create.restype = wintypes.HANDLE
        close = kernel.CloseHandle
        close.argtypes = [wintypes.HANDLE]
        close.restype = wintypes.BOOL
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); path = root / 'sessions/123/worker0/STATE.json'
            path.parent.mkdir(parents=True); path.write_text('{"stage":"READY"}')
            handle = create(str(path), 0x80000000, 0, None, 3, 0x80, None)
            self.assertNotEqual(handle, ctypes.c_void_p(-1).value)
            try:
                with self.assertRaises(PermissionError):
                    run.READ(path)
            except BaseException:
                close(handle)
                raise
            timer = threading.Timer(0.12, lambda: close(handle)); timer.start()
            try:
                with patch.object(run.pool, 'REV', root), patch.object(run, 'log_retry') as log:
                    self.assertEqual(run.read_state_retry(path), {'stage': 'READY'})
                    self.assertEqual(log.call_count, 1)
                    self.assertEqual(log.call_args.args[2], 'RECOVERED')
            finally:
                timer.join()

    def test_original_coordinate_and_duplicate_guard_are_used(self):
        original_read = run.pool.g.read_json
        original_tokens = run.pool.TOKENS
        def check():
            self.assertIs(run.pool.g.read_json, run.read_state_retry)
            self.assertIn(run.MODULE, run.pool.TOKENS)
            self.assertEqual(run.pool.MODULE, 'evaluation.white_phase_pool_20261106.run')
        with patch.object(run, 'verify'), patch.object(run.pool, 'coordinate', side_effect=check) as coordinate:
            run.coordinate(); coordinate.assert_called_once_with()
        self.assertIs(run.pool.g.read_json, original_read)
        self.assertEqual(run.pool.TOKENS, original_tokens)


if __name__ == '__main__':
    unittest.main()
