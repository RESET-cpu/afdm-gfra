# 后 500 场景校准固定门限，重画前 1000 场景

当前采用的方案，来自用户 2026-10-23 的最新指令。

- 主实验已安全暂停：四个 baseline 各完成 1502 场景，STMP 完成 1184 场景另 3 个 SNR 输入。
- 额外种子校准也已停止；其结果不参与本次拟合。
- **校准集：主实验编号 1000–1499，共 500 场景。**
- **绘图集：主实验编号 0–999，共 1000 场景。**
- 每场景包含 −4、−2、0、2、4、6 dB；已知相位、估计噪声。
- 四个 baseline 各自一个固定门限，跨所有 SNR 共用；STMP 保持固定概率门限 0.5。
- 目标为六档 SNR 的总用户误判数最小；并列时先取虚警较少者，再取较小门限。
- 校准后先保存并冻结门限，再读取绘图集评分。独立向量化穷举核对门限解。
- 不启动推断或训练，不改动主实验原始输出、配置、权重与 NMSE。

本次使用的校准和绘图场景互不重叠。前 1000 场景曾被查看并用于已废弃的校准，
1000–1499 中的 1040–1057 也有停止条件/GNN 诊断历史；因此这是回顾性比较，
不宣称完全未查看的盲态测试。不删除不利样本，也不使用额外完成的 1500、1501 替换校准样本。

校准集逐份核对 12,000 个 baseline 输出、压缩文件、输入哈希与原判决。
绘图集复用此前审核的保存分数与原始统计，重新核对 30,000 份结果及压缩输出哈希；
不读取旧门限作为本次拟合输入。新旧 NMSE 及 STMP 判决逐项相同。

```powershell
.venv\Scripts\python.exe -B result\snr_comparison\data\baseline_fixed_last500_20261023\run.py check
.venv\Scripts\python.exe -B -u result\snr_comparison\data\baseline_fixed_last500_20261023\run.py run
.venv\Scripts\python.exe -B src\evaluation\plots\snr_comparison.py --input result\snr_comparison\data\baseline_fixed_last500_20261023\first1000\SUMMARY.json --output result\snr_comparison\figures\fixed_last500_first1000_20261023 --aer-scale auto
```

结果见 `REPORT.md`、`FROZEN_READOUT.json`、`first1000/SUMMARY.json`。
图中不增加样本划分说明；完整来源和历史查看情况保存在元数据中。
主实验不会自动恢复；`STOP.json` 保持存在，恢复需要用户后续指令。
