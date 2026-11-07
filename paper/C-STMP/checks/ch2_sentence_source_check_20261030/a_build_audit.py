import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(r'D:/afdm-gfra/paper/C-STMP/checks/ch2_sentence_source_check_20261030')

def ref(key, page, section, quote=None, locator=None, eq=None, note=None):
    result = dict(key=key, page=page, section=section)
    for name, value in [('quote', quote), ('locator', locator), ('eq', eq), ('note', note)]:
        if value is not None:
            result[name] = value
    return result

def item(category, source_refs, changes, reason, technical_status, formula_adaptation, action):
    return dict(category=category, source_refs=source_refs, changes=changes, reason=reason,
                technical_status=technical_status, formula_adaptation=formula_adaptation, action=action)

ding_open = ref('ding2026', 2, 'II. AFDM-GF-RA System',
    'We consider an AFDM-GF-RA system, where a LEO satellite equipped with M antennas serves K single-antenna devices.',
    locator='左栏 §II 第一完整句。')
shen_array = ref('shen2025', 3, 'II. System Model',
    'The system comprises U single-antenna terrestrial devices that communicate with a LEO satellite equipped with a uniform planar array (UPA) consisting of N_a = N_z × N_y antennas and a regenerative payload for on-board baseband signal processing.',
    locator='右栏 Fig.1 后第一段第二句。', note='英文逐字核对；N_a=N_z×N_y 是原 PDF 数学记号的文本转写。')
shen_access = ref('shen2025', 3, 'II. System Model',
    'During each time interval, active devices share the same time-frequency resources to transmit their signals to the satellite.',
    locator='右栏 Fig.1 后第一段第三句。')
shen_gnss = ref('shen2025', 3, 'II. System Model',
    'Additionally, to minimize energy consumption, we assume that these terrestrial devices operate without GNSS capabilities and do not pre-compensate for delay and Doppler shifts.',
    locator='右栏 Fig.1 后第一段第四句。')
shen_double = ref('shen2025', 3, 'II-A. Terrestrial-satellite Link Model',
    'The TSLs will experience fast variations due to the high mobility of the LEO satellite. Hence, this time variation and multipath propagation require a doubly dispersive channel model for accurate TSLs characterization.',
    locator='§II-A 起首两句。')
huang_stationary = ref('huang2026', 2, 'II. System Model; Doppler shift',
    'Take the ground user as the stationary reference point.',
    locator='印刷页 2950，左栏 Doppler shift 小段首句。')
huang_common = ref('huang2026', 2, 'II. System Model; Doppler shift',
    'The resulting Doppler term D(ψ) is assumed to be common to all propagation paths within the same satellite-to-ground (S2G) link [15].',
    locator='印刷页 2950，Eq.(2) 后第二个完整句；下一句以很小的多径角度扩展解释该近似。', eq='(2)')
li_array = ref('li2023', 4, 'II-B. Signal Models', locator='左栏 Eq.(3) 之前的阵列段：先给出按路径的二维到达角和 Kronecker 阵列向量，再基于星地距离长令同一终端各路径到达角近似相同，并去掉阵列向量的路径下标。这里为中文释义，无英文直引。', note='阵列响应按方向采用负指数及单位范数；本稿采用正指数、单位模各元素，不能直接按同一数值向量替换。')
li_cir = ref('li2023', 3, 'II-B. Signal Models', locator='右栏 Eq.(2) 及紧跟的 where 句：给出逐路径复增益、Doppler、绝对传播延迟、阵列向量相乘求和的时变冲激响应，逐项解释这些量。中文释义，无英文直引。', eq='(2)')
shen_delay = ref('shen2025', 3, 'II-A. Terrestrial-satellite Link Model',
    'As shown in Fig. 1, τ_{i,u} = τ̃_{i,u} − τ^c represents the differential delay for the i-th path from the u-th device to the satellite, where τ̃_{i,u} and τ^c are denoted as propagation delay and common delay, respectively.',
    locator='Eq.(1) 后第二句。', eq='(1)', note='英文逐字核对；引语中的数学符号是原 PDF 的文本转写，原文共同延迟 c 为上标，本稿 τ_c 将其改为下标。')
