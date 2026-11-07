from pathlib import Path
items={
'README.md':'2026-11-07 后续：白噪声去噪 12000 个查询已核验，图 4 和图 3 示例已采用，两版工作稿同步。继续导频数阶段。[采用记录](paper/C-STMP/checks/white_denoising_adopted_20261107/README.md)。',
'paper/C-STMP/figures/README.md':'2026-11-07 后续：图 4 的 GP-MP 六个点及图 3 的同场景示例已采用白噪声输出，其他曲线和样式保持；现仅图 7–10 待逐项替换。[采用核验](../checks/white_denoising_adopted_20261107/README.md)。',
'src/evaluation/plots/manuscript/README.md':'2026-11-07 后续：图 4 绑定 `result/channel_denoising/figures/white_mainline_500_20261107/PLOT_DATA.json`，图 3 绑定同目录 `scene000_example.npz`。500 场景去噪已重评分核验，原图源保持；白噪声后续扫描已获作者授权，当前阶段见 `result/white_followup_20261107/REQUEST.json`。'}
for name,paragraph in items.items():
    p=Path(name);s=p.read_text(encoding='utf-8-sig');first,rest=s.split('\n',1);p.write_text(first+'\n\n'+paragraph+'\n'+rest,encoding='utf-8')
