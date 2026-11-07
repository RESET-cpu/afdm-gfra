# 场景

- `geometry.py`、`geometry_consistent.py`、`scene_generator.py`：几何与物理路径采样。
- `generate.py`：已知相位的配对观测、真值和元数据。
- `unknown_phase.py`：给接收机提供原始导频；相位真值单独保留。
- `profiles.py`：NTN-TDL-A/B/C/D 条件；从原实验目录归入场景模块。
- `catalog.py`：保存场景编号、种子和条件键；从原实验目录归入此处。
- `continuous.py`：物理路径到参考有效信道与跨帧相位的连接。

`generate_case` 返回公开输入、真值、元数据三个对象。接收机不得通过场景生成器读取真值；评分在实验层完成。正式实验仍使用对应计划指定的场景及种子，新诊断使用独立种子。
