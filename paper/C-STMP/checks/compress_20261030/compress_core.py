"""Tighten prose only; retain every numbered equation, figure and algorithm."""
from pathlib import Path
import hashlib,json
RUN=Path(__file__).resolve().parent
PAPER=RUN.parents[1]
base=json.loads((RUN/'BASELINE.json').read_text(encoding='utf-8'))
texts={p+'.tex':(RUN/'before'/(p+'.tex')).read_text(encoding='utf-8') for p in base['active_inputs']}
ops=[]
def block(file,start,end,new):
 rel='sections/'+file+'.tex';t=texts[rel]
 assert t.count(start)==1,(file,start,t.count(start))
 a=t.index(start);b=t.index(end,a)
 old=t[a:b]
 texts[rel]=t[:a]+new.strip()+'\n\n'+t[b:]
 ops.append({'file':rel,'before':old,'after':new.strip()+'\n\n'})

block('01_introduction','Sixth-generation','The remainder of this paper',r'''
Sixth-generation (6G) networks must connect large numbers of
Internet-of-Things (IoT) devices, including remote, power-limited
devices served by low Earth orbit (LEO) satellites
\cite{cai2026,xu2026,shen2025}. Their short, sporadic transmissions
favor grant-free random access (GFRA), which avoids the handshaking
overhead and propagation latency of grant-based access
\cite{cai2026,xu2026}.

LEO links introduce large delays and Doppler shifts. The 3rd Generation
Partnership Project (3GPP) Release 17 framework uses global navigation
satellite system (GNSS)-assisted device-side precompensation
\cite{3gpp38300}; many satellite GFRA schemes consequently assume
perfect compensation or small residual offsets \cite{shen2025}.
Frequent estimation and compensation consume energy, motivating
GNSS-independent operation as considered in the Release 19 study
\cite{3gpp22865}. The receiver must then accommodate large differential
delays and Doppler shifts, which cause inter-symbol and inter-carrier
interference in orthogonal frequency division multiplexing (OFDM)
\cite{shen2025,huang2026}.

Orthogonal time frequency space (OTFS) modulation exploits quasi-static
delay--Doppler channels \cite{shen2025,hadani2017}. Multi-frame OTFS
in \cite{shen2025} handles these offsets without device-side GNSS
precompensation, but its two-dimensional transformation incurs higher
modulation complexity \cite{ding2026,huang2026}. Affine frequency
division multiplexing (AFDM) uses one-dimensional chirp modulation
and, with suitable chirp parameters, achieves full diversity over
doubly dispersive channels at lower modulation complexity
\cite{bemani2022,ding2026,huang2026}.

AFDM-GFRA requires joint activity detection and channel estimation
(JADCE). Compressed sensing (CS) methods exploit sporadic activity
and structured channel sparsity \cite{shen2025,ding2026}; the graph
neural network in \cite{ding2026} learns sparsity patterns on a
predefined delay--Doppler grid. Fractional delays and Doppler shifts,
however, cause power leakage that weakens effective-channel sparsity
\cite{huang2026}, motivating priors learned directly from channel
samples \cite{cai2026,huang2026}.

Score-based generative models learn such priors through the channel
distribution's score function \cite{song2019,arvinte2023}.
The AFDM estimator in \cite{huang2026} addresses fractional
delay--Doppler leakage, while \cite{ying2026} combines a Transformer
activity detector with diffusion-based channel estimation and data
detection. Both require repeated score evaluations for iterative
posterior sampling. Score-based turbo message passing (STMP)
\cite{cai2026} instead uses Tweedie's formulas and separate first-
and second-order score networks for single-step minimum mean-squared
error (MMSE) denoising under equivalent additive white Gaussian noise
(AWGN) observations.

The AWGN approximation is justified in the large-system limit with
right-rotationally invariant sensing matrices \cite{cai2026}.
Finite-dimensional, structured multi-frame AFDM can depart from these
conditions, increasing the mismatch between denoiser input errors and
white-noise training perturbations; a related limitation is reported
in \cite{wei2026}. Furthermore, STMP computes activity probabilities
from Gaussian extrinsic messages after posterior projection.
For a non-Gaussian channel prior, matching posterior moments need not
preserve the marginal likelihood. The resulting activity-probability
errors can therefore affect channel estimation even when the
conditional moments are accurate.

We investigate GNSS-independent AFDM-GFRA with the following contributions:
\begin{enumerate}[label=\arabic*)]
\item A multi-frame AFDM model retains fractional delay--Doppler effects
and CPP phases for delays exceeding the useful symbol duration.
Separating inter-frame phases yields a multiple measurement vector
(MMV) model: additional pilot frames provide observations of the
same effective channel without increasing its dimension.
\item A score-based generative prior is learned from multiantenna AFDM
effective channels using colored Gaussian perturbations. The trained
denoiser provides posterior means and variances for message passing.
\item A learned density-ratio estimator supplies soft activity
probabilities, which combine with the channel moments to form
Gaussian extrinsic messages. The resulting JADCE receiver improves
on STMP across the evaluated SNR and pilot-frame grids.
\end{enumerate}
''')

