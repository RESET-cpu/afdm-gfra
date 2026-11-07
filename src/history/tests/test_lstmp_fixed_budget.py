"""Continuation must preserve scene identities, consumed order and Adam state."""
import copy
import json
import time
from pathlib import Path
import numpy as np
import torch
from experiments.lstmp_candidate_20261019 import common, data, fixed_budget


def fixed_config():
    path=Path(__file__).resolve().parents[1]/'experiments/lstmp_candidate_20261019/reuse_50000_fixed_budget.json'
    return json.loads(path.read_text(encoding='utf-8'))


def test_fixed_budget_includes_all_previously_consumed_scenes_once(monkeypatch):
    config=fixed_config()
    monkeypatch.setattr(fixed_budget,'CONFIG',config)
    indices=config['receiver']['case_sources']['train']['indices']
    order=fixed_budget.epoch_order(indices,1,1)
    original=np.random.default_rng(config['seed']+101).permutation(12000)
    visited=np.asarray(indices)[order]
    np.testing.assert_array_equal(visited[:1981],original[:1981])
    assert len(set(visited))==4800
    assert not set(visited[:1981]) & set(visited[1981:])
    np.testing.assert_array_equal(np.bincount(visited%24),np.full(24,200))
    assert 4800*sum(fixed_budget.epochs_for_depth(d) for d in range(1,6))==57600
    assert not fixed_budget.plateau_reached(100,1000)
    for depth,epoch in [(1,2),(2,1),(5,4)]:
        later=fixed_budget.epoch_order(indices,depth,epoch)
        assert sorted(later)==list(range(4800))
        np.testing.assert_array_equal(later,fixed_budget.epoch_order(indices,depth,epoch))


def test_read_only_pool_subset_retains_original_seed_and_observation(tmp_path,monkeypatch):
    settings=copy.deepcopy(common.CONFIG['receiver'])
    settings.update(train_scenes=4,train_seed=202610199600001,snr_db=[0.],generation_workers=1,
                    phase_mode='known',noise_mode='known')
    settings['conditions']['train']=[dict(users=20,frames=8,activity_probability=.05)]
    source=tmp_path/'old';target=tmp_path/'new'
    monkeypatch.setitem(common.CONFIG,'receiver',settings)
    monkeypatch.setattr(data,'OUT',source);monkeypatch.setattr(common,'OUT',source)
    original=data.build_cases('train',.25,time.time())
    source_receipt=source/'data/receiver_train.json'
    original_hash=common.sha(source_receipt)
    original_cases=data.Cases('train',.25,'cpu')
    expected=original_cases[3]
    settings['train_scenes']=2
    settings['case_sources']={'train':dict(run_directory=str(source),pool_count=4,
        receipt_sha256=original_hash,indices=[3,1])}
    monkeypatch.setattr(data,'OUT',target);monkeypatch.setattr(common,'OUT',target)
    selected=data.build_cases('train',.25,time.time())
    cases=data.Cases('train',.25,'cpu')
    public,labels,info=cases[0]
    assert len(cases)==2 and info['source_pool_index']==3
    assert info['seed']==settings['train_seed']+3
    torch.testing.assert_close(public['y'],expected[0]['y'],rtol=0,atol=0)
    torch.testing.assert_close(labels['x'],expected[1]['x'],rtol=0,atol=0)
    assert set(selected['files'])=={'train_0003.npz','train_0001.npz'}
    assert common.sha(source_receipt)==original_hash
    assert all(common.sha(source/'data/receiver'/name)==digest for name,digest in original['files'].items())
    assert not (target/'data/receiver').exists()


def test_continuation_copies_optimizer_and_partial_epoch_without_touching_source(tmp_path,monkeypatch):
    source=tmp_path/'old';target=tmp_path/'new'
    folder=source/'checkpoints/depth_1';folder.mkdir(parents=True)
    config=fixed_config();previous=copy.deepcopy(config)
    previous['receiver']['train_scenes']=6
    previous['receiver'].pop('case_sources')
    common.save_json(source/'MANIFEST.json',dict(configuration=previous))
    original_order=np.random.default_rng(config['seed']+101).permutation(6).tolist()
    first=original_order[:2]+original_order[3:5]
    config['receiver']['train_scenes']=4
    config['receiver']['case_sources']['train']['indices']=sorted(first)
    config['receiver']['first_epoch_pool_indices']=first
    parameter=torch.nn.Parameter(torch.tensor([.2,.5]))
    optimizer=torch.optim.Adam([parameter],lr=.01)
    parameter.square().sum().backward();optimizer.step()
    state=dict(state={'example':parameter.detach().clone()},optimizer=optimizer.state_dict(),
        depth=1,epoch=1,cursor=2,steps=2,samples=2,loss_sum=1.75,best=.7,history=[],stale=0,selected_epoch=0)
    torch.save(state,folder/'last.pt');torch.save(dict(state=state['state'],epoch=0),folder/'best.pt')
    common.save_json(folder/'initial_validation.json',dict(synthetic_fixture=True))
    config['continuation']=dict(source_run=str(source),source_manifest_sha256=common.sha(source/'MANIFEST.json'),
        checkpoint_sha256=common.sha(folder/'last.pt'),completed_updates=2)
    before={p.name:common.sha(p) for p in folder.iterdir()}
    monkeypatch.setattr(fixed_budget,'OUT',target);monkeypatch.setattr(fixed_budget,'CONFIG',config)
    fixed_budget.prepare_continuation()
    copied=torch.load(target/'checkpoints/depth_1/last.pt',map_location='cpu',weights_only=False)
    torch.testing.assert_close(copied,state,rtol=0,atol=0)
    fixed_budget.prepare_continuation()
    assert all(common.sha(folder/name)==digest for name,digest in before.items())
    receipt=json.loads((target/'CONTINUATION.json').read_text())
    assert receipt['optimizer_state_preserved'] and receipt['consumed_prefix_preserved']
