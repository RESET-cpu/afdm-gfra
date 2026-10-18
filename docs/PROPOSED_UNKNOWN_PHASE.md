# Proposed：估计跨帧相位后进行信道与活动推断

本页保留 2026-10-15 的已知噪声版本及候选实验记录。2026-10-17 起默认配置为
[proposed_frontend.json](../configs/proposed_frontend.json)，相位采用原两轮完整搜索的优化实现，
并从观测估计噪声。当前版本及验收证据见[主线说明](PROPOSED_MAINLINE.md)。

本页历史版本的主要评价指标为完整信道 NMSE 和 AER。配置为 [proposed_unknown_phase.json](../configs/proposed_unknown_phase.json)，通过 `run.py run --method proposed --config configs/proposed_unknown_phase.json --noise-mode known` 调用。

## 输入与计算

公开输入文件严格包含 `observation`、原始 `pilot`、`noise_variance`、`activity_prior`。真实相位、Doppler、活动、信道与方向保存在独立真值文件中，由评分器读取。噪声方差为公开已知量。

1. 对每个候选用户拟合一个主导物理 AFDM 路径，解析消去复天线增益，完成两轮逐用户相位更新及联合增益最小二乘更新。
2. 从估计 Doppler 得到跨帧相位斜率，构造 `A_hat[q,k,n] = pilot[q,k,n] * exp(i*q*beta_hat[k])`。
3. 将原观测和 `A_hat` 送入 Proposed 的原条件接收机，进行完整信道与活动推断。

相位拟合参数与五基线评测一致：128 个相位格点、3 个相关峰候选、最多 12 个物理 Doppler 别名候选、两轮更新和每个候选最多 25 次局部细化。第二轮同时保留上一轮位置作为额外初值。

条件接收机使用绑定的 `configs/proposed.json`：原一阶、二阶 score 与活动分类器，新值权重 0.2、最多 600 轮、活动概率阈值 0.5。信道与活动更新见 [THEORY.md](THEORY.md)。相位在进入该条件接收机前估计；当前实现为两阶段计算。

相位前端通过独立公共输入重新计算。与五基线比较时，已保存的 baseline 相位只在 Proposed 推断完成后读取，用于核验相位与有效算子的一致性。

## 文件与输出

| 文件 | 职责 |
|---|---|
| [unknown_phase_model.py](../src/afdm_jadcedd/algorithm/unknown_phase_model.py) | 原始导频输入、相位算子与物理路径导数 |
| [phase_estimation.py](../src/afdm_jadcedd/algorithm/phase_estimation.py) | 观测驱动的共享相位估计 |
| [proposed/unknown_phase.py](../src/afdm_jadcedd/algorithm/proposed/unknown_phase.py) | 相位前端与 Proposed 的组合、计时和文件保存 |
| [evaluate.py](../docs/history/experiments/proposed_unknown_phase_20261015/evaluate.py) | 在五基线原始面板上评价 Proposed，逐条件核验相位一致性 |

输出保留 Proposed 的 `estimate`、`probabilities`、`activity_decision` 等字段，并增加 `phase_slopes`、`phase_doppler_hz`、`phase_folded_delay_samples`、`phase_path_gains`、`phase_fitted_observation`。配套 JSON 保存两阶段耗时、相位优化记录、完整 Proposed 迭代记录及输入、配置与源码身份。

计时包含完整相位前端与 Proposed 推断，分别列出两个阶段；模型加载与数据生成另计。完整信道 NMSE 包含非活跃用户误差，AER 由漏检加虚警除以全部候选用户数。各方法使用同一批物理场景、观测和相位前端；统计单位为物理场景。

## 依据与验证入口

相位前端由已执行五基线实验中的实现整理为公共模块，数学操作相同。变量投影与物理相位定义的原文定位见 [TERMINOLOGY.md](TERMINOLOGY.md)。原实验代码和结果保留作数值一致性参照。

输入隔离、物理原子一致性、相位计算一致性、有效算子传递和原生输出保留由 test_proposed_unknown_phase.py（历史文件已清理，原路径：`tests/test_proposed_unknown_phase.py`） 检查。真实网络入口检查见 [CHECK.json](../docs/history/results/proposed_unknown_phase_20261015/smoke/CHECK.json)。

