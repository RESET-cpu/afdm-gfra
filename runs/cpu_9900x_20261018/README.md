# 9900X CPU 实验

本目录是 2026-10-18 冻结的用户数和跨信道 baseline 实验，使用 Linux 或 Windows WSL2。Mac 继续其他 baseline，5080 执行 Proposed。

代码、配置、GNN 权重、计划和校验清单位于 `package/`。14,500 份固定测试输入和 116 份已完成结果保存在本仓库的 `cpu-9900x-20261018` Release 附件中。下载器自动校验并解压到正确位置；剩余 57,884 次推断由 9900X 完成。

## 下载

目标电脑需有 Python 3.12 和 GitHub CLI `gh`。用能访问本私有仓库的账户登录，再下载仓库及配套输入：

```bash
gh auth login
gh repo clone RESET-cpu/afdm-gfra
cd afdm-gfra
python3.12 runs/cpu_9900x_20261018/download_inputs.py
```

已经下载仓库时，只需进入已有仓库并执行最后一行。下载中断后可重跑；已经校验的附件会复用。请预留至少 17 GB 空间容纳数据附件与解压后的输入，正式结果还会继续占用空间。

## 先检查，再正式运行

```bash
cd runs/cpu_9900x_20261018/package
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements-cpu.txt
python run_cpu.py check --experiment user_count
python run_cpu.py check --experiment cross_channel
python run_cpu.py smoke --experiment user_count --conditions 0
python run_cpu.py smoke --experiment cross_channel --conditions 0
```

两组 smoke 完成后，在两个终端分别运行，每个终端先激活上述虚拟环境：

```bash
python run_cpu.py run --experiment user_count
python run_cpu.py run --experiment cross_channel
```

完整恢复、汇总、停止规则、与 5080 配对及交回说明见 [README_9900X.md](package/README_9900X.md)。本机已验证全部输入并完成 8 次小规模推断；9900X/Linux/WSL2 仍需上述实机 smoke。Off-grid SBL 达到 120 轮预算的输出保留原停止状态，不能表述为满足收敛条件。

这是独立冻结副本。使用本目录的 `run_cpu.py` 与保存输入，保持原源码、配置、权重、种子和数组身份；不同处理器不要求浮点结果逐比特相同。
