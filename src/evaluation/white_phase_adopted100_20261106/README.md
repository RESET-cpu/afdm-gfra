# 白噪声估计相位：采用 100 场景消融前置

本入口只落实作者将前置消融从每档 500 改为每档 100 场景的决定。原 `white_phase_frontend_20261106` 包、PLAN、权重、接收机、相位初始化和逐输入保存/评分逻辑保持。

`run.py` 从冻结执行器复制，仅改门控导入、同一接收机与报告的绝对导入、子进程模块路径及重复执行检测。`gate.py` 核对 adopted100 的完成收据、2400 行配对覆盖、汇总/来源哈希和进程退出；不会把原 500 场景计划记成完成。白噪声已知相位的 6000 份前置要求保持。

实际执行入口为 `python -m evaluation.white_phase_adopted100_20261106.run inspect` / `coordinate`。使用项目 Python，`PYTHONPATH=D:\afdm-gfra\src`。后续恢复仍须先检查进程、锁、失败、暂停和逐输入输出，然后使用 `coordinate --resume`；不得覆盖或重跑完成项。

修订清单、原始源码哈希、差异、CPU 针对性检查和前置来源复核保存在结果目录的 `gate_adopted100_20261106/`。GP-MP-EP 本身仍为原定 1000 场景、六档 SNR、6000 份推断；预检通过与正式启动另以 PREFLIGHT、START 和实时状态为准。
