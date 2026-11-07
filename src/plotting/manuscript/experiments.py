"""Render the seven manuscript experiments from their saved, verified rows."""
from copy import deepcopy
from types import SimpleNamespace
import math

import matplotlib.pyplot as plt
from matplotlib.legend import Legend
import plotting.style as style
from plotting.configurable import panel
from plotting.configurable import prepare

LEGEND = dict(fontsize=8, handlelength=2, handletextpad=.4, columnspacing=.85,
              borderpad=.3, labelspacing=.25, frameon=True, fancybox=False,
              framealpha=1, edgecolor='#777777')


def configure():
    style.configure()
    plt.rcParams.update({'font.size':8.5,'axes.labelsize':8.5,'axes.titlesize':8.5,
                         'xtick.labelsize':8.5,'ytick.labelsize':8.5})


def axis_style(ax, xlabel, xs):
    ax.set_xlabel(xlabel, labelpad=1)
    ax.set_ylabel('NMSE (dB)', labelpad=1)
    ax.set_xlim(min(xs), max(xs))
    ax.set_xticks(sorted(set(xs)))
    ax.tick_params(which='both', direction='in', top=True, right=True, pad=3, length=3, width=.55)
    ax.grid(True, which='major', color='#b9b9b9', alpha=.65, linewidth=.45)


def coordinate(row, key):
    return row[key] if key in row else row['parameters'][key]


def add_curves(ax, raw, cfg, channel=None):
    curves=[]
    for method in cfg['methods']:
        rows=sorted((r for r in raw['rows'] if r['method']==method and
                     (channel is None or r['channel_model']==channel)),
                    key=lambda r:coordinate(r,cfg['x']))
        if not rows:
            raise ValueError(f'Missing saved rows: {method}, {channel}')
        x=[coordinate(r,cfg['x']) for r in rows]
        y=[r['nmse_db'] for r in rows]
        line,=ax.plot(x,y,label=cfg['labels'][method],**cfg['styles'][method])
        if line.get_xdata().tolist()!=x or line.get_ydata().tolist()!=y:
            raise ValueError('Plotted values differ from saved values')
        curves.append(dict(method=method,channel=channel,metric='nmse_db',x=x,y=y))
    return curves


def dual(name, raw, cfg):
    panel_cfg=deepcopy(cfg['panel_config'])
    data=SimpleNamespace(**raw)
    prepare(data,panel_cfg)
    size=cfg.get('size_inches',(3.5,2.5))
    legend_fraction=cfg.get('legend_height_inches',.31)/size[1]
    fig=plt.figure(figsize=size,layout='constrained')
    fig.get_layout_engine().set(**panel_cfg['figure']['layout'],
                                rect=(0,legend_fraction,1,1-legend_fraction))
    grid=fig.add_gridspec(1,2)
    curves,handles=[],{}
    for j,metric in enumerate(['nmse_db','aer']):
        ax,zero=panel(fig,grid[0,j],data.rows,data,panel_cfg,metric,'')
        if zero is not None or len(ax.lines)!=len(data.methods):
            raise ValueError('Unexpected panels or missing methods')
        for method,line in zip(data.methods,ax.lines):
            rows=sorted((r for r in data.rows if r['method']==method),
                        key=lambda r:coordinate(r,cfg['x']))
            x=[coordinate(r,cfg['x']) for r in rows]
            y=[r[metric] for r in rows]
            if line.get_xdata().tolist()!=x or line.get_ydata().tolist()!=y:
                raise ValueError('Plotted values differ from saved values')
            if name=='pilot_frames':
                line.set_clip_on(True)
                line.set_clip_path(ax.patch)
            handles[method]=line
            curves.append(dict(method=method,channel=None,metric=metric,x=x,y=y))
    order=cfg['legend_order']
    legend=fig.legend([handles[m] for m in order],[handles[m].get_label() for m in order],
                     loc='lower center',bbox_to_anchor=(.5,.008),ncol=3,borderaxespad=0,
                     **dict(LEGEND,**cfg.get('legend_style',{})))
    legend.get_frame().set_linewidth(.45)
    return fig,curves


