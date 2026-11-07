"""Verify all planned native metrics and render the requested two-panel figure."""
import csv,json,gzip
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from run import OUT,ROOT,read,save,arrays,sha,verify_sources,score,digest

LABELS={'proposed':'Proposed','offgrid_sbl':'Off-grid SBL','gnn':'GNN-ASPL','gamp':'GAMP-SBL','somp':'SOMP'}
STYLES={'proposed':dict(color='#b83253',marker='o',linestyle='-',linewidth=2.5),
 'offgrid_sbl':dict(color='#20847c',marker='s',linestyle='--',linewidth=1.8,markerfacecolor='none'),
 'gnn':dict(color='#745c9f',marker='^',linestyle='-.',linewidth=1.8,markerfacecolor='none'),
 'gamp':dict(color='#b7802a',marker='D',linestyle=':',linewidth=1.8,markerfacecolor='none'),
 'somp':dict(color='#6d7b8e',marker='x',linestyle='--',linewidth=1.8)}

def audit():
 plan=verify_sources();rows=[];native_checks=0
 for scene in range(plan['scenes']):
  parent=OUT/'scenes'/f'scene{scene:03d}'
  truth=arrays(parent/'truth.npz');scene_meta=read(parent/'READY.json')
  assert sha(parent/'truth.npz')==scene_meta['truth_sha256']
  assert scene_meta['seed']==plan['seeds'][scene]
  active=truth['activity'].astype(bool)
  signal=float(np.sum(truth['channel'].real**2+truth['channel'].imag**2))
  for snr in plan['snr_db']:
   folder=parent/f'snr{snr:+03d}';ready=read(folder/'READY.json')
   assert sha(folder/'phase.npz')==ready['phase_sha256']
   for method in plan['methods']:
    row=read(folder/(method+'.metrics.json'))
    assert row['status']=='COMPLETE' and (row['scene'],row['snr'],row['method'])==(scene,snr,method)
    assert row['shared_phase_sha256']==ready['phase_sha256']
    assert sha(folder/(method+'.compact.npz'))==row['compact_sha256']
    compact=arrays(folder/(method+'.compact.npz'));m=row['metrics']
    np.testing.assert_array_equal(compact['truth_activity'],truth['activity'])
    decision=compact['activity_decision'].astype(bool)
    md=int(np.count_nonzero(active&~decision));fa=int(np.count_nonzero(~active&decision))
    assert (md,fa)==(m['misses'],m['false_alarms'])
    assert m['users']==40 and m['active']==int(active.sum())
    np.testing.assert_allclose(np.sum(compact['per_user_error']),m['full_error'],rtol=1e-13)
    np.testing.assert_allclose(signal,m['signal_energy'],rtol=1e-13)
    if scene in plan['full_prediction_scenes']:
     native=arrays(folder/(method+'.prediction.npz'))
     rescored=score(native,truth)
     assert rescored==m
     record=read(folder/(method+'.record.json.gz'))
     assert digest(native)==record['output_array_sha256']
     native_checks+=1
    rows.append(row)
 assert len(rows)==plan['expected_receiver_runs']==21000
 save(OUT/'VERIFICATION.json',dict(status='PASS',planned_runs=21000,completed_runs=len(rows),
   independent_physical_scenes=600,snr_points=7,methods=5,native_output_recomputations=native_checks,
   per_user_metric_audits=len(rows),paired_phase_and_input_identity=True))
 return plan,rows

