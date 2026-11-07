# AFDM-GFRA

面向低轨卫星物联网的 GNSS-independent AFDM 免授权随机接入研究。代码包括多帧 AFDM 观测模型、联合活动检测与信道估计接收机 GP-MP / GP-MP-EP、STMP 与传统基线，以及实验和绘图入口。

[阅读论文](paper/main.pdf) · [完整稿](paper/main_full.pdf) · [运行与复现](REPRODUCING.md) · [代码导读](src/README.md)

## 快速开始

安装 Python 和 [Git LFS](https://git-lfs.com/) 后，在终端运行：

```text
git lfs install
git clone https://github.com/RESET-cpu/afdm-gfra.git
cd afdm-gfra
git lfs pull
python -m pip install -r requirements.txt
python run_experiments.py demo --output result/demo_first
```

`demo` 是无需权重的单场景 AFDM 最小二乘示例，用于检查环境。运行真实 GP-MP 接收机的单场景命令见[运行指南](REPRODUCING.md)。项目直接通过根目录脚本运行。

## 阅读入口

| 内容 | 位置 |
|---|---|
| 当前论文、LaTeX 编译 | [paper](paper/README.md) |
| 模块分工、算法和配置 | [src](src/README.md) |
| 新实验的计划、运行和汇总 | [实验说明](src/experiment/README.md) |
| 已采用结果与待完成实验 | [实验索引](result/README.md) |
| 论文图的数据来源与复现范围 | [逐图说明](paper/docs/REPRODUCTION.md) |
| 模型文件及校验值 | [权重清单](src/configs/release/weights.json) |

公开仓库包含代码、配置、论文、正式图表、小型汇总和八个 Git LFS 模型资产。原始训练数据、逐场景预测及部分历史资产保留在本地；完整重新训练和历史批次复现的条件见运行指南。当前稿件仍有实验曲线待替换，采用状态统一在实验索引维护。

原创代码保留版权，第三方代码保留原许可与署名，见 [RIGHTS.md](RIGHTS.md)。
