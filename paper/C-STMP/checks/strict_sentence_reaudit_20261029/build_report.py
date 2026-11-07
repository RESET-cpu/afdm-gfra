from pathlib import Path
import collections
import hashlib
import json
import re
import runpy

run=Path(__file__).parent
manifest=json.loads((run/'manifest.json').read_text(encoding='utf-8'))
adj=json.loads((run/'ADJUDICATION.json').read_text(encoding='utf-8'))
overrides={x['sentence_id']:x for x in adj['overrides']}
def norm(s): return re.sub(r'\s+','',re.sub(r'\\label\{[^}]*\}','',s))
names=['系统总述','物理信道与阵列','导频与AFDM调制','CPP','分数时延与信道表示','多帧与相位','活动、观测和导频矩阵','块稀疏性','问题目标','前端参数和训练先验','精确贝叶斯估计','后验分解及估计目标','深度生成先验结尾']
counts=collections.Counter()
rows=[]
full=[]
all_sentences=[]
for i,p in enumerate(manifest['paragraphs']):
    d=json.loads((run/f"{p['id']}.json").read_text(encoding='utf-8-sig'))
    ss=d['sentences']
    assert norm(''.join(x['draft_tex'] for x in ss))==norm(p['text']),p['id']
    assert len(set(x['id'] for x in ss))==len(ss)
    local=collections.Counter()
    for x in ss:
        x=dict(x)
        x['auditor_category']=x['category']
        if x['id'] in overrides:
            x['category']=overrides[x['id']]['final_category']
            x['root_adjudication']=overrides[x['id']]
        assert x['category'] in ['EXACT','TERM_ONLY','OTHER_CHANGE','NO_SOURCE','UNVERIFIED']
        local[x['category']]+=1
        all_sentences.append(x)
    counts.update(local)
    passed=local['EXACT']+local['TERM_ONLY']
    rows.append({'id':p['id'],'topic':names[i],'lines':p['source_lines'],'total':len(ss),'language_pass':passed,'all_language_pass':passed==len(ss),'counts':dict(local),'structure':d['paragraph_structure']})
    full.append(f"## {p['id']}：{names[i]}（正文第 {p['source_lines'][0]}–{p['source_lines'][1]} 行）\n\n")
    if any(x['id'] in overrides for x in ss):
        full.append('总代理裁决：本段存在语言/公式分类调整，见 ADJUDICATION.json；下方保留子代理原始判断。\n\n')
    body=(run/f"{p['id']}.md").read_text(encoding='utf-8')
    full.append(body+'\n\n---\n\n')

