# 信道、观测与公共输入

| 文件 | 职责 |
|---|---|
| `config.py`、`core/` | 物理参数、阵列配置、数据类型与约定 |
| `physics.py`、`dictionary.py` | 物理信道及基准使用的字典 |
| `atoms.py`、`phase_atoms.py` | 路径响应及导数；从原接收机前端目录归入信道模块 |
| `pilot` 位于相邻 `waveform/` | 导频生成与观测算子的输入 |
| `phase.py`、`noise.py` | 相位算子与观测噪声约定 |
| `observation.py` | `ReceiverInput`、数组哈希与观测构造 |
| `unknown_phase.py` | `UnknownPhaseInput`，原始导频及给定相位下的输入转换 |

这些模块描述物理输入与算子，不负责估计相位或运行迭代接收机。相位估计和噪声估计实现位于 `receiver/frontend/`。
