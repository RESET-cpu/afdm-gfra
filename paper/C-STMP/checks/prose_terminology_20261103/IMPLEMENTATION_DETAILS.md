# 正文移出的实现设置

本轮只移动说明，不改变计算。以下完整停止规则同步保存在 main_full 附录 C。

归一化常数：s = 0.2647966453。

活动变化、Gaussian site 参数和活动历史容差分别为 1e-3、0.1、1e-3；历史权重 0.2，连续通过窗口 5，硬判决稳定窗口 10。最小／最大迭代数 60／600，相对变化容差 5e-4。

```tex
The estimate check monitors relative changes in $\widehat X$ and $v$,
the maximum activity change $\max_k|p_k^{(i)}-p_k^{(i-1)}|$, and
$d_{\rm var}^{(i)}=|v_{\rm tar}^{(i)}-v^{(i)}|/
\max\{v_{\rm tar}^{(i)},v^{(i)}\}$.
The site check requires accepted updates with stable precision
$c_k^{-1}$ and natural parameter $E_k/c_k$, together with a small
activity-history residual $\max_k|p_k^{(i)}-w_k^{(i-1)}|$.
After this comparison, update
$w_k^{(i)}=(1-\zeta_{\rm hist})w_k^{(i-1)}+\zeta_{\rm hist} p_k^{(i)}$, starting from
$w_k^{(0)}=\rho$. This history is used only for stopping.
After $I_{\min}$ iterations, both checks must hold for $L_s$
consecutive iterations and hard activity decisions must remain unchanged
for $L_d$ iterations; otherwise, return the last iterate at $I_{\max}$.

```
