# AMP阻尼实现与配对消融结果

**递推一致的阻尼已实现并核验，但在本轮四个开发条件上只延缓了方差越界，尚未恢复正常检测。** 16条新增运行全部因噪声标签超过冻结网络的训练支持上限100而停止；没有完成预设100轮预算。原Proposed和原无阻尼AMP均保留。

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent；日期2026-10-15。
- Origin Mode: implement / validate；用户已授权补充阻尼和配对消融。
- Verification Status: 实现代数和保存数组核验通过；16条算法运行均为FAILED，运行调度全部完成。
- 数据范围：四个既有开发条件；不是独立确认集，不建立总体方法排名。
- 预测与评分分离：16条预测全部保存后才读truth评分；权重和输入见[FROZEN_RUN](FROZEN_RUN.json)与[PRESERVED_BASELINES](PRESERVED_BASELINES.json)。

## 实现的更新

完整推导见[PROPOSED_AMP_DAMPING](../../docs/PROPOSED_AMP_DAMPING.md)，原无阻尼框架见[PROPOSED_AMP](../../docs/PROPOSED_AMP.md)。以原完整联合映射D=pF和原复数Jacobian部分迹B为基础，固定新值权重beta：

```text
r_t = x_t + A^H z_t
d_t = D(r_t; ||z_t||_F^2/(Q C))
x_{t+1} = (1-beta) x_t + beta d_t
c_{t+1} = (1-beta) c_t + beta z_t B_t
z_{t+1} = y - A x_{t+1} + c_{t+1}
```

初始化x_0=0、z_0=y、c_0=0。代码采用等价的完整状态阻尼：z_{t+1}=(1-beta)z_t+beta[y-A d_t+z_t B_t]。历史校正随均值阻尼一致更新；B不额外重复乘beta。每轮由实际残差求标签，因此包含跨轮交叉项。输出固定为阻尼信道状态x，活动概率仍为当前原始分类器输出，阈值0.5；原始去噪信道另存诊断。

beta越小，阻尼越强。beta=1逐步退化为原无阻尼AMP。首轮输入、原始去噪输出和活动概率与beta无关，这一点已用真实输入核对。

