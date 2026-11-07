"""Freeze the independent white-network evaluation and check completed training."""
import os
from pathlib import Path
import shutil
import sys
import time

import psutil

from project import ROOT
from utils import read_json, write_json, sha256
from .receiver import verify, Receiver, NumericalReceiver, require

OUT = ROOT / 'result/snr_comparison/data/white_preconditioned_matched_1000_snr_20261104'
DENOISER = ROOT / 'result/channel_denoising/data/white_preconditioned_matched_20261104'
CLASSIFIER = ROOT / 'result/snr_comparison/data/white_preconditioned_classifier_matched_20261104'
CONFIG = ROOT / 'src/configs/candidates/GP_MP_white_preconditioned_matched_20261104.json'


def prepare():
    require(not (OUT / 'PLAN.json').exists() and not CONFIG.exists(), 'Preparation already exists')
    request = read_json(DENOISER / 'EVALUATION_PLAN.json')
    native = Path(request['native_output'])
    require(not native.exists(), 'Native output already exists')
    require(shutil.disk_usage(native.parent).free > 35 * 2**30, 'Need 35 GiB free output space')
    for proc in psutil.process_iter(['pid', 'cmdline']):
        command = ' '.join(proc.info['cmdline'] or [])
        if proc.pid != os.getpid() and proc.name().lower().startswith('python'):
            require(not ('training.' in command and ('white_activity_matched' in command or 'white_preconditioned_matched' in command)),
                    'A matching training process is still alive')
    basepath = ROOT / request['base_receiver_configuration']
    require(sha256(basepath) == request['base_receiver_configuration_sha256'], 'Base receiver changed')
    config = read_json(basepath)
    dc, cc = read_json(DENOISER / 'complete.json'), read_json(CLASSIFIER / 'complete.json')
    config.update(schema='white-matched-receiver-binding-v1', method='GP-MP',
                  classifier_policy='matched_white_mean_vI', first_epoch=dc['selected_epoch'],
                  classifier_epoch=cc['selected_epoch'],
                  classifier_training_binding=dict(first_sha256=dc['weight_sha256'], second_sha256=None),
                  limitations=['Historical research scenes; not untouched test data.',
                               'White-trained denoiser and its matched classifier; all numerical receiver controls unchanged.',
                               'Derivative-trace variance remains an approximation.'])
    paths = dict(first_checkpoint=DENOISER/'first_best.pt', evidence_checkpoint=CLASSIFIER/'evidence_best.pt',
                 first_training_record=DENOISER/'complete.json', first_training_specification=DENOISER/'specification.json',
                 classifier_training_record=CLASSIFIER/'complete.json', classifier_training_specification=CLASSIFIER/'specification.json',
                 classifier_execution_record=CLASSIFIER/'LAUNCH.json', classifier_history=CLASSIFIER/'history.json',
                 classifier_initialization=CLASSIFIER/'initialization.pt', base_receiver_configuration=basepath,
                 evaluation_plan=DENOISER/'EVALUATION_PLAN.json')
    for key, path in paths.items():
        config[key] = path.relative_to(ROOT).as_posix()
        config[key+'_sha256'] = sha256(path)
    verify(config)
    require(Receiver.infer is NumericalReceiver.infer, 'Numerical inference implementation changed')
    # The independent verifier must also reject controls and teacher mismatches.
    from copy import deepcopy
    for key in ('ep', 'classifier_training_binding'):
        bad = deepcopy(config)
        if key == 'ep': bad[key]['damping'] = .2
        else: bad[key]['first_sha256'] = '0' * 64
        try:
            verify(bad)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid binding accepted: ' + key)
    write_json(CONFIG, config)
    for key, target in (('input_manifest','INPUTS.json'), ('reference_manifest','REFERENCES.json')):
        path = ROOT / request[key]
        require(sha256(path) == request[key+'_sha256'], 'Changed input or reference manifest')
        shutil.copyfile(path, OUT / target)
    cases, refs = read_json(OUT/'INPUTS.json'), read_json(OUT/'REFERENCES.json')
    require(len(cases) == len(refs) == 6000, 'Wrong input/reference count')
    require([(c['scene'],c['index']) for c in cases] == [(s,i) for s in range(1000) for i in range(6)], 'Coverage mismatch')
    for case, ref in zip(cases, refs):
        require((case['scene'],case['index'],case['snr_db']) == (ref['scene'],ref['index'],ref['snr_db']), 'Unpaired reference')
        require(case['snr_db'] == [-4,-2,0,2,4,6][case['index']], 'SNR mismatch')
        known = ref['known_phase']
        require(sha256(known['pointer']) == known['pointer_sha256'], 'Reference pointer changed')
        p = Path(known['stem']).with_suffix('.json')
        require(sha256(p) == known['files'][str(p)], 'Reference result changed')
        row = read_json(p)
        require(row['scene'] == case['scene'] and row['index'] == case['index'] and row['input_files'] == case['files'], 'Reference inputs differ')
    assets = set(paths.values()) | {CONFIG, ROOT/config['prior_definition'], OUT/'INPUTS.json', OUT/'REFERENCES.json', ROOT/'FINAL.json', ROOT/'MAINLINE.json'}
    for folder in ('src/algorithm/STMP','src/algorithm/C_STMP','src/algorithm/C_STMP_retrained',
                   'src/algorithm/C_STMP_variance_em_20261025','src/evaluation/white_matched_20261105',
                   'src/networks','src/training/colored_preconditioned_20261024',
                   'src/training/colored_score_20261024','src/system'):
        assets.update((ROOT/folder).rglob('*.py'))
    assets.update(ROOT/p for p in ('src/utils.py','src/project.py','src/evaluation/metrics.py','src/evaluation/storage.py'))
    for key in ('reference_summary','reference_completion'):
        path = ROOT/request[key]
        require(sha256(path) == request[key+'_sha256'], 'Changed reference summary/completion')
        assets.add(path)
    plan = dict(schema='white-matched-main-snr-execution-v1',created_unix=time.time(),planned=6000,
                configuration=str(CONFIG),receiver_configuration=config,native_directory=str(native),
                assets={str(p):sha256(p) for p in sorted(assets)},snrs=[-4,-2,0,2,4,6],
                runtime=dict(device='cuda',max_workers=2,threads_per_worker=2,worker_peak_budget_gib=2.5,
                             minimum_free_ram_gib=1.25,gpu_budget_gib_per_worker=6.0,minimum_free_gpu_gib=1.0,
                             input_timeout_seconds=7200,total_timeout_seconds=14*86400,fresh_process_per_input=True),
                preflight_position=0,automatic_retry=False,phase_mode='known',noise_mode='estimated',
                scoring='Saved predictions rescored; channel/activity truth only after inference.',
                finite_iteration_limit_outputs_retained=True,mainline_changed=False,
                authorization='User requested launch in this chat; saved EVALUATION_PLAN.json fixes scientific scope.')
    write_json(OUT/'PLAN.json',plan)
    write_json(OUT/'PLAN_HASH.json',dict(sha256=sha256(OUT/'PLAN.json')))
    native.mkdir()
    check = dict(status='PASS',checked_unix=time.time(),inputs=6000,paired_known_phase_references=6000,
                 denoiser_epochs=200,classifier_epochs=100,first_epoch=config['first_epoch'],classifier_epoch=config['classifier_epoch'],
                 selected_weights_and_teacher_verified=True,training_processes_exited=True,
                 unchanged_numerical_infer=True,invalid_binding_rejected=True,full_inference_preflight_pending=True)
    write_json(OUT/'PREPARATION_CHECK.json',check)
    write_json(CLASSIFIER/'CLASSIFIER_COMPLETION_CHECK.json',dict(check,weight_sha256=cc['weight_sha256'],
               first_sha256=cc['first_sha256'],complete_sha256=sha256(CLASSIFIER/'complete.json')))
    print(check,flush=True)


if __name__ == '__main__':
    prepare()
