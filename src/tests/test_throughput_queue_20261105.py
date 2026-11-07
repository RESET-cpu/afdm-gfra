"""Runtime admission and backend separation, without launching experiments."""
from evaluation.throughput_20261105.convergence_queue import admission, backend


def test_backend_separation():
    assert backend('STMP') == backend('GP-MP') == 'gpu'
    for budget in (7, 13, 25):
        assert backend(f'Off-grid SBL ({budget})') == 'cpu'


def test_reserve_includes_unallocated_worker_growth():
    assert admission(6., 1., 2.3, 1.25)
    assert not admission(4., 1., 2.3, 1.25)
    assert admission(3.55, 0., 2.3, 1.25)
    assert not admission(3.54, 0., 2.3, 1.25)


def test_transient_status_lock_does_not_stop_queue(monkeypatch, tmp_path):
    from evaluation.throughput_20261105 import convergence_queue as queue
    calls = []

    def locked_then_free(path, value):
        calls.append(value)
        if len(calls) < 3:
            raise PermissionError('temporary Windows sharing violation')

    monkeypatch.setattr(queue, 'write_json', locked_then_free)
    monkeypatch.setattr(queue.time, 'sleep', lambda seconds: None)
    assert queue.publish_status(tmp_path/'STATUS.json', {'completed': 3})
    assert len(calls) == 3


def test_locked_advisory_read_uses_last_complete_snapshot(monkeypatch, tmp_path):
    from evaluation.throughput_20261105 import convergence_queue as queue
    path = tmp_path/'STATUS.json'
    queue.STATE_CACHE[str(path)] = {'completed': 10}

    def locked(path):
        raise PermissionError('temporary Windows sharing violation')

    monkeypatch.setattr(queue, 'read_json', locked)
    monkeypatch.setattr(queue.time, 'sleep', lambda seconds: None)
    assert queue.read_state(path) == {'completed': 10}
