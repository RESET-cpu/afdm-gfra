# 9900X CPU 实验交接

本包承担用户数和跨信道两组实验，四种方法均为 Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP。用户数为 5 个条件 × 500 场景 × 4 方法；跨信道为 4 个模型 × 6 档 SNR × 500 场景 × 4 方法。已完成的首场景结果随包移交，正式运行验证后复用。Mac 继续执行其余实验，5080 GPU 执行 Proposed。

## 环境

建议 Python 3.12。为避免改变现有 Proposed 环境，在包目录创建单独虚拟环境。下面命令需要目标电脑能够下载依赖；本地打包过程没有安装或下载它们。建议保留完整解压路径与所有输入文件。

CPU PyTorch 安装命令依据 [PyTorch 官方 2.7.1 历史版本说明](https://pytorch.org/get-started/previous-versions/#v271)。依赖版本与本地验证环境一致，目标机仍需完成下述 smoke 检查。

Linux：

```bash
cd /path/to/cpu_9900x_package
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements-cpu.txt
```

已选运行环境为 Linux，或 Windows 的 WSL2。Windows 使用 WSL2 的 Ubuntu/Linux 终端，在 WSL 内按上面的 Linux 命令创建环境与安装依赖。例如解压到 WSL 家目录的 `~/experiments/cpu_9900x_package`，不要复用 Windows Python 虚拟环境。若已安装 WSL，可从 PowerShell 输入 `wsl` 进入 Linux 终端。WSL 的安装与发行版管理由目标电脑自行完成，本包不修改系统设置。

当前不支持原生 Windows Python：冻结接收机把源码相对路径纳入配置签名，Windows 的反斜杠会使冻结签名不一致。入口会明确提示使用 WSL，保持冻结源码不变。WSL 和 9900X 尚未实机验证。

不需要安装项目包或设置 PYTHONPATH；入口根据自身文件位置定位所有资产。设备固定 CPU，每个进程限制 PyTorch 与数值库为单线程。包里的 Proposed 源码和配置作为冻结依赖保留，但不包含 Proposed 权重，也不执行 Proposed。

## 完整性检查与小规模检查

先校验全部保存输入（共 14,500 份条件场景）、源码、配置、GNN 权重及继承结果：

```bash
python run_cpu.py check --experiment user_count
python run_cpu.py check --experiment cross_channel
```

接着在两个实验各选首场景一个条件真实执行相位估计和四个 baseline：

```bash
python run_cpu.py smoke --experiment user_count --conditions 0
python run_cpu.py smoke --experiment cross_channel --conditions 0
```

每次 smoke 写入新的 `results/smoke_<实验>_<时间戳>`。它读取正式输入并实际推断，不因正式目录已有首场景而跳过，也不会覆盖正式结果。省略 `--conditions 0` 会运行首场景全部条件；跨信道有 24 个条件，因此完整 smoke 比单条件慢。小规模成功要求命令正常退出且对应 `SMOKE.json` 为 COMPLETE。这里未宣称已经在 9900X 或 Windows 上验证。

可从另一个工作目录运行，输入与结果仍定位到包内：

```bash
cd /tmp
/path/to/cpu_9900x_package/.venv/bin/python /path/to/cpu_9900x_package/run_cpu.py smoke --experiment user_count --conditions 0
```

Windows 的 WSL 终端同样使用 Linux 完整路径。带空格的路径用双引号括起。

## 正式运行

先通过完整性检查与 smoke，再分别运行：

```bash
python run_cpu.py run --experiment user_count
python run_cpu.py run --experiment cross_channel
```

两条命令可以放在两个终端同时执行，最多两个单线程进程；9900X 的安全并行度未实测。不要对同一实验目录同时启动多个进程。`RUNNING.lock` 防止重复写入。每个实验按场景顺序执行，四种方法共用一次相位估计。第一次正式运行会保留 `RUN_PLAN.json`、运行环境和底层数值库信息。

若只想先推进两个场景：

```bash
python run_cpu.py run --experiment user_count --max-scenes 2
```

该命令会跳过已验证的首场景，推断第二场景；正式计划仍为 500 场景，不会把子集误标成完成。随后原正式命令可继续剩余任务。

正常中断后可用同一命令继续，已完成且哈希一致的方法不重算。失败会写入 FAILED 记录并停止，不会静默重试或移除不利样本。先保留故障目录并调查，再决定恢复方法。若系统断电留下 `RUNNING.lock`，确认该实验确实没有运行进程后再手动删除锁；不要直接删失败记录来伪装通过。

## 预检结果与停止状态

随包继承的首场景共有 116 份方法结果，其中 29 份 Off-grid SBL 结果均达到既定 120 轮预算。它们保留为有效的有限迭代输出，不能称为满足原生收敛条件。继续使用原上限、容差和判决阈值，不根据测试曲线调参。矩阵运算警告及停止原因保留在原始记录中；数值非有限或推断失败会报错并留档。

包的本机核验覆盖固定输入与结果身份、源码/配置/权重、独立小规模重放。目标 9900X/Linux/WSL2 尚需运行上述 check 和 smoke；不同 CPU 的浮点输出不承诺逐比特一致，但读取的测试数组必须满足同一份哈希身份。

## 输入配对与结果交回

- `inputs/<实验>/PLAN.json` 是本地原正式计划的逐字节副本；旧计划包含不随本 CPU 包分发的 Proposed 权重哈希，因此入口用独立 `SOURCE_MANIFEST.json` 校验实际包资产，并对所含冻结文件逐一比对旧计划。没有改写原计划哈希。
- `inputs/INDEX.json` 固定每份 `CASE.json` 的哈希；每份 CASE 固定 `public.npz`、`truth.npz` 的文件哈希及公共输入数组哈希、seed、参数、生成记录。运行入口不重新采样测试观测。
- `public.npz` 含 observation、pilot、activity_prior 和占位 noise_variance=1；占位值不表示已知真实噪声。真值单独存储，仅用于评分。
- `results/<实验>/sceneNNN/conditionNN/PAIRING.json` 绑定公共输入、估计相位、条件算子及单独真值。5080 Proposed 应直接读取这些保存的观测与估计相位/算子，避免跨平台仅凭相同种子或重新估计相位导致比较失配。
- 已完成首场景由 `INHERITED_RESULTS.json` 固定文件与原计划身份，正式入口验证其输入及 PAIRING 后复用。新结果和继承结果的环境/耗时应分别保留；Mac 与 9900X 的运行时间不能直接用作算法速度排名。
- 回传整个 `results/user_count` 与 `results/cross_channel` 目录，保留 `RUN_PLAN.json`、`INHERITED_RESULTS.json`、`environments`、逐场景结果、PAIRING 及相位文件。同时保留 `SOURCE_MANIFEST.json` 和 `inputs/INDEX.json` 以核对版本。不要只回传截图或平均值。

随时汇总已完成数量：

```bash
python run_cpu.py summarize --experiment user_count
python run_cpu.py summarize --experiment cross_channel
```

汇总写 `SUMMARY.json` 与 `STATISTICS.csv`；正式 500 场景全部完成后生成 `comparison.png` 和 `comparison.pdf`。未完成时返回非零状态并明确标为 INCOMPLETE，不画成完整曲线。AER 使用合并错误计数，NMSE 使用合并信道误差与能量，不是逐场景 dB 简单平均。

汇总中的 `inherited_completed_results` 计移交前已完成的结果，`completed_by_portable_runner` 计本入口新完成的结果；原有 `reused_results` 字段保留原实验的历史结果复用口径。
