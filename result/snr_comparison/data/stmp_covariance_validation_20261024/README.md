# C 候选的有界验证

正式结论见 [研究报告](../../../../paper/docs/STMP_COVARIANCE_VALIDATION_20261024.md)。

完成旧24场景/48条件的查询对照，以及正式1000场景/2000条件的首轮线性计算。没有训练、网络调用或新接收机完整迭代。

## 当前有效文件

- PLAN.json：初始范围、输入、种子、受保护文件哈希。
- SAVED.npz / SAVED_COMPLETE.json / SAVED_SUMMARY.json：旧查询oracle逐模式功率与16份匹配Gaussian参考；各参考也重新拟合。
- FIRST_ESTIMATED_PLAN.json：正式噪声入口不一致的修正记录。
- FIRST_ESTIMATED.npz / FIRST_ESTIMATED_COMPLETE.json / FIRST_ESTIMATED_SUMMARY.json：正式噪声估计后的首轮结果。
- ALGEBRA_ESTIMATED.json：640维工作模型协方差对角恒等式。
- NUMERICAL_AUDIT.json：近奇异块、SVD比较及全量/补充分位数。
- VALIDATION_ESTIMATED.json：当前核验；PASS仅指代数、复现及文件完整性，科学判断为ANALYZED。
- 图形位于 ../../figures/stmp_covariance_validation_20261024/，保存PNG及PDF。

## 拒绝使用的首版首轮结果

FIRST.npz、FIRST_COMPLETE.json、FIRST_SUMMARY.json、ALGEBRA.json、VALIDATION.json属于误用输入旧噪声字段的首版。旧首轮复现失败，不能作为正式接收机对照。文件保留审计，INITIAL_ATTEMPT_STATUS.json明确标记拒绝。SAVED系列不受影响。

原 run.py first 和 summarize.py 默认主入口保留以追溯首版，**不要用它们复算当前有效首轮结果**。

## 复算

在仓库根目录PowerShell使用项目虚拟环境：

    .venv\Scripts\python.exe result/snr_comparison/data/stmp_covariance_validation_20261024/first_estimated_noise.py

已有完成记录时直接返回，不覆盖结果。新版本应另建候选目录并保存新计划，不删除当前产物。

只更新当前有效首轮结果的汇总：

    .venv\Scripts\python.exe -c "import sys;sys.path.insert(0,'result/snr_comparison/data/stmp_covariance_validation_20261024');from summarize import first_summary;from run import read,OUT;first_summary(read(OUT/'PLAN.json'),'FIRST_ESTIMATED.npz','FIRST_ESTIMATED_SUMMARY.json')"

补充数值审计与图形/哈希检查：

    .venv\Scripts\python.exe result/snr_comparison/data/stmp_covariance_validation_20261024/numerical_audit.py
    .venv\Scripts\python.exe result/snr_comparison/data/stmp_covariance_validation_20261024/finalize.py

metrics.py记录统计量定义；run.py的saved分支生成Gaussian参考；first_estimated_noise.py调用冻结的estimate_spatial_noise并检查48份已保存首轮。

## 数组与边界

SAVED的meta列为 scene、condition、group、stage、user、active、final_missed；actual为5760×14，reference为5760×16×14。group=0均匀、1失败富集；stage=0/1/2对应第1/20/最终轮。

FIRST_ESTIMATED的meta列为 scene、condition、previously_examined、user、active、completed；fine/scalar为80000×14，tau为80000×16，properties为80000×7。condition=0为−4 dB、2为0 dB。指标名保存在npz中。

inactive用户的信号投影为NaN，表示不适用。SVD判秩均为16，但场景22的8个近奇异块应单独说明，不能把浮点极端量当作精确物理方差。全部原始记录保留。

逐模式归一化使首轮MSE比中位数约27倍；旧查询中间轮仍有明显结构。两者不等于最终活动检测下降。完整限制、分层及来源见研究报告。
