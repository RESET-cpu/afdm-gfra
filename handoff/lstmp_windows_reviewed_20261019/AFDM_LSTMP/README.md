# AFDM L-STMP 新网络训练交接说明

更新日期：2026年10月19日，上传前复核版。接收方可以在独立的 Windows 目录中继续本轮训练，无须合并进另一个 AFDM 工程，也无须使用现有三个网络初始化新模型。

Mac 训练已按用户要求停止，进程已退出。已保存一阶 score 预训练第 **1轮、第366次更新、样本游标11712/16384** 的模型、EMA、Adam 状态和进度。默认交接方式是在 Windows 继续这个新网络的断点；该断点来自随机初始化训练，与旧三个网络无关。还没有完成第1轮验证，`best.pt` 目前仍是初始验证候选；**续训必须读取 `last.pt`，不能仅加载 `best.pt`**。


GitHub 交接版本使用独立候选分支，完整代码、数据和第366步断点在该仓库的 `lstmp-windows-reviewed-20261019` Release 附件中。请下载 **AFDM_LSTMP_Windows_reviewed.zip**；GitHub 自动生成的 “Source code.zip” 不含大体积数据和权重，不能代替完整运行包。私有仓库需要登录具有访问权限的 GitHub 账号。上传前审查记录见本目录 `AUDIT.md`。

## 1 交接内容和研究目标

本候选借鉴 Wei 与 Yuan 的 L-STMP，把实际 AFDM 接收机展开为逐层可训练结构，验证联合学习能否补偿实际消息与理想 AWGN 模型之间的失配。预训练完成后，程序自动训练1至5层接收机；每层拥有独立 score 和活动分支。旧的一阶 score、二阶 score、活动分类器只在最后作为冻结对照调用，不参与新网络训练。

这是一套多用户 AFDM 适配，尚无接收机性能结论。第一阶段使用已知相位和已知噪声，属于明确标记的 oracle 诊断；估计相位、估计噪声的配对验证留待这一阶段完成后进行。

