"""Create a current, equation-by-equation provenance ledger and integrity report."""
from pathlib import Path
import re,json,hashlib,difflib
RUN=Path(__file__).resolve().parent
PAPER=RUN.parents[1]
ROOT=PAPER.parents[1]
old=json.loads((RUN.parent/'notation_formula_review_20261104/EQUATION_INVENTORY.json').read_text(encoding='utf8'))
oldnums={x['label']:x['number'] for x in old}
aux=(PAPER/'main.aux').read_text(encoding='utf8')
eqnums=dict(re.findall(r'\\newlabel\{((?:eq:|frontend:eq:)[^}]+)\}\{\{([^}]+)\}',aux))
inventory=[]
for path in [PAPER/'main.tex',*sorted((PAPER/'sections').glob('*.tex'))]:
    if path.name=='appendix_second_order_training.tex':continue
    src=path.read_text(encoding='utf8')
    for m in re.finditer(r'\\label\{((?:eq:|frontend:eq:)[^}]+)\}',src):
        label=m[1]
        inventory.append({'label':label,'number':eqnums[label],'old_number':oldnums[label],
                          'file':path.relative_to(ROOT).as_posix(),'line':src.count('\n',0,m.start())+1})
inventory.sort(key=lambda x:(0,int(x['number'])) if x['number'].isdigit() else (ord(x['number'][0]),int(x['number'].split('.')[1])))

