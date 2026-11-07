"""Apply the individually reviewed wording changes to the saved manuscript units."""
from pathlib import Path
import json

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[1]
units = {u['id']: u for u in json.loads((RUN/'UNITS.json').read_text(encoding='utf-8'))}
revised = {i: u['text'] for i, u in units.items()}
changes = []

def edit(i, old, new, reason, evidence='本文公式/操作语义；普通描述，不作为文献中的方法名称'):
    assert revised[i].count(old) == 1, (i, old, revised[i].count(old))
    revised[i] = revised[i].replace(old, new)
    changes.append(dict(unit=i, file=units[i]['file'], old=old, new=new,
                        reason=reason, evidence=evidence))

edit(6, 'Euclidean norm of all matrix or tensor entries', 'Frobenius norm',
     '采用矩阵/张量范数的标准名称，避免绕行解释。', 'Shen，Notation，PDF p.3；本文沿用到张量所有元素的平方和')
edit(13, 'received-symbol delay position', 'the position of the received symbol along the delay dimension',
     '三个索引中第三个是接收符号的延迟维位置；旧压缩搭配不自然。', 'Shen，II-B，PDF p.4，received symbol position along the delay dimension')
edit(13, 'an inverse DFT and two diagonal chirp multiplications',
     'an inverse DFT and multiplications by two diagonal chirp matrices',
     'diagonal 修饰矩阵，不是 multiplication。', 'Bemani，II-B，式(16)：IDAFT 的两个对角 chirp 矩阵')
edit(13, 'For the stationary-device channel considered here,', 'For the stationary devices considered here,',
     'stationary 的对象是终端；此处不需要另造 channel 类别。')
edit(16, 'structured compression matrices', 'structured sensing matrices',
     '与本段 sensing matrices 的对象和用词一致；不增加引文。', 'Cai，III-A/V；保留此前作者指定的无 Wei 标号句，不将本次一致性编辑当成新增文献验证')
edit(18, 'The resulting formulation\ncollects additional pilot observations', 'Additional pilot frames\nprovide more observations',
     '提供更多观测的是新增导频帧，不是 formulation。')
edit(21, 'the learning of channel and activity denoisers', 'the learned channel denoiser and activity classifier',
     '活动概率由分类器估计；与第四章实际模型名称一致。', 'Cai，IV：channel denoising；Menon，§2/§4.2：classification 与 density ratio estimation')
edit(27, '$g_{k\\ell}$ is the path gain of the $\\ell$th path, and', '$g_{k\\ell}$ is the path gain of the $\\ell$th path,',
     '删除并列定义中重复的 and。')
edit(27, '$\\widetilde\\tau_{k\\ell}$ and $\\tau_c$ are denoted as\npropagation delay and common delay, respectively.',
     '$\\widetilde\\tau_{k\\ell}$ and $\\tau_c$ denote the\npropagation delay and common delay, respectively.', '符号 denote 物理量，旧句把指代关系写反。')
edit(32, 'The time-domain transmitted signal is generated through the inverse\ndiscrete affine Fourier transform (IDAFT) applied to $\\mathbf p_{qk}$,\nmathematically formulated as',
     'Applying the inverse discrete affine Fourier transform (IDAFT) to\n$\\mathbf p_{qk}$ gives the time-domain transmitted signal', '直接描述变换与输出，删去重复引式套语。')
edit(34, 'chirp-periodic prefix (CPP) length', 'chirp-periodic prefix (CPP) duration',
     '下文比较 N_CPP*T_s 与秒制时延，应为持续时间；参数表 N_CPP 仍是样点长度。', '本文 CPP 不等式；Shen，II-B，PDF p.4：CP time duration')
edit(38, 'The pilot symbols including this phase rotation are given by',
     'Incorporating this phase rotation into the pilot matrix gives', 'A 是引入相位后的矩阵，不把原始发送符号 P 与 A 混称。')
edit(39, 'the same useful-symbol\nenergy', 'the same energy in the useful symbols', '展开压缩修饰语，保留能量对齐条件。')
edit(41, 'Each device determines whether to access the channel in an independent\nand identically distributed (i.i.d.) manner.\nWe use a binary activity variable $\\alpha_k$, defined as',
     'We model device activities as independent and identically distributed\n(i.i.d.) binary variables. For device $k$, define $\\alpha_k$ as',
     'i.i.d. 描述随机变量，不描述设备作决定的 manner。', 'Cai，II 中 Bernoulli activity 模型；本文推断模型保持')
