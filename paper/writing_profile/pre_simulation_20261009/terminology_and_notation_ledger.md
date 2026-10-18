# 术语与符号

专业术语的项目统一记录位于 [docs/TERMINOLOGY.md](../../../docs/TERMINOLOGY.md)。此表约束本稿II–V的含义，专业名称使用已核对原词；常规英语连接句不作为新术语登记。

| 用词/符号 | 原文位置 | 本稿含义 |
|---|---|---|
| AFDM; DAFT; chirp-periodic prefix | C07 II-B、III-A，(15)–(19) | 使用原定义；连续延迟算子另列波形假设 |
| array response vector | C10 II-B/C，(2)–(8) | M维未归一化UPA响应，范数平方M |
| multiple measurement vector | C08 III-A，(11)–(12)附近；C06 III-C | Q×KN共享测量矩阵，MN测量向量 |
| posterior mean; MMSE denoiser | C09 III-C，(19)–(22) | 在明确指定的工作后验/局部查询后验下定义 |
| extrinsic message; Gaussian site | C01 III；Minka 2001 §§2–3 | 高斯自然参数相减；site有正精度 |
| denoising score matching | C12 §2/4.1；C03 III-A(14) | 实坐标中的方差加权score回归 |
| trace of second-order score | C13 §4.2，Corollary4.2(15)；C01 IV-C | 本网络只监督全坐标平均，有限教师时对应其条件MSE |
| conditional mean squared error | C01 IV-A均值/方差；C13有限低阶误差；项目THEORY A3 | 给定R,v及active时Fθ的均方误差，用公式直接描述 |
| density ratio; class-probability estimation | C14 §3，(6)–(8)，§4.2 | q1/q0和活动后验；BCE最优logit关系 |
| binary cross-entropy | C04 IV-D；C14 §2–4的log loss | 标量logit分类损失 |
| damping | C01 V-B；C08 Algorithm1 | η为新消息权重，不新增算法名 |
| computational complexity | C04 V-E；C06 IV-B | 根据本实现算子和网络调用计数 |

符号保护：ν_k表示物理Doppler；实高斯方差改记v_R=v/2，以避免原稿ν=v/2与ν_k含义冲突。ρ为公开接入边缘，π_tr为分类器训练类先验，p_k为迭代活动概率。D=MN²。Fθ为当前网络均值，μ_k为当前site与查询合成的条件均值，二者只在接受site时相等。τ̂_k、τ、t_k、t̄_X依次为单用户误差读数、共享误差、当前条件高斯方差、混合后验平均方差。
