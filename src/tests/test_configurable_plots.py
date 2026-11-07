"""Configuration and paired aggregation tests using explicitly synthetic data."""
import copy
import csv
import json
import math
import sys
from pathlib import Path

import pytest


from test_paper_plotting import fixture, CONDITIONS
from plotting.configurable import DEFAULT, prepare, render, resolve_config, panel, execute_config
from plotting.plot_selection import load_saved, select
import plotting.style as style


@pytest.mark.parametrize('experiment', CONDITIONS)
def test_configured_eight_entries(tmp_path, experiment, monkeypatch):
    source,_,_=fixture(tmp_path,experiment)
    cfg=copy.deepcopy(DEFAULT)
    cfg['experiment']=experiment
    cfg['selection']['methods']=['pretrained_first','noisy'] if experiment=='channel_denoising' else ['STMP']
    data=select(load_saved(source,experiment),cfg['selection'])
    method=data.methods[0]
    cfg['labels'][method]='Custom legend'
    cfg['styles'][method]={'color':'#123456','marker':'D'}
    cfg['export']['formats']=['png'];cfg['export']['dpi']=60
    cfg['export']['preview_dpi']=40
    figures=[]
    original=style.plt.Figure.savefig
    def inspect(fig,path,**kwargs):
        fig.canvas.draw()
        for ax in fig.axes:
            assert ax.lines[0].get_label() in ('Custom legend','Custom legend (cuda)')
            assert ax.lines[0].get_color()=='#123456'
            assert len(ax.lines)==len(data.methods)
        figures.append(path)
        original(fig,path,**kwargs)
    monkeypatch.setattr(style.plt.Figure,'savefig',inspect)
    assert render(data,tmp_path,cfg)==figures


def scene_fixture(tmp_path):
    source,_,_=fixture(tmp_path)
    data=load_saved(source,'snr_comparison')
    data.metadata['scene_ids']=[10,11]
    path=tmp_path/'per_scene.csv'
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['scene','method','snr_db','full_error','signal_energy','active','inactive','misses','false_alarms'])
        writer.writeheader()
        for r in data.rows:
            for scene,error,energy,misses in [(10,1,2,0),(11,9,100,1)]:
                writer.writerow(dict(scene=scene,method=r['method'],snr_db=r['parameters']['snr_db'],
                                     full_error=error,signal_energy=energy,active=4,inactive=36,misses=misses,false_alarms=0))
    return data


def test_pooling_scene_ids_filters_and_order(tmp_path):
    data=scene_fixture(tmp_path)
    selected=select(data,dict(methods=['gnn','STMP'],conditions={'snr_db':[-4,0]},scenes={'ids':[10,11]}))
    assert selected.methods==['gnn','STMP']
    assert len(selected.rows)==4
    assert selected.rows[0]['nmse_db']==pytest.approx(10*math.log10(10/102))
    assert selected.rows[0]['aer']==1/80
    first=select(data,dict(methods=['STMP'],scenes={'first':1}))
    assert first.scenes==1 and first.rows[0]['aer']==0
    assert first.metadata['scene_ids']==[10]


def test_missing_duplicate_scene_is_rejected(tmp_path):
    data=scene_fixture(tmp_path)
    p=tmp_path/'per_scene.csv';lines=p.read_text().splitlines()
    p.write_text('\n'.join(lines[:-1]))
    with pytest.raises(ValueError,match='paired scene records'):
        select(data,dict(scenes={'ids':[10,11]}))
    p.write_text('\n'.join(lines+[lines[1]]))
    with pytest.raises(ValueError,match='paired scene records'):
        select(data,dict(scenes={'ids':[10,11]}))


