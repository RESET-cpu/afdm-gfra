# 已保存 STMP 查询的 C 表示分析

2026-10-24。只做离线描述性计算，没有新接收机、网络、训练或物理场景运行。主报告见 [C 表示分析](../../../../paper/docs/STMP_COVARIANCE_REPRESENTATION_20261024.md)。

- 来源：同级 low_snr_query_check_20261024 的48条件、24场景、3阶段快照；共5760个用户阶段记录。
- PLAN.json / analyze_saved_queries.py：三轴未中心化二阶矩与预定 DFT 基；SUMMARY.json 为全部分层，RECORDS.json 保留全部用户。INPUTS.json 保存查询、源 READY 与公开输入哈希。
- PUBLIC_BASIS_PLAN.json / analyze_public_basis.py：看到输入列相关后追加的探索性比较；两种基均只依赖公开 A。PUBLIC_BASIS_SUMMARY.json / PUBLIC_BASIS_RECORDS.json 保存完整结果。
- check_algebra.py / ALGEBRA_CHECK.json：小尺寸 Gaussian 线性求解、固定基投影后的 quotient 及标量先验查询 covariance 恒等式；最大相对误差小于1e-13，不是统计或性能验证。
- 原样保留全部条件和失败分层；没有根据结果删除用户。用户和张量坐标不作为独立场景，分位数仅用于描述。
- 这些评价场景已用于机制与候选设计，不能随后充当独立确认数据；未据此拟合训练噪声分布。

在仓库根目录按顺序运行项目 .venv 的 Python，执行 analyze_saved_queries.py、analyze_public_basis.py、check_algebra.py 即可复算。后两项读取第一项结果；均不导入接收机或网络。
