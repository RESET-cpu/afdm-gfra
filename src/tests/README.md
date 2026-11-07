# 当前检查

在根目录运行 `.venv/Scripts/python.exe -B -m pytest -q`。
这里保留当前入口、共享场景、公共输入变换和评分检查；历史候选算法及训练测试原件位于 `src/history/tests`。
目录迁移的已有场景回放与完整文件核验单独记录于 `result/layout_20261021`，不属于全量实验。

`test_configured_experiments.py` 验证独立实验入口、配置选择、算法类别和新增方法的完整执行/评分/作图接入。
其中临时接收机仅是接口测试数据，不是科研 baseline；不运行 STMP 或正式场景。

`test_source_cleanup.py` 检查统一文件读写、模型配置解析、归位后的导入，以及 STMP 与消融共享的停止判定和文件保存。
这部分使用合成测试对象，不加载三网络推断。已有诊断场景的逐数组回放记录在 `result/source_cleanup_20261021`。

`test_proposed_phase_integration.py` 检查内部相位估计的原始输入边界、known/estimated 路由、
噪声字段隔离、固定高斯目标的梯度及下降、端到端计时不重复叠加。
原10份开发输入的完整CPU回放单独记录于 `result/mainline_message_gem_20261022/REPLAY_COMPLETE.json`。