def test_zero_log_strip_no_epsilon_and_axis_options(tmp_path):
    data=scene_fixture(tmp_path)
    data=select(data,dict(methods=['STMP'],scenes={'first':1}))
    cfg=copy.deepcopy(DEFAULT)
    cfg['axes']['aer']={'scale':'log','zeros':'separate'}
    cfg['axes']['x']={'label':'Custom x','ticks':[-4,0,6],'limits':[-5,7]}
    cfg['legend']['show']=False
    prepare(data,cfg)
    fig=style.plt.figure();grid=fig.add_gridspec(1,1)
    ax,zero=panel(fig,grid[0],data.rows,data,cfg,'aer','Title')
    assert ax.get_yscale()=='log' and all(math.isnan(y) for y in ax.lines[0].get_ydata())
    assert list(zero.lines[0].get_ydata())==[0]*6
    assert zero.get_xlim()==(-5,7) and zero.get_xlabel()=='Custom x'
    assert ax.get_legend() is None
    style.plt.close(fig)


def test_bad_config_and_relative_paths(tmp_path):
    p=tmp_path/'plot.json'
    p.write_text(json.dumps(dict(input='SUMMARY.json',output='out',legend={'ncols':2})))
    with pytest.raises(ValueError,match='Unknown keys'):
        resolve_config(p,'snr_comparison')
    p.write_text(json.dumps(dict(input='SUMMARY.json',output='out')))
    cfg=resolve_config(p,'snr_comparison')
    assert cfg['input']==str(tmp_path/'SUMMARY.json')
    assert cfg['output']==str(tmp_path/'out')


def test_cli_manifest_and_no_overwrite(tmp_path):
    source,_,_=fixture(tmp_path)
    p=tmp_path/'config.json'
    p.write_text(json.dumps(dict(input='SUMMARY.json',output='out',selection={'methods':['STMP']},
                                plot={'panels':['combined']},export={'formats':['png'],'dpi':50,'preview_dpi':40})))
    from plotting.common import execute
    assert execute('snr_comparison',None,['--config',str(p)])==0
    manifest=json.loads((tmp_path/'out/FIGURES.json').read_text())
    assert manifest['inference_started'] is False
    assert manifest['methods']==['STMP']
    assert 'CONFIG.json' in manifest['files']
    with pytest.raises(SystemExit):
        execute_config('snr_comparison',['--config',str(p)])


def test_reject_concurrent_and_unknown_method(tmp_path):
    source,plan,_=fixture(tmp_path,'runtime_comparison')
    plan['parallel_execution']=True
    (tmp_path/'PLAN.json').write_text(json.dumps(plan))
    data=load_saved(source,'runtime_comparison')
    with pytest.raises(ValueError,match='isolated'):
        prepare(data,copy.deepcopy(DEFAULT))
    with pytest.raises(ValueError,match='saved method IDs'):
        select(data,{'methods':['C_STMP']})


def test_saved_baseline_threshold_preserves_float64_boundary(tmp_path):
    import numpy as np
    from plotting.data import PlotData,digest
    from plotting.plot_selection import scene_records
    score=np.float32(.1)
    compact=tmp_path/'prediction.npz'
    np.savez(compact,truth_activity=np.array([True]),activity_score=np.array([score]),coefficient_energy=np.array([1.]))
    result=tmp_path/'prediction.json'
    result.write_text(json.dumps(dict(compact_sha256=digest(compact),metrics={'full_error':1,'signal_energy':2})))
    audit=tmp_path/'BASELINE_AUDIT.json'
    audit.write_text(json.dumps({'references':[dict(scene=0,index=0,method='gnn',result=str(result),sha256=digest(result),threshold=float(score)+1e-10)]}))
    plan=tmp_path/'PLAN.json';plan.write_text(json.dumps({'snrs':[0]}))
    csvpath=tmp_path/'per_scene.csv';csvpath.write_text('scene,method,snr_db\n0,STMP,0\n')
    (tmp_path/'COMPLETE.json').write_text(json.dumps(dict(status='COMPLETE',files={p.name:digest(p) for p in [audit,csvpath]})))
    data=PlotData('snr_comparison',[],['gnn'],1,dict(source_summary=str(tmp_path/'SUMMARY.json'),source_plan=str(plan),sealed_snapshot=True))
    rows=scene_records(data,{0})
    assert rows[0]['misses']==1 and rows[0]['false_alarms']==0