历史偏导依据为[Fan §5式(5.3)–(5.8)、(5.12)，Remark 5.1](https://arxiv.org/html/2008.11892v5#S5)；复数非可分矩阵部分迹参考[Kunde等 §III-C式(18)–(21)](https://arxiv.org/html/2604.21115v1#S3.SS3)。这些原文的随机矩阵和函数条件不自动覆盖当前有限AFDM。完整状态阻尼的代数一致性不等于状态演化成立或保证收敛。

## 四条件的实际结果

条件顺序固定为scene000/SNR−4 dB、scene008/0 dB、scene016/4 dB、scene024/−4 dB。新增实验仅改变beta及Onsager开关；同一初始化、网络、8探针、差分步长0.01、随机种子202610157301和阈值均不变。每个设置合计18个活跃、142个非活跃用户实例。

| 设置 | 四条件有效更新数 | 运行结果 | 漏检/18 | 虚警/142 | 汇总NMSE（dB） |
|---|---|---|---:|---:|---:|
| 原Proposed，既有配对结果 | 62 / 66 / 99 / 111 | 4条完成并按原规则收敛 | 1 | 0 | −9.700 |
| 原AMP，beta=1，真实输入重放 | 2 / 1 / 2 / 1 | 4条标签越界 | 0 | 142 | +20.225* |
| AMP，beta=0.5 | 3 / 2 / 2 / 2 | 4条标签越界 | 0 | 142 | +14.784* |
| AMP，beta=0.2 | 7 / 5 / 6 / 5 | 4条标签越界 | 0 | 142 | +15.024* |
| AMP，beta=0.1 | 14 / 9 / 12 / 10 | 4条标签越界 | 0 | 142 | +14.419* |
| 关闭Onsager，beta=0.2 | 2 / 1 / 2 / 1 | 4条标签越界 | 0 | 142 | +4.905* |

*失败行NMSE取各条件最后有效输出，再以总误差能量除以总信号能量汇总。停止轮数不同，不能当作完成100轮或相同计算预算的性能排名。无Onsager一行的数值较低，伴随更早停止和较小的阻尼信道幅度，不构成其估计性能更好的证据。完整数值、逐条件分数与轨迹见[PAIRED_RESULTS](PAIRED_RESULTS.json)。

所有新增运行的55个已保存查询快照均把全部用户判为活跃；因此每个设置最后输出的虚警率为100%。以scene000为例，beta=0.2将首轮更新后的残差标签从无阻尼时29.362降至5.504，但后续仍持续增长，在第8次查询前升至148.170而停止。beta=0.1也只是将该条件延长到14个有效更新。

![残差标签与有效迭代](/Users/wangbo/Desktop/科研/JADCEDD/results/proposed_amp_damping_20261015/variance_trajectories.png)

红虚线为训练支持上限，叉号表示下一次查询被拒绝，未在该标签上执行网络。这里“有效更新”只表示数值有限且标签受支持，不表示估计准确。

## 代价与解释

| 新设置，四条件合计 | 一阶score调用 | 分类器调用 | 推断时间（秒） |
|---|---:|---:|---:|
| beta=0.5，Onsager开启 | 297 | 297 | 31.11 |
| beta=0.2，Onsager开启 | 759 | 759 | 76.06 |
| beta=0.1，Onsager开启 | 1485 | 1485 | 145.01 |
| beta=0.2，Onsager关闭 | 6 | 6 | 2.95 |

新增方法均不调用二阶score。Onsager开启时每轮33次联合映射，即66次网络调用；关闭时每轮2次。上述时间为同机MPS推断计时，含相应保存观察开销；全部子进程的总墙钟时间为279.04秒。score与分类器调用的计算量不同，不能将调用总数当作等价FLOPs。原Proposed既有四条件合计1014次网络调用、94.46秒，沿用原保存结果而非本轮重新计时。

![NMSE与累计网络调用](/Users/wangbo/Desktop/科研/JADCEDD/results/proposed_amp_damping_20261015/nmse_vs_network_calls.png)

本轮事实支持“固定阻尼可延缓当前循环的标签增长”，也支持“在beta=0.2时，保留Onsager比关闭它有更长的受支持轨迹”。它们不证明查询误差变成AWGN，也不表示实现已经具有可用的检测性能。仅检查了0.1、0.2、0.5，不能据此断言任意阻尼或所有AMP框架均无效。

先前[单次查询诊断](../proposed_amp_20261015/diagnosis_followup/REPORT.md)显示，天线相关Gaussian噪声足以复现冻结网络的异常分类。与本轮结果结合，优先检验查询协方差与网络噪声训练模型的匹配更有依据。不过原Proposed也曾首轮全判活跃、随后恢复，因此首轮异常不是完整循环失败的唯一已证原因。下一步应针对这项匹配开展独立验证，而不能把更小步长本身当作模型修复。

## 核验与文件保留

- 原9项和新增13项测试共22项通过；命令为`.venv/bin/python -m pytest -q tests/test_score_amp.py tests/test_score_amp_damping.py`。
- [独立数学审查](../../experiments/proposed_amp_damping_20261015/MATH_AUDIT.md)及[合成检查](../../experiments/proposed_amp_damping_20261015/DAMPING_ALGEBRA_CHECK.json)：完整历史、紧凑递推与矩阵历史列扩展的最大状态相对误差低于2×10^−16；历史偏导差分误差低于4.24×10^−10。审查继承本任务上下文，不是盲审。
- [beta=1真实重放](beta_one_replay/CHECK.json)：四条件所有保存数组逐元素完全相同，实际误差为0，失败轮数一致。
- [独立数组核验](VERIFICATION.json)：16条预测、55个快照、信道评分、活动判决、网络代价、历史残差恒等式和方差交叉项均通过。
- [公开入口核对](CLI_CHECK.json)：默认beta=0.2在scene000完成7次有效更新后按设计返回退出码2；全部输出数组及文件哈希与实验调用一致。
- 36项保护清单中35项哈希不变，包括原Proposed代码、三份权重、配置、原AMP代码与原推导。共享注册表在本任务之外新增L-DAMP分支；本任务未编辑或回退它。[范围核对](BASELINE_CHANGE_REVIEW.json)确认完整模块除该分支外的语法树不变，本轮AMP也不通过该注册表调用。最初核验中止的日志保留在[VERIFICATION.initial.log](VERIFICATION.initial.log)，经精确差异审查后重新核验通过，未修改原冻结清单。
- 冻结的新推断源码与四个输入哈希全部不变；没有启用Git。两张PNG已做视觉核对，PDF版本同目录保留。

独立运行入口为[scripts/run_proposed_amp_damped.py](../../scripts/run_proposed_amp_damped.py)，配置为[configs/proposed_amp_damped.json](../../configs/proposed_amp_damped.json)，核心更新在[score_amp_damped/core.py](../../src/afdm_jadcedd/algorithm/score_amp_damped/core.py)。默认beta=0.2，支持`--damping`和`--without-onsager`，结果需写入新路径。旧入口保持可用。
