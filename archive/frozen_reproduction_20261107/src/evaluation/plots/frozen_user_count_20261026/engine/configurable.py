"""Configuration-driven plotting for the eight public experiment entry points."""
import argparse
from copy import deepcopy
from dataclasses import asdict
import json
import math
from pathlib import Path

import numpy as np
from matplotlib.ticker import LogLocator, NullFormatter
import style
from data import digest, read
from plot_selection import COORDINATES, load_saved, select

DEFAULT = {
    'version': 1, 'experiment': None, 'input': None, 'output': None,
    'selection': {'methods': None, 'conditions': {}, 'scenes': {}, 'per_scene': None},
    'labels': {}, 'styles': {},
    'plot': {'x': None, 'metrics': None, 'facet': None, 'facet_order': None,
             'panels': ['combined'], 'title': '', 'show_panel_titles': False, 'annotate': None,
             'facet_columns': 2},
    'axes': {'x': {'labelpad': 0, 'tickpad': 4}, 'nmse_db': {'labelpad': 0, 'tickpad': 4},
             'aer': {'scale': 'log', 'zeros': 'separate', 'labelpad': 0, 'tickpad': 4}},
    'legend': {'show': True, 'loc': 'auto', 'ncol': 1, 'fontsize': 6, 'groups': [], 'combined_metrics': None,
               'frameon': True, 'framealpha': 1, 'fancybox': False,
               'handlelength': 2.6, 'handletextpad': .4, 'borderpad': .3, 'labelspacing': .1},
    'figure': {'panel_size': [1.75, 2.2], 'separate_panel_size': [3.5, 2.2], 'font_family': 'Times New Roman',
               'font_size': 8.5, 'layout': {'w_pad': .01, 'h_pad': .02, 'wspace': 0, 'hspace': 0}, 'grid': True, 'minor_grid': True,
               'major_grid_color': '#909090', 'major_grid_alpha': .8, 'major_grid_linewidth': .65},
    'export': {'formats': ['pdf', 'svg', 'png'], 'dpi': 600, 'preview_dpi': 180},
}
AXIS_KEYS = {'label','scale','limits','ticks','ticklabels','zeros','tight','labelpad','tickpad'}
STYLE_KEYS = {'color','marker','linestyle','linewidth','markersize','markerfacecolor','markeredgecolor','markeredgewidth','markevery','alpha','zorder','clip_on'}
LEGEND_KEYS = set(DEFAULT['legend']) | {'bbox_to_anchor','frameon','framealpha','fancybox','title','handlelength',
                                     'labelspacing','handletextpad','borderpad'}


def merge(base, override):
    result = deepcopy(base)
    for k,v in override.items():
        result[k] = merge(base[k], v) if isinstance(v,dict) and isinstance(base.get(k),dict) else v
    return result


def reject_keys(value, allowed, name):
    if not isinstance(value,dict) or set(value)-set(allowed):
        raise ValueError(f'Unknown keys or non-object in {name}: {value}')


