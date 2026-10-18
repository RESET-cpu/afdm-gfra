# 2026-10-18 测试归档

本目录保存精简前完整 `tests/` 的 110 个源码与支持文件，逐文件 SHA-256 核对后，才移除当前目录中不再默认执行的 44 个旧测试文件、历史检查入口和夹具。当前保留原来的 6 个测试文件，另新增一个核心实验检查文件。

- [归档测试](workspace/tests/)；原文件内容保持不变。
- [文件哈希](../../results/experiment_organization_20261018/TEST_ARCHIVE_SHA256.json)与[保留／归档清单](../../results/experiment_organization_20261018/TEST_SELECTION.json)。
- `workspace/` 通过链接使用当前项目依赖，本归档不是独立冻结的运行环境。

仅在需要复核旧实现时，显式指定归档测试：

```sh
.venv/bin/python -B -m pytest archive/tests_20261018/workspace/tests
```

需要恢复某个文件时，将其从 `workspace/tests/` 复制回项目 `tests/`，先检查同名文件，避免覆盖后续改动。旧测试并非全部无用；涉及某个旧算法或训练流程的修改时，应恢复对应检查。
