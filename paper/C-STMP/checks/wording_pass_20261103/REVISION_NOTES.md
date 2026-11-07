# 进一步逐词检查与操作对象修订

2026-11-03。重读 main 实际使用的摘要、I–VII、A/B，以及 main_full 的附录 C；按 198 个源码单元保存审阅底稿。标题、公式与排版单元也在清单中，198 不等于自然段数。

已作 134 项措辞修改，涉及 87 个单元、11 个源码文件。这个计数包含语法、并列关系和术语一致性调整，不表示发现了 134 个自造术语。改前、改后与逐项理由见 [EDITS.json](EDITS.json)；全单元底稿及改后文本分别为 [UNITS.json](UNITS.json)、[AFTER_UNITS.json](AFTER_UNITS.json)。

主要处理如下。

| 原表达 | 处理及原因 |
|---|---|
| mean function；complex mean map | denoiser；complex-valued denoiser，直接说明该函数实际用途 |
| proper complex Gaussian covariance | proper complex Gaussian noise with covariance，Gaussian/proper 修饰随机噪声而非矩阵 |
| noise estimate；internal noise update | 明确为 noise-variance estimate/update，实际对象是方差 |
| received-symbol delay position | 展开为接收符号沿 delay dimension 的位置，对应 Shen II-B |
| diagonal chirp multiplications | 改为乘两个 diagonal chirp matrices，明确 diagonal 修饰对象 |
| CPP length 与秒制时延比较 | duration；表中以样点计的 N_CPP length 仍保留 |
| population optimum over unrestricted logits | 改为期望损失在所有函数上的最小化解，保留理想函数类条件 |
| Monte Carlo finite differences | 分别描述有限差分近似导数和 Monte Carlo 估计迹，不称为固定组合方法名 |
| previous position | previous parameter estimates，实际为时延和 Doppler 参数 |
| scenes converge；nonconverged outputs | 运行满足停止条件或达到迭代上限，不将数值停止状态扩大成数学收敛结论 |
| valid mean and covariance estimates | 按已读实现说明训练方差范围内接受 site 更新的实际检查 |
| Section learns；Appendix estimates；Table pools | 分别改成章节描述方法、附录中的方法执行估计、表格报告汇总结果 |

保留了核对后成立的表达：Cai 的 single-step denoising、Huang 摘要中的 fractional delay-Doppler off-grid leakage，以及既有方法名、作者确认的 MFLE/GPJD/GP-MP 系列名称。没有把“在 Cai/Shen 未找到”扩大成“全部文献不存在”。sign-preserving logarithmic transform 与实际 sign(x) log(1+|x|) 操作吻合，作为描述保留，不登记为新算法名称。

## 核验与停止编译后的状态

此次措辞修订期间，用户发出停止编译指令之前，两版曾成功编译为 13/15 页；核对了全部 59 个当前编号数学环境、42 条参考文献和表格数值，并查看渲染页面。没有未定义引用、缺字或 overfull box；保留既有 PDF 版本提示和少量 underfull 提示。未改变图文件、模型、权重、实验或训练。

最后另改了两处短语：noise **with** covariance，以及算法第一步 Construct A and **estimate** sigma²。这两处未进入上述 PDF。用户随后要求停止编译并改查蔡文段落骨架，故未再次编译。VALIDATION.json 中 PDF 状态针对停止前已编译版本；当前源码的结构对应关系以[后一项逐段核查](../cai_paragraph_alignment_20261103/PARAGRAPH_AUDIT.md)为准。

逐词修订不证明段落结构符合 Cai。后一项核查明确认定现稿仍存在拆段、拼段及跨章搬移，没有将此次语言修改冒充为逐段对齐完成。
