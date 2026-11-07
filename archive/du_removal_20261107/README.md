# DU 移除记录

作者明确要求不上传 DU，并进一步确认本地独立 DU 论文、权重及冻结实验记录也删除，
STMP 等方法共用的文件保留。[范围及状态](REMOVAL.json) 记录具体路径和源码哈希。

当前入口移除 `DU`、`proposed` 两个登记；运行时间比较改用 GP-MP，STMP 活动证据
消融保留 STMP 两个变体。冻结主线及旧配置的字节保持，不把旧 DU 结果改称 GP-MP。
GitHub 当前文件清单排除 DU 稿件、独立推断/训练实现、专用历史实验与 DU 权重。
未重写 Git 历史，旧提交仍可包含 DU。

STMP 的三个共用相位模块归入 `src/receiver/frontend`；原相位源码仍在
`src/algorithm/proposed` 原路径供冻结批次核验。相位校准文件
`result/models/proposed_10/phase_moments.npz` 和共用场景登记
`result/lstmp_v3_shared2000_20261021` 保留，它们并非 DU 独占资产。

初次本地批量永久删除命令被自动审批拒绝，返回原因仅为 `blocked by policy`。
作者随后明确改为移动到根目录 `delete/` 后自行删除；已按原相对路径完成移动，
没有永久删除文件。`delete/` 被 Git 忽略，且不进入上传清单。
历史混合文档保留原文，其中指向已移出发布范围的 DU 文件的链接不再作为现行使用入口。