block('02_system_model','We consider an AFDM-GFRA system','\\subsection{Terrestrial-Satellite',r'''
A LEO satellite with $M=M_yM_z$ antennas serves $K$ single-antenna
devices sharing pilot resources \cite{ding2026,shen2025}.
The devices operate without GNSS or delay/Doppler precompensation
\cite{shen2025}.
''')
block('02_system_model','The terrestrial-satellite links','\\begin{equation}',r'''
Satellite mobility and multipath propagation produce doubly dispersive
terrestrial-satellite links (TSLs) \cite{shen2025}. Taking each ground
device as stationary, we assume a common Doppler shift $\nu_k$ for
its paths \cite{huang2026}. Let $\mathbf a_k$ be its uniform planar
array (UPA) response and $t_{\rm c}$ the time from the block start.
After receiver compensation for the common delay $\tau_c$, the
impulse response is
''')
block('02_system_model','where $k=1,\\ldots,K$','For antenna indices',r'''
where $k=1,\ldots,K$, $L_k$ is the path count, $g_{k\ell}$ the path
gain, and $\delta(\cdot)$ the Dirac delta.
The differential delay $\tau_{k\ell}=\widetilde\tau_{k\ell}-\tau_c$
subtracts the propagation time to the closest point in the beam
footprint from the path delay $\widetilde\tau_{k\ell}$ \cite{shen2025}.
''')
block('02_system_model','Here, $\\lambda$ is the wavelength','\\subsection{Multi-Frame',r'''
Here $\lambda$ is the wavelength; $\bigl(d_y,d_z\bigr)$ and
$\bigl(\mu_{y,k},\mu_{z,k}\bigr)$ are the element spacings and
directional cosines along the two array axes \cite{shen2025,li2023}.
Path gains, delays, Doppler shifts, and arrival angles are approximately
constant within a transmission block.
''')
block('02_system_model','The $k$-th device transmits signal','\\begin{equation}',r'''
With subcarrier spacing $\Delta f$ and sampling interval
$T_s=1/(N\Delta f)$, the inverse discrete affine Fourier transform
(IDAFT) gives, for $t=0,\ldots,N-1$ \cite{ding2026},
''')
block('02_system_model','where $H_{kmrn}$ is the channel coefficient','\\begin{equation}',r'''
where $H_{kmrn}$ maps transmitted symbol $n$ to received symbol $r$
at antenna $m$. For a unit-gain path of normalized delay $d$ and
Doppler $\nu$, starting at sample $g$, the path matrix is
''')
block('02_system_model','Here, $\\varphi_n$ is the $n$th','For frame $q$',r'''
The CPP-extended basis $\varphi_n$ is defined in
Appendix~\ref{app:afdm-model}; frame $0$ starts at $g=N_{\rm CPP}$.
Fractional delays and Doppler shifts cause power leakage in this
matrix and weaken the sparsity of $H_k$ \cite{huang2026}.
''')
block('02_system_model','The phase rotation $e^{jq\\beta_k}$','\\subsection{Problem Formulation}',r'''
Thus the $Q$ frames observe the same $H_k$ up to phase rotation.
''')
block('02_system_model','We directly estimate the full AFDM','\\begin{equation}',r'''
We estimate the full $H_k$ without imposing channel sparsity
\cite{huang2026}. For $Q<KN$, \eqref{eq:mmv} is underdetermined,
but device inactivity gives block sparsity through
$X_k=\alpha_kH_k=\mathbf0$ \cite{cai2026}.
For Bayesian JADCE, fix $\widehat{\mathbf A}$ and
$\widehat\sigma^2$ as in Section~\ref{sec:frontend}.
The training prior $q_{\rm tr}$ retains dependence within $H_k$;
devices and their activity/channel variables are otherwise independent.
With Bernoulli activity priors, the posterior factorizes as
''')
block('02_system_model','where $\\mathbf x_j\\in','\\begin{equation}',r'''
where $\mathbf x_j\in\mathbb C^{KN}$ and $\mathbf y_j\in\mathbb C^Q$
are columns of $\mathbf X$ and $\mathbf Y$,
$p(\mathbf y_j\mid\mathbf x_j)=\CN(\mathbf y_j;
\widehat{\mathbf A}\mathbf x_j,\widehat\sigma^2\I_Q)$,
$p(X_k\mid H_k,\alpha_k)$ enforces $X_k=\alpha_kH_k$, and
$p(\alpha_k)=\rho^{\alpha_k}(1-\rho)^{1-\alpha_k}$.
The desired MMSE estimate and activity probability are
''')
# The final sentence is only a repeated transition to Section III.
rel='sections/02_system_model.tex'
t=texts[rel];a=t.index('Message-passing algorithms provide an iterative approach')
ops.append({'file':rel,'before':t[a:],'after':''});texts[rel]=t[:a]

