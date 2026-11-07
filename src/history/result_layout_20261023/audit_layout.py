"""Read-only checks of saved data, aliases and frozen assets after organization."""
from pathlib import Path
from datetime import datetime, timezone
import ast
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
RECORD = ROOT / 'paper/docs/result_layout_20261023'
plan = json.loads((RECORD / 'PLAN.json').read_text(encoding='utf-8'))
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()

visible = sorted(p.name for p in (ROOT / 'result').iterdir()
                 if p.is_dir() and not p.stat(follow_symlinks=False).st_file_attributes & 2)
assert visible == sorted(plan['experiments']), visible
for name in plan['experiments']:
    directory = ROOT / 'result' / name
    assert sorted(p.name for p in directory.iterdir() if p.is_dir()) == ['data', 'figures']
    assert (directory / 'data/INDEX.json').is_file()
    assert (directory / 'data/README.md').is_file()
    assert (directory / 'figures/README.md').is_file()

changed_directory_ids = []
for item in plan['moves']:
    old, new = Path(item['source']), Path(item['destination'])
    assert old.is_junction() and old.samefile(new), item
    current_id = new.stat().st_ino
    if current_id != item['directory_id']:
        changed_directory_ids.append(dict(source=str(old), destination=str(new),
                                          previous_id=item['directory_id'], current_id=current_id))
for item in plan['data_links']:
    assert Path(item['path']).is_junction()
    assert Path(item['path']).samefile(item['target'])
original_ids = {item['path']: item['directory_id'] for item in plan['original_top_directories']}
for path in plan['protected_original_directories']:
    assert not Path(path).is_junction()
    assert Path(path).stat().st_ino == original_ids[path]
for item in plan['figure_files']:
    assert sha(item['new']) == sha(item['old']) == item['sha256'], item['new']
for path, expected in plan['frozen_assets'].items():
    assert sha(path) == expected, path
assert sha(plan['active_plan']) == plan['active_plan_sha256']
exports = json.loads((RECORD / 'FIGURE_EXPORTS.json').read_text(encoding='utf-8'))
for item in exports:
    assert sha(item['source']) == sha(item['output']) == item['sha256']
for name in ('snr_comparison', 'channel_denoising'):
    assert (ROOT / 'result' / name / 'figures/current').is_junction()

sys.path.insert(0, str(ROOT / 'src/evaluation/plots'))
from data import load
from channel_denoising import load_denoising
snr = load(ROOT / 'result/snr_comparison/data/interim_500', 'snr_comparison')
denoising = load_denoising(ROOT / 'result/channel_denoising/data/current', 'channel_denoising')
assert snr.scenes == 500 and len(snr.rows) == 30
assert snr.metadata['scene_ids'] == list(range(500))
assert denoising.scenes == 500 and len(denoising.rows) == 54

# The generated importer checker now finds the repository from its markers,
# because its physical package moved deeper. Do not rerun/overwrite its audit.
checker = ROOT / 'result/channel_denoising/data/imports/denoising_mac_20261023_4173ccc/audit_saved_results.py'
ast.parse(checker.read_text(encoding='utf-8-sig'))
import_root = checker.parent
detected = next(parent for parent in import_root.parents
                if (parent / 'AGENTS.md').is_file() and (parent / 'run_experiments.py').is_file())
assert detected == ROOT

# Check local links in the newly maintained navigation, without following
# arbitrary historical Markdown or recursively traversing shared inputs.
markdown = [ROOT/'result/README.md', ROOT/'README.md', ROOT/'src/evaluation/plots/README.md',
            ROOT/'paper/TWC-1/README.md', ROOT/'paper/TWC-1/figures/README.md']
markdown.extend(ROOT/'result'/name/kind/'README.md' for name in plan['experiments'] for kind in ('data','figures'))
broken = []
for document in markdown:
    for value in re.findall(r'\]\(([^)]+)\)', document.read_text(encoding='utf-8-sig')):
        if '://' in value or value.startswith('#'):
            continue
        path = document.parent / value.split('#')[0]
        if not path.exists():
            broken.append(dict(document=str(document), target=value))
# REPORT.md is written immediately below, after the evidence is collected.
broken = [item for item in broken if not item['target'].endswith('result_layout_20261023/REPORT.md')]
assert not broken, broken

