# 当前 59 个编号公式的出处与四类对应关系

日期：2026-11-06。对象：当前白噪声版本 `main.tex` / `main_full.tex` 共用正文，式 (1)–(59)。按编号计数；同一式的换行及配套行内定义不另计。历史有色噪声版本、已移出的附录和旧编号不纳入统计。

## 结论与统计口径

**不是每个公式都能在已有论文中找到原样的一式。** 59 式都能交代数学依据：50 式有可直接对应或直接适配的文献原型，另 9 式是已有关系的组合或当前系统模型的定义、推导。

| 类别 | 含义 | 数量 | 占 59 式比例 | 数学形式的接近程度 |
|---|---|---:|---:|---|
| A 原式等价 | 换符号、按矩阵排列或作等价代数整理后，公式运算关系相同 | 22 | 37.29% | 相同的基本运算关系 |
| B 直接适配 | 有明确原型，但需改变实复约定、归一化、平均方式、应用对象或参数设置 | 28 | 47.46% | 主体结构一致，适配项可明确指出 |
| C 关系组合 | 当前表达式由已有模型或恒等式组合、代入、求矩得到，不能归给一条原式 | 5 | 8.47% | 组成关系有出处，最终组合为本稿写法 |
| D 本文模型定义或推导 | 由本稿的波形延拓、帧结构及参数化直接定义或推出 | 4 | 6.78% | 未找到完整的一对一原式 |

**可直接对应或适配的公式占比为 50/59 = 84.75%（约 84.7%）。** 这是本次人工逐式分类的覆盖比例，不是字符相似度、查重率或创新程度评分。没有使用查重系统，也没有为单条公式编造“相似度 90%”一类数字。

A 类判定针对所列数学关系。例如 `Y=AX+W` 的形式相同，不表示 AFDM 与原文 OFDM 的物理算子相同；改变平均轴、实复方差单位或估计对象则单列 B 类。分类边界采用本报告的口径，逐式理由如下。

## 来源索引

下表页码指所链接版本的 PDF 页；正式出版页码另行标出。作者稿用于核对已经发表论文的公式，不涉及为正文新增预印本文献。

