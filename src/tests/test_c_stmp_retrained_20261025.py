"""Binding checks for the completed new classifier; no receiver performance claims."""
from copy import deepcopy
import pytest
from project import ROOT
from utils import read_json
from algorithm.C_STMP_retrained.configuration import verify
from algorithm.C_STMP_retrained.receiver import Receiver
from algorithm.C_STMP.receiver import Receiver as PreviousReceiver

PATH=ROOT/'src/configs/candidates/C_STMP_retrained_20261025.json'


def test_completed_same_teacher_classifier_and_unchanged_equations():
    c,hashes=verify(PATH)
    assert c['classifier_epoch']==90
    assert c['classifier_training_binding']['first_sha256']==hashes['first_checkpoint']
    assert c['classifier_training_binding']['second_sha256'] is None
    old=read_json(ROOT/'src/configs/candidates/C_STMP_20261024.json')
    for key in ('ep','variance_estimator','scale','decision_threshold','site_damping','initialization','batch_size'):
        assert c[key]==old[key]
    assert Receiver.infer is PreviousReceiver.infer


@pytest.mark.parametrize('key,value',[
    ('classifier_epoch',100),('classifier_policy','frozen_legacy_teacher'),
    ('decision_threshold',.6),('classifier_training_record_sha256','0'*64)])
def test_reject_misbound_checkpoint_or_changed_controls(key,value):
    c=read_json(PATH);c[key]=value
    with pytest.raises(ValueError):verify(c)


def test_reject_old_teacher_binding():
    c=read_json(PATH)
    c['classifier_training_binding']=read_json(ROOT/'src/configs/candidates/C_STMP_20261024.json')['classifier_training_binding']
    with pytest.raises(ValueError,match='provenance'):verify(c)