assert hashlib.sha256(Path(manifest['source_file']).read_bytes()).hexdigest()==manifest['source_sha256']
total=sum(counts.values())
out={'source_file':manifest['source_file'],'source_sha256':manifest['source_sha256'],'paragraphs':rows,'sentences':all_sentences,'counts':dict(counts),'sentence_count':total,'paragraph_count':len(rows),'all_sentence_language_pass_paragraphs':[x['id'] for x in rows if x['all_language_pass']],'manuscript_unchanged':True,'adjudication':adj}
(run/'FINAL_AUDIT.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sources=json.loads((run/'SOURCES.json').read_text(encoding='utf-8'))
source_hashes={x['key']:hashlib.sha256(Path(x['pdf']).read_bytes()).hexdigest()==x['sha256'] for x in sources}
assert all(source_hashes.values())
project=run.parent.parent
previous=json.loads((project/'checks/ch2_source_revision_20261029/verification.json').read_text(encoding='utf-8'))
pdf_unchanged=hashlib.sha256((project/'main.pdf').read_bytes()).hexdigest()==previous['pdf_sha256']
assert pdf_unchanged
verification={'manuscript_unchanged':True,'pdf_unchanged':pdf_unchanged,'all_source_pdf_hashes_match':source_hashes,'paragraph_count':len(rows),'sentence_count':total,'coverage_all_paragraphs_exact':True,'all_paragraphs_have_json_and_md':all((run/f"{p['id']}.md").is_file() for p in rows),'assignments':[{'paragraph_id':p['id'],'agent':'/root/reaudit_'+p['id'].lower(),'report':p['id']+'.json'} for p in rows],'root_review':'总代理独立查看并对照了全部EXACT/TERM_ONLY句的原句与当前句，以及OTHER_CHANGE关键差异；数学适配和语言分类分开。','adjudication_count':len(overrides)}
(run/'VERIFICATION.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary=f'''# 第二章逐句原文复审

结论：当前第二章仍不满足“每一段、每一句都仅替换必要术语，其余不变”。

本次以 D 盘实际保存的第二章为准，共 {len(rows)} 个正文段落，分别交给 {len(rows)} 个新建子代理审查；子代理不读取同伴或旧审查的判断。总代理另行核对通过项与关键差异并统一口径。子代理使用同一工具与模型体系，不等于跨模型独立验证。

审查对象 SHA-256：`{manifest['source_sha256']}`。审查期间正文未修改。

## 句子层面结果

共 {total} 个完整语法句（公式及后接 where 等从句合并计算）：

| 类别 | 句数 |
|---|---:|
| 原句一致 EXACT | {counts['EXACT']} |
| 仅必要术语/符号替换 TERM_ONLY | {counts['TERM_ONLY']} |
| 有来源，但另有增删改写 OTHER_CHANGE | {counts['OTHER_CHANGE']} |
| 本次检索未定位完整对应句 NO_SOURCE | {counts['NO_SOURCE']} |
| 尚不能核实 UNVERIFIED | {counts['UNVERIFIED']} |

EXACT/TERM_ONLY 合计 {counts['EXACT']+counts['TERM_ONLY']}/{total}。这些是语言对齐结果；公式适配另列，不表示公式相同或模型条件被原论文证明。未定位来源也不等于技术内容错误或全世界论文均无此句。

## 分段覆盖

| 段落 | 内容 | 语言通过/全部 | 全段句子均通过 |
|---|---|---:|---|
'''
for x in rows:
    summary+=f"| {x['id']} | {x['topic']} | {x['language_pass']}/{x['total']} | {'是' if x['all_language_pass'] else '否'} |\n"
summary+='''
段落组织单独记录：不同论文之间拼接、同一原段抽取或重排、删去中间解释句，都不能由句子层面的通过掩盖。完整组织证据见各段报告的 paragraph_structure。

## 明确不符合要求的例子

- P02：Huang 的 resulting 被删除；Shen 原句的图示引导被删除；多个 Let 定义没有定位完整原句。
- P03：采样间隔原文为 where 从句，当前抽出并改为 Let…denote，谓语和句法改变。
- P05：公式引导句沿用了 Huang 的开头，但原 where 的等效时延定义被替换成本文的输入/输出信道系数解释。
- P06：前三句可按 Shen 原句进行语言对齐，但原段中间七句被删；最后 Since…公式…where wrap… 整句未找到对应原句。
- P10、P12：训练先验、固定前端估计量及工作后验等说明需逐句区分来源与本文自述，不能仅凭采用了 Cai 的消息传递术语就认定原句复用。

## 文件与核查边界

- `FULL_AUDIT.md`：13 份子代理详细报告的汇编；包括当前句、原句或定位、页码和差异。
- `FINAL_AUDIT.json`：总代理裁决后的完整逐句记录与统计。
- `ADJUDICATION.json`：保留原始判断与最终分类调整的理由。
- `coverage_status.json`：逐句文本拼接覆盖检查。
- `SOURCES.json`：Shen、Cai 期刊版及 v2、Ding、Huang，以及相关 Li、Bemani PDF；本轮 PDF 哈希与已有原件记录一致。检索结论限定于该语料，不声称已检查所有其他论文。

本次为来源审查，没有改写第二章、修改模型或重新编译 PDF。不能把“有术语依据”“技术合理”或“语言相似”替代用户要求的完整原句对齐。
'''
(run/'SUMMARY.md').write_text(summary,encoding='utf-8')
(run/'FULL_AUDIT.md').write_text('# 第二章当前版本逐段逐句复审完整记录\n\n最终统计和裁决以 SUMMARY.md、FINAL_AUDIT.json 和 ADJUDICATION.json 为准；以下保留各代理独立原始报告。\n\n'+''.join(full),encoding='utf-8')
print(json.dumps({'counts':dict(counts),'sentences':total,'paragraphs':len(rows),'all_language_pass_paragraphs':out['all_sentence_language_pass_paragraphs']},ensure_ascii=False,indent=2))
