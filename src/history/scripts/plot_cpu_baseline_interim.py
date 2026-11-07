"""Read-only, timestamped paired-scene plots of the running CPU baselines."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt, font_manager, ticker

METHODS=['offgrid_sbl','gnn','gamp','somp']
LABELS=['Off-grid SBL','GNN-ASPL','GAMP-SBL','SOMP']
COLORS=['#2459A6','#D25B28','#14836D','#8B5AA7']
MARKERS=['o','s','^','D']
KEYS=['active','inactive','misses','false_alarms','full_error','signal_energy']


def save_json(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')


def snapshot(base,package,job,cutoff):
    spec=json.loads((package/'inputs'/job/'PLAN.json').read_text())['experiment']
    records={}; sources=[]; failures=[]
    for scene in sorted((base/job).glob('scene*')):
        for folder in sorted(scene.glob('condition*')):
            for method in METHODS:
                path=folder/(method+'.json')
                if not path.exists() or path.stat().st_mtime>cutoff:
                    continue
                content=path.read_bytes(); row=json.loads(content)
                key=(row['scene'],row['condition'],method)
                if row['status']!='COMPLETE':
                    failures.append(str(path)); continue
                records[key]=(row,path,content)
    scenes=[s for s in range(spec['scenes']) if all((s,i,m) in records for i in range(len(spec['values'])) for m in METHODS)]
    if not scenes:
        raise ValueError('No complete paired scene across all conditions: '+job)
    selected=[]
    for scene in scenes:
        for i in range(len(spec['values'])):
            shared=None
            for method in METHODS:
                row,path,content=records[scene,i,method]
                assert row['truth_used_in_inference'] is False
                if shared is None: shared=row['input_array_sha256']
                assert shared==row['input_array_sha256'], 'Methods use different observations'
                assert hashlib.sha256(path.with_suffix('.npz').read_bytes()).hexdigest()==row['compact_sha256']
                selected.append(dict(scene=scene,condition=i,method=method,metrics={k:row['metrics'][k] for k in KEYS}))
                sources.append(dict(path=str(path),sha256=hashlib.sha256(content).hexdigest()))
    aggregate=[]
    for i,value in enumerate(spec['values']):
        for method in METHODS:
            group=[r['metrics'] for r in selected if r['condition']==i and r['method']==method]
            sums={key:sum(r[key] for r in group) for key in KEYS}
            ratio=sums['full_error']/sums['signal_energy']
            aggregate.append(dict(condition=i,value=value,method=method,scenes=len(group),**sums,
                aer=(sums['misses']+sums['false_alarms'])/(sums['active']+sums['inactive']),
                nmse_db=float(10*np.log10(ratio)) if ratio>0 else None))
    return dict(experiment=spec,paired_scenes=scenes,available_complete_results=len(records),
        included_results=len(selected),pending_pairing_results=len(records)-len(selected),
        failures=failures,metrics=selected,sources=sources,aggregate=aggregate)


def style(ax):
    ax.set_facecolor('#FFFFFF')
    ax.spines[['top','right']].set_visible(False)
    ax.spines[['left','bottom']].set_color('#C5CBD3')
    ax.grid(axis='both',color='#E4E8EE',linewidth=.7)
    ax.set_axisbelow(True)
    ax.tick_params(colors='#354052',labelsize=10)


def draw_lines(ax,rows,key,indices):
    for method,label,color,marker in zip(METHODS,LABELS,COLORS,MARKERS):
        group=[next(r for r in rows if r['condition']==i and r['method']==method) for i in indices]
        values=[r['aer']*100 if key=='aer' else r['nmse_db'] for r in group]
        ax.plot(range(len(indices)),values,color=color,marker=marker,label=label,
            linewidth=2,markersize=5.5,markeredgecolor='white',markeredgewidth=.7)
    style(ax)
    if key=='aer':
        ax.set_ylim(bottom=0)
        ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=100,decimals=1))


def render(out,job,data,stamp):
    n=len(data['paired_scenes']); rows=data['aggregate']; spec=data['experiment']
    if job=='user_count':
        fig,axes=plt.subplots(1,2,figsize=(11.8,5.5))
        fig.subplots_adjust(left=.085,right=.98,bottom=.25,top=.70,wspace=.28)
        fig.text(.07,.94,'用户数量实验 · 阶段性结果',fontsize=20,fontweight='bold',color='#18283D')
        fig.text(.07,.875,f'每点 n = {n}/500 个配对场景  |  SNR = 0 dB  |  16 帧导频  |  活动概率 0.1',fontsize=11,color='#536174')
        for ax,key,title in zip(axes,['aer','nmse_db'],['活动检测错误率','全信道 NMSE（dB）']):
            draw_lines(ax,rows,key,list(range(5)))
            ax.set_xticks(range(5),[str(v) for v in spec['values']])
            ax.set_xlabel('候选用户数',labelpad=9)
            ax.set_title(title+' ↓ 越低越好',fontsize=12,pad=12,loc='left')
        handles,labels=axes[0].get_legend_handles_labels()
        fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.53,.825),ncol=4,frameon=False,fontsize=11)
    else:
        fig,axes=plt.subplots(2,4,figsize=(16,8.4),sharey='row')
        fig.subplots_adjust(left=.075,right=.985,bottom=.20,top=.77,wspace=.18,hspace=.48)
        fig.text(.06,.95,'跨信道模型实验 · 阶段性结果',fontsize=22,fontweight='bold',color='#18283D')
        fig.text(.06,.895,f'所有曲线共用 n = {n}/500 个配对场景  |  40 个候选用户  |  16 帧导频  |  活动概率 0.1',fontsize=12,color='#536174')
        for col,profile in enumerate(spec['profiles']):
            indices=[i for i,v in enumerate(spec['values']) if v.split('/')[0]==profile]
            for row,key in enumerate(['aer','nmse_db']):
                ax=axes[row,col]
                draw_lines(ax,rows,key,indices)
                ax.set_xticks(range(6),[str(v) for v in spec['snr']])
                ax.set_xlabel('SNR（dB）',labelpad=7)
            axes[0,col].set_title('NTN-TDL-'+profile,fontsize=13,fontweight='bold',pad=13)
        axes[0,0].set_ylabel('活动检测错误率 ↓',labelpad=12)
        axes[1,0].set_ylabel('全信道 NMSE（dB）↓',labelpad=12)
        axes[0,0].set_ylim(0,max(r['aer'] for r in rows)*100*1.12)
        handles,labels=axes[0,0].get_legend_handles_labels()
        fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.52,.854),ncol=4,frameon=False,fontsize=12)
    fig.text(.07,.075,'各方法、各横轴点使用相同场景；仅纳入所有条件和四种方法均已完成的场景。',fontsize=10,color='#536174')
    fig.text(.07,.030,f'截至 {stamp}  |  尚未完成 500 场景；仅供观察趋势  |  Proposed 待训练完成后加入',fontsize=10,color='#536174')
    for suffix in ('png','pdf'):
        fig.savefig(out/f'{job}.{suffix}',dpi=180,facecolor='white')
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--base',type=Path,default=Path('D:/afdm-gfra-cpu/results_windows'))
    parser.add_argument('--package',type=Path,default=Path('D:/afdm-gfra-cpu/runs/cpu_9900x_20261018/package'))
    args=parser.parse_args()
    cutoff=time.time(); stamp=datetime.fromtimestamp(cutoff).strftime('%Y-%m-%d %H:%M:%S')
    out=args.base/'interim_figures'/datetime.fromtimestamp(cutoff).strftime('%Y%m%d_%H%M%S')
    out.mkdir(parents=True,exist_ok=False)
    font_manager.fontManager.addfont('C:/Windows/Fonts/msyh.ttc')
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname='C:/Windows/Fonts/msyh.ttc').get_name(),
        'font.size':11,'axes.unicode_minus':False,'pdf.fonttype':42})
    result=dict(status='INTERIM',cutoff_unix=cutoff,snapshot_time_local=stamp,
        inclusion='Intersection of COMPLETE scenes across all methods and all conditions, selected without consulting metric values.',
        statistics='AER=sum(misses+false_alarms)/sum(active+inactive); full-channel NMSE=10log10(sum(full_error)/sum(signal_energy)).',
        limitation='Completion order may depend on runtime; this subset is not a certified random sample. No final ranking or statistical significance is claimed.',
        inherited_scene_zero='Included if paired and complete; inherited Mac inference retained. No timing comparison.',
        generator=str(Path(__file__).resolve()),generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),jobs={})
    for job in ('user_count','cross_channel'):
        data=snapshot(args.base,args.package,job,cutoff)
        save_json(out/f'{job}_snapshot.json',data)
        render(out,job,data,stamp)
        result['jobs'][job]={k:data[k] for k in ('paired_scenes','available_complete_results','included_results','pending_pairing_results','failures','aggregate')}
        print(job,'paired scenes',len(data['paired_scenes']),flush=True)
    save_json(out/'SUMMARY.json',result)
    print(str(out),flush=True)


if __name__=='__main__':
    main()