shen_common_delay = ref('shen2025', 3, 'II-A. Terrestrial-satellite Link Model',
    'The common delay corresponds to the propagation time between the satellite and the closest point on earth within the beam coverage [21].',
    locator='Eq.(1) 后 τ 差定义之后。', eq='(1)')
shen_dd_equation = ref('shen2025', 3, 'II-A. Terrestrial-satellite Link Model',
    locator='Eq.(1)：逐路径 h_{i,u} δ(τ−τ_{i,u}) δ(ν−ν_{i,u}) 乘 e^{jπ n_z Θ^z_u} e^{jπ n_y Θ^y_u}；阵列角没有路径下标，而 ν_{i,u} 有路径下标。Eq.(1) 后 where 句定义天线索引与 physical paths。', eq='(1)')
shen_cosines = ref('shen2025', 3, 'II-A. Terrestrial-satellite Link Model',
    'The directional cosines Θ^z_u = cos ϑ^z_u and Θ^y_u = sin ϑ^z_u sin ϑ^a_u, along the z-axis and y-axis, depend on the zenith angle ϑ^z_u and azimuth angle ϑ^a_u, respectively.',
    locator='§II-A 在本页末尾的最后一句。', eq='(1)', note='英文逐字核对；引语中的上下标及三角函数公式按原 PDF 转写。')
li_upa = ref('li2023', 4, 'II-B. Signal Models', locator='左栏第一完整段的无编号 UPA 公式 g(θ)=a_{M_x}(sin θ_y cos θ_x)⊗a_{M_y}(cos θ_y)，以及随后逐元素 a_{n_v}(x) 定义；其 where 句定义 λ=c/f_c 和沿轴相邻阵元间距 d_v。中文释义，无英文直引。', note='原式归一化因子为 1/√n_v，指数为负号。')
shen_quasistatic = ref('shen2025', 4, 'II-B. Transmission Scheme',
    'Fortunately, H^{DDS}_{n_z,n_y,u}[k′,l′,l] remains approximately constant over Q consecutive frames, benefited by the quasi-static property of (1) in the delay-Doppler domain.',
    locator='右栏最后一句，Eq.(9) 讨论之后。', eq='(1), (9)', note='英文逐字核对；引语中的 H 张量记号按原 PDF 转写。')
shen_limit = ref('shen2025', 5, 'II-B. Transmission Scheme',
    'In practice, the quasi-static property may be disrupted when the number of transmitted frames becomes large.',
    locator='左栏上端第二句；随后给 Q=8 与 Q=25 的 Doppler/时延变化例子，说明近似有时间范围。')
huang_quasistatic = ref('huang2026', 3, 'III-A. Score-Based Model Training for AFDM Channel',
    'Meanwhile, although AFDM can only guarantee approximate channel invariance within a finite signaling duration, the effective channel variation across several adjacent pilot sequences remains negligible because the corresponding Doppler-angle variation over a short interval is relatively small within pilot frames.',
    locator='印刷页 2951，左栏 Eq.(6) 后第二段末句。', eq='(6)')
li_slow = ref('li2023', 4, 'II-B. Signal Models', locator='左栏阵列段末两句指出星地距离长使空间角变化缓慢；右栏 Eq.(5) 后的 block-fading 讨论则依赖终端 Doppler/时延预补偿。该后者条件不适用于本稿无终端预补偿情形。中文释义，无英文直引。', eq='(5)')

