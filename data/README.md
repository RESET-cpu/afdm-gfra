# 当前训练数据

`proposed/` 保存 50,000 个训练信道、5,000 个验证信道、场景/用户标识、矩统计和先验定义。
这些是原训练库的实际副本，SHA 与当前冻结网络所绑定的数据一致。

入口使用 [configs/training/proposed.json](../configs/training/proposed.json) 中的相对路径，
不读取 `prior_definition.json` 内保留的历史绝对路径。先验文件自身保持原字节内容，
因此其 SHA 及分类器内嵌的先验身份仍然一致。

数据生成实现位于 `experiment/training/proposed/data.py`。另建数据库时使用新的输出目录：

```sh
.venv/bin/python -B scripts/train_proposed.py --stage data --output runs/proposed_bank
```

新库的先验定义写入该输出目录。后续训练显式传入 `--prior runs/proposed_bank/prior_definition.json --data-dir runs/proposed_bank`。
生成数据需要完整的计算和磁盘预算；本次整理复用了原数据。
