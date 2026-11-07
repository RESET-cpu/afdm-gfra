# 相对当前白噪声假设的协方差检查

状态：ANALYZED。24个已有场景的48条件离线复查完成；没有训练、接收机运行或新增物理MC实验。

- [完整说明与判断](../../../../paper/docs/COLORED_COVARIANCE_RELATIVE_CHECK_20261024.md)
- PLAN.json：输入哈希、评分规则、边界与保护文件。
- RESULTS.npz：5760条用户阶段记录，包含全部方法/折次参数和元数据。
- SUMMARY.json：场景等权汇总的24个分层及逐场景配对差。
- ALGEBRA.json、SANITY.json：数值核对及独立合成检查。
- COMPLETE.json、VALIDATION.json：完成身份及11项统计解释检查。

主要比较为两折离线拟合的可分协方差与同样拟合误差功率的白噪声模型。结果支持保留当前受限C族作下一阶段候选，不证明随机采样分布或活动检测性能已经适配。

命令：从项目根目录运行 .venv/Scripts/python.exe -B result/snr_comparison/data/colored_covariance_relative_check_20261024/check.py。已完成目录拒绝覆盖；需复算时将检查脚本复制至同级新目录，再执行。合成检查入口为同目录 sanity.py。
