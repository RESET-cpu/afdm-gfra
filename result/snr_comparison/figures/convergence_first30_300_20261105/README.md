# 前 30 个配对场景的收敛图

固定使用场景 0–29、SNR = 0 dB、已知相位、观测估计噪声。每种算法每个场景均实际执行 300 次迭代，共核验 90 份完整结果。按作者 2026-11-06 要求，仅绘制前 150 次迭代的 NMSE，保留 GP-MP、STMP 和原基础配置 Off-grid SBL (7)。NMSE 按总误差能量除以总活动信号能量后转为 dB。不平滑，不补齐，不按结果筛选场景。

作者已采用本图替换论文收敛图，并停止原 50 场景批次。图例使用 Off-grid SBL，不标注预算编号；底层仍为原 7 点基础配置。所选 90 份结果的完整 300 轮数据仍保存在原实验中。

本脚本仅读取已保存结果，不运行推断。论文图由统一入口 `src/evaluation/plots/render_paper.py --figures convergence` 生成。

复现：在仓库根目录运行 `.venv/Scripts/python.exe -X utf8 -B src/evaluation/plots/convergence_first30_20261105.py`。
