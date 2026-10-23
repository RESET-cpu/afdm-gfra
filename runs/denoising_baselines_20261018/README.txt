现有 baseline 的 500 场景独立去噪实验

用户授权范围：复用 SOMP、GAMP-SBL、GNN-ASPL、Off-grid SBL，对同一批 500 个场景运行六档噪声的直接信道去噪，并合并已有 Proposed 5k/50k 结果。

运行目录包含：
- runtime/：191 个源码、配置与 GNN 权重文件的独立副本；身份见 SNAPSHOT.json。
- adapter.py：逐个候选信道使用恒等观测算子，转换到物理尺度，调用原生求解器，再还原评分坐标。
- run.py：输入核验、六进程调度、逐场景结果保存、汇总、绘图。
- verify_adapter.py：与原生接收机入口进行低/中/高三档 SNR 的 12 项输出与停止状态对照。
- report.py：完整结果的文字说明和 SNR–NMSE 宽表。
- preflight.log / adapter_verification.log / formal.log：实际执行日志。

状态与结果：../../results/denoising_four_baselines_20261018/STATUS.json
正式输入：../../results/local_baselines_20261018/formal/channel_denoising/
Proposed 来源：../../results/denoising_merged_20261018/

预检场景为预先固定的 scene000，六档条件均完成四个候选信道和四种方法，共 96 次推断。正式运行直接保留该场景；未按性能选择。
原生入口验证与适配输出的一致性只验证执行适配，不证明权重在新观测任务中的泛化性能。

配置与运行边界：
每进程的 PyTorch/数值库单线程，正式最多六个场景进程；每个场景内部逐条件、逐方法、逐信道运行。使用已知 AWGN 方差。
算法核心、字典、GNN 权重和停止规则保持原配置。全部警告和达到迭代上限的记录保留，不以效果筛样。
GAMP 保留其原生内部噪声估计。输出仅评价信道估计，活动与相位前端不进入此任务。
每场景完成后保存紧凑 NPZ 和完整指标/输入身份 JSON。首场景额外保存全部预测。失败记录原样保存，不自动重新运行失败场景。

复现（从项目根目录）：
.venv/bin/python runs/denoising_baselines_20261018/run.py preflight
.venv/bin/python runs/denoising_baselines_20261018/verify_adapter.py
.venv/bin/python runs/denoising_baselines_20261018/run.py run --workers 6
.venv/bin/python runs/denoising_baselines_20261018/report.py

运行中的脚本和快照不可修改；PLAN.json 绑定其哈希。需要改变设置时建立新批次。
