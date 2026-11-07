# 接收机

- `gp_mp/`：当前白噪声 GP-MP。`receiver.py` 为已知相位，`phase_receiver.py` 为 GP-MP-EP，`denoising.py` 为独立去噪。迭代、初始化、条件矩、模型与配置核验各在独立文件中。
- `stmp/`：STMP 三网络实现及现有相位处理依赖。
- `baseline/`：Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP。
- `frontend/`：相位估计、候选筛选、噪声估计，以及 STMP 共用的 `phase_math.py`、`phase_initialization.py`、`phase_update.py`。物理输入结构和路径算子已归入 `channel/`。
- `denoising.py`、`stmp_ablation/`：去噪对照与 STMP 活动判决消融。
- `registry.py`：从工作代码登记构造模型，不在实验脚本中增加方法名分支。

接收机对外提供 `infer`；实验层负责加载观测、计时、保存和对真值评分。GP-MP 的权重、数值设置和配置核验条件保持原样。新方法添加独立实现、登记和配置，不能修改旧计划来跳过哈希核验。

有色版本已经退出默认入口，未从仓库删除。原有色接收机、训练代码和登记已移入独立的
`archive/frozen_reproduction_20261107`，供旧实验追溯。当前 `gp_mp` 明确核验
训练记录中的 `max_strength=0`，查询使用 `vI`；旧检查点的 `colored` 格式名和
兼容网络结构仍保留，不代表当前使用有色训练。`C_STMP` 默认登记仅是 GP-MP 的旧名称别名。

基线实际运行源码由 `src/configs/organized/baseline_sources.json` 校验；原 `final/baseline_sources.json` 只维持原活动读出校准的身份，两者分别记录。
