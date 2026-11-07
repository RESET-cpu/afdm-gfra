from pathlib import Path
import re, json, hashlib, difflib, sys, subprocess
sys.path.append(str(Path.home()/'.cache/codex-pymupdf'))
import pymupdf as fitz
from PIL import Image, ImageOps, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
before = HERE/'before'
read = lambda p: p.read_text(encoding='utf-8')
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
keymap = {'dytso2021':'dytso2023', 'metzler2014':'metzler2016', 'xu2019otfs':'zou2021otfs'}
checks = {}
diffs = []
mathcount = 0
mathpat = r'\\begin\{(equation\*?|align\*?|gather\*?)\}.*?\\end\{\1\}'
stripcite = lambda s: re.sub(r'\\cite(?:\[[^\]]*\])?\{[^}]*\}', '', s)
for old in (before/'sections').glob('*'):
    if not old.is_file():
        continue
    new = ROOT/'sections'/old.name
    a, b = read(old), read(new)
    if old.name == '01_introduction.tex':
        expected = a.replace(r' in \cite{wei2026}', '')
        checks['introduction_only_wei_marker_and_dangling_in_removed'] = b == expected
        checks['wei_related_sentence_retained'] = 'A similar\nlimitation has been highlighted for structured compression matrices. This' in b
    else:
        checks[old.name+'_prose_unchanged_except_citations'] = stripcite(a) == stripcite(b)
    am = [m[0] for m in re.finditer(mathpat, a, re.S)]
    bm = [m[0] for m in re.finditer(mathpat, b, re.S)]
    checks[old.name+'_numbered_math_identical'] = am == bm
    mathcount += len(am)
    checks[old.name+'_labels_identical'] = re.findall(r'\\label\{[^}]+\}',a) == re.findall(r'\\label\{[^}]+\}',b)
    checks[old.name+'_figures_identical'] = re.findall(r'\\includegraphics[^\n]+',a) == re.findall(r'\\includegraphics[^\n]+',b)
    if a != b:
        diffs.extend(difflib.unified_diff(a.splitlines(True), b.splitlines(True), fromfile='before/sections/'+old.name, tofile='sections/'+old.name))
for name in ['main.tex','main_full.tex']:
    checks[name+'_identical'] = read(before/name) == read(ROOT/name)
diffs.extend(difflib.unified_diff(read(before/'references.bib').splitlines(True), read(ROOT/'references.bib').splitlines(True), fromfile='before/references.bib', tofile='references.bib'))
(HERE/'CHANGES.diff').write_text(''.join(diffs),encoding='utf-8')
bib = read(ROOT/'references.bib')
checks['no_preprint_entries'] = not re.search(r'@misc\{|howpublished\s*=\s*\{arxiv|archivePrefix|eprint\s*=|10\.48550/', bib, re.I)
checks['retired_keys_absent_from_active_sources'] = not any(k in bib or any(k in read(p) for p in (ROOT/'sections').glob('*.tex')) for k in [*keymap,'wei2026'])
for key in ['dytso2023','metzler2016','shastri2022','zou2021otfs']:
    metadata = json.loads(read(HERE/'metadata'/(key+'.json')))
    entry = re.search(r'@\w+\{'+key+r',\n(.*?)(?=\n@|\Z)',bib,re.S)[1]
    checks[key+'_DOI_matches_Crossref'] = metadata['DOI'].lower() in entry.lower()
    checks[key+'_pages_match_Crossref'] = '{'+metadata['page'].replace('-', '--')+'}' in entry
    checks[key+'_year_matches_Crossref'] = '{'+str(metadata['published']['date-parts'][0][0])+'}' in entry
oldrefs = set(re.findall(r'\\bibitem\{([^}]+)\}',read(before/'main.bbl')))
expectedrefs = {keymap.get(k,k) for k in oldrefs if k!='wei2026'}
documents = {}
for name, expectedpages in [('main',13),('main_full',15)]:
    doc = fitz.open(ROOT/(name+'.pdf'))
    bbl = read(ROOT/(name+'.bbl'))
    refs = re.findall(r'\\bibitem\{([^}]+)\}',bbl)
    text = '\n'.join(p.get_text() for p in doc)
    diagnostics = read(ROOT/(name+'.log'))+'\n'+read(ROOT/(name+'.blg'))
    bad = re.findall(r'^.*(?:Undefined control sequence|undefined references|Citation .*undefined|Overfull|There were \d+ error messages|I was expecting).*$',diagnostics,re.M)
    checks[name+'_42_references'] = len(refs)==42 and len(set(refs))==42
    checks[name+'_expected_reference_set'] = set(refs)==expectedrefs
    checks[name+'_expected_pages'] = len(doc)==expectedpages
    checks[name+'_no_unresolved_or_overfull'] = not bad
    checks[name+'_no_preprint_in_output'] = not re.search(r'arxiv|preprint', text+'\n'+bbl,re.I)
    checks[name+'_conclusion_included'] = 'VII. CONCLUSION' in text
    checks[name+'_appendix_C_policy'] = ('APPENDIX C' in text)==(name=='main_full')
    documents[name] = {'pages':len(doc),'references':len(refs),'sha256':digest(ROOT/(name+'.pdf')),'diagnostics':bad}
result = {'all_pass':all(checks.values()), 'checks':checks, 'numbered_math_blocks_checked':mathcount, 'documents':documents,
          'scope':'Four publication records replaced; Wei bibliography entry and inline marker removed, sentence retained. No model, formula, figure, result, or experiment changes.'}
(HERE/'VALIDATION.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2,ensure_ascii=False))
if not result['all_pass']:
    print({k:v for k,v in checks.items() if not v})
    raise SystemExit(1)

render = HERE/'render'
render.mkdir(exist_ok=True)
poppler = Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe'
for name in ['main','main_full']:
    subprocess.run([str(poppler),'-scale-to','1100','-png',str(ROOT/(name+'.pdf')),str(render/name)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    images = sorted(render.glob(name+'-*.png'))
    images = [p for p in images if re.fullmatch(re.escape(name)+r'-\d+\.png',p.name)]
    sheet = Image.new('RGB',(4*290,((len(images)+3)//4)*400),'#cccccc')
    draw = ImageDraw.Draw(sheet)
    for i,p in enumerate(images):
        im=Image.open(p).convert('RGB'); im.thumbnail((280,375))
        x=(i%4)*290+5; y=(i//4)*400+20
        sheet.paste(im,(x,y)); draw.text((x,y-16),p.stem,fill='black')
    sheet.save(render/(name+'_overview.png'))
print('Rendered both final PDFs and overview sheets.')
