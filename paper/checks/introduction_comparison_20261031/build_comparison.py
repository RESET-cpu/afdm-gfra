from pathlib import Path
import difflib
import hashlib
import html
import json
import re

root = Path(r'D:\afdm-gfra\paper\C-STMP')
out = Path(__file__).resolve().parent
old_path = root / 'checks/compress_20261030/before/sections/01_introduction.tex'
new_path = root / 'sections/01_introduction.tex'
old = old_path.read_text(encoding='utf-8')
new = new_path.read_text(encoding='utf-8')
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
protected = [root/'main.tex', root/'main.pdf', root/'sections/00_abstract_zh.md', new_path]
before_hashes = {str(p): digest(p) for p in protected}

cites = dict(zip(['cai2026','xu2026','shen2025','3gpp38300','3gpp22865',
                 'huang2026','hadani2017','ding2026','bemani2022','song2019',
                 'arvinte2023','ying2026','wei2026'], range(1,14)))
refs = {'sec:system':'II','sec:algorithm':'III','sec:generative':'IV',
        'sec:overall':'V','sec:simulations':'VI'}

def plain(s):
    s = re.sub(r'\\cite\{([^}]+)\}', lambda m: '[' + ', '.join(str(cites[k]) for k in m[1].split(',')) + ']', s)
    s = re.sub(r'\\ref\{([^}]+)\}', lambda m: refs[m[1]], s)
    s = s.replace('~', ' ').replace('--', '–')
    s = re.sub(r'\s+', ' ', s).strip()
    assert '\\' not in s, s
    return s

def split_source(s):
    s = re.sub(r'\\section\{Introduction\}\s*\\label\{sec:introduction\}\s*', '', s)
    head, tail = s.split(r'\begin{enumerate}[label=\arabic*)]')
    items, ending = tail.split(r'\end{enumerate}')
    paras = re.split(r'\n\s*\n', head.strip())
    item_list = [x.strip() for x in items.split(r'\item') if x.strip()]
    assert len(paras) == 7 and len(item_list) == 3
    return paras, item_list, ending.strip()

op, oi, oe = split_source(old)
np, ni, ne = split_source(new)
sections = [
    ('研究背景与 GFRA 动机', op[0], np[0],
     '删除了农业、气候监测等应用例子，将设备特点和接入动机合并。需要纠正：原文是“reducing … access latency”，现文“avoids … propagation latency”可能被理解为避免传播时延，超过原句含义。', True),
    ('GNSS 预补偿与研究需求', op[1], np[1],
     '保留 Release 17、Release 19 及 GNSS-independent 的背景，删减了电池寿命、偏远低功耗设备适用性和成因说明。主线仍在，但动机铺垫变短。', False),
    ('从 OTFS 到 AFDM', op[2], np[2],
     '保留变换维度、复杂度及 full diversity 的比较；删除了对多普勒鲁棒性的单独说明，以及末尾联系低功耗 IoT 设备的总结句。', False),
    ('JADCE、稀疏方法与分数时延／多普勒', op[3], np[3],
     '压缩 CS 建模、GNN 与预设网格的介绍，保留功率泄漏削弱稀疏性这一动机。', False),
    ('生成式方法、STMP 与现有不足', '\n\n'.join(op[4:6]), '\n\n'.join(np[4:6]),
     '重组两段：将 STMP 的介绍并入生成式方法综述，后一段集中说明 AWGN 近似条件与活动概率问题。删除了计算成本、去噪精度下降及误差向线性模块传递的部分展开；条件矩与边缘似然的关键区分仍在，但论证展开减少。', False),
    ('贡献之前的研究对象说明', op[6], np[6],
     '原文明确承接“GNSS-independent AFDM-GFRA for LEO satellite IoT systems”；现文仅剩“Our contributions are”。研究对象在前文仍有提及，但这里的承接被删掉了。', True),
    ('贡献 1：多帧 AFDM 模型', oi[0], ni[0],
     '保留分数效应、CPP 相位和增加观测而不增加信道维数。需要恢复：原文的“remains approximately constant over consecutive frames”被压成“the same effective channel”，丢失“近似”限定；大差分时延／多普勒由卫星端处理的贡献说明也缩短了。', True),
    ('贡献 2：生成式信道先验', oi[1], ni[1],
     '保留多天线有效信道、有色高斯扰动以及后验均值／方差。删除了本条中的 fractional delays and Doppler shifts；原句以 learned prior 为主语，现句改为 trained denoiser，原句对整体计算方式的表述更稳妥。', False),
    ('贡献 3：活动概率与消息传递接收机', oi[2], ni[2],
     '保留密度比估计、软活动概率和高斯外信息，但删除了活动／非活动分布的比较对象、结构化多帧模型以及与线性模块迭代交换的明确表述。原来的性能句分别点明活动检测和信道估计，现句只说 improves on STMP，贡献描述不如原文充分。', True),
    ('论文结构介绍', oe, ne, '本段逐字保持（忽略换行）。', False),
]

