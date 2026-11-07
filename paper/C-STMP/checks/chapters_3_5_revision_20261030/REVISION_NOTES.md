# C-STMP 第三至第五章修订记录

日期：2026-10-30。范围：按作者确认的章节结构进行组织、论证衔接和语言修订。正式稿已整合，`paper/C-STMP/main.pdf` 已重新编译为 15 页。

## 最终结构与主要改动

| 章节 | 小节 |
|---|---|
| III. Bayesian Receiver Design | A. Receiver Structure；B. Multi-Frame Linear Estimation；C. Generative-Prior-Aided Joint Denoising |
| IV. Learning Channel and Activity Denoisers with Score-Based Generative Priors | A. Channel Denoising with Colored Gaussian Noise；B. Variance from Conditional-Mean Derivatives；C. Density Ratio Estimation；D. Offline Training |
| V. Overall Algorithm | A. Overall Algorithm；B. Computational Complexity Analysis |

第三章以工作后验与两模块的信息交换开篇，首次定义作者批准的 MFLE、GPJD，并增加原生矢量框图。MFLE 按后验矩、标量近似、外信息和 SVD 顺序展开；GPJD 先给局部模型的精确矩，再说明网络近似、Gaussian site、活动加权矩、反馈及方差更新。原方差与外信息小节已合入 GPJD，原前端说明移入 V-A。

第四章贯通条件均值、导数方差和活动密度比。补明协方差加权 score matching 的代数关系、实数 Jacobian 的方向及复数坐标归一化、分类训练标签与类先验修正；将精确总体恒等式与训练网络的近似输出区分开。离线训练保留两网络顺序及实际输入特征。

第五章将前端、初始化、阻尼、site 接受/保持、区间外回退与停止检查纳入整体算法。工程细节没有独立小节；伪代码显式标出 MFLE/GPJD、首轮输入及下一轮使用的方差比例。复杂度分别说明矩阵计算、网络调用及存储。

本轮未改动摘要、引言、第二章、仿真章、附录、参考文献数据库及既有实验图。没有训练、接收机推断、实验重跑、参数调整或权重变更。

## 实际作者与审查链

| 章节总代理 | 小节独立作者 | 章审及返修 |
|---|---|---|
| `/root/chapter3_lead` | `iii_a_writer`、`iii_b_writer`、`iii_c_writer` | 三稿均经总代理审读，并交回各原作者澄清网络近似、相位因子所在的 Gram 内积、当前输入方差、活动矩引用及分类器评估条件。返修稿已复审。 |
| `/root/chapter4_lead` | `section4a_writer`、`section4b_writer`、`section4c_writer`、`section4d_writer` | A/B/D首审通过；C因重复引用和重复前提交回原作者精简后复审通过。 |
| `/root/chapter5_lead` | `v_a_writer`、`v_b_writer` | A返修澄清下界后的正方差及首轮赋值；B返修明确矩阵乘积计数约定。两稿均由原作者修改并复审通过。 |

共 9 位小节作者、3 位章节总代理。根代理在整合前阅读最终章稿与来源记录，检查跨章接口，负责框图、术语附记及全文编译/视觉核验。初稿、返修稿与实际审查问题均留存，没有用单一代理代写全部小节。

详见 [III 审查](ch3/REVIEW.md)、[IV 审查](ch4/REVIEW.md)、[V 审查](ch5/REVIEW.md)；对应 [III 来源](ch3/SOURCES.md)、[IV 来源](ch4/SOURCES.md)、[V 来源](ch5/SOURCES.md)。技术词语、页码与适配范围已追加至 `docs/TERMINOLOGY.md`，其既有内容逐字保留。

## 核验结果

