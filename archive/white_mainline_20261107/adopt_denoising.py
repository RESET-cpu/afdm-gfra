"""Prepare the verified denoising figure replacement, preserving prior assets."""
from copy import deepcopy
from pathlib import Path
import shutil
import sys
import time
import numpy as np
import psutil

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from utils import read_json,write_json,sha256
from evaluation.white_followup_20261107.denoising import DEST,paired_inputs,PLOT,verify_plan

CHECK=ROOT/'paper/C-STMP/checks/white_denoising_adopted_20261107'
FIG=ROOT/'result/channel_denoising/figures/white_mainline_500_20261107'
CONFIG=ROOT/'src/configs/plots/manuscript.json'


def main():
    completion=read_json(DEST/'COMPLETION.json')
    assert completion['status']=='PASS'
    assert sha256(DEST/'SUMMARY.json')==completion['summary_sha256']
    assert sha256(DEST/'OUTPUT_HASHES.json')==completion['output_hashes_sha256']
    summary=read_json(DEST/'SUMMARY.json');assert summary['status']=='VERIFIED'
    assert (summary['scenes'],summary['inputs'],summary['channel_queries'])==(500,3000,12000)
    start=read_json(DEST/'START.json')
    try:
        p=psutil.Process(start['pid'])
        assert abs(p.create_time()-start['created_unix'])>.01, 'Coordinator still alive'
    except psutil.NoSuchProcess:pass
    assert not (DEST/'RUNNING.lock').exists()
    assert not (DEST/'FAILURE.json').exists()
    plan=verify_plan(DEST)
    for path,digest in read_json(DEST/'OUTPUT_HASHES.json').items():assert sha256(path)==digest
    CHECK.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True)
    targets=[CONFIG,ROOT/'src/evaluation/plots/manuscript/receiver.py',
             ROOT/'paper/C-STMP/main.pdf',ROOT/'paper/C-STMP/main_full.pdf',
             ROOT/'paper/C-STMP/figures/learned_receiver.pdf',ROOT/'paper/C-STMP/figures/channel_denoising.pdf',
             ROOT/'paper/C-STMP/sections/06_simulation_results.tex']
    hashes={}
    for p in targets:
        dst=CHECK/'before'/p.relative_to(ROOT)
        if not dst.exists():dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
        hashes[str(p.relative_to(ROOT))]=sha256(dst)
    protected=list((ROOT/'paper/C-STMP/sections').glob('*'))+list((ROOT/'paper/C-STMP/figures').glob('*.pdf'))
    protected=[p for p in protected if p not in targets and p.is_file()]
    write_json(CHECK/'BEFORE.json',dict(changed=hashes,protected={str(p.relative_to(ROOT)):sha256(p) for p in protected}))
    raw=read_json(PLOT);new=deepcopy(raw)
    new['rows']=[r for r in raw['rows'] if r['method']!='pretrained_colored_first']+summary['rows']
    new['methods']=[m.replace('pretrained_colored_first','pretrained_white_first') for m in raw['methods']]
    new['metadata']=dict(status='VERIFIED',source_summary=str(DEST/'SUMMARY.json'),
        source_summary_sha256=sha256(DEST/'SUMMARY.json'),source_completion=str(DEST/'COMPLETION.json'),
        source_completion_sha256=sha256(DEST/'COMPLETION.json'),
        prior_plot=str(PLOT),prior_plot_sha256=sha256(PLOT),historical_baseline_metadata=raw['metadata'],
        replacement='Only the GP-MP denoising curve; all eight other curves copied without changing any row.',
        phase_mode='not_applicable',noise_mode='known',scenes=500,channel_queries=12000,
        limitations=summary['limitations'])
    assert len(new['rows'])==54
    assert new['rows'][:48]==[r for r in raw['rows'] if r['method']!='pretrained_colored_first']
    write_json(FIG/'PLOT_DATA.json',new)
    _,query,identities=paired_inputs(0,plan['scale'])
    with np.load(DEST/'scenes/scene000.npz',allow_pickle=False) as z:estimate=z['estimate']
    with (FIG/'scene000_example.npz').open('xb') as f:
        np.savez_compressed(f,query=query.reshape(6,4,16,16,16),estimate=estimate.reshape(6,4,16,16,16))
    write_json(FIG/'EXAMPLE.json',dict(scene=0,device_index=0,variance_index=3,antennas=[0,1,2],
        saved_prediction_sha256=sha256(DEST/'scenes/scene000.npz'),inputs=identities,
        example_sha256=sha256(FIG/'scene000_example.npz'),selection='Same fixed illustrative selection as the preceding figure.'))
    cfg=read_json(CONFIG);c=cfg['figures']['channel_denoising']
    c['source']=str((FIG/'PLOT_DATA.json').relative_to(ROOT)).replace('\\','/')
    c['source_sha256']=sha256(FIG/'PLOT_DATA.json')
    for k in ('styles','labels'):c[k]['pretrained_white_first']=c[k].pop('pretrained_colored_first')
    for k in ('methods','legend_order'):c[k]=[m.replace('pretrained_colored_first','pretrained_white_first') for m in c[k]]
    old_example='result/channel_denoising/data/colored_first_500_20261025_v2/scene000_predictions.npz'
    cfg['method_sources'].pop(old_example)
    cfg['method_sources'][str((FIG/'scene000_example.npz').relative_to(ROOT)).replace('\\','/')]=sha256(FIG/'scene000_example.npz')
    write_json(CONFIG,cfg)
    p=ROOT/'src/evaluation/plots/manuscript/receiver.py';text=p.read_text(encoding='utf-8')
    text=text.replace("SOURCE=ROOT/'result/channel_denoising/data/colored_first_500_20261025_v2'", "SOURCE=ROOT/'result/channel_denoising/figures/white_mainline_500_20261107'")
    text=text.replace("SAVED=SOURCE/'scene000_predictions.npz'", "SAVED=SOURCE/'scene000_example.npz'")
    p.write_text(text,encoding='utf-8')
    p=ROOT/'paper/C-STMP/sections/06_simulation_results.tex';text=p.read_text(encoding='utf-8')
    old='''Figs.~\\ref{fig:cstmp-convergence} and~\\ref{fig:cstmp-snr}
and Table~\\ref{tab:activity-evidence}; GP-MP-EP in Fig.~\\ref{fig:cstmp-snr}
uses the same networks. The GP-MP results in Fig.~\\ref{fig:cstmp-denoising}
and Figs.~\\ref{fig:cstmp-pilots}--\\ref{fig:cstmp-cross} use earlier checkpoints'''
    newtext='''Figs.~\\ref{fig:cstmp-denoising}--\\ref{fig:cstmp-snr}
and Table~\\ref{tab:activity-evidence}; GP-MP-EP in Fig.~\\ref{fig:cstmp-snr}
uses the same networks. The GP-MP results in
Figs.~\\ref{fig:cstmp-pilots}--\\ref{fig:cstmp-cross} use earlier checkpoints'''
    assert text.count(old)==1;text=text.replace(old,newtext);p.write_text(text,encoding='utf-8')
    comparison=[]
    for r in sorted(summary['rows'],key=lambda r:r['snr_db']):
        oldrow=next(x for x in raw['rows'] if x['method']=='pretrained_colored_first' and x['variance']==r['variance'])
        stmp=next(x for x in raw['rows'] if x['method']=='proposed' and x['variance']==r['variance'])
        comparison.append(dict(snr_db=r['snr_db'],white_nmse_db=r['nmse_db'],old_nmse_db=oldrow['nmse_db'],
                               stmp_nmse_db=stmp['nmse_db'],white_minus_old_db=r['nmse_db']-oldrow['nmse_db']))
    write_json(CHECK/'DATA_VERIFICATION.json',dict(status='PASS',completion_sha256=sha256(DEST/'COMPLETION.json'),
        coordinator_exited=True,full_output_hash_audit=True,baseline_rows_unchanged=48,
        replaced_rows=6,comparison=comparison,old_data_unchanged=True,created_unix=time.time()))
    print(comparison)


if __name__=='__main__':main()
