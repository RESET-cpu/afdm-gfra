# 接收机

- `gp_mp/`：当前白噪声 GP-MP。`receiver.py` 为已知相位，`phase_receiver.py` 为 GP-MP-EP，`denoising.py` 为独立去噪。迭代、初始化、条件矩、模型与配置核验各在独立文件中。
- `stmp/`：STMP 三网络实现及现有相位处理依赖。
- `du/`：原 `algorithm/proposed` 的深度展开实现，使用明确的目录名。
- `baseline/`：Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP。
- `frontend/`：相位估计、候选筛选、噪声估计。物理输入结构和路径算子已归入 `channel/`。
- `denoising.py`、`stmp_ablation/`：去噪对照与 STMP 活动判决消融。
- `registry.py`：从工作代码登记构造模型，不在实验脚本中增加方法名分支。

接收机对外提供 `infer`；实验层负责加载观测、计时、保存和对真值评分。GP-MP 的权重、数值设置和配置核验条件保持原样。新方法添加独立实现、登记和配置，不能修改旧计划来跳过哈希核验。
