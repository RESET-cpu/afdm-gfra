"""Check saved diagnostics and draw a figure, without rerunning a receiver."""
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

ROOT=Path(r'C:\Users\25911\Desktop\afdm-gfra')
OUT=ROOT/'results/lstmp_cai_activity_frozen_20261019'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    complete=read(OUT/'COMPLETE.json')
    report=read(OUT/'REPORT.json')
    plan=read(OUT/'PLAN.json')
    assert sha(OUT/'REPORT.json')==complete['report_sha256']
    assert sha(OUT/'PLAN.json')==report['plan_sha256']
    assert sha(OUT/'scene_metrics.csv')==report['metrics_sha256']
    rows=list(csv.DictReader((OUT/'scene_metrics.csv').open(encoding='utf-8')))
    assert len(rows)==96*3*3 and not report['failures']
    for scene,receipt in enumerate(read(OUT/'INPUTS.json')):
        folder=OUT/'scenes'/f'{scene:03d}'
        assert sha(folder/'input.npz')==receipt['input_sha256']
        assert sha(folder/'truth.npz')==receipt['truth_sha256']
        with np.load(folder/'predictions.npz') as z:
            truth=z['active'].astype(bool)
            selected=[r for r in rows if int(r['scene'])==scene]
            assert len(selected)==9
            for row in selected:
                p=z[f"{row['method']}_layer{row['depth']}_probability"]
                assert np.isfinite(p).all()
                assert int(row['misses'])==np.sum(truth & (p<.5))
                assert int(row['false_alarms'])==np.sum(~truth & (p>=.5))
            # Both closed loops must start from exactly the same linear query.
            np.testing.assert_array_equal(z['classifier_layer1_query_energy_over_v'],z['cai_feedback_layer1_query_energy_over_v'])
            np.testing.assert_array_equal(z['cai_same_messages_layer1_logit'],z['cai_feedback_layer1_logit'])
    tables=[]
    for group,methods in report['summaries'].items():
        for method,by_depth in methods.items():
            for s in by_depth:
                a=[r for r in rows if r['method']==method and int(r['depth'])==s['depth'] and (group=='all' or r['group']==group)]
                n=sum(int(r['active'])+int(r['inactive']) for r in a)
                aer=sum(int(r['misses'])+int(r['false_alarms']) for r in a)/n
                nmse=10*math.log10(sum(float(r['error_energy']) for r in a)/sum(float(r['truth_energy']) for r in a))
                assert abs(aer-s['aer'])<1e-12 and abs(nmse-s['pooled_nmse_db'])<1e-10
                if s['depth']==3:
                    tables.append(dict(group=group,method=method,scenes=s['scenes'],aer=s['aer'],
                        missed_detection_rate=s['missed_detection_rate'],false_alarm_rate=s['false_alarm_rate'],
                        pooled_nmse_db=s['pooled_nmse_db'],probability_brier=s['probability_brier'],
                        saturated_fraction=s['saturated_fraction'],confidently_wrong_fraction=s['confidently_wrong_fraction'],
                        all_inactive_reference_aer=s['active']/n,all_inactive_reference_nmse_db=0.))
    review=dict(all_checks_passed=True,checks=['96 scenes x 3 arms x 3 layers',
        'input and truth file hashes','saved predictions reproduce classification counts',
        'identical initial queries and analytic logits','CSV and summary agreement'],
        final_layer=tables,report_sha256=sha(OUT/'REPORT.json'))
    (OUT/'REVIEW.json').write_text(json.dumps(review,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,axes=plt.subplots(2,2,figsize=(12,8))
    groups=['balanced','standard','stress']
    labels=['Balanced\n48 scenes','K40 / Q16 / 5 dB\n24 scenes','K100 / Q8 / 10 dB\n24 scenes']
    methods=['classifier','cai_same_messages','cai_feedback']
    names=['Trained classifier','Cai rule on same queries*','Cai rule with feedback']
    colors=['#176b9b','#85969e','#db772d']
    panels=[('aer','Activity error (%)',100),('pooled_nmse_db','Pooled channel NMSE (dB)',1),
            ('missed_detection_rate','Missed detection (%)',100),('false_alarm_rate','False alarm (%)',100)]
    x=np.arange(3)
    for ax,(metric,label,factor) in zip(axes.flat,panels):
        for j,(method,name,color) in enumerate(zip(methods,names,colors)):
            values=[report['summaries'][g][method][-1][metric]*factor for g in groups]
            bars=ax.bar(x+(j-1)*.25,values,width=.24,label=name,color=color)
            ax.bar_label(bars,fmt='%.1f',padding=3,fontsize=9)
        ax.set_xticks(x,labels);ax.set_ylabel(label);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
        lo,hi=ax.get_ylim();ax.set_ylim(lo-(hi-lo)*.10 if lo<0 else 0,hi+(hi-lo)*.16)
    handles,names=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,names,loc='upper center',bbox_to_anchor=(.5,.95),ncol=3,frameon=False)
    fig.suptitle('Frozen depth-3 checkpoint: analytic activity evidence versus classifier',y=.995,fontsize=15)
    fig.text(.5,.035,'96 new development scenes | known phase/noise | threshold 0.5 | no weight updates\n'
        '* Same-query arm changes the current output only; it does not enter the feedback loop.',ha='center',fontsize=10)
    fig.tight_layout(rect=(0,.085,1,.91))
    fig.savefig(OUT/'comparison.png',dpi=170)
    fig.savefig(OUT/'comparison.pdf')
    plt.close(fig)
    print(json.dumps(review,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
