# 检查

在仓库根目录运行无需权重或原始数据的默认检查：

```text
python -m pytest -q
```

默认范围为 `public/`，覆盖数学恒等式、信道重构、评分、配置、路径和命令接口。

完整本地研究检查使用 `python -m pytest -q src/tests`。下载版已有推断权重时可运行：

```text
python -m pytest -q src/tests -k "not test_independent_entry_and_updated_1000_scene_defaults"
```

排除的八项依赖未发布的旧计划备份；其余研究检查可能需要已发布权重和 Times New Roman 字体。测试范围包括当前接收机与原实现的数值对照、实验流程、图表来源，以及后续批次的任务派发和结果验证。

最新验证见[逐文件审查后的修改](../../archive/code_fixes_20261107/README.md)：228 项通过，2 项 CUDA 检查因在跑实验而跳过。已退役候选的专项测试随候选移入 `delete/`，原件仍在冻结归档。

更早记录见[代码整理检查](../../archive/code_cleanup_20261107/README.md)和[导频任务读取修复](../../archive/pilot_resume_20261107/README.md)。测试通过的范围与完整重新训练、论文全部数值复现分开记录。
