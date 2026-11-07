"""Plot all six completed training histories without smoothing or filtering."""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt, font_manager
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT/'runs/proposed_auxiliary_100_cuda_graph_20261019'
FIRST = {5000:ROOT/'runs/proposed_sample_sizes_20261018/n5000/first',
         50000:ROOT/'runs/proposed_50000_cuda_graph_20261018/model/first'}
NAMES = {'first':'一阶网络', 'second':'二阶网络', 'activity':'活动分类器'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    font = Path('C:/Windows/Fonts/msyh.ttc')
    font_manager.fontManager.addfont(str(font))
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname=str(font)).get_name(),
        'font.size':11, 'axes.unicode_minus':False, 'pdf.fonttype':42,
        'axes.spines.top':False, 'axes.spines.right':False, 'axes.titleweight':'bold',
        'savefig.facecolor':'white'})
    report = dict(smoothing=False, yscale='log', epoch_zero='Initial validation included; no training value at epoch zero',
        train_definition='Online noisy queries, current model, average over the epoch',
        validation_definition='Fixed validation queries evaluated with EMA weights at epoch end',
        budget_note='First: 200 epochs. Auxiliary: 100 epochs. The 50k second score switched from a 200-epoch horizon during epoch 5; prior updates retained.',
        curves={})
    with PdfPages(out/'all_training_losses.pdf') as pdf:
        for stage in ('first','second','activity'):
            fig, axes = plt.subplots(1,2,figsize=(14.6,5.6),sharey=True)
            fig.subplots_adjust(left=.075,right=.98,bottom=.27,top=.78,wspace=.12)
            fig.suptitle(f'{NAMES[stage]} · 训练与验证 loss',fontsize=19,y=.985)
            epochs = 200 if stage == 'first' else 100
            fig.text(.5,.89,f'完整 {epochs} 轮  ·  原始逐轮记录，未平滑  ·  纵轴为对数刻度',ha='center',color='#475569')
            values=[]
            for ax, size in zip(axes,(5000,50000)):
                folder = FIRST[size] if stage == 'first' else TRAIN/f'n{size}'/stage
                history=json.loads((folder/'history.json').read_text())
                complete=json.loads((folder/'complete.json').read_text())
                assert complete['status']=='COMPLETED' and complete['epochs']==epochs
                assert [r['epoch'] for r in history if r['epoch']>0]==list(range(1,epochs+1))
                snapshot=out/'source_histories'/f'n{size}'/stage
                snapshot.mkdir(parents=True)
                source_hashes={}
                for name in ('history.json','complete.json','baseline.json','specification.json'):
                    path=folder/name
                    if path.exists():
                        shutil.copy2(path,snapshot/name)
                        source_hashes[str(path.relative_to(ROOT))]=sha(path)
                if history[0]['epoch']!=0:
                    baseline=json.loads((folder/'baseline.json').read_text())
                    history=[dict(epoch=0,validation=baseline)]+history
                train=[(r['epoch'],r['train_loss']) for r in history if 'train_loss' in r]
                validation=[(r['epoch'],r['validation']['loss']) for r in history]
                assert all(np.isfinite(v) and v>0 for e,v in train+validation)
                selected=complete['selected_epoch']
                best=dict(validation)[selected]
                assert np.isclose(best, min(v for e,v in validation),rtol=1e-10,atol=1e-15)
                assert np.isclose(best,complete['validation']['loss'],rtol=1e-10,atol=1e-15)
                ax.plot(*zip(*train),color='#2563eb',lw=1.65,label='训练 loss')
                ax.plot(*zip(*validation),color='#ea580c',lw=1.65,ls='--',label='验证 loss（EMA）')
                ax.scatter([selected],[best],marker='*',s=135,color='#ea580c',edgecolors='white',linewidth=.65,zorder=5,label='最佳验证权重')
                ax.set(title=f'{size:,} 个训练样本',xlabel='训练轮次（epoch）',yscale='log',xlim=(-epochs*.015,epochs*1.035))
                ax.set_xticks(np.linspace(0,epochs,6))
                ax.grid(True,which='major',color='#e2e8f0',lw=.7)
                ax.grid(True,which='minor',axis='y',color='#f1f5f9',lw=.4)
                ax.text(.97,.96,f'最佳验证：{best:.5g}\n第 {selected} 轮',ha='right',va='top',transform=ax.transAxes,
                    fontsize=10.5,bbox=dict(boxstyle='round,pad=.45',facecolor='white',edgecolor='#e2e8f0',alpha=.95))
                values.extend(v for e,v in train+validation)
                report['curves'][f'{stage}_{size}']=dict(train=train,validation=validation,
                    selected_epoch=selected,best_validation_loss=best,final_train_loss=train[-1][1],
                    final_validation_loss=validation[-1][1],source_sha256=source_hashes)
            axes[0].set_ylabel('BCE loss（对数刻度）' if stage=='activity' else 'Loss（对数刻度）')
            axes[0].set_ylim(min(values)/1.5,max(values)*1.5)
            handles,labels=axes[0].get_legend_handles_labels()
            fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,.14),ncol=3,frameon=False)
            note='训练：当前模型、在线噪声；验证：滑动平均（EMA）权重、固定噪声。两者并非完全相同的评估口径。'
            fig.text(.5,.075,note,ha='center',fontsize=9.3,color='#475569')
            if stage=='second':
                fig.text(.5,.025,'50,000 样本二阶网络在第 5 轮内改为总计 100 轮；已有更新与完整历史均保留。',ha='center',fontsize=9,color='#64748b')
            fig.savefig(out/f'{stage}_loss.png',dpi=180)
            pdf.savefig(fig)
            plt.close(fig)
    (out/'curves_and_sources.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(output=str(out),curves=len(report['curves']),status='VERIFIED'),ensure_ascii=False))


if __name__=='__main__':
    main()
