from pathlib import Path
import re,json,difflib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
changes=[]
def revise(name,pairs):
    p=ROOT/'sections'/name
    old=p.read_text(encoding='utf-8')
    text=old
    for a,b in pairs:
        if text.count(a)!=1: raise ValueError((name,text.count(a),a[:100]))
        text=text.replace(a,b,1)
    p.write_text(text,encoding='utf-8')
    changes.append({'file':name,'before_words':len(old.split()),'after_words':len(text.split())})

revise('01_introduction.tex',[
 (r'monitoring \cite{shen2025}.',r'monitoring \cite{shen2025,kodheli2021}.'),
 (r'fraction active at a given time \cite{shen2025,cai2026}.',r'fraction active at a given time \cite{shen2025,cai2026,mei2022}.'),
 (r'\cite{shen2025,ding2026}. The scheme',r'\cite{shen2025,ding2026,ke2020}. The scheme'),
 (r'limit with right-rotationally invariant random sensing matrices \cite{cai2026}.',r'limit with right-rotationally invariant random sensing matrices \cite{cai2026,rangan2019}.'),
])
revise('03_bayesian_receiver_design.tex',[
 (r'$t_{\rm L}\I_{KN}$ \cite{ma2015,cai2026}.',r'$t_{\rm L}\I_{KN}$ \cite{ma2015,ma2017,cai2026}.'),
])
revise('04_generative_priors.tex',[
 ('first-order score function.','first-order score function \\cite{hyvarinen2005}.'),
])
revise('05_overall_algorithm.tex',[
 (r'''Substituting the estimators in Section~\ref{sec:learning} into the
framework of Section~\ref{sec:algorithm} yields GP-MP-CCD.
The multi-frame linear estimation (MFLE) and generative-prior-aided
joint denoising (GPJD) modules implement
Sections~\ref{sec:linear-estimation} and \ref{sec:joint-denoising},
respectively. Fig.~\ref{fig:learned-receiver} shows their message exchange.''',r'''GP-MP-CCD combines the multi-frame linear estimation (MFLE) in
Section~\ref{sec:linear-estimation} with generative-prior-aided joint
denoising (GPJD) using the estimators in Section~\ref{sec:learning}.
Fig.~\ref{fig:learned-receiver} shows their message exchange.'''),
 (r'''We update the site when the input variance lies within the training
range and $0<\tau^{\rm post}<v$; otherwise, the previous site is retained.

''',''),
 (r'''Combining $p_k$ with $(\mu_k,t_k)$ gives the joint estimate in
\eqref{eq:mixture} and covariance in \eqref{eq:joint-spatial-covariance}.
The Gaussian extrinsic message in \eqref{eq:nonlinear-extrinsic} is then
passed back to MFLE.
Algorithm~1 summarizes the iteration for fixed phases. When phases are
estimated, these updates alternate with the refinement described in
Appendix~\ref{app:phase-refinement}. In normalized coordinates,''',r'''Algorithm~1 combines these moments with $p_k$ and returns Gaussian
extrinsic messages to MFLE. Estimated phases are refined as in
Appendix~\ref{app:phase-refinement}. In normalized coordinates,'''),
 (r'''The parameter estimates, normalization,
and message damping are specified below.''',''),
 (r'''description length (MDL) criterion \cite{nadakuditi2008}.
Under a lower-rank spatial signal plus white noise, the trailing
eigenvalues estimate the noise variance, which remains fixed during MP.''',r'''description length (MDL) criterion \cite{wax1985,nadakuditi2008}.
Under a lower-rank spatial signal plus white noise, this estimate remains
fixed during MP.'''),
 (r'''To update the input variance $v$ in \eqref{eq:pseudo-awgn}, minimize
the expected Gaussian negative log likelihood with
the current approximate posterior \eqref{eq:mixture} held fixed
\cite[Sec.~III-A]{vila2013}.
For a candidate variance $\widetilde v$, the terms depending on it are
$KD\log\widetilde v+ \sum_k\E_{\widetilde
q_k}[\norm{R_k-X_k}_F^2]/\widetilde v$.
Minimizing this expression and expanding the expected squared error gives''',r'''Minimizing the expected Gaussian negative log likelihood over the input
variance $v$, with the current approximate posterior \eqref{eq:mixture}
held fixed \cite[Sec.~III-A]{vila2013}, gives'''),
 (r'''The current $v^{(i)}$ is used for both joint denoising and the extrinsic
update; the updated scale enters the following iteration.

The channel prior and online observations use the same fixed normalization.
Let $s$ denote the root mean square of the training-channel coefficients. We
divide $(H_k,X_k,\mathbf Y,\mathbf W)$ by $s$ and the physical noise
variance by $s^2$, retaining the same symbols for normalized quantities.
The pilot matrix is unchanged.
The MFLE output is damped by combining the current and previous messages
\cite[Sec.~V-B1]{cai2026} for $i\geq2$:''',r'''Joint denoising and the extrinsic update use the current $v^{(i)}$.
For normalization, we divide $(H_k,X_k,\mathbf Y,\mathbf W)$ by the training-channel
root mean square $s$ and the noise variance by $s^2$, retaining their
symbols and leaving the pilot matrix unchanged.
For $i\geq2$, the MFLE output is damped as \cite[Sec.~V-B1]{cai2026}'''),
 (r'''Outside the training variance range, the retained Gaussian sites provide the
activity density ratio specified in \eqref{eq:gaussian-evidence}.
''',''),
 (r'''Within the training interval, GPJD requires $1+2L_z$ denoiser evaluations
and one classifier evaluation.
The resulting per-iteration complexity is''',r'''The $1+2L_z$ denoiser evaluations and one classifier evaluation within the
training interval give the per-iteration complexity'''),
 (r'''For supplied phases, $C_{\rm phase}=0$.
With iterative phase refinement, the phase-update cost and a new
$O(KNQ^2)$ SVD are additionally incurred whenever the observation
matrix is rebuilt.
All devices share the trained parameters.
The working storage for the pilot/SVD factors, channel messages, and spatial
covariance matrices is $O(QKN+KMN^2+KM^2)$, excluding trained parameters and
network activations.''',r'''Here $C_{\rm phase}=0$ for supplied phases; each phase refinement also
requires a new $O(KNQ^2)$ SVD. With shared network parameters, working storage
is $O(QKN+KMN^2+KM^2)$ for pilot/SVD factors, channel messages, and spatial
covariances, excluding parameters and network activations.'''),
])
revise('06_simulation_results.tex',[
 (r'''We evaluate channel denoising, activity detection, and JADCE performance
under different system settings and channel profiles.

''',''),
 (r'''The channel denoiser uses a RefineNet backbone
\cite[Appendix~A]{song2019} with $128$ base channels. It processes
$2M$ real/imaginary input maps over the $N\times N$ DAFT
coordinates, conditioned on $v$ and the covariance factors.
The backbone has four stages, each containing two residual blocks,
with $128$, $256$, $256$, and $256$ channels, respectively.
Each block uses two $3\times3$ convolutions, conditional instance
normalization, and exponential linear unit (ELU) activations.
The second stage halves the spatial resolution; the last two stages
retain this resolution using dilation factors $2$ and $4$.
Four refinement blocks with $256$, $256$, $128$, and $128$ channels
combine the stage outputs and recover the input resolution.
The input and output projections use $3\times3$ convolutions.
The scaled log variance $\log(v)/5$ and flattened real/imaginary entries of
$\mathbf R_{\rm a}-\I_M$ and $\mathbf R_{\rm c}-\I_N$
pass through two fully connected layers of width $64$, each followed
by a sigmoid-weighted linear unit (SiLU), to condition the normalization
layers through learned linear projections.
To control scales across noise levels, we extend the scalar input,
skip, and output preconditioning in \cite[Sec.~5]{karras2022}
to the covariance matrix:''',r'''The denoiser uses the RefineNet \cite{lin2017} variant in
\cite[Appendix~A]{song2019}, with $2M$ real/imaginary input maps over
$N\times N$ DAFT coordinates. Its four stages have $(128,256,256,256)$
channels and two residual blocks each, with two $3\times3$ convolutions,
conditional instance normalization, and exponential linear unit (ELU)
activations per block. Stage~2 halves the resolution; stages~3--4 retain it
with dilations $2$ and $4$. Four refinement blocks with
$(256,256,128,128)$ channels combine the stage outputs and restore the
resolution; input/output projections use $3\times3$ convolutions.
For conditioning, $\log(v)/5$ and flattened real/imaginary entries of
$\mathbf R_{\rm a}-\I_M$ and $\mathbf R_{\rm c}-\I_N$ pass through two
$64$-unit fully connected layers with sigmoid-weighted linear unit (SiLU)
activations, followed by linear projections to the normalization layers.
We extend the scalar preconditioning in \cite[Sec.~5]{karras2022} to'''),
 (r'''The classifier receives real/imaginary maps of $R$ and $F_\theta(R,v\I_D)$
scaled by $\sqrt{2/(1+v)}$. Scalar inputs comprise $\log(v)/5$,
logarithmic transforms of input, output, and residual energies normalized
by $Dv$, and a sign-preserving logarithmic transform of the real inner
product normalized by $Dv$.
The $4M$ input maps pass through three stages of two $3\times3$
convolutions each, with $64$, $128$, and $128$ channels and SiLU
activations and padding $1$. The first convolution in the second and third stages
uses stride $2$; all other convolutions use stride $1$.
A $64$-unit fully connected layer with SiLU maps the scaled log variance
to a condition, whose linear projections are added to each stage output.
The final feature maps are flattened and concatenated with the five
scalar inputs, then passed through fully connected layers of widths
$128$ and $1$, with SiLU between them, to produce one logit per device.''',r'''The classifier takes $4M$ real/imaginary maps of $R$ and
$F_\theta(R,v\I_D)$, scaled by $\sqrt{2/(1+v)}$, plus five scalars:
$\log(v)/5$, logarithmic input/output/residual energies divided by $Dv$,
and the sign-preserving logarithm of the real inner product divided by $Dv$.
Three stages contain two $3\times3$ convolutions each, with
$(64,128,128)$ channels, SiLU, and padding $1$. The first convolution
of stages~2--3 has stride $2$; all others have stride $1$.
A $64$-unit fully connected SiLU layer embeds $\log(v)/5$; its linear
projections are added to each stage output. Flattened features and the
five scalars pass through fully connected layers of widths $(128,1)$,
with SiLU between them, yielding one logit per device.'''),
 (r'''Their
AFDM and multiantenna adaptations, weights, and activity readout rules
remain fixed.
SOMP selects at most $64$ atoms, GAMP-SBL allows $1{,}000$ iterations,
GNN-ASPL uses $10$ layers, and off-grid SBL uses $120$ iterations.''',r'''With fixed AFDM/multiantenna adaptations, weights, and activity readout,
SOMP selects up to $64$ atoms, GAMP-SBL and off-grid SBL allow
$1{,}000$ and $120$ iterations, and GNN-ASPL uses $10$ layers.'''),
 (r'''For GP-MP-CCD, the derivative estimate in
\eqref{eq:derivative-trace} uses $L_z=1$
and $\delta_{\rm FD}=10^{-2}$, with one random sign vector per device reused
throughout a transmission block. The pooled variance floor in
\eqref{eq:pooled-variance} is $\tau_{\min}=10^{-4}$.''',r'''GP-MP-CCD uses $L_z=1$, $\delta_{\rm FD}=10^{-2}$, and
$\tau_{\min}=10^{-4}$ in \eqref{eq:derivative-trace}--\eqref{eq:pooled-variance},
with a block-fixed random sign vector per device.'''),
 (r'''The training variance interval is $[v_{\min},v_{\max}]
=[10^{-3},10^2]$. Outside this interval, GP-MP-CCD retains
the Gaussian sites and computes the activity probability from
their Gaussian density ratio:''',r'''Outside the training interval $[v_{\min},v_{\max}]=[10^{-3},10^2]$,
the retained sites give'''),
])
(HERE/'TEXT_CHANGES.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
print(json.dumps(changes,indent=2))