- III/IV/V 分别保留 18/8/6 个编号公式标签，共 32 个。按标签逐一比较公式内容，忽略空白后全部一致。新增行内说明明确已有行为，没有新增编号推导或改动算法定义。
- 有效全文无缺失交叉引用、重复标签或缺失文献键。旧前端标签指向 V-A，方差更新标签指向 III-C；正文中的节号由 LaTeX 自动更新。
- 16 个受保护的稿件/文献/图文件与运行前哈希一致。第五章审查还核对了相关实现与 VI 的哈希。
- Tectonic 编译成功，PDF 为 15 页。无 overfull、缺字、未定义引用或重复标签警告。日志保留 4 处 underfull 提示：引言、III/V各一段及参考文献 URL；不把编译称为“零警告”。
- 已渲染全部 15 页并检查总览，逐页查看受影响的第4–8页：两模块框图、公式及编号、算法块均在栏内，未见重叠、裁切或异常空白。算法块完整位于第8页；原实验图的内容文件未改。
- 未运行算法测试或性能测量；本次验证针对稿件结构、公式保留、出处、实现描述及排版，不是对研究结论的重新实证验证。

检查数据见 [structural_verification.json](structural_verification.json)、[verification.json](verification.json)、[编译日志](compile.log) 和 [根审记录](ROOT_VERIFICATION_NOTES.md)。图像预览位于仓库 `tmp/pdfs/chapters_3_5_revision_20261030/`，未另外生成带日期的完整论文 PDF。

## 复杂度口径及实现差异

V-B 作者发现现有 `STMP/gaussian.py:30` 的三输入 `einsum` 使用 `optimize=False`。根代理仅分析收缩计划，确认其缩放阶数为 4，而两两矩阵相乘的阶数为 3；没有运行接收机或测量耗时。因此，当前实现该处仍有额外 O(M^4) 成本。

按本轮稿件修订范围，正文保留既有复杂度公式，并明确按标准稠密矩阵乘法/分解、三矩阵乘积两两求值计数。这是算法的代数计算口径，不能称为现有每条 NumPy 指令的严格成本。实现未被优化，没有宣称测得加速。此记录修正前期仅检查 M-by-M 分解而未覆盖该收缩路径的概括。

## 缩写检查与覆盖边界

对 I–VI 的临时纯文本视图运行了缩写检查。抽取排除了公式、图表、摘要和附录，且检查器未能识别若干带连字符的全称，因此属于部分覆盖。MFLE、GPJD在III-A均已先给全称再给缩写，SVD在III-B首次展开；其他未自动确认项已对照原稿查看。V中未展开的孤立MP用法已移除。

最终自动提示中的NTN、TDL、ASPL、GAMP、GNN、SBL、MSE来自未修改的VI。GAMP-SBL已有组合全称，自动拆词造成部分提示；其余留作VI的后续编辑提醒，本轮未扩张到仿真章。不将自动报告解释为全稿缩写全部通过。

最终原始报告如下（无需回复）：

```text
### Acronym check (advisory; no reply needed)
Coverage: body (partial)
Not checked:
- Body, line 3: GFRA (the initials before its parentheses do not spell it)
- Body, line 3: IoT (the initials before its parentheses do not spell it)
- Body, line 13: MMSE (the initials before its parentheses do not spell it)
- Body, line 37: CPP (the initials before its parentheses do not spell it)
- Body, line 59: GPJD (the initials before its parentheses do not spell it)
- Body, line 59: MFLE (the initials before its parentheses do not spell it)
- Body, line 131: SNR (the initials before its parentheses do not spell it)
- Body, line 143: NMSE (the initials before its parentheses do not spell it)

| Scope | Line | Rule | Acronym | Uses |
|---|---|---|---|---|
| Body | 127 | Not defined | NTN | 1 |
| Body | 127 | Not defined | TDL | 1 |
| Body | 137 | Not defined | ASPL | 3 |
| Body | 137 | Not defined | GAMP | 4 |
| Body | 137 | Not defined | GNN | 4 |
| Body | 137 | Not defined | SBL | 10 |
| Body | 147 | Not defined | MSE | 1 |
```

本次是限定范围的作者修改与章节审查，未声称已完成全论文投稿认证、所有参考文献的重新全文核验或达到某一分区期刊的录用标准。
