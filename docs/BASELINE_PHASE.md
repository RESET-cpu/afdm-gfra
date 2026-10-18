# 两个 SBL 基线的后验相位更新

参考 Shen et al., *LEO Satellite-Enabled Random Access with Large Differential Delay and Doppler Shift*, TWC 24(4), 2025，[作者稿 §III-C，式(47)–(54)](https://arxiv.org/html/2412.20806v1#S3.SS3)，PDF p.9，Algorithm 1 p.10。借鉴的是利用后验二阶矩更新相位、再重建测量矩阵的思路。此处是当前 AFDM 模型下的推导，不复现原文 OTFS 接收机。

## 目标及协方差

第 q 帧的无跨帧旋转字典按用户分为 D_qk，系数为 X_k，均值为 μ_k。保留本项目跨帧关系 φ_qk=exp(jqβ_k)，q 从 0 开始。固定当前后验及字典中心/偏移，忽略与 β 无关的噪声尺度，最小化

\[
 F(\boldsymbol\beta)=\sum_q \boldsymbol\phi_q^H B_q\boldsymbol\phi_q
       -2\operatorname{Re}(b_q^H\boldsymbol\phi_q),
 \quad [B_q]_{kl}=\mathbb E\langle D_{qk}X_k,D_{ql}X_l\rangle_F,
 \quad [b_q]_k=\langle D_{qk}\mu_k,Y_q\rangle_F.
\]

F 加上观测能量等于后验期望残差能量。若各天线有相同系数协方差 Σ，M 为天线数，则

\[
 [B_q]_{kl}=\langle D_{qk}\mu_k,D_{ql}\mu_l\rangle_F
 +M\sum_{i\in k,\,j\in l}(D_q^HD_q)_{ij}\Sigma_{ji}.
\]

这里是 Σ_ji 而非 Σ_ij。GAMP-SBL 的近似后验按系数、天线分解，第二项只有用户对角项，在 |φ|=1 下为常数；代码仍计算并记录它。off-grid SBL 保留完整 Σ，其跨用户项通常不是常数，不能只用均值替代。

off-grid SBL 在最后一次方差、偏移更新之后重新计算的后验为

\[
 C=A\Lambda A^H+\sigma^2I,\quad
 \mu=\Lambda A^HC^{-1}Y,\quad
 \Sigma=\Lambda-\Lambda A^HC^{-1}A\Lambda.
\]

A 是该基线最终的**一阶线性化字典**。相位目标使用这个 A 对应的后验；该基线对外报告的信道仍按最终连续位置的精确物理原子重建。二者有线性化差异，逐次保留原基线的 `linearization_relative_error`。

## 实现边界

原前端先拟合每用户一条物理路径获得 β 初值；新流程随后调用各自条件接收机，计算上述 B、b，做一次外部相位更新，再重新运行同一接收机。相位目标去掉常数对角项后做两轮逐用户搜索。局部更新最大化

\[
 \operatorname{Re}\sum_q c_{qk}e^{-jq\beta_k},\quad
 c_{qk}=b_{qk}-\sum_{l\ne k}[B_q]_{kl}e^{jq\beta_l}.
\]

全步及半步分别使用 β_new=wrap(β_old+w·wrap(β_candidate−β_old))，w=1 或 0.5。保留旧点并检查完整目标下降。固定目标的梯度为 2Σ_q q·Im{φ_qk*[(B_qφ_q)_k−b_qk]}，用于独立有限差分核对。

本实现保留 exp(jqβ_k) 的跨帧约束。Shen 式(53)先求无约束线性解再投影到单位圆；直接照搬会丢失这里的跨帧关系。因此采用上述一维搜索，不声称使用了其同一个闭式更新。

后验更新不等于整体收敛保证：GAMP 是近似后验；SBL 有筛选、局部偏移更新及重新初始化。新相位也没有与每个基线的帧内物理 Doppler 强制绑定，因此只能解释为更新的相位斜率，不把它反解成最终绝对物理 Doppler。更小的后验目标可能只使错误的信道解释更自洽；必须以独立信道 NMSE、活动和相位误差判定效果。

`algorithm/baseline_phase_posterior.py` 导出后验，`algorithm/baseline_phase.py` 更新相位，`scripts/run_baseline_phase.py` 提供只接受四项公开输入的独立入口。为保留冻结的读出身份，off-grid 的适配循环放在原模块外并调用其原数值内核；测试要求输出和迭代轨迹逐项等于原接收机。主线五基线由 `algorithm/unknown_phase_baselines.py` 从原始导频估计相位；本节实现用于在这个估计初值上继续进行后验更新。

```text
.venv/bin/python scripts/run_baseline_phase.py --method offgrid_sbl --input /absolute/path/input.npz --output /absolute/path/new_output.npz --phase-weight 0.5
```

主线的未知相位与理想参考定义见 [实验协议](EXPERIMENT_PROTOCOL.md)。后验更新的开发和验证约定见 [更新实验协议](history/experiments/baseline_phase_learning_20261015/PROTOCOL.md)，完成结果见 [报告](../docs/history/results/baseline_phase_learning_20261015/REPORT.md)。其中“固定相位”指固定从观测获得的估计值；真实相位只出现在单列的 oracle 诊断中。
