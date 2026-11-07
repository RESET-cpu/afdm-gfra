# Abstract

This paper investigates grant-free random access in low Earth orbit
satellite Internet-of-Things systems without global navigation satellite
system (GNSS) assistance. To handle large differential delays and
Doppler shifts across devices, we propose a multi-frame affine
frequency division multiplexing (AFDM) transmission scheme and analyze
its input-output relationship. Based on this model, we learn a
score-based generative prior directly from AFDM effective-channel
samples, without imposing sparse or grid-aligned channel assumptions.
The finite-dimensional, structured multi-frame AFDM observation model
may cause a mismatch between denoiser-input errors and white Gaussian
noise used for training. We therefore train the channel
denoiser using colored Gaussian noise with different covariance matrices.
The learned prior is then incorporated into a message-passing (MP)
receiver with two modules: multi-frame linear estimation (MFLE), which
suppresses inter-user interference; and generative-prior-aided joint
denoising (GPJD), which performs minimum mean-squared error (MMSE)
denoising.
GPJD combines channel posterior mean and variance estimates with posterior
probabilities of activity from a learned density-ratio estimator to account
for activity uncertainty in channel estimation.
The two modules iteratively exchange soft information for joint activity
detection and channel estimation (JADCE). Numerical simulations demonstrate
that the proposed receiver
outperforms the baseline receiver in activity detection and channel
estimation.

# 摘要

本文研究无全球导航卫星系统（GNSS）辅助的低轨卫星物联网免授权随机接入。针对设备间的大差分时延与多普勒频移，提出多帧仿射频分复用（AFDM）传输方案，并分析其输入输出关系。在该模型基础上，直接从AFDM有效信道样本中学习基于得分的生成式先验，无须对信道施加稀疏或网格对齐假设。有限维、结构化的多帧AFDM观测模型可能导致去噪输入误差与用于训练的白高斯噪声之间的失配。因此，采用不同协方差矩阵的有色高斯噪声训练信道去噪器。随后，将所学先验引入包含两个模块的消息传递（MP）接收机：多帧线性估计（MFLE）模块用于抑制用户间干扰；生成式先验辅助联合去噪（GPJD）模块进行最小均方误差（MMSE）去噪。GPJD将信道后验均值与方差估计与学习得到的密度比估计器提供的活动后验概率相结合，以在信道估计中考虑活动不确定性。两个模块迭代交换软信息，以完成联合活动检测与信道估计（JADCE）。数值仿真表明，所提接收机在活动检测和信道估计方面优于基准接收机。

**关键词：**仿射频分复用；免授权随机接入；联合活动检测与信道估计；基于得分的生成模型。