block('03_bayesian_receiver_design','GP-CCD-MP-DRE uses a generative prior','\\begin{figure}',r'''
GP-CCD-MP-DRE combines a generative prior (GP), learned by
covariance-conditioned denoising (CCD) with colored perturbations,
with message passing (MP) and density ratio estimation (DRE).

\subsection{Receiver Structure}
\label{sec:receiver-structure}

Following turbo message passing \cite{ma2015,cai2026}, the receiver
alternates multi-frame linear estimation (MFLE) and
generative-prior-aided joint denoising (GPJD), as shown in
Fig.~\ref{fig:receiver-structure}. The phases
$\widehat{\mathbf A}$ and noise variance $\widehat\sigma^2$ remain
fixed within the block.
''')
block('03_bayesian_receiver_design','MFLE combines the received pilots','\\subsection{Multi-Frame Linear',r'''
MFLE supplies linear posterior moments; GPJD combines channel moments
from the denoiser and its derivatives with activity probabilities from
the classifier. Extrinsic messages divide each Gaussian posterior
approximation by its incoming message, as in expectation propagation
\cite{minka2001,cai2026}.
''')
block('03_bayesian_receiver_design','The MFLE module combines the multi-frame','\\begin{align}',r'''
The incoming message has mean
$\mathbf X^{\rm pri}\in\mathbb C^{KN\times MN}$ and per-column
covariance $\gamma\I_{KN}$, where $\gamma>0$.
The device-dependent factors $e^{j(q-q')\beta_k}$ prevent pilot row
orthogonality from carrying over to $\widehat{\mathbf A}$, so we
retain its full Gram matrix. Linear MMSE estimation with the Gaussian
likelihood in \eqref{eq:working-posterior} gives \cite[Sec.~III-A]{cai2026}
''')
block('03_bayesian_receiver_design','The GPJD module combines the channel prior','\\begin{equation}',r'''
GPJD uses the local denoising model \cite[Sec.~III-B]{cai2026}
''')
block('03_bayesian_receiver_design','This decomposition separates conditional channel uncertainty','\\begin{equation}',r'''
The two covariance terms describe channel and activity uncertainty
\cite[Secs.~III-C--III-D]{liu2018}, \cite[Sec.~III-B]{cai2026}.
We approximate the active-channel mean by
$F_k=F_\theta(R_k,v\I_D)$ and its variance by the fixed-covariance
derivative estimate $\widehat\tau_k$ in
Section~\ref{sec:conditional-error}. Pooling across devices gives
''')
block('03_bayesian_receiver_design','For each device, we maintain a Gaussian site','\\begin{equation}',r'''
A Gaussian site approximation to the channel prior
\cite[Sec.~2.1]{vehtari2020} has form
$\CN(\vect(H_k);\vect(E_k),c_k\I_D)$.
Within the training variance range and for $0<\tau<v$, dividing
the Gaussian approximation with moments $(F_k,\tau)$ by the input
likelihood updates the site as
''')
block('03_bayesian_receiver_design','Section~\\ref{sec:density-ratio} shows how subtracting','\\begin{equation}',r'''
The subtraction estimates the log density ratio
(Section~\ref{sec:density-ratio}). The approximate local posterior is
''')
block('03_bayesian_receiver_design','The mixture in \\eqref{eq:mixture} approximates','\\begin{equation}',r'''
Reshape $\mu_k$ into $\mathbf U_k\in\mathbb C^{M\times N^2}$,
with one row per antenna. Its average spatial covariance is
''')
block('03_bayesian_receiver_design','The two terms retain the conditional channel uncertainty','\\begin{equation}',r'''
Averaging over devices and complex coordinates gives the feedback variance
''')
block('03_bayesian_receiver_design','These parameters specify the outgoing Gaussian message','\\begin{equation}',r'''
Holding \eqref{eq:mixture} fixed, the Gaussian variance update
\cite[Sec.~III-A]{vila2013} applied to \eqref{eq:pseudo-awgn}
gives the denoiser input-variance target
''')

