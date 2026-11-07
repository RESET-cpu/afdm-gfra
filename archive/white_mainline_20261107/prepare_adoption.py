"""Archive old entry bindings, then adopt the verified white-only implementation."""
from copy import deepcopy
from pathlib import Path
import shutil
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from utils import read_json, write_json, sha256

HERE=Path(__file__).resolve().parent
OUT=ROOT/'result/white_followup_20261107'
REQUEST='这样吧，你先把代码整理一下，把有色噪声部分全部退出主线，数据暂时先不用动，然后开始补跑后续实验的内容，跑完一个替换一个'


def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    request=dict(schema='white-mainline-followup-request-v1',created_unix=time.time(),
        author_request=REQUEST,authorization='Direct author request in this chat on 2026-11-07',
        old_data_policy='Preserve all existing model, input, prediction, report and source data in place.',
        code_policy='White-only default registry; preserve frozen historical implementations and catalog for replay.',
        sequence=['channel_denoising','pilot_frames','user_count','activity_probability','cross_channel'],
        per_condition_scenes=500,selection='All original scene IDs 0-499, without outcome selection.',
        scientific_controls='Adopted white weights and matched classifier; FP32; TF32/benchmark off; original phase frontend once and fixed; damping .4; 60-600 iterations; threshold .5.',
        new_receiver_inferences={'pilot_frames':10000,'user_count':8000,'activity_probability':8000,'cross_channel':9000},
        receiver_reuse='Use completed main-SNR white known/EP and SBL13/25 only when raw input files and scientific bindings match.',
        denoising_channel_queries=12000,denoising_inputs=3000,
        sbl_policy='Prior authorized 13/25 budgets, frozen readout and remaining numerical controls; CPU.',
        user_count_policy='New white protocol uses beta .4 for every scene and K, including K80/scene372 and all K100; no isolated replacement. Historical C1 remains recorded as history, not retroactively resolved.',
        adoption='Each complete stage must pass full rescore, source/output hashes, coverage, process-exit verification before figure and necessary manuscript update; do not start next stage before adoption.',
        failure_policy='Preserve new failures and partial results; no automatic unconditional inference retries.',
        no_extra_training=True,convergence_and_ablation_not_restarted=True,
        material_passport=dict(origin_skill='academic-research-suite/experiment-agent',origin_mode='run',
                              verification_status='PENDING',version_label='white_followup_20261107'))
    if not (OUT/'REQUEST.json').exists():write_json(OUT/'REQUEST.json',request)
    targets=[ROOT/'FINAL.json',ROOT/'src/configs/algorithms.json',ROOT/'README.md',ROOT/'src/README.md',
             ROOT/'src/algorithm/README.md',ROOT/'src/evaluation/README.md',ROOT/'run_experiments.py']
    targets+=list((ROOT/'src/configs/experiments').glob('*.json'))
    hashes={}
    for path in targets:
        dest=HERE/'before'/path.relative_to(ROOT)
        if not dest.exists():
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
        hashes[str(path.relative_to(ROOT))]=sha256(dest)
    if not (HERE/'BEFORE_HASHES.json').exists():write_json(HERE/'BEFORE_HASHES.json',hashes)
    return request


