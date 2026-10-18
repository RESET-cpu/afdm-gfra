import json,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator,LogFormatterMathtext
LABELS={'proposed':'Proposed','offgrid_sbl':'Off-grid SBL','gnn':'GNN-ASPL','gamp':'GAMP-SBL','somp':'SOMP'}
STYLES={'proposed':dict(color='#b83253',marker='o',linestyle='-',linewidth=2.5),
 'offgrid_sbl':dict(color='#20847c',marker='s',linestyle='--',linewidth=1.8,markerfacecolor='none'),
 'gnn':dict(color='#745c9f',marker='^',linestyle='-.',linewidth=1.8,markerfacecolor='none'),
 'gamp':dict(color='#b7802a',marker='D',linestyle=':',linewidth=1.8,markerfacecolor='none'),
 'somp':dict(color='#6d7b8e',marker='x',linestyle='--',linewidth=1.8)}
def plot(plan,rows):
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.5,'text.color':'#2b3547',
  'axes.labelcolor':'#2b3547','xtick.color':'#4d586a','ytick.color':'#4d586a','pdf.fonttype':42,'svg.fonttype':'none'})
 fig=plt.figure(figsize=(12.8,6.1),facecolor='white')
 left=fig.add_axes([.075,.22,.405,.50]);right=fig.add_axes([.575,.22,.405,.50])
 handles=[]
 for method in plan['methods']:
  g=sorted([r for r in rows if r['method']==method],key=lambda r:r['snr_db'])
  x=[r['snr_db'] for r in g]
  line,=left.plot(x,[r['aer_percent']/100 for r in g],markersize=6,markeredgewidth=1.5,**STYLES[method]);handles.append(line)
  right.plot(x,[r['nmse_db'] for r in g],markersize=6,markeredgewidth=1.5,**STYLES[method])
 for ax in [left,right]:
  ax.set_xticks(plan['snr_db']);ax.set_xlabel('SNR (dB)',labelpad=9)
  ax.grid(True,color='#dfe2e7',alpha=.75,linewidth=.75)
  ax.spines[['top','right']].set_visible(False)
  for side in ['left','bottom']:ax.spines[side].set_color('#bdc4ce')
  ax.tick_params(length=0,pad=7)
 left.set_ylabel('Activity error rate',labelpad=9)
 left.set_yscale('log')
 left.yaxis.set_major_locator(LogLocator(base=10))
 left.yaxis.set_major_formatter(LogFormatterMathtext(base=10))
 positive=[r['aer_percent']/100 for r in rows if r['aer_percent']>0]
 left.set_ylim(10**np.floor(np.log10(min(positive))),10**np.ceil(np.log10(max(positive))))
 right.set_ylabel('Full-channel NMSE (dB)',labelpad=11)
 left.set_title('(a) Activity detection',loc='left',fontweight='bold',fontsize=14,pad=15)
 right.set_title('(b) Channel estimation',loc='left',fontweight='bold',fontsize=14,pad=15)
 fig.text(.075,.94,'Baseline comparison on off-grid AFDM channels'+(' — interim' if plan.get('interim',False) else ''),fontweight='bold',fontsize=19)
 fig.text(.075,.887,'40 candidate users | 16 pilot frames | 16 receive antennas',fontsize=11.5,color='#657083')
 fig.legend(handles,[LABELS[m]+f'\n(n={plan["scenes"]})' for m in plan['methods']],loc='center left',
   bbox_to_anchor=(.068,.804),ncol=5,frameon=False,handlelength=3.1,columnspacing=2.3,handletextpad=.7)
 fig.text(.075,.105,'n = physical scenes per SNR, shown in the legend. Lower is better in both panels.',fontsize=10,color='#657083')
 fig.text(.075,.064,f'All methods use the same {plan["scenes"]} scenes and estimated phases. Each scene is reused across SNR.',fontsize=10,color='#657083')
 noise='Noise variance supplied to all methods.' if plan['noise_mode']=='known' else 'Noise variance estimated from observations for all methods.'
 fig.text(.075,.025,'Frozen receiver settings and activity thresholds. '+noise,fontsize=9.4,color='#657083')
 for ext in ['png','pdf','svg']:fig.savefig(OUT/('comparison.'+ext),dpi=180)
 plt.close(fig)


if __name__=='__main__':
 OUT=Path(sys.argv[1]).resolve()
 rows=json.loads((OUT/'SUMMARY.json').read_text())['rows']
 plan=dict(scenes=rows[0]['scenes'],methods=list(LABELS),snr_db=sorted(set(r['snr_db'] for r in rows)),noise_mode='estimated',interim='partial' in str(OUT))
 assert all(r['aer_percent']>0 for r in rows), 'Zero AER requires explicit annotation, not substitution'
 plot(plan,rows)
 (OUT/'PLOT_SCALE.json').write_text(json.dumps(dict(aer_scale='log10',aer_unit='probability',conversion='aer_percent / 100',renderer=str(Path(__file__).resolve())),indent=2))