| 代号 | 原文与本次使用位置 |
|---|---|
| Cai | [JSAC 正式版](../../../reference/literature/cai2026.pdf)：§II 式 (4)–(5)，PDF p.4；§III-A 式 (7)–(11)，pp.5–6；§III-B 式 (18)–(42)，pp.6–7；§IV 式 (43)–(49)，pp.8–9；§V 式 (57)–(58)、(66)，pp.9–10。 |
| Shen | [项目中的作者稿](../../../reference/literature/shen2025.pdf)：§II-A 式 (1)，PDF p.3；§II-B 式 (8)–(9)，p.4。 |
| Huang | [WCL 正式版](../../../reference/literature/huang2026.pdf)：§II 式 (1)–(5) 及式 (2) 后的共同 Doppler 假设，PDF p.2／印刷 p.2950。 |
| Bemani | [AFDM 作者稿](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/full_terminology_audit_20261030/downloaded_sources/bemani2022.pdf)：§II-B 式 (16)，PDF p.7；§III-A 式 (18)–(19)，p.8。 |
| Bemani thesis | [学位论文](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/notation_formula_revision_20261104/sources/bemani2023thesis.pdf)：§3.1.1 式 (3.7)、(3.9)，PDF pp.52–53／印刷 pp.26–27；§3.2 式 (3.13)–(3.15)，PDF p.55／印刷 p.29。 |
| Ma | [OAMP 作者稿](../../../reference/literature/ma2017_oamp_v3.pdf)：§III-A 式 (12)、(15c)，PDF p.3。注意一般 LMMSE 在 §III-A，历史记录中的 §III-C 不准确。 |
| Rangan | [VAMP 作者稿](../../../reference/literature/rangan2019_vamp.pdf)：Algorithm 2 第 9–11 行，PDF p.4；§III-B 式 (24)–(25) 与 Algorithm 3，p.5；§III-C 式 (26)–(27)，p.6。 |
| Dytso | [TIT 正式版](../../../reference/literature/dytso2023_conditional_mean_published.pdf)：式 (3)，PDF p.1／印刷 p.1883；Jacobian 定义式 (9)，p.2／1884；§III Proposition 1 式 (17)，p.3／1885。 |
| Manor | [ICLR 2024 原文](../../../reference/literature/manor_michaeli_2024_posterior.pdf)：§3.2 式 (11)、§4.1，支持利用去噪器导数计算条件矩。 |
| Metzler | [D-AMP 作者稿](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/formula_prototypes_20261104/metzler2016_damp.pdf)：§V-B，PDF p.15，未编号的 Monte Carlo 散度公式。原文为 Gaussian 方向和单边差分。 |
| Avron–Toledo | 随机符号迹估计沿用[已有核验记录](DAMPING_AND_FORMULA_PROTOTYPES_20261104.md)：§2 Lemma 2.1、§3 Definition 3.3。本轮作者网站访问超时，未将其记为本轮重新读取成功；式 (34) 的迹关系也在下文直接说明。 |
| Menon–Ong | [ICML 2016 原文](https://proceedings.mlr.press/v48/menon16.pdf)：§2.2 logistic loss，PDF p.2；§3 式 (6)–(8)，p.2；§4.2 式 (16)–(17) 及紧随其后的 balanced logistic 例，p.3。 |
| Nadakuditi–Edelman | [TSP 正式版](../../../archive/figure_cleanup_20261104/retired_files/paper/C-STMP/checks/full_terminology_audit_20261030/downloaded_sources/nadakuditi2008.pdf)：§II-A 式 (5)、(7)，PDF p.2／印刷 p.2626；§IV 式 (22)，p.6／2630。式 (22) 是尾部特征值均值的直接出处；MDL 原始来源仍为稿件已引 Wax–Kailath (1985)。 |
| Tipping–Faul | [AISTATS 2003／PMLR 重印 PDF](https://proceedings.mlr.press/r4/tipping03a/tipping03a.pdf)：§2.1 式 (7)–(8)，该版本 PDF p.2。[本轮副本](../checks/formula_provenance_20261106/tipping2003_pmlr.pdf)已按原页核对；历史记录的 p.3 对应另一排版的作者稿。 |
| Vila–Schniter | [已发表论文的作者稿](https://arxiv.org/pdf/1207.3107)：§III-A 式 (22)–(27)，其中残差平方加后验方差为式 (27)，PDF p.4。本地旧 PDF 解析有修复警告，本轮改用[重新获取的作者稿](../checks/formula_provenance_20261106/vila2013_arxiv.pdf)核对。 |
| Karras | [NeurIPS 2022 原文](../../../reference/literature/karras2022_edm.pdf)：Table 1，PDF p.3；§5 式 (7)–(8)，p.8。 |

## 逐式清单

| 本文式号 | 内容 | 类别 | 文献定位及与本稿的具体关系 |
|---:|---|:---:|---|
| 1 | 时变多径信道 | B | Shen (1) 的时延–Doppler–阵列模型，结合 Huang §II 共同 Doppler 假设；本稿写成时域冲激响应并采用公共时延补偿。 |
| 2 | UPA 阵列响应 | B | Shen (1) 中两轴指数因子；本稿用一般阵元间距和波长表达，而原式写半波长间距。 |
| 3 | IDAFT 发射信号 | A | Bemani (18) 及其基函数定义；设备、帧下标仅标记不同发送块。 |
| 4 | DAFT 矩阵 | A | Bemani (16) 的 Λc2 F Λc1 逐元素展开。 |
| 5 | 连续 AFDM 基函数及延拓 | D | 基础为 Bemani thesis (3.7)、(3.9)、(3.14)；当前无量纲时间、取模及多周期 CPP 组合是本稿定义，未找到完整同式。 |
| 6 | 各天线有效信道 | C | Huang (4) 的路径叠加，加本稿 (1)、(2)、(5)、(7) 的阵列响应与连续波形算子。 |
| 7 | 路径算子 F_A D B | C | 将 Bemani 的 DAFT、thesis (3.13)–(3.15) 的延时波形采样和 Doppler 乘法组合；当前时间原点、完整分数时延和 CPP 已纳入 B、D 的定义。 |
| 8 | 跨帧公共相位 | D | 从 (7) 的 g_q=g_0+q(N+N_CPP) 直接提出共同指数因子。Shen (8)–(9) 提供多帧相位背景，不是当前 AFDM 原式。 |
| 9 | 含相位的有效导频 | D | 将 (8) 的 e^{jqβ_k} 吸收到每行导频中的定义。 |
| 10 | 块观测 Y=ΣA_kX_k+W | A | Cai (4)，相同的块矩阵叠加形式；A、X 的 AFDM 物理含义由本稿前文定义。 |
| 11 | 后验因子分解 | A | Cai (5)，观测似然、活动–信道约束、信道先验、活动先验的同一分解关系。 |
| 12 | 一般矩阵 LMMSE 均值 | B | Ma (12)、(15c)，Rangan (24)；复数矩阵和多列观测适配。Cai (7) 是行正交条件下的简式，不能直接替换本式。 |
| 13 | LMMSE 协方差 | B | Rangan (24)–(25) 的逆精度矩阵、Tipping–Faul (6) 的 Gaussian 协方差；使用复数 Hermitian 转置及本文精度单位。 |
| 14 | 线性外信息方差 | A | Cai (10)，Gaussian 精度相减。 |
| 15 | 线性外信息均值 | A | Cai (11)，Gaussian 自然参数相减后乘外信息方差。 |
| 16 | 含活动变量的局部观测 | B | Cai (20)、(43) 为活动条件下 H+W；本稿在统一观测中显式保留 α。 |
| 17 | 活动条件下的信道均值 | A | Cai (22) 的条件期望目标；本稿近似号表示实际算法近似该目标。 |
| 18 | 每设备平均条件方差 | B | Cai (23) 的条件方差平均；本稿先在每设备 D 个复坐标取平均，平均轴不同。 |
| 19 | 活动假设的边缘密度 | B | Cai §IV-B、式 (46) 前的加噪密度积分；把一般先验积分写成训练分布下 Gaussian 似然的期望。 |
| 20 | 不活动假设的 Gaussian 密度 | A | Cai (30) 中不活动分支的零均值 Gaussian 似然；将独立坐标合写为向量密度。 |
| 21 | Bayes 活动概率 | A | Menon–Ong (6)–(8) 的 posterior odds 关系，经等价整理得到分式。 |
| 22 | 活动概率加权信道均值 | A | Cai (35)，混合均值 p×活动分量均值。 |
| 23 | 空间平均混合协方差 | C | Cai (32)、(35)–(36) 的混合分布，加全协方差公式与天线子块平均；Cai 未给出本稿 U_k U_k^H/N² 的矩阵形式。 |
| 24 | 全局平均后验方差 | B | Cai (36)、(38) 的混合方差及平均；本稿扩到 D=MN²，并对设备和天线汇总。 |
| 25 | 非线性外信息方差 | A | Cai (41)，以 b=t̄_X/v 作等价代数改写。 |
| 26 | 非线性外信息均值 | A | Cai (42)，与 (25) 使用同一 b 简记。 |
| 27 | 实数表示下的训练加噪 | B | Cai (43) 的 proper complex AWGN 转成实虚堆叠；每实坐标方差 v/2。 |
| 28 | Tweedie 条件均值 | B | Dytso (3) 的各向同性实噪声特例；与 Cai (44) 同类，按本稿实数表示取噪声协方差 (v/2)I。 |
| 29 | Tweedie 条件协方差 | B | Cai (45)，并与 Dytso (3)、(17) 对应；实数 Hessian、v/2 和 v²/4 依本稿约定。 |
| 30 | DSM 损失 | B | Cai (47)–(49) 的 Gaussian DSM 及噪声尺度加权；本稿使用实数 score、v/(4D) 归一化。 |
| 31 | 直接均值网络训练损失 | C | 将 Tweedie 所对应的 score 参数化 s=2(f−u)/v 代入 (30)，得到 1/(Dv) 加权 MSE。是已有关系的重参数化组合。 |
| 32 | 条件协方差与均值 Jacobian | B | Dytso Proposition 1 (17)；改用本稿 Jacobian 约定及 (v/2)I 噪声协方差。 |
| 33 | Jacobian 散度给出平均方差 | B | 对 Dytso (17)／本稿 (32) 取迹，再按每复坐标除以 D。 |
| 34 | 随机中央差分方差估计 | C | Dytso 的导数–协方差关系、Metzler §V-B 的差分散度估计、随机符号迹估计相结合；中央差分、方向尺度和复坐标归一化为本稿实现。 |
| 35 | 活动后验 log odds | A | Menon–Ong (6) 两边取对数。 |
| 36 | 二分类交叉熵 | A | Menon–Ong §2.2 logistic loss；用 y=2a−1 将 ±1 标签改写为 0/1 标签，逐样本损失等价。网络输入特征在公式外另定义。 |
| 37 | 理想 logit 等于 log 密度比 | A | Menon–Ong (16)–(17) 及 balanced logistic 例，训练先验 1/2 时得到 z*=log(q1/q0)。 |
| 38 | 学习密度比与活动先验结合 | B | Menon–Ong (6)、(17)，在本稿活动检测中代入学习 logit；接收端先验为 ρ。 |
| 39 | Gaussian site 方差 | A | Cai (26)，Gaussian 相除的精度公式。 |
| 40 | Gaussian site 均值 | A | Cai (27)，Gaussian 相除的自然参数公式。 |
| 41 | site 与似然相乘后的方差 | A | Cai (33) 的精度相加，展开分母后相同。 |
| 42 | site 与似然相乘后的均值 | A | Cai (34)，展开分母后相同。 |
| 43 | 空间样本协方差 | A | Nadakuditi–Edelman (5)，用帧–采样双下标表示样本集合。 |
| 44 | 尾部特征值平均估计噪声 | A | Nadakuditi–Edelman (22)；MDL 选秩参见该文 (7) 及 Wax–Kailath。 |
| 45 | 多帧相位搜索原子 | D | 本稿 (7)–(9) 作用于已知导频，去掉能被未知增益吸收的标量相位后定义；不是 Tipping 的原文物理字典。 |
| 46 | 相位前端的边缘协方差 | B | Tipping–Faul (8) 的 σ²I+ΦA^{-1}Φ^T；本稿改为复数物理原子和每用户增益方差 γ_k。 |
| 47 | 相位前端的边缘似然目标 | B | Tipping–Faul (7)；改为复 Gaussian、多观测列，取负号、去常数并除以天线数 M。 |
| 48 | 局部输入方差目标 | B | Vila–Schniter (27) 的“残差平方＋后验方差”；原文更新观测噪声，本稿用于局部伪观测方差。 |
| 49 | 输入均值递归阻尼 | B | Rangan (26) 的旧状态与新估计凸组合；本稿作用于传递的输入消息。 |
| 50 | 输入方差递归阻尼 | B | Rangan §III-C 的参数阻尼、Cai (58) 的方差加权；本稿递归平滑方差。Rangan (27) 平滑精度，数值操作不同。 |
| 51 | 输出均值递归阻尼 | B | Rangan (26) 的同类递归更新；作用对象为外信息反馈。 |
| 52 | 输出方差递归阻尼 | B | 与 (50) 同类；作用对象为反馈方差，沿用本稿已阻尼历史状态。 |
| 53 | 奇异值增益平均 f_L | B | Rangan Algorithm 2 第 9–10 行：取原文噪声精度 1/σ²、输入精度 1/γ，f_L=Σd_a/(KN)。 |
| 54 | SVD 后验方差 | B | Rangan (25)、Algorithm 3 第 12–13 行；本稿 α_2=1−f_L，从精度换为方差即得 γ(1−f_L)。 |
| 55 | SVD 外信息方差 | B | Rangan Algorithm 2 第 10 行／Algorithm 3 第 14 行，转换为方差后得 γ(1−f_L)/f_L。 |
| 56 | 部分 DFT 导频 | B | Cai (66) 及 §II-A 部分正交导频；本稿使用 KN 点 DFT，另加行选择、列置换和单位模列相位。 |
| 57 | 去噪器标量预条件 | B | Karras Table 1、§5 (7)；代入实噪声方差 σ²=v/2 得三个系数。网络及噪声嵌入、训练权重按本稿配置，不是 EDM 全套训练方案。 |
| 58 | Gaussian 活动 log 似然比 | B | Cai (30) 两个假设下的 Gaussian 密度比；在本稿共享标量方差条件下取对数，展开为能量和 D·log 项。 |
| 59 | Gaussian 后备活动概率 | A | Cai (30) 的 Bayes 概率，经 log odds／sigmoid 表达得到；具体近似密度由 (58) 定义。 |

各类式号：

- A：3、4、10、11、14、15、17、20、21、22、25、26、35、36、37、39、40、41、42、43、44、59。
- B：1、2、12、13、16、18、19、24、27、28、29、30、32、33、38、46、47、48、49、50、51、52、53、54、55、56、57、58。
- C：6、7、23、31、34。
- D：5、8、9、45。

## 组合与本文推导的依据

式 (23) 使用全协方差关系：若活动分量的均值、协方差为 μ、tI，零分量概率为 1−p，则 Cov(X)=ptI+p(1−p)μμ^H。将同一坐标的天线子块取出并对 N² 个位置平均，即得到 U U^H/N² 项。

式 (31) 是 (30) 中 `s=2(f−u)/v` 的直接代入：平方项带来 4/v²，与 v/(4D) 相乘后为 1/(Dv)。它不依赖新的 score matching 定理。

式 (34) 由 E[zz^T]=I、w=√(v/2)z 得 E[w^T J_f w]=(v/2)tr(J_f)，再以中心差分近似 J_f w，并除以 D。有限网络、有限步长与有限方向数带来估计误差；这是数值近似，不是 Cai 的二阶 score 网络原式。

式 (5) 在一周期内对应 Bemani 连续波形，前缀区间使用本稿 chirp-periodic 延拓；式 (6)–(7) 据此采样、乘 Doppler 再做 DAFT。内部详细推导保存在 [AFDM 信道推导](derivations/afdm_channel_model.tex)。式 (8) 是不同帧时间原点之间的公共指数因子，式 (9) 是吸收该因子的导频定义。

式 (45) 是本稿相位前端的物理原子；其后的 (46)–(47) 则是标准稀疏 Bayesian 边缘似然的适配。两者不应一起标成“完全原创”，也不应一起标成“Tipping 原式”。详细模型和消元过程见[相位估计推导](derivations/phase_estimation.md)。

**C、D 两类并不自动代表新的理论贡献。** 当前差别主要体现为 AFDM 多帧模型、均值导数方差估计、密度比活动检测与消息传递的具体结合。公式来源审查回答数学来路；创新性需要比较完整方法和实验结果，不能按不同公式的数量判断。

## 本轮核验记录

本轮读取全部现行编号公式及其配套定义，复核上述主要来源原文的有关章节与公式，并查看关键原页。沿用 11 月 4 日已完成的代数核验，不重复运行实验或训练。此前的有色噪声、矩阵预条件与旧相位最小二乘报告保留为历史记录，不直接套用其分类。

更新后的来源定位包括：Ma 一般 LMMSE 位于 §III-A；Nadakuditi 噪声均值可直接定位到式 (22)；本轮 PMLR 版 Tipping 式 (7)–(8) 位于 PDF p.2。VAMP 的 SVD 对应关系明确到 Algorithm 2/3，故 (53)–(55) 归入 B 类。

来源文本、页图、PDF 结构检查及文件哈希保存在[核查目录](../checks/formula_provenance_20261106/)。本轮未修改论文正文、PDF、参考文献、实验数字或实现。
