from pathlib import Path
import hashlib
import re

RUN = Path(__file__).resolve().parent
PAPER = RUN.parents[1]
TARGET = PAPER / 'sections/06_simulation_results.tex'
BEFORE = RUN / 'before/sections/06_simulation_results.tex'
assert TARGET.read_bytes() == BEFORE.read_bytes(), 'Source changed since snapshot'
old = BEFORE.read_text(encoding='utf-8')

def environment(env, label):
    for match in re.finditer(r'\\begin\{' + re.escape(env) + r'\}.*?\\end\{' + re.escape(env) + r'\}', old, re.S):
        if r'\label{' + label + '}' in match.group():
            return match.group()
    raise ValueError(label)

def figure(label, wide=False):
    return environment('figure*' if wide else 'figure', label)

pilot = environment('equation', 'eq:pilot')
preconditioning = environment('equation', 'eq:mean-preconditioning')
gaussian = environment('equation', 'eq:gaussian-evidence')
parameters = environment('table', 'tab:simulation-parameters')
ablation = environment('table', 'tab:activity-evidence')

parts = [r'''\section{Simulation Results}
\label{sec:simulations}

\subsection{Simulation Settings}
\label{sec:simulation-settings}

\subsubsection{Channel Dataset and System Parameters}
Table~\ref{tab:simulation-parameters} summarizes the default settings.
Devices are uniformly distributed over the beam footprint, with delays,
Doppler shifts, and array responses determined by the geometry.
Large-scale effects are compensated. We use the NTN-TDL-D profile
\cite{shen2025}, with a delay spread drawn uniformly from $[30,50]$~ns,
a line-of-sight gain of fixed amplitude and uniform phase, and proper
complex Gaussian diffuse gains. Path parameters remain fixed per block.
The training and validation sets contain $50{,}000$ and $5{,}000$ clean
$16\times16\times16$ channels, respectively, drawn from disjoint sets
of scenes. Each scene provides four channel samples before multiplication
by $\alpha_k$.

For $Q\leq KN$, we select distinct DFT rows
$r_q\in\{0,\ldots,KN-1\}$, a column permutation
$\{c_{kn}\}_{k,n}$ of the same set, and independent phases
$\phi_{kn}\sim\mathcal U[0,2\pi)$. The pilots are
''', pilot, r'''
The total pilot energy per device is $QE_p$.

Independent Bernoulli activity variables with nominal probability $p$ are
conditioned on at least one active device. The receiver prior uses the
resulting marginal activity probability $\rho=p/[1-(1-p)^K]$.
We define the received SNR as the ratio of the average noiseless signal
power per complex observation to the noise variance.
For each scene, we compute this power over the $QMN$ entries of
$\mathbf A\mathbf X$ and set $\sigma^2$ to achieve the specified SNR.
''', parameters, r'''

\subsubsection{Network Architectures and Training}
\label{sec:network-settings}
\label{sec:training-settings}
Device matrices are reshaped to $M\times N\times N$ arrays for the
networks, preserving the order of antennas, received symbols, and transmitted
symbols in $\vect(\mathbf H_k)$.
The denoiser uses the RefineNet \cite{lin2017} variant in
\cite[Appendix~A]{song2019}, with $2M$ real and imaginary input maps over
$N\times N$ DAFT coordinates. Table~\ref{tab:network-architectures}
lists the channel widths and spatial resolutions of the two networks.
Each denoiser stage contains two residual blocks, each with two
$3\times3$ convolutions, conditional instance normalization, and
exponential linear unit (ELU) activations. Four refinement blocks combine
the stage outputs and restore the resolution; the input and output layers
use $3\times3$ convolutions.

\begin{table}[!t]
\caption{Network Architectures}
\label{tab:network-architectures}
\centering
\small
\setlength{\tabcolsep}{3pt}
\begin{tabular}{@{}lcc@{}}
\toprule
Layer or stage & Channels & Map size \\
\midrule
\multicolumn{3}{@{}l}{\textit{Channel denoiser}} \\
Input convolution & $128$ & $N\times N$ \\
Residual stage 1 & $128$ & $N\times N$ \\
Residual stage 2 & $256$ & $N/2\times N/2$ \\
Residual stage 3 (dilation 2) & $256$ & $N/2\times N/2$ \\
Residual stage 4 (dilation 4) & $256$ & $N/2\times N/2$ \\
Refinement blocks 1--2 & $256,256$ & $N/2\times N/2$ \\
Refinement block 3 & $128$ & $N/2\times N/2$ \\
Refinement block 4 & $128$ & $N\times N$ \\
Output convolution & $2M$ & $N\times N$ \\
\midrule
\multicolumn{3}{@{}l}{\textit{Activity classifier}} \\
Convolutional stage 1 & $64$ & $N\times N$ \\
Convolutional stage 2 & $128$ & $N/2\times N/2$ \\
Convolutional stage 3 & $128$ & $N/4\times N/4$ \\
Fully connected layers & $128,1$ & --- \\
\bottomrule
\end{tabular}
\end{table}

For conditioning, $\log(v)/5$ and flattened real and imaginary entries of
$\mathbf R_{\rm a}-\I_M$ and $\mathbf R_{\rm c}-\I_N$ pass through two
$64$-unit fully connected layers with sigmoid-weighted linear unit (SiLU)
activations, followed by linear projections to the normalization layers.
The denoiser uses a matrix extension of the scalar preconditioning in
\cite[Sec.~5]{karras2022}, with matrix coefficients as in
\cite[Appendix~B.1]{albuquerque2024}:
''', preconditioning, r'''
Here $\sigma_{\rm d}^2=1/2$ is the nominal variance per real coordinate after
normalization, and $\mathbf g_\theta$ is the RefineNet described above.

The classifier takes $4M$ real and imaginary maps of $\mathbf R$ and
$\mathbf F_\theta(\mathbf R,v\I_D)$, scaled by $\sqrt{2/(1+v)}$, plus five scalars:
$\log(v)/5$, logarithmic transforms of input/output/residual energies
normalized by $Dv$, and a sign-preserving logarithmic transform of the
real inner product normalized by $Dv$.
Each of its three stages contains two $3\times3$ convolutions with SiLU
activations and padding $1$. The first convolution of stages~2--3 has
stride $2$; all others have stride $1$.
A $64$-unit fully connected SiLU layer embeds $\log(v)/5$; its linear
projections are added to each stage output. Flattened features and the
five scalars pass through the fully connected layers in
Table~\ref{tab:network-architectures}, with SiLU between them, yielding
one logit per device.

The denoiser is trained using Adam for $200$ epochs with batch size $64$,
initial learning rate $10^{-4}$, and exponential moving average decay
$0.999$. We select the model with the lowest validation loss under fixed
noise realizations. The white-noise reference uses the same clean channels
and number of epochs.

For colored-noise training, we use proper complex
Gaussian noise with covariance
$\mathbf C=v(\mathbf R_{\rm a}\otimes\I_{16}\otimes\mathbf R_{\rm c})$,
where the factors correspond to antennas, received symbols, and transmitted
symbols, respectively. We sample $v$ uniformly on a logarithmic scale over
$[10^{-3},10^2]$. The two covariance factors are generated independently.
For each factor, we draw a $16\times4$ matrix with independent $\CN(0,1)$
entries, multiply it by its conjugate transpose, and normalize the resulting
matrix to have trace $16$. We then take a convex combination of this matrix
and $\I_{16}$, with the weight of the former sampled uniformly from $[0,0.5]$.

We freeze the denoiser and train the classifier from random initialization
using the loss in \eqref{eq:classifier-loss}, with batch size $32$,
initial learning rate $3\times10^{-4}$, and $100$ epochs.
Model selection is based on validation loss.
Classifier training and receiver evaluation use $\mathbf C=v\I$.

\subsubsection{Compared Receivers}
\label{sec:compared-receivers}
We compare GP-MP-C with the following five baselines:
\begin{itemize}[leftmargin=*,topsep=2pt,itemsep=2pt,parsep=0pt]
\item \textbf{GP-MP:} This receiver adapts the STMP framework
\cite{cai2026} to the AFDM model. It uses a white-noise-trained first-order
score network, a learned second-order score network, and a classifier
for density ratio estimation.
\item \textbf{Simultaneous orthogonal matching pursuit (SOMP):}
\cite{TroppGilbertStrauss2006SOMP} This greedy method sequentially selects
dictionary atoms shared by the receive antennas and estimates their
coefficients by least squares. We use an integer delay--Doppler dictionary
and select up to $64$ atoms.
\item \textbf{GAMP-SBL:} This method uses generalized approximate message
passing in sparse Bayesian learning \cite{ZhangFanHaoQuan2023GAMPSBL}.
Our multiantenna implementation uses the integer delay--Doppler dictionary,
shares row precisions across receive antennas, and allows up to
$1{,}000$ iterations.
\item \textbf{GNN-ASPL:} This method alternates AMP-based channel estimation
with adaptive sparsity pattern learning using a graph neural network
\cite{ding2026}. It uses the same integer delay--Doppler dictionary and
a $10$-layer network.
\item \textbf{Off-grid SBL:} In addition to the channel coefficients,
this method estimates continuous delay and Doppler offsets through a
first-order linear approximation of the dictionary
\cite{WeiEtAl2022OffgridSBL}. We allow up to $120$ iterations.
\end{itemize}

\subsubsection{Evaluation Settings and Metrics}
\label{sec:receiver-settings}
\label{sec:stopping-criteria}
All receivers estimate the noise variance from the observations and use
known phases. GP-MP and GP-MP-C use activity threshold $0.5$,
with $I_{\min}=60$, $I_{\max}=600$, and relative-change tolerance
$5\times10^{-4}$. After $I_{\min}$ iterations, stopping is based on the
stability of channel and activity estimates and the consistency of variance
updates. If the stopping criterion is not met by $I_{\max}$, we return
the last iterate. The default damping factors for GP-MP and GP-MP-C
are $0.2$ and $0.4$, respectively.
GP-MP-C uses $L_z=1$ and $\delta_{\rm FD}=10^{-2}$ in
\eqref{eq:derivative-trace}, with the random sign vectors reused across
iterations. The common variance has a lower bound $\tau_{\min}=10^{-4}$.
\ifdefined\FullManuscript
The complete stopping checks and tolerances are given in
Appendix~\ref{app:implementation-settings}.
\fi

The SNR figure uses $1{,}000$ paired scenes per point. The pilot-frame,
device-count, activity-probability, and cross-profile figures use $500$
paired scenes per point. Scenes are reused across conditions.
\ifdefined\FullManuscript
Appendix~\ref{app:evaluation-protocol} gives the evaluation protocol.
\fi

For scene indices $e\in\mathcal T$ at a given condition, the
normalized mean-squared error (NMSE) is the sum of squared Frobenius
errors between $\widehat{\mathbf X}_{ek}$ and $\mathbf X_{ek}$, divided
by the sum of squared Frobenius norms of $\mathbf X_{ek}$.
Both sums cover all $K$ devices and all scenes in $\mathcal T$, and the
ratio is reported in decibels.
Here $\mathbf X_{ek}=\alpha_{ek}\mathbf H_{ek}$; errors on inactive devices
are included. For direct channel denoising, $\mathbf X$ is replaced by
$\mathbf H$ and the sums run over individual channel samples.
The activity error rate (AER) is the total number of missed detections
and false alarms divided by the $K|\mathcal T|$ device decisions.

\subsection{Channel Denoising Performance}
\label{sec:denoising-performance}
Before evaluating the complete receiver, we separately compare the channel
denoisers under AWGN, following \cite[Sec.~VI-B]{cai2026}.
We consider $\mathbf R=\mathbf H+\mathbf W$, with
$\vect(\mathbf W)\sim\CN(\mathbf0,v\I)$, known $v$, and nominal SNR
$-10\log_{10}v$. At each of six SNRs from $-20$ to $30$~dB, both
neural estimators share $2{,}000$ samples from $500$ scenes and the
same white-noise realizations. The following reference methods are included:
\begin{itemize}[leftmargin=*,topsep=2pt,itemsep=2pt,parsep=0pt]
\item \textbf{Least squares (LS):} The estimate is the noisy observation
$\mathbf R$.
\item \textbf{Gaussian-prior estimate:} The estimate is
$\widehat P_H\mathbf R/(\widehat P_H+v)$, where $\widehat P_H$ is the
training-channel power defined in Section~\ref{sec:schedule}.
\item \textbf{Genie-aided conditional MMSE:} We compute the analytic
conditional MSE of the remaining Gaussian gains given the true path
geometry, powers, and line-of-sight gain.
\end{itemize}
The four sparse-recovery methods in Section~\ref{sec:compared-receivers}
are also evaluated using an identity observation operator and known AWGN
variance. They retain their receiver settings and GNN weights;
GAMP-SBL retains its internal noise-variance update.
''', figure('fig:cstmp-denoising'), r'''

Figure~\ref{fig:cstmp-denoising} shows that the NMSE of both learned
denoisers continues to decrease with SNR, whereas the four sparse-recovery
methods approach error floors. The advantage of the learned denoisers
becomes more pronounced at moderate and high SNR.
The denoiser trained with colored noise has lower NMSE at low SNR than
the white-noise-trained denoiser, even though both are tested under AWGN.
Both learned curves remain above the genie-aided reference, which uses
true path information.

\subsection{Effect of Density Ratio Estimation}
\label{sec:activity-evidence}
We next examine the role of the learned density ratio in the activity
probability update. As a comparison, the Gaussian approximation gives
''', gaussian, r'''
We replace \eqref{eq:activity-probability} with \eqref{eq:gaussian-evidence},
keeping the remaining receiver settings unchanged.
Both versions use known phases and $354$ paired scenes per SNR.
Table~\ref{tab:activity-evidence} reports AER over all runs and the percentage
reaching the $600$-iteration limit.
''', ablation, r'''

The learned density ratio gives lower AER at every evaluated SNR, with no
runs reaching the iteration limit. For the Gaussian approximation, both
AER and the iteration-limit rate decrease with SNR, but remain higher
than those obtained with the learned density ratio.
False alarms account for $31{,}207$ of its $31{,}394$ pooled activity errors.
The difference in AER is therefore dominated by false activity declarations,
supporting the use of a learned density ratio for the activity update.

\subsection{JADCE Performance}
\label{sec:jadce-performance}
Unless stated otherwise, the receivers use the defaults in
Table~\ref{tab:simulation-parameters} and the evaluation settings in
Section~\ref{sec:receiver-settings}.
''', figure('fig:cstmp-convergence'), r'''

Figure~\ref{fig:cstmp-convergence} shows the NMSE versus iteration at
$0$~dB for one paired scene with five active devices.
GP-MP-C approaches its final NMSE in fewer iterations than GP-MP and
attains a lower final error in this example. Under the adopted stopping
criteria, GP-MP-C stops at the minimum of $60$ iterations, compared with
$85$ for GP-MP.
''', figure('fig:cstmp-snr'), r'''

Figure~\ref{fig:cstmp-snr} compares channel NMSE and AER over
$-4$ to $6$~dB. GP-MP-C achieves the lowest NMSE throughout this range.
Its advantage over GP-MP is more pronounced at low SNR and narrows as
SNR increases. The four sparse-recovery baselines improve more slowly
with SNR, leaving a larger NMSE gap relative to the learned receivers
at higher SNR.

The AER also generally decreases with SNR. GP-MP-C has lower AER than
GP-MP throughout the range and outperforms the four sparse-recovery
baselines at moderate and high SNR. The AER reduction relative to GP-MP
comes mainly from fewer missed detections; false alarms remain rare in
both configurations.
''', figure('fig:cstmp-users'), r'''

Figure~\ref{fig:cstmp-users} compares the channel NMSE for $K=20$--$100$
at $0$~dB, with $Q=16$ and $p=0.1$.
At fixed activity probability and pilot-frame count, increasing $K$
enlarges the set of candidate channels and raises the expected number
of active devices. All methods exhibit higher NMSE as this load increases.
GP-MP-C maintains the lowest NMSE, and its advantage over GP-MP grows
with the number of candidate devices.
''', figure('fig:cstmp-activity'), r'''

Figure~\ref{fig:cstmp-activity} varies the nominal activity probability
from $0.05$ to $0.25$, with $K=40$, $Q=16$, and an SNR of $0$~dB.
Here the candidate set is fixed, while a larger fraction of devices
becomes active. Channel estimation degrades for all methods, but GP-MP-C
retains the lowest NMSE and its advantage over GP-MP increases.
Together with Fig.~\ref{fig:cstmp-users}, this result shows that the
advantage persists when the load grows through either the candidate
device count or the activity probability.
''', figure('fig:cstmp-pilots'), '\n\n', figure('fig:cstmp-cross', wide=True), r'''

Figure~\ref{fig:cstmp-pilots} shows the effect of the number of pilot
frames at $0$~dB, with $K=40$ and $p=0.1$.
Additional frames provide further observations of the same effective
channels at fixed per-frame energy, and generally improve both channel
estimation and activity detection. Among the evaluated frame counts,
GP-MP-C first reaches $-14$~dB NMSE at $Q=24$, whereas GP-MP requires
$Q=32$. This corresponds to $25\%$ fewer pilot frames for the same
NMSE target.

\subsection{Comparison Across Channel Profiles}
To examine performance beyond the training distribution, we evaluate
the receivers on NTN-TDL profiles A, B, and C without retraining the
networks trained on profile D. Only the power delay profiles and fading
distributions change; geometry, pilots, and receiver settings remain
fixed, with known phases and $500$ paired scenes per condition.

Figure~\ref{fig:cstmp-cross} shows that GP-MP-C achieves lower NMSE than
the four sparse-recovery baselines on every evaluated profile.
The difference relative to GP-MP is smaller and varies with the profile
and SNR. The retained advantage over the sparse-recovery baselines
supports the use of the learned effective-channel prior beyond the
training profile without retraining.
''']

new = '\n'.join(parts).strip() + '\n'
TARGET.write_text(new, encoding='utf-8')
for env, label in [('equation','eq:pilot'), ('equation','eq:mean-preconditioning'),
                   ('equation','eq:gaussian-evidence'), ('table','tab:simulation-parameters'),
                   ('table','tab:activity-evidence')]:
    assert environment(env,label) in new
print('Revised chapter VI:',len(old.split()),'->',len(new.split()),'source tokens')
