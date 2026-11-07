from pathlib import Path
import re,json,hashlib,difflib,sys
sys.path.append(str(Path.home()/'.cache/codex-pymupdf'))
import pymupdf as fitz
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
before=HERE/'before'
read=lambda p:p.read_text(encoding='utf-8')
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stripcite=lambda s:re.sub(r'\\cite(?:\[[^\]]*\])?\{[^}]*\}', '', s)
checks={}
extractabstract=lambda s:re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',s,re.S)[1]
checks['abstract_identical']=extractabstract(read(ROOT/'main.tex'))==extractabstract(read(before/'main.tex'))
checks['introduction_identical_except_citations']=stripcite(read(ROOT/'sections/01_introduction.tex'))==stripcite(read(before/'sections/01_introduction.tex'))
for name in ['02_system_model.tex','07_conclusion.tex','appendix_parameter_estimation.tex','appendix_afdm_channel_model.tex','appendix_evaluation_protocol.tex']:
    checks[name+'_identical']=read(ROOT/'sections'/name)==read(before/'sections'/name)
mathpat=r'\\begin\{(equation\*?|align\*?|gather\*?)\}.*?\\end\{\1\}'
mathcount=0; worddelta={}; diffs=[]
for old in (before/'sections').glob('*.tex'):
    new=ROOT/'sections'/old.name
    a,b=read(old),read(new)
    oldmath=[m[0] for m in re.finditer(mathpat,a,re.S)]
    newmath=[m[0] for m in re.finditer(mathpat,b,re.S)]
    checks[old.name+'_numbered_math_identical']=oldmath==newmath
    mathcount+=len(oldmath)
    checks[old.name+'_labels_identical']=re.findall(r'\\label\{([^}]+)\}',a)==re.findall(r'\\label\{([^}]+)\}',b)
    checks[old.name+'_graphics_identical']=re.findall(r'\\includegraphics[^\n]+',a)==re.findall(r'\\includegraphics[^\n]+',b)
    if a!=b:
        worddelta[old.name]={'before':len(a.split()),'after':len(b.split()),'removed':len(a.split())-len(b.split())}
        diffs.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='before/sections/'+old.name,tofile='sections/'+old.name))
for name in ['main.tex','references.bib']:
    diffs.extend(difflib.unified_diff(read(before/name).splitlines(True),read(ROOT/name).splitlines(True),fromfile='before/'+name,tofile=name))
(HERE/'CHANGES.diff').write_text(''.join(diffs),encoding='utf-8')
results={}
for name,expected in [('main',13),('main_full',15)]:
    doc=fitz.open(ROOT/(name+'.pdf'))
    bbl=read(ROOT/(name+'.bbl'))
    refs=re.findall(r'\\bibitem\{([^}]+)\}',bbl)
    log=read(ROOT/(name+'.log'))
    blg=read(ROOT/(name+'.blg'))
    bad=re.findall(r'^.*(?:Undefined control sequence|undefined references|Citation .*undefined|Overfull|There were \d+ error messages|I was expecting).*$' , log+'\n'+blg,re.M)
    checks[name+'_page_count']=len(doc)==expected
    checks[name+'_43_references']=len(refs)==43 and len(set(refs))==43
    checks[name+'_no_unresolved_or_overfull']=not bad
    text='\n'.join(p.get_text() for p in doc)
    checks[name+'_conclusion_included']='VII. CONCLUSION' in text
    checks[name+'_appendix_C_policy']=('APPENDIX C' in text)==(name=='main_full')
    results[name]={'pages':len(doc),'references':len(refs),'sha256':digest(ROOT/(name+'.pdf')),'diagnostics':bad,'appendix_C':'APPENDIX C' in text,'url_entries':bbl.count('Available:')}
oldrefs=set(re.findall(r'\\bibitem\{([^}]+)\}',read(before/'main.bbl')))
newrefs=set(re.findall(r'\\bibitem\{([^}]+)\}',read(ROOT/'main.bbl')))
checks['original_35_references_retained']=oldrefs<=newrefs
checks['exactly_8_added']=len(newrefs-oldrefs)==8
result={'checks':checks,'all_pass':all(checks.values()),'numbered_math_blocks_checked':mathcount,'documents':results,'word_changes':worddelta,'added_references':sorted(newrefs-oldrefs),'scope':'Manuscript, citation placement, publication metadata, layout; no new experimental runs.'}
(HERE/'VALIDATION.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2,ensure_ascii=False))
if not result['all_pass']:
    print({k:v for k,v in checks.items() if not v})
    raise SystemExit(1)
