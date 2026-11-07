# 新网络闭环阻尼试验

## Material Passport

- origin_skill: academic-research-suite / experiment-agent
- origin_mode: run + validate
- origin_date: 2026-10-24
- verification_status: VERIFIED（数值接口与原网络复现；不代表新方差物理有效）
- version_label: closed_loop_damping_20261024

用户授权测试旧阻尼是否限制新网络。固定原网络 epoch 200、新网络 epoch 92；4 个均匀组场景 × −4/0 dB × 三种网络输入方案 × 三档新消息权重，共 72 条闭环轨迹，每条固定 120 轮。

## 接入中发现的问题

新网络的完整条件均值导数在首轮实际查询上给出负的平均方差估计。有限差分步长及1/4探针检查、自动微分检查均确认该现象；并非差分计算错误。保留原接收机方差下限和拒绝规则后继续试验，触发次数完整报告。这是一个带近似方差和旧分类器的接收机候选，不是已经校准的新接收机。

## 第120轮结果

|SNR|方案|新消息权重|一阶去噪 NMSE|整体信道 NMSE|AER|原停止条件满足场景|方差触底轮数/480|
|---:|---|---:|---:|---:|---:|---:|---:|
|-4|old_native|0.2|-10.045|-10.045|0.0000|4/4|2|
|-4|old_native|0.4|不可用|0.000|0.0750|0/4|1|
|-4|old_native|0.6|不可用|35.645|0.4875|0/4|1|
|-4|new_I|0.2|-9.861|-9.860|0.0000|4/4|90|
|-4|new_I|0.4|-9.861|-9.861|0.0000|4/4|108|
|-4|new_I|0.6|7.430|17.466|0.6875|1/4|117|
|-4|new_C|0.2|-8.983|-8.983|0.0000|4/4|301|
|-4|new_C|0.4|-8.970|-8.970|0.0000|4/4|336|
|-4|new_C|0.6|7.305|17.370|0.6875|1/4|122|
|0|old_native|0.2|-13.391|-13.391|0.0000|4/4|1|
|0|old_native|0.4|不可用|39.714|0.2750|0/4|1|
|0|old_native|0.6|不可用|53.065|0.7125|0/4|1|
|0|new_I|0.2|-12.158|-12.157|0.0000|4/4|114|
|0|new_I|0.4|-12.159|-12.159|0.0000|4/4|123|
|0|new_I|0.6|8.267|18.981|0.9250|0/4|4|
|0|new_C|0.2|-9.338|-8.943|0.0125|0/4|320|
|0|new_C|0.4|-9.150|-8.763|0.0125|4/4|339|
|0|new_C|0.6|7.888|17.971|0.7000|1/4|118|

## 阻尼对速度的影响

以下是 pooled 去噪 NMSE 首次低于 −8 dB、且随后连续10轮保持的窗口起点。需要再观察9轮才能确认这个窗口；这是使用真值的离线速度读数，不是接收机的在线停止条件。

|接收 SNR|新网络输入|权重0.2|权重0.4|窗口起点提前比例|
|---:|---|---:|---:|---:|
|-4|new_I|22|14|36.4%|
|-4|new_C|27|14|48.1%|
|0|new_I|21|13|38.1%|
|0|new_C|27|16|40.7%|

这组小规模试验支持：原0.2新消息权重限制了新接口的收敛速度。新网络使用vI时，0.4在8组条件中全部于原允许的最少60轮满足停止条件，120轮末的去噪NMSE相对0.2变化小于0.002 dB。新C也更快，但最终精度仍差；0 dB时仍有2个用户判决错误。0.6多数失败，不建议直接采用。

提高权重没有补上最终精度差距：0.4的新vI在−4/0 dB末轮分别为−9.861/−12.159 dB，原网络0.2为−10.045/−13.391 dB；新C则为−8.970/−9.150 dB。

反馈方差仍需处理：新C的0.4在两档SNR分别有336/480、339/480轮触发原方差下限；新vI为108/480、123/480。故本轮证据针对包含原floor规则的完整候选接口，不能归因于纯粹的一阶均值替换，也不能说明已得到物理校准的方差。

当前原型需要数值导数额外前向，且旧网络用了既有CUDA图加速；有并发训练。虽然迭代次数减少，本轮原型达到原停止条件的耗时尚未胜过原网络，不声称端到端运行时间改善。未修改正式接收机绑定。

## 范围与复现

- Small reused development sample; not an independent 1000-scene confirmation.
- Old native arm uses its trained second network; new arms use matched Jacobian variance. Cross-model effects include this interface change; within-model damping comparison is controlled.
- Classifier is frozen from old AWGN training and receives new conditional mean.
- C is linearly interpolated working covariance, not the true covariance of temporally correlated errors.
- Feedback and activity site still use original scalar variance projection; this is not full D-GEC.
- Single fixed random probe; finite differences and finite network may give imperfect or negative variance; original pooling/floor/rejection rules are retained and counted.
- Concurrent training and numerical derivative overhead make wall times descriptive, not isolated deployment timing.

数值复核说明：有色 C 情况下，单个 wᵀJ_Dw 即使对精确后验均值也可能为负；无偏的随机 trace 估计不保证逐探针非负。自动微分一致证明方向导数计算一致，不表示已经求得精确 trace。标量 vI 下精确后验均值的 Jacobian 为半正定，new_I 首轮负方向响应具有更直接的诊断意义。独立 CPU 验证及合法 Gaussian 反例见 REVIEW.json。

方差公式依据：Dytso–Poor–Shamai (2021), §IV Proposition 1 / Corollary 1，条件均值 Jacobian 与条件协方差的关系。实坐标完整均值为 D，Σ=real_embedding(C)/2；以输出为行的 Jacobian 定义，平均复坐标方差为 tr(J_D Σ)/4096。精确恒等式要求精确条件均值和匹配高斯模型；本网络与实际查询并不保证满足。
来源：https://arxiv.org/abs/2104.01883；已有术语出处见 paper/docs/TERMINOLOGY.md。

脚本、计划、每轮结果、接口预检、自动微分检查和失败尝试均保留在此目录。`attempt_01` 为读取旧紧凑结果字段时的记录错误；修复只改变复现检查使用的保存字段，未改变推断。

图目录：D:\afdm-gfra\result\channel_denoising\figures\closed_loop_damping_20261024

最终独立复核见 `FINAL_REVIEW.json`：72条/8640轮完整、首轮配对一致、8次原基线复现和全部汇总通过。全部图形已检查并修复图例重叠；交付核验见 `DELIVERY_CHECK.json`。
