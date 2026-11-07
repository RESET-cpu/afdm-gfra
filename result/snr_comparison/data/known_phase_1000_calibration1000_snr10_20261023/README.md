# 1000 场景比较与 1000 场景门限校准

按用户 2026-10-23 的最新要求：所有后续实验统一采用前1000个MC场景。
本批次 SNR 为 −4、−2、0、2、4、6、8、10 dB，已知相位、估计噪声。

| 用途 | 固定场景编号 | 方法 | 结果数 |
|---|---|---|---:|
| 正式结果比较 | 0–999 | STMP、Off-grid SBL、GNN、GAMP、SOMP | 40000 |
| 门限校准 | 1000–1999 | 四个 baseline | 32000 |

每个 baseline 拟合一个固定标量门限，八档 SNR 共用；目标是校准集上合并用户判决错误数最小。
并列时先选虚警较少者，再选较小门限。禁止使用前1000场景拟合或挑选门限。
STMP 固定概率门限0.5，算法、权重和停止配置不变。NMSE采用原始全信道误差，不随门限重算信道。
该划分是回顾性评估：前1000场景此前已查看并参与过废弃的门限拟合；不声称完全未见的盲态测试。

旧六档SNR的前1000场景五种方法全部复用；baseline 后段已有结果也复用。
导入时检查结果、压缩数组哈希、输入凭据与算法身份；最终校准及评分前再核验输入文件、真值配对与判决。
需新增29952个结果：STMP 2000个，四个baseline各6988个。
STMP 超出999号的1107个主实验结果以及导频目录185个副本按用户授权删除，清单见 `PRUNING_MANIFEST.json`。
共享输入、场景种子、baseline结果、旧聚合统计及图像历史均保留。

入口：`.venv\Scripts\python.exe -B result/snr_comparison/data/known_phase_1000_calibration1000_snr10_20261023/parallel_run.py`

四个GPU进程、一个CPU进程，每进程四线程，PASSIVE等待；同一输入仅由父进程写入。
`PLAN.json` 和 `PLAN_HASH.json` 固定算法与任务范围；`STATUS.json` 为实时进度，`stdout.log`、`stderr.log` 为日志。
创建 `STOP.json` 可停止派发并等待当前任务安全落盘。旧运行的 STOP 保留，不能恢复旧2000场景STMP计划。
后台完成全部推断后自动审核后1000场景、冻结四个门限，再审核并统计前1000场景。
最终结果为 `evaluation/SUMMARY.json`，校准记录为 `calibration/` 和 `FROZEN_READOUT.json`。
本批次并发耗时仅用于吞吐，不作为独占设备的算法时延结论。

公共图片入口仍为 `src/evaluation/plots/snr_comparison.py`，读取本批次审核后的 `evaluation/SUMMARY.json`。
沿用论文图样式、NMSE上限0且5dB一格、STMP红色虚线空心圆；SNR横轴扩至10dB。
图片应输出到新的版本目录，并经渲染检查后交付；此前六档图片不覆盖。

Material Passport: academic-research-suite / experiment-agent; run + validate。
原始源码和配置已在改动前核验并保存到 `source_before.zip` 与 `before/`，新计划有独立运行身份。
主实验源文件身份变化仅来自默认MC数量和本批次调度、审核代码；输入生成、算法、权重不变。