groups=[
('physical-channel upa','文献模型适配','Shen §II-A，Huang §II（PDF p.2），阵列与共同 Doppler 模型。本文固定块内路径参数并引入接收端公共时延补偿；不宣称逐字原式。'),
('afdm-time-signal daft','同类原式','Bemani AFDM 的 DAFT/IDAFT 定义；作者稿 §II-B 式 (16)、§III-A 式 (18)。转置、指数符号及 1/√N 已核对。'),
('cpp continuous-waveform','文献基础＋本文延拓','Bemani 学位论文 §3.1.1 式 (3.7)、(3.9)，印刷 pp.26–27/PDF pp.52–53；§3.2 式 (3.14)，印刷 p.29/PDF p.55。本文采用无量纲时间、取模和多周期 CPP；已核对采样及延拓恒等式。'),
('channel path-operator-system','物理模型推导','Huang §II 式 (4)–(5)，PDF p.2；Bemani 学位论文 §3.2 式 (3.13)–(3.15)。本文将路径波形采样、Doppler 乘法与 DAFT 组合；不是 Huang 的同一索引原式。'),
('twc-frame-channel effective-pilot','本文直接推导/定义','由 D_{ν,g_q}=exp(j2πνqT_frame)D_{ν,g_0} 及每设备共同 Doppler 得出；β 取主值只选相位代表，不丢弃 Doppler 候选。设备块导频定义没有额外假设。'),
('mmv','文献分块形式＋本文排列','Cai §II-A 式 (4)，Shen §II-C 式 (14)–(15)；本文 H_k 为 N×MN，与 Cai 的 N×M 不同。已核对物理逐分量叠加、设备块乘法及 vec 顺序。'),
('working-posterior','同类因子分解','Cai §II-B 式 (5)，其因子图为 Fig.2。本文 q_tr 为训练信道分布；先验因子和确定性约束按分布理解，不要求物理信道具有全维 Lebesgue 密度。'),
('linear-mean linear-variance linear-extrinsic','标准 Gaussian 运算','Cai §III-A；Ma–Ping §III-C 式 (12)、(15c)，作者稿 PDF p.3；均值及逆协方差来自 Gaussian conditioning，外信息来自 Gaussian 相除。保留一般矩阵式，不能套用 A 行正交的简式。'),
('pseudo-awgn conditional-channel-integrals','工作模型与条件矩','Cai §III-B1 式 (20)、(22)–(23)。本文 D=MN²；近似号对应有限网络及保留 site 后的条件均值/方差，不承诺真实迭代误差严格 AWGN。'),
('query-densities local-activity','Bayes 公式','Cai §III-B2；Menon §3 式 (6)–(9)。本文在任意训练信道分布下对 Gaussian 似然取期望；式中 q_1 是加噪后的密度，q_tr 本身无需有普通密度。'),
('mixture','Bernoulli–Gaussian 均值','Cai §III-B3 式 (32)–(35)，Liu §III-C–III-D。零分量与活动分量的含义保留，用文字和均值式替代测度展开。'),
('joint-spatial-covariance joint-average-variance','混合矩的本文排列','由 Cov(vec X)=p t I+p(1−p)vec(Hpost)vec(Hpost)^H，按同一收发坐标取天线子块并平均得到。Cai 的混合矩提供基础，M×M 空间平均形式为本文推导。'),
('nonlinear-extrinsic','标准 Gaussian 相除','Cai §III-B3 式 (40)–(42)；令 b=tbar_X/v 即得到当前简记。b 的数值裁剪是另列的实现规则。'),
('colored-query','复数到实数表示','proper complex Gaussian 的实虚协方差转换；Neeser–Massey 的 proper complex 概念。Σ 的 1/2、负虚部位置及 D/2D 区别保留，不能直接套用复数 score 的另一种梯度约定。'),
('tweedie-mean tweedie-covariance mean-derivative-variance','已有恒等式的约定转换','Dytso 正式出版版 §I-B 式 (9)、§III Proposition 1 式 (17)，PDF p.3/印刷 p.1885；Cai §IV-A 式 (44)–(45)。本文 Jacobian 为输出行/输入列，因此 P=JΣ；Dytso 的 Jacobian 定义转置，不可机械复制乘法顺序。'),
('denoising-score-objective first-loss','DSM 的协方差加权适配','Vincent 的 denoising score matching；Cai §IV-B1 的加噪 score 学习。本文在固定 Σ 下加权并代入 s=Σ^{-1}(f−u)，直接得到均值损失；条件期望最优性不依赖 Karras 的训练权重。'),
('derivative-trace','随机迹估计的本文适配','Metzler §V-B，作者稿 v5 PDF p.15，使用 Gaussian 方向和单边差分。本文用 E[zz^T]=I 的随机符号方向、w=Σ^{1/2}z、中央差分；由 E[w^TJw]=tr(JΣ) 得出，不是 Metzler 的原式。'),
('activity-log-odds classifier-loss ideal-logit activity-probability','已有分类与密度比关系','Menon §3 式 (6)–(9)、§4.2 式 (16)–(17)，PDF pp.2–3；§4.2 明确 balanced logistic classifier 的密度比为 exp(logit)。本文使用 a∈{0,1} 和接收端活动先验 ρ。'),
('pooled-variance','本文数值规则','对设备方差求平均并设置正下限。没有将此规则包装成新定理，也不声称来自某篇论文的同式；已去掉只使用一次的 τ_raw。'),
('site-update conditional-moments','Gaussian 外信息/条件矩','Cai §III-B1 式 (24)–(27)，Vehtari §2.1 的 site 概念。本文按设备保留 site，τ_k^ext 取代与 c1/c2 重名的 c_k；重新相乘可恢复新网络矩，保留旧 site 时 Hpost 不必等于 F。'),
('noise-estimation','标准样本协方差与谱估计','Wax–Kailath 的 MDL 源数估计与尾部特征值均值；Nadakuditi–Edelman 的低秩信号加白噪声模型。本文把 QN 个空间向量作为样本；不是新的噪声估计算法。'),
('query-variance-target','EM 思路下的本文目标','Vila–Schniter §III-A 式 (22)–(27)，PDF p.4/印刷 p.4661，针对观测噪声。本文将相同的期望 Gaussian 负对数似然计算用于局部输入，得到残差能量＋后验方差；不是原论文的观测噪声更新原式。'),
('query-variance-update input-damping output-damping','本文数值更新/文献阻尼形式','Cai §V-B1 给出消息阻尼思路；κ、作用对象、顺序、首轮处理属于本稿设置。没有通用理论要求其参数取本文数值。'),
('linear-fraction','一般 LMMSE 的等价计算','将一般 LMMSE 后验协方差按 A 的奇异值展开，使用 KN−rank(A) 个零奇异值贡献。与前文直接矩阵计算核对；无需另一篇论文存在同名 f_L。'),
('iteration-complexity','本文运算计数','由当前步骤的矩阵维度和 1+2L_z 次去噪器调用计数，网络调用代价保留为 Cθ/Cφ。不是文献定理；本轮没有重跑硬件计时或重新审计全部实现。'),
('pilot','部分 DFT 构造适配','Cai §II-A 对部分正交导频的条件；本文采用 Q 行 KN 点 DFT、列置换和单位模列相位。PP^H=KE_pI 及每设备每帧能量已核对。'),
('snr simulation-nmse simulation-aer','实验指标定义','按接收信号功率、能量加权 NMSE 和活动错误计数定义；无需参考论文使用相同场景索引。保留原统计方式、所有数值及图。'),
('simulation-colored-covariance','本文训练分布定义','I 与归一化 ZZ^H 的凸组合；ξ∈[0,0.5] 保证正定，trace=16。Shastri 支撑相关噪声训练思路，不支撑声称这组随机采样参数是原文方案。'),
('mean-preconditioning','Karras 标量形式的矩阵扩展','Karras Table 1（PDF p.3）、§5 式 (7)–(8)（PDF p.8），Appendix B.6。本文用 Σ 的矩阵函数；输入与名义残差的协方差核对通过，Σ=σ²I 时严格退化为原标量预条件。'),
('gaussian-evidence','Gaussian 似然比','由 CN(R;E,(τext+v)I)/CN(R;0,vI) 取对数，得到平方残差及 log determinant 项。与 Cai §III-B2 的活动似然计算同类，当前维度和 site 记号为本文适配。'),
('path-entry-expansion integer-operator integer-prefix-phase','AFDM 算子的本文展开','Bemani 的整数时延 CPP/循环移位矩阵；Huang §II 式 (5) 的分段分数时延基底。本文明确保留参考帧相位、完整时延和 wrap 区间；与直接波形采样后 DAFT 的计算相符。'),
]
lookup={}
for labels,kind,evidence in groups:
    for s in labels.split():lookup['eq:'+s]=(kind,evidence)
