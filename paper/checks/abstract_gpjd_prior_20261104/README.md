# 摘要明确 GPJD 中的生成式先验

2026-11-04，按作者反馈将所学生成式先验的作用直接写入 GPJD 功能从句。

修改后接收机说明：

> We then develop a message-passing (MP) receiver with two modules: multi-frame linear estimation (MFLE), which suppresses inter-user interference; and generative-prior-aided joint denoising (GPJD), which uses the learned generative prior for minimum mean-squared error (MMSE) denoising.

原先对 learned prior 的接收机总体说明移到 GPJD 从句，中文摘要同步。技术含义与引言第三项贡献、第四章学习方法及第五章模块操作保持一致。没有改变 score-based 的定位或任何算法、实验结果、公式与图表。

两版 PDF 编译成功，保持 13/15 页、44 篇参考文献；只有首页渲染发生变化，其余页面逐像素一致。首页已目视检查，无新增溢出、截断或遮挡。编译无未定义引用、缺字或越栏报告。

`before/` 保存原稿；`CHANGES.diff` 为英文修改；`VALIDATION.json` 为核验；`render/` 保存两版首页预览。预审决定与术语记录已同步这次澄清。