tokenize = lambda s: re.findall(r'\s+|\w+(?:[\-’\']\w+)*|[^\w\s]', s)
def highlighted(a, b):
    aa, bb = tokenize(a), tokenize(b)
    left, right = [], []
    for tag, a0, a1, b0, b1 in difflib.SequenceMatcher(None, aa, bb, autojunk=False).get_opcodes():
        x, y = html.escape(''.join(aa[a0:a1])), html.escape(''.join(bb[b0:b1]))
        left.append(x if tag == 'equal' else '<mark class="removed">'+x+'</mark>')
        right.append(y if tag == 'equal' else '<mark class="added">'+y+'</mark>')
    l, r = ''.join(left), ''.join(right)
    assert html.unescape(re.sub('<[^>]+>', '', l)) == a
    assert html.unescape(re.sub('<[^>]+>', '', r)) == b
    return l, r

cards, nav, manifest_sections = [], [], []
old_all, new_all = [], []
for i, (title, a, b, note, priority) in enumerate(sections, 1):
    a, b = plain(a), plain(b)
    old_all.append(a); new_all.append(b)
    l, r = highlighted(a, b)
    nav.append(f'<a href="#s{i}">{i}. {html.escape(title)}</a>')
    cards.append(f'''<section id="s{i}" class="card">
      <h2>{i}. {html.escape(title)}{' <span class="flag">重点复核</span>' if priority else ''}</h2>
      <p class="note">{html.escape(note)}</p>
      <div class="columns"><article><h3>压缩前原文</h3><p lang="en">{l}</p></article>
      <article><h3>当前压缩版</h3><p lang="en">{r}</p></article></div>
      </section>''')
    manifest_sections.append({'title':title,'before':a,'after':b,'assessment':note,'priority':priority})

def count_words(text):
    text = re.sub(r'\[[0-9, ]+\]', '', text)
    return len(re.findall(r"[A-Za-z]+(?:[-’'][A-Za-z]+)*", text))
