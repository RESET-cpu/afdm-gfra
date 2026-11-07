"""Freeze input pairing, CPU scheduling, and unchanged baseline dependencies."""
import datetime
import math
import shutil

import psutil

from project import ROOT
from utils import read_json, sha256, write_json
from evaluation.offgrid_budget_20261105.run import OUT, NATIVE, SNRS


def prepare():
    if OUT.exists() or NATIVE.exists():
        raise FileExistsError('Independent output already exists; inspect before proceeding')
    main = ROOT / 'result/snr_comparison/data/c_stmp_variance_em_1000_snr_m4_p6_20261025'
    manifest = main / 'INPUTS.json'
    if sha256(manifest) != '9b5c367571a0d3773420217d158c442947268151797bfb0bfa77142cb1bfb571':
        raise ValueError('Main-SNR input manifest changed')
    cases = read_json(manifest)
    assert [(c['scene'],c['index'],c['snr_db']) for c in cases] == [
        (s,i,v) for s in range(1000) for i,v in enumerate(SNRS)]
    audit = read_json(main / 'BASELINE_AUDIT.json')
    assert audit['status'] == 'PASS'
    refs = sorted([r for r in audit['references'] if r['method']=='offgrid_sbl'],key=lambda r:(r['scene'],r['index']))
    assert [(r['scene'],r['index']) for r in refs] == [(c['scene'],c['index']) for c in cases]
    selection = ROOT / 'result/snr_comparison/data/c_stmp_retrained_1000_20261025/BASELINE_SELECTION.json'
    entry = read_json(selection)
    assert entry['status'] == 'ADOPTED_BY_USER'
    for key in ('adoption','policy','readout_implementation'):
        assert sha256(entry[key]) == entry[key+'_sha256']
    configurations = {str(n):f'src/configs/candidates/offgrid_sbl_budget{n}_20261105.json' for n in [13,25]}
    base = read_json(ROOT/'src/configs/final/offgrid_sbl.json')
    base_solver = base['methods']['offgrid_sbl']['solver']
    assert base_solver['iterations'] == 120
    for count,path in configurations.items():
        config = read_json(ROOT/path)
        assert math.ceil((2*41000/30000)/config['solver_changes']['doppler_step'])+1 == int(count)
        assert config['unchanged_iterations'] == 120 and config['delay_points'] == 112
        assert config['activity_policy_sha256'] == entry['policy_sha256']
    OUT.mkdir(parents=True); NATIVE.mkdir(parents=True)
    shutil.copyfile(manifest,OUT/'INPUTS.json')
    write_json(OUT/'REFERENCES.json',refs)
    paths = {ROOT/p for p in read_json(ROOT/'src/configs/final/baseline_sources.json')['sha256']}
    paths.update(ROOT/p for p in configurations.values())
    paths.update((ROOT/'src/evaluation/offgrid_budget_20261105').glob('*.py'))
    paths.update(ROOT/p for p in ['FINAL.json','MAINLINE.json','src/project.py','src/utils.py',
        'src/evaluation/metrics.py','src/evaluation/storage.py','src/configs/final/offgrid_sbl.json',
        'src/configs/final/offgrid_readout_policy.json','src/configs/final/baseline_noise.json',
        'src/configs/final/baseline_sources.json','src/configs/training/white_preconditioned_matched_20261104.json'])
    paths.update([selection,OUT/'INPUTS.json',OUT/'REFERENCES.json',main/'BASELINE_SUMMARY.json',
                  main/'BASELINE_AUDIT.json'])
    paths.update(__import__('pathlib').Path(entry[k]) for k in ['adoption','policy','readout_implementation'])
    affinity=[cpu for cpu in psutil.Process().cpu_affinity() if cpu>=4]
    assert affinity
    plan=dict(schema='offgrid-search-budgets-main-snr-cpu-v1',
        created_local=datetime.datetime.now().astimezone().isoformat(),
        authorization='User: 那两档off-grid SBL用V CPU来跑吧',
        target_assumption='Local CPU; no separately connected V CPU host found. Clarification offered; no remote upload.',
        phase_mode='known',noise_mode='estimated',scenes=1000,snrs_db=SNRS,
        planned_new_inferences=12000,reference_inferences_reused=6000,
        input_manifest=str(OUT/'INPUTS.json'),native_output=str(NATIVE),
        configurations=configurations,base_solver=base_solver,
        baseline_selection=selection.relative_to(ROOT).as_posix(),
        baseline_summary=(main/'BASELINE_SUMMARY.json').relative_to(ROOT).as_posix(),
        runtime=dict(device='cpu',max_workers=4,threads_per_worker=1,cpu_affinity=affinity,
            priority='BELOW_NORMAL',worker_peak_budget_gib=1.8,minimum_free_ram_gib=1.5,
            fresh_process_per_input=True,input_timeout_seconds=7200,total_timeout_seconds=14*86400,
            automatic_retry=False,cuda_visible_devices='',training_unchanged=True),
        preflight=dict(position=0,budgets=[7,13,25],original_budget_reproduction=True,
            relative_numeric_tolerance=1e-7,absolute_error_tolerance=1e-8,decisions='exact',
            new_budgets='Finite full-budget outputs and resource checks; no performance selection',
            output_not_reused_in_formal_results=True),
        metrics='Full channel error energy / active signal energy NMSE; all-device AER, misses, false alarms and iteration caps.',
        limitations=['Doppler grid density and candidate budgets change together.',
            'The adopted main-SNR activity thresholds transfer unchanged; no new calibration claim.',
            'Historical research scenes are not an untouched independent test set.',
            'No performance-based omission or automatic retries; finite iteration-limit outputs are retained.',
            'Concurrent CPU wall times are not controlled hardware-comparison evidence.'],
        assets={p.relative_to(ROOT).as_posix():sha256(p) for p in sorted(paths)})
    write_json(OUT/'PLAN.json',plan)
    write_json(OUT/'PLAN_HASH.json',dict(sha256=sha256(OUT/'PLAN.json')))
    write_json(OUT/'PREPARED.json',dict(status='PASS',paired_inputs=6000,new_inferences=12000,
        grid_points=[13,25],iterations=120,activity_thresholds_unchanged=True,
        disk_free_bytes=shutil.disk_usage(NATIVE).free,available_ram_gib=psutil.virtual_memory().available/2**30,
        inference_started=False))
    print('Prepared 12000 CPU inferences on exactly 6000 saved inputs; no inference launched.',flush=True)


if __name__=='__main__':
    prepare()
