"""Record the original sentence used for every prose unit in the revised chapter."""
import difflib
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parents[1]
ROOT = PAPER.parents[1]
tex = (PAPER / 'sections/02_system_model.tex').read_text(encoding='utf-8')
before = (HERE / 'before/02_system_model.tex').read_text(encoding='utf-8')
sources = {}

def source(key, location, original):
    sources[key] = {'location': location, 'original': original}

source('S01', 'Shen, PDF p.3, §II 首段第1句', 'We consider a LEO satellite-enabled grant-free random access system with the fixed beam as illustrated in Fig. 1, where OTFS is adopted to mitigate the doubly dispersive effect [18] inherent in TSLs.')
source('S02', 'Shen, PDF p.3, §II 首段第2句', 'The system comprises U single-antenna terrestrial devices that communicate with a LEO satellite equipped with a uniform planar array (UPA) consisting of Na = Nz × Ny antennas and a regenerative payload for on-board baseband signal processing.')
source('S03', 'Shen, PDF p.3, §II 首段第3句', 'During each time interval, active devices share the same time-frequency resources to transmit their signals to the satellite.')
source('S04', 'Shen, PDF p.3, §II 首段第4句', 'Additionally, to minimize energy consumption, we assume that these terrestrial devices operate without GNSS capabilities and do not pre-compensate for delay and Doppler shifts.')
source('S05', 'Shen, PDF p.3, §II-A 首段第1–2句', 'The TSLs will experience fast variations due to the high mobility of the LEO satellite. Hence, this time variation and multipath propagation require a doubly dispersive channel model for accurate TSLs characterization.')
source('S06', 'Shen, PDF p.3, §II-A 式(1)前', 'Then, the delay-Doppler-space domain channel from the u-th device to the (nz + nyNz)-th antenna at the satellite can be represented as [18]')
source('S07', 'Shen, PDF p.3, §II-A 式(1)后', 'where u = 0,...,U − 1, nz = 0,...,Nz − 1, ny = 0,...,Ny − 1, and P is the number of physical paths.')
source('S08', 'Shen, PDF p.3, §II-A 式(1)后', 'As shown in Fig. 1, τi,u = τ̃i,u − τc represents the differential delay for the i-th path from the u-th device to the satellite, where τ̃i,u and τc are denoted as propagation delay and common delay, respectively.')
source('S09', 'Shen, PDF p.3, §II-A 式(1)后', 'The common delay corresponds to the propagation time between the satellite and the closest point on earth within the beam coverage [21].')
source('S10', 'Shen, PDF p.3, §II-A 式(1)后', 'Additionally, the notations hi,u and νi,u are the path gain and Doppler shift of the i-th path from u-th device to the satellite, respectively.')
source('S11', 'Shen, PDF p.3, Notations', 'The superscripts (·)* and (·)H denote the conjugate and conjugated-transpose operations, respectively. δ(·) denotes the Dirac delta function.')
source('S12', 'Shen, PDF p.3, §II-A 末句', 'The directional cosines Θz_u = cos θz_u and Θy_u = sin θz_u sin θa_u, along the z-axis and y-axis, depend on the zenith angle θz_u and azimuth angle θa_u, respectively.')
source('S13', 'Shen, PDF p.4, §II-B 式(3)后', 'where Tcp is the time duration of the cyclic prefix (CP), and Tsym = T + Tcp is the time duration of a OFDM symbol with CP.')
source('S14', 'Shen, PDF p.4, §II-B 式(2)前', 'Then, the transmitted signal in the delay-Doppler domain is given by XDD_u,q[k,l] = Cu,q[k,l]td_u[l], where td_u[l] represents the data symbol selected from a predefined alphabet A = {a1,...,a|A|} with cardinality |A|.')
source('S15', 'Shen, PDF p.4, §II-B 式(7)前', 'We denote the delay and Doppler taps for the i-th path of the u-th device as follows')
source('S16', 'Shen, PDF p.4, §II-B 式(7)后', 'where li,u = 0,...,M − 1 and ki,u = ⌈−N/2⌉,...,⌈N/2⌉ − 1 represent the indexes of the delay and Doppler tap, respectively.')
source('S17', 'Shen, PDF p.4, §II-B Proposition 1 后', 'Note that the relationship (8) aligns with those in [30], [34] when adopting a single-frame OTFS transmission with replacing Cu,q[k,l]td_u[l] for XDD_u,q[k,l], provided Δf > 2νmax and T > τmax.')
source('S18', 'Shen, PDF p.4, §II-B Proposition 1 前', 'Based on (1)-(7), we can derive the input-output relationship of the system, as given in the following proposition.')
source('S19', 'Shen, PDF p.4, §II-B 末段', 'Fortunately, HDDS_nz,ny,u[k′,l′,l] remains approximately constant over Q consecutive frames, benefited by the quasi-static property of (1) in the delay-Doppler domain.')
source('S20', 'Shen, PDF p.1, §I', 'It should be noted that the schemes in [9]–[17] are designed for block fading channels, which are assumed to remain constant during one block transmission.')
source('S21', 'Shen, PDF p.5, §II-C 式(14)后', 'where Yl_q and Zl_q are with the (k,az + Nzay)-th element YDDA_az,ay,q[k,l] and ZDDA_az,ay,q[k,l], respectively.')
source('S22', 'Shen, PDF p.4, §II-B 式(6)前', 'Finally, the symplectic finite Fourier transform (SFFT) [31] maps the symbols into the delay-Doppler-space domain as')
source('C01', 'Cai, PDF p.3, §II-A 首段', 'A total of N adjacent OFDM subcarriers are shared among the devices for pilot transmission.')
source('C02', 'Cai, PDF p.3, §II-A 首段', 'We adopt a block-fading model, i.e., all the channels remain quasi-static within a transmission block.')
source('C03', 'Cai, PDF pp.3–4, §II-A 首段', 'Moreover, we assume that the IoT devices are synchronized, and each device determines whether to access the channel in an independent and identically distributed (i.i.d.) manner.')
source('C04', 'Cai, PDF p.4, §II-A', 'As a result, only a (small) subset of the devices is active in any given transmission block.')
source('C05', 'Cai, PDF p.4, §II-A 式(1)前', 'We use an indicator function αk to model the device activity as')
source('C06', 'Cai, PDF p.4, §II-A 式(1)后', 'Let λ represent the probability of a device being active, i.e., p(αk = 1) = λ, where λ ≪ 1.')
source('C07', 'Cai, PDF p.4, §II-A 式(2)前', 'Denote by hknm ∈ C the channel frequency response on the n-th subcarrier from the k-th device to the m-th BS antenna.')
source('C08', 'Cai, PDF p.4, §II-A 式(2)前', 'Then, the channel frequency response from the k-th device to the BS can be expressed in a matrix form as')
source('C09', 'Cai, PDF p.4, §II-A 导频段', 'Assume that a total of T OFDM symbols are allocated for pilot transmission.')
source('C10', 'Cai, PDF p.4, §II-A 导频段', 'Let qktn ∈ C be the pilot symbol transmitted by the k-th device during the t-th OFDM symbol on the n-th subcarrier.')
source('C11', 'Cai, PDF p.4, §II-A 导频段', 'We construct a diagonal pilot matrix as Qkt ≜ diag{qkt1,...,qktN} ∈ C^(N×N), ∀k,t.')
source('C12', 'Cai, PDF p.4, §II-A 式(3)前', 'Assume that the cyclic prefix (CP) length exceeds the maximum channel delay spread.')
source('C13', 'Cai, PDF p.4, §II-A 式(3)前', 'After removing the CP and applying the DFT, the received signal Yt ∈ C^(N×M) during the t-th OFDM symbol is given by')
source('C14', 'Cai, PDF p.4, §II-A 式(3)后', 'where Nt ∈ C^(N×M) is an AWGN matrix with the elements i.i.d. drawn from CN(0,δ0²).')
source('C15', 'Cai, PDF p.4, §II-A 式(3)后', 'Let Xk ≜ αkHk.')
source('C16', 'Cai, PDF p.4, §II-A 式(4)前', 'Define Y ≜ [Y1^H,...,YT^H]^H ∈ C^(NT×M), Qk ≜ [Qk1^H,...,QkT^H]^H ∈ C^(NT×N), and N ≜ [N1^H,...,NT^H]^H ∈ C^(NT×M).')
source('C17', 'Cai, PDF p.4, §II-A 式(4)前', 'We express the received signal Y over the T OFDM symbols in a more compact form as')
source('C18', 'Cai, PDF p.4, §II-A 式(4)后', 'For simplicity, we impose the condition that Q is partial orthogonal, specifically requiring that QQH = KP INT, where each device has the same transmit power budget P.')
source('C19', 'Cai, PDF p.4, §II-A 式(4)后', 'The design of partial orthogonal Q is deferred to Section V-C.')
source('C20', 'Cai, PDF p.4, §II-A 式(4)后', 'Due to the sporadic access of the devices, matrix X exhibits a block-sparsity structure. Specifically, if the k-th device is inactive, we have Xk = αkHk = 0.')
source('C21', 'Cai, PDF p.4, §II-B 首句', 'In this paper, we aim to simultaneously detect the active devices and estimate the corresponding channels based on the observation Y under a Bayesian inference framework.')
source('C22', 'Cai, PDF p.4, §II-B 式(5)前', 'In message passing, we factorize the joint posterior distribution according to Baye’s theorem and the conditional independence relationships among the variables, expressed as')
source('C23', 'Cai, PDF p.5, §II-B 式(5)续文', 'where xm ∈ C^(NK) and ym ∈ C^(NT) denote the m-th column of X = [x1,...,xM] and Y = [y1,...,yM], respectively.')
source('C24', 'Cai, PDF p.1, 摘要', 'Specifically, we develop a novel turbo message passing (TMP) framework that models the entire channel matrix as a super node, rather than factorizing it element-wise.')
source('C25', 'Cai, PDF p.6, §III-B 式(14)后', 'where (13) arises from the fact that the messages Mfym→xkm(xkm) are independent for different values of m.')
source('C26', 'Cai, PDF p.9, §IV-B 式(51)后', 'Please refer to [31, Appendix F] for the detailed derivation.')
source('C27', 'Cai, PDF p.3, §I-B1', 'However, an energy leakage problem arises from the inverse discrete Fourier transform (IDFT) to obtain the time-domain channel, which undermines its sparsity level.')
source('C28', 'Cai, PDF p.11, 信道模型段', 'the temporal and spatial steering vectors are defined as [aN(τl) 与 bM(φl) 的向量公式]')
source('C29', 'Cai, PDF p.7, §III-B2/3 式(30)、(35)附近', 'is the posterior probability of activity for the k-th device. By taking the Gaussian projection, the mean of xkm with respect to the belief MfXk(Xk) is given by')
source('C30', 'Cai, PDF p.5, Table II（表格，非原句）', 'p(ym|xm): CN(Qxm,δ0² INT); p(Xk|Hk,αk): δ(Xk−αkHk); p(αk): (1−λ)δ(αk)+λδ(1−αk).')
source('D01', 'Ding, PDF p.2, §II 式(1)前', 'The time-domain transmitted signal is generated through the inverse discrete affine Fourier transform (IDAFT) applied to xk, mathematically formulated as')
source('D02', 'Ding, PDF p.2, §II 式(1)后及式(3)后', 'c1 and c2 are AFDM modulation parameters. where Ts = 1/(NΔf) gives the sampling interval.')
source('D03', 'Ding, PDF p.2, §II 式(2)后', 'where AH = Λc1^H F Λc2^H represents the DAFT matrix.')
source('X01', 'Xu, 作者稿印刷 p.3（含封面 PDF p.4）, §II-B 式(6)前', 'The time-domain signal can be obtained by')
source('W01', 'Wei–Yuan, PDF p.2, §II-A 式(2)前', 'Let M denote the number of compressed spatial measurements per subcarrier, where M ≪ Nr, and let B ∈ C^(M×Nr) denote a known analog spatial compression matrix.')
source('W02', 'Wei–Yuan, PDF p.2, §II-B 式(4)后', 'Since M ≪ Nr and ρ ≪ 1 in the extreme compression regime of interest, this inverse problem is severely underdetermined and requires both measurement consistency and effective channel priors.')