lookup['frontend:eq:phase-atom']=('本文相位前端定义','由前文路径算子作用于已知导频得到；G0 去除可由未知增益吸收的常数相位。d 与 d+jN 的等价已核对；单主径近似不等于物理信道的完整多径模型。')
lookup['frontend:eq:phase-fit']=('已有最小二乘形式的模型适配','O’Leary–Rust 的 separable nonlinear least squares / variable projection；当前多设备 AFDM 原子与候选选择属于本稿相位算法，不称为 Shen 原式。')
lookup['frontend:eq:phase-variable-projection']=('已有 variable projection 关系','固定 d,ν 后的线性最小二乘解与投影残差；与独立最小二乘求解核对。更新策略和 M4 的后续相位工作按既有决定处理。')
assert len(inventory)==57
assert set(lookup)=={x['label'] for x in inventory},set(lookup)^{x['label'] for x in inventory}
for x in inventory:x.update(zip(['kind','evidence'],lookup[x['label']]))
(RUN/'EQUATION_INVENTORY.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf8')

intro='''# 变量与公式修订、逐式出处复核

日期：2026-11-04。状态：已按作者“请你修正一下，然后再详细检查”实施。本轮限于变量形式、公式组织及相应出处；语言建议表仍暂缓。两版稿件共用正文。

## 已完成的修改

| 内容 | 本轮处理 |
|---|---|
| 第二章 Y、A、X、W 的四行 entries | 删除独立索引式和重复的逐分量观测式，改用设备矩阵块定义，保留 Y=∑A_kX_k+W=AX+W。 |
| 张量和矩阵混用 | 接收机统一为 N×MN 设备矩阵；各天线 N×N 信道矩阵转置后横向拼接。标准列 vec 顺序与原 M×N×N 数组一致，网络入口明确重排。 |
| 大小写/字体 | H、X、R、W、E、F 等矩阵使用粗体大写；实数网络输出与 score 用粗体小写；导频标量采用 [p_qk]_n，删除 P_qkn/A_qkn 等并行别名。E_p、P_H 等功率标量保持原约定。 |
| c1/c2 与 c_k 重名 | AFDM 参数 c1/c2 保持；site 方差统一为 τ_k^ext，算法、Gaussian 后备判决和附录 C 同步。 |
| 条件均值记号 | μ_k 改为 H_k^post，网络输出 F_k 单独保留；保留旧 site 时两者不能合并。 |
| 冗余后验层 | 删除单独 π_v 后验及其积分层，直接写条件期望/协方差目标；Bernoulli–Gaussian 近似保留文字定义和均值式，删除不必要的测度变量。 |
| 训练先验修正 | 训练已经均衡，删除 π_tr 与恒为零的 logit π_tr；保留接收端 logit ρ。Menon 引文精确到 §4.2 式 (17)。 |
| 一次性辅助量 | 删除 τ_raw，合并平均与正下限；全局 MMSE/活动概率目标改为行内式，β 的 floor 展开改为模 2π 的主值定义。 |
| 进一步发现的 Y0 重名 | Y_0 已指第 0 帧观测；无噪声整块观测改为 Y_sig，SNR 定义不变。 |
| Algorithm 1 表述 | 明确先归一化再初始化，与原说明一致；将含混的第二个 Otherwise 改为“输入方差在训练区间外”。未改变接收机代码。 |
| 方法图及引用 | Fig.2/3 同步矩阵、Hpost、均衡训练记号。实验图、图 9 坐标范围、数值及书目保持。 |

原稿 61 个编号公式减为 **57 个**（正文 51 个、附录 A/B 共 6 个）。删除的是原式 (11)、(13)、(15)、(20) 的独立编号层，不是删除观测关系或贝叶斯估计目标。当前编号见下表，历史审查中的旧编号不继续当作当前编号使用。

## 哪些没有文献中的逐字原式，为什么保留

1. **长 CPP、分数时延与跨帧路径算子。** Bemani 的连续波形和 CPP 有直接出处；本文的取模形式、多周期延拓及参考帧起点是本模型推导。已重新读取学位论文原页，并将波形引出句改成明确的文献基础加 chirp-periodic extension。不能把 Huang 的式 (5) 或 Bemani 的单周期式直接说成当前完整原式。
2. **空间混合协方差和 SVD 简记。** 分别由 Bernoulli–Gaussian 混合的全协方差、一般 LMMSE 的谱分解直接得出。属于必要的维度适配，未发现需要删除的无依据运算。
3. **有色协方差下的中央差分迹估计。** Dytso 给精确条件均值导数恒等式；Metzler 给 Monte Carlo 散度估计思路。本文的随机符号方向、Σ 加权和中央差分组合是推导后的近似实现。不能将有限网络和单个随机方向的结果说成精确后验方差。
4. **矩阵预条件。** Karras 原文为标量；本文的 BΣ/KΣ/OΣ 是矩阵扩展。按名义 Cov(h_R)=σ_d²I，输入归一化和残差目标协方差可直接验证；白噪声时退化为 Karras。它不是“物理信道本身为白色 Gaussian”的假设，也不等于复制 Karras 的训练 loss weighting。
5. **输入方差尺度、方差下限、相关协方差采样。** v_tar 来自固定近似后验下的期望负对数似然；κ 阻尼、下限与训练噪声采样是本文明确给出的数值设置。没有同名原式不构成错误，不应给它们补造一个文献算法名称。
6. **相位前端。** 最小二乘及 variable projection 有已有方法依据；AFDM 原子、单主径候选和更新安排是本稿方案。此次只核对记号、可吸收相位和投影代数，不把它升级为相位方案已完成验证，也不重开既有 M4 讨论。

## 两处容易因照搬文献而改错的地方

- P 行正交不意味着各设备加入不同相位后的 A 仍行正交。保留一般 LMMSE；小尺寸反例的相对偏离为 0.474，不能套用 Cai 特殊条件下的简化增益。
- Dytso 正式版的 Jacobian 是输入行/输出列；本文为输出行/输入列，因此 P_R=J_mΣ。乘法顺序、复数到实数的 1/2 和每复坐标方差除以 D 均保留。旧作者稿与正式版的式号不同，本表按正式版注明。

结论限于本次检查：没有发现还需凭空补造理论出处才能成立的编号公式；仍有上列明确的本文推导及数值设计。不是宣称每个公式都有逐字相同的参考原式，也不是给学习误差、收敛或相位性能提供了新增证明。

## 核验及来源范围

本轮重新核对 Cai 的分块模型、条件矩和外信息，Ma 的一般 LMMSE，Dytso 正式版，Huang 的 AFDM 模型，Bemani 学位论文连续波形/CPP，Karras 标量预条件，Menon 分类密度比，以及 Metzler 的 Monte Carlo 方法；Vila 的 §III-A 连同项目已有核验图核对。Wax、Nadakuditi、Vincent、Vehtari 等沿用已登记的出处，并核对本文相关代数；未声称本轮重读所有参考论文全文。

32 项小尺寸恒等式检查通过，最大残差 3.63×10⁻¹³，容差 10⁻¹⁰；覆盖重排、波形、长时延、Gaussian 消息、混合矩、导数、预条件、导频能量、方差目标和 variable projection。它们是确定性代数样例，不是接收机实验，也不能代替网络性能或收敛证据。

## 全部当前编号公式

| 当前号（原号） | 公式位置 | 来源性质 | 对应依据与边界 |
|---|---|---|---|
'''
rows=[]
for x in inventory:
    url=(ROOT/x['file']).as_posix()+':'+str(x['line'])
    rows.append(f"| {x['number']}（{x['old_number']}） | [{x['label']}]({url}) | {x['kind']} | {x['evidence']} |")