def resolve_config(path, experiment, input_override=None, output_override=None):
    path = Path(path).resolve()
    raw = read(path)
    reject_keys(raw, DEFAULT, 'configuration')
    for key in ('selection','plot','figure','export'):
        reject_keys(raw.get(key,{}), DEFAULT[key], key)
    reject_keys(raw.get('figure',{}).get('layout',{}), {'w_pad','h_pad','wspace','hspace'}, 'figure.layout')
    reject_keys(raw.get('legend',{}), LEGEND_KEYS, 'legend')
    groups=raw.get('legend',{}).get('groups',[])
    if not isinstance(groups,list):
        raise ValueError('legend.groups must be a list')
    for group in groups:
        reject_keys(group,(LEGEND_KEYS-{'groups','show'}) | {'methods'},'legend.groups')
        if not isinstance(group.get('methods'),list) or not group['methods'] or any(not isinstance(m,str) for m in group['methods']):
            raise ValueError('Each legend group needs a nonempty methods list')
    for key,opts in raw.get('axes',{}).items():
        reject_keys(opts, AXIS_KEYS, 'axes.'+key)
    for key,opts in raw.get('styles',{}).items():
        reject_keys(opts, STYLE_KEYS, 'styles.'+key)
    cfg = merge(DEFAULT, raw)
    if cfg['version'] != 1 or cfg['experiment'] not in (None,experiment):
        raise ValueError('Configuration version/experiment does not match this entry point')
    cfg['experiment'] = experiment
    for key,override in [('input',input_override),('output',output_override)]:
        value = override or cfg[key]
        if not value:
            raise ValueError(f'Set {key} in JSON or --{key}')
        p = Path(value)
        cfg[key] = str(p.resolve() if override else (path.parent/p).resolve())
    if cfg['selection']['per_scene']:
        cfg['selection']['per_scene'] = str((path.parent/Path(cfg['selection']['per_scene'])).resolve())
    if not set(cfg['plot']['panels']) <= {'combined','separate'} or not cfg['plot']['panels']:
        raise ValueError('plot.panels must contain combined and/or separate')
    if len(set(cfg['plot']['panels'])) != len(cfg['plot']['panels']):
        raise ValueError('Duplicate panel layout')
    if not cfg['export']['formats'] or not set(cfg['export']['formats']) <= {'pdf','svg','png'}:
        raise ValueError('export.formats supports pdf, svg and png')
    if any(type(cfg['export'][k]) is not int or cfg['export'][k]<=0 for k in ('dpi','preview_dpi')):
        raise ValueError('Export DPI must be positive integers')
    if len(cfg['figure']['panel_size'])!=2 or min(cfg['figure']['panel_size'])<=0:
        raise ValueError('figure.panel_size needs positive [width, height] in inches')
    separate_size = cfg['figure']['separate_panel_size']
    if separate_size is not None and (len(separate_size)!=2 or min(separate_size)<=0):
        raise ValueError('figure.separate_panel_size needs positive [width, height] in inches')
    if type(cfg['plot']['facet_columns']) is not int or cfg['plot']['facet_columns']<=0:
        raise ValueError('plot.facet_columns must be a positive integer')
    for opts in cfg['axes'].values():
        if opts.get('scale','linear') not in ('linear','log','auto') or opts.get('zeros','separate') not in ('separate','clip','error'):
            raise ValueError('Invalid axis scale or zeros policy')
        if 'limits' in opts and (len(opts['limits'])!=2 or opts['limits'][0]>=opts['limits'][1]):
            raise ValueError('Axis limits must be [lower, upper]')
        if opts.get('scale')=='log' and 'limits' in opts and opts['limits'][0]<=0:
            raise ValueError('Log axis limits must be positive')
        if 'ticklabels' in opts and len(opts['ticklabels'])!=len(opts.get('ticks',[])):
            raise ValueError('ticklabels must match explicit ticks')
    return cfg


def value(row, key):
    return row['parameters'][key] if key in row['parameters'] else row[key]


def prepare(data, cfg):
    legend_groups=cfg['legend'].get('groups',[])
    if cfg['legend']['show'] and legend_groups:
        grouped=[m for group in legend_groups for m in group['methods']]
        if len(grouped)!=len(set(grouped)) or any(grouped.count(m)!=1 for m in data.methods):
            raise ValueError('Legend groups must include each selected method exactly once')
    if data.experiment == 'runtime_comparison':
        timing = str(data.metadata.get('timing','')).lower()
        if data.metadata.get('parallel_execution') or 'concurrent' in timing or 'contention' in timing:
            raise ValueError('Runtime comparison requires isolated measurements, not concurrent throughput')
    plot = cfg['plot']
    plot['x'] = plot['x'] or COORDINATES[data.experiment]
    plot['metrics'] = plot['metrics'] or (['nmse_db'] if data.experiment=='channel_denoising' else ['nmse_db','aer'])
    if not isinstance(plot['metrics'],list) or len(set(plot['metrics']))!=len(plot['metrics']):
        raise ValueError('plot.metrics must be a list of distinct saved numeric fields')
    legend_metrics=cfg['legend'].get('combined_metrics')
    if legend_metrics is not None and (not isinstance(legend_metrics,list) or not legend_metrics or
                                      not set(legend_metrics)<=set(plot['metrics'])):
        raise ValueError('legend.combined_metrics must name plotted metrics')
    if data.experiment=='cross_channel' and plot['facet'] is None:
        plot['facet'] = 'channel_model'
    if data.metadata.get('historical_protocol') and plot['x']=='variance':
        plot['x'] = 'snr_db'
    facet = plot['facet']
    groups = list(dict.fromkeys(value(r,facet) for r in data.rows)) if facet else [None]
    if plot['facet_order'] is not None:
        if set(plot['facet_order'])!=set(groups) or len(plot['facet_order'])!=len(groups):
            raise ValueError('facet_order must contain each selected facet once; filter using selection.conditions')
        groups = plot['facet_order']
    for group in groups:
        for method in data.methods:
            rows = [r for r in data.rows if r['method']==method and (not facet or value(r,facet)==group)]
            if not rows:
                raise ValueError(f'Missing curve: {method}, {group}')
            xs = [value(r,plot['x']) for r in rows]
            if len(set(xs))!=len(xs):
                raise ValueError('Repeated x coordinates: select conditions or set plot.facet to separate them')
            for key in [plot['x']]+plot['metrics']:
                if any(not isinstance(value(r,key),(int,float)) or not math.isfinite(value(r,key)) for r in rows):
                    raise ValueError(f'Not a finite numeric field: {key}')
            if data.experiment=='runtime_comparison' and len({r.get('backend') for r in rows})!=1:
                raise ValueError('A runtime curve cannot mix backends')
    return groups