block('04_generative_priors','The GPJD module requires conditional channel moments','\\subsection{Channel Denoiser',r'''
We train a channel denoiser with colored Gaussian perturbations
\cite{song2019,arvinte2023}, derive its conditional variance from
mean derivatives, and learn the activity density ratio with a binary classifier.
''')
block('04_generative_priors','The expectation is over clean channels','To control the input',r'''
The expectation averages clean channels, covariances, and perturbations.
At each fixed $C$, its unrestricted population minimizer is
$\mathbf m_{\mathbb R}(\mathbf u,C)$. Setting
$S_\theta=\bm\Sigma^{-1}(f_\theta-\mathbf u)$ converts the loss
to the squared score error against
$-\bm\Sigma^{-1}(\mathbf u-\mathbf h_{\mathbb R})$, weighted by
$\bm\Sigma$: a form of denoising score matching \cite{vincent2011}.
Conditioning on $C$ supplies the noise statistics
\cite[Sec.~III-B]{shastri2022}.
''')
block('04_generative_priors','The conditional mean also determines','\\begin{equation}',r'''
For $\mathbf P_{\mathbb R}=\operatorname{Cov}(\mathbf h_{\mathbb R}\mid
\mathbf u,C)$ and output-by-input Jacobian
$\mathbf J_m=\partial\mathbf m_{\mathbb R}/\partial\mathbf u$,
the fixed-$C$ identity in \cite[Prop.~1]{dytso2021} gives
''')
block('04_generative_priors','Here $\\tau^\\star$ is the average','\\begin{equation}',r'''
The trace sums real and imaginary variances; dividing by $D$ gives
the variance per complex coordinate. For $C=v\I_D$,
$\tau^\star=v\,\operatorname{div}\mathbf m_{\mathbb R}/(2D)$.
We replace the exact mean by $f_\theta$ and approximate the trace by
Monte Carlo finite differences \cite[Sec.~V-B]{metzler2014}.
Draw independent sign vectors $\mathbf z_\ell$ satisfying
$\E[\mathbf z_\ell\mathbf z_\ell^{\mathsf T}]=\I_{2D}$ and set
$\mathbf w_\ell=\bm\Sigma^{1/2}\mathbf z_\ell$. Then
''')
block('04_generative_priors','Both perturbed evaluations hold','\\subsection{Density Ratio',r'''
Both evaluations hold $C$ fixed and include the complete mean map
in \eqref{eq:mean-preconditioning}. Pooling by
\eqref{eq:pooled-variance} supplies the variance without a second
network; numerical settings appear in Appendix~\ref{app:implementation}.
''')
block('04_generative_priors','GPJD requires the density ratio','The classifier receives',r'''
Binary classification estimates $q_{1,v}/q_{0,v}$ \cite{menon2016}.
Sample activity $a\in\{0,1\}$ with
$\Pr(a=1)=\pi_{\rm tr}=1/2$: use $R=H+W$, $H\sim q_{\rm tr}$,
for $a=1$ and $R=W$ for $a=0$. In both classes,
$\vect(W)\sim\CN(\mathbf0,v\I_D)$ independently of $H$, and $v$
has the same sampling law, yielding \eqref{eq:query-densities}.
''')
block('04_generative_priors','The channel denoiser remains fixed during classifier training','\\begin{equation}',r'''
The frozen denoiser makes its output a deterministic function of
$R$ and $v$. At the population optimum over unrestricted logits,
binary cross-entropy recovers the training posterior log odds:
''')
block('04_generative_priors','The trained classifier approximates this ideal logit','\\subsection{Offline Training}',r'''
Subtracting $\logit\pi_{\rm tr}$ from the trained logit estimates
the log density ratio \cite[Sec.~4.2]{menon2016}; adding
$\logit\rho$ yields \eqref{eq:activity-probability}.
''')
block('04_generative_priors','We generate clean channel tensors before activity masking','After training the channel denoiser',r'''
Clean channels are sampled before activity masking, from disjoint
training and validation scenes. Draw $\log v$ uniformly over
$[\log v_{\min},\log v_{\max}]$ and use covariance
$C=v(R_{\rm a}\otimes\I_N\otimes R_{\rm c})$ in
antenna--output--input order; factors follow
\eqref{eq:simulation-colored-covariance}.
A RefineNet backbone \cite[Appendix~A.3]{song2019} with $128$ base
channels processes $2M$ real/imaginary input maps over the
$N\times N$ DAFT coordinates, conditioned on $v$ and the covariance factors.
''')
rel='sections/04_generative_priors.tex';t=texts[rel]
a=t.index('After training the channel denoiser')
new=r'''The denoiser is then frozen while the classifier is trained from
random initialization using \eqref{eq:classifier-loss}. It combines
maps of $R$ and $F_\theta(R,v\I_D)$ with variance, energy, and
inner-product features (Appendix~\ref{app:implementation}).
Both networks remain fixed online and operate per device, allowing
the same weights at fixed $M,N$ across different $K,Q$.
Dataset and optimization settings appear in
Section~\ref{sec:simulation-settings}.
'''
ops.append({'file':rel,'before':t[a:],'after':new});texts[rel]=t[:a]+new