rows = {
'P01': [
 item('REASONABLE_COMBINATION', [ding_open, shen_array],
      ['保留 Ding 起首句主干；AFDM-GF-RA→AFDM-GFRA 是缩写拼写调整。', '把 M 展开为 M_y M_z，阵列尺寸依据是 Shen 的 N_a=N_z×N_y。', 'where 改为 in which 属连接语法调整，其余主体关系不变。'],
      '能定位 Ding 的完整主句及 Shen 的阵列维数子句；没有新增服务关系或收发天线配置。按协议接受为有定位的原句组合，而非仅凭系统主题相似。',
      'SUPPORTED：系统配置和二维阵列维数均有直接依据；当前句只引 Ding，阵列维数最好同时指向 Shen。',
      'M=N_yN_z 的变量改名与乘法因子顺序交换；无数学内容变化。',
      '可保留；若目标是每个新增细节都可追溯，应在此处补 Shen 对阵列维数的来源。'),
 item('SUPPORTED_PARAPHRASE', [shen_access],
      ['During each time interval→In each transmission block。', 'share resources to transmit signals 改写为 transmit pilots over resources，变更句子谓语组织。', 'signals→pilots 是本稿导频对象限定；删除 to the satellite。'],
      '内容与 Shen 原句一致且导频是信号的具体用途，但完整英文句经过重组，不只是必要术语替换，也不是拼接保留的原句分句。',
      'SUPPORTED：同时复用时频资源有原文直接支持；导频用途由本稿建模明确。',
      '无公式。transmission block 是本稿时间分组，不能单凭此句获得多帧准静态条件。',
      '若严格执行原句适配标准，应采用 Shen 的原句结构，只替换 time interval 为本稿 block、signals 为 pilots。'),
 item('SUPPORTED_PARAPHRASE', [shen_gnss],
      ['删去 Additionally。', 'to minimize→To reduce、these terrestrial devices→the devices，属于普通措辞精简而不是技术术语替换。', 'without GNSS capabilities and do not pre-compensate for delay and Doppler shifts 保留了完整实质分句。'],
      '无 GNSS、无终端延迟与 Doppler 预补偿及节能动机均有明确原句；但普通词语已自行改写，按严格类别不能标 TERM_ONLY。',
      'SUPPORTED：假设与 Shen 相同，含义没有变强。',
      '无公式。',
      '若必须满足仅术语替换，可恢复 Shen 原句的动机和指代用语；现句可作为有来源的改写保留，但不能宣称逐字适配。')
],
'P02': [
 item('SUPPORTED_PARAPHRASE', [shen_double],
      ['把“高速→时变”和“时变+多径→需要双扩展模型”两个句子的因果链压缩为单句。', 'will experience / require a ... channel model→give rise to ... links；删除 accurate ... characterization。'],
      '可定位完整的两句因果依据，但原句分句没有按原有语法保留，属于支持性概述，而非必要连接后直接组合。',
      'SUPPORTED：卫星高速及多径导致时变和频率选择性的描述与来源一致；不存在把单一 Doppler 误称为无时变的问题。',
      '无公式。',
      '若严格要求原句，保留 Shen 的两句及其因果连接，仅调整 TSLs 首次展开。'),
 item('REASONABLE_COMBINATION', [huang_stationary, huang_common],
      ['Take→We take，user→device，给同一链路加入 k 下标。', '把原文被动假设分句改为与 We take 并列的 and assume that ... share the same ...；D(ψ)→ν_k。', '原文同一 S2G 链路各传播路径的范围改写为同一 device k 的全部路径，未扩展为不同设备共用 Doppler。'],
      '两分句均对应 Huang §II 同一 Doppler 小段的可定位原句；主动/被动调整用于合成同一主语的并列句，未添加额外物理前提。按协议接受合理组合。该结论并非由“Doppler”词汇重合或仅由仿真设定推断。',
      'SUPPORTED：Huang p.2 正文明言同链路各径共用 Doppler，并以很小的多径角扩展作近似依据；这里仍须理解为建模近似，非所有移动散射环境的恒等式。',
      'D(ψ)→ν_k；source 的单用户链路扩展为按 k 独立定义的一组链路，没有假定 ν_k=ν_{k′}。',
      '可保留；正文可补一句小角扩展的物理理由，若用户要求最小变更则无需扩写。'),
 item('AUTHOR_DEFINED_OR_DERIVED', [li_array, shen_dd_equation],
      ['a_k 是本稿给共同 UPA 阵列响应所取符号；Shen 用逐天线指数，Li 用 g_k。', 't_c 从本稿 transmission block 起点计时，是本稿新增的时间参考定义。'],
      '查阅的来源支持共同阵列响应概念，但未找到含此时间起点和这两个定义的对应完整原句。本句是作者符号/坐标定义，不能因 Let ... denote 模板常见而算原句。',
      'SUPPORTED AS DEFINITION：共同 a_k 需采用同设备各径 AoA 近同的近似；Li p.4 有明确说明，Shen Eq.(1)采用该结构。t_c 可自行定义。',
      '把逐天线阵列因子收成向量；确定接收端块参考时间。该定义不等于各时刻 h_k 不变。',
      '作为本稿定义明确保留，并在引入共同 a_k 处引用/说明相同 AoA 近似；若要求每句均为参考原句，则此句不满足，不能作已通过处理。'),
 item('AUTHOR_DEFINED_OR_DERIVED', [li_cir, li_array, shen_dd_equation, shen_delay, huang_common],
      ['Li Eq.(2) 的逐路径 â、ν_{k,q}、τ_{k,q}、g_{k,q} 经符号改名与参数约束，得到共同 a_k 和 ν_k。', 'Shen 的差分时延替代绝对时延；本稿指定接收端补偿共同传播时延。', 'where 合并路径数、复增益和 Dirac 函数定义，但“补偿后时变向量 CIR”完整句及本稿公式不是任一参考原句。'],
      '这是可说明来源的模型适配/公式推导：至少施加共同阵列、共同 Doppler，并变更延迟和时间参考。不能称只做术语替换，也不能以多篇分别支持各个词语即认定原句组合。',
      'CONDITIONALLY CONSISTENT：在同设备各径共同 Doppler、共同 AoA、差分延迟及固定块参考下数学形式成立。Shen 只直接给差分时延模型和共同延迟定义，其正文没有逐字给出本稿“在卫星接收机补偿后”的操作句。',
      '从 Li 的逐路径时变 CIR 出发，令 ν_{kℓ}=ν_k、a_{kℓ}=a_k；以 τ̃_{kℓ}−τ_c 重定延迟零点。若接收端 t_c 的零点随共同补偿平移，所产生的固定 Doppler 相位须吸收入 g_{kℓ}，因 g 为复增益可做到。Shen Eq.(4) 使用 e^{j2πν(t−τ)} 的约定，与本稿 e^{j2πνt_c} 比较时也须相应吸收逐路径固定相位；二者不能在保留同一增益数值时直接等同。',
      '保留为明确的本稿适配，并在公式附近补来源和前提，尤其说明共同 a_k 与时间/复增益约定。不能将该整句报告为参考原句直接改名。'),
 item('SUPPORTED_PARAPHRASE', [shen_delay],
      ['把“τ差值 represents differential delay”改为“differential delay is τ差值”，重排定义方向。', '删除 Fig.1 指引、重复的设备/卫星描述；把 propagation delay and common delay 的双定义拆出，只在本句保留传播延迟。'],
      '精确差分时延等式与物理含义有来源，但完整句的语序与从句组织已改写，不能归入仅术语替换。',
      'SUPPORTED：τ_{kℓ}=τ̃_{kℓ}−τ_c 与 Shen 相同。',
      'u→k、i→ℓ、共同延迟 τ^c→τ_c，差分时延等式无变化。',
      '若必须逐句原句适配，恢复 Shen 该句的原有定义组织，并只改索引/删除失效图指引。'),
 item('SUPPORTED_PARAPHRASE', [shen_common_delay],
      ['增加 τ_c 符号。', 'corresponds to→is；earth→Earth；移除 Shen 的内部编号 [21]，替换为本稿引用。'],
      '核心连续原文高度一致，事实精确对应；但 corresponds to→is 是普通谓语改写，并非必要技术对象替换。严格类别应保留这个差别，不能把技术正确等同 TERM_ONLY。',
      'SUPPORTED：共同延迟取波束内最近地面点到卫星的传播时间，来源直接明确。',
      '只补 τ_c 标签，无公式推导。',
      '若严格要求仅术语替换，可把 is 恢复为 corresponds to；其余保留。')
],
'P03': [
 item('AUTHOR_DEFINED_OR_DERIVED', [shen_dd_equation, li_upa],
      ['由 Shen 的两个逐天线阵列指数抽取并相乘，写成本稿向量单个元素。', '引入任意 d_y,d_z 和 λ；Shen Eq.(1) 的 π 指数对应 d_y=d_z=λ/2。', 'Li 一般间距向量具有负号和归一化，本稿改用正号和未归一化形式，另改轴命名与向量索引。'],
      '检索到的是源公式和相应定义，而不是“for antenna indices ... entries ... given by”连同此公式的原句。本稿完成向量化、索引展开与间距一般化，属于有来源的数学定义/适配。',
      'CONDITIONALLY CONSISTENT：当 μ 是相应 y/z 轴方向余弦并采用该接收阵列相位约定时公式成立；d=λ/2 时还原 Shen Eq.(1) 的阵列因子。归一化/相位符号与 Li 不同，不应声称其公式逐符号一致。',
      'n_z+M_z n_y 的索引与 Shen 的 n_z+n_y N_z 一致。将 e^{jπn_zΘ_z}e^{jπn_yΘ_y} 改写为 e^{j2π(d_y n_y μ_y+d_z n_z μ_z)/λ}，需要显式一般间距平面波阵列模型；不是只改变量名。',
      '保留为本稿定义，附 Shen/Li 来源并写明阵列约定；若本稿实际固定半波长间距，可直接令 d_y=d_z=λ/2，但本次仅审计不修改。'),
 item('SUPPORTED_PARAPHRASE', [shen_cosines, li_upa],
      ['Shen 的两个方向余弦及角度关系改写为符号对 (μ_y,k, μ_z,k) 的统称。', 'Li 的 where 句给出波长及相邻阵元间距，本稿精简重组为 Here 后的三个并列定义。', '未保留源句的完整原句或分句顺序。'],
      '三个物理名词都有可定位来源，含义可支持；本稿采用新符号并重写成并列定义句，不能将普通定义模板当作具体原句证据。',
      'SUPPORTED：方向余弦、间距和波长为上述阵列公式的相应物理量。方向余弦应明确关联 y/z 轴；该解释由公式和符号下标可推知，但当前句未展开角度定义。',
      'μ_y,k 对应 Shen Θ^y_u，μ_z,k 对应 Θ^z_u；d_y,d_z,λ 沿用一般阵列模型含义。',
      '若必须采用原句组合，可明确拼合 Shen 的 directional-cosines 句与 Li 的定义分句，并妥善处理 Li 引用长度；现句应如实标为支持性改写。'),
 item('AUTHOR_DEFINED_OR_DERIVED', [shen_quasistatic, shen_limit, huang_quasistatic, li_slow],
      ['把 Shen 对 Q 帧 DD 域信道的准静态讨论与 Huang 的短时相邻导频讨论，细化为四类物理参数在本稿 transmission block 内近似不变。', '加入 angles of arrival 的联合冻结条件；Li 只直接说明角度缓变。', '未给 block 时长相对于这些变化尺度的明确界限。'],
      '在本轮核查的 Shen、Ding、Huang、Li 及 Cai 两版本中，未找到列出这四类参数并以 transmission block 为范围的对应原句。相关文献提供短时近似的背景，但该完整假设是本稿明确建立的模型条件。其写法“are assumed”允许作为作者假设，不等于来源错误或必须删除。',
      'CONDITIONALLY REASONABLE：冻结 g、τ、ν、AoA 不会消除 e^{j2πνt_c} 的相位变化，因而与时变 CIR 并不矛盾。该近似只适用于足够短的块，Shen 明示 Q 大时失效。Li Eq.(5) 后的补偿后 block fading 不可搬用为本稿无终端预补偿的直接证明。',
      '无新显示公式；这是后续跨帧只含共同相位变化所需的建模条件。文献不能自动保证本稿任意 Q 或任意 block 时长均满足近似。',
      '明确标为本稿短块假设，并在邻近处引用 Shen/Huang/Li 的限定依据。若用户坚持每句都是参考原句，本句目前不满足；不能只加一条泛引就标成原句适配。')
]
}

