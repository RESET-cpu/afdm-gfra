from types import SimpleNamespace
import numpy as np
from structured_receiver import Receiver


def test_postprocessing_has_no_truth_and_preserves_base():
    rng=np.random.default_rng(33)
    estimate=rng.normal(size=(3,4,3,5))+1j*rng.normal(size=(3,4,3,5))
    raw=estimate.copy();base=dict(estimate=estimate,activity_score=np.ones(3),activity_decision=np.ones(3,bool))
    receiver=object.__new__(Receiver);receiver.signature='candidate';receiver.base=SimpleNamespace(signature='base');receiver.configuration={};receiver.readout=dict(threshold=25.)
    out,record=receiver.postprocess(base,dict(seconds=2.))
    np.testing.assert_array_equal(base['estimate'],raw)
    np.testing.assert_allclose(out['activity_score'],np.sum(abs(out['estimate'])**2,axis=(1,2,3)))
    np.testing.assert_array_equal(out['activity_decision'],out['activity_score']>=25.)
    assert record['seconds']>=2. and not record['recurrence_modified'] and not record['truth_used_in_inference']
    assert np.linalg.matrix_rank(out['estimate'].reshape(3,4,-1)).tolist()==[1,1,1]
