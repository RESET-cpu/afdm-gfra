"""Shared manuscript style chosen by the user; no experiment data here."""
from pathlib import Path
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import font_manager
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator
from matplotlib.ticker import LogFormatterMathtext
from matplotlib.ticker import NullFormatter
from matplotlib.ticker import MaxNLocator

LABELS = {'STMP':'STMP','C_STMP':'C-STMP','offgrid_sbl':'Off-grid SBL','gnn':'GNN-ASPL','gamp':'GAMP-SBL',
          'somp':'SOMP','STMP_gaussian':'STMP (Gaussian evidence)',
          'noisy':'Noisy query','gaussian':'Gaussian mean','genie_bound':'Genie (truth used)',
          'pretrained_first':'Pretrained first score',
          'pretrained_colored_first':'Colored-trained first score'}
# Colors and baseline styles: historical baseline_comparison_600_20261017/report.py.
# User change: STMP is red, dashed, and uses hollow circles.
STYLES = {
    'STMP':dict(color='#b83253',marker='o',linestyle='--',linewidth=1.4),
    'C_STMP':dict(color='#2878b5',marker='s',linestyle='-',linewidth=1.7),
    'offgrid_sbl':dict(color='#20847c',marker='s',linestyle='--',linewidth=1.0),
    'gnn':dict(color='#745c9f',marker='^',linestyle='-.',linewidth=1.0),
    'gamp':dict(color='#b7802a',marker='D',linestyle=':',linewidth=1.0),
    'somp':dict(color='#6d7b8e',marker='x',linestyle='--',linewidth=1.0),
    'STMP_gaussian':dict(color='#20847c',marker='s',linestyle='--',linewidth=1.0),
    'noisy':dict(color='#6d7b8e',marker='x',linestyle='--',linewidth=1.0),
    'gaussian':dict(color='#20847c',marker='s',linestyle='--',linewidth=1.0),
    'genie_bound':dict(color='#b7802a',marker='D',linestyle=':',linewidth=1.0),
    'pretrained_first':dict(color='#b83253',marker='o',linestyle='--',linewidth=1.4),
    'pretrained_colored_first':dict(color='#2878b5',marker='^',linestyle='-',linewidth=1.4),
}