block('05_overall_algorithm','This section combines the MFLE','\\subsection{Overall Algorithm}',r'''
Algorithm~1 combines the module updates and learned networks.
''')
block('05_overall_algorithm','Before the iterations, we form','The receiver uses the same',r'''
Form $\widehat{\mathbf A}$ from the available inter-frame phases
via \eqref{eq:effective-pilot}. When needed, estimate the phases
by variable projection \cite{oleary2013} and the physical noise
variance $\widehat\sigma^2$ by minimum description length
\cite{nadakuditi2008}, as detailed in Appendix~\ref{app:frontend}.
Both remain fixed within the block.
''')
# Noise is estimated even when phases are supplied: keep the two operations independent.
texts['sections/05_overall_algorithm.tex']=texts['sections/05_overall_algorithm.tex'].replace(
 'When needed, estimate the phases\nby variable projection \\cite{oleary2013} and the physical noise\nvariance $\\widehat\\sigma^2$ by minimum description length',
 'Estimate missing phases\nby variable projection \\cite{oleary2013}, and estimate the physical\nnoise variance $\\widehat\\sigma^2$ by minimum description length')
block('05_overall_algorithm','At iteration $i$, MFLE produces','\\begin{equation}',r'''
MFLE returns $(\mathbf R_{\rm L}^{(i)},v_{\rm L}^{(i)})$.
With $R_{{\rm L},k}^{(i)}$ reshaped per device, apply new-message
weight $\eta\in(0,1]$ \cite[Sec.~V-B1]{cai2026} for $i\geq2$:
''')
block('05_overall_algorithm','GPJD applies the updates in Section','\\begin{equation}',r'''
GPJD uses $v^{(i)}=\kappa^{(i)}\bar v^{(i)}$, held fixed during
the current update. Outside $[v_{\min},v_{\max}]$, retain the
sites and use their Gaussian density ratio:
''')
block('05_overall_algorithm','The same weight $\\eta$ is used','\\begin{equation}',r'''
Form the extrinsic message in \eqref{eq:nonlinear-extrinsic} using
the current $v^{(i)}$ and damp feedback with the same $\eta$ for $i\geq2$:
''')
block('05_overall_algorithm','After at least $I_{\\min}$ iterations','\\subsection{Computational Complexity',r'''
Stopping checks and numerical settings are specified in
Appendix~\ref{app:implementation}.
''')
block('05_overall_algorithm','Using standard dense matrix arithmetic','\\begin{equation}',r'''
For $Q\leq KN$, a thin SVD of $\widehat{\mathbf A}$ costs
$O(KNQ^2)$ once per block. Noise estimation costs
$O(QNM^2+M^3)$; let $C_{\rm phase}$ cover the phase search,
refinement, and gain refits in Appendix~\ref{app:frontend}.
Per iteration, MFLE transformations cost $O(QKMN^2)$, spatial
covariance operations $O(KM^2N^2)$, and matrix factorizations
$O(M^3)$. If $C_\theta,C_\phi$ are per-device denoiser/classifier
costs, GPJD requires $1+2L_z$ denoiser passes and one classifier
pass within the training interval. Hence
''')

for rel,text in texts.items():
 p=PAPER/rel
 assert hashlib.sha256(p.read_bytes()).hexdigest()==base['files'][rel],rel
for rel,text in texts.items():
 p=PAPER/rel;raw=p.read_bytes();nl='\r\n' if b'\r\n' in raw else '\n'
 p.write_bytes(text.replace('\n',nl).encode('utf-8'))
(RUN/'CORE_EDITS.json').write_text(json.dumps(ops,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Applied',len(ops),'prose edits.')
