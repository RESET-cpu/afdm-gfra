# 一阶训练方案小规模对照

2026-10-13 状态核对：本试验最后保存状态为 FAILED，错误为 `TimeoutError: [Errno 60] Operation timed out`，原进程已退出，断点保留。尚不能报告三组最终性能结论。实际状态见 [STATUS.json](STATUS.json)，运行日志见 [pipeline.log](pipeline.log)。以下为原试验设计与恢复入口；原 200/100/100 续训另已按用户要求暂停。

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: plan + run
- Date: 2026-10-13
- Verification Status: 32 项相关测试和真实 MPS 前向/反向检查通过；性能试验因 I/O 超时失败，断点保留。

## 固定对照

| 组 | 目标 | 参数更新数 |
|---|---|---:|
| dsm | 原 DSM | 1,000 |
| augmentation | 原查询与相位旋转查询各占一半 DSM | 1,000 |
| consistency | 同上，再加 0.1 倍相位关系惩罚 | 1,000 |

三组均从原第 81 轮选定 EMA 初始化，使用相同训练信道、噪声抽样、学习率及更新次数。增强和约束组计算量更大，单独记录；不宣称训练耗时相同。最终固定第 1,000 步 EMA，不事后选择最优轮次。原三个网络与默认接收机保持原样。

验证使用原完整 5,000 个独立 AWGN 信道，以及预先固定的 4 个新物理场景 × 3 个 SNR。后者与训练、原验证、proposed 100 场景和 baseline 1,000 场景种子均不重叠，属于开发验证，不能据此宣称总体优势。完整迭代只替换一阶，保留旧二阶和分类器，明确作为教师尚未重训的诊断。

完整定义见[冻结协议](runtime/experiments/proposed_phase_training_20261012/PROTOCOL.md)、[配置](config.json)和[文件身份](MANIFEST.json)。[测试记录](TEST_VERIFICATION.json)和[MPS 检查](MPS_SMOKE.json)保留核验结果；既有数值库警告未隐瞒。所有失败与支持范围外查询均记录。

## 保存与结果

训练每约 120 秒保存完整断点，阶段完成也保存。所有阶段串行执行，单次启动有 24 小时时限。进程退出会释放防空闲睡眠状态。最终生成 `SUMMARY.json`、`REPORT.md`、`SAMPLING_VERIFICATION.json` 和原模型核验；不自动采用候选权重或训练新二阶/分类器。

如需暂停此独立试验，在本目录创建 `pause.request`。恢复前查看日志、移除该标记并使用冻结入口：

```sh
.venv/bin/python -B runs/proposed_phase_training_20261012/runtime/experiments/proposed_phase_training_20261012/runner.py --run runs/proposed_phase_training_20261012
```

该入口与已暂停的 200/100/100 续训相互独立。
