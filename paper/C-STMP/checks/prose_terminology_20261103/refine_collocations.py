from pathlib import Path
import json, shutil

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[1]
edits = json.loads((RUN/'EDITS.json').read_text(encoding='utf-8'))

def change(name, old, new, reason):
    path = ROOT/name
    s = path.read_text(encoding='utf-8')
    assert s.count(old) == 1, (name, old, s.count(old))
    path.write_text(s.replace(old,new),encoding='utf-8')
    edits.append(dict(file=name,old=old,new=new,reason=reason))

change('sections/04_generative_priors.tex', 'covariance-weighted\nscore matching', 'score matching weighted by $\\bm\\Sigma$', 'Describe the weighting rather than introduce an unattested name for the objective.')
change('sections/04_generative_priors.tex', 'gives the output-by-input Jacobian', 'gives the Jacobian', 'The displayed derivative defines the convention; remove the unusual compound modifier.')
change('sections/04_generative_priors.tex', 'training posterior log odds:', 'posterior log odds under the training distribution:', 'Attach the qualifier to the distribution rather than stack three noun modifiers.')
change('sections/04_generative_priors.tex', 'gives the receiver activity probability', 'gives the activity probability', 'The receiver context is already explicit.')
change('sections/05_overall_algorithm.tex', 'In normalized coordinates,', 'After normalization,', 'Describe the actual scaling operation directly.')
change('sections/05_overall_algorithm.tex', 'With new-message weight $\\eta\\in(0,1]$', 'With damping factor $\\eta\\in(0,1]$', 'Use Cai V-B1 damping factor; the update formula specifies which message receives this weight.')
change('sections/06_simulation_results.tex', 'Their default new-message weights are $0.2$ and $0.4$.', 'Their default damping factors are $0.2$ and $0.4$.', 'Use the established full expression damping factor.')
change('sections/06_simulation_results.tex', 'continuous offsets through a first-order atom approximation.', 'continuous offsets through a first-order linear approximation of the dictionary.', 'Wei IV-B uses First-Order Linear Approximation; atom approximation is needlessly compressed here.')
change('sections/03_bayesian_receiver_design.tex', 'over the $N^2$ channel positions', 'over the $N^2$ channel entries', 'Use entries for tensor/matrix elements.')
change('sections/02_system_model.tex', 'We use an indicator function $\\alpha_k$ to model the device activity as', 'We use a binary activity variable $\\alpha_k$, defined as', 'Alpha is the random activity variable; the indicator function appears only in the hard decision.')
change('sections/02_system_model.tex', 'Please refer to Appendix~\\ref{app:afdm-model} for the detailed\nderivation and the expression for integer $d$.', 'Appendix~\\ref{app:afdm-model} gives the derivation and the expression for integer $d$.', 'Remove reader-addressing filler.')
change('sections/appendix_parameter_estimation.tex', 'Coordinate updates optimize the\nphase slopes and constant device rotations, absorbing the latter\ninto the feedback means.', 'Coordinate updates optimize $\\beta_k$ and a constant phase for each\ndevice, absorbing the constant phase into the feedback means.', 'Replace phase slopes and device rotations by the actual parameters being optimized.')
change('sections/appendix_parameter_estimation.tex', 'jointly refit the gains', 'jointly re-estimate the gains', 'Use estimation in the parameter-estimation description.')
change('sections/appendix_evaluation_protocol.tex', 'The clean-channel bank and denoiser epoch budget are shared.', 'The two configurations use the same clean training channels and number of\ndenoiser training epochs.', 'Replace channel bank and epoch budget with the data and training settings.')
change('sections/appendix_evaluation_protocol.tex', 'independent test of phase-policy selection.', 'independent test of the phase-update settings.', 'No phase policy is defined in the mathematical model.')
change('sections/appendix_evaluation_protocol.tex', 'GP-MP uses new-message weight', 'GP-MP uses damping factor', 'Use the same established expression as the main text.')
change('sections/appendix_evaluation_protocol.tex', 'satisfy the native convergence criterion.', 'satisfy the receiver stopping criterion.', 'Native describes a software implementation, not a convergence property.')
change('sections/appendix_evaluation_protocol.tex', '\n reach the iteration limit.', '\nreach the iteration limit.', 'Remove a leading space introduced during the first rewrite.')
change('sections/06_simulation_results.tex', 'After $I_{\\min}$ iterations, stopping requires stable channel estimates,\ninput variance, activity probabilities, and Gaussian site parameters\nfor five consecutive iterations, together with unchanged activity\ndecisions for ten iterations.', 'After $I_{\\min}$ iterations, stopping requires stable channel estimates\nand activity probabilities, agreement between the input and updated\nvariances, and accepted, stable Gaussian site updates for five\nconsecutive iterations, together with unchanged activity decisions\nfor ten iterations.', 'Keep the variance-consistency and accepted-update requirements in the short main-text summary.')
(RUN/'EDITS.json').write_text(json.dumps(edits,ensure_ascii=False,indent=2),encoding='utf-8')

for ext in ('pdf','svg','png'):
    p=ROOT/f'figures/learned_receiver.{ext}'
    dst=RUN/'before'/f'figures/learned_receiver.{ext}'
    dst.parent.mkdir(parents=True,exist_ok=True)
    assert not dst.exists()
    shutil.copy2(p,dst)
print('Total targeted prose edits:',len(edits))