def adopt():
    validation=read_json(HERE/'VALIDATION.json')
    assert validation['status']=='PASS'
    for path,digest in validation['new_sources'].items():assert sha256(ROOT/path)==digest
    previous=read_json(HERE/'before/src/configs/algorithms.json')
    history=ROOT/'src/configs/historical/algorithms_colored_20261107.json'
    if not history.exists():
        history.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(HERE/'before/src/configs/algorithms.json',history)
    catalog=deepcopy(previous)
    catalog['algorithms'].pop('pretrained_colored_first')
    catalog['algorithms'].pop('C_STMP')
    config='src/configs/candidates/GP_MP_white_preconditioned_matched_20261104.json'
    phase='src/configs/candidates/GP_MP_white_phase_frontend_marginal_20261106.json'
    c=read_json(ROOT/config)
    assets=[c[k] for k in c if k+'_sha256' in c]
    assets+= [str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'src/algorithm/GP_MP').glob('*.py')]
    common=dict(kind='receiver',group='GP_MP',backend='device',
                device_modules=['model.network','evidence.network'],assets=assets)
    catalog['algorithms']['GP_MP']=dict(common,label='GP-MP (white-trained, known phase)',
        factory='algorithm.GP_MP.receiver:Receiver',path_kwargs={'configuration':config})
    catalog['algorithms']['GP_MP_EP']=dict(common,label='GP-MP-EP (white-trained, estimated phase)',
        factory='algorithm.GP_MP.phase_receiver:PhaseReceiver',path_kwargs={'configuration':phase},
        estimates_phase_internally=True)
    catalog['algorithms']['C_STMP']=dict(deepcopy(catalog['algorithms']['GP_MP']),alias_of='GP_MP',
        label='GP-MP (historical identifier; white mainline)')
    catalog['algorithms']['pretrained_white_first']=dict(kind='denoiser',group='denoising',
        label='GP-MP white-trained conditional mean',backend='device',factory='algorithm.GP_MP.denoising:Denoiser',
        path_kwargs={'configuration':config},device_modules=['network'],assets=assets)
    catalog['current_mainline']={'known_phase':'GP_MP','estimated_phase':'GP_MP_EP','denoiser':'pretrained_white_first',
        'historical_catalog':str(history.relative_to(ROOT)).replace('\\','/'),'adoption':'archive/white_mainline_20261107/ADOPTION.json'}
    write_json(ROOT/'src/configs/algorithms.json',catalog)
    for name in ['snr_comparison','pilot_frames','user_count','activity_probability','cross_channel']:
        path=ROOT/f'src/configs/experiments/{name}.json';spec=read_json(path)
        spec.update(methods=['GP_MP','STMP','offgrid_sbl','gnn','gamp','somp'],reference_method='GP_MP',
                    include_stmp=True,phase_mode='known',noise_mode='estimated')
        # Preserve stored historical plans; these defaults only affect newly created plans.
        if name=='snr_comparison':spec['values']=[-4,-2,0,2,4,6]
        else:spec['scenes']=500
        write_json(path,spec)
    path=ROOT/'src/configs/experiments/channel_denoising.json';spec=read_json(path)
    spec['methods']=[('pretrained_white_first' if m=='pretrained_colored_first' else m) for m in spec['methods']]
    spec['scenes']=500;spec['reference_method']='pretrained_white_first';write_json(path,spec)
    final=dict(schema='afdm-white-mainline-20261107-v1',status='VERIFIED',entrypoint='run_experiments.py',
        algorithm='src/algorithm/GP_MP',algorithm_catalog='src/configs/algorithms.json',
        known_phase='GP_MP',estimated_phase='GP_MP_EP',inference_config=config,phase_config=phase,
        checkpoint=c['first_checkpoint'],checkpoint_sha256=c['first_checkpoint_sha256'],
        evidence_checkpoint=c['evidence_checkpoint'],evidence_checkpoint_sha256=c['evidence_checkpoint_sha256'],
        prior_mainline='archive/white_mainline_20261107/before/FINAL.json',original_mainline_preserved='MAINLINE.json',
        historical_catalog=str(history.relative_to(ROOT)).replace('\\','/'),
        validation='archive/white_mainline_20261107/VALIDATION.json',
        followup_request='result/white_followup_20261107/REQUEST.json',
        numerical_settings_preserved=True,old_data_unchanged=True,
        prior_DU_and_STMP_bindings='src/configs/final/models.json')
    write_json(ROOT/'FINAL.json',final)
    changed=[ROOT/'FINAL.json',ROOT/'src/configs/algorithms.json']+[ROOT/f'src/configs/experiments/{n}.json' for n in ['channel_denoising','snr_comparison','pilot_frames','user_count','activity_probability','cross_channel']]
    write_json(HERE/'ADOPTION.json',dict(status='PASS',adopted_unix=time.time(),
        validation_sha256=sha256(HERE/'VALIDATION.json'),request_sha256=sha256(OUT/'REQUEST.json'),
        files={str(p.relative_to(ROOT)):sha256(p) for p in changed},historical_data_untouched=True))


if __name__=='__main__':
    prepare()
    if '--adopt' in sys.argv:adopt()