def method_style(method, index, data, cfg):
    if data.metadata.get('historical_protocol'):
        from channel_denoising import historical_style
        options = historical_style(method)
    elif method in style.STYLES or method=='DU':
        options = style.style('proposed' if method=='DU' else method)
    else:
        options = dict(color=style.plt.get_cmap('tab10')(index%10), marker=['o','s','^','D','v'][index%5], linewidth=1.2)
    colored_denoiser = data.experiment=='channel_denoising' and method=='pretrained_colored_first'
    awgn_denoiser = data.experiment=='channel_denoising' and (method=='pretrained_first' or
                    (method=='proposed' and data.metadata.get('historical_protocol')))
    if method=='C_STMP' or colored_denoiser:
        options.update(color='#b83253',marker='o',linestyle='-',linewidth=1.7)
    elif method=='STMP' or awgn_denoiser:
        options.update(color='#2878b5',marker='s',linestyle='-',linewidth=1.4)
    options.update(markersize=3.5, markeredgewidth=.7,
                   linewidth=.9 if options.get('linestyle','-')=='-' else .65, clip_on=False)
    return options | cfg['styles'].get(method,{})


def apply_axis(ax, axis, opts):
    if 'labelpad' in opts:
        getattr(ax,axis+'axis').labelpad=opts['labelpad']
    if 'tickpad' in opts:
        ax.tick_params(axis=axis,pad=opts['tickpad'])
    if 'label' in opts:
        getattr(ax,'set_'+axis+'label')(opts['label'])
    if 'ticks' in opts:
        getattr(ax,'set_'+axis+'ticks')(opts['ticks'], **({'labels':opts['ticklabels']} if 'ticklabels' in opts else {}))
    if 'limits' in opts:
        getattr(ax,'set_'+axis+'lim')(opts['limits'])


