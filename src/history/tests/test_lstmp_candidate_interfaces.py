"""Nontraining regression checks for the independent five-layer candidate."""
import copy
import json
import time
from pathlib import Path

import numpy as np
import pytest
import torch

from experiments.lstmp_candidate_20261019 import common,data,receiver,train


@pytest.mark.parametrize('shape,q', [((3,2,2,4,3),4),((2,2,3,2,2),6),((5,2,2,3,4),3)])
def test_dimensions_and_lmmse_against_complex_precision(shape,q):
    rng=np.random.default_rng(3127+q)
    k,_,m,t,n=shape; count=k*n
    z=lambda *s:(rng.normal(size=s)+1j*rng.normal(size=s))/2**.5
    a=z(q,count);y=z(q,m*t);prior=z(k,m,t,n)
    u,s,vh=np.linalg.svd(a,full_matrices=False)
    block=lambda x:torch.from_numpy(np.block([[x.real,-x.imag],[x.imag,x.real]]))
    p=torch.from_numpy(np.stack((prior.real,prior.imag),axis=1))
    public=dict(a=block(a),y=torch.from_numpy(np.concatenate((y.real,y.imag))),
        uh=block(u.conj().T),vv=block(vh.conj().T),s=torch.from_numpy(s),noise=.3)
    v=torch.tensor(.7,dtype=torch.float64)
    mean,var=receiver.linear_update(public,p,v)
    assert torch.equal(data.unpack(data.pack(p),shape),p)
    covariance=np.linalg.inv(np.eye(count)/float(v)+a.conj().T@a/.3)
    packed=prior.transpose(0,3,1,2).reshape(count,m*t)
    expected=covariance@(packed/float(v)+a.conj().T@y/.3)
    actual=data.pack(mean).numpy()
    np.testing.assert_allclose(actual[:count]+1j*actual[count:],expected,rtol=2e-12,atol=2e-12)
    assert float(var)==pytest.approx(covariance.trace().real/count,rel=2e-12)


@pytest.mark.parametrize('raw',[-.5,-.01,0.,.1,2.])
def test_feedback_calibration_removes_negative_residual_range_restriction(raw):
    v=torch.tensor(1.,dtype=torch.float64);d=torch.tensor(raw,dtype=torch.float64)
    zero=torch.tensor(0.,dtype=torch.float64)
    new,_=receiver.feedback_variance(d,v,zero)
    old,_=receiver.feedback_variance(d,v,zero,order='before_positive')
    # The smooth ratio floor adds at most 1e-6 relative to the old hard floor.
    torch.testing.assert_close(new,old,rtol=0,atol=1.01e-6)
    beta=torch.tensor(12.,dtype=torch.float64,requires_grad=True)
    new,q=receiver.feedback_variance(d,v,beta)
    old,_=receiver.feedback_variance(d,v,beta,order='before_positive')
    if raw<=0: assert new>.1 and old<.014
    assert 0<q<=.95
    if raw==0:
        derivative=torch.autograd.grad(new,beta)[0]
        # At high beta the cap saturates. Check a nonsaturated point as well.
        b=torch.tensor(2.,dtype=torch.float64,requires_grad=True)
        value,_=receiver.feedback_variance(d,v,b)
        assert torch.autograd.grad(value,b)[0]>0
        assert torch.isfinite(derivative)


@pytest.mark.parametrize('q',[3,8])
@pytest.mark.parametrize('variance',[1e-12,1e-4,1.,1e8])
def test_extrinsic_query_matches_row_orthogonal_identity_at_extreme_scales(q,variance):
    rng=np.random.default_rng(37)
    a=np.eye(8,dtype=np.complex128)[:q]
    y=rng.normal(size=(q,4))+1j*rng.normal(size=(q,4))
    prior=rng.normal(size=(2,2,2,4))+1j*rng.normal(size=(2,2,2,4))
    p=common.real_tensor(prior,'cpu')
    u,s,vh=np.linalg.svd(a,full_matrices=False)
    public=dict(a=data.block(a,'cpu'),y=torch.tensor(np.concatenate((y.real,y.imag)),dtype=torch.float32),
        uh=data.block(u.conj().T,'cpu'),vv=data.block(vh.conj().T,'cpu'),
        s=torch.tensor(s,dtype=torch.float32),noise=.3)
    query,v,_=receiver.linear_query(public,p,torch.tensor(variance),torch.tensor(0.))
    # Closed form for A A^H=I, independent of an implementation trace calculation.
    expected_v=(8/q)*.3+(8/q-1)*variance
    packed=prior.transpose(0,3,1,2).reshape(8,4)
    expected=packed+(8/q)*a.conj().T@(y-a@packed)
    actual=data.pack(query).numpy()
    np.testing.assert_allclose(actual[:8]+1j*actual[8:],expected,rtol=2e-6,atol=2e-6)
    assert float(v)==pytest.approx(expected_v,rel=2e-6)


def test_smooth_feedback_floor_keeps_beta_gradient_for_negative_residual():
    beta=torch.tensor(0.,requires_grad=True)
    value,_=receiver.feedback_variance(torch.tensor(-1.1686),torch.tensor(2.8889),beta)
    assert torch.autograd.grad(value,beta)[0]>0


