# MacBook 代码审阅快照（2026-10-21）

来源为 Windows 运行目录 `D:/afdm-gfra-cpu/runs/lstmp_conditional_bce_v3_depth10_fast_20261020`。
`SNAPSHOT.json` 记录采集时刻、文件大小及复制字节的 SHA-256；复制时已逐文件校验。

## 建议阅读顺序

1. `protocol/` 和根目录 `MANIFEST.json`：实际绑定的配置、训练协议和原资产哈希。
2. `source_code/experiments/lstmp_candidate_20261019/receiver.py`、`receiver_base.py`、`message_damping.py`：运行时组合后的基础消息更新与阻尼。
3. `source_code/experiments/lstmp_training_v2_20261020/receiver.py`、`objectives.py`、`optimization.py`、`evaluation.py`：条件信道输出、损失、梯度和选模。
4. `source_code/experiments/lstmp_training_v3_20261020/`：19条件及十层训练入口。
5. `source_code/experiments/lstmp_execution_v3_20261020/`：执行加速；`source_project/` 是实际绑定的物理模型和公共代码。
6. `runtime_corrections/`：原运行保存的执行修正记录；`STATUS.json` 是采集时读取的状态文件，不是实时状态或完成证明。

快照保持原代码与配置，保留 Windows 路径，仅供审阅。未包含训练数据、初始化权重、检查点和完整结果，因此不能原样启动训练；原 `MANIFEST.json` 引用的这些外部资产也不代表已上传。
协议规划最大十层，不表示十层模型已经训练完成或性能已验证。已知相位/噪声训练与估计相位/噪声评价必须分别解释。

仓库根目录的最新比较入口包括 `scripts/compare_lstmp_standard20_cpu_20261021.py` 和 `scripts/evaluate_lstmp_v3_depth6_previous20_cpu_20261021.py`；脚本本身不能代替尚未上传的结果证据。
