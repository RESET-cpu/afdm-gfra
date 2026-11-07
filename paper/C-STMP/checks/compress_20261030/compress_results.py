from pathlib import Path
import json
RUN=Path(__file__).resolve().parent
PAPER=RUN.parents[1]
files=['06_simulation_results','appendix_parameter_estimation','appendix_afdm_channel_model','appendix_implementation']
texts={f:(PAPER/'sections'/(f+'.tex')).read_text(encoding='utf-8') for f in files}
ops=[]
def block(file,start,end,new):
 t=texts[file];assert t.count(start)==1,(file,start)
 a=t.index(start);b=len(t) if end is None else t.index(end,a)
 after=new.strip()+'\n\n';ops.append({'file':file,'before':t[a:b],'after':after})
 texts[file]=t[:a]+after+t[b:]
f='06_simulation_results'
block(f,'We first examine the channel structure','\\subsection{Simulation Settings}',r'''
We evaluate channel denoising, JADCE accuracy, pilot requirements,
access load, and transfer across channel profiles.
''')
block(f,'We consider the satellite uplink','For $Q\\leq KN$',r'''
Table~\ref{tab:simulation-parameters} specifies the satellite uplink.
Devices are uniform over the beam footprint; delays, Doppler shifts,
and array responses share the same geometry. Large-scale propagation
effects are compensated. The NTN-TDL-D profile \cite{shen2025} uses
uniform delay spread $[30,50]$~ns, a line-of-sight gain of fixed
amplitude and uniform phase, and proper complex Gaussian diffuse gains.
Path parameters remain fixed per block. Defaults are $K=40$,
$Q=16$, and $p=0.1$.
''')
block(f,'The training and validation sets contain','For colored-noise training',r'''
Training and validation use $50{,}000$ and $5{,}000$ clean
$16\times16\times16$ channels from disjoint scenes, with four
candidate channels sampled per scene before activity masking.
All use the same fixed normalization. The denoiser uses Adam,
batch size $64$, initial learning rate $10^{-4}$, and exponential
moving average decay $0.999$ over $200$ epochs; the minimum
fixed-noise validation loss selects the checkpoint. The white-noise
reference shares the channel bank and epoch budget.
''')
block(f,'For colored-noise training','\\begin{equation}',r'''
Colored training uses the proper complex Gaussian covariance
$C=v(R_{\rm a}\otimes\I_{16}\otimes R_{\rm c})$ in
antenna--output--input order, with log-uniform $v\in[10^{-3},10^2]$
and independent factors
''')
block(f,'where $G\\in\\mathbb C^{16\\times4}$','\\subsubsection{Compared Receivers}',r'''
where $G\in\mathbb C^{16\times4}$ has independent $\CN(0,1)$
entries and $\xi$ is uniform on $[0,0.5]$; each factor has trace
$16$ and varying eigenvectors/eigenvalues. After training by
\eqref{eq:first-loss}, freeze the denoiser and train the classifier
from random initialization using binary cross-entropy and equally
likely active/inactive labels. Its batch size, initial learning rate,
and epoch budget are $32$, $3\times10^{-4}$, and $100$; validation
selects the checkpoint. Classifier inputs use noise covariance
$C=v\I$ and frozen denoiser features; receiver evaluations use
the same covariance form. Appendix~\ref{app:implementation} gives
the normalization scale and selected checkpoints.
''')
block(f,'All receiver comparisons use known inter-frame phases','\\subsubsection{Evaluation Metrics}',r'''
All comparisons use known inter-frame phases and observation-based
noise estimates. STMP and GP-CCD-MP-DRE use activity threshold $0.5$,
$60$--$600$ iterations, relative-change tolerance $5\times10^{-4}$,
and activity/message-stability checks (Appendix~\ref{app:implementation}).
Their default new-message weights are $0.2$ and $0.4$.
The SNR comparison uses $1{,}000$ scenes per point; the pilot-frame,
device-count, activity-probability, and cross-profile comparisons
use $500$ paired scenes per point. Scenes are reused across conditions;
parameter selection and evaluation details appear in
Appendix~\ref{app:evaluation-protocol}.
''')
block(f,'We first evaluate the channel mean independently','\\begin{figure}',r'''
Following \cite[Sec.~VI-B]{cai2026}, we evaluate denoising separately
using $R=H+W$, $\vect(W)\sim\CN(\mathbf0,v\I)$, with known $v$
and nominal SNR $-10\log_{10}v$. Six SNRs span $-20$ to $30$~dB;
each uses $500$ scenes and four channels per scene ($2{,}000$ samples).
Both neural estimators receive identical channels and white test noise;
AWGN and colored label their training perturbations.

References are least squares (LS), returning $R$; the Gaussian-prior
estimate $P_{\rm tr}R/(P_{\rm tr}+v)$, where $P_{\rm tr}$ is the
normalized training-channel power; and genie-aided conditional MMSE.
Given true path geometry, powers, and line-of-sight gain, the genie
reports the analytic conditional MSE of the remaining Gaussian gains.
The four sparse-recovery kernels use an identity observation operator
and known AWGN variance, retaining their receiver settings and GNN
weights; GAMP-SBL retains its internal noise update.
''')
block(f,'Figure~\\ref{fig:cstmp-denoising} highlights','\\subsection{JADCE Performance}',r'''
At $0$~dB in Fig.~\ref{fig:cstmp-denoising}, the colored-trained
estimator reaches $-17.98$~dB NMSE versus $-2.98$~dB for the
Gaussian-prior estimator, demonstrating the value of structure beyond
average power. The learned estimators continue improving at high SNR,
whereas sparse recovery flattens, consistent with residual dictionary
and first-order offset approximation error. Colored training's
estimator gains $2.11$~dB over the white-trained estimator at $-10$~dB,
but the latter is better at high SNR. The benefit is therefore
concentrated at high input uncertainty. The genie remains better,
with additional path information unavailable to the learned estimators.
''')
block(f,'Both trajectories initially increase in NMSE','\\subsubsection{Effect of SNR}',r'''
Both trajectories initially increase in NMSE: approximate extrinsic
updates do not guarantee monotonic error reduction. GP-CCD-MP-DRE
approaches its final $-13.85$~dB by about $30$ iterations, while
STMP improves more slowly to $-11.79$~dB. This is a single-scene result.
''')
block(f,'The NMSE curves exhibit two distinct trends','\\subsubsection{Effect of Pilot-Frame Count}',r'''
The learned receivers continue improving as SNR increases, while
sparse recovery improves less, consistent with the representation
constraints seen in direct denoising. The NMSE gain over STMP narrows
from $1.87$~dB at $-4$~dB to $0.41$~dB at $6$~dB.
At $0$~dB, GP-CCD-MP-DRE reduces STMP's AER by about $47\%$,
mainly through fewer misses. At $-4$~dB, off-grid SBL has slightly
lower AER but substantially higher NMSE, showing that accurate
activity decisions alone do not ensure accurate channel estimates.
''')
block(f,'Increasing $Q$ provides more measurements','\\subsubsection{Effect of Candidate Device Count}',r'''
More pilot frames constrain the same channel at fixed per-frame
energy. The gain over STMP decreases from $1.57$~dB at $Q=16$
to $0.51$~dB at $Q=48$. Reaching $-14$~dB on the tested grid
requires $24$ frames with GP-CCD-MP-DRE versus $32$ with STMP,
a $25\%$ reduction. At $Q=48$, AER is equal but the channel-NMSE
gap remains.
''')
block(f,'At fixed $p$, increasing $K$ enlarges','\\subsubsection{Effect of Nominal Activity Probability}',r'''
Increasing $K$ at fixed $p$ raises both the candidate dimension
$KN$ and expected active population, while each observation column
still has $Q$ measurements. Fixed aggregate SNR also lowers typical
per-device SNR. NMSE consequently increases for all methods.
GP-CCD-MP-DRE remains best: at target $-10$~dB, the largest tested
candidate populations are $80$ versus $40$ for STMP; at $K=100$,
its advantage over off-grid SBL is $2.53$~dB.
''')
block(f,'With $K$ fixed, this experiment keeps','\\subsection{Comparison Across Channel Profiles}',r'''
At fixed $K$, increasing activity raises the number of unknown active
coefficients without adding measurements, reducing activity sparsity.
GP-CCD-MP-DRE remains most accurate; its gain over STMP grows from
$1.07$~dB at $p=0.05$ to $2.25$~dB at $p=0.25$. At the latter
point, off-grid SBL slightly surpasses STMP but remains $2.15$~dB
behind GP-CCD-MP-DRE. Together with the device-count sweep, this
supports the proposed receiver under heavier access loads.
''')
block(f,'The preceding comparisons use profile D','\\begin{figure*}',r'''
Figure~\ref{fig:cstmp-cross} transfers the receivers trained on
profile D to profiles A, B, and C without retraining. Geometry
and receiver settings remain fixed; each of the $24$ profile--SNR
conditions uses $500$ paired scenes.
''')
block(f,'GP-CCD-MP-DRE remains substantially more accurate',None,r'''
GP-CCD-MP-DRE outperforms the four sparse-recovery baselines on
every evaluated profile. Gains over STMP at $0$~dB range from
$1.02$ to $1.60$~dB. It remains better on D and C throughout
the SNR range, but the ordering changes on A and B: the B curves
nearly coincide at $4$~dB, and STMP is better by $0.39$ and
$0.58$~dB at $6$~dB on A and B, respectively. Thus the learned
prior transfers beyond profile D, with profile-dependent high-SNR performance.
''')

