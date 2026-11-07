"""Scientific selection checks using explicitly synthetic metrics, no inference."""
from copy import deepcopy
import importlib.util
import math
import pytest
from project import ROOT

path=ROOT/'result/candidates/c_stmp_phase_selection_20261030/comparison.py'
spec=importlib.util.spec_from_file_location('phase_comparison',path)
comparison=importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparison)


def row(scene,index=0,error=1.,signal=10.,misses=0,converged=True,iterations=100):
    return dict(scene=scene,index=index,snr_db=[-4,0,6][index],converged=converged,iterations=iterations,
        phase_updates=2,metrics=dict(full_error=error,signal_energy=signal,misses=misses,false_alarms=0,
        active=4,inactive=36,nmse_db=10*math.log10(error/signal)))


def test_nmse_uses_energy_ratio_and_keeps_iteration_cap():
    rows=[row(0,error=1.,signal=10.),row(1,error=90.,signal=100.,converged=False,iterations=600)]
    result=comparison.aggregate(rows)
    assert result['nmse_db']==pytest.approx(10*math.log10(91/110))
    assert result['capped']==1 and result['mean_iterations']==350


def test_duplicate_or_unpaired_cases_are_rejected():
    with pytest.raises(ValueError,match='Duplicate'):
        comparison.aggregate([row(0),row(0)])
    with pytest.raises(ValueError,match='paired coverage'):
        comparison.paired([row(0)],[row(1)])
    with pytest.raises(ValueError,match='denominator mismatch'):
        comparison.paired([row(0,signal=20.)],[row(0)])


def test_detecting_more_errors_cannot_win_by_converging_faster():
    ref=[row(0),row(1)];stress=[row(10,converged=False)]
    bad=[row(0,misses=1,error=.5,iterations=10),row(1,error=.5,iterations=10)]
    result=comparison.choose({'fast_but_wrong':dict(regular=bad,stress=[row(10)])},ref,stress)
    assert result['selected'] is None


def test_stress_is_separate_and_tie_break_uses_regular_iterations():
    ref=[row(0),row(1)];stress=[row(10,converged=False)]
    a=dict(regular=[row(0,iterations=100),row(1,iterations=100)],stress=[row(10,iterations=500)])
    b=dict(regular=[row(0,error=.999,iterations=120),row(1,error=.999,iterations=120)],stress=[row(10,iterations=10)])
    result=comparison.choose({'physical_a':a,'physical_b':b},ref,stress)
    assert result['selected']=='physical_a'
    assert result['candidates']['physical_a']['regular']['candidate']['inputs']==2


def test_a_bad_snr_cannot_be_hidden_by_pooled_improvement():
    ref=[row(0,0),row(0,1)]
    cand=[row(0,0,error=1.04),row(0,1,error=.5)]
    paired=comparison.paired(cand,ref)
    assert paired['delta_nmse_db']<0
    assert not comparison.acceptable_regular(paired)


def test_holdout_uses_scene_clusters_and_preserves_caps():
    ref=[row(s,i,converged=s!=1) for s in range(3) for i in range(3)]
    cand=deepcopy(ref)
    result=comparison.validate(cand,ref,bootstrap_samples=100)
    assert result['passed']
    assert result['paired']['candidate']['scenes']==3
    assert result['paired']['candidate']['inputs']==9
    assert result['uncertainty']['delta_nmse_db_percentile95']==[0.,0.]
    assert result['uncertainty']['delta_aer_percentile95']==[0.,0.]
    cand[0]['converged']=False
    assert not comparison.validate(cand,ref,bootstrap_samples=100)['passed']