starts = {
    'P01': ['We consider', 'In each transmission block', 'To reduce energy consumption'],
    'P02': ['The high mobility', 'We take the ground device', 'Let $\\mathbf a_k$', 'After compensation', 'The differential delay', 'The common\ndelay'],
    'P03': ['For antenna indices', 'Here,', 'The path gains'],
}
structures = {
'P01': dict(source_order=['Ding §II 起首句 + Shen §II 阵列尺寸', 'Shen §II 同段共享资源句', 'Shen §II 同段无 GNSS 句'], cross_source=True, structure_effect='从 Ding 的系统配置进入 Shen 的共享资源与无预补偿设定，顺序连贯；把信号限制为导频和把时间间隔叫作 block 是本稿范围设定。阵列维数来自另一个来源，单引 Ding 不能覆盖此细节。', verdict='1 句合理组合，2 句支持性改写；不能称整段仅替换术语。'),
'P02': dict(source_order=['Shen §II-A 双扩展因果', 'Huang §II 静止参考 + 共同 Doppler', '本稿向量/时间定义，Li/Shen 阵列背景', 'Li 时变 CIR + Shen 差分延迟/阵列 + Huang 共同 Doppler的适配', 'Shen §II-A 差分延迟定义', 'Shen §II-A 共同延迟定义'], cross_source=True, structure_effect='该段把不同论文的模型条件组装成新系统模型。共同 Doppler 与共同阵列均有明确来源；从逐路径 Doppler 到共同 Doppler、从绝对时延到差分时延、以及本稿时间参考是实质模型适配，不是简单术语替换。所有条件应在公式附近透明说明。', verdict='1 句合理组合，3 句支持性改写，2 句本稿定义/推导；来源支持概念不等于整段原句改名。'),
'P03': dict(source_order=['Shen Eq.(1) 阵列项 + Li §II-B 一般间距阵列，写成本稿向量索引', 'Shen 方向余弦 + Li 间距/波长定义的改写', '本稿四参数短块假设，背景为 Shen/Huang 的短时条件及 Li 的角度缓变'], cross_source=True, structure_effect='将阵列指数一般化后新增共同的块内参数冻结条件；该末句是本稿假设，不能由前两句阵列定义或 Li 的预补偿后 block fading 直接推出。短块条件应保留。', verdict='1 句支持性改写，2 句本稿定义/推导；当前三句都不能归为仅术语替换或直接原句组合。')
}