f='appendix_parameter_estimation'
block(f,'Stack the received samples as','\\begin{equation}',r'''
Stack $[\mathbf Y_{\rm s}]_{qN+r,m}=Y_{qmr}$ into
$\mathbf Y_{\rm s}\in\mathbb C^{QN\times M}$. Approximate each
candidate device by one dominant path with unconstrained
per-antenna gains. Absorbing the common scalar phase into the gain gives
''')
block(f,'The delay search is restricted','\\begin{equation}',r'''
Search $d\in[0,N)$ and $|\nu|\leq\nu_{\max}$. Since
$2Nc_1\in\mathbb N_+$, shifts by integer multiples of $N$ change
the operator only by a scalar phase absorbed by the fitted gains.
With $\mathbf h_k=\mathbf h_k(d_k,\nu_k)$ and
$\mathbf b_k\in\mathbb C^M$, minimize
''')
block(f,'The gains are eliminated from the separable','\\begin{equation}',r'''
Variable projection eliminates the gains \cite{oleary2013}.
Coarse delay, within-frame Doppler, and frame-phase correlations
initialize candidates; phase $\beta$ admits Doppler aliases
''')
block(f,'Candidates are ranked using the pilot response','\\subsection{Noise variance estimation}',r'''
Rank candidates by \eqref{frontend:eq:phase-atom}, enforcing the
same Doppler within and across frames. Refine by L-BFGS-B
\cite{zhu1997} within one differentiable waveform branch, accepting
only updates that do not increase residual energy beyond numerical
tolerance. Jointly refit all gains after each sweep. Use a fixed
number of sweeps and, after the first, include the previous position
as a refinement start. Finally set
$\widehat\beta_k=\operatorname{wrap}(2\pi\widehat\nu_kT_{\rm frame})$
and form $\widehat{\mathbf A}$ by \eqref{eq:effective-pilot}.
The nonlinear denoiser still estimates the full channel tensor.
''')
block(f,'Under a lower-rank spatial signal plus white-noise model',None,r'''
Under a lower-rank spatial signal plus white noise, the selected
rank leaves the trailing eigenvalues for noise estimation.
$\widehat\sigma^2$ and $\widehat{\mathbf A}$ remain fixed during MP.
''')

