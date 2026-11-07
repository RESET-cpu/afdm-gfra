# 导频数实验断点恢复

2026-11-07 22:03，按作者本轮复跑请求，从原计划启动续跑。恢复前已有 **2906/12000** 份结果，剩余 **9094** 份；本记录不代表阶段完成或图稿采用。

上次失败发生在工作进程读取 `job000906.json` 时，异常为 `PermissionError`；尚未进入该任务的接收机推断。该文件现在可正常读取，没有发现遗留半写入结果目录。原失败记录保存在本地 `delete/pilot_resume_20261107/FAILURE.original.json` 及原会话中；[发布前的失败记录](https://github.com/RESET-cpu/afdm-gfra/blob/61834c835efc56efab2e445c21e1676b682448c9/result/pilot_frames/data/white_mainline_500_20261107/FAILURE.json)仍可查阅。

本次只修改任务文件读取：遇到权限错误时，每隔 0.05 秒重新读取，最多等待两秒。持续拒绝访问仍报错，非法 JSON 或文件缺失立即报错；接收机推断失败不自动重试。实际占用该文件的进程未能追溯，因此不把临时文件占用的判断当作已经确定的根因。

- [代码验证](VALIDATION.json)：27 项检查通过，包括真实 Windows 独占文件句柄的复现、释放后恢复、持续失败有界退出、非法内容不重试。除新增读取函数与工作进程中的该调用外，其余语法树一致。
- [已有结果核验](SAVED_RESULTS.json)：2906 份保存数组全部重新评分，核对输入、输出、参数、原计划和哈希；GP-MP 1406 份，其余三种方法各 500 份。没有未知结果或未登记的部分输出目录。
- 原计划绑定的 164 项资产通过校验，500 个场景、导频数 8/16/24/32/40/48、四种方法、权重和数值设置保持原样。原计划文件不重写；新执行记录使用更新后的源码清单。

运行入口：

```text
python run_experiments.py white_followup inspect
python run_experiments.py white_followup coordinate --stage pilot_frames
```

`coordinate` 会先重新核验全部输入与已有结果，然后只派发缺失任务。完整数组保留在原计划的本地 E 盘路径，未上传 GitHub；从 GitHub 下载的副本不具备续跑这一历史批次所需的全部原始输入。

本轮仅启动导频数阶段。完成后仍须全量评分、覆盖与哈希校验，并核对进程退出，之后才能更新论文图；下一实验不会由此命令自动启动。状态文件是本地实时进度，GitHub 内容是提交时的快照。

Material Passport: `academic-research-suite/experiment-agent`, mode `run`; 已验证范围为任务读取修复与已有结果完整性，完整实验验证待完成。