edit(50, 'Each likelihood factor uses the corresponding', 'Each likelihood factor depends on the corresponding', '因子图表达概率因子对变量的依赖。')
edit(56, 'For any device tensor $H_k$', 'For the channel tensor $H_k$', '张量表示信道，不表示设备。')
edit(58, 'the normalized\nconditional posterior', 'the posterior distribution', '活跃条件已在首句说明；不重复叠加限定。')
edit(62, 'the active-channel posterior', 'the channel posterior under the active hypothesis', '将 active 对应假设明确写出，避免类别式拼接。')
edit(63, 'To obtain the spatial covariance', 'To compute the posterior covariance across antennas', '明确协方差的变量维度及后验含义。')
edit(63, 'Averaging the resulting covariance over the $N^2$ channel entries gives', 'Averaging over the $N^2$ channel entries per antenna gives', '重排均值不直接产生协方差；明确平均的索引。')
edit(67, 'Section~\\ref{sec:learning} learns the channel mean, variance, and\nactivity probability from channel samples.',
     'Section~\\ref{sec:learning} describes learned estimators for the channel\nmean, variance, and activity probability.', '章节不能执行学习；方差由已学去噪器的导数估计。')
edit(68, 'Learning Channel and Activity Denoisers', 'Learning Channel Denoising and Activity Detection', '标题同时覆盖去噪器和活动分类器，不混称两个 denoisers。')
edit(71, 'an independent proper\ncomplex Gaussian perturbation with covariance $\\mathbf C\\succ0$, giving the real\nobservation',
     'a proper complex Gaussian\nperturbation independent of $H$, with covariance $\\mathbf C\\succ0$.\nThe real observation is', '明确 independence 的对象，避免误读为各坐标独立而与有色噪声矛盾。')
edit(77, 'is a mean function', 'is a denoiser', '此函数是参数化去噪器；不用含义过泛的 mean function。', 'Cai，IV-A/B；Karras，§5 的 denoiser 与 preconditioning')
edit(78, 'over unrestricted mean functions', 'over all estimators of $\\mathbf h_{\\mathbb R}$ from $\\mathbf u$',
     '最小化范围是估计函数，不是另一个名为 mean functions 的类别；保留无限函数类条件。')
edit(79, 'sampling law for $v$', 'sampling distribution of $v$', '使用明确常见的分布表述；law 并非错误或不存在。')
edit(80, 'complex mean map', 'complex-valued denoiser', '与 f_theta 的操作及数学类型一致，不另起 map 名称。')
edit(80, 'scalar-variance message', 'input message', '噪声协方差 vI 已在同句给出，无需制造消息类别。')
edit(83, 'the variance per complex coordinate', 'the average conditional variance per complex coordinate', 'tr(P)/D 是各坐标条件方差的平均，不等同于每个坐标方差。', 'Dytso，Prop.1；本文 trace/D 定义')
edit(84, 'We estimate this trace using Monte Carlo finite differences\n\\cite{metzler2016}, with $f_\\theta$ in place of the conditional\nmean.',
     'We approximate the derivatives by finite differences and estimate the\ntrace by Monte Carlo averaging \\cite{metzler2016}, with $f_\\theta$ in\nplace of the conditional mean.', '拆开求导近似与随机迹估计两项操作，不将组合包装为方法名。', 'Metzler 作者稿，V-B Monte Carlo method，PDF p.15；随机符号和中心差分仍为本文公式')
edit(88, 'sampling law for $v$', 'sampling distribution of $v$', '与有色训练段落统一。')
edit(89, 'At the population optimum over unrestricted logits, this loss recovers the\nposterior log odds under the training distribution:',
     'The minimizer of the expected loss over all functions of $(R,v)$ is\nthe posterior log odds under the training distribution:', '优化对象是 logit 函数；将 population optimum 的技术压缩改成具体数学陈述。', 'Menon，§2.1–2.2，PDF p.2，expected risk/Bayes-optimal scorer/logistic link；§4.2')