def test_existing_prior_receipts_resume_without_json_local_error(tmp_path,monkeypatch):
    monkeypatch.setattr(data,'OUT',tmp_path)
    settings=copy.deepcopy(common.CONFIG['prior'])
    settings.update(train_samples=4,validation_samples=2,candidates_per_scene=2)
    monkeypatch.setitem(common.CONFIG,'prior',settings)
    folder=tmp_path/'data';folder.mkdir()
    for split in ('train','validation'):
        path=folder/f'prior_{split}.npy'
        np.save(path,np.ones((settings[f'{split}_samples'],16,16,16),np.complex64))
        (folder/f'prior_{split}.json').write_text(json.dumps(dict(samples=settings[f'{split}_samples'],
            seed_base=settings[f'{split}_seed'],candidates_per_scene=2,sha256=common.sha(path),
            physical_mean_element_power=1.)))
    before={p.name:common.sha(p) for p in folder.iterdir()}
    assert data.build_prior(time.time())==1.
    assert all(common.sha(folder/name)==value for name,value in before.items())


def test_pooled_nmse_and_mean_scene_nmse_are_distinct_and_scaled_physically():
    def row(truth,estimate,scale):
        labels=dict(x=torch.tensor([[[[[truth]]]],[[[[0.]]]]]).reshape(1,2,1,1,1),
                    active=torch.ones(1),physical_scale=scale)
        x=labels['x']*0; x[0,0]=estimate
        return receiver.metrics([(x,torch.ones(1))],labels)
    rows=[row(1.,2.,2.),row(10.,11.,2.)]
    result=receiver.summarize_rows(rows)
    assert result['error_energy']==8.
    assert result['truth_energy']==404.
    assert result['pooled_nmse']==pytest.approx(2/101)
    assert result['mean_scene_nmse']==pytest.approx(.505)


def test_mixed_conditions_are_not_correlated_with_snr():
    settings=common.CONFIG['receiver'];count=len(settings['conditions']['train'])*len(settings['snr_db'])
    actual={tuple(sorted(data.condition_for('train',i).items())) for i in range(count)}
    assert len(actual)==count


def test_estimated_frontend_never_reads_truth_or_oracle_fields(monkeypatch):
    from afdm_jadcedd.algorithm import phase_estimation_optimized as phase
    rng=np.random.default_rng(721)
    z=lambda shape:rng.normal(size=shape)+1j*rng.normal(size=shape)
    class PublicOnly(dict):
        def __getitem__(self,key):
            if key in ('a','noise','x','active'):raise AssertionError('Oracle field read: '+key)
            return super().__getitem__(key)
    values=PublicOnly(y=z((8,16,16)),pilot=z((8,20,16)),rho=.1)
    # Isolate the information boundary; actual phase estimation is exercised by
    # the independent physical-scene audit, not mocked there.
    monkeypatch.setattr(phase,'estimate',lambda inputs,controls:(dict(phase_slopes=np.zeros(20)),{}))
    public,record=data.prepare_public(values,.25,'cpu',phase_mode='estimated',noise_mode='estimated')
    assert public['channel_shape']==(20,2,16,16,16)
    assert not record['oracle_phase_supplied'] and not record['oracle_noise_supplied']
    assert public['physical_input'].observation is values['y']


def test_training_entry_requires_explicit_training_flag(monkeypatch):
    monkeypatch.setattr('sys.argv',['train'])
    with pytest.raises(SystemExit) as error:train.main()
    assert error.value.code==2


def test_physical_cases_use_configured_dimensions_and_resume_exactly(tmp_path,monkeypatch):
    settings=copy.deepcopy(common.CONFIG['receiver'])
    profiles=[dict(users=20,frames=8,activity_probability=.05),
        dict(users=40,frames=16,activity_probability=.1),
        dict(users=100,frames=24,activity_probability=.2)]
    settings.update(train_scenes=3,train_seed=202610199300001,snr_db=[0.],
        phase_mode='known',noise_mode='known')
    settings['conditions']['train']=profiles
    monkeypatch.setitem(common.CONFIG,'receiver',settings)
    monkeypatch.setattr(data,'OUT',tmp_path);monkeypatch.setattr(common,'OUT',tmp_path)
    first=data.build_cases('train',.25,time.time())
    second=data.build_cases('train',.25,time.time())
    assert first==second
    cases=data.Cases('train',.25,'cpu')
    for index,profile in enumerate(profiles):
        public,labels,info=cases[index]
        assert public['channel_shape']==(profile['users'],2,16,16,16)
        assert public['a'].shape==(2*profile['frames'],2*profile['users']*16)
        assert labels['x'].shape==public['channel_shape']
        assert info['condition']['activity_probability']==profile['activity_probability']


def test_layer_curve_uses_intermediate_outputs_of_one_model():
    class Fixture(torch.nn.Module):
        calls=0
        def forward(self,public,return_messages=False):
            self.calls+=1
            outputs=[(torch.full((2,2,1,1,1),i/10),torch.zeros(2)) for i in range(1,6)]
            messages=[dict(query=torch.zeros(2,2,1,1,1)) for _ in outputs]
            return outputs,[{} for _ in outputs],messages
    class Cases:
        device='cpu'
        def __len__(self):return 2
        def __getitem__(self,index):
            return {},dict(x=torch.ones(2,2,1,1,1),active=torch.tensor([1.,0.])),dict(seed=index,snr=0.)
    model=Fixture();result=receiver.evaluate(model,Cases())
    assert model.calls==2 and len(result['layer_summary'])==5
    assert result['layer_summary'][0]['pooled_nmse']==pytest.approx(.81)
    assert result['layer_summary'][-1]['pooled_nmse']==pytest.approx(.25)