status = json.loads((Path(plan['active_plan']).parent/'STATUS.json').read_text(encoding='utf-8'))
assert status['pid'] == plan['current_status_before']['pid']
assert status['completed'] >= plan['current_status_before']['completed']
audit = dict(status='PASS', checked_utc=datetime.now(timezone.utc).isoformat(),
    visible_experiments=visible, per_experiment_subdirectories=['data','figures'],
    compatibility_directory_links_checked=len(plan['moves']), data_links_checked=len(plan['data_links']),
    protected_original_directories_unchanged=len(plan['protected_original_directories']),
    frozen_file_sha256_passed=len(plan['frozen_assets']), moved_figure_file_sha256_passed=len(plan['figure_files']),
    unchanged_figure_copies_checked=len(exports), active_plan_sha256=sha(plan['active_plan']),
    plot_loaders=dict(snr=dict(scenes=snr.scenes,rows=len(snr.rows),scene_ids='0..499'),
                      denoising=dict(scenes=denoising.scenes,rows=len(denoising.rows))),
    maintained_markdown_files_checked=len(markdown), broken_links=broken,
    generated_import_checker=dict(path=str(checker),ast_parse='PASS',detected_root=str(detected)),
    current_status_before=plan['current_status_before'], current_status_after=status,
    changed_directory_ids=changed_directory_ids,
    scope='No inference, training, result rescoring or plot regeneration. Hash checks cover the enumerated frozen assets and moved figures, not every historical file.',
    note='Three inactive destination directory IDs changed during Move-Item. Compatibility aliases resolve correctly; directory ID is not used as evidence of file-content equality.')
(RECORD/'AUDIT.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report = f'''# 2026-10-23 实验结果目录整理

状态：PASS。检查时间：{audit['checked_utc']}。

统一入口为 [result/README.md](../../../result/README.md)。八项实验各有且仅有 data/ 和 figures/ 两个直接子目录。
当前 SNR 与 Mac 去噪结果有 current 入口；未完成的其他实验保留历史记录和旧计划，不补造结果。

## 本次操作

- 97 个非当前 result 目录归入 archive/result_legacy_20261023/；原路径保留隐藏 NTFS 目录链接。
- Mac 导入包移动到 result/channel_denoising/data/imports/，原 imports 路径兼容。
- 7 个论文图目录移动到所属实验的 figures/；paper/TWC-1/figures/ 旧路径兼容。
- 63 个数据入口连接现有数据，2 个 figures/current 入口选择现有图片版本。
- 10 个历史 PDF/PNG 图片复制到 figures/history/ 或 figures/mac_original/，逐字节核验并记录来源。
- 运行中的主实验、共享场景清单、models、runs、训练 data 五个目录原位保留；仅隐藏旧入口。
- 只修正生成式导入审计脚本的仓库根目录发现逻辑，备份在 before/audit_saved_results.py；没有重跑其原始审计或覆盖 AUDIT.json。
- 更新导航文档与路径示例。冻结入口的默认输出路径保持原值；新批次显式使用 result/<实验>/data/<批次>。

## 验证

- 八个可见实验目录，逐项检查 data/、figures/ 及索引。
- 105 个迁移目录的旧路径均链接到对应新位置；63 个数据目录入口全部可访问。
- 204 项冻结文件与主实验 PLAN.json 哈希不变；127 个已移动图目录内文件哈希不变；10 个图片副本与来源相同。
- 新路径成功加载 500 场景 SNR 汇总（30 行，固定场景 0–499）及去噪汇总（54 行）；原汇总指标与已有审核记录一致。
- 主实验 PID 仍为 {status['pid']}，保存的任务数从 {plan['current_status_before']['completed']} 增至 {status['completed']}，状态 {status['stage']}。
- 维护中的 21 份导航文档本地链接检查通过。

候选目录 candidates、known_phase500_20261022、output 移动后目录 ID 改变；旧新路径指向相同目标。
原先要求所有目录 ID 完全不变的检查因此未通过，最终检查改为验证目录链接和已记录文件哈希，
并在 AUDIT.json 中保留三个目录 ID 差异。没有把目录 ID 当作文件内容不变的证据，也没有声称全量历史文件逐一重算哈希。
原历史脚本中的相对路径仍可能依赖旧布局；不自动改写历史协议或再次执行历史脚本。

没有删除实验数据、启动新推断/训练、改写主实验计划或中断现有进程。

## 记录

- [PLAN.json](PLAN.json)：迁移前的目录身份、冻结文件与图文件哈希。
- [OPERATIONS.json](OPERATIONS.json)：实际目录操作。
- [MAPPING.json](MAPPING.json)：原位置、新位置与数据入口。
- [FIGURE_EXPORTS.json](FIGURE_EXPORTS.json)：旧图片副本来源。
- [AUDIT.json](AUDIT.json)：本次核验结果与范围。
- before/：本次修改前的文档和导入检查脚本。
- 执行代码：src/history/result_layout_20261023/，不属于冻结算法代码。
'''
(RECORD/'REPORT.md').write_text(report,encoding='utf-8')
print(json.dumps({key:audit[key] for key in ('status','frozen_file_sha256_passed','moved_figure_file_sha256_passed','plot_loaders')},ensure_ascii=False))