edit(90, 'through this Bayes correction', "through Bayes' rule", '实际操作是代入先验的 Bayes 公式，与前文和图标一致。')
edit(94, 'mean-network illustration', 'denoiser illustration', '图中的功能是去噪，统一名称。')
edit(95, 'common conditional variance', 'common variance estimate', '这里是跨设备平均并加下限后的估计量。')
edit(96, 'Dividing the Gaussian approximation with mean', 'Dividing the Gaussian posterior approximation with mean', '明确被除的分布对象。')
edit(97, 'current Gaussian input likelihood', 'current Gaussian likelihood', '去除 input 的冗余修饰，前文已定义此似然。')
edit(98, 'is the training average\nof $\\norm{H}_F^2/D$', 'is the average\nof $\\norm{H}_F^2/D$ over the training channels', '说明在哪些样本上取平均。')
edit(99, 'Form \\eqref{eq:nonlinear-extrinsic}', 'Compute the extrinsic message in \\eqref{eq:nonlinear-extrinsic}', '计算的是外信息，不是公式编号。')
edit(101, 'Appendix~\\ref{app:frontend} estimates the phases', 'The procedure in Appendix~\\ref{app:frontend} estimates the phases', '执行估计的是方法，不是附录。')
edit(101, 'For noise estimation', 'For noise-variance estimation', '估计对象是 sigma^2，不是噪声样本。')
edit(101, 'spatial sample covariance and noise estimate', 'spatial sample covariance and noise-variance estimate', '与公式对象一致。')
edit(101, 'Under a lower-rank spatial signal plus white noise, this estimate remains\nfixed during MP.',
     'This estimator assumes a low-rank signal covariance and spatially white\nnoise. We keep the estimate fixed during MP.', '低秩修饰协方差；统计假设与固定估计量的算法选择分别表述。', 'Nadakuditi–Edelman，II-A，式(5)–(7)，pp.2626–2627；本文实现')
edit(103, 'the next scale is', 'the updated scaling factor is', 'kappa 是方差缩放因子，不是泛指尺度。')
edit(104, 'the training-channel\nroot mean square $s$', 'the root mean square $s$ of the training-channel entries', '说明 RMS 的取值对象。')
edit(105, 'the same weight', 'the same damping factor', '统一 eta 的名称。', 'Cai，V-B1：damping factor')
edit(108, 'rectangular-pulse OTFS with an identity transmit window', 'rectangular-pulse OTFS without transmit windowing',
     '单位窗表示不加窗；使用具体操作而非 identity window 组合。', 'Zou/Xu 作者稿，II-A/B，式(1)/(4)/(5)，Pi_t=I')
edit(108, 'after transform cancellation', 'after cancelling the consecutive DFT and inverse DFT operations', '明确消掉的是哪些变换。', '同上，F_N^H F_N=I；原文 M/N 与本文 L/N 已重映射')
edit(108, 'Their ordering depends', 'The relative modulation costs depend', 'ordering 的比较对象是复杂度大小。')
edit(110, 'SVD and noise estimation', 'SVD and noise-variance estimation', '统一噪声方差估计对象。')
edit(112, 'supplied phases', 'known phases', '统一相位条件用词。')
edit(112, 'working storage\nis', 'the memory requirement\nis', '改成直接的存储需求描述。')
edit(112, 'pilot/SVD factors', 'the pilot matrix and SVD factors', 'pilot 是矩阵而非 factor；展开斜杠关系。')
edit(115, 'Devices are uniform', 'Devices are uniformly distributed', 'uniform 描述位置分布。')
edit(115, 'determined by the geometry and large-scale effects\ncompensated. The NTN-TDL-D profile \\cite{shen2025} uses\nuniform delay spread $[30,50]$~ns,',
     'determined by the geometry. Large-scale effects are\ncompensated. We use the NTN-TDL-D profile \\cite{shen2025}, with a delay\nspread drawn uniformly from $[30,50]$~ns,', '分开补偿与几何关系；均匀抽样是本实验设置，不是 profile 名称的定义。')
edit(117, 'Independent Bernoulli activities', 'Independent Bernoulli activity variables', 'Bernoulli 分布修饰随机变量。')
edit(117, 'resulting marginal $\\rho', 'resulting marginal activity probability $\\rho', '说明边缘量是概率。')
edit(117, 'clean signal', 'noiseless received signal', 'Y0 是无噪声接收信号；与去噪训练的 clean channel 区分。')
edit(118, 'Doppler support', 'Doppler-shift range', '参数表描述具体取值范围，避免无必要的 support 术语。')
edit(119, 'activity masking', 'multiplication by $\\alpha_k$', '直接写出实际操作，避免未定义 masking 名称。')
edit(119, 'decay $0.999$;\nvalidation loss under fixed noise realizations selects the model.',
     'decay $0.999$.\nWe select the model with the lowest validation loss under fixed noise\nrealizations.', '模型由训练者按验证损失选择，补回实际的最低损失标准。', '已登记训练流程/保存模型；本地训练代码以 validation loss 最低值选 checkpoint')
