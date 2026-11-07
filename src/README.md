# 代码

从项目根目录使用 `run_experiments.py`。Python 包直接位于 `src/`，例如 `from algorithm import registry`。

| 目录或文件 | 职责 |
|---|---|
| [algorithm/](algorithm/README.md) | 当前白噪声 GP-MP、STMP、DU、基准及历史实现 |
| `system/` | 物理模型、场景、相位与噪声估计 |
| `networks/` | 接收机与训练共用的网络结构 |
| `training/` | 训练代码；执行须有相应实验授权 |
| [evaluation/](evaluation/README.md) | 实验入口、共享输入、评分、报告与绘图 |
| `configs/experiments/` | 实验方法和扫描范围的默认配置 |
| [configs/algorithms.json](configs/algorithms.json) | 算法名称、构造入口和资源登记 |
| `configs/final/`、`configs/candidates/` | 当前绑定与独立候选配置 |
| [tests/](tests/README.md) | 当前检查；按修改范围选择测试 |
| `history/` | 依赖旧目录布局的历史脚本和测试原件 |
| `project.py`、`utils.py` | 项目路径、资源定位、读写及哈希 |

当前 `GP_MP` / `GP_MP_EP` 登记使用独立的 `algorithm.GP_MP` 白噪声接收机；`C_STMP` 兼容标识也指向白噪声版本。独立去噪使用 `pretrained_white_first`。有色模型不再出现在默认登记，旧目录及历史登记保留用于复现。整理前后的 CPU、源码及 GPU 回放证据见 [主线采用记录](../archive/white_mainline_20261107/ADOPTION.json)。默认配置、历史冻结计划和论文已采用批次仍须分别核对；状态见[实验索引](../result/README.md)。

已有算法目录、配置和历史文件继续保留原路径。目录名中的日期表示实现版本，不能据此判断其是否可删除。历史说明原件见[本次整理记录](../archive/project_cleanup_20261030/README.md)。
