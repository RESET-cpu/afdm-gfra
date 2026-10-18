# 局部平衡提议与多温度 MCMC：来源和本模型适配

2026-10-15。只核验公开原文和数学适用条件，未运行采样、推断或训练。
本文件不登记温度、链长或新实验参数。下面把论文原式与本项目的代数推导分开。

## 原始论文及准确位置

1. **Giacomo Zanella, Informed Proposals for Local MCMC in Discrete Spaces.**
   *JASA* 115(530), 852–865, 2020；在线发表于 2019。
   [出版信息](https://www.tandfonline.com/doi/abs/10.1080/01621459.2019.1585255)，
   [作者主页](https://sites.google.com/site/gzanellawebpage/research)，
   [作者上传原文](https://arxiv.org/pdf/1711.07424v1)。
   实际核对的是 2017 年 v1，共 34 页；以下式号和页码属于该版本，不冒充期刊排版。
   §2.2，第 4 页式 (2)–(4) 定义 informed proposal、归一化项及 balancing function
   的条件 \(g(t)=t g(1/t)\)。第 8 页表 1 明列 \(g(t)=\sqrt t\)；§4.1、式 (11)
   区分提议权重与接受概率。§3，第 5–7 页的渐近比较依赖条件；§6.4，第 14–15 页
   讨论邻域变大带来的计算开销。本文引用其构造与术语，不把渐近最优性外推到本项目。

2. **Koji Hukushima and Koji Nemoto, Exchange Monte Carlo Method and Application
   to Spin Glass Simulations.** *JPSJ* 65(6), 1604–1608, 1996。
   [出版信息](https://www.jstage.jst.go.jp/article/jpsj/65/6/65_6_1604/_article)，
   [作者上传原文](https://arxiv.org/pdf/cond-mat/9512035v1)。
   所读预印本共 16 页。§II，第 3 页式 (2.1)–(2.7) 给出副本乘积目标、交换详细平衡
   和 Metropolis 接受率；第 4 页式 (2.8)–(2.9) 按温度收集统计量。
   §III，第 5 页列出必要诊断，并明确交换与温度往返均发生仍可能未遗忘初态。
   §IV 的离散 Ising 自旋提供有限离散状态应用；§V，第 8 页讨论交换失败的情形。

3. **Gautam Altekar, Sandhya Dwarkadas, John P. Huelsenbeck, Fredrik Ronquist,
   Parallel Metropolis coupled Markov chain Monte Carlo for Bayesian phylogenetic
   inference.** *Bioinformatics* 20(3), 407–415, 2004。
   [DOI](https://doi.org/10.1093/bioinformatics/btg427)，
   [出版社全文](https://academic.oup.com/bioinformatics/article-pdf/20/3/407/48905115/bioinformatics_20_3_407.pdf)。
   第 409 页（PDF 第 3 页）“Metropolis coupled MCMC”小节定义后验幂温度，算法步骤
   (3) 的无编号公式给出交换接受率，并说明只从冷链近似原后验；同页末段讨论多副本
   开销。第 410 页讨论并行实现。它是方法实现的原始研究，不是该方法最早提出的论文；
   本项目不移植其树模型、经验温度准则或加速比。

## 单比特翻转加活动／非活动交换：变度数图仍然成立

以下是**本项目的直接推导**。用 \(\ell(x)\) 表示已积分掉 Gaussian 信道后的
未归一化对数后验，\(\pi(x)\propto e^{\ell(x)}\)，\(x\in\{0,1\}^K\)。
当前正噪声方差、\(0<\rho<1\) 的模型使所有支持的后验严格为正。

令 \(\mathcal N(x)\) 是全部单比特翻转，以及全部一次活动／非活动互换产生的
**唯一邻居集合**。两类操作的逆操作均在集合内，所以
\(c(x,y)=\mathbf1\{y\in\mathcal N(x)\}=c(y,x)\)。
若 \(s=\sum_k x_k\)，图度为 \(d(x)=K+s(K-s)\)，不必恒定。
定义

\[
Z(x)=\sum_{z\in\mathcal N(x)}
      \exp\{[\ell(z)-\ell(x)]/2\},\qquad
q(y\mid x)=\frac{c(x,y)\exp\{[\ell(y)-\ell(x)]/2\}}{Z(x)}.
\]

由 Metropolis–Hastings 比值直接得到

\[
\frac{\pi(y)q(x\mid y)}{\pi(x)q(y\mid x)}
=\frac{Z(x)}{Z(y)},\qquad
\alpha(x,y)=\min\{1,Z(x)/Z(y)\}.
\]

对 \(x\ne y\)，接受后的概率流为

\[
\pi(x)P(x,y)
=c(x,y)\sqrt{\pi(x)\pi(y)}
  \min\{Z(x)^{-1},Z(y)^{-1}\}
=\pi(y)P(y,x).
\]

因此本项目图上的该接受率**严格满足详细平衡，度数变化不需要再加一项**。
这利用 Zanella 的平方根 balancing function，但其正文以对称 Markov 基核表述；
这里的 \(c\) 是未按行归一化的对称边权，上式是本项目的适用性证明。
它不等于已经证明本项目满足论文局部极限或高维渐近效率假设。
去掉接受步骤时，提议本身一般以 \(\pi(x)Z(x)\) 为不变权重，而不是 \(\pi(x)\)。

必须区分三种归一化记法：

- 若 \(Z\) 是上面的**邻居总和**，采用 \(\min(1,Z(x)/Z(y))\)。
- 若代码用邻居均值 \(\bar Z(x)=Z(x)/d(x)\)，接受率是
  \(\min\{1,d(x)\bar Z(x)/[d(y)\bar Z(y)]\}\)。
  \(K(x,y)=c(x,y)/d(x)\) 在此变度数图上不关于 counting measure 对称。
- 若 softmax 使用绝对权重 \(e^{\ell(y)/2}\)，归一化项
  \(S(x)=\sum_{z\in\mathcal N(x)}e^{\ell(z)/2}\)，则
  \(Z(x)=e^{-\ell(x)/2}S(x)\)；不能直接用 \(S(x)/S(y)\) 代替接受率。

实际可用
\(\log Z(x)=\operatorname{logsumexp}_{z\in\mathcal N(x)}
[(\ell(z)-\ell(x))/2]\)，比较 \(\log U\) 与
\(\min\{0,\log Z(x)-\log Z(y)\}\)。
均匀目标是一个解析检查：此时 \(Z(x)=d(x)\)，接受率仍为
\(\min\{1,d(x)/d(y)\}\)；未经校正的均匀选邻居会偏向高度数状态。
单比特边保证全支持域连通。\(K\ge2\) 时加入互换边还产生三角形，故该正权有限图
的链非周期；这一结构结论同样不提供可用的有限混合时间上界。

## 多温度副本交换的目标与接受率

本节把上述文献的 Metropolis coupled MCMC / exchange Monte Carlo 具体代入支持后验。
固定 \(1=\beta_1>\beta_2>\cdots\ge0\)，若温度作用于**完整后验**，则

\[
\pi_{\beta_r}(x)\propto e^{\beta_r\ell(x)},\qquad
\Pi(x_1,\ldots,x_L)=\prod_{r=1}^L\pi_{\beta_r}(x_r).
\]

副本内用 \(\ell_r=\beta_r\ell\) 代入前述提议和接受率。
对以相同概率提出正反交换的副本对 \((i,j)\)，

\[
\alpha_{\rm swap}=
\min\{1,\exp[(\beta_i-\beta_j)(\ell(x_j)-\ell(x_i))]\}.
\]

这是乘积目标的 MH 比值；温度归一化常数相消。相邻温度交换也成立。
每个副本内核及每个交换核保持 \(\Pi\) 不变，按固定顺序组合仍保持它不变；
组合核不必整体满足详细平衡。普通后验均值和活动概率只使用 \(\beta=1\) 温度槽的
保留样本，不能把各温度样本直接等权混合。

若改为**只加热似然**，应明确
\(\ell_r(x)=\log p(x)+\beta_r\log p(Y\mid x)\)，交换式中的 \(\ell\)
相应替换为 \(\log p(Y\mid x)\)。两种路径的热端分布不同，不能混用内核与交换公式。
更一般且不易混淆的形式为
\(\log R=\ell_i(x_j)+\ell_j(x_i)-\ell_i(x_i)-\ell_j(x_j)\)。

## 计算成本及有限运行的边界

本项目的成本估计：无缓存时，一次 informed MH 提议需要当前与被提议状态的完整
邻域权重，目标评估量约为 \(O(d(x)+d(y))\)，不能只计算被抽中邻居。
\(K=40\) 时 \(d=40+s(40-s)\)：\(s=4\) 为 184，最大 440。
缓存或矩阵更新可以减少实际代价，但必须保留正确的正反提议归一化；随机截断邻域
后不能直接套用上述 \(Z\) 公式。Zanella §6.4 的计算与统计效率权衡正是相关边界。

多温度方案还需支付全部 \(L\) 个副本的局部更新成本；缓存对数目标后，单次温度
交换的接受率计算只需常数次标量运算。并行能改变墙钟时间，不消除总计算量。
比较需同时报告目标评估次数、时间与后验近似误差；不能把一次 informed MH 步骤
与一个 Gibbs sweep 按同一步数解释成等预算。

详细平衡证明的是目标正确，不证明给定链长已经探索到所有重要支持。局部交换可能
帮助跨越两个单比特更新之间的低概率状态，但不能自动克服所有多用户联合屏障。
Hukushima–Nemoto §III 明示：温度交换与往返都正常，也可能仍未遗忘先前所在区域。
因此接受率、温度往返、链间边际一致均只能作诊断。大规模结论仍需保留有限预算限制；
小规模可继续与完整枚举后验比较。同一温度梯的热副本不是多条独立目标后验链。

本轮没有执行数值详细平衡检验或混合实验，也没有选定温度梯与采样预算。

## v2 补充：Barker balancing function 与 MH 校正

2026-10-15 补充。主任务报告平方根提议的小规模门槛失败，提出保持邻域、目标、预算
和门槛，仅替换提议权重。本次只核对来源与机制，不复算实验、不更改已有失败记录。

**原文定位。** Zanella v1 第 8 页表 1 明列 \(g_B(t)=t/(1+t)\)；同页 §4.1 末段
称其为 Barker choice。§4.1 同时区分 balancing function 与 acceptance probability
function，并说明不存在已经建立的普遍支配关系。§4.2 的比较针对独立二元分量及其
高维极限，不能当成本项目相关支持后验的性能保证。

**本项目代入。** 对 \(\Delta=\ell(y)-\ell(x)\)，使用

\[
g_B(e^\Delta)=\frac{1}{1+e^{-\Delta}}=\operatorname{sigmoid}(\Delta),\qquad
g_B(t)=t g_B(1/t).
\]

因此在原有对称边权 \(c(x,y)\) 下，令

\[
Z_B(x)=\sum_{z\in\mathcal N(x)}g_B(e^{\ell(z)-\ell(x)}),\quad
q_B(y\mid x)=\frac{c(x,y)g_B(e^{\ell(y)-\ell(x)})}{Z_B(x)},\quad
\alpha_B^{\rm MH}(x,y)=\min\{1,Z_B(x)/Z_B(y)\}.
\]

接受后的概率流为
\(c(x,y)\frac{\pi(x)\pi(y)}{\pi(x)+\pi(y)}
\min\{Z_B(x)^{-1},Z_B(y)^{-1}\}\)，关于 \(x,y\) 对称。
该算法使用 **Barker 提议权重加 Metropolis–Hastings 接受步骤**。
若改用 Barker 接受规则，则对完整 MH 比值 \(R=Z_B(x)/Z_B(y)\) 应采用
\(R/(1+R)\)；这不是本次修订。不能把 \(\operatorname{sigmoid}(\Delta)\)
直接当作最终接受概率，也不能因为权重有界就省去 MH 校正。
稳定的对数权重可写为 \(\log g_B(e^\Delta)=-\log(1+e^{-\Delta})\)，
以 logaddexp 计算，再按原方案计算正反邻域的 logsumexp。

**本项目的机制诊断，不是论文对本次失败的结论。** 对平方根权重，邻域中较大的
对数密度差会使某项按指数增长，因此即使 \(\ell(y)>\ell(x)\)，仍可能出现
\(Z(y)\gg Z(x)\)，使 MH 接受率很小。这里没有将其解释为目标分布或详细平衡错误。
在所核对 v1 中，§6.2 第 12–13 页明确描述低概率初态导致几乎全拒绝的段落，针对的是
GB（\(g(t)=t\)），不能拿该段落证明平方根提议也必然如此；本轮没有找到直接分析
“平方根提议从全活动初态发生上述失败”的原文结论。

有界权重提供一个本项目可直接证明的区别：对当前 \(c=1\) 的图，
\(0<Z_B(y)<d(y)\)。若 \(\ell(y)\ge\ell(x)\)，则
\(Z_B(x)\ge g_B(e^\Delta)\ge1/2\)，故

\[
\alpha_B^{\rm MH}(x,y)\ge\frac{1}{2d(y)}.
\]

这个下界只针对**已经提出的非降密度移动的接受概率**，不约束提出该移动的概率，
不保证跨越低概率屏障，也不保证 v2 通过有限预算门槛。它说明此次替换针对的是
无界权重导致的归一化比失衡，有明确机制依据；最终效果仍按原门槛验证。