# Each anchor begins the next sentence or displayed-equation definition unit.
# Target text is read from the actual manuscript, never copied from a second draft.
rows = []
def row(group, anchor, keys, change):
    rows.append({'group': group, 'anchor': anchor, 'sources': keys.split(), 'change': change})

row('01 系统场景', 'We consider', 'S01', '删除 fixed beam、图号；OTFS→AFDM；TSLs 首次展开。')
row('01 系统场景', 'The system comprises', 'S02', 'U→K，Na=NzNy→M=MyMz；删除本文未建模的载荷描述。')
row('01 系统场景', 'During each', 'S03', 'time interval→transmission block；time-frequency resources→pilot resources。')
row('01 系统场景', 'Additionally, we assume', 'S04', '仅删除动机状语 to minimize energy consumption。')
row('02 物理信道引入', 'The TSLs experience', 'S05', '删除 will 和结尾重复的 characterization；保留原两句因果顺序。')
row('02 物理信道引入', 'Moreover, we assume', 'C03', '保留假设句骨架，将同步／接入假设换成本文已有的静止设备与共同 Doppler 假设。')
row('02 物理信道引入', 'After receiver compensation', 'S06', '改为时间域冲激响应和阵列向量；补入原稿已有的接收端公共时延补偿。')
row('03 路径参数定义', 'where $k=1', 'S07', '代入 k、Lk；阵列索引放在阵列响应式后。')
row('03 路径参数定义', 'Here $\\tau_', 'S08', '删除图号，i/u→ℓ/k；保持差分时延原句顺序。')
row('03 路径参数定义', 'The common delay corresponds', 'S09', '保留原句，仅 Earth 大写及本文引文键。')
row('03 路径参数定义', 'Additionally, $g_', 'S10', '只保留此处需要定义的 path gain；共同 Doppler 已在式前定义。')
row('03 路径参数定义', 'The notations $\\mathbf a_k$', 'S11', '沿用原记号定义句，代入本文 a_k、t_c、δ 及已有含义；非 Shen 同一符号定义。')
row('04 阵列与块内参数', 'The UPA response is defined', 'C28', '两种 steering vectors→UPA response；其公式仍由本文原式及 Shen/Li 支撑。')
row('04 阵列与块内参数', 'where $n_z=', 'S07', '保留阵列索引枚举方式；代入本文范围和 λ 定义。')
row('04 阵列与块内参数', 'The notations $d_y$', 'S11', '原记号定义句代入 d_y/d_z；spacing between adjacent antennas 用词仍据 Li p.4。')
row('04 阵列与块内参数', 'The directional cosines', 'S12', 'Θ→μ；保留 z/y 顺序，删除本稿未引入的 θ 参数。')
row('04 阵列与块内参数', 'We assume that the path gains', 'C02', '把原句准静态对象由整个信道改为本文原有的物理参数；不引入 block-fading 假设。')
row('05 导频分配', 'A total of $N$', 'C01', 'adjacent OFDM→chirp；保留共享导频资源句式。')
row('05 导频分配', 'Assume that a total', 'C09', 'T OFDM symbols→Q AFDM frames。')
row('05 导频分配', 'Let $P_{qkn}', 'C10', 'qktn→Pqkn，OFDM symbol→AFDM frame，subcarrier→chirp subcarrier。')
row('05 导频分配', 'We construct a pilot vector as', 'C11', 'diagonal pilot matrix→pilot vector，保留本文原向量定义。')
row('05 导频分配', 'Let $\\mathbf P', 'W01', '保留 let…denote a known…matrix；代入本文 P、维度、接收端和索引。')
row('06 导频条件', 'For simplicity, we impose', 'C18', 'Q→P，功率预算→原有每帧导频能量；保留原 PPH 条件。')
row('06 导频条件', 'The design of', 'C19', '只换矩阵名与章节号；删去重复修饰语。')
row('07 AFDM 调制', 'The time-domain transmitted', 'D01', '仅 x_k→p_qk；IDAFT 公式保持本稿原式。')
row('07 AFDM 调制', 'where $t=0', 'S16', '索引定义句，换为本稿时域样本范围；不移植 Shen 的延迟／Doppler 网格。')
row('07 AFDM 调制', 'Here $T_s=', 'D02', '保留采样间隔原句，补回原稿 Δf 的既有定义。')
row('07 AFDM 调制', 'The parameters $c_1$', 'D02', '只增加 The parameters 作主语引导，参数名称不变。')
row('07 AFDM 调制', 'The time-domain signal can', 'X01', '保留原句，矩阵符号及公式用本文原稿。')
row('07 AFDM 调制', 'where\n\\begin{equation}', 'D03', '使用本文 F_A 的 DAFT 约定；不复制 Ding 原文中 A^H 的混用。')
row('08 CPP', 'Assume that the chirp-periodic', 'C12', 'CP→CPP，exceeds→greater than or equal to，最大时延→最大差分时延；均由本文原条件决定。')
row('08 CPP', 'The CPP is given by', 'S14', '原公式引导句的定义对象换为 CPP；具体公式仍为原稿/Bemani，不称 Shen 使用 CPP。')
row('08 CPP', 'where $\\langle x', 'C16', '用原多变量定义句承接本文已有模运算和 2Nc1 条件；公式内容不来自 Cai。')
row('08 CPP', 'Here $T_{\\rm frame}', 'S13', 'Tsym、OFDM symbol、CP→Tframe、AFDM frame、CPP；保留原句时长结构。')
row('09 连续波形', 'Define $w_', 'C16', '同一多变量定义句代入 wξ、ζn 与原时间变量；本文特有定义。')
row('09 连续波形', 'We denote the transmit waveform', 'S15', '保持 We denote…as follows；定义对象换为第 n 个 chirp subcarrier 的 transmit waveform。')
row('09 连续波形', 'Note that $\\varphi', 'S17', '保留“说明公式与另一表达一致并给出条件”的句子功能；代入原样本等式和 CPP 条件，属于必要数学适配。')
row('10 有效信道', 'Denote by $H_k', 'C07 C13', '保留 Denote by…from the kth device…；把 OFDM 子载波响应换为经 CPP/DAFT 后的 AFDM 有效信道。')
row('10 有效信道', 'Let $H_k=', 'C15', '原 Let 等式定义句，代入本文参考帧定义。')
row('10 有效信道', 'Then, the effective channel', 'C08', 'channel frequency response→effective channel Hk；删去不对应张量的 matrix form。')
row('10 有效信道', 'where $n$ and $r$', 'S16', '原成对索引说明改为发射／接收符号索引，并保留原天线索引定义。')
row('10 有效信道', 'For path gain', 'C08', '原 channel response→matrix form 句；前置本稿原路径增益、时延和 Doppler 条件。')
row('10 有效信道', 'where $t_{\\rm c}', 'C16', '原多变量定义句适配本稿已有时间对应与参考帧起点。')
row('10 有效信道', 'Please refer to', 'C26', '只换为本稿附录，并保留原稿对整数 d 情形的指引。')
row('10 有效信道', 'Power leakage arises', 'C27', '保留 leakage arises from…which…sparsity 的整句结构；原因换为本稿分数时延/Doppler，术语与结论据 Huang。')
row('11 跨帧关系', 'After removing the CPP in frame', 'C13 C15', 'Cai 的 CPP 接收操作句承接原 Let 定义，代入本稿 gq；无对应原文跨帧 gq 定义。')
row('11 跨帧关系', 'Based on \\eqref{eq:path', 'S18', '保留 Based on…we can derive…as，代入原推导关系及 qth AFDM frame。')
row('11 跨帧关系', 'where $\\operatorname{wrap}', 'S22', '保留 maps…to/into 的映射句，改为本文原 wrap 映射；不称 Shen 定义了该算子。')
row('11 跨帧关系', 'After separating the phase', 'S19', '保留 remains approximately constant over Q consecutive frames；成立条件换为本稿已定义的相位分离，沿用引言措辞。')
row('12 活动与有效导频', 'Each device determines', 'C03', '保留原接入独立同分布分句，删除不适用于本稿的同步假设。')
row('12 活动与有效导频', 'As a result', 'C04', '仅去括号；保持原句。')
row('12 活动与有效导频', 'We use an indicator', 'C05', '保留原句与本稿原活动定义。')
row('12 活动与有效导频', 'Let $\\rho$', 'C06', 'λ→ρ，p→Pr，技术定义不变。')
row('12 活动与有效导频', 'The activity states are', 'S20', '原不变性从句作用于本稿已有活动状态假设。')
row('12 活动与有效导频', 'Let $X_k=', 'C15', '原句，仅保留本稿等号写法。')
row('12 活动与有效导频', 'The pilot symbols including', 'S14', '原 transmitted signal is given by 的对象换为含帧间相位的导频；式(10)仍是本文原式。')
row('13 接收观测', 'After removing the CPP and applying', 'C13', 'CP/DFT/OFDM→CPP/DAFT/AFDM；维度与索引保持本文原稿。')
row('13 接收观测', 'where $\\mathbf W_q', 'C14', 'Nt→Wq，δ0²→σ²，并代入本稿噪声矩阵维度。')
row('14 紧凑观测', 'We express the received signal', 'C17', 'T OFDM symbols→Q AFDM frames，保持句式及原 MMV 式。')
row('14 紧凑观测', 'where $\\mathbf Y,', 'C16', '原矩阵定义方式，代入本文四个矩阵的维度。')
row('14 紧凑观测', 'The matrices $\\mathbf Y$', 'S21', '原矩阵—元素对应句改列四个矩阵的条目；are with 改 have，保留本稿全部索引等式。')
row('15 稀疏结构', 'Due to the sporadic', 'C20', '恢复原段两句顺序及 Specifically；仅删去 matrix 修饰语。')
row('15 稀疏结构', 'Since $Q<KN$', 'W02', '保留 Since…this inverse problem is…underdetermined；条件换为本文维度，删除 severely 和无关后半句。')
row('16 贝叶斯问题', 'In this paper, we aim', 'C21', '保留原句，符号仍为 Y。')
row('16 贝叶斯问题', 'We estimate the full', 'C21', '原 aim…estimate…channels 句的对象与限定换成原稿 full Hk、without imposing channel sparsity；技术依据仍为 Huang。')
row('16 贝叶斯问题', 'Let $\\widehat', 'C10', '使用原 Let…be…定义句；本文特有的 Ahat、σhat² 条件固定方式保留，不称 Cai 有同一前端。')
row('16 贝叶斯问题', 'Let $q_{\\rm tr}', 'C06', '使用原 Let…represent…定义句，代入原 qtr 训练信道先验。')
row('16 贝叶斯问题', 'Specifically, we model', 'C24', '保留 model the entire…rather than factorizing it element-wise；删除不在本章引入的 TMP/super node。')
row('16 贝叶斯问题', 'The variables $H_k$', 'C25', '保留 independent for different values of…；对象与 k 内独立条件均是本文原假设。')
row('16 贝叶斯问题', 'We factorize the joint posterior', 'C22', '保留原整句，删除 In message passing；修正 Baye’s 拼写为 Bayes\'。')
row('17 后验因子与目标', 'where $\\mathbf x_j', 'C23', 'm→j，并换为本文维度；删除重复写出的列向量拼接。')
row('17 后验因子与目标', 'Here\n$p(', 'C30', '表中因子的公式写入正文；保留原稿 Ahat、σhat²、硬约束和 Bernoulli 质量函数，不标作原文完整句。')
row('17 后验因子与目标', 'The MMSE estimate and the posterior', 'C29', '以原 posterior probability of activity 与 mean…is given by 两处说明合并引出本文两个既有目标；未使用高斯投影。')