wc_old = count_words(' '.join(old_all)); wc_new = count_words(' '.join(new_all))
page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>引言压缩前后对照</title>
<style>
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f4f5f7;color:#26303d;font-family:system-ui,"Microsoft YaHei",sans-serif;line-height:1.65}
main{max-width:1450px;margin:auto;padding:32px 28px 80px}h1{font-size:30px;margin:0 0 12px}h2{font-size:20px;margin:0 0 12px}h3{font-size:14px;letter-spacing:.03em;color:#536272;margin:0 0 12px}
.lead,.card{background:white;border:1px solid #dce1e7;border-radius:12px;padding:26px;margin-bottom:24px}.summary{border-left:4px solid #d3892c;padding:12px 18px;background:#fff7e9}.subtle{font-size:14px;color:#687384}
nav{display:flex;flex-wrap:wrap;gap:8px 20px;margin:20px 0}a{color:#225b82;text-decoration:underline;text-underline-offset:3px}.columns{display:grid;grid-template-columns:1fr 1fr;gap:30px}article+article{border-left:1px solid #e0e5ea;padding-left:30px}
article p{font-family:Georgia,"Times New Roman",serif;font-size:17px;line-height:1.8;margin:0;overflow-wrap:anywhere}mark{color:inherit;padding:1px 0}.removed{background:#fde6e4}.added{background:#dff1e7}
.note{background:#f1f4f7;padding:12px 16px;border-radius:6px;font-size:15px;margin:0 0 24px}.flag{font-size:12px;font-weight:500;color:#8a4b07;background:#fff0d7;padding:3px 8px;border-radius:4px;margin-left:10px}
.legend span{display:inline-block;padding:2px 9px;margin-right:12px}.card{scroll-margin-top:14px}
@media(max-width:850px){main{padding:18px 12px}.lead,.card{padding:19px}.columns{grid-template-columns:1fr}article+article{border-left:0;border-top:1px solid #e0e5ea;padding:20px 0 0}h1{font-size:25px}}
@media print{body{background:white}main{padding:0}.lead,.card{border-radius:0;box-shadow:none}nav{display:none}h2{break-after:avoid}article p{font-size:11pt}.card{break-inside:auto}}
</style><main><div class="lead"><h1>引言压缩前后对照</h1>
<p>2026-10-31 · GP-CCD-MP-DRE 稿件 · 完整引言逐段展示</p>
<div class="summary"><strong>复核意见：建议恢复压缩前的引言。</strong><br>
当前版保留了主要研究线索，但贡献陈述明显缩短，而且有两处措辞丢失了原有含义或限定。恢复对象是<strong>本轮压缩前、已完成术语统一</strong>的版本。</div>
<p>本次仅生成对照，论文源码和阅读 PDF 尚未改回；中英文摘要没有改动，也未重新生成。</p>
<p class="subtle">计数口径：自动统计正文英文词，排除引用编号和 LaTeX 命令；连字符词计作一词。原文 WORD_OLD 词，压缩版 WORD_NEW 词，约减少 WORD_PCT%。</p>
<p class="legend"><span class="removed">粉色：被删去或替换的文字</span><span class="added">绿色：新增或改写的文字</span></p>
<p class="subtle">左右两栏为源码中实际英文，仅合并换行并将引用转换为当前论文编号；中文说明是本次复核意见。下方覆盖全部引言，含未修改的论文结构段。</p>
<nav>NAV</nav></div>CARDS
<p class="subtle">原文：checks/compress_20261030/before/sections/01_introduction.tex<br>现文：sections/01_introduction.tex<br>所有分段和源文件校验值见 comparison.json。</p></main></html>'''
page = page.replace('WORD_OLD',str(wc_old)).replace('WORD_NEW',str(wc_new)).replace('WORD_PCT',str(round(100*(1-wc_new/wc_old))))
page = page.replace('NAV',''.join(nav)).replace('CARDS',''.join(cards))
(out/'引言压缩前后对照.html').write_text(page,encoding='utf-8')
manifest = {'date':'2026-10-31','before_path':str(old_path),'after_path':str(new_path),
    'before_sha256':digest(old_path),'after_sha256':digest(new_path),
    'word_counts':{'before':wc_old,'after':wc_new,'method':'English words; hyphenated word counted once; citations and LaTeX commands excluded'},
    'sections':manifest_sections,'manuscript_files_unchanged':all(digest(Path(p))==h for p,h in before_hashes.items()),
    'protected_file_hashes':before_hashes}
assert manifest['manuscript_files_unchanged']
(out/'comparison.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'introduction.diff').write_text(''.join(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile='before/01_introduction.tex',tofile='current/01_introduction.tex')),encoding='utf-8')
print(json.dumps({'before_words':wc_old,'after_words':wc_new,'sections':len(sections),'manuscript_unchanged':manifest['manuscript_files_unchanged'],'html':str(out/'引言压缩前后对照.html')},ensure_ascii=False))
