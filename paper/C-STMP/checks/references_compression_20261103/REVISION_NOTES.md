# 参考文献补充与 13 页压缩

日期：2026-11-03。作者授权在上一轮分析的范围内补充参考文献、规范著录，并继续精简第五、六章。

## 交付结果

- `main.pdf`：14 页降至 **13 页**，不含附录 C。
- `main_full.pdf`：**15 页**，保留附录 C；两版共享正文和 43 篇参考文献。
- 实际引用由 **35 篇增至 43 篇**，原有 35 篇全部保留。
- 第五章按空白分词减少 173 词，第六章减少 142 词，合计 315 词。该统计含 LaTeX 源码，供前后对照，不作为排版正文的精确英文词数。
- 使用原有 IEEEtran 10pt 双栏字体、页边距和图片尺寸；未通过缩小字体或负间距压页。

## 内容改动

1. 引言原文保持，只在四处已有论述后补引文；摘要、第二章、结论和附录 A/B/C 字节一致。
2. 第三章在 LMMSE 均值式前补 OAMP 的原式出处；第四章在 score 定义处补 score matching 原始文献。两章未删改论述。
3. 第五章合并算法引入及反馈流程描述，删除与 Algorithm 1 重复的 site 保留规则、方差范围外处理说明，压缩归一化和复杂度段落。方差更新保留固定当前近似后验的条件和闭式结果，删去中间的行内负对数似然展开式。
4. 第六章删除章首预告句，紧凑表达网络结构、基线配置和有限差分参数；仍保留各级通道、残差块数量、卷积核、步长、dilation、条件输入、分类器五个标量、预条件公式、训练设置及停止条件。结果分析及实验数字保持。
5. 已发表文献统一期刊/会议缩写；超过六位作者按首位作者加 et al. 输出。可由出版信息定位的论文及已明确 arXiv 编号的文献不重复打印长网址，原网址保存于 `source_url` 字段。两份标准和学位论文的在线链接保留。
6. 根据 DOI 注册元数据补齐 Cai、Shen、Li、Ying、Mei、Ke 的卷期页码；Huang 末页由 2952 更正为 2953；补录 Zhu、SOMP、Vila 的 DOI。Ding 暂按 early access 和 DOI 著录，不虚构卷期页码。

## 新增引用及依据

| 引用键 | 插入位置和支持范围 | 核对来源 |
|---|---|---|
| `kodheli2021` | I：卫星通信补充地面覆盖的背景；不将该综述当作本文 GNSS 独立算法的证明 | [IEEE 出版页及摘要](https://ieeexplore.ieee.org/document/9210567/)，DOI 10.1109/COMST.2020.3028247；卷 23(1)，70–109 |
| `mei2022` | I：海量 IoT 业务的稀疏活动；不将 JADD 误称为本文 JADCE | [作者原文 I、I-A](https://arxiv.org/html/2011.07928v3)，DOI 10.1109/TWC.2021.3107576；原库已有但未引用 |
| `ke2020` | I：利用活动和信道结构稀疏性的 CS 接入 | 本地 `reference/literature/ke2020_gmmv_amp.pdf`，摘要、II-B/II-C，PDF pp.1、3–4；[作者原文](https://arxiv.org/html/1906.09867v4)，DOI 10.1109/TSP.2020.2967175；原库已有但未引用 |
| `rangan2019` | I：大系统右正交不变测量矩阵下的 SE 背景 | 本地 `reference/literature/rangan2019_vamp.pdf`，摘要、I-D，PDF pp.1–2；[作者版本](https://arxiv.org/abs/1610.03082)，DOI 10.1109/TIT.2019.2916359。该原文的理论有 denoiser 条件，不据此声称本文有限维网络接收机满足其定理 |
| `ma2017` | III-A：LMMSE 线性估计式的原始方法依据 | 本地 `reference/literature/ma2017_oamp_v3.pdf`，III-B，PDF p.3，式(15c)；[作者机构正式版](https://scholars.cityu.edu.hk/files/26279282/Orthogonal_AMP.pdf)，DOI 10.1109/ACCESS.2017.2653119 |
| `hyvarinen2005` | IV-A：score 是对数密度关于样本的梯度 | [JMLR 原文页面与摘要](https://www.jmlr.org/papers/v6/hyvarinen05a.html)，6:695–709；只补基本 score 出处，有色加权 DSM 推导仍由本文及 Vincent 支持 |
| `wax1985` | V-B：为已有 Wax–Kailath MDL 名称补原始来源 | DOI 注册记录及 [作者 Stanford 目录](https://profiles.stanford.edu/thomas-kailath)，33(2):387–392。方法对应继续依据已经核对的 Nadakuditi–Edelman II-A、式(5)–(7)，不声称本轮重读了 Wax 全文 |
| `lin2017` | VI-A2：RefineNet 原始架构；保留 Song Appendix A 的改型出处 | [CVF 论文页面及摘要](https://openaccess.thecvf.com/content_cvpr_2017/html/Lin_RefineNet_Multi-Path_Refinement_CVPR_2017_paper.html)，DOI 10.1109/CVPR.2017.549。采用 IEEE DOI 记录页码 5168–5177；本稿层宽与条件输入仍以实现核验为准 |

出版元数据原始响应在 `metadata/`；初次并发查询的部分 429 响应记录于 `metadata_summary.json`，需要补齐的关键记录随后串行取得。未获取成功的其余既有条目未据此改写。新增引用的存在及用途已核对；本轮不是对全部参考文献的全文或撤稿状态审计。

## 验证与回退

- `VALIDATION.json`：两版页数、43 个唯一引文、原有引文保留、附录 C 分流、结论编入等全部通过。
- 62 个编号数学环境前后相同；所有章节 label 和插图引用保持。该环境数不是公式编号数。
- 最终 BibTeX 无错误；无未定义引用、未定义交叉引用或 overfull box。保留局部 underfull 和既有图 PDF 版本提示。
- 修改前文件和 PDF 在 `before/`，源文件逐行差异在 `CHANGES.diff`；页面预览在 `preview/`。
- 未启动训练或实验，未修改权重、结果数据或图文件。

本轮摘要未重新生成；没有改变摘要所述的模型、方法、结果或适用范围。
