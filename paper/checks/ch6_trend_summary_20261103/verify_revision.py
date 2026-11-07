"""Verify a prose-only manuscript trim and render the compiled PDF."""
from pathlib import Path
import difflib, hashlib, json, re, shutil, sys
sys.path.append(str(Path.home()/'.cache/codex-pymupdf'))
import pymupdf as fitz
from PIL import Image, ImageDraw

RUN=Path(__file__).resolve().parent
PAPER=RUN.parents[1]
def read(path): return path.read_text(encoding='utf-8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def blocks(text):
    pattern=r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}.*?\\end\{\1\}|\\\[.*?\\\]'
    return [m.group() for m in re.finditer(pattern,text,re.S)]
def word_count(text):
    text=re.sub(r'(?<!\\)%[^\n]*',' ',text)
    for block in blocks(text): text=text.replace(block,' ')
    text=re.sub(r'\$[^$]*\$',' ',text,flags=re.S)
    text=re.sub(r'\\[A-Za-z]+(?:\[[^\]]*\])?\{[^}]*\}',' ',text)
    return len(re.findall(r'\b[A-Za-z]+(?:[-\u2013][A-Za-z]+)*\b',text))

manifest=json.loads(read(RUN/'BEFORE.json'))
changed=['sections/06_simulation_results.tex']
protected={rel:sha(PAPER/rel)==expected for rel,expected in manifest.items() if rel not in changed+['main.pdf']}
assert all(protected.values()),protected
diff=[]; counts={}; equations=0; deletion_only={}
for rel in changed:
    old,new=read(RUN/'before'/rel),read(PAPER/rel)
    assert blocks(old)==blocks(new),rel
    equations+=len(blocks(new))
    assert re.findall(r'\\label\{[^}]+\}',old)==re.findall(r'\\label\{[^}]+\}',new)
    counts[rel]={'before':word_count(old),'after':word_count(new)}
    diff.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=rel+' (before)',tofile=rel))
    if not rel.endswith('06_simulation_results.tex'):
        a,b=re.sub(r'\s+','',old),re.sub(r'\s+','',new)
        cursor=iter(a)
        deletion_only[rel]=all(char in cursor for char in b)
assert all(deletion_only.values())
rel='sections/06_simulation_results.tex'
old,new=read(RUN/'before'/rel),read(PAPER/rel)
key=r'\subsection{Channel Denoising Performance}'
assert old.split(key)[0]==new.split(key)[0]
counts['VI-B-E']={'before':word_count(old.split(key)[1]),'after':word_count(new.split(key)[1])}
float_pattern=r'\\begin\{(figure\*?|table\*?)\}.*?\\end\{\1\}'
assert [m.group() for m in re.finditer(float_pattern,old,re.S)]==[m.group() for m in re.finditer(float_pattern,new,re.S)]
inline=lambda s:set(re.findall(r'\$[^$]*\$',s,re.S))
assert inline(new)<=inline(old),inline(new)-inline(old)
segments=[]
markers=[r'\label{fig:cstmp-denoising}',r'\label{tab:activity-evidence}',r'\label{fig:cstmp-convergence}',r'\label{fig:cstmp-snr}',r'\label{fig:cstmp-users}',r'\label{fig:cstmp-activity}',r'\label{fig:cstmp-pilots}',r'\label{fig:cstmp-cross}']
def extract_ranges(text):
    ranges=[]
    for marker in markers:
        start=text.index(marker)
        endfloat=re.search(r'\\end\{(?:figure\*?|table\*?)\}',text[start:])
        assert endfloat
        a=start+endfloat.end()
        nxt=re.search(r'\\sub(?:sub)?section\{',text[a:])
        b=a+nxt.start() if nxt else len(text)
        ranges.append((a,b))
    return ranges
def protected_prose(text,ranges):
    for a,b in reversed(ranges): text=text[:a]+'<RESULTS_ANALYSIS>'+text[b:]
    return text
old_ranges,new_ranges=extract_ranges(old),extract_ranges(new)
assert protected_prose(old,old_ranges)==protected_prose(new,new_ranges)
for marker,(a,b),(c,d) in zip(markers,old_ranges,new_ranges):
    segments.append({'anchor':marker,'before_words':word_count(old[a:b]),'after_words':word_count(new[c:d])})
counts['results_interpretation_only']={'before':sum(x['before_words'] for x in segments),'after':sum(x['after_words'] for x in segments)}
(RUN/'ANALYSIS_BLOCKS.json').write_text(json.dumps(segments,ensure_ascii=False,indent=2),encoding='utf-8')

(RUN/'CHANGES.diff').write_text(''.join(diff),encoding='utf-8')
log=read(PAPER/'main.log')
assert 'Overfull' not in log
assert not re.search(r'(?:Reference|Citation).*undefined|There were undefined',log)
shutil.copy2(PAPER/'main.log',RUN/'compile.log')
doc=fitz.open(PAPER/'main.pdf'); preview=RUN/'preview'; preview.mkdir(exist_ok=True)
locations={}
for i,page in enumerate(doc,1):
    page.get_pixmap(dpi=110,alpha=False).save(preview/f'page-{i:02d}.png')
    text=page.get_text()
    for term in ['Fig. 1.', 'Fig. 2.', 'Fig. 3.', 'VI. SIMULATION RESULTS','APPENDIX A','APPENDIX B','APPENDIX C','REFERENCES']:
        if term in text: locations.setdefault(term,[]).append(i)
for start in range(1,len(doc)+1,6):
    sheet=Image.new('RGB',(1440,1300),'white'); draw=ImageDraw.Draw(sheet)
    for j,n in enumerate(range(start,min(start+6,len(doc)+1))):
        im=Image.open(preview/f'page-{n:02d}.png'); im.thumbnail((470,620))
        x,y=(j%3)*480,(j//3)*650; sheet.paste(im,(x,y+24)); draw.text((x+8,y+5),f'Page {n}',fill='black')
    sheet.save(preview/f'contact-{start:02d}.png')
record={
    'scope':'VI-B-E results interpretation only; unchanged experimental setup, captions, figures, tables, and all other manuscript sections',
    'protected_files_unchanged':protected,
    'changed_sections_display_blocks_unchanged':equations,
    'VI_A_and_all_VI_figures_tables_unchanged':True,
    'all_text_outside_eight_results_interpretation_blocks_unchanged':True,
    'all_retained_VI_inline_math_from_original':True,
    'word_counts_excluding_math_and_tex_commands':counts,
    'before_pdf_pages':len(fitz.open(RUN/'before/main.pdf')),
    'after_pdf_pages':len(doc),'pdf_sha256':sha(PAPER/'main.pdf'),
    'page_locations':locations,'no_overfull_or_undefined_references':True,
    'visual_review':'pending',
    'source_sha256':{rel:sha(PAPER/rel) for rel in changed}
}
(RUN/'VALIDATION.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k not in ['protected_files_unchanged','source_sha256']},ensure_ascii=False,indent=2))
print(f'All {len(protected)} protected files are byte-identical.')