footer='''

## 证据入口

- [逐式清单及新旧编号](../checks/notation_formula_revision_20261104/EQUATION_INVENTORY.json)
- [32 项代数核验](../checks/notation_formula_revision_20261104/MATH_VALIDATION.json)
- [文件保护、编译与版面核验](../checks/notation_formula_revision_20261104/VALIDATION.json)
- [完整源码差异](../checks/notation_formula_revision_20261104/CHANGES.diff)
- [Bemani 学位论文原文](https://www.eurecom.eu/publication/7447/download/comsys-publi-7447.pdf)；核对了印刷 pp.26–27、29（PDF pp.52–53、55）。
- [Menon 原文](https://proceedings.mlr.press/v48/menon16.pdf)，§3、§4.2；[Metzler 作者稿 v5](https://arxiv.org/pdf/1406.4175)，§V-B、PDF p.15。

本轮没有训练、批量实验、接收机实现或实验数字变更。相位进度和已讨论 C/M 项继续以 REVIEW_DECISIONS.md 为准，不因本轮公式审查重新提问。
'''
(PAPER/'docs/FORMULA_PROVENANCE_20261104.md').write_text(intro+'\n'.join(rows)+footer,encoding='utf8')

before={k.replace('\\','/'):v for k,v in json.loads((RUN/'BEFORE.json').read_text(encoding='utf8')).items()}
changed=[];unchanged=[];diffs=[]
for rel,sha in before.items():
    p=PAPER/rel
    if hashlib.sha256(p.read_bytes()).hexdigest()==sha:unchanged.append(rel)
    else:
        changed.append(rel)
        if p.suffix=='.tex':
            diffs.extend(difflib.unified_diff((RUN/'before'/rel).read_text(encoding='utf8').splitlines(True),p.read_text(encoding='utf8').splitlines(True),fromfile='before/'+rel,tofile=rel))
