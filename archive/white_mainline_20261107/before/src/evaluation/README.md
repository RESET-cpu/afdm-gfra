# 最终实验入口

当前 GP-MP-C 论文图统一使用 [render_paper.py](plots/render_paper.py)，见[说明](plots/manuscript/README.md)。下文早期绘图入口和样式记录用于历史复现，不再作为当前稿件默认入口。

2026-10-25 后续：用户要求追加旧图，已完成原 500 场景六档 AWGN 的新网络曲线，见[报告](../../result/channel_denoising/data/colored_first_500_20261025_v2/REPORT.md)。本轮使用与旧 cloud 一阶网络完全相同的数组哈希，原九条曲线逐点保留；绘图入口为 `src/evaluation/plots/channel_denoising_colored_20261025.py`。

2026-10-25：独立 AWGN 去噪默认新增 `pretrained_colored_first`，固定使用有色噪声训练的一阶 epoch 200 EMA（`first_best.pt`，SHA-256 `7327d01785f10e3e18d76f7085604e1d1d53baa9d8cd80e12943768015452b91`）。与 `pretrained_first` 共享真值、噪声及六档方差，新网络输入 `C=vI`、实坐标协方差 `vI/2`，直接读取其均值输出。本项不使用二阶网络或分类器，也不改变接收机绑定。已冻结的 500 场景九曲线数据和图片保留原文；新的 1000 场景计划属于独立比较，不能直接拼接到旧图。接入检查与新计划见[记录](../../result/channel_denoising/data/colored_first_integration_20261025/README.md)。

2026-10-24：当前三种研究算法的展示名/程序标识为 **STMP / `STMP`**、**C-STMP / `C_STMP`**、**DU / `DU`**。DU就是原十层展开，`proposed`保留为历史别名；旧冻结计划不重写。C-STMP采用独立候选配置 `src/configs/candidates/C_STMP_20261024.json`，当前为有色训练网络在 `C=vI` 下推断、近似导数方差、冻结旧分类器。新建计划可用 `--methods STMP C_STMP DU --include-stmp`；本次已验证已知相位、估计噪声，C-STMP的内部联合相位更新尚未接入。配对结果见[本轮报告](../../result/channel_denoising/data/c_stmp_integration_20261024/REPORT.md)。下文历史默认配置和旧名称保留其上下文。

从仓库根目录使用 `python run_experiments.py`，本机解释器为 `.venv/Scripts/python.exe`。
每项实验独立放在 `evaluation/experiments/<实验名>.py`，对应配置在 `src/configs/experiments/<实验名>.json`。

| 实验名称 | 默认范围 | 状态 |
|---|---|---|
| snr_comparison | −4、−2、0、2、4、6 dB；每点2000场景 | 启用 |
| pilot_frames | 8、16、24、32、40、48导频；每点2000场景 | 启用 |
| user_count | 20、40、60、80、100用户；每点2000场景 | 启用 |
| activity_probability | 0.05、0.1、0.15、0.2、0.25；每点2000场景 | 启用 |
| cross_channel | D/A/B/C × 六档SNR；每点2000场景 | 启用 |
| channel_denoising | 六档已知AWGN方差；新计划1000场景，每场景4候选信道 | 旧一阶、新有色训练一阶及三个参照 |
| runtime_comparison | −4、0、4 dB；固定前20共享场景；每输入测3次 | 替代收敛曲线 |
| density_ratio_ablation | 保留旧三网络的证据消融定义 | 暂缓 |

常规方法为 Proposed 十层、Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP。
代码和结果中的方法标识分别为 `proposed`、`offgrid_sbl`、`gnn`、`gamp`、`somp`。
三网络标识为 `STMP`，需要用户后续明确要求后再启用；显式选项为 `--include-stmp`，
或在对应实验配置中设置 `include_stmp: true`。
去噪单独比较 noisy、Gaussian、显式使用真值信息的 genie、旧预训练一阶网络和新有色训练一阶网络；不加载每层网络。

