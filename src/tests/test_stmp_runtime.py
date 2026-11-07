"""Numerical equivalence of the independent runtime-only initializer."""
import numpy as np
from algorithm.proposed import phase_initialization as original
from algorithm.STMP import runtime_initialization as candidate


def test_repeated_optimizer_value_does_not_recompute_or_alias_gradient():
    calls=[]
    def function(x,scale):
        calls.append(x.copy())
        return scale*np.dot(x,x),2*scale*x
    evaluate=candidate._MemoizedObjective(function,(3.,))
    x=np.array([1.,2.])
    value,gradient=evaluate(x)
    gradient[:]=99
    assert evaluate(x)[0]==value
    np.testing.assert_array_equal(evaluate(x)[1],[6.,12.])
    x[0]=4.
    assert evaluate(x)[0]==60.
    assert len(calls)==2


def problem():
    rng=np.random.default_rng(202610231)
    blocks=rng.normal(size=(3,6,4))+1j*rng.normal(size=(3,6,4))
    gram=np.einsum('kin,kjn->kij',blocks,blocks.conj())/4
    y=rng.normal(size=(6,16))+1j*rng.normal(size=(6,16))
    sample=y@y.conj().T/16
    return gram,sample,.3,np.repeat(np.arange(3),2),.1


def test_value_without_unused_weight_is_identical():
    gram,sample,noise,_,_=problem()
    covariance=gram.sum(axis=0)+noise*np.eye(6)
    expected=original.factor_value(covariance,sample)
    value,inverse,weight=candidate.factor_value(covariance,sample,weight_required=False)
    assert value==expected[0]
    np.testing.assert_array_equal(inverse,expected[1])
    assert weight is None


def test_coordinate_and_joint_paths_are_exactly_preserved():
    args=problem()
    a=original.coordinate(*args)
    b=candidate.coordinate(*args)
    np.testing.assert_array_equal(a[0],b[0])
    np.testing.assert_array_equal(a[1],b[1])
    np.testing.assert_array_equal(a[2]['objective'],b[2]['objective'])
    gram,sample,noise,frames,rho=args
    a=original.joint(gram,sample,noise,frames,a[0],a[1],rho)
    b=candidate.joint(gram,sample,noise,frames,b[0],b[1],rho)
    np.testing.assert_array_equal(a[0],b[0])
    np.testing.assert_array_equal(a[1],b[1])
    np.testing.assert_array_equal(a[2]['objective'],b[2]['objective'])
    assert a[2]['evaluations']==b[2]['actual_objective_evaluations']
    assert b[2]['reused_objective_evaluations']>0


def test_evaluator_releases_only_inactive_receiver_cache():
    from types import SimpleNamespace
    from evaluation.receivers import activate
    calls=[]
    def receiver(name):
        return SimpleNamespace(_experiment_spec=dict(device_modules=[],backend='cpu'),
            release_runtime_cache=lambda:calls.append(name))
    models={name:receiver(name) for name in ('first','second')}
    activate(models,'first','cpu')
    assert calls==['second']
    activate(models,'second','cpu')
    assert calls==['second','first']
