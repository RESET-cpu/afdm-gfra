# 冻结实验源码

这里保存仍被保留实验的哈希记录引用的原始源码和配置。`MANIFEST.json` 给出原路径、归档路径和原 SHA-256；当前实现位于 `src` 的功能目录。
原始文件未修改。独立 DU 资产及重复旧快照在本地 `delete/`，不属于这个回放源集合。测试原件单列于 `TESTS.json`，不参与当前运行。

日常入口 `python run_experiments.py ...` 使用当前代码。读取冻结元数据时，仅清单中声明的旧路径会解析到这里；写入不重定向。`FINAL.json` 保留原始绑定字节，其旧源码路径通过这个清单查找。

需要显式回放原模块时，在仓库根目录使用：

```text
python archive/frozen_reproduction_20261107/replay.py evaluation.white_followup_20261107.run inspect
python archive/frozen_reproduction_20261107/replay.py evaluation.suite --help
```

`replay.py` 先验证全部归档哈希，再将原模块的资源读取定位到当前仓库。它只调整路径，不修改算法、原计划和结果；只有显式传入原模块的执行命令才运行实验。原模块可能需要未发布的原始数据或历史模型。现有失败、停止、完成标记仍然有效，不应为方便续跑而覆盖。

已有旧计划应使用匹配的冻结入口；新实验在新的输出目录创建当前计划。迁移后的 `white_followup` / `convergence` 如用于执行，会另行核验并记录 `archive/code_cleanup_20261107/CURRENT_SOURCES.json`，明确区别原计划身份和实际执行源码。当前队列未重启。

历史有色算法在此仅供旧曲线追溯；当前 `src` 的接收机和训练不导入它们。旧检查点中的 `colored` 格式名以及历史绘图中的方法标签仍保留原义。