```powershell
python run_experiments.py list
python run_experiments.py inspect
python run_experiments.py snr_comparison inspect
python run_experiments.py snr_comparison --help
python run_experiments.py evaluate --estimate <预测.npz> --truth <配对真值.npz>
# 明确启动正式实验
python run_experiments.py snr_comparison run
# 同一个实验的独立文件入口
python src/evaluation/experiments/snr_comparison.py --help
```

`prepare` 只生成并核验默认计划，不执行推断。当前已经准备完成，无须重复创建。
输出默认写入 `result/main2000_message_gem_20261022/<实验名>/`，所有实验共享同一结果缓存。
旧 `result/final2000` 的计划、暂停状态和结果保留原文，本次接入不启动批量实验。
`run` 校验计划及所有绑定文件；已完成时验证报告后退出；失败保留原记录，锁冲突须先核查对应进程。
`summarize` 从已保存场景生成汇总；不启动接收机。

新建开发检查可使用 `plan --smoke --output <新目录>`，其种子与正式2000场景分离。
用户指定复用既有开发场景时直接回放已保存输入，本次核验记录于 `result/mainline_message_gem_20261022`。
更改源代码或实验配置后，应在新目录重新生成计划；不能为了绕过核验手工改写原计划哈希。
`run` 读取保存的计划。算法登记项会复制进计划，运行不会悄悄换成后来修改的登记参数。

`experiments/` 各文件负责各自的条件定义，`suite.py` 共用计划与执行，`scenes.py` 负责共享场景身份，
`algorithm/registry.py` 根据算法登记配置构造方法，`receivers.py` 共用设备与计时处理，
`observations.py` 与 `profiles.py` 生成配对输入，`denoising.py` 检查一阶网络，`reporting.py` 输出报告。
`metrics.py` 统一计算接收机评分，`storage.py` 只保存和加载 NumPy 数组；
JSON 读写与哈希由包根目录的 `utils.py` 提供。物理场景生成器在 `system/scenario/`。
`algorithm/registry.py` 解析 `models.json` 引用的唯一 STMP 配置，再将完整配置存入计划。

## 选择某项实验的方法

例如只比较 Proposed、GAMP 和 SOMP，修改 `src/configs/experiments/snr_comparison.json`：

```json
"methods": ["proposed", "gamp", "somp"]
```

其余实验各自的 `methods` 不受影响。`values` 或 `snr_db` 指定本实验的扫描点。
正式接收实验默认使用共享的 2000 场景；`--scenes N` 或配置的 `scenes` 选择正式清单前 N 个，
不按结果挑选场景。运行时间实验默认使用固定前 20 场景，最多 20 个。
去噪配置只能选择 `kind: denoiser` 的方法，接收实验只能选择 `kind: receiver` 的方法。
仅选数值基准时，不要求未选中网络的权重；去噪只加载所选方法，不自动执行其他网络。

```powershell
# 修改配置后创建计划；此步骤不做推断
python run_experiments.py snr_comparison plan --output result/my_snr
# 检查并明确执行刚才的计划
python run_experiments.py snr_comparison inspect --output result/my_snr
python run_experiments.py snr_comparison run --output result/my_snr
```

也可用 `plan --config <实验JSON> --catalog <算法登记JSON>` 选用独立配置。
`--methods` 是创建计划时的临时覆盖；未知名称、重复方法和不适用的算法类别会立即报错。
`reference_method` 指定配对差值的参照；若本次未选择它，使用所选方法中的第一项。

## 接入一个 baseline

1. 将实现放在 `algorithm/baseline/my_baseline.py`，提供 `Receiver` 类或构造函数。
2. 在 `src/configs/algorithms.json` 的 `algorithms` 中加入登记项。
3. 在需要运行它的实验配置 `methods` 中加入 `my_baseline`，创建新计划即可。

下例是登记格式示例，需先提供对应实现：

```json
"my_baseline": {
  "kind": "receiver",
  "group": "baseline",
  "label": "My baseline",
  "factory": "algorithm.baseline.my_baseline:Receiver",
  "backend": "cpu",
  "kwargs": {}
}
```

