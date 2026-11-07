# 绘图配置

[manuscript.json](manuscript.json) 登记当前十幅论文图的数据路径、哈希、曲线和样式，由 [render_paper.py](../../plotting/render_paper.py) 读取。命令见[绘图说明](../../plotting/README.md)，图号与采用状态见[逐图复现说明](../../../paper/docs/REPRODUCTION.md)。

论文图路径以仓库根目录为基准。采用新结果前应核对样本范围、配对条件和来源，再更新绑定。每幅方法图单独声明所需素材，因子图无需其他方法图的文献或示例数据。

其余九个文件是通用绘图模板，复用 `plotting/configurable.py` 的共同样式；调用时须明确给出 `--input` 和 `--output`，不再默认指向旧实验。模板中的相对路径以配置文件所在目录为基准。
