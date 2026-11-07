import json,re,unicodedata,hashlib,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[4]
HERE=pathlib.Path(__file__).resolve().parent
BASE=HERE.parent/'abstract_sources_20261026'
PAT=r"[a-z]+(?:[-'][a-z]+)*"
def normalized(s):
    s=unicodedata.normalize('NFKC',s).replace('\u00ad','')
    return re.sub(r'[\u2010-\u2015\u2212]','-',s).lower()
def tokens(s): return re.findall(PAT,normalized(s))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d): (HERE/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
spec=json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))
pages=[];sources=[]
for key,item in spec.items():
    path=ROOT/item['pdf']
    pre=json.loads((BASE/(key+'.preflight.json')).read_text(encoding='utf-8'))
    assert sha(path)==pre['sha256'],key+' PDF changed'
    assert pre['verdict']=='PASS',key+' preflight did not pass'
    textfile=BASE/(key+'.txt')
    raw=textfile.read_text(encoding='utf-8')
    ref=re.search(r'^\s*(?:\d+\.\s*)?REFERENCES\s*$',raw,re.M|re.I)
    assert ref,key+' references heading not found'
    raw=raw[:ref.start()]
    source=dict(key=key,pdf=item['pdf'],pdf_sha256=sha(path),text_file=str(textfile.relative_to(ROOT)),text_sha256=sha(textfile),preflight=str((BASE/(key+'.preflight.json')).relative_to(ROOT)),bibliography_excluded=True)
    sources.append(source)
    for number,body in re.findall(r'PDF PAGE (\d+)\n(.*?)(?=PDF PAGE \d+\n|\Z)',raw,re.S):
        body=normalized(body)
        matches=list(re.finditer(PAT,body))
        pages.append(dict(source=key,pdf=item['pdf'],pdf_page=int(number),normalized_text=body,matches=matches,words=[m.group() for m in matches]))
def evidence(page,a,b):
    start=page['matches'][a].start();end=page['matches'][b].end()
    return dict(source=page['source'],pdf=page['pdf'],pdf_page=page['pdf_page'],matched_text=' '.join(page['normalized_text'][start:end].split()),context=' '.join(page['normalized_text'][max(0,start-75):min(len(page['normalized_text']),end+90)].split()))
tex=(ROOT/'paper/C-STMP/main.tex').read_text(encoding='utf-8')
abstract=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',tex,re.S).group(1).strip()
keywords=re.search(r'\\begin\{IEEEkeywords\}(.*?)\\end\{IEEEkeywords\}',tex,re.S).group(1).strip()
abstract_tokens=tokens(abstract);keyword_tokens=tokens(keywords)
rows=[];missing=[]
for word in sorted(set(abstract_tokens+keyword_tokens)):
    found=None
    for page in pages:
        if word in page['words']:
            i=page['words'].index(word);found=evidence(page,i,i);break
    if not found: missing.append(word)
    rows.append(dict(word=word,in_abstract=word in abstract_tokens,in_keywords=word in keyword_tokens,evidence=found))
save('WORD_AUDIT.json',dict(status='PASS' if not missing else 'FAIL',policy='Case-insensitive whole lexical tokens, including entire hyphenated words; Unicode typography normalized; no stemming, lemmatization, stopword exceptions or method-name exceptions; bibliography excluded.',sources=sources,abstract_word_count=len(abstract_tokens),abstract_unique_word_count=len(set(abstract_tokens)),abstract_and_keywords_unique_word_count=len(rows),missing=missing,words=rows))
phrases=json.loads((HERE/'PHRASES.json').read_text(encoding='utf-8'))
term_rows=[];missing_terms=[]
for phrase in phrases:
    wanted=tokens(phrase);hits=[]
    for page in pages:
        ws=page['words'];n=len(wanted)
        for i in range(len(ws)-n+1):
            if ws[i:i+n]==wanted:
                hits.append(evidence(page,i,i+n-1));break
    if not hits: missing_terms.append(phrase)
    term_rows.append(dict(phrase=phrase,evidence=hits))
save('TERM_AUDIT.json',dict(status='PASS' if not missing_terms else 'FAIL',policy='Whole consecutive lexical-token sequences; matching punctuation and typography are recorded in the evidence; no reordering, stemming or substitutions.',missing=missing_terms,terms=term_rows))
zh=(ROOT/'paper/C-STMP/sections/00_abstract_zh.md').read_text(encoding='utf-8').split('**关键词：**')[0]
md=['# C-STMP 摘要逐词核验','',
'范围为本轮英文摘要及关键词；中文是同义翻译。全部英文词形均在指定四篇论文的摘要或正文中检出，排除参考文献列表。只统一大小写及 Unicode 排版字符，不采用词干归并、近义词替代、停用词或方法名豁免。连字符词按完整词形匹配。','',
'本核验不表示整句来自文献，也不表示这些论文已经提出本项目的全部操作或证明本项目的结果。句子仍描述当前 AFDM 系统与接收机。技术含义、原文位置和适配边界另见 paper/C-STMP/docs/TERMINOLOGY.md；结果来自本项目已保存实验。','',
f'- 英文摘要：{len(abstract_tokens)} 词，{len(set(abstract_tokens))} 个不同词形。',
f'- 摘要与关键词合计：{len(rows)} 个不同词形；未检出词形：{len(missing)}。',
f'- 技术短语：{len(phrases)} 项；未检出项：{len(missing_terms)}。',
f'- 中文摘要：{len(re.findall(r"[\u4e00-\u9fff]",zh))-2} 个汉字（不计标题）。',
'- 逐词证据：[WORD_AUDIT.json](WORD_AUDIT.json)。',
'- 短语证据：[TERM_AUDIT.json](TERM_AUDIT.json)。',
'- 重查程序：[verify_source_words.py](verify_source_words.py)。','',
'| 摘要中的短语 | 原文首次匹配位置（PDF 页码） |','|---|---|']
for row in term_rows:
    hit=row['evidence'][0] if row['evidence'] else None
    md.append('| '+row['phrase']+' | '+(hit['source']+'，p.'+str(hit['pdf_page']) if hit else '未检出')+' |')
md+=['','“共享信道观测 / shared effective channel”已从摘要删除；改用 Shen 的 quasi-static property 与 consecutive frames。C-STMP 是作者的方法名，不在这四篇原文中，本轮摘要不使用该名称。旧版摘要源文件保存在 before/；不保存历史 PDF。逐句来源与本项目适配边界见 SENTENCE_SOURCES.md。']
(HERE/'SOURCE_WORD_CHECK.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps(dict(word_status='PASS' if not missing else 'FAIL',phrase_status='PASS' if not missing_terms else 'FAIL',abstract_words=len(abstract_tokens),abstract_unique_words=len(set(abstract_tokens)),all_unique_words=len(rows),phrases=len(phrases),missing_words=missing,missing_phrases=missing_terms),ensure_ascii=False))
sys.exit(1 if missing or missing_terms else 0)