def panel(fig, slot, rows, data, cfg, metric, title):
    xkey = cfg['plot']['x']
    yopts = cfg['axes'].get(metric,{})
    ys = [value(r,metric) for r in rows]
    scale = yopts.get('scale','auto' if metric=='aer' else 'linear')
    if metric=='aer' and any(y<0 or y>1 for y in ys):
        raise ValueError('AER must be a probability')
    if scale=='auto':
        scale = 'log' if metric=='aer' and min(ys)>0 else 'linear'
    has_log_zero = scale=='log' and min(ys)==0
    zero_policy = yopts.get('zeros','separate')
    zero_strip = has_log_zero and zero_policy=='separate'
    if scale=='log' and (min(ys)<0 or (has_log_zero and zero_policy=='error')):
        raise ValueError('Nonpositive log-axis values; use linear scale or zeros=separate/clip')
    if zero_strip:
        inner = slot.subgridspec(2,1,height_ratios=[5,max(1,len(data.methods)*.4)],hspace=.08)
        ax = fig.add_subplot(inner[0]); zero = fig.add_subplot(inner[1],sharex=ax)
        ax.tick_params(labelbottom=False)
        zero_labels=[cfg['labels'].get(m,data.metadata.get('labels',{}).get(m,style.LABELS.get(m,m))) for m in data.methods]
        zero.set_yticks(range(len(data.methods)),labels=zero_labels,fontsize=7)
        zero.set_ylim(len(data.methods)-.5,-.5)
        zero.set_ylabel('AER = 0' if metric=='aer' else 'Observed zero',fontsize=8)
        bottom = zero
    else:
        ax = fig.add_subplot(slot); zero = None; bottom = ax
    for i,method in enumerate(data.methods):
        group = sorted([r for r in rows if r['method']==method],key=lambda r:value(r,xkey))
        x = np.asarray([value(r,xkey) for r in group]); y = np.asarray([value(r,metric) for r in group])
        label = cfg['labels'].get(method, data.metadata.get('labels',{}).get(method,style.LABELS.get(method,method)))
        if method in ('DU','proposed') and data.experiment!='channel_denoising' and method not in cfg['labels']:
            label = 'DU'
        if data.experiment=='runtime_comparison':
            label += ' ('+str(group[0].get('backend','unspecified'))+')'
        options = method_style(method,i,data,cfg)
        ax.plot(x,np.where(y==0,np.nan,y) if zero_strip else y,label=label,**options)
        if zero is not None:
            # Separate method rows prevent coincident zero markers from hiding curves.
            zero.plot(x[y==0],np.full(sum(y==0),i),**(options | {'linestyle':'none'}))
        if cfg['plot']['annotate']:
            for xx,yy,r in zip(x,y,group):
                target = zero if zero_strip and yy==0 else ax
                target.annotate(str(value(r,cfg['plot']['annotate'])),(xx,i if target is zero else yy),xytext=(3,3),textcoords='offset points',fontsize=8)
    xopts = cfg['axes']['x']
    xscale = xopts.get('scale','log' if xkey in ('variance','mean_end_to_end_seconds') else 'linear')
    if xscale=='auto': xscale='linear'
    xs = [value(r,xkey) for r in rows]
    if xscale=='log' and min(xs)<=0:
        raise ValueError('Log x coordinates must be positive')
    ax.set_xscale(xscale); ax.set_yscale(scale)
    ax.set_ylabel({'nmse_db':'NMSE (dB)','aer':'AER'}.get(metric,metric))
    xlabel = {'snr_db':'SNR (dB)','frames':'Number of pilot frames','users':'Number of users',
              'activity_probability':'Activity probability','variance':'Complex AWGN variance',
              'mean_end_to_end_seconds':'Mean end-to-end time (s)'}.get(xkey,xkey)
    bottom.set_xlabel(xopts.get('label',xlabel))
    if xscale=='linear': bottom.set_xticks(sorted(set(xs)))
    if metric=='nmse_db' and scale=='linear': style.nmse_axis(ax,ys)
    if metric=='aer' and scale=='linear': ax.set_ylim(bottom=0)
    if scale=='log':
        positive = [y for y in ys if y>0]
        if positive:
            lower = math.floor(math.log10(min(positive)))
            upper = math.ceil(math.log10(max(positive)))
            if lower==upper: lower-=1
            ax.set_ylim(10.**lower, 10.**upper)
        else:
            ax.set_ylim(1e-5,1)
    if yopts.get('tight'):
        visible_ys=[y for y in ys if scale!='log' or y>0]
        if visible_ys and min(visible_ys)<max(visible_ys):
            ax.set_ylim(min(visible_ys),max(visible_ys))
    if scale=='log':
        ax.yaxis.set_minor_locator(LogLocator(base=10,subs=np.arange(2,10)))
        ax.yaxis.set_minor_formatter(NullFormatter())
    apply_axis(bottom,'x',xopts);apply_axis(ax,'y',yopts)
    if has_log_zero and zero_policy=='clip':
        # Display-only placement at the final axis floor. Saved pooled counts,
        # probabilities and PLOT_DATA retain their exact zeros.
        floor = ax.get_ylim()[0]
        for line in ax.lines:
            line_y = np.asarray(line.get_ydata())
            line.set_ydata(np.where(line_y==0, floor, line_y))
    for target in (ax,zero):
        if target is not None:
            target.grid(False,which='both')
            if cfg['figure']['grid']:
                target.grid(True,which='major',color=cfg['figure'].get('major_grid_color','#909090'),
                            alpha=cfg['figure'].get('major_grid_alpha',.8),
                            linewidth=cfg['figure'].get('major_grid_linewidth',.65))
                if target is ax and scale=='log' and cfg['figure'].get('minor_grid',True):
                    target.grid(True,which='minor',axis='y',color='#d4d4d4',linestyle=':',linewidth=.4)
            target.tick_params(direction='in',top=True,right=True)
            target.margins(x=0)
    ax.set_title(title if cfg['plot']['show_panel_titles'] else '')
    if cfg['legend']['show']:
        legend_opts={k:v for k,v in cfg['legend'].items() if k not in ('show','groups','combined_metrics')}
        groups=cfg['legend'].get('groups',[])
        if groups:
            if legend_opts['loc']=='auto':legend_opts['loc']='best'
            handles=dict(zip(data.methods,ax.lines))
            legends=[]
            for group in groups:
                selected=[handles[m] for m in group['methods'] if m in handles]
                if not selected:
                    continue
                opts=legend_opts | {k:v for k,v in group.items() if k!='methods'}
                legends.append(ax.legend(handles=selected,**opts))
            for legend in legends[:-1]:
                ax.add_artist(legend)
        elif cfg['legend']['loc']!='auto':
            ax.legend(**legend_opts)
    return ax, zero