edit(120, 'Colored training uses the proper complex Gaussian covariance', 'We train with proper complex Gaussian noise of covariance', 'Gaussian/proper 描述随机噪声，不描述协方差矩阵。', 'Neeser，proper complex random processes；Shastri，III-B，DNN Denoiser for Correlated Noise')
edit(121, 'with validation\nmodel selection', 'with model selection based on\nvalidation loss', '说明模型选择依据，展开压缩组合。')
edit(123, 'real/imaginary input maps', 'real and imaginary input maps', '明确两个输入部分。')
edit(123, 'input/output projections use', 'the input and output layers use', '这里具体是卷积层，与后面的条件线性投影区分。')
edit(123, 'flattened real/imaginary entries', 'flattened real and imaginary entries', '展开并列关系。')
edit(124, 'the nominal normalized variance per\nreal coordinate, and $g_\\theta$ is the backbone',
     'the nominal variance per real coordinate after\nnormalization, and $g_\\theta$ is the RefineNet described above', '明确归一化修饰范围及网络指代，避免泛称 backbone。')
edit(125, 'real/imaginary maps', 'real and imaginary maps', '统一表示。')
edit(126, 'fixed AFDM/multiantenna adaptations', 'fixed adaptations to multiantenna AFDM', '展开两个限定词的关系。')
edit(136, 'References are', 'The reference methods are', '此处为比较方法，不是文献条目。')
edit(136, 'Given true path geometry, powers, and line-of-sight gain, the genie\nreports the analytic conditional MSE of the remaining Gaussian gains.',
     'For the genie-aided reference, we compute the analytic conditional MSE\nof the remaining Gaussian gains given the true path geometry, powers,\nand line-of-sight gain.', '执行计算的是研究者；保留 genie 所知真值及条件 MSE 的含义。')
edit(136, 'internal noise update', 'internal noise-variance update', '更新对象是方差。')
edit(137, 'AWGN test noise with known variance', 'AWGN with known variance', 'AWGN 已包含 noise；删除重复词。')
edit(140, 'Table~\\ref{tab:activity-evidence} pools AER', 'Table~\\ref{tab:activity-evidence} reports AER pooled', '表格报告结果，不执行合并计算。')
edit(144, 'the complete receivers', 'the receivers', '此节已明确是 JADCE 接收机，无需重复 complete。')
edit(145, 'compares the iteration trajectories', 'compares NMSE versus iteration', '明确曲线变量。')
edit(147, 'approaches its final accuracy earlier than', 'approaches its final NMSE in fewer iterations than', '指明指标与横轴，不用泛指 accuracy/earlier。')
edit(150, 'improves AER over GP-MP', 'achieves lower AER than GP-MP', '明确误差率越低越好。')
edit(153, 'the candidate population', 'the number of candidate devices', '明确增加的是候选终端数量。')
edit(156, 'remains the most accurate receiver', 'maintains the lowest NMSE', '性能判断限定为图中度量。')
edit(157, 'investigates the effect of pilot-frame\ncount', 'shows the effect of the number of pilot frames', '图展示结果；统一 pilot-frame count 的普通表述。')
edit(159, 'On the tested grid', 'Among the evaluated pilot-frame counts', 'grid 在本文已有时延多普勒含义；这里实际是测试的帧数集合。')
edit(160, 'power-delay and\nfading distributions', 'power delay profiles and\nfading distributions', 'power delay profile 与 fading distribution 是不同对象。')
edit(162, 'outperforms the four sparse-recovery baselines', 'achieves lower NMSE than the four sparse-recovery baselines', '结果限定为本图报告的 NMSE。')
edit(164, 'using a shared\neffective-channel representation to collect additional pilot observations',
     'using a shared\neffective-channel representation to process additional pilot observations', '表示用于处理观测，不自行采集观测。')
edit(167, 'Approximate each\ncandidate device by one dominant path', 'Approximate the channel of each\ncandidate device by one dominant path', '单路径近似的对象是信道。')
edit(168, 'shifts by integer multiples of $N$ change', 'adding integer multiples of $N$ to $d$ changes', '明确被移位的是时延参数。')
edit(169, 'When updating device $k$', 'When updating the parameters of device $k$', '更新的是参数。')
edit(169, 'Coarse correlations initialize candidates.', 'A coarse search based on pilot correlations initializes the candidates.',
     'correlation 是搜索评分，不是 coarse 的抽象对象。', 'phase_estimation.py，coarse_scores/candidates：匹配滤波相关和网格候选选择')