paragraphs=[]
for pid, sentence_rows in rows.items():
    original=(ROOT / f'{pid}.input.txt').read_text(encoding='utf-8')
    positions=[original.index(start) for start in starts[pid]] + [len(original)]
    assert positions[0] == 0 and positions == sorted(positions)
    for idx, sentence_row in enumerate(sentence_rows):
        sentence_row['id']=f'{pid}-S{idx+1:02d}'
        sentence_row['draft_tex']=original[positions[idx]:positions[idx+1]]
    assert ''.join(row['draft_tex'] for row in sentence_rows) == original
    paragraphs.append(dict(id=pid, sentences=sentence_rows, paragraph_structure=structures[pid],
                           coverage=dict(exact_byte_normalized_text=True, whitespace_ignored_match=True,
                                         note='文件读取规范化 CRLF 为 LF；片段直接由连续字符区间切出，顺序拼接与规范化输入逐字相同。')))

counts=dict(Counter(s['category'] for p in paragraphs for s in p['sentences']))
audit=dict(scope='P01–P03 当前英文第二章逐句来源核查；仅审计，不修改 canonical',
    protocol='PROTOCOL.md', source_manifest='SOURCES.json',
    method='直接读取 SOURCES.json 所列原 PDF 与 clean.pages 文本；不读取旧 Pxx 审查或同伴审查输出。完整语法句含其公式和从属 where；句号后的 Here 另算完整句。',
    paragraphs=paragraphs, sentence_count=sum(len(p['sentences']) for p in paragraphs), category_counts=counts,
    source_search_scope=['shen2025', 'ding2026', 'huang2026', 'li2023', 'cai2026', 'cai2026_stmp_v2'],
    original_pdf_pages_viewed=[dict(key=k,page=p,image=f'a_pdf_views/{n}.png') for k,p,n in [
        ('shen2025',3,'shen_p3'),('shen2025',4,'shen_p4'),('shen2025',5,'shen_p5'),('ding2026',2,'ding_p2'),
        ('huang2026',2,'huang_p2'),('huang2026',3,'huang_p3'),('li2023',3,'li_p3'),('li2023',4,'li_p4')]],
    render_note='本轮用 Poppler 重新渲染并实际 view_image 核对上列 8 个整页。Poppler 对 Shen 字体映射输出警告，相关原句、符号和公式均可读；以页面核对去除 clean 文本中的跨行断词/伪空格。',
    quote_policy=dict(li2023_verbatim_english_words=0, li2023_maximum=25,
                      note='Li 仅列精确页码/公式定位和中文释义。Shen/Ding/Huang 是本地用户提供论文，列出核查必要原句。'),
    conclusion='12 句已完整覆盖：2 句可认定合理原句组合，6 句为有来源的改写，4 句为本稿定义/推导或显式假设。未发现需归 SOURCE_GAP 的无条件实质主张；这不代表 12 句均满足原句适配要求。')
