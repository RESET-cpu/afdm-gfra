# MNOMP 归档

2026-10-14 按用户要求单独归档。当前 `run.py` 的主线与研究入口均不注册 MNOMP。

- `snapshot/src/`：归档前的源码及共用依赖，保留原字节。
- `snapshot/configs/`：归档前的默认配置、预算配置和活动门限；共用文件按当时状态保留。
- `snapshot/tests/test_offgrid_baselines.py`：包含 MNOMP 的原始物理、恢复和文件读写检查。
- `experiments/`：MNOMP 专用实验及调用它的联合比较入口；目录结构与原路径对应。
- `results/`：MNOMP 专用结果。原 `results/mnomp*` 路径保留历史访问链接。
- [MANIFEST.json](MANIFEST.json)：移入路径和文件 SHA256。

共享 SBL/MNOMP 结果仍位于原结果目录，包括 `results/offgrid_baselines_20261012`、
`results/offgrid_budget_20261014` 和 `results/offgrid_original_grid_20261014`。
这些文件及其中的冻结配置、源码快照作为历史证据保留。
归档脚本中的原根目录和配置绑定反映当时运行环境；如需重新运行，应先在独立目录恢复配套环境。
