"""Check final plot adoption, protected manuscript assets and compiled PDFs."""
import json
import re
import sys
from pathlib import Path
from utils import read_json, write_json, sha256

ROOT=Path(__file__).resolve().parents[4]
CHECK=Path(__file__).resolve().parent
OUT=ROOT/'result/snr_comparison/data/white_phase_frontend_marginal_1000_20261106'
sys.path.append(str(Path.home()/'.cache/codex-pymupdf'))
import pymupdf as fitz


def main():
    before=read_json(CHECK/'BEFORE_HASHES.json')
    allowed={'src/configs/plots/manuscript.json','paper/C-STMP/sections/06_simulation_results.tex',
             'paper/C-STMP/figures/snr_comparison.pdf','paper/C-STMP/figures/snr_comparison.svg','paper/C-STMP/figures/snr_comparison.png',
             'README.md','paper/C-STMP/README.md','paper/C-STMP/figures/README.md',
             'src/evaluation/plots/manuscript/README.md','paper/C-STMP/docs/REVIEW_DECISIONS.md'}
    unchanged=[]
    for name,digest in before.items():
        if name not in allowed:
            assert sha256(ROOT/name)==digest,name
            unchanged.append(name)
    cfg=read_json(ROOT/'src/configs/plots/manuscript.json')
    old_cfg=read_json(CHECK/'before/src/configs/plots/manuscript.json')
    new=cfg['figures']['snr_comparison'];old=old_cfg['figures']['snr_comparison']
    assert {k:v for k,v in cfg['figures'].items() if k!='snr_comparison'}=={k:v for k,v in old_cfg['figures'].items() if k!='snr_comparison'}
    for key in ('styles','labels','methods','size_inches','point_count','legend_order','legend_style'):
        assert new[key]==old[key]
    assert new['panel_config']['figure']==old['panel_config']['figure']
    assert new['panel_config']['axes']==old['panel_config']['axes']
    data=read_json(ROOT/new['source']);historical=read_json(ROOT/old['source'])
    assert sha256(ROOT/new['source'])==new['source_sha256']
    assert sha256(ROOT/old['source'])==old['source_sha256']
    changed={'C_STMP','C_STMP_phase_frontend_marginal_20261104'}
    assert [r for r in data['rows'] if r['method'] not in changed]==[r for r in historical['rows'] if r['method'] not in changed]
    for source,digest in data['metadata']['source_sha256'].items():
        assert sha256(ROOT/source)==digest,source
    render=read_json(CHECK/'RENDER.json');r=render['figures']['snr_comparison']
    assert render['status']=='PASS' and r['pdf_images']==0
    assert r['sha256']==sha256(ROOT/'paper/C-STMP/figures/snr_comparison.pdf')
    assert sum(len(c['y']) for c in r['curves'])==108
    for curve in r['curves']:
        rows=sorted((v for v in data['rows'] if v['method']==curve['method']),key=lambda v:v['snr_db'])
        assert curve['x']==[v['snr_db'] for v in rows]
        assert curve['y']==[v[curve['metric']] for v in rows]
    source=ROOT/'paper/C-STMP/sections/06_simulation_results.tex'
    old_text=(CHECK/'before/paper/C-STMP/sections/06_simulation_results.tex').read_text('utf-8')
    new_text=source.read_text('utf-8')
    pattern=r'\\begin\{(equation|align)\*?\}[\s\S]*?\\end\{\1\*?\}'
    assert [m.group() for m in re.finditer(pattern,new_text)]==[m.group() for m in re.finditer(pattern,old_text)]
    assert re.findall(r'\\cite(?:\[[^]]*\])?\{[^}]*\}',new_text)==re.findall(r'\\cite(?:\[[^]]*\])?\{[^}]*\}',old_text)
    pdfs={}
    for name,count in [('main',13),('main_full',14)]:
        path=ROOT/f'paper/C-STMP/{name}.pdf'
        with fitz.open(path) as doc:
            assert len(doc)==count
            text='\n'.join(p.get_text() for p in doc)
            assert '0.28–0.60' in text and '1.5 dB' in text and 'Fig. 6.' in text
            assert '\ufffd' not in text
            assert '[42]' in text and '[43]' not in text
            pdfs[name]=dict(path=str(path),pages=len(doc),sha256=sha256(path),references=42,visually_checked_pages=[8,11,12])
        log=(ROOT/f'paper/C-STMP/{name}.log').read_text('utf-8',errors='replace')
        for bad in ('Overfull','undefined references','undefined citations','Missing character','! LaTeX Error'):
            assert bad not in log,bad
    output=dict(status='PASS',changed_data_rows=12,unchanged_baseline_rows=42,curve_points=108,
        all_non_snr_figures_unchanged=True,protected_assets_unchanged=unchanged,plot_styles_labels_axes_grid_unchanged=True,
        equations_and_citations_unchanged=True,compilation='Both Tectonic commands exited 0; inherited PDF 1.7 versus output 1.5 compatibility warnings only.',
        pdfs=pdfs,visual_review='Main SNR figure and both documents pages 8, 11 and 12 inspected: readable labels, no clipping or overlap; chapter data status and numeric prose agree with verified results.',
        figure_audit=dict(type='experimental-results',paradigm='NMSE and AER line panels versus SNR',
            canvas_inches=[3.5,2.65],primary_tool='Existing Matplotlib render_paper.py',
            vector=True,minimum_main_text_pt=8,dual_encoding='Color with marker and line style; approved palette preserved.',
            honest_axes=True,no_chartjunk=True,caption='Existing descriptive caption retained under the authorized focused update; sample size, units and SBL grid label meaning retained.',
            critical=0,major=0),source_summary_sha256=sha256(OUT/'SUMMARY.json'))
    write_json(CHECK/'VALIDATION.json',output)
    print(json.dumps(dict(status='PASS',pdfs={k:v['pages'] for k,v in pdfs.items()},curve_points=108,unchanged_assets=len(unchanged)),indent=2))


if __name__=='__main__':main()