构造器接收 `device` 和 `kwargs`。若需要文件路径，使用 `path_kwargs`，其中的路径相对项目根目录解析。
权重或额外资源文件列入 `assets`，它们和实现源码会在计划里记录 SHA-256。
当前模型配置可通过 `model_kwargs` 传入，如 `{"configuration": "STMP"}`；普通新基准通常不需要这一项。
新增独立文件不会改变现有四个基准的源码校验或活动门限。

接收机的统一接口为 `infer(public) -> (arrays, record)`：

- `public` 默认是 `ReceiverInput`：包含观测、选定相位形成的算子和活动先验。算法登记 `estimates_phase_internally: true` 时，在 estimated 相位模式改为提供 `UnknownPhaseInput` 的原始导频，接收机自行初始化和更新相位。known 相位模式仍提供真值形成的算子。
- 默认未知噪声模式中噪声字段是占位值，算法应从观测估计噪声；显式 known 模式才提供真实方差。
- `arrays['estimate']` 是复信道估计，形状为 `[K, M, R, N]`；`arrays['activity_decision']` 是长度 K 的布尔判决。
- `record` 至少提供 `iterations` 和 `stopping_reason`。真值由评分模块持有，不传入接收机。
- 使用 GPU 的实现设 `backend: "device"`，并在 `device_modules` 列出需切换设备的网络属性路径，如 `["model"]`。
  CPU 网络可用 `parameter_modules` 单独指定参数统计对象。未声明网络的数值方法参数量记为零。

按此接口接入后，各接收实验自动获得相同场景输入、NMSE/AER/漏检/虚警评分、运行时间和显存记录、配对区间与图表，无需添加方法名称分支。
新增去噪方法同样登记，类别为 `denoiser`；接口为 `infer(query, variance, *, priors) -> (mean, metadata)`。
只有显式 `uses_truth: true` 的 genie 方法会得到真实条件先验，普通方法的 `priors` 为 `None`。

## 相位、噪声和场景数量

接收实验独立支持 `--phase-mode known|estimated` 和 `--noise-mode known|estimated`；
也可在实验 JSON 中设置 `phase_mode`、`noise_mode`。未指定时仍为双估计模式。
`known` 提供相应模拟真值，`estimated` 从观测估计；场景、预测和报告均记录这两个模式，
不同模式使用不同缓存标识。噪声开关控制是否提供真实方差，保留各方法原有条件求解器；
GAMP-SBL 的 known 分支仍按原算法用给定方差设置 Gamma 先验并更新内部噪声精度。
独立 AWGN 去噪使用给定方差，不接受接收实验的这两个开关。

Proposed 在 estimated 相位模式使用已接受的 `message_gem`：初始化后，十层各执行一次，
第1至9层之后更新相位。公共相位估计仅供未登记内部相位估计的基线使用。
各方法共享同一物理场景、导频和观测；相位估计器属于各自算法流程。
Proposed 的接收机计时包括内部相位初始化和更新，外部相位耗时记为0；其他方法列出公共前端耗时。
比较时使用端到端时间，同时标明CPU/GPU后端，避免遗漏相位代价或重复累加。

例如，每个 SNR 使用 500 个正式配对场景，已知相位、未知噪声，排除旧三网络：

```powershell
python run_experiments.py snr_comparison plan --scenes 500 --phase-mode known --noise-mode estimated --methods proposed offgrid_sbl gnn gamp somp --output result/known_phase500_20261022/snr_comparison
python run_experiments.py snr_comparison run --output result/known_phase500_20261022/snr_comparison
```

选项在 `plan` 时冻结，`run` 按保存的计划执行。修改源码前的副本保存在
`result/receiver_modes_20261022/before`；已有计划和结果保留原文，不能改写旧计划哈希来使用新源码续跑。

NMSE采用汇总误差能量/信号能量；AER与漏检、虚警按真实个数汇总。区间使用10000次物理场景配对重抽样。
十层使用CUDA，现有数值基线保留原生CPU实现；时延与显存按方法标明，不能据此声称纯算法复杂度降低。
