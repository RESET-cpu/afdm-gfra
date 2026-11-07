# 固定门限应用结果

pilot_frames：每个条件前1000个场景；共30000份结果。

四个baseline使用独立编号1000–1999场景、八档SNR共同校准的一组固定门限；本批次不调门限。STMP保持0.5。
所有原始预测、原判决与运行时间保留；只重算最终活动判决。信道NMSE由汇总误差能量除以汇总信号能量计算，未改变。
这是回顾性评估；同一场景跨实验复用，不视为独立重复样本。并发时间仅作诊断，不能用于独占算法时延比较。

|条件|方法|NMSE dB|AER|漏检率|虚警率|
|---|---|---:|---:|---:|---:|
|{'users': 40, 'frames': 8, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|STMP|33.029172|0.807975|0.0507477|0.893962|
|{'users': 40, 'frames': 8, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|offgrid_sbl|-6.616568|0.005425|0.0448639|0.000946522|
|{'users': 40, 'frames': 8, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|gnn|-3.573721|0.0199|0.0985536|0.0109685|
|{'users': 40, 'frames': 8, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|gamp|-3.127402|0.019975|0.0916891|0.0118315|
|{'users': 40, 'frames': 8, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|somp|-2.113440|0.03075|0.0811473|0.0250271|
|{'users': 40, 'frames': 16, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|STMP|-11.431817|0.002025|0.0198578|0|
|{'users': 40, 'frames': 16, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|offgrid_sbl|-8.519418|0.002075|0.0203481|0|
|{'users': 40, 'frames': 16, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|gnn|-5.508056|0.00255|0.0237803|0.000139194|
|{'users': 40, 'frames': 16, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|gamp|-4.597894|0.004|0.037264|0.000222711|
|{'users': 40, 'frames': 16, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|somp|-3.909672|0.0055|0.0406962|0.0015033|
|{'users': 40, 'frames': 24, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|STMP|-13.269685|0.00065|0.00637411|0|
|{'users': 40, 'frames': 24, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|offgrid_sbl|-9.314327|0.001575|0.015445|0|
|{'users': 40, 'frames': 24, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|gnn|-6.175535|0.001425|0.013974|0|
|{'users': 40, 'frames': 24, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|gamp|-5.305434|0.002475|0.0242707|0|
|{'users': 40, 'frames': 24, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|somp|-4.724463|0.003575|0.0338318|0.000139194|
|{'users': 40, 'frames': 32, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|STMP|-14.411868|0.000375|0.00367737|0|
|{'users': 40, 'frames': 32, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|offgrid_sbl|-9.779528|0.001525|0.0149546|0|
|{'users': 40, 'frames': 32, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|gnn|-6.579371|0.0011|0.010787|0|
|{'users': 40, 'frames': 32, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|gamp|-5.769779|0.001925|0.0188772|0|
|{'users': 40, 'frames': 32, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|somp|-5.252370|0.003425|0.0335867|0|
|{'users': 40, 'frames': 40, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|STMP|-15.274012|0.00025|0.00245158|0|
|{'users': 40, 'frames': 40, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|offgrid_sbl|-10.082565|0.001375|0.0134837|0|
|{'users': 40, 'frames': 40, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|gnn|-6.866579|0.000975|0.00956117|0|
|{'users': 40, 'frames': 40, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|gamp|-6.106869|0.001625|0.0159353|0|
|{'users': 40, 'frames': 40, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|somp|-5.641396|0.003075|0.0301544|0|
|{'users': 40, 'frames': 48, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|STMP|-15.947548|0.000175|0.00171611|0|
|{'users': 40, 'frames': 48, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|offgrid_sbl|-10.295473|0.0014|0.0137289|0|
|{'users': 40, 'frames': 48, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|gnn|-7.093463|0.000825|0.00809022|0|
|{'users': 40, 'frames': 48, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|gamp|-6.372725|0.001525|0.0149546|0|
|{'users': 40, 'frames': 48, 'activity_probability': 0.1, 'snr_db': 0, 'channel_model': 'D', 'pilot': 'dft'}|somp|-6.018763|0.003175|0.0311351|0|