f='appendix_afdm_channel_model'
block(f,'At integer sample times in the useful interval','For normalized delay',r'''
For integer useful samples, $\varphi_n(t)=[\mathbf F_{\rm A}^{\mathsf H}]_{tn}$;
for $\xi<0$, it satisfies the CPP relation \eqref{eq:cpp}
\cite{bemani2022}.
''')
block(f,'where $\\zeta_{tn}=','\\begin{align}',r'''
where $\zeta_{tn}=\zeta_n(\langle t-d\rangle_N)$.
Integer phase factors cancel because $t,\zeta_{tn}$ are integers
and $w_{t-d}-(t-d)$ is an integer multiple of $N$.
For integer $d$, the final factor is one, giving
''')

f='appendix_implementation'
block(f,'The reference scale for the normalized training coordinates','The classifier takes',r'''
The normalization scale is $s=0.2647966453$. Selected checkpoints
are epoch $200$ for the denoiser and epoch $90$ for the classifier,
chosen by validation (Section~\ref{sec:simulation-settings}).
''')
# Appendix C and all stopping formulas/parameters remain verbatim.
for f,text in texts.items():
 p=PAPER/'sections'/(f+'.tex');raw=p.read_bytes();nl='\r\n' if b'\r\n' in raw else '\n'
 p.write_bytes(text.replace('\n',nl).encode('utf-8'))
(RUN/'RESULT_EDITS.json').write_text(json.dumps(ops,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Applied',len(ops),'result/appendix prose edits; Appendix C unchanged.')
