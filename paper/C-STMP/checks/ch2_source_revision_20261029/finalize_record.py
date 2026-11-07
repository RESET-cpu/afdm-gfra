from pathlib import Path
import collections
import difflib
import hashlib
import json
import re
from pypdf import PdfReader

root = Path(r'D:\afdm-gfra\paper\C-STMP')
run = root / 'checks/ch2_source_revision_20261029'
record = json.loads((run / 'source_and_authority.json').read_text(encoding='utf-8'))
target = root / 'sections/02_system_model.tex'
current = target.read_text(encoding='utf-8')
before = record['source_before'].replace('\r\n', '\n')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
labels = lambda s: re.findall(r'\\label\{([^}]+)\}', s)
old_labels, new_labels = labels(before), labels(current)
texts = '\n'.join(p.read_text(encoding='utf-8') for p in [root/'main.tex', *sorted((root/'sections').glob('*.tex'))])
known_labels = set(labels(texts))
missing_refs = sorted(set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', current))-known_labels)
bib = (root/'references.bib').read_text(encoding='utf-8')
bib_keys = set(re.findall(r'@\w+\s*\{\s*([^,\s]+)', bib))
cites = {key.strip() for group in re.findall(r'\\cite(?:\[[^]]*\])?\{([^}]+)\}', current) for key in group.split(',')}
unchanged = {p: sha(root/p)==expected for p, expected in record['other_manuscript_sha256'].items()}
log = (root/'main.log').read_text(encoding='utf-8', errors='replace')
log_issues = [line for line in log.splitlines() if re.search(r'undefined|Overfull|^!|Warning.*Reference|Warning.*Citation', line, re.I)]
begins = collections.Counter(re.findall(r'\\begin\{([^}]+)\}', current))
ends = collections.Counter(re.findall(r'\\end\{([^}]+)\}', current))
result = {
    'target': str(target), 'before_sha256': record['source_sha256'], 'after_sha256': sha(target),
    'all_original_labels_retained': set(old_labels).issubset(new_labels),
    'new_labels': sorted(set(new_labels)-set(old_labels)),
    'numbered_equations': current.count('\\begin{equation}'),
    'duplicate_chapter_labels': [k for k,v in collections.Counter(new_labels).items() if v>1],
    'missing_references': missing_refs, 'missing_citations': sorted(cites-bib_keys),
    'environment_counts_balanced': begins==ends,
    'other_manuscript_files_unchanged': unchanged,
    'compile_exit_code': 0, 'pdf_pages': len(PdfReader(root/'main.pdf').pages),
    'pdf_sha256': sha(root/'main.pdf'), 'compile_errors_or_unresolved_references_or_overfull': log_issues,
    'visual_review': 'PDF pages 2–4 inspected. Final acronym expansion on page 2 checked separately.',
    'scope': 'Source-based revision and mathematical/compilation consistency checks. This is not a claim that every final sentence is EXACT or TERM_ONLY.',
}
assert result['all_original_labels_retained']
assert all(unchanged.values()) and begins==ends
assert not missing_refs and not (cites-bib_keys) and not log_issues
assert not result['duplicate_chapter_labels']
(run/'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
(run/'chapter2.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True), current.splitlines(True), fromfile='02_system_model.tex (before)', tofile='02_system_model.tex (revised)')), encoding='utf-8')

notes = '''# 第二章对照修订记录（2026-10-29）

用户要求实际对照修改。本次已直接修订 D:\\afdm-gfra\\paper\\C-STMP\\sections\\02_system_model.tex，并重新生成 main.pdf。

## 已落地的修改

| 位置 | 来源及核对位置 | 实际修改 |
|---|---|---|
| 总述 | Ding PDF p.2；Shen PDF p.3 | 采用 Ding 的完整系统引入句；采用 Shen 的资源共享及无 GNSS、无预补偿句式。去除不属于本文的图示、载荷与广播设定。 |
| 物理信道 | Shen PDF pp.3–4；Huang PDF p.2 | 恢复物理信道引入、路径参数及差分时延解释的原文顺序和连接词；保留本文接收端公共传播时延补偿及阵列定义；补全 TSLs 首次全称。 |
| 导频与 AFDM | Cai PDF p.4；Ding PDF p.2；Huang PDF p.2 | 按原句分别定义帧、子载波和导频符号；恢复 IDAFT 的完整公式引入及 where 从句，增加与原矩阵表达等价的标量 IDAFT 式；将调制参数定义分开。 |
| 分数时延、多帧 | Huang PDF pp.2–3；Shen PDF pp.4–5 | 恢复泄漏、完整信道估计与多导频需求的论证；按 Shen 的 Fortunately / This characteristic / Furthermore 顺序衔接跨帧信道及相位关系。 |
| 活动与观测 | Cai PDF p.4；Shen PDF p.5 | 恢复活动指示函数、活动概率与小概率条件；恢复完整接收信号和 AWGN 的 where 从句；保留本稿矩阵排列，补清噪声、导频的索引定义；恢复部分正交导频句的能量从句。 |
| 贝叶斯问题 | Cai PDF pp.4–5 | 恢复高维后验、低复杂度消息传递及因子分解的完整表述和列向量 where 定义；显式写出各列高斯似然。删除未在该段展开支撑的先验“不精确/太复杂”概括句。 |

## 不能归为“仅替换术语”的保留内容

以下内容为本文模型所必需，未将其虚报为参考论文完整原句：

- 卫星接收端补偿公共传播时延的时间参考、阵列方向余弦及块内参数不变假设。
- 长 CPP 条件、延拓、波形与路径算子 G/D/B 的定义，以及相应附录指引。
- 本文信道张量、跨帧相位分离关系、wrap 定义和 Q×MN / KN×MN 的索引约定。
- 导频已知性、块内活动不变和本文导频能量归一化。
- 固定前端估计量、训练先验 q_tr、独立性假设、工作后验 q 及活动估计目标。

必要修正也不计作纯术语替换：Cai 的 Baye’s 排字错误改为 Bayes’；不保留不存在的图号，不引入 Shen 的后续参数更新或广播假设。仅有术语依据的句子不因此视为完整句式有来源。

## 验证范围

原 13 个公式标签全部保留；新增 1 个等价标量 IDAFT 公式，共 14 个编号公式。后验似然从联合形式显式写为独立观测列的乘积；没有改变已有信道、跨帧关系或估计目标。摘要、引言、其他章节、附录和参考文献的 11 个文件哈希均未变。

编译成功，PDF 共 14 页；无未定义引用、缺失文献或溢出版面。检查了第二章所在的第 2–4 页。未运行实验或训练。

strict_sentence_audit_20261029 中的 16/70 是修订前基线，不是本版统计。physical_sources.json、channel_sources.json 和 bayes_sources.json 为逐句候选来源记录，最终正文另有合稿修正；不得直接将候选统计当作最终通过率。本次没有声称最终全文已满足“每句只作术语替换”。

最终差异见 chapter2.diff；文件哈希、交叉引用和编译结果见 verification.json。
'''
(run/'REVISION_NOTES.md').write_text(notes, encoding='utf-8')

term = root/'docs/TERMINOLOGY.md'
entry = '''

## 2026-10-29 第二章严格原句审查后的实际修订

本次已按用户“必须对照修改”的要求修订第二章并编译。更正此前记录中的过度概括：“有相同术语/句式来源”不等于“整句仅替换必要术语”。上轮严格审查为修订前基线，本次未把它当作修订后通过统计。

Ding（PDF p.2）：系统总述、IDAFT 完整引入及调制参数。Shen（PDF pp.3–5）：资源共享、GNSS/预补偿、物理路径与时延、多帧衔接和堆叠。Cai（PDF pp.4–5）：导频分配、活动变量、接收信号及噪声 where 从句、部分正交导频、贝叶斯推断与完整列向量定义。Huang（PDF pp.2–3）：AFDM 子载波、共用 Doppler 假设、分数时延/Doppler 泄漏及完整信道估计的多导频需求。

本文的长 CPP/路径算子、阵列/矩阵索引、跨帧关系、固定前端参数、q_tr 与工作后验定义仍属必要模型说明，不宣称为参考文献完整原句。没有引入同步、终端预补偿、参数迭代更新等不适用假设。TSLs 首次出现补全为 terrestrial-satellite links (TSLs)。

原 13 个公式标签保留，新增等价标量 IDAFT 公式后为 14 个编号公式。摘要、引言、其他章节、附录及文献文件未修改；PDF 重新编译为 14 页，第二章第 2–4 页已检查。

详见 checks/ch2_source_revision_20261029/REVISION_NOTES.md、chapter2.diff 和 verification.json。候选逐句来源文件与最终正文有合稿差异，不可直接充作最终全部通过证明。
'''
assert '## 2026-10-29 第二章严格原句审查后的实际修订' not in term.read_text(encoding='utf-8')
with term.open('a', encoding='utf-8') as f:
    f.write(entry)
print(json.dumps({k:v for k,v in result.items() if k not in ['other_manuscript_files_unchanged']}, ensure_ascii=False, indent=2))
