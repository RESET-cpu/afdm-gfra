# 追加独立 baseline 校准场景

用户授权：先检查独立校准门限是否稳定；若不稳定，追加场景，但不能使用实际比较的 1000 场景。

`../baseline_threshold_stability_20261025/REPORT.md` 记录触发依据：Off-grid SBL 在 −4 dB 的留出 AER 抽样敏感性达到预先冻结的追加条件。此处保留旧校准与所有官方算法、权重和门限。

`PLAN.json` 已冻结，SHA256：`255eb8d74dc6c69aa565160a791de8058697b645c0bc9a24e0e071e5f72a4e1f`。

- 新场景 2000–2999，700 个补充校准，300 个单独验证，固定划分见 `SCENES.csv`。
- 四种 baseline：Off-grid SBL、GNN-ASPL、GAMP-SBL、SOMP；六档 SNR −4、−2、0、2、4、6 dB。
- 原 1000 校准场景 1000–1999 只读复用；正式比较场景 0–999 不参与，也不读取其预测和真值。
- 700 个新增校准场景完成后，使用 1700 个校准场景冻结四种新门限，再运行验证场景。
- 不自动采用新门限；验证同时完整报告旧八档、旧六档与扩充后六档三个规则。
- 一个 CPU 进程、两个线程，CUDA 禁用；主 C-STMP SNR、导频接续和其他 CPU 实验不受本脚本控制。
- `STATUS.json` 是实时进度，`START.json` 是真实解释器身份，`LAUNCH.json` 是 Windows 启动器记录。
- `STOP.json` 在当前接收机结果保存后停止；失败保留 `FAILED.json`，不自动重试。不要重复执行 `run`。
- `INFERENCE_COMPLETE.json` 只代表推断完成；最终完成必须是 `COMPLETE.json` 的所有输出哈希通过。

2026-10-26 已接上独立的完成后核验：`follow_completion.py` 仅等待本次真实进程退出且完成凭据有效，再调用冻结的 `postprocess.py`。该核验只读检查 24000 份输出与 6000 份输入，使用原 1000 与扩充后 1700 个校准场景分别重采样，并在同一组 300 个独立验证场景上比较 AER 和门限波动。结果写入 `stability_after_extension/`；跟进状态位于 `completion_followup/STATUS.json`。不重复推断、不自动采用门限、不启动额外场景。

所有新结果位于本目录；接收机代码和历史数据均不修改。