@pytest.mark.parametrize('experiment',CONDITIONS)
def test_public_entries_use_shared_defaults_without_config(tmp_path,experiment,monkeypatch):
    import importlib
    from plotting.configurable import method_style
    source,plan,summary=fixture(tmp_path,experiment)
    if experiment=='channel_denoising':
        # The approved historical plot selects nine denoisers, including legacy IDs.
        selected=['proposed','pretrained_colored_first','noisy','gaussian','genie_bound','offgrid_sbl','gnn','gamp','somp']
        template=[r for r in summary['rows'] if r['method']=='pretrained_first']
        for method in selected:
            if method not in plan['methods']:
                plan['methods'].append(method)
                plan['algorithm_specs'][method]={'label':method}
                summary['rows'].extend(dict(r,method=method) for r in template)
        (tmp_path/'PLAN.json').write_text(json.dumps(plan))
        source.write_text(json.dumps(summary))
    seen=[]
    def capture(data,out,cfg):
        seen.append(cfg)
        stmp=method_style('STMP',0,data,cfg);cstmp=method_style('C_STMP',1,data,cfg)
        assert (stmp['color'],stmp['marker'],stmp['linestyle'])==('#2878b5','s','-')
        assert (cstmp['color'],cstmp['marker'],cstmp['linestyle'])==('#b83253','o','-')
        assert cfg['figure']['major_grid_color']=='#909090'
        assert cfg['figure']['major_grid_alpha']==.8 and cfg['figure']['minor_grid']
        assert cfg['figure']['font_size']==8.5
        assert cfg['legend']['fontsize']==6 and cfg['legend']['handlelength']==2.6
        assert cfg['plot']['panels']==['combined'] and not cfg['plot']['show_panel_titles']
        return []
    monkeypatch.setattr('plotting.configurable.render',capture)
    from plotting.common import execute_public
    assert execute_public(experiment,None,['--input',str(source),'--output',str(tmp_path/'out')])==0
    assert len(seen)==1


def test_auto_legend_never_expands_limits_even_when_crowded():
    from plotting.legend_layout import automatic_legend
    from matplotlib.legend import Legend
    fig,ax=style.plt.subplots(figsize=(3.5,3),layout='constrained')
    methods=[f'Curve {i}' for i in range(12)]
    for i,m in enumerate(methods):ax.plot([0,1],[i,i],label=m)
    ax.set_xlim(0,1);ax.set_ylim(0,11);fig.canvas.draw()
    before=(ax.get_xlim(),ax.get_ylim())
    chosen=automatic_legend(ax,methods,copy.deepcopy(DEFAULT['legend']))
    fig.canvas.draw()
    assert (ax.get_xlim(),ax.get_ylim())==before
    assert chosen[0]['loc']=='outside below'
    legends=[a for a in ax.get_children() if isinstance(a,Legend)]
    assert len(legends)==1
    assert [t.get_text() for t in legends[0].get_texts()]==methods
    style.plt.close(fig)


def test_config_loading_does_not_mutate_defaults(tmp_path):
    p=tmp_path/'c.json';p.write_text(json.dumps(dict(input='input',output='output')))
    cfg=resolve_config(p,'snr_comparison');cfg['plot']['metrics']=['aer']
    cfg['figure']['major_grid_color']='black'
    next_cfg=resolve_config(p,'pilot_frames')
    assert next_cfg['plot']['metrics'] is None
    assert next_cfg['figure']['major_grid_color']=='#909090'


def test_log_grid_has_complete_decades_and_no_horizontal_padding(tmp_path):
    source,_,_=fixture(tmp_path)
    data=select(load_saved(source,'snr_comparison'),{'methods':['STMP']})
    cfg=copy.deepcopy(DEFAULT);cfg['legend']['show']=False
    prepare(data,cfg)
    fig=style.plt.figure();grid=fig.add_gridspec(1,1)
    ax,_=panel(fig,grid[0],data.rows,data,cfg,'aer','')
    assert ax.get_ylim()==pytest.approx((.01,.1))
    assert ax.get_xlim()==(-4,6)
    cfg['axes']['aer']['limits']=[.005,.5]
    ax,_=panel(fig,grid[0],data.rows,data,cfg,'aer','')
    assert ax.get_ylim()==(.005,.5)
    style.plt.close(fig)
