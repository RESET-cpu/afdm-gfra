# GitHub 内容与复现范围

本快照包括 2026-11-07 的代码分区、目录上移、路径修复和源码使用说明。
从 GitHub 下载后安装依赖，直接运行根目录脚本；使用与复现指南见
[REPRODUCING.md](REPRODUCING.md)，许可状态见 [RIGHTS.md](RIGHTS.md)。

本次快照日期为 2026-11-07，目标为私有仓库 `RESET-cpu/afdm-gfra`。全部内容以本地最新工作目录为准，不合入远端过时文件。保留本地当前目录布局及研究状态；本次上传没有启动训练或批量实验。

## 保留的内容

- `src/`、`run_experiments.py`、`requirements.txt`：算法、系统模型、网络定义、训练与数据生成代码、配置、测试、历史源码和现有许可证。`pyproject.toml` 只配置默认测试。
- `paper/STMP`、`paper/C-STMP`、`paper/DU`：稿件源码、已有阅读 PDF、正式图表、研究文档、审稿决定和小型修订核验记录。
- `reference/`：文献索引、阅读记录和写作资料；下载的第三方论文 PDF 与页面预览留在本地。
- `result/`：精选实验计划、完成/失败说明、小型结果汇总、论文绘图汇总及模型/数据的描述信息。目录名中的 `data` 或 `models` 不表示包含原始样本或权重。
- `FINAL.json`、`MAINLINE.json` 与精选归档记录：当前绑定、冻结历史、目录映射与采用依据。

完整文件清单和 SHA-256 见 `GITHUB_MANIFEST.json`。它记录这次上传的字节内容，不包括清单本身。状态文件是上传时的快照，运行中的实验需以本地状态为准。

## 不包含的资产

模型权重和检查点、原始训练/验证/测试数据、逐场景预测与轨迹、运行日志、环境目录、编译缓存、临时截图、重复备份和大型压缩包均不在当前快照中。部分历史文档链接因此需要本地完整研究目录才能访问。

本地资产没有删除或移动；冻结绑定与哈希保持原文。GitHub 旧提交曾包含模型或数据，本次更新不重写提交历史，所以旧版本中的这些资产仍可追溯。

## 阅读与复现

当前工作算法入口是 `receiver.gp_mp`，冻结批次保留 `algorithm.GP_MP`，已知相位与估计相位登记为 `GP_MP` / `GP_MP_EP`。论文目录仍为 `paper/C-STMP`；白噪声主线及其他曲线的替换状态见根目录 README 和稿件说明。

安装 Python 依赖后，可用以下命令查看入口并运行不需要权重的小型合成示例：

```text
python -B run_experiments.py list
python -B run_experiments.py snr_comparison --help
python run_experiments.py demo --output result/demo_first
```

论文 PDF 和正式图表可以直接阅读。当前七组实验曲线所需的小型绘图 JSON 按 `src/configs/plots/manuscript.json` 保留。图 3 的信道示例还依赖未上传的 `scene000_example.npz`；其最终图形已保留。图形重绘还需绘图说明中列出的依赖和字体。

完整推断、训练和数值复现需要恢复配置所引用的本地资产。当前两项模型权重的路径及 SHA-256 在 `FINAL.json` 中，其他模型绑定见 `src/configs/final/models.json`。请核对这些记录，不能用任意新权重替代后声称复现冻结结果。

## 后续同步

`.gitignore` 默认排除实验输出及权重、数组等文件。新增汇总应先检查其是否为聚合指标，再按具体文件路径加入 Git；不要整体强制加入 `result/`。本次按文件清单构建提交，保留原工作目录及暂存区中的研究修改。