参考原文为 [Learned Score-Based Turbo Message Passing for Channel Recovery From Spatially Compressed Measurements](https://arxiv.org/abs/2610.17785)，arXiv:2610.17785v1，2026年10月13日。包内原文位于 `references/lstmp_2610_17785/wei_yuan_2026_lstmp_v1.pdf`，细读记录为同目录 `READING_AND_RETRAINING.json`。

Cai 的 STMP-JADCE 与 Wei 的 L-STMP 有共同来源：前者参考文献[24]、后者[16]均为 Cai–Yuan–Zhang 的 *Score-Based Turbo Message Passing for Plug-and-Play Compressive Image Recovery*。本候选借鉴 [Cai §III-B](https://arxiv.org/html/2506.00581v2#S3.SS2) 的用户信道块与活动分离建模，以及 [Wei §III-D、§V-A](https://arxiv.org/html/2610.17785v1#S3.SS4) 的逐层独立网络联合训练。监督活动分类器与残差方差的结合是本项目的适配，不宣称两篇论文直接给出了这套AFDM算法。

## 2 Windows 安装和启动

将整个 `AFDM_LSTMP` 文件夹复制到一个独立目录，例如 `D:\Research\AFDM_LSTMP`。保留目录层次。建议使用 Python 3.12、NVIDIA CUDA 显卡，并预留至少10 GB磁盘空间供环境、后续权重和结果使用。先用下面的五层前向、反向与Adam更新检查显存；正式训练仍需监控实际峰值；本包没有在真实 Windows/CUDA 机器上运行过。

在 PowerShell 中执行：

```powershell
Set-Location 'D:\Research\AFDM_LSTMP'
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cu128
.\.venv\Scripts\python.exe -m pip install -r requirements-windows.txt
.\.venv\Scripts\python.exe -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CUDA unavailable')"
```

CUDA 12.8 的 PyTorch 2.7.1 安装地址依据 [PyTorch 官方历史版本页面](https://pytorch.org/get-started/previous-versions/#v271)。若驱动或显卡与该轮子不兼容，先按官方页面选择适合的 CUDA 构建，记录实际版本，确保 `torch.cuda.is_available()` 为 `True` 后继续。无需安装 torchvision 或 torchaudio。没有 NVIDIA CUDA 显卡时可安装官方 CPU 轮子，并把下列命令中的 `cuda` 换成 `cpu`。

先检查环境、包内资产、断点恢复、五层反向传播和Adam状态分配：

```powershell
.\.venv\Scripts\python.exe run_windows.py --check --device cuda
```

只有返回检查通过，才开始续训：

```powershell
.\.venv\Scripts\python.exe run_windows.py --resume --device cuda
```

训练在当前窗口运行，同时记录日志。保持窗口和机器运行。入口仅在明确执行 `--resume` 时清除包内的暂停请求，恢复第366次更新之后的训练；`--check` 不会推进或改写正式训练断点。CUDA运行设备单独记录，原始研究配置里的CPU字段保留为Mac来源记录，不需要手工修改配置或哈希。

如果希望完全从第0步重新开始，应另建一个运行目录并重新记录初始化和配置，不能删除这个交接包中的断点后冒充续训。本包的默认入口专用于继续已保存的这次新权重训练。

## 3 查看进度和安全暂停

在另一个 PowerShell 窗口中进入同一目录后执行：

```powershell
.\.venv\Scripts\python.exe run_windows.py --status
.\.venv\Scripts\python.exe run_windows.py --pause
```

`--pause` 请求在训练步、验证微批次或接收机场景边界保存并退出；当前正在推断的场景先完成。随后读取状态，确认 `PAUSED`，再关闭训练窗口或移动文件。暂停后用相同的 `--resume --device cuda` 命令继续。不要通过删除权重、修改测试样本或关闭异常日志来恢复训练。

运行目录固定为 `runs/lstmp_fresh_20261019/`：

| 文件或目录 | 用途 |
|---|---|
| `STATUS.json` | 当前阶段、轮数、步数和损失 |
| `run.log` | 完整日志，包含原Mac记录及后续记录 |
| `history.jsonl` | 验证结果事件 |
| `RUNTIME.json`、`runtime_history.jsonl` | 实际设备、依赖版本和启动历史 |
| `check_cpu.json`、`check_cuda.json` | 对应设备实际执行后的检查报告 |
| `checkpoints/pretrain/last.pt` | 最新score断点，含优化器和EMA |
| `checkpoints/pretrain/best.pt` | 验证集选出的预训练权重 |
| `checkpoints/depth_1/` 至 `depth_5/` | 每个深度的断点、最佳模型和验证记录 |
| `results/test_depth_*.json` | 各深度的独立测试结果 |
| `results/original_test.json` | 同一批输入上的旧接收机对照 |
| `COMPLETE.json` | 整个流程完成及旧资产哈希检查 |
| `FAILURE.json` | 若发生异常，保存原因和调用栈 |

最终测试逐场景保存，续跑会核对模型、数据与运行环境并跳过已完成场景和深度。结果JSON包含 `status`、`identity`、`rows`；新接收机完成后另有 `summary`。中断的验证可能重算，但已完成优化步不会因正常暂停而重复。

首轮每次启动的总时间预算为24小时。达到预算会保存断点并停止，状态为 `TIME_BUDGET_REACHED`；这不是收敛，也不是性能合格。检查记录后可显式续训。Mac的8至10小时估计不能直接套用于Windows，按该机器前几百步和五层检查的实测速度估算。

## 4 采用的结构及与论文的关系

| 环节 | 论文依据 | 本候选实现 |
|---|---|---|
| 先预训练score，再联合训练 | PDF第3页 §III-D | 新AFDM数据，从随机初始化开始 |
| 各层独立NCSN++ | 第4页 §V-A | 每层独立参数，初始化时复制新预训练权重 |
| 逐层增加深度并共同训练已有层 | 第3页 §III-D | 按1、2、3、4、5层训练 |
| 一阶score修正均值 | 第3页 式(11) | 实坐标采用复方差的一半，避免因子2错误 |
| 残差方差替代二阶score | 第3页 图1、式(12) | 使用残差与可学习系数，并明确记录数值约束 |
| 一般AFDM观测矩阵 | 本项目扩展 | 使用实际矩阵的SVD形式LMMSE |
| 未知多用户活动 | 本项目扩展 | 每层新建活动网络，用真实展开消息和活动标签训练 |

NCSN++来自 [Song等官方实现的固定提交](https://github.com/yang-song/score_sde_pytorch/blob/cb1f359f4aadf0ff9a5e122fe8fffc9451fd6e44/models/ncsnpp.py)。许可证、源文件哈希、依赖适配均保存在 `source_experiment/vendor/`。具体骨干宽度和训练超参数由本项目确定，不能写成L-STMP作者的完整复现配置。

一阶score输入为 `[批量, 2, 16, 16, 16]`，第二维分别为实部和虚部；网络内部打包为32个通道、16×16图。基础宽度64，通道倍率(1,2,2)，每级两个残差块，连续Fourier噪声条件，dropout为0，FIR关闭。每层约704万参数。关闭FIR使该配置不依赖CUDA自定义扩展。

## 5 公式与数值处理

观测写为 `Y=A X+N`，其中每列的 `A` 为16×640；`X`按40个用户、每用户16个系数堆叠，另有16×16个观测列。网络用户块与线性矩阵的排列关系由 `data.py` 的 `pack/unpack` 定义，不能只改reshape而不核对复数观测。

对于先验均值 `m` 和复方差 `v`，线性后验均值为

```text
m_post = m + v A^H (v A A^H + sigma_n^2 I)^(-1) (Y - A m)
v_post_ana = v - (v^2 / 640) trace[(v A A^H + sigma_n^2 I)^(-1) A A^H]
```

实现对 `v_post_ana/v` 作有界logit校准，再计算Gaussian外信息。不能替换为论文仅在行正交条件下成立的简式。

一阶score的人工噪声满足每个实坐标标准差 `sqrt(v/2)`。预训练目标和均值更新分别为

```text
DSM = mean[(sqrt(v/2) * s_theta(r,v) + epsilon)^2]
conditional_mean = r + exp(alpha_parameter) * (v/2) * s_theta(r,v)
p = sigmoid(activity_logits)
X_hat = p * conditional_mean
```

活动网络接收实际消息、方差和score产生的均值；真值只用于损失。活动输出是直接监督的后验分类器，不被解释成在任意有色消息下仍成立的AWGN似然比。

本项目的原始残差方差为

```text
d = exp(beta_parameter) * (||Y-A X_hat||_F^2 - 16*256*sigma_n^2)
                         / (256*||A||_F^2)
```

代码先以温度 `0.02*v` 的softplus把该量变为正值，再以tanh使反馈后验方差严格小于 `0.95*v`，保证外信息精度为正。这是项目数值适配，并非论文给出的精确后验方差公式。每层记录负原始方差、接近上界及超出预训练噪声范围的情况。

残差不能识别 `A` 零空间中的信道误差；学习系数也不能保证消息变成独立白高斯噪声。联合训练后的网络作为可训练的恢复映射使用，不再未经检验就视为精确的先验score或MMSE去噪器。最后一层的反馈方差不会影响该深度的最终均值损失，其beta在加入下一层之后才获得该反馈路径上的训练梯度。因此最终第五层beta不受损失监督，其反馈方差也不能作为已经校准的后验误差证据；它不影响第五层输出。

## 6 数据与训练配置

场景采用项目完整物理AFDM生成器，40个候选用户，16帧、16根天线和16×16信道块。预训练从活动掩码之前的候选信道中均匀抽样，每个物理场景抽取4个用户，不按能量、方向或接收机误差筛选。

训练集独立确定的固定尺度为 **0.2657475291508846**。不逐用户归一化，不使用验证或测试集重新估计尺度。非活跃用户的零信道由展开阶段的活动模型和监督处理。

| 阶段 | 训练 | 验证 | 测试 |
|---|---:|---:|---:|
| score预训练 | 16384个候选信道，4096个场景 | 2048个候选信道，512个场景 | 不在此阶段使用接收机测试集 |
| 接收机展开 | 512个物理场景 | 64个物理场景 | 64个物理场景 |

接收机SNR按场景索引在−5、0、5、10 dB之间均衡分配，使用接收信号功率定义。每个测试SNR只有16个场景，属于首轮训练验证预算；不能据此宣称已经得到大规模可靠性结果。

| 配置项 | 当前数值 |
|---|---|
| 预训练复噪声方差 | 0.001至100，对数均匀采样 |
| 预训练最大／最小轮数 | 40／10 |
| 预训练验证耐心 | 6轮，相对改善阈值0.001 |
| 预训练批量／微批量 | 32／8，梯度累积保持批量32 |
| 预训练学习率 | 0.0002余弦下降至0.00002 |
| 优化器／EMA／梯度裁剪 | Adam／0.995／1.0 |
| 每个展开深度最大／最小轮数 | 12／4 |
| 展开验证耐心 | 4轮，相对改善阈值0.001 |
| 展开网络／校准学习率 | 0.00002／0.001 |
| 展开训练批量 | 每步1个完整场景，40个用户，网络微批量8 |
| 损失 | 有效信道NMSE加0.1倍活动BCE |
| 层间损失权重 | 先前各层0.2，当前最后一层1.0，再除以权重和 |
| 活动判决阈值 | 0.5 |

最终接收机深度预先指定为5层，1至4层结果作为消融对照；不能依据测试集再选择深度。所有深度完成训练和验证选模型后才生成、读取测试集。种子范围和全部配置以 `source_experiment/config.json` 与 `MANIFEST.json` 为准。GPU显存不足时优先另行记录并降低微批量，保留有效批量和目标函数；不可直接修改已冻结快照绕过哈希检查。任何配置修改应形成独立候选或明确的迁移记录。

## 7 移植检查和可复现边界

最终交接审查结果见 `AUDIT.md`。Mac端旧对照的复数矩阵运算出现NumPy运行时警告；相关输出均有限。对两个警告位置做独立张量收缩比较，最大相对差为7.87e-15（容差3e-12）。这仅验证本次检查输入，尚未确定警告根因；保留警告记录，未修改冻结源码或关闭警告。目标Windows仍需实机检查。

Mac端已通过：复数打包核对、一般矩阵LMMSE与精确计算比较、残差方差因子核对、五层独立参数检查、各层score和活动分支的有限非零梯度检查、优化器保存恢复检查。线性均值相对误差约为 `5.6e-8`，优化器检查最大差为0。

交接包使用相同模型、数据、优化器和样本顺序；Windows交接版增加设备选择、完整训练检查、日志、进程锁和UTF-8启动，并修正验证暂停、最终测试续跑、数据核对和计时；没有改变模型公式或训练配置。修改前的Mac训练入口和清单保存在 `provenance/mac_train.py.txt`、`MAC_ORIGINAL_MANIFEST.json`，差异记录在 `WINDOWS_PORTABILITY.json`。跨操作系统和CPU/CUDA训练不保证逐位相同，应比较有统计意义的验证指标，不能要求每一步loss完全重合。

交接包本身已在Mac CPU执行 `--check` 并通过：192项固定源码、资产和数据核对通过，恢复第366步模型、EMA与Adam后完成一次仅在内存中的更新，五层score与活动分支梯度均有限且非零，五层Adam状态分配与内存更新通过，所有断点哈希保持一致。报告位于 `runs/lstmp_fresh_20261019/check_cpu.json`；这不是正式训练结果。

`--check` 必须在Windows本机实际运行。包内的CPU检查只能证明在当前Mac环境可以加载、恢复和计算，不能代替Windows/CUDA验证。不要仅因为出现训练loss下降，就宣称接收机性能改善。

## 8 训练完成后的交付与判断

交回 `MANIFEST.json`、运行设备记录、检查记录、所有阶段的验证历史、各深度最佳模型、完整测试结果和旧接收机对照。应按相同测试场景比较：信道NMSE、漏检数、误报数、迭代或层数、运行时间，以及方差异常记录。

目前程序自动保存各场景的NMSE和检测错误；正式汇总时需按SNR分别统计，并使用物理场景作为配对单位。不得根据测试结果回头选择学习率、深度或修改测试集。若需要进一步调参，回到训练和验证集，保留本轮全部结果。

## 9 给 Windows 端编码代理的执行要求

1. 先阅读本说明、论文细读记录和 `MANIFEST.json`，确认当前只是新候选，不切换冻结主线。
2. 在独立目录运行环境检查。检查失败先查具体错误，保留日志；不修改模型公式来掩盖环境问题。
3. 运行 `--check --device cuda`，通过后才 `--resume --device cuda`；恢复本轮新网络，不载入旧权重作初始化。
4. 保持数据划分、尺度、种子、测试隔离和训练预算。记录设备及依赖版本；修改配置前建立独立记录。
5. 监控状态、损失、验证趋势及非有限值。测试失败和不利样本全部保留，不自动提高容差。
6. 训练结束先报告实际结果，不把L-STMP论文的收益、40倍计算量比较或AWGN叙述当成本项目已验证结论。
7. 不初始化Git、不恢复原项目Git自动快照；不覆盖旧网络、冻结副本或其他线程资产。

## 10 文件完整性

`PACKAGE_FILES_SHA256.json` 用于首次复制或解压后的文件核对。训练开始后，断点、状态和日志会正常变化；不能把这些变化误报成原始包损坏。源码及固定资产由运行入口按 `MANIFEST.json` 检查。

本包包含旧三个权重及其配置，只为最后在同一测试集上运行冻结对照；它们与新模型的初始化、预训练和展开训练路径分离。