edit(169, 'and refine by L-BFGS-B \\cite{zhu1997}, accepting updates that do not\nincrease the residual beyond numerical tolerance within an interval where the waveform is differentiable.',
     'and refine by L-BFGS-B \\cite{zhu1997} within an interval where the\nwaveform is differentiable. Accept updates that do not increase the\nobjective beyond numerical tolerance.', '可微区间限定搜索；验收比较标量目标而非残差向量。', 'phase_estimation.py，refine/objective/estimate；Zhu，L-BFGS-B 原论文')
edit(169, 'previous position', 'previous parameter estimates', 'position 是实现变量名，实际为 delay/Doppler 参数，不是设备位置。')
edit(171, 'retaining cross-device conditional covariances and the\nconstraint $e^{\\mathrm jq\\beta_k}$',
     'retaining cross-device conditional covariances and imposing inter-frame\nphase rotations of the form $e^{\\mathrm jq\\beta_k}$', '表达式本身不是 constraint，明确相位形式约束。', 'Shen，III-C，式(47)–(54) 为参照；共同斜率形式是本文约束')
edit(172, 'rebuild $\\widehat{\\mathbf A}$ and its SVD', 'update $\\widehat{\\mathbf A}$ and recompute its SVD', '矩阵更新与重新分解分开陈述。')
edit(174, 'Integer phase factors cancel because', 'Factors with phases equal to integer multiples of $2\\pi$ are one because', '不是相位因子为整数，也不是与另一个因子抵消；指数为 2pi 整数倍才等于一。')
edit(175, 'The remainder of $d$ determines', 'The value $d\\bmod N$ determines', '明确模数。')
edit(175, 'delays extending over multiple useful-symbol periods', 'delays exceeding $N$ samples', 'useful-symbol period 容易误解，直接用该推导的样点单位。')
edit(176, 'the useful interval starts', 'the useful part starts', '此处指参考帧除去前缀后的部分。')
edit(179, 'learned second-order network', 'learned second-order score network', 'second-order 的对象是 score，不是网络本身。', 'Cai，IV-A/B')
edit(179, 'learned density-ratio classifier', 'classifier for density ratio estimation', '明确分类器用途，不另设方法类别。', 'Menon，§2/§4.2')
edit(179, 'complete-receiver comparison', 'comparison of the receivers', '展开过度压缩的组合；保留比较因素不唯一的必要披露。')
edit(181, 'Development and baseline-threshold selection\noverlap the evaluation scenes;',
     'Some evaluation scenes were used during method development and\nselection of baseline activity thresholds;', '重叠的是场景集合，明确评估数据曾用于开发。')
edit(181, 'All finite outputs enter the reported metrics', 'All finite outputs are included in the reported metrics', '明确纳入计算的关系。')
edit(183, 'condition evaluations per method', 'receiver runs per method', '计数对象为场景×SNR 的接收机运行。')
edit(183, 'used for the complete receiver. AER pools all device decisions across',
     'used for the receiver with learned density ratios. AER is computed from\nall device decisions across', '两者都是完整接收机；明确比较版本与统计操作。')
edit(184, 'The learned density ratio and Gaussian approximation\nproduce',
     'The receivers using the learned density ratio and Gaussian approximation\nproduce', '产生检测结果的是接收机。')
edit(184, 'the\ntested receiver substitution', 'the\nreplacement of the activity-probability calculation', '写明替换内容。')
edit(184, 'cause of nonconvergence', 'cause of failure to meet the stopping criterion', '达到迭代上限不等于证明算法数学上不收敛。')
edit(186, 'The receiver receives', 'The receiver uses', '避免无意义重复。')
edit(186, 'are unavailable to inference', 'are not supplied to the receiver', '明确真值信息不可用的对象。')
edit(187, 'A check is eligible when', 'The conditions for performing a refinement are met when', 'eligible 是内部调度口吻，改成操作条件。')
edit(187, 'and the current channel mean and covariance estimates are valid.',
     'and site updates have been accepted within the training variance\ninterval for five consecutive iterations.', 'valid 含义不明，直接说明原实现用于判断的条件及窗口。', 'C_STMP_phase_selection_20261030/iterations.py，observe_decisions/ready；STMP/denoiser.py 的 supported/site_accepted')
