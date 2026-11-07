"""The public NMSE must include estimation error on inactive users."""
import json

import numpy as np
import pytest

from experiment import cli
from experiment.metrics import evaluate, score_arrays


@pytest.mark.parametrize('entry', ['arrays', 'files', 'cli'])
def test_nmse_includes_inactive_channel_error(entry, tmp_path, capsys):
    truth = dict(channel=np.array([2., 0.], complex).reshape(2, 1, 1, 1),
                 activity=np.array([True, False]))
    arrays = dict(estimate=np.array([1.+1.j, 3.j]).reshape(2, 1, 1, 1),
                  activity_decision=np.array([True, True]))
    if entry == 'arrays':
        metrics = score_arrays(arrays, truth)
    else:
        estimate_path, truth_path = tmp_path/'estimate.npz', tmp_path/'truth.npz'
        np.savez(estimate_path, **arrays)
        np.savez(truth_path, **truth)
        if entry == 'files':
            metrics = evaluate(estimate_path, truth_path)
        else:
            assert cli.main(['evaluate', '--estimate', str(estimate_path), '--truth', str(truth_path)]) == 0
            metrics = json.loads(capsys.readouterr().out)
            assert metrics['aer'] == .5
    assert metrics['nmse_db'] == pytest.approx(10*np.log10(11/4))
    assert metrics['active_nmse_db'] == pytest.approx(10*np.log10(2/4))
    assert metrics['full_error'] == pytest.approx(11.)
    assert metrics['active_error'] == pytest.approx(2.)
    assert metrics['inactive_error'] == pytest.approx(9.)
    assert metrics['misses'] == 0 and metrics['false_alarms'] == 1
