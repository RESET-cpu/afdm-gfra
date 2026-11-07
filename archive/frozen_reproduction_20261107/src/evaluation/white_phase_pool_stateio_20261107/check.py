"""CPU fault injection: worker state reads and atomic replacements only."""
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

from . import run


class StateIO(unittest.TestCase):
    def setUp(self):
        self.state = run.pool.REV / 'sessions/123/worker0/STATE.json'

    def test_transient_write_reuses_same_value(self):
        value = {'stage': 'BUSY', 'position': 4483}
        writer = Mock(side_effect=[PermissionError(13, 'busy'), None])
        with patch.object(run, 'WRITE', writer), patch.object(run.time, 'sleep'), \
                patch.object(run, 'log_retry') as log:
            run.write_state_retry(self.state, value)
            self.assertEqual(writer.call_count, 2)
            for call in writer.call_args_list:
                self.assertIs(call.args[1], value)
            log.assert_called_once_with(self.state, 'write', 1, 'RECOVERED')

    def test_persistent_write_error_is_not_hidden(self):
        writer = Mock(side_effect=PermissionError(13, 'busy'))
        with patch.object(run, 'WRITE', writer), patch.object(run.time, 'sleep') as sleep, \
                patch.object(run, 'log_retry') as log:
            with self.assertRaises(PermissionError):
                run.write_state_retry(self.state, {})
            self.assertEqual(writer.call_count, 11)
            self.assertEqual(sleep.call_count, 10)
            log.assert_called_once_with(self.state, 'write', 11, 'EXHAUSTED')

    def test_result_write_and_serialization_errors_are_not_retried(self):
        for path, error in ((self.state.with_name('RESULT.json'), PermissionError('busy')),
                            (self.state, ValueError('invalid value'))):
            writer = Mock(side_effect=error)
            with patch.object(run, 'WRITE', writer), patch.object(run.time, 'sleep') as sleep:
                with self.assertRaises(type(error)):
                    run.write_state_retry(path, {})
                self.assertEqual(writer.call_count, 1)
                sleep.assert_not_called()

    def test_read_retry_and_invalid_json(self):
        with patch.object(run, 'READ', side_effect=[PermissionError('busy'), {'stage': 'READY'}]), \
                patch.object(run.time, 'sleep'), patch.object(run, 'log_retry'):
            self.assertEqual(run.read_state_retry(self.state), {'stage': 'READY'})
        reader = Mock(side_effect=json.JSONDecodeError('invalid', '', 0))
        with patch.object(run, 'READ', reader), patch.object(run.time, 'sleep') as sleep:
            with self.assertRaises(json.JSONDecodeError):
                run.read_state_retry(self.state)
            self.assertEqual(reader.call_count, 1)
            sleep.assert_not_called()

    def test_real_windows_reader_blocks_atomic_replace_then_releases(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); path = root / 'sessions/123/worker0/STATE.json'
            run.WRITE(path, {'stage': 'COMPLETE', 'position': 4482})
            held = path.open('rb')
            try:
                with self.assertRaises(PermissionError):
                    run.WRITE(path, {'stage': 'BUSY', 'position': 4483})
                self.assertEqual(json.loads(held.read()), {'stage': 'COMPLETE', 'position': 4482})
            except BaseException:
                held.close()
                raise
            timer = threading.Timer(0.12, held.close); timer.start()
            try:
                with patch.object(run.pool, 'REV', root), patch.object(run, 'log_retry') as log:
                    run.write_state_retry(path, {'stage': 'BUSY', 'position': 4483})
                    self.assertEqual(run.READ(path), {'stage': 'BUSY', 'position': 4483})
                    self.assertEqual(log.call_count, 1)
                    self.assertEqual(log.call_args.args[1], 'write')
                    self.assertEqual(log.call_args.args[3], 'RECOVERED')
            finally:
                timer.join()

    def test_read_write_contention_keeps_whole_states(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); path = root / 'sessions/123/worker0/STATE.json'
            run.WRITE(path, {'sequence': 0, 'payload': 'x' * 1000})
            done = threading.Event(); failures = []
            def publish():
                try:
                    for sequence in range(1, 201):
                        run.write_state_retry(path, {'sequence': sequence, 'payload': 'x' * 1000})
                except BaseException as error:
                    failures.append(error)
                finally:
                    done.set()
            with patch.object(run.pool, 'REV', root), patch.object(run, 'log_retry'):
                thread = threading.Thread(target=publish); thread.start()
                try:
                    while not done.is_set():
                        state = run.read_state_retry(path)
                        self.assertTrue(0 <= state['sequence'] <= 200)
                        self.assertEqual(state['payload'], 'x' * 1000)
                finally:
                    thread.join()
            self.assertFalse(failures)
            self.assertEqual(run.READ(path)['sequence'], 200)

    def test_both_entrypoints_use_unchanged_worker_and_restore_globals(self):
        old = (run.pool.MODULE, run.pool.g.read_json, run.pool.g.write_json)
        execute = run.pool.execute_case
        def check(*args):
            self.assertEqual(run.pool.MODULE, run.MODULE)
            self.assertIs(run.pool.execute_case, execute)
            self.assertIs(run.pool.g.read_json, run.read_state_retry)
            self.assertIs(run.pool.g.write_json, run.write_state_retry)
            self.assertIn(run.previous.MODULE, run.pool.TOKENS)
        with patch.object(run, 'verify'), patch.object(run.pool, 'coordinate', side_effect=check) as coord, \
                patch.object(run.pool, 'worker', side_effect=check) as worker:
            run.coordinate(); run.worker('123', 0)
            coord.assert_called_once_with(); worker.assert_called_once_with('123', 0)
        self.assertEqual(old, (run.pool.MODULE, run.pool.g.read_json, run.pool.g.write_json))


if __name__ == '__main__':
    unittest.main()