def configure():
    path=Path('C:/Windows/Fonts/times.ttf')
    if path.exists():
        font_manager.fontManager.addfont(str(path))
    font_manager.findfont('Times New Roman',fallback_to_default=False)
    plt.rcParams.update({'font.family':'Times New Roman','mathtext.fontset':'stix','font.size':10,
        'axes.labelsize':11,'axes.titlesize':11,'xtick.labelsize':10,'ytick.labelsize':10,'legend.fontsize':9,
        'axes.linewidth':.6,'axes.spines.top':True,'axes.spines.right':True,
        'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white',
        'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'path','axes.unicode_minus':False})


def style(method):
    if method not in STYLES:
        raise ValueError(f'Add an explicit, stable plotting style for method {method}.')
    return dict(STYLES[method],markersize=6,markeredgewidth=1.1,markerfacecolor='white')


def axes_style(ax,xlabel,ylabel,xvalues,xscale='linear',yscale='linear'):
    ax.set_xlabel(xlabel,labelpad=3);ax.set_ylabel(ylabel,labelpad=4)
    ax.set_xscale(xscale);ax.set_yscale(yscale)
    ax.tick_params(which='both',direction='in',top=True,right=True,length=3,width=.55,pad=3)
    ax.tick_params(which='minor',length=1.7,width=.4)
    ax.grid(True,which='major',color='#b9b9b9',linewidth=.45,alpha=.8)
    if xscale=='linear':
        ax.set_xticks(sorted(set(xvalues)))
    # Put the first and last measured coordinates on the frame, as in the reference.
    ax.margins(x=0,y=.04)
    if yscale=='log':
        ax.yaxis.set_major_locator(LogLocator(base=10))
        ax.yaxis.set_major_formatter(LogFormatterMathtext(base=10))
        ax.yaxis.set_minor_locator(LogLocator(base=10,subs=np.arange(2,10)))
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.grid(True,which='minor',axis='y',color='#d4d4d4',linestyle=':',linewidth=.4)
    else:
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
    legend=ax.legend(loc='best',frameon=True,fancybox=False,framealpha=1,
        facecolor='white',edgecolor='#777777',handlelength=2.4,borderpad=.35,
        labelspacing=.25,handletextpad=.55,borderaxespad=.45)
    legend.get_frame().set_linewidth(.45)


def nmse_axis(ax, values):
    lower = 5 * math.floor(min(values) / 5)
    # Current receiver curves end at 0 dB; retain positive results in other experiments.
    upper = max(0, 5 * math.ceil(max(values) / 5))
    if lower == upper:
        lower -= 5
    ax.set_ylim(lower, upper)
    ax.set_yticks(np.arange(lower, upper + 1, 5))


def compact_layout(fig):
    # Keep physical publication dimensions, while fitting labels close to page edges.
    fig.tight_layout(pad=.25, w_pad=.7, h_pad=1.0)


def aer_scale(values,requested='auto'):
    if any(v<0 or v>1 or not math.isfinite(v) for v in values):
        raise ValueError('AER must be a probability in [0,1].')
    if requested=='log' and any(v==0 for v in values):
        raise ValueError('Observed zero AER cannot be plotted on a log axis. Use --aer-scale auto or linear; zeros are never replaced.')
    return ('linear' if any(v==0 for v in values) else 'log') if requested=='auto' else requested


def panel(ax,data,parameter,xlabel,metric,*,xscale='linear',requested_aer_scale='auto'):
    xvalues=[];yvalues=[]
    for method in data.methods:
        group=sorted((r for r in data.rows if r['method']==method),key=lambda r:r['parameters'][parameter])
        x=[r['parameters'][parameter] for r in group];y=[r[metric] for r in group]
        if len(x)!=len(set(x)):
            raise ValueError('Repeated x values: split channel profiles or other conditions before plotting.')
        ax.plot(x,y,label=LABELS.get(method,method),clip_on=False,**style(method))
        xvalues.extend(x);yvalues.extend(y)
    if xscale=='log' and any(x<=0 for x in xvalues):
        raise ValueError('Log x coordinates must be positive.')
    scale=aer_scale(yvalues,requested_aer_scale) if metric=='aer' else 'linear'
    axes_style(ax,xlabel,'AER' if metric=='aer' else 'NMSE (dB)',xvalues,xscale,scale)
    if metric=='aer':
        if scale=='linear':
            ax.set_ylim(bottom=0)
        else:
            lower=10**math.floor(math.log10(min(yvalues)))
            upper=max(yvalues)*1.08
            ax.set_ylim(lower,upper)
    else:
        nmse_axis(ax,yvalues)
    return scale


def save(fig,out,name):
    compact_layout(fig)
    for suffix in ('pdf','svg','png'):
        fig.savefig(out/f'{name}.{suffix}',dpi=600)
    fig.savefig(out/f'{name}_preview.png',dpi=180)
    plt.close(fig)


def receiver_sweep(data,out,name,parameter,xlabel,requested_aer_scale='auto'):
    fig,axes=plt.subplots(1,2,figsize=(7.16,2.90))
    scale=None
    for ax,metric,title in zip(axes,('nmse_db','aer'),('(a) Channel estimation','(b) Activity detection')):
        s=panel(ax,data,parameter,xlabel,metric,requested_aer_scale=requested_aer_scale)
        if metric=='aer':scale=s
        ax.set_title(title,pad=4)
    save(fig,out,name)
    outputs=[(name,True)]
    for metric,suffix in (('nmse_db','nmse'),('aer','aer')):
        fig,ax=plt.subplots(figsize=(3.5,2.65))
        panel(ax,data,parameter,xlabel,metric,requested_aer_scale=requested_aer_scale)
        save(fig,out,name+'_'+suffix);outputs.append((name+'_'+suffix,False))
    return outputs,[f'AER is plotted as a probability on a {scale} axis; observed zeros are never replaced.']