def aggregate(plan,rows):
 rng=np.random.default_rng(202610172099999)
 draws=rng.integers(0,plan['scenes'],size=(10000,plan['scenes']))
 result=[]
 for method in plan['methods']:
  for snr in plan['snr_db']:
   group=sorted([r for r in rows if r['method']==method and r['snr']==snr],key=lambda r:r['scene'])
   assert len(group)==plan['scenes']
   errors=np.array([r['metrics']['full_error'] for r in group])
   signal=np.array([r['metrics']['signal_energy'] for r in group])
   misses=np.array([r['metrics']['misses'] for r in group]);fa=np.array([r['metrics']['false_alarms'] for r in group])
   nmse=10*np.log10(errors.sum()/signal.sum());aer=100*(misses+fa).sum()/(40*len(group))
   boot_nmse=10*np.log10(errors[draws].sum(axis=1)/signal[draws].sum(axis=1))
   boot_aer=100*(misses+fa)[draws].sum(axis=1)/(40*len(group))
   ci_n=np.quantile(boot_nmse,[.025,.975]);ci_a=np.quantile(boot_aer,[.025,.975])
   result.append(dict(method=method,snr_db=snr,scenes=len(group),aer_percent=float(aer),nmse_db=float(nmse),
      misses=int(misses.sum()),false_alarms=int(fa.sum()),users=40*len(group),
      full_error=float(errors.sum()),signal_energy=float(signal.sum()),
      aer_low=float(ci_a[0]),aer_high=float(ci_a[1]),nmse_low=float(ci_n[0]),nmse_high=float(ci_n[1])))
 save(OUT/'SUMMARY.json',dict(status='COMPLETE',rows=result,noise_mode=plan['noise_mode'],
  phase_mode='estimated',bootstrap=dict(repetitions=10000,unit='physical_scene',pointwise=True),
  timing_scope='Producer/baseline and Proposed workers may overlap; receiver wall times are not isolated latency benchmarks'))
 with (OUT/'STATISTICS.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(result[0]));writer.writeheader();writer.writerows(result)
 return result

def plot(plan,rows):
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.5,'text.color':'#2b3547',
  'axes.labelcolor':'#2b3547','xtick.color':'#4d586a','ytick.color':'#4d586a','pdf.fonttype':42,'svg.fonttype':'none'})
 fig=plt.figure(figsize=(12.8,6.1),facecolor='white')
 left=fig.add_axes([.075,.22,.405,.50]);right=fig.add_axes([.575,.22,.405,.50])
 handles=[]
 for method in plan['methods']:
  g=sorted([r for r in rows if r['method']==method],key=lambda r:r['snr_db'])
  x=[r['snr_db'] for r in g]
  line,=left.plot(x,[r['aer_percent'] for r in g],markersize=6,markeredgewidth=1.5,**STYLES[method]);handles.append(line)
  right.plot(x,[r['nmse_db'] for r in g],markersize=6,markeredgewidth=1.5,**STYLES[method])
 for ax in [left,right]:
  ax.set_xticks(plan['snr_db']);ax.set_xlabel('SNR (dB)',labelpad=9)
  ax.grid(True,color='#dfe2e7',alpha=.75,linewidth=.75)
  ax.spines[['top','right']].set_visible(False)
  for side in ['left','bottom']:ax.spines[side].set_color('#bdc4ce')
  ax.tick_params(length=0,pad=7)
 left.set_ylabel('Activity error rate (%)',labelpad=9);left.set_ylim(bottom=-max(.01,.04*max(r['aer_percent'] for r in rows)))
 left.yaxis.set_major_locator(MaxNLocator(nbins=5))
 right.set_ylabel('Full-channel NMSE (dB)',labelpad=11)
 left.set_title('(a) Activity detection',loc='left',fontweight='bold',fontsize=14,pad=15)
 right.set_title('(b) Channel estimation',loc='left',fontweight='bold',fontsize=14,pad=15)
 fig.text(.075,.94,'Baseline comparison on off-grid AFDM channels',fontweight='bold',fontsize=19)
 fig.text(.075,.887,'40 candidate users | 16 pilot frames | 16 receive antennas',fontsize=11.5,color='#657083')
 fig.legend(handles,[LABELS[m]+'\n(n=600)' for m in plan['methods']],loc='center left',
   bbox_to_anchor=(.068,.804),ncol=5,frameon=False,handlelength=3.1,columnspacing=2.3,handletextpad=.7)
 fig.text(.075,.105,'n = physical scenes per SNR, shown in the legend. Lower is better in both panels.',fontsize=10,color='#657083')
 fig.text(.075,.064,'All methods use the same 600 scenes and estimated phases. Each scene is reused across SNR.',fontsize=10,color='#657083')
 noise='Noise variance supplied to all methods.' if plan['noise_mode']=='known' else 'Noise variance estimated from observations for all methods.'
 fig.text(.075,.025,'Frozen receiver settings and activity thresholds. '+noise,fontsize=9.4,color='#657083')
 for ext in ['png','pdf','svg']:fig.savefig(OUT/('comparison.'+ext),dpi=180)
 plt.close(fig)

if __name__=='__main__':
 p,r=audit();summary=aggregate(p,r);plot(p,summary)
 print('All 21,000 runs verified; comparison.png, comparison.pdf, comparison.svg written.')