cursor = tex.index('We consider')
for item in rows:
    index = tex.find(item['anchor'], cursor)
    if index < 0:
        raise ValueError('Missing or out-of-order anchor: ' + item['anchor'])
    item['start'] = index
    cursor = index + len(item['anchor'])

def prose_view(value):
    def equation(match):
        label = re.search(r'\\label\{([^}]+)\}', match.group())
        return '\n[本文原公式 ' + (label.group(1) if label else '无编号') + ']\n'
    value = re.sub(r'\\begin\{equation\}.*?\\end\{equation\}|\\\[.*?\\\]', equation, value, flags=re.S)
    value = re.sub(r'\\subsection\{[^}]+\}', '', value)
    return re.sub(r'\s+', ' ', value).strip()

head = '''# 第二章原段原句对照：Shen、Cai、Xu、Ding、Wei

本记录对应当前 `sections/02_system_model.tex`。按正文顺序，把每个句子或与陈列公式连用的定义单元列出。改后文字直接从实际源稿截取，没有另写一份展示稿。原句中的数学符号作可读转写，PDF 连字、断行已还原；来源中个别公式用方括号明确占位。

段落母本：01–03 以 Shen §II/II-A 为主；04 沿 Shen 阵列说明与 Cai 定义句；05–06 沿 Cai §II-A 导频段；07 沿 Ding §II 与 Xu §II-B 的 AFDM 调制段；08–11 采用相关前缀、公式定义和跨帧段落；12–15 沿 Cai §II-A 的活动、观测和稀疏性段，并使用 Wei 的已知矩阵／欠定问题句；16–17 沿 Cai §II-B 的贝叶斯问题段。

只有条件、符号、技术对象相符的句子才作局部替换。连续波形、跨帧 gq、wrap 和前端固定估计等本文特有内容，保留原数学定义，明确登记为“原定义句的对象替换／必要数学适配”，不虚称这些公式已经出现在母本。Table II 转正文的因子说明明确标作表格来源。

Xu 使用[Surrey 作者稿](https://openresearch.surrey.ac.uk/esploro/outputs/journalArticle/AFDM-aided-Grant-Free-Random-Access-for-LEO/991050765702346)，§II-B、印刷 p.3、式(6)前。仅采用已读到的一句；当前读取到在线 PDF 文本，未取得该页截图。其余四篇为本地原文。Wei 指 Yiming Wei 与 Xiaojun Yuan 的 L-STMP 论文。

'''
lines = [head]
last_group = None
for number, item in enumerate(rows, 1):
    end = rows[number]['start'] if number < len(rows) else len(tex)
    item['target'] = prose_view(tex[item['start']:end])
    item['line'] = tex[:item['start']].count('\n') + 1
    if item['group'] != last_group:
        lines.append('\n## ' + item['group'] + '\n\n')
        last_group = item['group']
    lines.append(f'### {number:02d}（正文第 {item["line"]} 行）\n\n')
    for key in item['sources']:
        s = sources[key]
        lines.append('**原句 — ' + s['location'] + '：**\n\n> ' + s['original'] + '\n\n')
    lines.append('**改后：**\n\n```tex\n' + item['target'] + '\n```\n\n')
    lines.append('**必要替换：**' + item['change'] + '\n\n')

(HERE / 'SENTENCE_ALIGNMENT.md').write_text(''.join(lines), encoding='utf-8')
(HERE / 'ALIGNMENT.json').write_text(json.dumps({'sources': sources, 'units': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(HERE / 'CHANGES.diff').write_text(''.join(difflib.unified_diff(before.splitlines(keepends=True), tex.splitlines(keepends=True), fromfile='before/02_system_model.tex', tofile='sections/02_system_model.tex')), encoding='utf-8')
print('Recorded', len(rows), 'prose/formula-definition units in', len(set(r['group'] for r in rows)), 'groups.')
