# GP-CCD-MP-DRE 命名修订

2026-10-30，作者确认整体算法名为 **GP-CCD-MP-DRE**。

## 正文和命名依据

- 第 III 章开头解释 generative prior（GP）、covariance-conditioned denoising（CCD）、message passing（MP）、density ratio estimation（DRE）四个技术组成；两个功能模块仍为 MFLE、GPJD。
- Algorithm 1 和第 VI 章比较文字统一新名称，同段重复处使用自然指代。为避免加长名称使末条参考文献单独占页，简化 III 开头的重复导读语，并压缩五个已改名结果段落的重复措辞；数值、比较对象、适用范围和不利结果均保留。
- 正文没有增加“DRE 相对于本地 STMP 独有”的宣称。DRE 仍在适用的迭代内参与活动概率和联合矩更新。
- Shen 的 MRF-MP-GAMP（§III-C 末与 Algorithm 1，PDF pp.9–10）和 MRF-MP-GAMP-CNN（§IV-B 与 Fig.4，p.11）提供命名组织的参照；没有据此改变接收机结构。原文：https://arxiv.org/html/2412.20806v1 。
- 完整新名称和 CCD 缩写登记为作者批准的本文描述性名称，未冒称文献现成名称。来源与适配边界追加在本稿 docs/TERMINOLOGY.md。

## 图例和数值核验

六幅比较图的图例统一为 GP-CCD-MP-DRE，STMP 及四个稀疏恢复基线保留原名。内部方法标识、颜色、线型、标记和全部点保持原样。

493 个绘图点逐点与源 JSON 严格相同，其中 NMSE 421 点、AER 72 点。AER 仍仅用于 SNR 和导频帧数两图。独立去噪图未改。收敛、用户数和活动概率图保持 3.5×2.65 英寸；跨信道保持 7×2.6 英寸、一行四面板；SNR 和导频保持 3.5×2.2 英寸。双面板布局在导出前固定，以避免后端差异造成中间轴文字挤压。

本轮仅绘图和编译，未运行推断、批量实验或训练。原始统计、模型绑定、冻结绘图引擎和未涉及章节的 31 个基线文件哈希不变。C-STMP/C_STMP 作为历史名称、存储目录及实验标识保留；根 README 未由本任务编辑。

## 编译、复核与覆盖范围

唯一完整阅读稿仍为 paper/C-STMP/main.pdf，共 14 页。Tectonic 编译成功，无未解析引文/交叉引用、重复标签、缺字或 overfull 警告。少量 underfull 警告经视觉检查不影响阅读。

六幅图导出的 PDF 均经 Poppler 渲染检查。最终成稿第 4–8 页由主代理检查，第 9–14 页由绘图审查代理逐页检查：名称定义、算法题名、公式、图例与参考文献完整，无裁切、重叠或孤立末页。文字审查代理复核了名称替换、STMP 归属及 respectively 对应关系，后续五段精简采用其建议。主代理另核对所有数学表达、数字、引文、标签和交叉引用保持原序列。

ARS 缩写检查覆盖 I–VI 章正文的部分提取视图，不覆盖公式、图表、摘要或附录，状态仍为 partial。七项既有提示保留；新增 GP、MP、DRE 的 defined_after_use 提示来自组合名称在同一句内先出现、随后立即解释各组成部分，经人工核对定义完整。报告不是全稿缩写检查通过的证明。

## 复现与记录

- `render_named_figures.py`：只读取冻结来源并输出六幅暂存图；不启动接收机或修改正式图。
- `RENDER_VALIDATION.json`、`PLOT_PDF_VALIDATION.json`：曲线值、来源、尺寸和暂存 PDF 检查。
- `baseline.json`、`before/`：修改前文件哈希及受影响 TeX 源码，不保留额外完整论文 PDF。
- `verify_revision.py`、`VERIFICATION.json`：正式图与暂存图一致、数学和数字保持、受保护文件、名称统一及编译状态检查。
- `acronym_report.md`、`acronyms.json`：有明确覆盖限制的缩写建议报告。

重绘使用仓库的 `.venv/Scripts/python.exe`；将核验通过的六图发布到本稿 figures 后，再编译 main.tex。历史绘图记录不回写，以保留当时名称的可复现性。