def draw(name,raw,cfg):
    configure()
    if name in ('snr_comparison','pilot_frames'):
        return dual(name,raw,cfg)
    if name=='cross_channel':
        fig,axes=plt.subplots(1,4,figsize=(7,2.6))
        fig.subplots_adjust(left=.075,right=.985,bottom=.64/2.6,top=1-.31/2.6,wspace=.34)
        curves=[]
        for i,(ax,channel) in enumerate(zip(axes,cfg['panel_order'])):
            curves+=add_curves(ax,raw,cfg,channel)
            axis_style(ax,'SNR (dB)',[-4,-2,0,2,4,6])
            ax.set_title('NTN-TDL-'+channel,pad=5)
            ax.set_ylim(-20,0)
            ax.set_yticks([-20,-15,-10,-5,0])
            if i: ax.set_ylabel('')
        fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',
                   bbox_to_anchor=(.52,.025),ncol=6,**LEGEND)
    elif name=='channel_denoising':
        fig,ax=plt.subplots(figsize=(3.5,3))
        fig.subplots_adjust(left=.155,right=.965,bottom=.83/3,top=1-.09/3)
        curves=add_curves(ax,raw,cfg)
        axis_style(ax,'SNR (dB)',[-20,-10,0,10,20,30])
        ax.set_ylim(-65,25)
        ax.set_yticks(list(range(-60,21,10)))
        handles=dict(zip(cfg['methods'],ax.lines))
        order=cfg['legend_order']
        fig.legend([handles[m] for m in order],[cfg['labels'][m] for m in order],
                   loc='lower center',bbox_to_anchor=(.5,.015),ncol=3,
                   **dict(LEGEND,handlelength=1.65,columnspacing=.55))
    else:
        fig,ax=plt.subplots(figsize=(3.5,2.65))
        fig.subplots_adjust(left=.155,right=.965,bottom=.46/2.65,top=1-.09/2.65)
        curves=add_curves(ax,raw,cfg)
        label={'convergence':'Receiver iteration','user_count':'Number of candidate devices',
               'activity_probability':'Nominal activity probability'}[name]
        axis_style(ax,label,[x for c in curves for x in c['x']])
        style.nmse_axis(ax,[y for c in curves for y in c['y']])
        if name=='convergence':
            ax.set_xticks(cfg.get('xticks',[1,20,40,60,85]))
            ax.legend(loc='upper right',**LEGEND)
        else:
            fig.subplots_adjust(bottom=.75/2.65)
            fig.legend(*ax.get_legend_handles_labels(),loc='lower center',
                       bbox_to_anchor=(.55,.015),ncol=3,**LEGEND)
    return fig,curves


def validate(fig,curves,cfg):
    if sum(len(c['x']) for c in curves)!=cfg['point_count']:
        raise ValueError('Unexpected number of curve points')
    if not all(math.isfinite(v) for c in curves for v in c['x']+c['y']):
        raise ValueError('Nonfinite plot values')
    fig.canvas.draw()
    if fig.get_layout_engine() is not None:
        fig.canvas.draw()
        fig.set_layout_engine(None)
    renderer=fig.canvas.get_renderer()
    legends=fig.findobj(Legend)
    if not legends: raise ValueError('Missing legend')
    for legend in legends:
        legend.get_frame().set_linewidth(.45)
        box=legend.get_window_extent(renderer)
        if any(t.get_fontsize()!=8 for t in legend.get_texts()):
            raise ValueError('Unexpected legend font size')
        if box.x0<0 or box.y0<0 or box.x1>fig.bbox.width or box.y1>fig.bbox.height:
            raise ValueError('Legend outside canvas')
        for ax in fig.axes:
            if legend in ax.get_children():
                if any(line.get_path().transformed(line.get_transform()).intersects_bbox(box,filled=False)
                       for line in ax.lines): raise ValueError('Legend overlaps curve')
            elif box.overlaps(ax.get_tightbbox(renderer)):
                raise ValueError('Legend overlaps panel labels')
    excluded=set()
    for ax in fig.axes:
        for axis,limits in [(ax.xaxis,ax.get_xlim()),(ax.yaxis,ax.get_ylim())]:
            for tick in axis.get_major_ticks()+axis.get_minor_ticks():
                if not min(limits)<=tick.get_loc()<=max(limits):
                    excluded.update([tick.label1,tick.label2])
    for text in fig.findobj(match=lambda t:hasattr(t,'get_text') and hasattr(t,'get_window_extent')):
        if text in excluded or not text.get_visible() or not text.get_text(): continue
        b=text.get_window_extent(renderer)
        if b.width and b.height and (b.x0 < -1 or b.y0 < -1 or b.x1>fig.bbox.width+1 or b.y1>fig.bbox.height+1):
            raise ValueError(f'Text outside canvas: {text.get_text()}')
