# 主SNR图加入选定的估计相位结果

本图沿用主SNR实验的NMSE/AER双子图、字体、网格和原六种方法样式，增加
`physical_no_hypotheses_legacy_stop` 的完整估计相位结果。红实线空心圆为
GP-CCD-MP-DRE已知相位参照，红虚线空心三角为GP-CCD-MP-DRE估计相位版本。
STMP和四种基线均为已知相位；所有方法使用观测估计噪声。

所有曲线统一使用场景0–499，每档500场景，SNR为−4、−2、0、2、4、6 dB。
原主图的六条1000场景曲线重新从已保存逐场景记录汇总，NMSE采用总误差能量/
总信号能量，AER采用总错误判决数/总判决数。基线继续使用冻结的活动读出阈值，
没有重新拟合、推断或训练。

六方法原结果来自 `result/snr_comparison/data/c_stmp_variance_em_1000_snr_m4_p6_20261025`；
新增结果来自已完成且核验通过的 `result/snr_comparison/data/c_stmp_phase_selected_500_20261030`。
六档已知相位GP-CCD-MP-DRE的重新汇总值与本次相位实验的已知相位配对参照一致；
所有方法的信号能量、活动及非活动总数一致。原有限未收敛输出保留，新相位版本包括1份达到上限的输出。
本批含13个参与相位选择的场景，是回顾性比较，不宣称独立测试集。

这是用于查看新增曲线的主实验对照图；论文现有1000场景图及正文没有替换。
正式采用前需同步论文中的相位条件、样本数、图注及相应实验分析。

## 文件与复现

- `snr_comparison.pdf`：矢量图，宽3.5英寸、高2.2英寸。
- `snr_comparison.png`：360 dpi图像；`pdf_preview.png`是PDF的300 dpi实际渲染。
- `PLOT_DATA.json`、`SNR.csv`：42组统计，七方法×六档SNR。
- `CONFIG.json`：绘图样式与图例配置。
- `VALIDATION.json`：84个绘图点与源数据一致、图例不覆盖曲线、原资产哈希未变。
- `KNOWN_PHASE_500.json`：六方法重新汇总的缓存，绑定源文件和读取代码哈希。

在项目根目录运行：

```powershell
& .\.venv\Scripts\python.exe -B result/snr_comparison/figures/phase_selected_main_500_20261102/render.py
```

首次运行核验并读取冻结基线预测；后续重绘从有来源哈希绑定的汇总缓存读取。
