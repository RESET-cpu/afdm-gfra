# AFDM-GFRA

论文配套代码的使用、无权重示例、资产检查及复现边界见 **[REPRODUCING.md](REPRODUCING.md)**。
模型权重通过 Git LFS 提供。需要权重时，先安装 Git LFS，再下载仓库：

```text
git lfs install
git clone https://github.com/RESET-cpu/afdm-gfra.git
cd afdm-gfra
git lfs pull
```

在项目目录中安装依赖并运行：

```text
python -m pip install -r requirements.txt
python run_experiments.py demo --output result/demo_first
python -m pytest -q
```

示例只生成一个小型合成场景，不需要模型或原始数据。默认测试为 `src/tests/public`；
当前研究检查及冻结原件的适用范围见 [测试说明](src/tests/README.md)。
原创代码暂保留版权，不设置开放许可证；第三方许可原样保留，见 [RIGHTS.md](RIGHTS.md)。
当前为投稿准备中的源码版本，尚未宣称完整论文数值复现或发布最终投稿标签。

GitHub 保存代码、配置、论文、正式图表、精选小型汇总及当前 GP-MP、STMP、GNN 的模型资产；原始数据仍保留在本地。权重清单见 [模型资产](src/configs/release/weights.json)，可运行 `python run_experiments.py assets --scope models --verify` 核验。详见 [GitHub 内容与复现范围](GITHUB_CONTENTS.md)。

2026-11-07 代码整理：场景、波形、信道、接收机、实验、绘图、网络和训练直接按功能放在 [src](src/README.md) 下。根入口保持 `run_experiments.py`，增加 `plot --list` / `plot --check`。原源码保留给冻结批次复现，模型、数据、参数与正式图不变。[映射与验证](archive/src_flatten_20261107/README.md)。

2026-11-07 后续：白噪声去噪 12000 个查询已核验，图 4 和图 3 示例已采用，两版工作稿同步。[采用记录](paper/checks/white_denoising_adopted_20261107/README.md)。导频数阶段的任务读取权限错误已修复；已有 2906/12000 份结果全量重评分通过，22:03 按原计划启动断点续跑，剩余 9094 份，尚未完成或采用。完整核验及图稿采用后才进入用户数阶段。[恢复与验证](archive/pilot_resume_20261107/README.md)。GitHub 状态为提交时快照，本地 STATUS.json 为运行进度。

2026-11-07：代码主线已整理为独立白噪声 `receiver.gp_mp`，默认登记为 `GP_MP` / `GP_MP_EP`，旧 `C_STMP` 标识仅兼容指向白噪声版本。旧有色实现与登记已移至独立冻结归档，原数据保持。作者已授权按去噪、导频数、用户数、活动概率、跨信道的顺序补跑，每项核验并替换图稿后再开始下一项；状态见 [后续实验请求](result/white_followup_20261107/REQUEST.json)。

2026-11-07：白噪声网络主 SNR 的已知相位与估计相位结果均已完整核验并采用，每档 1000 场景。主图及两版工作稿同步，其他待替换曲线仍保留阶段说明。[采用与核验](paper/checks/white_snr_adopted_20261107/README.md)。

2026-11-06：当前 GP-MP 稿的训练说明与附录已统一为白噪声形式；尚未替换的历史实验曲线在工作稿第六章集中注明，图表数据保持。[修订与核验](paper/checks/white_noise_wording_20261106/README.md)。

2026-11-04：完整相位估计结果已加入主 SNR 图，展示名 **CGP-MP-EP**；每档 1000 场景，两版论文已同步。[结果与核验](paper/checks/snr_estimated_phase_1000_20261104/README.md)。下文旧 500 场景批次状态为历史快照。

当前论文绘图已统一：[整理后的绘图入口](src/plotting/README.md)；[现行图目录](paper/figures/README.md)。日常入口为 `python run_experiments.py plot`，原绘图脚本保留供旧记录复现。

MIMO-AFDM 卫星物联网免授权随机接入研究：系统模型、接收算法、实验与当前 GP-MP 稿件。

DU 已按作者要求退出当前代码入口及 GitHub 清单，共用相位模块和 STMP 校准文件保留。
本地待删目录及范围见 [DU 清理记录](archive/du_removal_20261107/README.md)。

2026-11-07 后续代码整理：当前功能包已去除旧包重复副本，训练、推断、采样、评分和绘图分离；核验范围与证据见 [整理记录](archive/code_cleanup_20261107/README.md)。

## 常用入口

