# 当前检查

默认 `python -m pytest -q` 运行 `public/` 内的 29 项发布检查，覆盖数值恒等式、
完整信道重建、指标、当前配置、路径搬迁、资产检查和命令，不需要本地权重或历史结果。
这些检查与以下研究检查分开维护，不把未运行的研究检查记作通过。

原研究测试继续保留原路径，避免破坏冻结记录。显式运行相应文件即可。
2026-11-07 发布预审抽查 `test_configured_experiments.py` 和
`test_layout.py::test_four_visible_top_level_folders`，结果为 7 通过、7 失败。
失败原因是历史方法名称、SNR 范围及目录布局断言与现状不一致；并非已经修复的算法失败。
默认入口改为发布检查，没有删除或放宽这些历史断言。旧研究检查还可能需要未上传的
权重、历史计划和本机运行环境，不适合作为纯源码下载后的统一验收入口。

代码整理的对照检查为 `test_organized_code.py`、`test_organized_pipeline.py`：验证冻结源码哈希、场景与观测逐数组一致、波形算子一致、登记参数一致，以及合成接收机从计划到评分/汇总/绘图的完整调用。运行 `python -m pytest -q src/tests/test_organized_code.py src/tests/test_organized_pipeline.py`。

目录上移后的真实预训练网络对照与十图临时重绘结果见 `archive/src_flatten_20261107/`。这些检查没有启动训练或正式实验；旧测试中依赖历史配置状态的断言不等于当前主线验收。

以下说明属于原研究检查；运行时显式给出对应文件路径。
这里保留当前入口、共享场景、公共输入变换和评分检查；历史候选算法及训练测试原件位于 `src/history/tests`。
目录迁移的已有场景回放与完整文件核验单独记录于 `result/layout_20261021`，不属于全量实验。

`test_configured_experiments.py` 验证独立实验入口、配置选择、算法类别和新增方法的完整执行/评分/作图接入。
其中临时接收机仅是接口测试数据，不是科研 baseline；不运行 STMP 或正式场景。

`test_source_cleanup.py` 检查统一文件读写、模型配置解析、归位后的导入，以及 STMP 与消融共享的停止判定和文件保存。
这部分使用合成测试对象，不加载三网络推断。已有诊断场景的逐数组回放记录在 `result/source_cleanup_20261021`。

`test_proposed_phase_integration.py` 检查内部相位估计的原始输入边界、known/estimated 路由、
噪声字段隔离、固定高斯目标的梯度及下降、端到端计时不重复叠加。
原10份开发输入的完整CPU回放单独记录于 `result/mainline_message_gem_20261022/REPLAY_COMPLETE.json`。