(RUN/'CHANGES.diff').write_text(''.join(diffs),encoding='utf8')
protected=['sections/01_introduction.tex','sections/07_conclusion.tex','references.bib','main_full.tex']
protected += [x for x in before if x.startswith('figures/') and Path(x).suffix in ['.pdf','.svg','.png'] and not any(z in x for z in ['factor_graph.','learned_receiver.'])]
assert all(x in unchanged for x in protected),set(protected)-set(unchanged)
assert len(eqnums)==57
validation={'equation_count_before':61,'equation_count_after':57,'changed_files':changed,
            'unchanged_files':unchanged,'protected_files_pass':protected,
            'algebra':json.loads((RUN/'MATH_VALIDATION.json').read_text(encoding='utf8')),
            'receiver_experiments':0,'training_runs':0,'versions':{}}
from pypdf import PdfReader
for name in ['main','main_full']:
    log=(PAPER/(name+'.log')).read_text(encoding='utf8')
    v={'pages':len(PdfReader(PAPER/(name+'.pdf')).pages),
       'sha256':hashlib.sha256((PAPER/(name+'.pdf')).read_bytes()).hexdigest(),
       'undefined_references':bool(re.search('undefined|multiply defined',log)),
       'overfull_boxes':'Overfull' in log,'missing_characters':'Missing character:' in log,
       'underfull_hboxes':log.count('Underfull \\hbox'),'underfull_vboxes':log.count('Underfull \\vbox'),
       'references':len(re.findall(r'\\bibitem\{', (PAPER/(name+'.bbl')).read_text(encoding='utf8')))}
    assert not any(v[z] for z in ['undefined_references','overfull_boxes','missing_characters']),v
    validation['versions'][name]=v
(RUN/'VALIDATION.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'equations':len(inventory),'protected_files':len(protected),'versions':validation['versions']},indent=2))
