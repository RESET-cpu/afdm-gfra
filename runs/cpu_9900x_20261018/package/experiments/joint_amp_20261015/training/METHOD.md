# 完整用户网络与预先固定的训练协议

## Material Passport

- 工作模式：academic-research-suite / experiment-agent / code_runner，独立网络设计与训练已获用户授权。
- 数据访问：本项目已有物理训练与验证信道 bank；不读取接收机测试真值，不加载已有学习权重。
- 产物范围：完整用户联合均值及活动证据网络；闭环接收机另行验证。
- 证据状态：本文件固定实现与选择准则；训练结果另存每次运行目录。有限网络的最优性、活动概率校准与闭环 AWGN 近似均不预先宣称成立。

## 坐标与总体目标

每个活跃物理信道先除以冻结总体尺度 `0.2647966452702405`，对已知 4×4 阵列作固定单位 beam DFT，然后对完整 16×16 AFDM 矩阵作现有可逆 time-lag-DFT 表示。输入是 `[B,2,16,16,16]`，依次为用户、实虚、波束及两个空间轴。全体16束共同进入网络，不作跨用户运算。

给定复方差向量 `v[B,16]`，每个实坐标的噪声方差为 `tau_m=v_m/2`。在训练坐标中令 `a∈{0,1}`、`r=a x+epsilon`、`epsilon∼N(0,T)`，T 对应各束的 tau，重复到实虚及空间坐标。活跃信道总体实方差 `q=1.0004404181394917/2`，不乘活动概率。

第一头 F 的目标为 `E[x|r,a=1,V]`。第二头 ell 在两类等权的 binary cross entropy 下具有总体最优值 `log p(r|a=1,V)−log p(r|a=0,V)`。对公开先验 rho，`p=sigmoid(logit(rho)+ell)`，完整均值 `D=pF`。因此 score 定义为 `s=T^{-1}(D−r)`，按束作 `/(v_m/2)`。

该网络训练的是活跃条件去噪目标和分类目标的和，不将其称作活动混合 DSM 损失。单独第一头的加权 clean MSE 与活跃条件 denoising score matching 等价：若 `s_a=T^{-1}(F−r)`，则第 j 坐标的 `lambda_D,j(F_j−x_j)^2=lambda_D,j tau_j^2(s_a,j+(r_j−x_j)/tau_j)^2`，其中 `lambda_D,j=1/c_out,j^2`。理想的两个头共同给出混合先验均值；有限网络并不因此满足 `F=T grad_r ell`，训练结束后将描述这一偏差。

专业术语来源沿用 `docs/TERMINOLOGY.md`：EDM 的 network preconditioning 见 Karras等2022 p.3 Table 1、式(2)–(3)、§5式(7)–(8)；score-based MMSE denoising/denoising score matching 见 STMP v2 p.3式(14)、(18)–(19)；density ratio estimation 与 class-probability estimation 见 Menon–Ong §3式(6)–(8)、§4.2式(16)–(17)。双头组合及以下网络宽度和采样比例为本项目明确给出的实现选择，不是引用论文中的算法名称。

## 网络与导数

2×16 束打包为32通道，96通道输入卷积、4个双卷积残差块、连续 log-noise 条件仿射、SiLU激活。无 batch normalization、无 dropout、无跨样本统计。每束采用 `c_skip=q/(tau+q)`、`c_out=sqrt(tau*q/(tau+q))`、`c_in=1/sqrt(tau+q)`。噪声编码包括各束的 `log(tau)/8` 及固定 Fourier 特征。

F 输出32通道残差并还原完整形状。ell 读取共享特征的空间均值、二阶矩、每束标准化输入能量和噪声编码，输出每用户一个值。输出头从零初始化，其余参数随机初始化。初始 F 为 Gaussian 线性均值，初始 ell=0；没有读取任何旧网络权重。

对输入求导时固定V与公开rho，必须保留 `dD=p dF+F dp`。网络不 detach 任何一项；实际 Onsager 导数由接收机对完整实际 `pF` 映射计算。有限模型的 score 不自动保证为某个正规化密度的梯度。

## 数据和噪声采样

仅使用 `data/proposed/train_channel.npy` 的50000个候选信道和 `validation_channel.npy` 的5000个候选信道，并核对原始hash及身份文件。训练12500个、验证1250个物理场景无交叉。可逆变换的训练缓存只存于本次 run 目录。

每步64个活跃用户、64个全零用户。两类使用完全相同的V集合，各自独立采样噪声；BCE不做rho加权。活跃样本施加独立均匀公共复相位，这是已声明物理先验的合法增广。

复方差范围 `[0.001,100]`，在查看验证结果前固定：50%用户16束共同log-uniform方差，25%用户各束独立log-uniform方差，25%用户共同log-uniform中心加各束±半个十进制数量级的均匀log偏移，最终裁到已声明支持。该裁剪仅是训练标签生成规则；网络和接收机接口不以此隐式裁剪输入方差。

损失为活跃样本全部坐标 `mean[(F−x)^2/c_out^2]` 加全部128样本的平衡BCE，两项系数均为1。rho仅用于推断的先验修正。Adam初始学习率3e−4，梯度范数上限10，固定验证风险停滞时学习率减半，下限1e−5。

## 固定验证与停止规则

每1000步在均匀覆盖验证bank的96个完整用户上评估。共同方差和有限spread各有五个log噪声档 `[.001,.01]` 至 `[10,100]`，另含一个各束独立全支持条件；使用固定噪声种子及成对活跃/零输入。各共同方差档权重0.1，各spread档0.05，独立条件权重0.25，匹配训练采样权重。

选权标准是固定验证上、rho=0.1时的混合 clean MSE 按 `1/c_out^2` 加权，再按已固定条件权重求和。比较同时保留 full/active/inactive MSE、条件F误差、线性和零基准、balanced BCE、prior-corrected BCE、Brier、漏检、虚警与AER。最终512个验证用户以另一固定噪声种子作完整报告；这仍属于模型选择bank的验证报告，不冒充独立测试。

上限63342步，每步64活跃样本，约对应旧训练的81×782次更新。30000步前不早停；此后连续10次验证没有相对至少0.2%的风险改进可按预定准则早停。保留10k、30k、63k及最终阶段的当前权重与截至该阶段的最佳权重。是否达到plateau和是否仅达到预设上限分别报告。

## 运行与交付

先做CPU64步小批和MPS100步完整批smoke及吞吐测量，记录样本独立性、CPU/MPS均值与JVP一致性、完整链式导数、有限差分及score换算。失败运行保留单独目录。正式训练从独立随机种子重新初始化。

每次运行保存PID、开始时间、硬超时、100步心跳、日志、固定验证曲线、数据和源码hash、环境、best/last及可恢复优化器/随机状态。运行期间由代理检查alive与进度。异常明确记录后再按已授权范围修复或续跑，禁止删除不利结果。

`load_checkpoint(path,device='cpu')` 返回 `(model,payload)`；schema=`afdm-joint-score-checkpoint-v1`。payload包含 `state_dict`、`network`、`recipe`、step和验证结果，其中recipe提供scale、noise_support、representation、input_shape及完整训练规则。`components(r,v,rho)` 返回 `conditional_mean`、`log_likelihood_ratio`、`probability`、`mean`；`forward`仅返回mean，`score`返回实坐标score。
