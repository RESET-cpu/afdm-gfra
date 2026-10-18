# 核心实验

每个实验一个入口文件，参数集中在文件顶部的 `EXPERIMENT`。日常运行从这里开始。

| 文件 | 改变的条件 | 默认范围 | 现有证据 |
|---|---|---|---|
| [snr_comparison.py](snr_comparison.py) | SNR | −4～8 dB，间隔 2 dB | [500 场景结果](../results/baseline_comparison_500_20261018/REPORT.md)已完成；新入口的生成结果与原批次逐元素一致 |
| [pilot_frames.py](pilot_frames.py) | 导频帧数 | 8、12、16、20、24、28、32 | 待正式运行 |
| [user_count.py](user_count.py) | 候选用户数 | 20、40、60、80 | 待正式运行 |
| [activity_probability.py](activity_probability.py) | 活动抽样概率 | 0.05～0.25，间隔 0.05 | 待正式运行 |
| [convergence.py](convergence.py) | 原生迭代次数／展开层数 | −4、0、8 dB，各 20 场景 | 逐轮完整信道 NMSE；待正式运行 |

统一比较 Proposed、Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP；使用当前固定权重、参数和判决规则，均估计相位和噪声。前四类实验除正在扫描的条件外，固定 40 用户、16 帧、16 天线、0 dB、活动抽样概率 0.1，每个条件默认 500 场景。收敛实验默认每档 SNR 20 场景；这些设置可在对应文件中修改。

`_common.py` 共享生成、算法调用、评分和保存。数值算法仍在 `src/`。原 `experiments/` 保存旧实验实现与复现依赖，本次不改动已有 500 场景的冻结代码和结果。

## 运行方式

在项目根目录执行，例如：

```sh
# 查看已完成的 500 场景结论，无计算、无文件修改
.venv/bin/python -B experiment/snr_comparison.py saved

# 先固定一份新的实验计划，再运行；输出目录必须为空或不存在
.venv/bin/python -B experiment/snr_comparison.py plan --output results/snr_new --scenes 500 --device cpu
.venv/bin/python -B experiment/snr_comparison.py run --output results/snr_new

# 事后汇总与绘图，不调用接收机
.venv/bin/python -B experiment/snr_comparison.py summarize --output results/snr_new
```

其他三个实验使用相同命令，只替换文件名和输出目录。`--values`、`--scenes`、`--seed`、`--methods`、`--device` 仅在 `plan` 时设定；`run` 和 `summarize` 严格使用保存的计划。先查看 `--help`，也可用 `--scenes 1 --values 0 --methods somp` 创建一个小 SNR 检查。

收敛对比同样使用一个入口，默认 20 场景、−4/0/8 dB、40 用户、16 帧；不改变各算法原生停止条件或迭代上限：

```sh
.venv/bin/python -B experiment/convergence.py plan --output results/convergence_new
.venv/bin/python -B experiment/convergence.py run --output results/convergence_new
.venv/bin/python -B experiment/convergence.py summarize --output results/convergence_new
```

创建收敛计划时可用 `--scenes`、`--snr`、`--seed`、`--users`、`--frames`、`--methods` 覆盖参数；运行和汇总仍只读取已保存计划。默认使用 CPU。输出 `CONVERGENCE.csv`、停止轮数汇总、完整范围的 `convergence.png/pdf`，以及前 100 轮的 `convergence_first100.png/pdf`。

## 收敛曲线口径

- 每个物理场景先估计一次共享相位，再运行五种条件接收机；曲线横轴不包括相位搜索轮数。
- 第 0 点为零信道估计。Proposed、GAMP-SBL、Off-grid SBL 按各自原生更新次数记录，GNN-ASPL 按 AMP 展开层数，SOMP 按选取原子数。它们的每轮计算量不同，不能将横轴当作统一计算预算。
- Proposed 和 SOMP 使用已有观察器；其余方法只读完成迭代时的局部状态，不修改冻结求解器文件。Off-grid SBL 在每次超参数更新后，使用该轮参数执行原生的最终后验与信道重构，结果仅供评分，不反馈给算法。
- 真实信道只进入观察评分。每个 SNR 的首个场景自动对照无观察器运行，要求全部最终输出数组逐元素一致、停止轮数和停止原因一致；每条轨迹末点也必须匹配原生最终信道。
- 多场景先汇总完整信道误差与真值能量，再转 dB。已停止的场景沿用最后估计，保持固定场景集合；原始轨迹不伪造后续迭代。各方法绘制到自身最晚停止轮数。
- 逐轮评分、SBL 附加后验重构及 Python 状态观察会增加耗时，因此本实验不作速度排名。有限轨迹反映本次实验的迭代行为，不构成理论收敛证明。

运行可从已完成条件继续；遇到已记录失败或内容变化会停止，保留原记录供诊断。生成、推断、评分产生的原始记录按 `sceneNNN/conditionNN/` 保存，输出 `SUMMARY.json`、`STATISTICS.csv` 和 `comparison.png/pdf`。每个条件保存第一场景的完整预测，其余保存原生输出哈希及每用户误差等紧凑记录。

## 统计口径

- 同一条件下五方法共享观测和估计相位，接收机不读取真实信道、真实活动状态或生成噪声方差。
- SNR 扫描复用相同物理场景和标准化噪声。其他扫描复用种子编号，但改变用户数或活动概率可能改变实际活动集合，不能将其称为完全相同的物理观测。
- 活动抽样要求至少一个用户活跃，接收机先验使用条件边缘概率。用户数扫描固定抽样概率，因此平均活跃人数也会改变。
- AER 汇总漏检与虚警；完整信道 NMSE 先汇总全部用户的误差能量和真值能量，再转 dB。缺失和失败单列，不从剩余样本冒充完整实验。
- 本入口给出点估计；正式论文需另作按物理场景配对的统计区间。已有 500 场景报告中的区间和核验不被替换。
- 日志中的时间包括共享相位时间和条件求解器时间，未构成严格的独立硬件速度比较。

信道泛化仍按[实验协议](../docs/EXPERIMENT_PROTOCOL.md)规划，待确定具体比较条件后再增加对应单文件入口。
