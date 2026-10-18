# 2026-10-11 代码整理前快照

用户要求各 baseline 与 proposed 各保留一个当前实现，并整理代码结构。
执行前保存了 563 个文件，共 5,210,881 字节；逐字节校验记录见
[`SNAPSHOT.json`](SNAPSHOT.json)。快照包含当时未提交的修改，未按 Git HEAD 回退。

`workspace/` 保存整理前的源码、脚本、配置、测试、文档及日期实验文本。
大型数据、权重、结果、参考文献、论文和虚拟环境通过相对链接指向项目原位置；
它是源码工作区快照，不是包含全部历史数据的独立备份。
这些共享资产的可用性仍取决于其原位置。

```sh
.venv/bin/python -B archive/code_consolidation_20261011/run_legacy.py run.py info
.venv/bin/python -B archive/code_consolidation_20261011/run_legacy.py scripts/train_scores.py --inspect
```

`run_legacy.py` 使用快照源码、工作目录及配置执行指定相对脚本。
运行历史实验仍会访问原结果目录；只读复核与创建新输出的语义由各原脚本决定。
本次整理没有运行历史实验队列。

当前映射见[代码说明](../../docs/CODE_GUIDE.md)，迁移记录见
[`MIGRATION.json`](../../results/code_consolidation_20261011/MIGRATION.json)，
验证见 [`VERIFICATION.json`](../../results/code_consolidation_20261011/VERIFICATION.json)。
旧 receiver、投影/解析对照、旧 SMV/EM 变体及相关测试均保存于此快照，
当前测试保留所选算法的公式检查，并增加迁移前后的一致性验证。
