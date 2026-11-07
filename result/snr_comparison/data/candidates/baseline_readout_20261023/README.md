# 跨SNR固定能量门限候选

状态：实现和确定性检查完成；未拟合正式门限，未接入主实验。

依据和方法差异见[GFRA核验报告](../../../../../paper/docs/BASELINE_GFRA_AUDIT_20261023.md)。`readout.py`提供固定门限判决及独立校准函数。推断接口没有SNR参数；一个方法在六档SNR共用一个门限，方法之间分别校准。没有将用户共享精度、信道能量和系数能量当作同一统计量。

`calibrate`要求case×user分数、同形能量、布尔真值、每个case的物理场景ID和禁止使用的测试场景ID。相同物理场景在不同SNR的ID必须一致。调用者须传入**整个2000场景主面板**的物理ID，以及所有其他禁止调参的验证/测试ID；不只检查已完成800场景。所有预定SNR均应纳入，禁止挑选易场景。应在正式校准后另存来源哈希、统计量定义、目标和冻结门限，并进行独立验证。

`result/snr_comparison/data/audits/baseline_gfra_20261023/READOUT_INPUTS.npz`是测试集诊断数据，不能用于`calibrate`。只以文献给定的0.1做事先指定的数值控制，不将任何更优测试点选择为正式门限。

数学检查及诊断数据的实际路径：`result/snr_comparison/data/audits/baseline_gfra_20261023/`。

在项目根目录运行：

```powershell
.venv\Scripts\python.exe -B result/snr_comparison/data/audits/baseline_gfra_20261023/check_math.py
.venv\Scripts\python.exe -B result/snr_comparison/data/audits/baseline_gfra_20261023/replay_readouts.py
```

这两条命令仅作数学核验及已保存数据重判，不启动接收机推断或训练。