def render(data, out, cfg):
    groups = prepare(data,cfg)
    metrics = cfg['plot']['metrics'];facet = cfg['plot']['facet']
    layouts = []
    if 'combined' in cfg['plot']['panels']:
        layouts.append((data.experiment,metrics))
    if 'separate' in cfg['plot']['panels']:
        layouts.extend((data.experiment+'_'+m,[m]) for m in metrics)
    files=[]
    legend_layouts=[]
    with style.plt.rc_context():
        style.configure()
        style.plt.rcParams.update({'font.family':cfg['figure']['font_family'],'font.size':cfg['figure']['font_size'],
                                  'axes.labelsize':cfg['figure']['font_size'],'axes.titlesize':cfg['figure']['font_size'],
                                  'xtick.labelsize':cfg['figure']['font_size'],'ytick.labelsize':cfg['figure']['font_size']})
        for name,selected_metrics in layouts:
            specs = [(g,m) for g in groups for m in selected_metrics]
            cols = len(selected_metrics) if len(selected_metrics)>1 else min(len(groups),cfg['plot']['facet_columns'])
            nrows = math.ceil(len(specs)/cols)
            width,height=cfg['figure']['panel_size']
            if name != data.experiment and cfg['figure']['separate_panel_size'] is not None:
                width,height=cfg['figure']['separate_panel_size']
            fig=style.plt.figure(figsize=(width*cols,height*nrows),layout='constrained')
            if cfg['figure']['layout']:
                fig.get_layout_engine().set(**cfg['figure']['layout'])
            grid=fig.add_gridspec(nrows,cols)
            try:
                figure_cfg=cfg
                if name!=data.experiment and cfg['legend'].get('combined_metrics') is not None:
                    # A standalone metric needs its own complete, independently placed legend.
                    figure_cfg=merge(cfg,{'legend':{'combined_metrics':None,'groups':[],'loc':'auto'}})
                panels=[]
                for i,(group,metric) in enumerate(specs):
                    rows=[r for r in data.rows if not facet or value(r,facet)==group]
                    metric_title={'nmse_db':'Channel denoising' if data.experiment=='channel_denoising' else 'Channel estimation',
                                  'aer':'Activity detection'}.get(metric,metric)
                    title=(str(group)+' — ' if facet else '')+metric_title
                    panel_cfg=figure_cfg
                    legend_metrics=figure_cfg['legend'].get('combined_metrics')
                    show_here=(name!=data.experiment or legend_metrics is None or metric in legend_metrics)
                    if not show_here:
                        panel_cfg=merge(figure_cfg,{'legend':{'show':False}})
                    ax,_=panel(fig,grid[i//cols,i%cols],rows,data,panel_cfg,metric,title)
                    panels.append((ax,group,metric))
                if cfg['plot']['title']:fig.suptitle(cfg['plot']['title'])
                if figure_cfg['legend']['show'] and figure_cfg['legend']['loc']=='auto' and not figure_cfg['legend'].get('groups'):
                    from legend_layout import automatic_legend
                    fig.canvas.draw()
                    limits=[(ax.get_xlim(),ax.get_ylim()) for ax,_,_ in panels]
                    for ax,group,metric in panels:
                        if name==data.experiment and cfg['legend'].get('combined_metrics') is not None and metric not in cfg['legend']['combined_metrics']:
                            continue
                        chosen=automatic_legend(ax,data.methods,figure_cfg['legend'])
                        legend_layouts.append(dict(figure=name,facet=group,metric=metric,groups=chosen))
                    fig.canvas.draw()
                    assert limits==[(ax.get_xlim(),ax.get_ylim()) for ax,_,_ in panels], 'Legend changed axis limits'
                for ext in cfg['export']['formats']:
                    p=out/(name+'.'+ext);fig.savefig(p,dpi=cfg['export']['dpi']);files.append(p)
                p=out/(name+'_preview.png');fig.savefig(p,dpi=cfg['export']['preview_dpi']);files.append(p)
            finally:
                style.plt.close(fig)
    if legend_layouts:
        (out/'LEGEND_LAYOUT.json').write_text(json.dumps(legend_layouts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return files


def execute_config(experiment, argv):
    parser=argparse.ArgumentParser(description='Plot saved results using a JSON configuration; no inference/training')
    parser.add_argument('--config',type=Path,default=Path(__file__).resolve().parents[2]/'configs'/'plots'/(experiment+'.json'),
                        help='Defaults to the matching src/configs/plots/<experiment>.json')
    parser.add_argument('--input',type=Path);parser.add_argument('--output',type=Path)
    parser.add_argument('--aer-scale',choices=['auto','linear','log'])
    args=parser.parse_args(argv)
    try:
        cfg=resolve_config(args.config,experiment,args.input,args.output)
        if args.aer_scale:cfg['axes']['aer']['scale']=args.aer_scale
        out=Path(cfg['output'])
        if out.exists():raise ValueError('Output directory already exists; choose a new directory')
        data=select(load_saved(cfg['input'],experiment),cfg['selection'])
        prepare(data,cfg)
        out.mkdir(parents=True)
        files=render(data,out,cfg)
        from common import caption
        notes=['Only saved results are plotted; no inference or training.',
               'Scene and condition selection is recorded in CONFIG.json and PLOT_DATA.json.']
        if any(opts.get('zeros')=='clip' for opts in cfg['axes'].values()):
            notes.append('Observed zeros are drawn at the logarithmic axis lower boundary for display only; saved statistics remain exactly zero.')
        else:
            notes.append('On logarithmic axes, observed zeros are shown in a separate strip; they are never replaced by epsilon.')
        if data.metadata.get('limitations'):notes.append('Source limitations: '+str(data.metadata['limitations']))
        if data.metadata.get('historical_protocol'):notes.append('Historical Proposed curves are denoisers, not the DU receiver; Genie uses truth.')
        description=caption(data,notes)
        for name,obj in [('CONFIG.json',cfg),('PLOT_DATA.json',asdict(data))]:
            (out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
        (out/'caption.txt').write_text(description+'\n',encoding='utf-8')
        if 'pdf' in cfg['export']['formats']:
            includes=[r'\includegraphics[width=\linewidth]{'+p.name+'}' for p in files if p.suffix=='.pdf']
            (out/'figure_include.tex').write_text('\n'.join(includes)+'\n',encoding='utf-8')
        manifest=dict(status='PLOTTED',experiment=experiment,scenes=data.scenes,methods=data.methods,
                      config_source=str(args.config.resolve()),config_source_sha256=digest(args.config),
                      source=data.metadata,inference_started=False,training_started=False,
                      scripts={p.name:digest(p) for p in Path(__file__).parent.glob('*.py')},
                      files={p.name:digest(p) for p in out.iterdir() if p.is_file()})
        (out/'FIGURES.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(status='PLOTTED',scenes=data.scenes,path=str(out),files=len(files)),ensure_ascii=False))
        return 0
    except (ValueError,KeyError,TypeError,FileNotFoundError) as error:
        parser.error(str(error))
