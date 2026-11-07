"""Read-only manuscript readiness checks; writes evidence only in this folder."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import sys

sys.path.insert(0, r'C:/Users/25911/.cache/codex-pymupdf')
sys.path.insert(0, r'C:/Users/25911/.cache/codex-plotdeps')
import pymupdf
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / 'paper/C-STMP'
OUT = Path(__file__).resolve().parent

def read(p):
    return p.read_text(encoding='utf-8-sig')

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

main = read(PAPER / 'main.tex')
includes = [PAPER / (x + '.tex') for x in re.findall(r'\\input\{([^}]+)\}', main)]
sources = [PAPER / 'main.tex', PAPER / 'main_full.tex', *includes]
assets = sorted(set(sources + list((PAPER/'sections').glob('*')) +
    [PAPER/'references.bib', PAPER/'main.pdf', PAPER/'main_full.pdf'] +
    list((PAPER/'figures').glob('*.pdf'))))
before = {str(p.relative_to(PAPER)):digest(p) for p in assets if p.is_file()}
text = '\n'.join(re.sub(r'(?<!\\)%.*', '', read(p)) for p in sources)
labels = re.findall(r'\\label\{([^}]+)\}', text)
refs = re.findall(r'\\(?:eqref|ref|pageref)\{([^}]+)\}', text)
cites = set(k.strip() for group in re.findall(r'\\(?:cite|bstctlcite)(?:\[[^\]]*\])*\{([^}]+)\}', text) for k in group.split(','))
bibkeys = set(re.findall(r'@\w+\s*\{\s*([^,\s]+)', read(PAPER/'references.bib')))
figures = re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', text)
result = {
    'scope':'Current shared manuscript and both included appendices; no new inference, training, compilation or manuscript edits.',
    'included_sections':[str(p.relative_to(PAPER)) for p in includes],
    'duplicate_labels':[k for k,v in Counter(labels).items() if v > 1],
    'unresolved_source_references':sorted(set(refs)-set(labels)),
    'undefined_citations':sorted(cites-bibkeys),
    'figure_files_missing':[f for f in figures if not (PAPER/'figures'/f).exists()],
    'figures':len(figures),
    'tables':len(re.findall(r'\\begin\{table\*?\}',text)),
    'todos':[line.strip() for line in text.splitlines() if re.search(r'\b(?:TODO|FIXME|TBD)\b|e-mail to be added',line)],
    'pdfs':{},
}
for stem in ['main','main_full']:
    aux = read(PAPER/(stem+'.aux'))
    log = read(PAPER/(stem+'.log'))
    eqs = re.findall(r'\\newlabel\{((?:eq:|frontend:eq:)[^}]+)\}\{\{([^}]+)\}',aux)
    doc = pymupdf.open(PAPER/(stem+'.pdf'))
    alltext = '\n'.join(p.get_text() for p in doc)
    result['pdfs'][stem] = {
        'pages':len(doc), 'numbered_equations':len(eqs),
        'equation_numbers':[n for _,n in eqs],
        'bibliography_entries':len(re.findall(r'\\bibcite\{',aux))-int('\\bibcite{IEEEcontrol}' in aux),
        'compile_error_lines':[l for l in log.splitlines() if re.search(r'^!|undefined|multiply defined|Overfull',l,re.I)],
        'underfull_warning_lines':[l for l in log.splitlines() if 'Underfull' in l],
        'pdf_newer_than_included_sources':(PAPER/(stem+'.pdf')).stat().st_mtime >= max(p.stat().st_mtime for p in sources),
        'current_prose_in_pdf':all(s in re.sub(r'\s+',' ',alltext) for s in ['computation of these moments','Each GPJD update','stopping is based','For comparison, the Gaussian approximation']),
    }
    (OUT/(stem+'_extracted.txt')).write_text(alltext,encoding='utf-8')
    if stem == 'main':
        for start in [0,6]:
            indices = list(range(start,min(start+7 if start else 6,len(doc))))
            sheet = Image.new('RGB',(3*336,((len(indices)+2)//3)*455),'#dddddd')
            draw = ImageDraw.Draw(sheet)
            for j,i in enumerate(indices):
                pix = doc[i].get_pixmap(matrix=pymupdf.Matrix(.52,.52),alpha=False)
                page = Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
                x,y=(j%3)*336,(j//3)*455
                sheet.paste(page,(x+8,y+20));draw.text((x+8,y+4),str(i+1),fill='black')
            sheet.save(OUT/f'main_pages_{indices[0]+1}_{indices[-1]+1}.png')

def data(rel):
    return json.loads(read(ROOT/rel))

snr = data('result/snr_comparison/figures/phase_selected_main_500_20261102/PLOT_DATA.json')['rows']
for row in snr:
    row['snr_db'] = row['parameters']['snr_db']
pilot = data('result/pilot_frames/figures/full_grid_final_20261026/PLOT_DATA.json')['rows']
cross = data('result/cross_channel/figures/full_500_paper_20261028/PLOT_DATA.json')['rows']
claims = {}
proposed = [r for r in snr if r['method']=='C_STMP']
claims['snr_proposed_lowest_nmse'] = all(r['nmse_db'] <= s['nmse_db'] for r in proposed for s in snr if s['snr_db']==r['snr_db'])
claims['snr_proposed_lower_aer_than_gpmp'] = all(r['aer'] < s['aer'] for r in proposed for s in snr if s['snr_db']==r['snr_db'] and s['method']=='STMP')
thresholds = {m:min(r['frames'] for r in pilot if r['method']==m and r['nmse_db']<=-14) for m in ['C_STMP','STMP']}
claims['first_evaluated_frame_count_at_minus14db'] = thresholds
claims['frame_reduction_fraction'] = 1-thresholds['C_STMP']/thresholds['STMP']
claims['cross_profile_all_points_lower_nmse_than_sparse_baselines'] = all(r['nmse_db'] < s['nmse_db'] for r in cross if r['method']=='C_STMP' for s in cross if s['method'] in ['offgrid_sbl','gnn','gamp','somp'] and s['snr_db']==r['snr_db'] and s['channel_model']==r['channel_model'])
completion = data('result/snr_comparison/data/c_stmp_phase_selected_500_20261030/COMPLETION.json')
claims['estimated_phase_batch'] = {k:completion[k] for k in ['status','inputs','physical_scenes','snrs','iteration_caps_by_variant']}
claims['table_ii_pooled_from_archived_counts'] = {'learned_aer_percent':114/84960*100,'gaussian_aer_percent':31394/84960*100,'gaussian_limit_percent':724/2124*100}
result['claim_checks'] = claims
result['reused_prior_algebra_checks'] = {
    'notation_formula_revision_20261104':data('paper/C-STMP/checks/notation_formula_revision_20261104/MATH_VALIDATION.json')['largest_residual'],
    'cai_formula_correspondence_20261104':data('paper/C-STMP/checks/cai_formula_correspondence_20261104/VALIDATION.json')['checks']['maximum_error'],
    'note':'32 and 7 prior deterministic checks reused, not rerun; no assertion of learned performance or overall convergence.'
}
result['assets_unchanged'] = all(digest(PAPER/p)==h for p,h in before.items())
result['asset_hashes'] = before
(OUT/'VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='asset_hashes'},ensure_ascii=False,indent=2))
