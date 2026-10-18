# JADCEDD 云端工作副本

**Generative-Model-Aided Grant-Free Random Access for GNSS-Independent MIMO-AFDM Satellite IoT Systems**

这是 2026-10-18 从本地研究项目导出的独立工作副本，用于 Codex Cloud 中的代码修改、论文修订和小规模 CPU 验证。
算法源码、配置、当前冻结推断权重和论文正文均按原文件复制；导出清单及源文件 SHA-256 见 [EXPORT_MANIFEST.json](cloud/EXPORT_MANIFEST.json)。
云端说明、Git 配置与 AGENTS.md 第 8 条适配了这个独立副本，未回写本地项目。

## 文件与研究状态

- `src/`：物理模型和接收机；`configs/`：当前冻结配置。
- `experiment/`：八项实验入口，详见 [实验说明](experiment/README.md)。
- `models/proposed/`：一阶、二阶及活动分类器冻结权重；`models/gnn/`：GNN 基线权重。通过 Git LFS 保存。
- `paper/main.tex`、`paper/main.pdf`：当前论文；第 I–V 章及附录已有稿件，实验章节待正式结果齐备后撰写。
- `docs/`：推导、术语依据、主线与来源记录；第三方代码归属见 [ATTRIBUTION.md](docs/ATTRIBUTION.md)。
- `results/baseline_comparison_500_20261018/`：已完成的比较报告、图与汇总表。

完整训练数据、仍在更新的 `runs/`、旧归档、历史逐场景原始结果和论文历次构建记录保留在本地。
部分历史文档中的链接因而只适用于完整本地项目；`MAINLINE.json` 保留原始溯源信息。
当前上传的是已有冻结权重，5,000/50,000 样本的新网络仍在本地训练。
**正式密度比消融等待新网络完成后运行。** 本副本的检查不产生论文性能结论。

## Codex Cloud 环境

连接本私有 GitHub 仓库，在环境准备阶段运行：

```sh
bash cloud/setup.sh
```

需要 Python 3.10–3.13、Git LFS，以及访问 GitHub LFS、PyPI 和 PyTorch CPU 包索引的网络。
安装脚本使用 CPU PyTorch 2.7.1、NumPy 2.2.1、SciPy 1.15.1，加载 LFS 权重并检查核心流程。
如果 Git LFS 未预装，先通过环境的包管理器安装 `git-lfs`，再重跑脚本。
完成准备后保存并发布云端环境。后续检查：

```sh
python cloud/check.py
```

检查包括三网络权重绑定、两个合成输入的实际网络前向计算、7 项核心测试，以及单场景消融计划生成；不启动完整接收机批量实验。
运行记录写入忽略提交的 `cloud/VALIDATION.local.json`。

## 小规模实验

由于云端没有历史逐场景结果，创建计划时显式使用 `--fresh`，并使用新输出目录：

```sh
python experiment/density_ratio_ablation.py plan --output results/cloud_smoke --scenes 1 --values 0 --device cpu --fresh
# 如需执行这个单场景检查，再运行：
python experiment/density_ratio_ablation.py run --output results/cloud_smoke
```

单场景只能检查流程。正式对照必须绑定同一版本的三网络、固定协议并保留全部计划场景。
完整训练和大规模实验继续在本地计算资源上运行；本副本不会同步或接管本地训练进程。

## 论文

编辑 `paper/sections/` 与 `paper/references.bib`。环境有 Tectonic 时可运行：

```sh
cd paper
tectonic main.tex
```

已附当前阅读版 PDF。论文中的术语及出处统一维护于 `docs/TERMINOLOGY.md`。
