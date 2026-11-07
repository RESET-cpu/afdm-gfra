# 线性模块协方差接口核验

2026-10-24，用户要求检查当前线性观测模块能否给出新一阶去噪器需要的 C。

结论、公式及局限见[报告](../../../../paper/docs/STMP_LINEAR_COVARIANCE_INTERFACE_20261024.md)。

- `audit.py`：小尺寸复数矩阵代数与 48 个已有公开输入首轮检查；只访问公开观测、导频、先验活动率和保存的首轮查询，不读取真值。
- `PLAN.json`：范围、输入计划哈希与保护文件哈希。
- `RESULT.json`：数值核验与完整条件列表。
- `RECORDS.json`：全部 1920 个用户条件的谱、投影误差及来源分组。
- `run.stdout.log`：本次执行输出。
- `benchmark.py` / `BENCHMARK.json`：现有尺寸、单 CPU 线程下，复用 SVD 的每轮 40 用户协方差构造与训练族投影微基准，三份公开输入各计时 100 次。中位耗时约 0.99–1.01 ms，原线性更新约 5.65–6.10 ms；不含 GPU 预条件、网络、传输或反馈导数，非完整接收机延迟。

复算命令：`.venv\Scripts\python.exe -B result/snr_comparison/data/linear_covariance_interface_20261024/audit.py`。

没有网络调用、训练变化、正式接收机或新增 Monte Carlo 场景。这里的 PASS 表示公式、复现和保护哈希检查通过，不是误差协方差已校准或活动检测改善。
