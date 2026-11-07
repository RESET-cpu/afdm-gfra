"""Single entry point for all ten current C-STMP figures; no inference or training."""
from pathlib import Path
import argparse
import hashlib
import importlib
import json
import tempfile
import sys

from workspace import ROOT, CONFIGS
DEFAULT_CONFIG=CONFIGS/'plots/manuscript.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_sources(config,names):
    sources={config['figures'][n]['source']:config['figures'][n]['source_sha256']
             for n in names if config['figures'][n]['kind']=='experiment'}
    if any(config['figures'][n]['kind']=='method' for n in names):
        sources.update(config['method_sources'])
    for relative,expected in sources.items():
        if sha(ROOT/relative)!=expected:
            raise ValueError(f'Saved input changed; review its provenance before updating: {relative}')
    return sources


def render(config,names,output,formats):
    from plotting.manuscript import vector
    from plotting.manuscript import experiments
    output.mkdir(parents=True,exist_ok=True)
    sources=verify_sources(config,names)
    results={}
    for name in names:
        cfg=config['figures'][name]
        vector.plt.rcdefaults()
        path=output/(name+'.pdf')
        if cfg['kind']=='method':
            vector.configure()
            module,func={'system_multiframe':('system','system'),'factor_graph':('factor','factor'),
                         'learned_receiver':('receiver','receiver')}[name]
            doc=getattr(importlib.import_module('plotting.manuscript.'+module),func)()
            doc.set_metadata({'title':name.replace('_',' '),
                'subject':'Adapted from supplied Cai and Shen paper artwork; see source record',
                'creator':'Recomposed scientific figure, 2026-11-03'})
            doc.subset_fonts()
            doc.save(path,garbage=4,deflate=True)
            doc.close()
            result={'kind':'method'}
        else:
            raw=read(ROOT/cfg['source'])
            fig,curves=experiments.draw(name,raw,cfg)
            experiments.validate(fig,curves,cfg)
            fig.savefig(path,metadata={'CreationDate':None,'ModDate':None})
            if 'svg' in formats: fig.savefig(output/(name+'.svg'))
            if 'png' in formats: fig.savefig(output/(name+'.png'),dpi=600)
            vector.plt.close(fig)
            result={'kind':'experiment','point_count':cfg['point_count'],'curves':curves}
        with vector.fitz.open(path) as doc:
            page=doc[0]
            result.update(size_pt=list(page.rect)[2:],pdf_images=len(page.get_images()),sha256=sha(path))
            if cfg['kind']=='method':
                if 'svg' in formats:
                    (output/(name+'.svg')).write_text(page.get_svg_image(text_as_path=True),encoding='utf-8')
                if 'png' in formats: page.get_pixmap(dpi=600).save(output/(name+'.png'))
        results[name]=result
        print(f'Rendered {cfg["number"]:2d}: {name}',flush=True)
    verify_sources(config,names)
    import matplotlib
    import numpy
    import platform
    return {'status':'PASS','sources':sources,'figures':results,
            'runtime':{'python':platform.python_version(),'matplotlib':matplotlib.__version__,
                       'numpy':numpy.__version__,'pymupdf':vector.fitz.VersionBind},
            'inference_started':False,'training_started':False}


def compare(output,reference,names):
    from plotting.manuscript.vector import fitz
    result={}
    for name in names:
        with fitz.open(output/(name+'.pdf')) as new,fitz.open(reference/(name+'.pdf')) as old:
            a,b=new[0],old[0]
            # Exact pixels at publication-independent resolution, not a loose similarity score.
            same_size=a.rect==b.rect
            pa,pb=a.get_pixmap(dpi=200,alpha=False),b.get_pixmap(dpi=200,alpha=False)
            same_pixels=pa.samples==pb.samples and (pa.width,pa.height)==(pb.width,pb.height)
            result[name]={'same_size':same_size,'pixel_identical_at_200_dpi':same_pixels,
                          'pdf_bytes_identical':sha(output/(name+'.pdf'))==sha(reference/(name+'.pdf')),
                          'reference_sha256':sha(reference/(name+'.pdf'))}
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=DEFAULT_CONFIG)
    parser.add_argument('--figures',nargs='+',help='Default: all ten figures, in manuscript order')
    parser.add_argument('--output',type=Path,help='Default: paper/figures; generated files are replaced')
    parser.add_argument('--formats',nargs='+',choices=['pdf','svg','png'],default=['pdf'])
    parser.add_argument('--list',action='store_true',help='List figures and sources without rendering')
    parser.add_argument('--check',action='store_true',help='Render in a temporary folder and compare with current paper figures')
    parser.add_argument('--report',type=Path,help='Save provenance, curve values and optional comparison results')
    args=parser.parse_args(argv)
    config=read(args.config)
    names=args.figures or list(config['figures'])
    if len(names)!=len(set(names)) or any(n not in config['figures'] for n in names):
        parser.error('--figures must contain unique names from --list')
    if args.list:
        for n in names:
            c=config['figures'][n]
            print(f'{c["number"]:2d} {n}: {c.get("source","vector drawing")}')
        return 0
    reference=ROOT/config['paper']/'figures'
    if args.check:
        if args.output: parser.error('--check does not write final figures; omit --output')
        with tempfile.TemporaryDirectory(prefix='afdm-paper-figures-') as temp:
            output=Path(temp)
            report=render(config,names,output,['pdf'])
            report['comparison']=compare(output,reference,names)
            if not all(r['same_size'] and r['pixel_identical_at_200_dpi'] for r in report['comparison'].values()):
                report['status']='FAIL'
    else:
        output=args.output.resolve() if args.output else reference
        report=render(config,names,output,args.formats)
    report['configuration_sha256']=sha(args.config)
    plot_dir=Path(__file__).parent
    support=['style.py','configurable.py','data.py','plot_selection.py','legend_layout.py']
    report['code_sha256']={str(p.relative_to(ROOT)):sha(p) for p in
                          [Path(__file__),*plot_dir.joinpath('manuscript').glob('*.py'),
                           *(plot_dir/n for n in support if (plot_dir/n).exists())]}
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(report['status'])
    return 0 if report['status']=='PASS' else 1


if __name__=='__main__':
    raise SystemExit(main())
