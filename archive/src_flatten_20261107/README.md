# 去掉项目包目录

按作者要求，去掉 `src/afdm_gfra` 这一层。场景、波形、信道、接收机、实验和绘图直接位于 `src` 下，导入改为 `from receiver ...` 等功能路径。目录导航见 [src/README.md](../../src/README.md)。

- 总入口仍为 `run_experiments.py`，内部命令分派位于 `src/experiment/commands.py`；安装项目后也可使用 `python -m experiment`。
- 路径和读写工具分别为 `src/workspace.py`、`src/fileio.py`。项目安装配置、算法登记、源码记录和文档同步调整。
- 网络直接复用 `src/networks`。整理后的训练代码位于 `src/training/organized`，与仍被冻结记录引用的原训练文件区分。
- 原 `src/algorithm`、`src/system`、`src/evaluation` 等冻结源码保持原位置和字节；`white_followup` 与 `convergence` 仍调用原执行模块。没有启动训练、正式实验或恢复导频数队列。

迁移前的 216 个工作文件与导航文件保存在 `before/`，校验值见 `BEFORE.json`。不再使用的包文件移至 `unused_package_files/`；它们不属于当前运行路径。初次整理的 [MAPPING.json](../code_organization_20261107/MAPPING.json) 已更新目标路径，原始源文件和哈希保持不变。

验证记录：

- `VALIDATION.json`：当前模块编译/导入、默认绘图配置、训练源码记录、冻结源码/计划和模型绑定核验。
- `CHECKPOINT_VALIDATION.json`：同一白噪声权重、一次合成 AWGN 查询，旧版与当前去噪器输出逐元素一致；这不是正式实验结果。
- `PLOT_VALIDATION.json`：十幅论文图在临时目录重绘，200 dpi 下逐像素一致；正式图未覆盖。
- 13 项对照测试全部通过：`python -B -m pytest -q src/tests/test_organized_code.py src/tests/test_organized_pipeline.py`。

本次改动尚未同步 GitHub。已有模型、数据和科研结果未随目录上移更换。
