# 检查

```text
python -m pytest -q
python -m pytest -q src/tests
```

第一条只运行 `public/`，无需权重或原始数据。第二条包含当前研究检查，需要已发布权重以及完整本地研究资产、Times New Roman 字体；不启动训练或正式批次。

- `public/`：数学恒等式、配置、资产、路径、公开命令及模块依赖边界。
- `test_organized_code.py`：冻结源码身份，以及场景、波形和指标的前后对照。
- `test_configured_experiments.py`：八类实验的计划、推断调用、评分、汇总和绘图；临时接收机明确是合成接口样例。
- `test_stmp*`、`test_phase_init_marginal*`、`test_convergence*`：相位、消息更新、固定迭代和评分的数值检查。
- `test_configurable_plots.py`、`test_paper_plotting.py`：汇总一致性、图例和出图边界。
- `test_white_followup_receivers*`：后续实验的输入隔离、结果验证、配对、调度和采用条件。

已退役算法专属测试及所有整理前测试原件保存在 `archive/frozen_reproduction_20261107/src/tests`；它们不在当前测试收集范围。重复的流程测试已移入 `delete/`。
当前测试按已采用的白噪声主线更新路径与协议断言，没有放宽算法误差容差。
真实预训练接收机前后对照、十图重绘和资产核验见 `archive/code_cleanup_20261107/`。
这些验证不等同于重新训练和全量 Monte Carlo 复现。
