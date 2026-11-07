"""Write navigation and expose saved figures; no inference or source-result edits."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[3]
RECORD = ROOT / 'paper/docs/result_layout_20261023'
PLAN = json.loads((RECORD / 'PLAN.json').read_text(encoding='utf-8'))
LABELS = dict(snr_comparison='SNR 对比', pilot_frames='导频帧数', user_count='用户数量',
              activity_probability='活动概率', cross_channel='跨信道', channel_denoising='独立去噪',
              runtime_comparison='运行时间与精度', density_ratio_ablation='密度比消融')
NOTES = {
    'snr_comparison': '当前为已知相位、估计噪声的 STMP 与四个 baseline 主实验；2000 场景仍在运行。interim_500 是固定前 500 个场景的已审核快照。',
    'channel_denoising': 'current 为 Mac 上传并审核通过的历史九曲线去噪实验：500 场景，每场景 4 个候选信道。Proposed 是一阶去噪器，不是十层展开接收机。',
    'runtime_comparison': '尚无本轮正式运行时间结果。并发 SNR 主实验的吞吐时间不能直接作为独立方法时延。',
    'density_ratio_ablation': '本项暂缓；保留历史记录和之前的计划，不表示已执行本轮实验。',
}


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


exports = []
for link in PLAN['data_links']:
    source = Path(link['path'])
    relative = source.relative_to(ROOT / 'result')
    experiment = relative.parts[0]
    entry = Path(*relative.parts[2:])
    pictures = sorted(p for p in source.iterdir() if p.is_file() and p.suffix.lower() in {'.pdf', '.svg', '.png'})
    if not pictures:
        continue
    destination = ROOT / 'result' / experiment / 'figures'
    destination = destination / ('mac_original' if experiment == 'channel_denoising' and entry.as_posix() == 'current'
                                 else 'history/' + entry.as_posix().removeprefix('history/'))
    destination.mkdir(parents=True, exist_ok=True)
    entries = []
    for original in pictures:
        output = destination / original.name
        expected = digest(original)
        if output.exists():
            assert digest(output) == expected, output
        else:
            shutil.copy2(original, output)
        assert digest(output) == expected, output
        entries.append(dict(source=str(original), output=str(output), sha256=expected))
    write_json(destination / 'PROVENANCE.json', dict(kind='unchanged_saved_figure_copy', files=entries))
    exports.extend(entries)

for name in PLAN['experiments']:
    data = ROOT / 'result' / name / 'data'
    figures = ROOT / 'result' / name / 'figures'
    links = [item for item in PLAN['data_links'] if Path(item['path']).is_relative_to(data)]
    index = []
    for item in links:
        path = Path(item['path'])
        index.append(dict(entry=path.relative_to(data).as_posix(), status=item['status'],
                          original_target=item['target'], resolved_target=str(path.resolve()),
                          summary_available=(path / 'SUMMARY.json').is_file(),
                          plan_available=(path / 'PLAN.json').is_file()))
    write_json(data / 'INDEX.json', dict(experiment=name, label=LABELS[name],
               generated_utc=datetime.now(timezone.utc).isoformat(), entries=index,
               note='Directory entries preserve source protocols; a stored plan or partial output is not a completed experiment.'))
    lines = [f'# {LABELS[name]}数据', '', NOTES.get(name, '尚无本轮 STMP 正式结果；以下保留不同协议的旧计划与历史记录。'), '',
             '| 入口 | 保存的状态 | 汇总文件 |', '|---|---|---|']
    for item in index:
        entry = item['entry']
        lines.append(f"| [{entry}]({entry}/) | `{item['status']}` | {'有' if item['summary_available'] else '无'} |")
    lines += ['', '有 SUMMARY.json 不代表结果完整；以文件内状态、计划和配对审核为准。',
              '`planned_2000_ten_layer/` 为旧十层计划，本次未启动。',
              '原始协议、方法名、场景身份与汇总数值保持原文；不得跨协议拼接。',
              '实际来源见 [INDEX.json](INDEX.json)。']
    (data / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    lines = [f'# {LABELS[name]}图片', '', f'独立绘图入口：`src/evaluation/plots/{name}.py`。',
             '新图保存到本目录的独立版本文件夹，读取相邻 data/ 内的已审核结果。', '']
    if (figures / 'current').exists():
        label = '500/2000 场景中期结果，11 pt 轴字号、6 pt 标记' if name == 'snr_comparison' else 'Mac 九曲线去噪结果，当前统一论文版式'
        lines += [f'[当前图片](current/)：{label}。', '']
    else:
        lines += ['尚未生成本轮正式论文图；本次只建立目录，未计算实验或生成模拟曲线。', '']
    for folder in sorted(p for p in figures.iterdir() if p.is_dir() and p.name != 'current'):
        lines.append(f'- [{folder.name}]({folder.name}/)')
    lines += ['', '`history/` 与 `mac_original/` 仅收录原有图片的逐字节副本，不代表采用新版式。',
              '图片应与对应 PLAN.json、SUMMARY.json 及来源记录一起引用。']
    (figures / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')

write_json(RECORD / 'FIGURE_EXPORTS.json', exports)
write_json(RECORD / 'MAPPING.json', dict(moves=PLAN['moves'], data_entries=PLAN['data_links'],
           current_figures={name:str((ROOT/'result'/name/'figures/current').resolve())
                            for name in ('snr_comparison','channel_denoising')},
           preserved_in_place=PLAN['protected_original_directories']))
archive = Path(PLAN['archive'])
(archive / 'README.md').write_text(
    '# 历史结果归档\n\n97 个非当前的旧 result 顶层目录保留在此；未删除历史数据。\n'
    '八项论文实验的统一入口为 ../../result/README.md，各项 data/history/ 链接到相关历史结果。\n'
    '旧 result/<原目录名>/ 路径仍通过隐藏目录链接兼容。\n'
    '移动前后的路径表见 ../../paper/docs/result_layout_20261023/MAPPING.json。\n'
    '历史文件中的相对路径可能仍依赖旧目录位置；执行旧脚本应检查其原协议与路径。\n', encoding='utf-8')
print(json.dumps(dict(experiments=len(PLAN['experiments']), figure_copies=len(exports)), ensure_ascii=False))
