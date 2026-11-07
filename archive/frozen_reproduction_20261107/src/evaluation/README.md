# 实验入口

当前默认算法为独立白噪声 `GP_MP`；估计相位版为 `GP_MP_EP`，独立去噪为 `pretrained_white_first`。入口使用 `run_experiments.py`，本机解释器为 `.venv/Scripts/python.exe`。历史有色代码、配置、权重和数据保留原位，退出当前默认登记。整理前说明保存在 [历史副本](../../archive/white_mainline_20261107/before/src/evaluation/README.md)。

论文图统一使用 [render_paper.py](plots/render_paper.py)。已完成白噪声主 SNR 两种相位各 6000 份；收敛图采用 30 场景，活动证据消融采用 100 场景，这两项已结束。

## 已授权逐项替换

2026-11-07 作者授权先整理白噪声代码主线，再补跑后续实验，完成一项替换一项。每点沿用当前图中的 500 个配对场景。使用保存观测和固定模型，不训练、不选样、不调参。

| 顺序 | 实验 | 补跑及复用 |
|---|---|---|
| 1 | 去噪 | 六档 AWGN、每场景 4 个信道，共 12000 个白噪声查询 |
| 2 | 导频数 | Q=8/16/24/32/40/48；白噪声已知/估计相位，SBL 13/25 |
| 3 | 用户数 | K=20/40/60/80/100；白噪声已知/估计相位，SBL 13/25 |
| 4 | 活动概率 | p=0.05/0.10/0.15/0.20/0.25；白噪声已知/估计相位，SBL 13/25 |
| 5 | 跨信道 | A/B/C/D 与六档 SNR；白噪声已知相位 |

相同中心条件只在全部输入哈希和模型设置一致时复用主 SNR 的已核验结果。白噪声接收机所有条件统一使用阻尼 0.4、最少 60 轮、最大 600 轮、门限 0.5。估计相位前端一次估计后固定，推断不接收真值相位。新用户数结果保留每个场景，历史单场景替换不带入新结果。

执行模块为 `evaluation.white_followup_20261107`。每项保存预测并全量重评分，核对来源、数组哈希和场景覆盖；确认进程退出后更新相应图和必要稿件说明、编译并目视检查。该项的 `ADOPTION.json` 通过后，下一项才允许启动。失败保留现场，不自动重试推断。状态见 [REQUEST.json](../../result/white_followup_20261107/REQUEST.json)。

```powershell
# 只读查看
python run_experiments.py list
python run_experiments.py white_followup inspect

# 单项准备，不启动 GPU；执行需要已有授权并先核对锁和进程
python run_experiments.py white_followup prepare --stage pilot_frames
python run_experiments.py white_followup coordinate --stage pilot_frames
```

元数据和收据在 `result/<实验>/data/white_mainline_500_20261107`，接收机新增数组在 `E:/afdm-gfra-results/white_followup_20261107/<实验>`。去噪数组保存在本次结果目录。输出不覆盖旧结果，停止使用各批次的 `STOP.json` 排空接口。

## 通用计划与历史复现

`experiments/` 定义条件，`suite.py` 管理冻结计划，`algorithm/registry.py` 按登记构造算法。配置位于 `src/configs/experiments/`，当前登记为 `src/configs/algorithms.json`。新建通用计划经公共入口默认写到独立的 `result/white_mainline_default_20261107/`，不会自动采用旧批次计划。

```powershell
python run_experiments.py snr_comparison plan --output result/my_snr
python run_experiments.py snr_comparison inspect --output result/my_snr
python run_experiments.py snr_comparison run --output result/my_snr
python run_experiments.py evaluate --estimate <预测.npz> --truth <配对真值.npz>
```

`plan` 仅准备，`run` 才执行。已有计划保存自己的算法登记、参数和文件哈希，不随默认登记改变。历史复现显式指定原输出目录或 `--catalog src/configs/historical/algorithms_colored_20261107.json`；旧独立入口保留原义，不作为新的主线入口。不要通过改写旧计划哈希绕过核验。

`metrics.py` 定义接收机评分；NMSE 使用误差与信号能量之和的比值，AER 使用全部设备。迭代上限、失败和不利场景均须保留。`storage.py` 保存 NumPy 数组，`utils.py` 提供原子 JSON 和 SHA-256。

新增方法在登记中指定 `factory`、`path_kwargs`、`assets` 和设备字段，再创建独立计划；不得覆盖冻结版本。STMP、DU 及传统基准仍保留各自配置和研究用途。
