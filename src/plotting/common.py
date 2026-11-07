"""CLI and provenance shared by independently runnable plotting scripts."""
import argparse
from dataclasses import asdict
from pathlib import Path
import json
import os
import sys

os.environ['OMP_NUM_THREADS']='1'
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
from plotting.data import load
from plotting.data import digest
import plotting.style as style


def caption(data,notes):
    lines=[f'{data.experiment}: {data.scenes} paired physical scenes per condition.',
           f'Result status: {data.metadata["status"]}; experiment mode: {data.metadata.get("mode")}.']
    if data.metadata['status']=='INTERIM':
        lines.append(f'Interim results from a planned {data.metadata["planned_scenes"]}-scene experiment.')
    if data.experiment=='channel_denoising':
        lines.append('Complex AWGN variance is supplied. Genie uses simulated truth information.')
    else:
        phase='Known phase (simulation truth)' if data.metadata['phase_mode']=='known' else 'Estimated phase'
        noise='known noise variance (simulation truth)' if data.metadata['noise_mode']=='known' else 'estimated noise variance'
        lines.append(phase+'; '+noise+'.')
        lines.append('NMSE uses pooled full-channel error and signal energies. AER pools missed detections and false alarms over all user decisions.')
    lines.extend(notes)
    return ' '.join(lines)


def execute_public(experiment,draw=None,argv=None,**kwargs):
    """The eight maintained CLI entries always use the current shared defaults."""
    from plotting.configurable import execute_config
    return execute_config(experiment,sys.argv[1:] if argv is None else argv)


def execute(experiment,draw,argv=None,*,load_data=load):
    # Keep the historical renderer unchanged for exact figure replay.
    arguments = sys.argv[1:] if argv is None else argv
    if any(a == '--config' or a.startswith('--config=') for a in arguments):
        from plotting.configurable import execute_config
        return execute_config(experiment, arguments)
    parser=argparse.ArgumentParser(description=f'Render {experiment} from saved results only; no inference or training.')
    parser.add_argument('--config', type=Path, help='JSON plotting configuration; see src/configs/plots/README.md')
    parser.add_argument('--input',required=True,type=Path,help='Saved SUMMARY.json, audited interim snapshot, or its directory')
    parser.add_argument('--output',required=True,type=Path,help='New directory for manuscript figures; original results are never overwritten')
    parser.add_argument('--aer-scale',choices=('auto','log','linear'),default='auto',help='auto: log for positive AER, linear if any observed value is zero')
    args=parser.parse_args(argv)
    try:
        data=load_data(args.input,experiment)
        out=args.output.resolve()
        if out.exists():
            raise ValueError('Output directory already exists; choose a new directory to preserve earlier figures.')
        if experiment=='runtime_comparison':
            text=str(data.metadata.get('timing','')).lower()
            if data.metadata.get('parallel_execution') or 'concurrent' in text or 'contention' in text:
                raise ValueError('Runtime comparison requires saved isolated measurements, not concurrent main-run timings.')
        style.configure()
        out.mkdir(parents=True)
        outputs,notes=draw(data,out,args)
        (out/'PLOT_DATA.json').write_text(json.dumps(asdict(data),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        description=caption(data,notes)
        (out/'caption.txt').write_text(description+'\n',encoding='utf-8')
        safe_caption=description.replace('_',r'\_').replace('%',r'\%').replace('&',r'\&')
        snippets=[]
        for name,wide in outputs:
            env='figure*' if wide else 'figure'
            width=r'\textwidth' if wide else r'\columnwidth'
            snippets.append('\n'.join([f'\\begin{{{env}}}[t]',r'  \centering',
                f'  \\includegraphics[width={width}]{{{name}.pdf}}',
                '  \\caption{'+safe_caption+'}',f'  \\label{{fig:{name.replace("_","-")}}}',f'\\end{{{env}}}']))
        (out/'figure_include.tex').write_text('% Copy the PDFs alongside the paper or set graphicspath.\n\n'+'\n\n'.join(snippets)+'\n',encoding='utf-8')
        scripts={p.name:digest(p) for p in Path(__file__).parent.glob('*.py')}
        manifest=dict(status='PLOTTED',experiment=experiment,scenes=data.scenes,result_status=data.metadata['status'],
            original_data_unchanged=digest(data.metadata['source_summary'])==data.metadata['source_sha256'],
            plot_only=True,inference_started=False,caption=description,source=data.metadata,
            scripts=scripts,outputs=[name for name,_ in outputs],
            files={p.name:digest(p) for p in out.iterdir() if p.is_file()})
        (out/'FIGURES.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(status='PLOTTED',experiment=experiment,scenes=data.scenes,path=str(out),figures=len(outputs)),ensure_ascii=False))
        return 0
    except (ValueError,KeyError,FileNotFoundError) as error:
        parser.error(str(error))
