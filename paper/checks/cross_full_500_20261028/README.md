# 完整跨信道图及论文核验

24000份STMP/C-STMP推断完成，六方法共72000条、144组各500场景。`DATA_VALIDATION.json`记录318186份审计绑定资产以及完成文件新增绑定项的独立哈希复核、逐组覆盖与CSV重新汇总、主/工作进程身份及退出检查。

仅呈现调整位于`result/cross_channel/figures/full_500_paper_20261028`，由本目录`render.py`复现；不修改原冻结报告或数值。四列依次D/A/B/C，上排NMSE、下排AER，统一图例。按用户要求，真实零AER只显示在对数轴底边10^-5，不另设零值栏、子图或标记。参考Ding论文第5页图3的对数轴呈现；不据图猜测其原始计数是否为零。

正式图为`paper/C-STMP/figures/cross_channel.pdf`，阅读稿`paper/C-STMP/main.pdf`共13页，第12页图7。实际PDF图页及正文页面人工视觉检查通过；图例、标题、对数刻度正常。全部高SNR不利比较保留。原用户数回顾性阻尼调整说明与12例诊断计入评估的披露保持不变。

`VALIDATION.json`绑定正式PDF、阅读稿、统计和核验；`FIGURE_RETIREMENT_PLAN.json`及`FIGURE_RETIREMENT_COMPLETE.json`记录9份重复图/预览/旧STMP单独PDF删除及正式图映射。原冻结COMPLETE/AUDIT不改；其中退役图像路径应通过收据校验，不再要求这些图文件存在。原始数值、配置、代码及冻结报告全部保留。