edit(187, 'at successive eligible checks', 'at successive checks satisfying these conditions', '承接刚定义的条件，不创建 eligible check 名称。')
edit(187, 'ten iterations with stable decisions and valid mean and covariance estimates',
     'ten iterations with stable decisions and accepted site updates within\nthe training variance interval', '用实际判断替代未定义的 valid。', 'STMP/phase_output_cycle_stopping.py 的 decision_stable/current_moment_iterations')
edit(189, 'at weight $0.2$ and a $12$-input diagnostic at weight\n$0.1$',
     'with damping factor $0.2$ and a diagnostic test with $12$ inputs at\ndamping factor $0.1$', '明确参数及诊断输入数，展开日志式短语。')
edit(189, 'With the original weight', 'With the original damping factor', '统一名称。')
edit(189, '$500$ scenes reached', '$500$ runs reached', '达到迭代上限的是运行，不是场景。')
edit(189, 'all $500$ scenes converge at', 'all $500$ runs satisfy the stopping criterion at', '报告实际停止条件，不扩大成数学收敛声明。')
edit(190, 'the weight was reduced', 'the damping factor was reduced', '统一名称。')
edit(190, 'with weight $0.2$', 'with damping factor $0.2$', '统一名称。')
edit(190, 'retain weight $0.4$', 'retain damping factor $0.4$', '统一名称。')
edit(190, 'These settings\nconstitute retrospective parameter development, rather than independent\nvalidation of a fixed damping rule across all candidate device counts.',
     'These damping factors were selected retrospectively and do not\nconstitute independent validation of a fixed rule across all candidate\ndevice counts.', '把 retrospective 的对象写清楚；保留选择性调参披露。')
edit(192, 'displayed trajectory', 'displayed curve', '图中实际是 NMSE 曲线。')
edit(193, 'All finite nonconverged outputs remain in both NMSE and AER.',
     'Finite outputs from runs reaching the iteration limit are included in\nboth NMSE and AER.', '不将上限运行直接命名为 nonconverged。')
edit(194, 'retain weights', 'retain damping factors', '统一名称。')
edit(194, 'runs in the activity sweep converge', 'runs in the activity-probability experiment meet the stopping criterion', '明确实验变量与实际停止事实。')
edit(195, 'power-delay and\nfading profiles', 'power delay profiles and\nfading distributions', '统一两类不同统计对象。')
edit(195, 'It does not introduce a full time-varying Doppler-spectrum\nmodel; its transfer conclusions concern the evaluated channel profiles.',
     'Path gains remain fixed within each block, so the comparison concerns\nthe evaluated delay and fading profiles.', '将未定义的 full Doppler-spectrum model 改成已有模型的实际假设；保留适用范围。')
edit(197, 'The activity-change, site-parameter, and activity-history tolerances',
     'The tolerances for changes in activity probabilities and site parameters,\nand for deviations from the moving average of activity probabilities', '展开三类阈值的对象，不依赖内部组合名称。')
edit(198, 'The estimate check monitors', 'The stopping rule monitors', '直接描述停止规则，避免自拟子检查名称。')
edit(198, 'the maximum activity change', 'the maximum change in activity probability', 'p 是软概率，不是硬活动状态。')
edit(198, 'The site check requires accepted updates with stable precision', 'It also requires accepted site updates with stable precision', '统一停止规则的叙述。')
edit(198, 'a small\nactivity-history residual', 'a small difference from the previous exponential moving average,', '明确 w 是何种历史量，不自造 residual 名称。')
edit(198, 'both checks must hold', 'all these conditions must hold', '与前面统一的规则叙述一致，数值和逻辑合取不变。')

# Validate every target against the turn's actual saved text before writing any file.
contents = {}
for i, u in units.items():
    if revised[i] == u['text']:
        continue
    rel = u['file']
    if rel not in contents:
        contents[rel] = (ROOT/rel).read_text(encoding='utf-8')
    assert contents[rel].count(u['text']) == 1, ('concurrent edit', i, rel)
    contents[rel] = contents[rel].replace(u['text'], revised[i])
for rel, s in contents.items():
    (ROOT/rel).write_text(s, encoding='utf-8')
(RUN/'EDITS.json').write_text(json.dumps(changes, ensure_ascii=False, indent=2), encoding='utf-8')
(RUN/'AFTER_UNITS.json').write_text(json.dumps([
    dict(u, text=revised[i]) for i, u in units.items()
], ensure_ascii=False, indent=2), encoding='utf-8')
print(f'{len(changes)} wording edits in {len(set(c["unit"] for c in changes))} units; {len(contents)} source files.')