| 要找的内容 | 入口 |
|---|---|
| 当前算法稿与阅读 PDF | [当前稿件](paper/README.md) · [main.pdf](paper/main.pdf) · [写作与修订规范](paper/docs/WRITING_GUIDE.md) |
| 再次预审前必读：已讨论问题与剩余事项 | [预审讨论记录](paper/docs/REVIEW_DECISIONS.md) |
| 实验数据、状态与论文用图 | [实验索引](result/README.md) |
| 代码、配置与检查 | [代码导读](src/README.md) · [实验用法](src/experiment/README.md) |
| 文献原文与阅读记录 | [参考资料](reference/README.md) |
| 历史记录、旧路径及整理清单 | [归档索引](archive/README.md) |

## 当前状态

2026-11-07 核对：

- 当前算法稿展示名为 **GP-MP**，估计相位版为 **GP-MP-EP**；`C-STMP` / `C_STMP` 仍是目录和历史实验标识。当前稿采用白噪声训练表述，图表替换状态见[稿件说明](paper/README.md)。
- 论文当前编入三幅方法图与七幅实验图，矢量 PDF 统一在 [paper/figures/](paper/figures/)。不含评估协议附录的版本为 `main.tex` / `main.pdf`，包含该附录的完整版本为 `main_full.tex` / `main_full.pdf`；两版共享正文。2026-11-04 精简后，原信道推导附录移至内部文档，完整稿中的评估协议附录由 C 顺延为 B。
- 白噪声主 SNR 两种相位各 6000 份已完成、核验并采用；收敛图采用 30 场景，活动证据消融采用 100 场景，均不继续原预算。
- 当前默认绑定见 [FINAL.json](FINAL.json) 和[算法登记](src/configs/organized/algorithms.json)。有色版本退出当前入口，旧批次的冻结配置和源码保持；历史登记位于 [冻结归档](archive/frozen_reproduction_20261107/README.md)。

批次参数、样本范围和执行状态分别查对应的 `PLAN.json`、`README.md`、`STATUS.json` 与完成记录。历次启动、暂停、修订及不利结果说明完整保存在[整理前项目说明](archive/project_cleanup_20261030/ROOT_HISTORY.md)。

## 项目目录

```text
src/          按功能分目录：scenario、waveform、channel、receiver、experiment、plotting、networks、training
src/configs/  工作代码登记与原科学参数、冻结配置
src/tests/    当前检查与整理前后对照检查
archive/frozen_reproduction_20261107/  冻结实验原源码，显式回放
result/       八类实验入口，以及保留的共享资源和兼容路径
paper/        当前稿件、图表及研究文档
reference/    文献原文、专题阅读及写作资料
archive/      历史记录、目录映射及已归档的检查预览
```

根目录保留统一入口 `run_experiments.py`、项目配置、代理约定和版本记录。`.venv/` 是本项目 Python 环境，`.git/` 是已有版本管理目录。

## 使用

在项目根目录运行以下只读入口：

```powershell
# 列出实验与默认方法，不执行推断
& .\.venv\Scripts\python.exe -B run_experiments.py list

# 查看指定实验的参数
& .\.venv\Scripts\python.exe -B run_experiments.py snr_comparison --help

# 查看逐项替换队列，不执行推断
& .\.venv\Scripts\python.exe -B run_experiments.py white_followup inspect
```

日常实验定义位于 `src/experiment/experiments/`，配置仍在 `src/configs/experiments/`，工作代码登记为 `src/configs/organized/algorithms.json`。新实验须显式创建独立输出计划；已有冻结计划使用独立归档中的原源码和配置。执行、检查和重绘用法见[实验说明](src/experiment/README.md)、[测试说明](src/tests/README.md)及[绘图说明](src/plotting/README.md)。

## 论文目录

| 稿件 | 内容 |
|---|---|
| [C-STMP](paper/README.md) | 当前 GP-MP 算法工作稿、七幅实验图和研究依据 |
| [STMP](paper/STMP/README.md) | 三网络 STMP 稿件及研究文档 |

各稿件的正文、图片、参考文献、术语出处和检查记录均在其自身目录维护。

## 版本与历史

当前执行和模型绑定从 [FINAL.json](FINAL.json)、[算法登记](src/configs/organized/algorithms.json)及具体批次计划核对；[MAINLINE.json](MAINLINE.json) 是保留原文的历史主线记录。候选修改使用独立的实现、配置、权重和结果路径，冻结资产不随日常整理移动。

旧路径通过[结果映射](result/layout_20261021/MAPPING.json)、[论文映射](archive/paper_layout_20261026/MAPPING.json)和[参考资料映射](archive/reference_layout_20261026/MAPPING.json)查找。`src/history/` 仅用于溯源。新增阶段记录写入对应批次或稿件文档，本页保留稳定导航和简短状态。
