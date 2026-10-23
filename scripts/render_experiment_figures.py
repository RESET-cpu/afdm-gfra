"""Render completed experiment summaries with the shared reference legend."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/figure_style_20261019'
BASE = 'results/local_baselines_20261018/formal'
RETURNED = 'results/cpu_9900x_returned_20261019'
STYLES = {
    'proposed': dict(label='Proposed', color='#BF3052', linestyle='-', marker='o'),
    'proposed_small': dict(label='Proposed', color='#DE7288', linestyle='-', marker='o'),
    'offgrid_sbl': dict(label='Off-grid SBL', color='#168682', linestyle='--', marker='s'),
    'gnn': dict(label='GNN-ASPL', color='#7158AC', linestyle='-.', marker='^'),
    'gamp': dict(label='GAMP-SBL', color='#BE7A10', linestyle=':', marker='D'),
    'somp': dict(label='SOMP', color='#687B96', linestyle='--', marker='x'),
    'bg_tmp': dict(label='BG-TMP', color='#7158AC', linestyle='-.', marker='^'),
    'noisy': dict(label='LS', color='#7C8795', linestyle=':', marker='+'),
    'gaussian': dict(label='Gaussian prior', color='#A88B32', linestyle='--', marker='v'),
    'genie_bound': dict(label='Genie conditional MMSE (oracle)', color='#438363', linestyle='-.', marker='x'),
}
ORDER = ['proposed', 'proposed_small', 'offgrid_sbl', 'gnn', 'gamp', 'somp', 'bg_tmp', 'noisy', 'gaussian', 'genie_bound']
INK, MUTED, GRID = '#253247', '#607087', '#E1E7EF'
SOURCES, FIGURES, REMOVED = {}, [], []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(relative):
    path = ROOT / relative
    SOURCES[relative] = sha(path)
    data = json.loads(path.read_text())
    assert data['status'] == 'COMPLETE', relative
    return data


def setup():
    OUT.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12,
        'text.color': INK, 'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED,
        'axes.edgecolor': '#B8C4D3', 'axes.labelsize': 13, 'axes.titlesize': 15,
        'axes.titleweight': 'bold', 'axes.titlecolor': INK,
        'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none', 'savefig.facecolor': 'white'})


def methods(rows):
    present = {r['method'] for r in rows}
    return [m for m in ORDER if m in present]


def style(method):
    return {k: v for k, v in STYLES[method].items() if k != 'label'}


def line(ax, x, y, method, markevery=None):
    ax.plot(x, y, **style(method), linewidth=2.3 if method.startswith('proposed') else 2.0,
            markersize=7.5, markerfacecolor='none', markeredgewidth=1.7, markevery=markevery)


def axes_style(ax):
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(True, color=GRID, linewidth=.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, pad=7)
    ax.xaxis.labelpad = 10
    ax.yaxis.labelpad = 10


def header(fig, title, subtitle, selected, n, denoising=False):
    fig.text(.075, .957, title, fontsize=22, weight='bold', va='top')
    fig.text(.075, .895, subtitle, fontsize=12.5, color=MUTED, va='top')
    handles = []
    for m in selected:
        label = STYLES[m]['label']
        if denoising and m.startswith('proposed'):
            label += ' (50k training)' if m == 'proposed' else ' (5k training)'
        handles.append(Line2D([], [], **style(m), label=f'{label}\n(n={n:,})',
            linewidth=2.2, markersize=8, markerfacecolor='none', markeredgewidth=1.7))
    columns = min(len(handles), 5 if denoising else 5)
    legend = fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(.075, .836),
        ncol=columns, frameon=False, handlelength=3.0, columnspacing=2.3,
        handletextpad=.7, borderaxespad=0, fontsize=11.5)
    return legend


def save(fig, name, source, aliases=(), description='', svg=False, primary_stem=None):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    # Shared legends must stay within the canvas and above every data panel.
    for legend in fig.legends:
        box = legend.get_window_extent(renderer)
        assert box.x0 >= 0 and box.x1 <= fig.bbox.x1 + 1, (name, 'legend horizontal bounds')
        assert box.y0 > max(ax.get_window_extent(renderer).y1 for ax in fig.axes), (name, 'legend overlap')
    outputs = []
    for ext in ('png', 'pdf', 'svg') if svg else ('png', 'pdf'):
        target = ROOT / f'{primary_stem}.{ext}' if primary_stem else OUT / f'{name}.{ext}'
        fig.savefig(target, dpi=180)
        outputs.append(str(target.relative_to(ROOT)))
        for stem in aliases:
            dest = ROOT / f'{stem}.{ext}'
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, dest)
            outputs.append(str(dest.relative_to(ROOT)))
    plt.close(fig)
    entry = dict(name=name, source=source, description=description,
                 files={p: sha(ROOT/p) for p in outputs})
    FIGURES.append(entry)
    (OUT/f'{name}.json').write_text(json.dumps(dict(entry, renderer_sha256=sha(Path(__file__)),
        sources={p:SOURCES[p] for p in ([source] if isinstance(source,str) else source)},
        styles=STYLES),indent=2)+'\n')


def scan(name, folder, title, subtitle, xlabel, xkey='value', percent=False, aliases=(), svg=False):
    source = folder + '/SUMMARY.json'
    rows = read(source)['rows']
    selected = methods(rows)
    n_values = {r.get('scenes', r.get('completed')) for r in rows}
    assert len(n_values) == 1
    n = n_values.pop()
    if xkey == 'snr_db':
        assert all(r['scenes'] == n for r in rows)
    else:
        assert all(r['status'] == 'COMPLETE' and r['missing'] == r['failed'] == 0 for r in rows)
    fig, axes = plt.subplots(1, 2, figsize=(15.5, 7.6))
    fig.subplots_adjust(left=.075, right=.975, bottom=.23, top=.65, wspace=.25)
    header(fig, title, subtitle, selected, n)
    zero_notes = []
    for m in selected:
        group = sorted([r for r in rows if r['method'] == m], key=lambda r: float(r[xkey]))
        x = [float(r[xkey]) for r in group]
        aer = [r['aer'] if 'aer' in r else r['aer_percent']/100 for r in group]
        plotted = [a*100 if percent else (a if a > 0 else math.nan) for a in aer]
        line(axes[0], x, plotted, m)
        line(axes[1], x, [r['nmse_db'] for r in group], m)
        if not percent and any(a == 0 for a in aer):
            zero_notes.append(STYLES[m]['label'] + ': AER = 0 at ' + ', '.join(f'{v:g}' for v,a in zip(x,aer) if a == 0))
    for ax, label, ylabel in zip(axes, ['(a) Activity detection', '(b) Channel estimation'],
                                 ['Activity error rate (%)' if percent else 'Activity error rate', 'Full-channel NMSE (dB)']):
        axes_style(ax)
        ax.set(title=label, xlabel=xlabel, ylabel=ylabel)
        ax.set_xticks(sorted({float(r[xkey]) for r in rows}))
    if percent:
        axes[0].set_ylim(bottom=0)
    else:
        axes[0].set_yscale('log')
    if zero_notes:
        axes[0].text(.03,.03,'\n'.join(zero_notes),transform=axes[0].transAxes,fontsize=8,
                     bbox=dict(facecolor='white',alpha=.9,edgecolor='none'))
    fig.text(.075, .125, 'n = paired physical scenes per condition. Estimated phase and noise.', fontsize=11, color=MUTED)
    fig.text(.075, .077, 'Curves show pooled point estimates; lower is better in both panels.', fontsize=11, color=MUTED)
    save(fig, name, source, aliases, svg=svg)


def cross_channel():
    source = RETURNED + '/cross_channel/SUMMARY.json'
    rows = read(source)['rows']; selected = methods(rows)
    assert all(r['completed'] == 500 and r['failed'] == r['missing'] == 0 for r in rows)
    fig, axes = plt.subplots(2, 4, figsize=(19, 11))
    fig.subplots_adjust(left=.075, right=.98, bottom=.14, top=.70, wspace=.30, hspace=.40)
    header(fig, 'Performance across channel models',
           '40 candidate users  |  16 pilot frames  |  16 receive antennas  |  Fixed trained weights', selected, 500)
    for col, profile in enumerate(['D', 'A', 'B', 'C']):
        for m in selected:
            group = sorted([r for r in rows if r['method'] == m and r['value'].split('/')[0] == profile],
                           key=lambda r: float(r['value'].split('/')[1]))
            x = [float(r['value'].split('/')[1]) for r in group]
            assert len(group) == 6 and all(r['aer'] > 0 for r in group)
            line(axes[0,col], x, [r['aer'] for r in group], m)
            line(axes[1,col], x, [r['nmse_db'] for r in group], m)
        axes[0,col].set_title('NTN-TDL-' + profile, loc='left', pad=16)
        axes[0,col].set_yscale('log')
        for ax in axes[:,col]:
            axes_style(ax); ax.set_xlabel('SNR (dB)'); ax.set_xticks([-4,-2,0,2,4,6])
        axes[0,col].set_ylabel('Activity error rate')
        axes[1,col].set_ylabel('Full-channel NMSE (dB)')
    fig.text(.075,.070,'n = physical scenes per profile and SNR. All methods use the same saved observations and estimated phases.',fontsize=11,color=MUTED)
    fig.text(.075,.032,'Tabulated power-delay and fading profiles under the fixed project geometry; estimated noise.',fontsize=11,color=MUTED)
    save(fig, 'cross_channel', source, [RETURNED + '/cross_channel/comparison'])


def denoising(name, folder, selected=None, aliases=()):
    source = folder + '/SUMMARY.json'; rows = read(source)['rows']
    if selected is not None:
        rows = [r for r in rows if r['method'] in selected]
    selected = methods(rows)
    n = {r.get('scenes',r.get('completed')) for r in rows}
    assert n == {500}
    with plt.rc_context({'font.family':'serif','font.serif':['STIXGeneral'],
                         'mathtext.fontset':'stix','font.size':8,'text.color':'black',
                         'axes.labelcolor':'black','xtick.color':'black','ytick.color':'black',
                         'axes.edgecolor':'black','axes.labelsize':9}):
        fig, ax = plt.subplots(figsize=(3.5, 3.25))
        fig.subplots_adjust(left=.17, right=.98, bottom=.15, top=.98)
        handles=[]
        for m in selected:
            group = sorted([r for r in rows if r['method'] == m], key=lambda r: -10*math.log10(r['variance']))
            assert len(group) == 6
            label=STYLES[m]['label']
            if m=='proposed': label=r'Proposed ($N_{\mathrm{train}}=50\,000$)'
            elif m=='proposed_small': label=r'Proposed ($N_{\mathrm{train}}=5\,000$)'
            elif m=='genie_bound': label='Genie MMSE (oracle)'
            handle,=ax.plot([-10*math.log10(r['variance']) for r in group],
                [r['nmse_db'] for r in group],**style(m),label=label,
                linewidth=1.25 if m.startswith('proposed') else 1.0,markersize=3.7,
                markerfacecolor='none',markeredgewidth=.85)
            handles.append(handle)
        by_method=dict(zip(selected,handles))
        legend_options=dict(fontsize=7,handlelength=2.1,handletextpad=.5,
                            labelspacing=.35,borderpad=.35,framealpha=1,
                            facecolor='white',edgecolor='#c0c0c0',fancybox=False)
        upper=ax.legend(handles=[by_method[m] for m in ['offgrid_sbl','gnn','gamp','somp'] if m in by_method],
                        loc='upper right',**legend_options)
        ax.add_artist(upper)
        lower=ax.legend(handles=[by_method[m] for m in ['proposed','proposed_small','noisy','gaussian','genie_bound'] if m in by_method],
                        loc='lower left',**legend_options)
        ax.set(xlabel='SNR (dB)',ylabel='NMSE (dB)',xticks=[-20,-10,0,10,20,30],
               xlim=(-21,31),ylim=(-65,25))
        ax.grid(True,color='#d6d6d6',linewidth=.5,linestyle=':')
        ax.set_axisbelow(True)
        ax.tick_params(direction='in',length=3,width=.7)
        for spine in ax.spines.values(): spine.set_linewidth(.7)
        fig.canvas.draw()
        for legend in (upper,lower):
            box=legend.get_window_extent(fig.canvas.get_renderer())
            assert not any(line.get_path().transformed(ax.transData).intersects_bbox(box,filled=False)
                           for line in handles),'Legend overlaps a data curve'
        save(fig, name, source, aliases, primary_stem=folder+'/denoising')


def convergence(name, folder, aliases=(), limit=None):
    source = folder + '/SUMMARY.json'; summary = read(source); groups = summary['groups']
    selected = methods(groups); snrs = sorted({g['snr_db'] for g in groups})
    n = groups[0]['curve'][0]['scenes']
    fig, axes = plt.subplots(1, len(snrs), figsize=(16,7.7))
    fig.subplots_adjust(left=.075,right=.975,bottom=.25,top=.64,wspace=.29)
    header(fig,'Convergence on off-grid AFDM channels',
           '40 candidate users  |  16 pilot frames  |  16 receive antennas  |  Activity probability = 0.1',selected,n)
    for ax,snr in zip(axes,snrs):
        for m in selected:
            group = next(g for g in groups if g['method']==m and g['snr_db']==snr)
            curve = [p for p in group['curve'] if limit is None or p['iteration']<=limit]
            assert all(p['scenes']==n for p in curve)
            markers = sorted({0,len(curve)-1,*range(0,len(curve),max(1,len(curve)//6))})
            line(ax,[p['iteration'] for p in curve],[p['nmse_db'] for p in curve],m,markers)
        axes_style(ax);ax.set_title(f'SNR = {snr:g} dB',loc='left',pad=16)
        ax.set(xlabel='Iteration / layer / selected atom',ylabel='Full-channel NMSE (dB)')
        if limit: ax.set_xlim(0,limit)
    fig.text(.075,.145,'n = paired physical scenes per SNR. Estimated phase and noise.',fontsize=11,color=MUTED)
    fig.text(.075,.097,'Curves follow the saved trajectories and actual iteration counts. Stopped scenes retain their final estimates.',fontsize=11,color=MUTED)
    fig.text(.075,.049,'Iteration counts are not equal computation budgets; lower NMSE is better.',fontsize=11,color=MUTED)
    save(fig,name,source,aliases)


def candidates():
    source = 'results/offgrid_candidates_20261019/SUMMARY.json'; rows=read(source)['rows']
    fig,axes=plt.subplots(1,3,figsize=(17,7.4));fig.subplots_adjust(left=.075,right=.98,bottom=.23,top=.65,wspace=.30)
    selected=[]
    for k,c,mark,ls in [(6,'#687B96','x','-.'),(12,'#168682','s','--'),(24,'#7158AC','^',':')]:
        m=f'offgrid_{k}';STYLES[m]=dict(label=f'Off-grid SBL ({k} candidates/user)',color=c,marker=mark,linestyle=ls);selected.append(m)
        group=sorted([r for r in rows if r['candidates_per_user']==k],key=lambda r:r['snr_db'])
        for ax,key in zip(axes,['aer','nmse_db','wall_seconds_median']):line(ax,[r['snr_db'] for r in group],[r[key] for r in group],m)
    header(fig,'Off-grid SBL candidate-count comparison','40 candidate users  |  16 pilot frames  |  120-iteration budget',selected,500)
    for ax,title,y in zip(axes,['Activity detection','Channel estimation','Conditional receiver time'],['Activity error rate','Full-channel NMSE (dB)','Median time (s)']):
        axes_style(ax);ax.set(title=title,xlabel='SNR (dB)',ylabel=y,xticks=[-4,-2,0,2,4,6])
    axes[0].set_yscale('log')
    fig.text(.075,.12,'n = paired physical scenes per SNR. Each configuration uses its independently calibrated activity threshold.',fontsize=11,color=MUTED)
    fig.text(.075,.07,'Timing excludes shared phase estimation; concurrent workloads may affect absolute time.',fontsize=11,color=MUTED)
    save(fig,'offgrid_candidates',source,['results/offgrid_candidates_20261019/comparison'])


def clean_superseded():
    # Current experiment previews and redundant extracted cloud figures only.
    paths=[]
    for folder in [ROOT/'results/local_baselines_20261018/preflight',ROOT/'results/local_baselines_20261018/progress',
                   ROOT/'results/density_ratio_smoke_20261018',
                   ROOT/(RETURNED+'/cpu-9900x-results-20261019/metadata/summaries')]:
        paths.extend(p for p in folder.rglob('*') if p.suffix.lower() in {'.png','.pdf','.svg','.eps'})
    for path in paths:
        REMOVED.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path)})
        path.unlink()


def diagnosis():
    folder='results/denoising_baseline_diagnosis_20261019'
    source='results/denoising_four_baselines_20261018/SUMMARY.json'
    rows=read(source)['rows'];extra={}
    for name in ['ALGEBRA_AND_DICTIONARY.json','OFFGRID_DECOMPOSITION.json']:
        p=folder+'/'+name;SOURCES[p]=sha(ROOT/p);extra[name]=json.loads((ROOT/p).read_text())
    selected=['offgrid_sbl','gnn','gamp','somp','noisy']
    fig,axes=plt.subplots(1,2,figsize=(17,8.5));fig.subplots_adjust(left=.075,right=.975,bottom=.24,top=.65,wspace=.26)
    header(fig,'Dictionary representation and reconstruction diagnostics',
           'Left: 500 scenes / 2,000 channels  |  Right: first 10 scenes / 40 channels at 30 dB',selected,500)
    for m in selected:
        group=sorted([r for r in rows if r['method']==m],key=lambda r:r['snr_db'])
        line(axes[0],[r['snr_db'] for r in group],[r['nmse_db'] for r in group],m)
    floor=extra['ALGEBRA_AND_DICTIONARY.json']['clean_full_grid_projection_nmse_db']
    axes[0].axhline(floor,color='#253247',linestyle='--',linewidth=1.3)
    axes[0].text(.02,.03,f'Clean 80-atom projection: {floor:.2f} dB',transform=axes[0].transAxes,fontsize=10,
                 bbox=dict(facecolor='white',alpha=.9,edgecolor='none'))
    axes[0].set(xlabel='SNR (dB)',ylabel='NMSE (dB)',title='(a) Dictionary representation',xticks=[-20,-10,0,10,20,30])
    data=extra['OFFGRID_DECOMPOSITION.json']
    keys=['ls_error','original_error','linearized_output_error','exact_atoms_ls_refit_error','oracle_true_positions_ls_error']
    values=[10*math.log10(sum(r[k] for r in data)/sum(r['energy'] for r in data)) for k in keys]
    axes[1].bar(range(5),values,color=['#7C8795','#168682','#BE7A10','#7158AC','#438363'])
    for i,value in enumerate(values):axes[1].text(i,value-1,f'{value:.2f}',ha='center',va='top',fontsize=10)
    axes[1].set(xticks=range(5),xticklabels=['LS','Off-grid\nSBL','Linearized\noutput','Exact atoms\nLS refit','True positions\nLS (oracle)'],
                ylim=(-55,0),ylabel='NMSE (dB)',title='(b) Reconstruction diagnostics')
    for ax in axes:axes_style(ax)
    fig.text(.075,.12,'The legend sample count applies to panel (a); panel (b) uses the fixed 10-scene diagnostic subset.',fontsize=11,color=MUTED)
    fig.text(.075,.07,'Diagnostic reconstructions retain their original scope; the true-position reference uses oracle information.',fontsize=11,color=MUTED)
    save(fig,'denoising_diagnosis',[source,*[folder+'/'+n for n in extra]],[folder+'/diagnosis'])


def main(clean=False):
    setup()
    scan('snr_comparison','results/baseline_comparison_500_20261018','Performance versus SNR',
         '40 candidate users  |  16 pilot frames  |  16 receive antennas','SNR (dB)','snr_db',
         aliases=['results/baseline_comparison_500_20261018/comparison'],svg=True)
    scan('snr_baselines',BASE+'/snr_comparison','Baseline performance versus SNR',
         '40 candidate users  |  16 pilot frames  |  16 receive antennas','SNR (dB)',aliases=[BASE+'/snr_comparison/comparison'])
    scan('pilot_frames',BASE+'/pilot_frames','Performance versus pilot frames',
         '40 candidate users  |  SNR = 0 dB  |  Activity probability = 0.1','Pilot frames',percent=True,aliases=[BASE+'/pilot_frames/comparison'])
    scan('activity_probability',BASE+'/activity_probability','Performance versus activity probability',
         '40 candidate users  |  16 pilot frames  |  SNR = 0 dB','Activity probability',percent=True,aliases=[BASE+'/activity_probability/comparison'])
    scan('user_count',RETURNED+'/user_count','Performance versus candidate users',
         '16 pilot frames  |  SNR = 0 dB  |  Activity probability = 0.1','Candidate users',aliases=[RETURNED+'/user_count/comparison'])
    cross_channel()
    denoising('channel_denoising','results/denoising_four_baselines_20261018')
    for name,folder,stem in [('convergence_original',BASE+'/convergence',BASE+'/convergence/convergence'),
                           ('convergence_300','results/convergence_300_20261018',None),
                           ('convergence_bg_tmp','results/bg_tmp_convergence_300_20261019/baselines',
                            'results/bg_tmp_convergence_300_20261019/baselines/convergence_baselines_300')]:
        convergence(name,folder,[stem] if stem else [])
        shortstem = stem.replace('baselines_300','baselines_first100') if stem and 'baselines_300' in stem else (stem+'_first100' if stem else None)
        convergence(name+'_first100',folder,[shortstem] if shortstem else [],100)
    candidates()
    if clean:clean_superseded()
    assert all(sha(ROOT/p)==h for p,h in SOURCES.items()),'Source statistics changed'
    manifest=dict(status='PASS',renderer=str(Path(__file__).relative_to(ROOT)),renderer_sha256=sha(Path(__file__)),
        reference='runs/convergence_300_20261018/figure_reference.png',styles=STYLES,
        source_statistics_unchanged=True,sources=SOURCES,figures=FIGURES,removed_derived_figures=REMOVED)
    (OUT/'FIGURES.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'status':'PASS','figure_sets':len(FIGURES),'removed_derived_figures':len(REMOVED)}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--clean',action='store_true')
    main(parser.parse_args().clean)
