# 学习密度比消融

入口：`experiment/density_ratio_ablation.py`。

## 比较对象

- Proposed：使用冻结分类器的 logit，并按训练先验与接入先验修正。
- Gaussian-site activity evidence：使用当前已接受或保留的 Gaussian site，计算
  `ell = ||R||²/v - ||R-E||²/(c+v) - D log(1+c/v)`，再取
  `p = sigmoid(logit(rho) + ell)`。

第二个版本在每次 MP 更新中使用该概率形成信道均值、协方差和反馈消息；最终活动门限仍为 0.5。
训练噪声范围外，两者都采用原 Gaussian fallback。信道均值／误差网络、公共方差汇总、
site 接受／复用规则、初始化、阻尼、停止规则、相位和噪声估计完全相同。
相同的是更新规则，替换证据之后的迭代轨迹和实际停止次数允许不同。

解析密度比对应 Cai §III-B 式(30)的 Gaussian 活动证据，以及本稿第五章已定义的
Gaussian fallback；具体运算调用冻结 `proposed/posterior.py::full_posterior`。
这是本文接收机的受控消融，不将对照标为完整复现 Cai 接收机。
术语依据见 `docs/TERMINOLOGY.md` 中 Gaussian site 和 density ratio 条目。

## 文件隔离

`denoiser.py` 和 `receiver.py` 是冻结数值实现的实验专用副本。前者只关闭分类器证据分支、
放宽为无分类器的构造条件，并转用已存在的 Gaussian posterior；后者加载相同信道网络、
使用本地 denoiser 并正确标记证据来源，不实例化分类器。冻结配置仍用于核对整套权重身份，
记录中明确 `classifier_loaded=false` 和 `classifier_calls=0`。
迭代、线性模块、Gaussian 运算、信道矩网络和估噪直接调用原实现。任何对原实现的后续改动
都需重新核对副本；计划保存全部源文件及权重哈希。

## 配对、复用与统计

默认 500 场景，种子起点 202610172000001，SNR = −4、−2、0、2、4、6、8 dB；
40 用户、16 帧、16 天线、活动抽样概率 0.1。使用原配对观测和估计相位，核验哈希后
复用同一计算后端的 Proposed 记录。默认 auto 在本机选择 MPS；指定 CPU 时，原 MPS
Proposed 结果不会复用，两个版本均在 CPU 推断。`--fresh` 关闭历史复用。

新结果保存在用户指定的新目录。原 500 场景结果、冻结配置及权重不写入。
失败结果保留，汇总不删除失败场景、不只选共同成功子集；正式图仅在全部计划条件完成后生成。
续跑校验已完成结果及其历史来源。

输出 `comparison.png/pdf` 包含 AER 与完整信道 NMSE；`STATISTICS.csv` 保存合计漏检、
虚警和误差能量；`PAIRED_STATISTICS.json/csv` 给出“学习密度比 − Gaussian 证据”的
AER 与 NMSE(dB)差异，负值表示学习密度比更好。95% 区间采用 10000 次场景配对 bootstrap，
每次保留场景内所有用户并对两个版本使用同一抽样索引；各 SNR 也使用相同重采样。
这是逐点区间，不是跨 SNR 同时置信区间；单场景运行仅验证流程，不产生区间。
历史与新增运行时间不用于速度比较。

## 运行

```sh
.venv/bin/python -B experiment/density_ratio_ablation.py plan --output results/density_ratio_ablation
.venv/bin/python -B experiment/density_ratio_ablation.py run --output results/density_ratio_ablation
.venv/bin/python -B experiment/density_ratio_ablation.py summarize --output results/density_ratio_ablation
```

`--scenes`、`--seed`、`--values`、`--device`、`--fresh` 仅在 plan 时生效。
单场景流程检查可在新的输出目录用 `--scenes 1 --values 0` 建计划；不修改正式计划的预算或规则。