十场景、六档 SNR 的 60 次推断已完成，全部达到原停止条件。60 组相位与有效算子与五 baseline 逐项一致；固定条件下完整入口复跑和直接调用原条件 Proposed 的输出均逐项精确一致。完整 NMSE、AER、计时及核验见 [REPORT.md](history/results/proposed_unknown_phase_20261015/evaluation/REPORT.md)和 [OUTPUT_AUDIT.json](../docs/history/results/proposed_unknown_phase_20261015/evaluation/OUTPUT_AUDIT.json)。

## Shen 2025 相位学习的适配核查（2026-10-15）

原始核查先完成原文、项目推导和合成数据上的公式核验。实现入口现为 `configs/proposed_iterative_phase.json`，经 `run.py run --method proposed --config configs/proposed_iterative_phase.json` 调用；同场景性能实验独立保存在 `docs/history/results/shen_phase_update_20261015/`，不覆盖原两阶段结果。

文献为 Shen 等 *LEO Satellite-Enabled Random Access With Large Differential Delay and Doppler Shift*，IEEE TWC 24(4), 2876–2893, 2025，DOI [10.1109/TWC.2025.3525738](https://ieeexplore.ieee.org/document/10839280/)。公式定位采用 [arXiv v1 作者稿](https://arxiv.org/html/2412.20806v1#S3.SS3)，§III-C，式(47)–(54)，PDF p.9；Algorithm 1，PDF p.10。

### 原文可借鉴的操作

原文以消息传递得到的后验均值与方差构造相位的期望二次目标，式(51)包含后验协方差对角项与均值外积。式(53)先求无约束线性方程解，再逐元素投影到单位圆；式(54)用估计路径能量选出的索引降低维数。Algorithm 1 在迭代中更新相位并重建测量矩阵。原文相位按用户、时延抽头和帧索引；当前项目采用每用户共同 Doppler，参数化不同。

式(53)是作者给出的近似投影规则。一般含非对角项的二次目标下，该投影不是单位模约束问题的精确最优解，也不保证比已有可行点更好。项目数值反例见下方核验。原文方差与 Gaussian 正则的对角项也不能直接解读为本项目相位更新必然改善的保证。

### 本项目推导：保留每用户跨帧相位斜率

定义有效信道 X_k=a_k H_k，使用当前软后验均值 m_k=E[X_k]。在现有近似下 m_k=p_k E[H_k|a_k=1]，不能再额外乘一次活动概率，也不先按 0.5 门限删掉弱用户。

将一帧所有天线和输出采样堆叠为 y_q，原始导频作用于 X_k 后的随机贡献记为 z_qk，组成 Z_q。其均值可直接由原始导频与完整信道均值计算：

\[
 \bar z_{qk}=\operatorname{vec}\!\left(\sum_n P_{qkn}m_k[:,:,n]\right),\quad
 \phi_q(\beta)_k=e^{jq\beta_k},\quad \phi_0=\mathbf 1.
\]

固定本轮近似后验，记 B_q=E[Z_q^H Z_q]、b_q=\bar Z_q^H y_q。忽略与相位无关的项及正的公共噪声尺度，期望负对数似然为

\[
 F_t(\beta)=\sum_q\left[
 \phi_q(\beta)^H B_q\phi_q(\beta)
 -2\operatorname{Re}\{b_q^H\phi_q(\beta)\}\right].
\]

这是借鉴式(47)的项目适配目标；没有把作者的独立逐帧投影公式称为本项目的闭式解。梯度为

\[
 \nabla_\beta F_t
 =2\sum_q q\operatorname{Im}\!\left[
 \phi_q^*\odot(B_q\phi_q-b_q)\right].
\]

当前采用用户间独立的后验近似时，B_q=\bar Z_q^H\bar Z_q+diag(d_q)，其中 d_qk=E||z_qk-\bar z_qk||²。由于每个用户相位为单位模，方差项贡献 sum(d_q) 与 beta 无关。即使每个用户内部有相关性，这个结论仍成立；如果保留用户间交叉协方差，通常不再成立。因此一阶/二阶信息应按实际近似传递，不能声称仅添加对角方差项就改变相位最优解。

在上述用户独立近似下，固定其余用户相位，令 r_q,-k=y_q-sum_{l!=k} exp(jq beta_l) bar z_ql，单用户更新等价于

\[
 \beta_k^{new}\in\arg\max_{\beta_k\in[-\pi,\pi)}
 \operatorname{Re}\sum_q e^{-jq\beta_k}\bar z_{qk}^{H}r_{q,-k}.
\]

可以周期网格搜索后局部细化，将旧值保留为候选并按同一目标接受更新。这样只保证冻结当前后验时目标不升，不能推广为学习近似后验下完整外迭代的似然单调性。

### 接入与验证范围

以已有物理相位前端作为初值，运行 Proposed 得到软活动及完整信道均值，在外迭代中更新 beta，再重建有效算子与线性模块。相位步使用完整信道均值，不要求在该步重新套用单主径近似。网络、活动门限和评价指标保持原定义；不以真实活动、真实相位或真实 Doppler 选候选。

这个方案仍使用当前独立边缘信道先验的工作模型；没有显式恢复帧内物理 Doppler 与 beta 的完整联合先验。自由完整信道与相位存在的代数替代关系见 [ALGEBRA_CHECK.json](../docs/history/results/phase_feasibility_20261015/ALGEBRA_CHECK.json)，因此观测拟合更好本身不足以证明完整信道 NMSE 更好。已在相同场景、相同网络与门限下比较固定初始相位和迭代相位，报告全部 NMSE/AER 和额外计算量，见后文。

数值核验：检查代码（历史文件已清理，原路径：`experiments/shen_phase_update_20261015/check.py`）、[结果](../docs/history/results/shen_phase_update_20261015/ALGEBRA_CHECK.json)。覆盖二次型与直接残差等价、解析梯度、独立用户方差项为常数、接受规则下的逐坐标目标变化，以及无约束解投影并非总能下降的反例。只使用固定种子的合成数组，不构成接收机性能实验。

### 接收机实现与记录

[`phase_refinement.py`](../src/afdm_jadcedd/algorithm/phase_refinement.py) 用 256 个周期相位点筛选每用户 4 个候选，再连续细化，执行两轮逐用户更新；旧相位始终作为候选，按直接观测残差接受下降更新。输入均值已包含软活动概率；全部候选用户均参与，不利用真实活动或估计活动门限筛选。

[`proposed_phase.py`](../src/afdm_jadcedd/algorithm/proposed_phase.py) 先执行原物理前端与 Proposed，再最多更新两次相位。每次应用新算子后，从原初始化重新运行条件 Proposed，以避免复用旧算子下的外信息；原三网络、0.2 阻尼、0.5 门限和每次条件推断的 600 轮上限保持不变。额外条件推断次数与全部网络调用数单独记录。相位步最大变化不超过 1e-4 rad 时保留原算子并停止；达到外迭代次数上限记为 `OUTER_UPDATE_BUDGET`，不标记为外迭代收敛。

最终 `phase_slopes` 与最终信道输出使用同一算子。物理前端的 Doppler、时延和增益只以 `initial_phase_*` 命名；更新斜率后没有把旧 Doppler 冒充最终物理 Doppler。`phase_slope_history` 保留全部实际使用的相位。该入口继续只接收 observation、pilot、noise_variance、activity_prior。

评测可复用已审计的原两阶段初始化结果，前提是公开输入、配置、权重和初始化实现身份一致，并通过新鲜复跑的逐元素一致性核查。正式 `infer/run` 入口始终重新估计初始相位。所有失败及浮点警告均保存；评分在输出保存后读取真值。

### 同场景验证结果

在原十个物理场景、六档 SNR 上完成 60 条新推断，参数在正式批次前冻结。这是已观察面板上的配对比较；两个开发场景共四个条件的结果与参数选择记录另行保留。

| SNR / dB | 原两阶段 NMSE / dB | 迭代相位 NMSE / dB | 原 AER / % | 迭代 AER / % |
|---:|---:|---:|---:|---:|
| −4 | −7.573 | −7.149 | 1.25 | 1.50 |
| −2 | −9.408 | −8.813 | 0.50 | 1.25 |
| 0 | −10.806 | −10.960 | 0.25 | 0.25 |
| 2 | −12.267 | −12.481 | 0.25 | 0.25 |
| 4 | −13.383 | −13.732 | 0.25 | 0.25 |
| 6 | −14.471 | −14.907 | 0.25 | 0.25 |

两列相位均由观测估计。完整信道 NMSE 按总误差能量与总真实能量之比汇总，AER 每档分母为 400 个用户判决。中高 SNR 的点估计有改善，低 SNR 出现退化；当前保留原两阶段配置作为比较入口。完整逐场景结果、场景重采样区间、调用量和核验见 [REPORT.md](../docs/history/results/shen_phase_update_20261015/evaluation/REPORT.md)。

停止条件另作了单案例诊断：scene007/−4 dB 的最后一次条件推断到第 600 轮仍未满足原概率残差门限。固定最终相位算子，若仅将活动权重残差门限从 1e-4 放宽到 1e-3，第 286 轮可停止，NMSE 为 −5.902 dB、1 次漏检；第 600 轮为 −4.866 dB、2 次漏检。第 544 轮发生新增漏检。这说明更严的停止规则未必改善 NMSE/AER，未达到数值门限也不等同于无有效输出。此为事后单条件诊断，尚未用新规则重跑全部外迭代；主表仍保持原停止规则。证据见 [停止诊断](../docs/history/results/shen_phase_update_20261015/stopping_diagnostic/RESULT.json)。

后续 [AER 专项诊断](history/results/shen_phase_update_20261015/activity_diagnosis/REPORT.md)确认，新增三次漏检和一次虚警均出现在第二次相位更新后的推断；一次更新的 AER 与原两阶段相同。三个新增错误在满足原停止条件的推断中出现，固定最终相位时放宽停止门限也未消除。单独给出真实相位的三项诊断仍保留对应漏检，未参与未知相位成绩。当前证据指向活动推断及相位更新后的判决退化，尚不能进一步单独归因于分类器、实际迭代输入或消息近似。

## 低 SNR 诊断与候选实验记录（2026-10-15）

当前选定流程为 [proposed_unknown_phase.json](../configs/proposed_unknown_phase.json)：
先从公开观测估计相位，再运行原推断过程和原活动分类器，所有 SNR 共用 0.5 概率门限。
以下候选及结果保留用于研究复核，当前比较和后续运行采用上述选定流程。

本轮保留原三网络、0.2 阻尼、至少 60 / 至多 600 轮和全部停止窗口。
原两阶段配置始终作为配对参照。所有可运行候选只接收四个公开输入；
诊断使用的真实信道、活动及相位另行存放，不进入未知相位接收机。

### 已验证的故障表现

8 个新开发场景、−4/−2 dB 中，原接收机分别有 5/2 次漏检、均无误报。
把全部用户真实相位直接给原接收机后，仍分别漏检 5/1 次。
这批数据不支持“主要是相位估计错了”的解释；真实相位控制也不属于未知相位成绩。
旧 scene008 则另有明显相位和 Doppler 别名错误，不能把两类情况混为一谈。

对 7 次新场景漏检的最后查询作线性分解，其他用户反馈误差沿目标信号方向的贡献
为 −0.195～−0.314，弱用户信号被部分抵消。完整查询的平均误差能量与所报方差之比
仍接近 1，故只看平均方差不能发现信号方向的偏差。原分类器确实被调用，且仍能抑制误报；
没有发现其被停用或权重更换的证据。详见
[查询诊断](../docs/history/results/proposed_low_snr_20261015/fresh_queries/)、
真实相位控制（历史文件已清理，原路径：`results/proposed_low_snr_20261015/oracle_phase/ROWS.json`）和
[反馈分解](../docs/history/results/proposed_low_snr_20261015/mechanism/DIAGNOSIS.json)。

### 实现

先由相同相位前端估计每用户折叠时延和物理 Doppler，构造实际 wrapped-chirp AFDM
原子及其两个一阶导数的三维局部子空间。每根天线的条件均值投影到该空间；
在标量 Gaussian 工作模型下，同时将条件协方差按 3/256 的维数因子缩放，
继续应用原方差正值下限。完整协方差的跨 AFDM 坐标相关性仍被压缩，
这个操作不等于已证明的实际后验校准，推导与范围见 [THEORY §13](THEORY.md)。

分类器继续接收未投影的同查询网络特征。修复改变后续反馈，从而改变下一轮分类器输入；
恢复弱用户的原因不是把活动门限直接降低。例如开发 scene005/−4 dB/user16 的
交叉用户反馈贡献由 −0.291 降到 −0.044，该用户恢复检出。
scene006/user20 的该项也减小，但仍漏检，说明这一机制改善并非每例都充分。

投影版在已观察场景新增了高概率、低估计能量的误报。因此增加了仅在推断结束后应用的
最终判决：原概率不低于 0.5，同时完整估计信道能量除以公开噪声方差不低于 30.6738313887353。
此门限在全部已观察的 18 个物理场景上标定，对各 SNR 共用；逐场景留一只检查门限稳定性。
门限选择没有使用正在运行的 20 个独立新场景结果。最终规则可能新增漏检，完整计入 AER。

该实验的复现配置为 [proposed_unknown_phase_projected_energy.json](../configs/proposed_unknown_phase_projected_energy.json)。
它在各 SNR 使用同一推断和最终判决，未满足全 SNR 验证要求。

`probabilities` 保留迭代内原分类器输出；最终 `activity_decision` 使用上述两个条件。
`activity_score` 不是概率，其判决门限为 1。完整 `estimate` 不按活动判决清零，
NMSE 包含不活动用户的全部估计误差；最终能量判决不改变信道 NMSE，也不增加网络调用。

### 验证范围与保留对照

该候选与相关原流程的 74 项测试通过。正式入口重新估计相位后，信道、概率、协方差和判决
与保存的开发实现逐位一致；派生能量统计量相对误差为 5.15e−16。
检查记录见 [CHECKS.json](history/results/proposed_low_snr_20261015/CHECKS.json)和
[正式入口复跑](../docs/history/results/proposed_low_snr_20261015/energy_production_smoke/VALIDATION.json)。

只投影均值、保留旧方差的尝试出现大量误报，已明确停止并保留完成与未完成数量。
四个整体相位旋转分别推断再平均的候选改善 NMSE，但在 8 个开发场景上没有减少 AER；
其独立验证与原实现均单独保留。逐用户方差、迭代内旋转平均及风险修正对照也保留失败记录。
这些结果不能与新场景确认混合选择或省略不利案例。

### 冻结候选的独立确认

20 个新物理场景、每场景 −4/−2 dB，使用同一观测和估计相位，
每档 800 个用户判决。完整输出、原始评分和相位均已逐条件复核，全部有限。

| SNR / dB | 原 Proposed NMSE / dB | 投影及能量判决 NMSE / dB | Off-grid SBL NMSE / dB | 原 AER / % | 投影及能量判决 AER / % | SBL AER / % |
|---:|---:|---:|---:|---:|---:|---:|
| −4 | −7.641 | −12.973 | −5.756 | 1.000 | 0.250 | 0.375 |
| −2 | −9.597 | −13.841 | −7.222 | 0.250 | 0.125 | 0.250 |

−4 dB 的漏检/误报从 7/1 变为 2/0，−2 dB 从 2/0 变为 1/0，
低 SNR 总错误 10→3。相较原 Proposed，没有新增错误用户；仍有 3 次漏检，
其中同一物理用户可能跨 SNR 重复出现。低 SNR 的 40 次修复推断均满足原停止条件，
一阶网络调用从 3840 降至 3074，减少 19.95%；相位前端仍计入完整成本。

分别按物理场景配对重采样，NMSE 改变量的 95% 区间为
−4 dB 的 [−6.128,−4.726] dB、−2 dB 的 [−5.545,−3.145] dB。
合并两档、仍按物理场景重采样，AER 改变量区间为 [−0.875,−0.125] 个百分点。
相对 SBL，每档少 1 次错误；20 个场景不足以据此宣称普遍严格优于 SBL。
完整统计与所有逐场景差值见 [PROJECTED_REPORT.json](../docs/history/results/proposed_low_snr_20261015/PROJECTED_REPORT.json)，
图见 [independent_comparison.png](../docs/history/results/proposed_low_snr_20261015/independent_comparison.png)。

不加最终能量判决的投影版在 −4/−2 dB 分别为 0 漏检+6误报、1漏检+15误报，
未通过冻结的联合标准。最终能量规则在该面板增加 2 次相对于投影版的漏检并消除 21 次误报，
未改信道输出。这些中间结果保留，不能把“投影本身”与最终完整方法的 AER 混称。

### 中高 SNR 验证

前 5 个确认场景还在 0/+6 dB 使用同一候选，每档 200 次用户判决：

| SNR / dB | 原 NMSE / dB | 候选 NMSE / dB | 原漏检/虚警 | 候选漏检/虚警 | 候选 AER / % |
|---:|---:|---:|---:|---:|---:|
| 0 | −10.750 | −12.007 | 0/0 | 1/0 | 0.5 |
| 6 | −14.764 | −13.806 | 0/0 | 0/6 | 3.0 |

未使用最终能量门限时，0/+6 dB 分别有 26/48 次虚警。门限不改变信道输出，
因此 +6 dB 的 NMSE 退化来自推断过程。另有 1 条有限输出达到 600 轮上限。
当前结果说明这套条件均值、方差及活动证据的组合在中高 SNR 仍有问题，
尚不能确定单独归因于哪一项。当前选择保留原推断及原分类器；本轮候选实验结束。
将来若有新候选，应在全部 SNR 使用同一推断公式、参数和判决，
并在新的独立场景上联合检验 NMSE 与 AER；上述场景此后属于已观察数据。
