"""Add verified SBL budgets to the saved main-SNR plotting snapshot."""
from pathlib import Path
from copy import deepcopy
import hashlib
import json
import math
import shutil

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
CONFIG = ROOT / 'src/configs/plots/manuscript.json'
BATCH = ROOT / 'result/snr_comparison/data/offgrid_search_budgets_1000_cpu_20261105'
DEST = ROOT / 'result/snr_comparison/figures/main_snr_sbl_budgets_20261105/PLOT_DATA.json'

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def main():
    assert not (OUT/'BEFORE_HASHES.json').exists(), 'Preserve the original snapshot'
    config = read(CONFIG)
    cfg = config['figures']['snr_comparison']
    source = ROOT/cfg['source']
    assert sha(source) == cfg['source_sha256']
    original = read(source)
    completion = read(BATCH/'COMPLETION.json')
    verification = read(BATCH/'verification/COMPLETION_VERIFICATION.json')
    assert completion['status'] == verification['status'] == 'PASS'
    assert completion['new_inferences'] == 12000 and completion['saved_arrays_rescored']
    assert sha(BATCH/'SUMMARY.json') == completion['summary_sha256']
    for name in ('SUMMARY.json','PAIRED_CASES.csv','COMPLETION.json'):
        assert sha(BATCH/name) == verification['files'][name]
    summary = read(BATCH/'SUMMARY.json')
    assert summary['status'] == 'COMPLETE' and summary['scenes'] == 1000
    for r in summary['rows']:
        assert r['scenes'] == 1000
        assert r['active']+r['inactive'] == 40000
        assert math.isclose(r['nmse_db'],10*math.log10(r['full_error']/r['signal_energy']),abs_tol=1e-12)
        assert r['aer'] == (r['misses']+r['false_alarms'])/40000
        if r['budget'] == 7:
            old = next(x for x in original['rows'] if x['method']=='offgrid_sbl' and x['snr_db']==r['snr_db'])
            for key in ('scenes','misses','false_alarms','active','inactive','nmse_db','aer','full_error','signal_energy'):
                assert math.isclose(old[key],r[key],rel_tol=1e-12,abs_tol=1e-12), key

    files = [CONFIG, ROOT/'paper/C-STMP/sections/06_simulation_results.tex',
             ROOT/'paper/C-STMP/main.pdf', ROOT/'paper/C-STMP/main_full.pdf',
             ROOT/'paper/C-STMP/docs/REVIEW_DECISIONS.md']
    files += list((ROOT/'paper/C-STMP/figures').glob('*.pdf'))
    files += [ROOT/'paper/C-STMP/figures/snr_comparison.png']
    files += [ROOT/'FINAL.json', ROOT/'MAINLINE.json']
    before = {}
    for path in files:
        if not path.exists(): continue
        relative = path.relative_to(ROOT)
        copy = OUT/'before'/relative
        copy.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,copy)
        before[relative.as_posix()] = sha(path)
    save(OUT/'BEFORE_HASHES.json',before)

    data = deepcopy(original)
    additions = []
    for budget,marker,linestyle in ((13,'o','-.'),(25,'v',':')):
        method = f'offgrid_sbl_{budget}'
        cfg['labels'][method] = f'Off-grid SBL ({budget})'
        cfg['styles'][method] = dict(cfg['styles']['offgrid_sbl'],marker=marker,linestyle=linestyle)
        for r in summary['rows']:
            if r['budget'] != budget: continue
            additions.append(dict(r,method=method,parameters={'snr_db':r['snr_db']},
                miss_rate=r['misses']/r['active'],false_alarm_rate=r['false_alarms']/r['inactive']))
    assert len(additions)==12
    cfg['labels']['offgrid_sbl'] = 'Off-grid SBL (7)'
    order = ['C_STMP','C_STMP_phase_frontend_marginal_20261104','STMP',
             'offgrid_sbl','offgrid_sbl_13','offgrid_sbl_25','gnn','gamp','somp']
    data['methods'] = cfg['methods'] = cfg['legend_order'] = order
    data['rows'].extend(additions)
    data['metadata']['sbl_budget_comparison'] = dict(
        source=(BATCH/'SUMMARY.json').relative_to(ROOT).as_posix(),
        source_sha256=sha(BATCH/'SUMMARY.json'),
        completion=(BATCH/'COMPLETION.json').relative_to(ROOT).as_posix(),
        verification=(BATCH/'verification/COMPLETION_VERIFICATION.json').relative_to(ROOT).as_posix(),
        original_snapshot=source.relative_to(ROOT).as_posix(),original_snapshot_sha256=sha(source),
        doppler_points=[7,13,25],delay_centers=112,retained_candidates_per_user=[12,24,48],
        offset_candidates_per_iteration=[48,96,192],max_iterations=120,
        grid_and_candidates_changed_together=True,activity_thresholds_transferred_without_refitting=True,
        all_finite_iteration_cap_outputs_retained=True)
    save(DEST,data)
    cfg['source'] = DEST.relative_to(ROOT).as_posix()
    cfg['source_sha256'] = sha(DEST)
    cfg['point_count'] = 108
    panel = cfg['panel_config']
    panel['input'] = cfg['source']
    panel['selection']['methods'] = order
    panel['labels'] = deepcopy(cfg['labels'])
    panel['styles'] = deepcopy(cfg['styles'])
    panel['axes']['aer']['limits'] = [0.0001,0.02]
    save(CONFIG,config)
    save(OUT/'DATA_VALIDATION.json',dict(status='PASS',original_rows_preserved=len(original['rows']),
        added_rows=len(additions),points=108,baseline_7_verified_against_completed_comparison=True,
        complete_1000_scenes_per_snr=True,summary_sha256=sha(BATCH/'SUMMARY.json'),
        plot_snapshot_sha256=sha(DEST),inference_started=False,training_started=False))
    print('Prepared 9 methods, 6 SNRs, 2 metrics: 108 verified plot points.')

if __name__=='__main__':
    main()
