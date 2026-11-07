from pathlib import Path
import json, re

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[1]
changes = []

def change(name, old, new, reason):
    path = ROOT / name
    text = path.read_text(encoding='utf-8')
    assert text.count(old) == 1, (name, old, text.count(old))
    path.write_text(text.replace(old, new), encoding='utf-8')
    changes.append(dict(file=name, old=old, new=new, reason=reason))

change('main.tex', 'proper complex Gaussian law', 'proper complex Gaussian distribution', 'Use the distribution wording used throughout the receiver derivation.')
change('sections/02_system_model.tex', 'frame lengths are schematic. Satellite, footprint, and array artwork', 'Satellite, footprint, and array artwork', 'Remove a generic schematic disclaimer.')
change('sections/02_system_model.tex', 'Device activity is fixed over the $Q$ frames;\nSatellite', 'Device activity is fixed over the $Q$ frames.\nSatellite', 'Join the caption after deleting the disclaimer.')
change('sections/02_system_model.tex', 'Thus, the proposed AFDM\nmodel contains', 'The dense AFDM channel representation\ncontains', 'Keep the dense-representation qualification with the comparison itself.')
change('sections/02_system_model.tex', ' The entry counts compare the\ndense channel representations; the AFDM receiver uses the\n$M\\times N\\times N$ tensor and scalar frame evolution in\n\\eqref{eq:twc-frame-channel}.', '', 'Remove repetition of the channel tensor and frame evolution.')
change('sections/02_system_model.tex', 'The column number is $j=mN+r+1$ for the zero-based element indices in\n\\eqref{eq:mmv-indexing}.\n', '', 'The element indexing is already defined; remove implementation-style index conversion.')
change('sections/03_bayesian_receiver_design.tex', ', so the input index $n$ varies\nfastest, followed by the output index $r$ and antenna index $m$.', '.', 'The vectorization formula already specifies the order.')
change('sections/03_bayesian_receiver_design.tex', 'Here $m=m(R,v)$ in the covariance integral.\n', '', 'Remove an immediate restatement of the mean definition.')
change('sections/03_bayesian_receiver_design.tex', 'learns the required channel moments and\nactivity probability', 'learns the channel mean, variance, and\nactivity probability', 'Identify the actual quantities instead of the broader moments term.')
change('sections/04_generative_priors.tex', 'The trace includes the variances of the real and imaginary components;\ndivision by $D$ therefore gives the variance per complex coordinate.', 'Here $\\tau^\\star$ is the variance per complex coordinate.', 'Retain the complex-coordinate convention without explaining the division twice.')
change('sections/04_generative_priors.tex', 'For message passing, set $\\mathbf C=v\\I_D$; the finite-difference\nsettings are given', 'The finite-difference settings are given', 'The online covariance was already specified in IV-B.')
change('sections/04_generative_priors.tex', '\nBoth networks remain fixed during online inference.\n', '\n', 'Training and inference have already been separated.')
change('sections/05_overall_algorithm.tex', 'Network and tensor illustrations are schematic; the mean-network\nillustration', 'The mean-network illustration', 'Remove a generic schematic disclaimer while preserving attribution.')
change('sections/05_overall_algorithm.tex', 'We incorporate the learned channel moments into message passing through', 'We incorporate the estimated channel mean and variance into message passing through', 'State the quantities and preserve that the network output is approximate.')
change('sections/05_overall_algorithm.tex', 'conditional channel moments\n', 'conditional channel mean and variance\n', 'Use the same wording as Cai and Shen for these two quantities.')
change('sections/05_overall_algorithm.tex', 'Algorithm~1 combines these moments with $p_k$', 'Algorithm~1 combines these estimates with $p_k$', 'Avoid an unnecessary umbrella term.')
change('sections/05_overall_algorithm.tex', 'draw one block-fixed random sign vector per device.', 'draw one random sign vector per device, reused across iterations.', 'Replace a project-specific compound with the operation itself.')
change('sections/05_overall_algorithm.tex', 'Joint denoising and the extrinsic update use the current $v^{(i)}$.\n', '', 'The iteration indices and algorithm already specify this.')
change('sections/05_overall_algorithm.tex', 'refinement, and gain-refitting cost', 'refinement, and gain-estimation cost', 'Use estimation rather than a software-style refitting label.')
change('sections/06_simulation_results.tex', 'activity masking, with normalization $s=0.2647966453$.', 'activity masking.', 'Move the full-precision normalization constant to implementation details.')
change('sections/06_simulation_results.tex', 'minimum fixed-noise validation loss selects the checkpoint.', 'validation loss under fixed noise realizations selects the model.', 'Replace compressed software terminology with its statistical meaning.')
change('sections/06_simulation_results.tex', 'checkpoint selection.', 'model selection.', 'Use the same model-selection wording.')
change('sections/06_simulation_results.tex', 'With fixed AFDM/multiantenna adaptations, weights, and activity readout,', 'With fixed AFDM/multiantenna adaptations, weights, and activity decision rules,', 'The operation is an activity decision, not a named readout method.')
change('sections/06_simulation_results.tex', 'and relative-change tolerance $5\\times10^{-4}$. The activity-change,\nsite-parameter, and activity-history tolerances are $10^{-3}$, $0.1$,\nand $10^{-3}$, respectively, with $\\zeta_{\\rm hist}=0.2$, $L_s=5$, and $L_d=10$.', 'and relative-change tolerance $5\\times10^{-4}$.', 'Concentrate the auxiliary stopping thresholds in full-version Appendix C.')
change('sections/06_simulation_results.tex', 'with a block-fixed random sign vector per device.', 'with the random sign vectors reused across iterations.', 'Describe reuse directly.')
stop_path=ROOT/'sections/06_simulation_results.tex'
text=stop_path.read_text(encoding='utf-8')
start=text.index('The estimate check monitors')
end=text.index('\\subsubsection{Evaluation Metrics}',start)
old_stop=text[start:end]
new_stop=r'''After $I_{\min}$ iterations, stopping requires stable channel estimates,
input variance, activity probabilities, and Gaussian site parameters
for five consecutive iterations, together with unchanged activity
decisions for ten iterations. Otherwise, the last iterate is returned
at $I_{\max}$.
\ifdefined\FullManuscript
The complete checks and tolerances are given in
Appendix~\ref{app:implementation-settings}.
\fi

'''
change('sections/06_simulation_results.tex',old_stop,new_stop,'Keep the stopping logic in the main text and preserve the complete rule in Appendix C and the local implementation record.')
change('sections/06_simulation_results.tex', ' AWGN and colored label the training noise.', '', 'The figure caption already explains the labels.')
change('sections/06_simulation_results.tex', 'The four sparse-recovery kernels', 'The four sparse-recovery methods', 'Kernel refers to a software implementation here, not a mathematical kernel.')
change('sections/06_simulation_results.tex', 'by the Gaussian-site probability in', 'by the probability from the Gaussian approximation in', 'Describe what the formula computes without coining a compound probability name.')
change('sections/06_simulation_results.tex', 'AER with Different Activity Evidence', 'AER with Different Activity Probability Estimates', 'The table compares probability calculations, not a separately defined evidence quantity.')
change('sections/06_simulation_results.tex', 'Activity evidence & AER', 'Probability calculation & AER', 'Use the actual operation as the column heading.')
change('sections/appendix_parameter_estimation.tex', 'Coarse correlations initialize candidates; a frame phase $\\beta$ admits Doppler aliases\n', 'Coarse correlations initialize candidates. Doppler shifts yielding the same frame phase $\\beta$ are\n', 'Replace an unverified compound label with its explicit mathematical meaning.')
change('sections/appendix_parameter_estimation.tex', 'waveform branch.', 'interval of the waveform.', 'Use a plain interval description rather than a branch label.')
change('sections/appendix_parameter_estimation.tex', 'within a differentiable\ninterval of the waveform.', 'within an interval where the waveform is differentiable.', 'Attach differentiability to the waveform, not to an interval.')
change('sections/appendix_parameter_estimation.tex', 'computes its conditional channel moments under', 'computes the conditional channel mean and covariance under', 'The phase objective uses cross-device covariances, so variance alone would be inaccurate.')
path=ROOT/'sections/appendix_evaluation_protocol.tex'
t=path.read_text(encoding='utf-8')
replacements={
 'learned activity evidence':'learned activity probabilities',
 'covariance-conditioned denoiser':'denoiser conditioned on the noise covariance',
 'query\nvariance update':'input\nvariance update',
 'The activity-evidence comparison':'The activity-probability comparison',
 'baseline readout rules':'baseline activity decision rules',
 '\\subsection{Activity-Evidence Comparison}':'\\subsection{Activity Probability Comparison}',
 'analytic Gaussian activity-evidence experiment':'experiment using the Gaussian approximation for activity detection',
 'Gaussian-evidence\nruns':'runs using the Gaussian approximation\n',
 'The learned and Gaussian evidence\nproduce':'The learned density ratio and Gaussian approximation\nproduce',
 'current channel moments are valid':'the current channel mean and covariance estimates are valid',
 'ten stable decisions and valid-moment iterations':'ten iterations with stable decisions and valid mean and covariance estimates',
}
for old,new in replacements.items():
 assert old in t,old
 t=t.replace(old,new)
 changes.append(dict(file=str(path.relative_to(ROOT)),old=old,new=new,reason='Replace an overbroad or project-specific shorthand with the actual probability, variance, mean, or covariance operation.'))
t += r'''
\subsection{Additional Implementation Settings}
\label{app:implementation-settings}

The training-channel root mean square is $s=0.2647966453$.
The activity-change, site-parameter, and activity-history tolerances
are $10^{-3}$, $0.1$, and $10^{-3}$, respectively, with
$\zeta_{\rm hist}=0.2$, $L_s=5$, and $L_d=10$.

''' + old_stop.replace(' This history is used only for stopping.','')
path.write_text(t,encoding='utf-8')
(RUN/'IMPLEMENTATION_DETAILS.md').write_text('# 正文移出的实现设置\n\n本轮只移动说明，不改变计算。以下完整停止规则同步保存在 main_full 附录 C。\n\n归一化常数：s = 0.2647966453。\n\n活动变化、Gaussian site 参数和活动历史容差分别为 1e-3、0.1、1e-3；历史权重 0.2，连续通过窗口 5，硬判决稳定窗口 10。最小／最大迭代数 60／600，相对变化容差 5e-4。\n\n```tex\n'+old_stop+'```\n',encoding='utf-8')
(RUN/'EDITS.json').write_text(json.dumps(changes,indent=2,ensure_ascii=False),encoding='utf-8')
print('Applied',len(changes),'targeted prose edits.')
