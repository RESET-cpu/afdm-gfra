"""Add the fixed-eta GNN diagnostic to an audited paired SNR AER figure.

Only saved outputs are read; no receiver, training, or frozen config mutation.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import base64
import json
import math
import numpy as np
from data import load, read, digest
import style as manuscript


def write_preview(out, stem):
    template=Path(__file__).with_name('gnn_readout_preview.html').read_text(encoding='utf-8')
    image=base64.b64encode((out/(stem+'_preview.png')).read_bytes()).decode('ascii')
    html=template.replace('__EMBEDDED_AER_PNG__','data:image/png;base64,'+image)
    assert len(html.encode('utf-8'))<1_000_000 and '__EMBEDDED_AER_PNG__' not in html
    (out/'gnn-fixed-eta-aer.html').write_text(html,encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    data=load(args.input,'snr_comparison')
    candidate=read(args.candidate)
    candidate_plan=read(args.candidate.parent/'PLAN.json')
    assert candidate['status']=='PASS_SAVED_OUTPUT_REPLAY'
    assert digest(args.candidate.parent/'PLAN.json')==candidate['plan_sha256']
    assert digest(args.candidate.parent/'DECISIONS.npz')==candidate['decisions_sha256']
    assert candidate['scene_count']==data.scenes==800
    assert data.metadata['scene_ids']==list(range(800))
    assert data.metadata['source_plan_sha256']==candidate['main_plan_sha256']
    assert candidate_plan['phase_mode']==data.metadata['phase_mode']=='known'
    assert candidate_plan['noise_mode']==data.metadata['noise_mode']=='estimated'
    methods=['STMP','offgrid_sbl','gnn','gamp','somp']
    assert set(data.methods)==set(methods)
    x=candidate['snr_db']
    originals=[]
    for m in methods:
        group=sorted((r for r in data.rows if r['method']==m),key=lambda r:r['parameters']['snr_db'])
        assert [r['parameters']['snr_db'] for r in group]==x
        originals.append(dict(method=m,label=manuscript.LABELS[m],snr_db=x,aer=[r['aer'] for r in group]))
        if m=='gnn':
            assert [r['misses']+r['false_alarms'] for r in group]==candidate['original']['errors']
    new=np.asarray(candidate['fixed_eta']['errors'])/candidate['user_decisions_per_snr']
    np.testing.assert_allclose(new,np.asarray(candidate['fixed_eta']['aer_percent'])/100,rtol=0,atol=2e-18)
    with np.load(args.candidate.parent/'DECISIONS.npz',allow_pickle=False) as z:
        assert np.array_equal(z['scene_ids'],np.arange(800))
        actual=(z['fixed_eta_decision']!=z['truth_activity']).sum(axis=(0,2))
        assert np.array_equal(actual,candidate['fixed_eta']['errors'])
    if args.output.exists():
        raise FileExistsError('Choose a new output directory; existing figures are retained.')
    args.output.mkdir(parents=True)
    original_hash=digest(args.input)
    candidate_hash=digest(args.candidate)
    manuscript.configure()
    fig,ax=manuscript.plt.subplots(figsize=(3.5,3.15))
    all_y=[]
    for row in originals:
        ax.plot(x,row['aer'],label=row['label'],clip_on=False,**manuscript.style(row['method']))
        all_y.extend(row['aer'])
    new_style=dict(manuscript.style('gnn'),linestyle='-',marker='v',linewidth=1.3)
    ax.plot(x,new,label=r'GNN-ASPL (fixed $\eta$)',clip_on=False,**new_style)
    all_y.extend(new.tolist())
    scale=manuscript.aer_scale(all_y)
    manuscript.axes_style(ax,'SNR (dB)','AER',x,yscale=scale)
    if scale=='log': ax.set_ylim(10**math.floor(math.log10(min(all_y))),max(all_y)*1.08)
    else: ax.set_ylim(bottom=0)
    stem='snr_aer_gnn_fixed_eta_800'
    manuscript.save(fig,args.output,stem)
    write_preview(args.output,stem)
    assert digest(args.input)==original_hash and digest(args.candidate)==candidate_hash
    plot_data=dict(experiment='snr_comparison',metric='aer_probability',scenes=800,
        original_series=originals,added_series=dict(method='gnn_fixed_eta',label='GNN-ASPL (fixed eta)',
            snr_db=x,aer=new.tolist(),threshold=candidate['threshold'],style=new_style))
    (args.output/'PLOT_DATA.json').write_text(json.dumps(plot_data,indent=2)+'\n',encoding='utf-8')
    caption=('AER on the same 800 paired physical scenes out of a planned 2000; known phase and estimated noise. '
        'Original five curves are unchanged. GNN-ASPL uses the current SNR-dependent thresholds; '
        f'the added GNN-ASPL (fixed eta) uses Ding Eq.(27) with historical project eta={candidate["threshold"]:.9f}. '
        'This eta was calibrated for a different checkpoint and scenario, not published by Ding. '
        'Saved-output diagnostic only; no new inference or training. AER is probability, not percent.')
    (args.output/'caption.txt').write_text(caption+'\n',encoding='utf-8')
    metadata=dict(status='PLOTTED',created_utc=datetime.now(timezone.utc).isoformat(),scenes=800,
        result_status='INTERIM_DIAGNOSTIC',original_five_curves_unchanged=True,new_inference=False,
        source=data.metadata,candidate=dict(path=str(args.candidate.resolve()),sha256=candidate_hash),
        script_sha256=digest(__file__),style_sha256=digest(Path(manuscript.__file__)),caption=caption,
        aer_scale=scale,exports={p.name:digest(p) for p in args.output.glob(stem+'.*')})
    (args.output/'FIGURES.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='PLOTTED',out=str(args.output.resolve()),series=6,scenes=800)))


if __name__=='__main__': main()