(ROOT/'a_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

out=['# P01–P03 逐句来源核查', '', audit['conclusion'], '',
     '核查口径：每句包含其显示公式和从属 where；独立 Here 句单列。引文是从本轮原始 PDF 页面与 clean.pages 文本核对的原句，已合并 PDF 断词和排版空白。Li 不直引英文，仅提供定位和中文释义。未改正文、PDF、参考文献或模型。', '',
     '| 类别 | 句数 |', '|---|---:|']
for category, count in counts.items(): out.append(f'| {category} | {count} |')
out += ['', '全部 12 个连续片段按段拼接，与相应 Pxx.input.txt 规范化换行后逐字一致；覆盖通过不等于来源适配通过。', '']
for p in paragraphs:
    out += [f"## {p['id']}", '', '**段落顺序：** '+' → '.join(p['paragraph_structure']['source_order']), '',
            '**结构判断：** '+p['paragraph_structure']['structure_effect'], '', '**段落结论：** '+p['paragraph_structure']['verdict'], '']
    for s in p['sentences']:
        out += [f"### {s['id']} — {s['category']}", '', '**当前稿完整句：**', '', '```tex', s['draft_tex'].rstrip(), '```', '', '**原文定位：**', '']
        for r in s['source_refs']:
            out.append(f"- {r['key']}，PDF 第 {r['page']} 页，{r['section']}"+(f"，式 {r['eq']}" if 'eq' in r else '')+'。')
            if 'quote' in r: out += ['', '> '+r['quote'], '']
            if 'locator' in r: out.append('  定位/释义：'+r['locator'])
            if 'note' in r: out.append('  对照限制：'+r['note'])
        out += ['', '**具体改动：** '+'；'.join(s['changes']), '', '**分类理由：** '+s['reason'], '',
                '**技术状态：** '+s['technical_status'], '', '**公式适配：** '+s['formula_adaptation'], '', '**处理建议：** '+s['action'], '']
out += ['## 原页视觉核对', '', audit['render_note'], '',
        '已查看：Shen PDF 3/4/5；Ding PDF 2；Huang PDF 2/3（印刷 2950/2951）；Li PDF 3/4。PNG 留存在 a_pdf_views/。', '',
        '本轮关于“未找到原句”的结论仅限 SOURCES.json 所列且本审查员检索的 Shen、Ding、Huang、Li 和 Cai 两版本，不代表所有文献均无此表述。', '']
(ROOT/'a_audit.md').write_text('\n'.join(out),encoding='utf-8')
print(json.dumps(dict(sentence_count=audit['sentence_count'], category_counts=counts, coverage='PASS', files=['a_audit.json','a_audit.md']),ensure_ascii=False))
