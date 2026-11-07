## 01_introduction

Introduction
 

Sixth-generation (6G) wireless networks are expected to provide ubiquitous
connectivity for a massive number of Internet-of-Things (IoT) devices
 . To serve devices in remote areas with limited terrestrial
coverage, low Earth orbit (LEO) satellites complement cellular networks for
applications such as smart agriculture and climate monitoring . These
power-limited devices transmit short packets sporadically, with only a small
fraction active at a given time . In grant-based random
access, handshaking before transmission incurs significant
signaling overhead, while the long propagation delay of terrestrial-satellite links
further increases access latency . Accordingly, grant-free
random access (GFRA) allows active devices to transmit pilots and data directly
without first obtaining a grant, reducing signaling overhead and access latency in LEO satellite IoT
systems .

Supporting GFRA over LEO links requires handling large delays and Doppler shifts
caused by long propagation distances and high satellite mobility. The 3rd Generation
Partnership Project (3GPP) Release 17 framework addresses these effects through
device-side pre-compensation assisted by the global navigation satellite system
(GNSS) . With such pre-compensation, many existing satellite GFRA
schemes assume perfect compensation or small residual delays and Doppler shifts at
the receiver . However, frequent estimation and compensation increase
energy consumption and reduce battery lifetime, making these schemes less suitable
for power-limited remote IoT devices . This motivates reducing
dependence on GNSS, consistent with the GNSS-independent operation considered in the
Release 19 study on satellite access . With reduced reliance on
device-side pre-compensation, the satellite receiver must accommodate
large differential delays and Doppler shifts, which can cause severe inter-symbol
and inter-carrier interference in conventional orthogonal frequency division
multiplexing (OFDM) systems .

To mitigate these effects, orthogonal time frequency space (OTFS) modulation
exploits the quasi-static properties of channels in the delay--Doppler domain
 . In , multi-frame OTFS transmission
handles large differential delays and Doppler shifts at the satellite receiver,
allowing devices to operate without GNSS assistance or pre-compensation of these
offsets. However, the two-dimensional transformation in OTFS entails relatively high
modulation complexity . Affine frequency division
multiplexing (AFDM), based on one-dimensional chirp modulation, offers lower
modulation complexity than OTFS while retaining strong Doppler robustness over
doubly dispersive channels . With properly
designed chirp parameters, AFDM can also achieve full diversity over such channels
 . This combination of low modulation complexity and full diversity
makes AFDM attractive for GFRA with power-limited IoT devices.

To unleash the full potential of AFDM-GFRA, accurate joint activity detection and
channel estimation (JADCE) is a critical prerequisite . Existing
methods exploit sporadic device activity to formulate JADCE as a compressed sensing
(CS) problem and incorporate structured priors to capture channel sparsity
 . The scheme in further uses a graph neural
network to adaptively learn sparsity patterns, while retaining a predefined
delay--Doppler grid for the sparse channel representation. However, in practical
propagation environments, fractional Doppler shifts and fractional time delays can
introduce significant power leakage in the effective channel matrix, thereby
weakening its sparsity . This motivates learning effective-channel
priors from data to capture channel structures beyond the assumed sparse
representation .

Score-based generative models learn channel priors from samples by estimating the
score function of the channel distribution . In
 , score-based learning is performed directly on the AFDM effective
channel to address fractional delay--Doppler off-grid leakage in channel estimation.
For massive random access, proposes a two-stage algorithm that first
identifies active users through a Transformer-based detector and then uses
generative diffusion models for joint channel estimation and data detection.
However, both approaches rely on iterative posterior sampling, which requires
repeated score function evaluations and incurs substantial computational cost
 .

To avoid iterative posterior sampling, develops a score-based turbo
message passing (STMP) algorithm that incorporates generative channel priors for
JADCE. Through Tweedie's formulas, separate first- and second-order score networks provide
posterior means and variances for single-step minimum mean-squared error (MMSE)
denoising under equivalent additive white Gaussian noise (AWGN) observations.
However, this AWGN model is justified in the large-system
limit with right-rotationally invariant random sensing matrices .
In the finite-dimensional, structured multi-frame AFDM system considered here,
departures from these conditions can exacerbate the mismatch between denoiser
input errors and the white Gaussian perturbations used for training. A similar
limitation has been highlighted for structured compression matrices in . This
mismatch can degrade channel denoising accuracy and, consequently, JADCE
performance. Moreover, computes activity probabilities using
Gaussian extrinsic messages obtained after projecting the channel posterior onto
a Gaussian distribution. In general, matching posterior means and variances does
not preserve the marginal likelihood associated with a non-Gaussian channel
prior. Consequently, the resulting likelihood ratio can yield inaccurate
activity probabilities even when the channel posterior moments are accurately
estimated. These errors further affect the activity-weighted channel estimates
exchanged with the linear estimation module.

Against this background, we investigate GNSS-independent AFDM-GFRA for
LEO satellite IoT systems. Our main contributions are summarized as follows:

enumerate[label=*)]
 We develop a multi-frame AFDM transmission scheme that handles large differential
delays and Doppler shifts at the satellite receiver. The derived input--output
relationship retains fractional delay--Doppler effects and the chirp-periodic prefix
phase for delays exceeding the useful symbol duration. Separating the phase
evolution across frames yields a multiple measurement vector (MMV) model in which
the effective channel of each device remains approximately constant over
consecutive frames. Additional pilot frames therefore provide more observations
without increasing the number of channel coefficients to be estimated.

 We learn a score-based generative prior directly from multiantenna AFDM
effective-channel samples with fractional delays and Doppler shifts. The denoiser is
trained with colored Gaussian perturbations and conditioned on their covariance to
account for correlations in the denoiser input error.

 We develop a message-passing JADCE receiver for the structured multi-frame AFDM
observation model. A learned density-ratio estimator compares the active and inactive
observation distributions under the effective-channel prior to obtain soft activity
probabilities. These probabilities are combined with channel posterior mean and
variance estimates obtained using the learned prior to form Gaussian extrinsic
messages for iterative exchange with the linear estimation module.
Simulation results demonstrate that the proposed receiver improves activity
detection and channel estimation performance compared with STMP across different
signal-to-noise ratios and pilot-frame counts.
enumerate

The remainder of this paper is organized as follows. Section 
presents the system model and the multi-frame AFDM input--output relationship.
Sections -- describe the receiver design, the
channel and activity denoisers, and the overall algorithm with its computational
complexity analysis, respectively. Section presents the
simulation results.

## 02_system_model

System Model
 

We consider an AFDM-GFRA system in which a LEO satellite equipped
with antennas serves single-antenna devices
 . During each transmission block, active devices share the same
time-frequency resources to transmit their pilots to the satellite.
Additionally, to minimize energy consumption, we assume that these
terrestrial devices operate without GNSS capabilities and do not
pre-compensate for delay and Doppler shifts .

Terrestrial-Satellite Link Model

The terrestrial-satellite links (TSLs) will experience fast variations
due to the high mobility of the LEO satellite. Hence, this time variation
and multipath propagation require a doubly dispersive channel model
for accurate TSLs characterization . We take the ground device as the stationary reference
point and assume that all propagation paths of device share the
same Doppler shift .
Let denote the uniform planar array (UPA) response vector
of device , and let denote the time measured from the
start of the transmission block. After compensation for the common
propagation delay at the satellite receiver, the time-varying
channel impulse response from device to the satellite is
 
where , is the number of physical paths,
 is the complex gain of the th path, and
 is the Dirac delta function. represents the differential
delay for the th path from device to the satellite, where
 and are denoted as propagation delay
and common delay, respectively. The common delay corresponds to the propagation time between
the satellite and the closest point on Earth within the beam coverage
 .

For antenna indices and
 , the entries of are given by
 
Here, is the wavelength, are the spacings
between adjacent antennas along the y-axis and z-axis, and
 are the directional cosines along these
axes, respectively . The path gains, differential delays, Doppler shifts, and
angles of arrival are assumed to remain approximately constant
within a transmission block.

Multi-Frame AFDM Transmission

We allocate AFDM frames to pilot transmission ,
with chirp subcarriers per frame .
Let be the pilot symbol transmitted by
the -th device during the -th AFDM frame on the -th
chirp subcarrier. The corresponding
pilot vector is
 , , .
Let denote the pilot matrix
known at the satellite receiver, with entries
 .
For simplicity, is chosen to satisfy
 , with equal pilot energy
 for all devices and frames .
The pilot construction is given in Section .

The -th device transmits signal using AFDM
modulation with sub-carriers and sub-carrier spacing ,
where gives the sampling interval.
For sample index , the time-domain transmitted
signal is generated through the inverse discrete affine Fourier
transform (IDAFT) applied to , mathematically
formulated as 
 
where and are AFDM modulation parameters. The signal in can be represented in
matrix form as
 
where
 
denotes the discrete affine Fourier transform (DAFT) matrix.

Assume that the chirp-periodic prefix (CPP) length is greater than
or equal to the maximum channel delay spread, i.e.,
 .
By the chirp periodicity, the prefix samples satisfy 
 
where and
 .
Including the CPP, each AFDM frame has duration
 .

After CPP removal and DAFT demodulation, the effective channel of
device in frame is represented by
 , with
 . Retaining fractional
delay and Doppler effects , the entries of are
 
where is the channel coefficient from transmitted
DAFT-domain symbol to received DAFT-domain symbol at
antenna .
The matrix is the effective channel
matrix of a path with gain , normalized delay , and Doppler
shift in frame . For a useful interval starting at sample
 of the transmission block, the path matrix is
 
Here, is the th AFDM basis waveform with its CPP
extension, defined in Appendix , and frame 
corresponds to . In practical propagation environments, fractional Doppler
shifts and fractional time delays can introduce significant
power leakage in the effective channel matrix of
 , thereby weakening the sparsity of
 .

For frame , the samples after CPP removal start at
 .
Since is common to all paths of device ,
 yields
 
where maps an angle to .
The phase rotation accounts for the variation of
 across frames, so the frames provide multiple
observations of .

Problem Formulation

We use an indicator function to model the device activity as
 
 
Let represent the probability of a device being active, i.e.,
 , where . Each device maintains
its activity state throughout a transmission block. We define
 and incorporate the inter-frame phase rotation
into the pilot symbols as
 
After removing the CPP and applying the DAFT, the received signal
 during the th AFDM
frame is given by 
 
where is an
AWGN matrix with the elements i.i.d. drawn from .
We express the received signal over the AFDM frames
in a more compact form as
 
where ,
 , and
 .
The corresponding entries are defined by
 
We directly estimate the full AFDM effective channel tensor 
without imposing sparsity assumptions
 . Since , is underdetermined.
Due to the sporadic access of the devices, matrix exhibits
a block-sparsity structure. Specifically, if the th device is inactive,
we have .

In this paper, we aim to simultaneously detect the active devices
and estimate the corresponding channels based on the observation
 under a Bayesian inference framework .

To formulate the inference problem, we treat 
and as given. These estimates are obtained from
 as described in Section .
Let denote the prior distribution of represented
by the training channel samples. We assume independence across
devices and between each device's activity and channel. The
activities follow Bernoulli priors, while retains
the dependence among the coefficients within .

Under these assumptions, the joint posterior factorizes as
 
where and
 denote the -th column of
 and
 , respectively.
Here, denotes the joint posterior distribution, and
 is the
Gaussian likelihood associated with . The factor
 enforces , and
 .
Under this posterior, the MMSE channel estimate and posterior
activity probability are
 

Message-passing algorithms provide an iterative approach for
approximately calculating these quantities by plugging in deep
generative priors for efficient message calculation, eliminating
the need to compute high-dimensional integrals .

## 03_bayesian_receiver_design

Bayesian Receiver Design
 

GP-CCD-MP-DRE combines a generative prior (GP),
covariance-conditioned denoising (CCD), message passing (MP), and
density ratio estimation (DRE) to approximate the posterior in
 through iterative Gaussian message
exchange. Sections and 
describe the learned denoisers and the overall algorithm, respectively.

Receiver Structure
 

The factorization in separates the
multi-frame observation likelihood from the channel and activity
priors. Following the turbo message-passing structure in
 , we organize the receiver into two modules:
multi-frame linear estimation (MFLE) and generative-prior-aided joint
denoising (GPJD), as illustrated in Fig. .
The modules exchange Gaussian extrinsic messages parameterized by
a mean and a scalar variance, with and
 fixed within the transmission block.

 

MFLE combines the received pilots with the incoming Gaussian message
to obtain linear posterior moments. GPJD uses the channel and activity
priors to estimate the joint moments of and the
activity probabilities . It obtains the conditional channel mean
and variance from a trained denoiser and its derivatives, and the
activity density ratio from a classifier.

In both modules, extrinsic messages are obtained by dividing a
Gaussian approximation to the local posterior by its incoming
Gaussian message, as in expectation propagation
 . The following subsections derive the module
updates, while Section specifies their initialization
and message schedule.

Multi-Frame Linear Estimation
 

The MFLE module combines the multi-frame observations with the
incoming Gaussian message from GPJD. Let this message have mean
 and covariance
 for each column of , where .
The terminal-dependent phases in enter
the cross-frame inner products through .
Thus, the row orthogonality of need not carry over to
 , and we retain the full Gram matrix
 .

Multiplying the incoming message by the Gaussian likelihood in
 gives a Gaussian posterior. Its mean
and covariance follow from linear MMSE estimation
 :
 
To exchange a scalar variance between the modules, we approximate
 by , preserving its trace.
Dividing this Gaussian approximation by the incoming message yields
the extrinsic variance and mean :
 
A thin singular value decomposition (SVD) of 
can be reused throughout the block to evaluate these quantities;
the equivalent expressions are given in Appendix .

Generative-Prior-Aided Joint Denoising
 
 

The GPJD module combines the channel prior and activity prior with
the Gaussian message from MFLE. Following the local denoising model
in , we write
 
Here represents the uncertainty of the input to the denoiser.
Under , the input densities conditioned on
activity and inactivity are, respectively,
 
Bayes' rule then gives the exact activity probability for this local
model:
 
Let and
 
denote the channel moments conditioned on activity. The laws of
conditional expectation and covariance give the moments of
 as
 
This decomposition separates conditional channel uncertainty from
activity uncertainty, as in the activity-weighted moments in
 and .
Computing these moments requires the active-channel conditional mean
and covariance together with the density ratio .

To approximate the conditional channel moments, we evaluate the
pretrained mean network as . The derivative
of this map at fixed covariance provides the variance estimate
 , as described in
Section . We pool the estimates across
devices to obtain a shared variance per complex coordinate:
 
For each device, we maintain a Gaussian site approximation to the
channel-prior factor , with the form
 . When the input variance
lies within the training range and , we divide the
Gaussian conditional-posterior approximation with mean and
variance by the input likelihood to obtain
 
Otherwise, the previous site is retained. Combining the site with
the current input gives the approximate conditional channel variance
and mean:
 
Within the training variance range, we estimate the activity
probability from the output of the separately trained classifier:
 
where is the training class prior,
 , and .
Section derives the training-prior correction.
Combining with the conditional channel moments yields
 
The mixture in approximates the local posterior
of . Let reshape
 with one row per antenna. Averaging the corresponding
spatial covariance across its columns gives
 
The two terms retain the conditional channel uncertainty and
activity uncertainty in , respectively.
Their average over all devices and complex coordinates gives the
scalar posterior variance used for feedback:
 
To form the extrinsic message to MFLE, set
 , where
 . Dividing the Gaussian approximation with
mean and variance per complex coordinate by
the incoming Gaussian message gives
 
These parameters specify the outgoing Gaussian message to MFLE.

We also use the expected residual energy under the approximate
posterior to adjust the denoiser input variance. With
 held fixed, the Gaussian variance update in
 , applied to the local model
 , gives the target
 
The first term is the squared residual of the joint posterior mean,
and the second includes both channel and activity uncertainty.
Section specifies how the module messages and
this variance target are used in the iterative receiver.

## 04_generative_priors

Learning Channel and Activity Denoisers with Score-Based Generative Priors
 

The GPJD module requires conditional channel moments and an activity
density ratio. Following score-based learning of channel priors
 , we train a covariance-conditioned channel
denoiser from Gaussian-perturbed samples. Its output approximates the
conditional mean, and its derivatives provide the variance estimate.
A binary classifier trained with the frozen denoiser supplies the
log-density-ratio estimate used for activity detection. We first derive these
learning objectives and their relation to the GPJD updates, and then
describe the offline training of the two networks.

Channel Denoising with Colored Gaussian Noise

For an active channel , let
 concatenate the real and
imaginary parts of . Adding an independent proper complex
Gaussian perturbation with covariance gives the real
observation
 
At fixed , denote the density of by
 . Tweedie's formula expresses the
conditional mean through the score of this perturbed density
 :
 
We parameterize the mean by and train it
using the covariance-weighted denoising loss
 
The expectation is over clean channels, training covariances, and
Gaussian perturbations. For each fixed , the unrestricted
population minimizer is ;
the trained network approximates this conditional mean.
With , this loss is
a covariance-weighted form of denoising score matching
 , with Gaussian perturbation score
 as its target.
Conditioning on supplies the noise statistics for denoising
 .

To control the input and output scales across noise levels, we
extend the scalar input, skip, and output preconditioning in
 to the covariance matrix:
 
Here is the nominal variance per real
coordinate in the normalized channel units, and is the
covariance-conditioned network. Reshaping the real and imaginary
outputs of gives the complex channel-mean map
 , evaluated at in GPJD.

Variance from Conditional-Mean Derivatives
 

The conditional mean also determines the conditional covariance under
the Gaussian perturbation model. Let
 and let
 
denote the output-by-input Jacobian. At fixed , the covariance
identity in gives
 
Here is the average conditional variance per complex
coordinate: the trace sums the real and imaginary variances, while
 counts the complex coordinates. For , it reduces to
 .
Replacing the exact conditional mean by yields a variance
approximation from the trained mean network.

To evaluate the trace without forming the full Jacobian, we adapt
the Monte Carlo divergence method in 
using covariance-scaled random sign directions and centered finite
differences. Draw independent random sign vectors 
with and set
 . Their second moment
is , giving the trace approximation
 
Both perturbed evaluations hold fixed and use the complete mean
map in , including its skip and
preconditioning terms.

The per-terminal variance estimates are pooled as in
 for the GPJD update. Thus, the same
trained network supplies both channel statistics without an
additional variance network. The finite-difference settings are
given in Appendix .

Density Ratio Estimation
 

GPJD requires the density ratio to estimate
activity probabilities. We learn this ratio through binary
classification . Let be the training
activity label, with denoting an active terminal and
 . For a sampled variance , an active
query is formed as , with , whereas an
inactive query is . In both cases,
 , independently of , and
 follows the same sampling law for both classes. The resulting
conditional query densities are those in
 .

The classifier receives , , and the channel estimate
 , and is trained with the binary cross-entropy
loss
 
The channel network remains fixed during classifier training, so
its output is a deterministic feature of the query and variance.
At the population optimum over unrestricted logits, the logistic
loss recovers the training posterior log odds. Under this sampling
model, Bayes' rule gives
 
The trained classifier approximates this ideal logit. Subtracting
 therefore provides an estimate of the log
density ratio . Adding the access prior
log odds and applying the sigmoid function yields the
GPJD activity estimate in .

Offline Training

We generate clean channel tensors before activity masking and use
disjoint physical scenes for training and validation. To construct
channel-denoising samples, we draw uniformly from
 and perturb each tensor with Gaussian
noise of covariance 
in antenna--output--input order. The covariance factors and their
sampling law are specified in .
The real and imaginary antenna maps form input channels over
the DAFT coordinates. We use a conditional RefineNet
backbone with base channels,
conditioned on and the covariance factors, to implement the
mean map in .

After training the channel network, we fix its weights and train
the activity classifier from random initialization using
 . The classifier combines normalized
real and imaginary maps of and with scalar
variance, energy, and inner-product features to produce one logit
per terminal; the input transformations are specified in
Appendix .

Both networks remain fixed during receiver iterations. Their
inputs describe a single terminal at fixed and , so the
same weights are used for different numbers of terminals 
and pilot frames . Dataset sizes and optimization settings
are given in Section .

## 05_overall_algorithm

Overall Algorithm
 

This section combines the MFLE and GPJD updates in
Section with the trained denoisers in
Section . We first specify the online procedure
and then analyze its computational cost.

Overall Algorithm
 
 
 

Before the iterations, we form in
 from the available inter-frame phases.
When needed, these phases are estimated by the dominant-path fit
with variable projection in Appendix 
 . The physical noise variance 
is estimated from the trailing eigenvalues of the received spatial
covariance using the minimum description length criterion
 ; see .
Both estimates remain fixed within the transmission block.

The receiver uses the same fixed normalization as the training
channels. Let be the root mean square of the training-channel
coefficients. Divide by and
the physical noise variance by , leaving the pilot matrix
unchanged. The distribution and all message updates
use these normalized coordinates, with the same symbols retained.
Initialize and
 , where is the
training average of in normalized units. Set the
initial sites to , , and the variance ratio to
 .

At iteration , MFLE produces the extrinsic message
 . We damp the exchanged
means and variances, as in , using
new-message weight . Let 
denote the reshaped linear message for device . For ,
the damped mean and variance are
 
GPJD applies the updates in Section using
 , where scales
the damped linear variance. This input variance remains fixed
throughout the current module update. When lies outside the
training interval , the sites are retained
and the activity evidence is computed from the corresponding
Gaussian densities:
 
After computing the joint moments, we evaluate
 from and update
the variance scale for the next iteration:
 
The same weight is used for this scale update and message
damping. GPJD forms the outgoing extrinsic message using the
current in . For ,
the feedback is damped before returning to MFLE:
 
The first input and feedback messages are used without damping.
Algorithm 1 summarizes the complete procedure.

 

After at least iterations, the receiver stops when the
channel and variance estimates, accepted site updates, and activity
decisions remain stable over the prescribed windows. Otherwise,
it returns the last iterate at . The detailed checks
and their settings are given in Appendix .

Computational Complexity Analysis

Using standard dense matrix arithmetic, the MFLE module computes
a thin SVD of once
per transmission block and reuses it throughout the iterations.
For , this preprocessing costs .
Noise estimation from the spatial sample covariance and its
eigenvalues requires operations. When phase
estimation is needed, let denote the cost of the
coarse search, local path refinement, and gain refits in
Appendix .

The MFLE transforms cost per iteration.
Spatial transformations and covariance products contribute
 , while the matrix factorizations in the
linear and extrinsic updates contribute .
Let and denote the costs of one forward pass
for a single terminal through the mean network and activity
classifier, respectively. Within the training interval, GPJD uses
 mean-network passes and one classifier pass per terminal,
giving the per-iteration bound
 
For iterations, the total online complexity is bounded by
 
For supplied phases, . Excluding trained
parameters and network activations, the pilot/SVD factors,
channel messages, and spatial covariance matrices require
 working storage.

## 06_simulation_results

Simulation Results
 

We first examine the channel structure captured by the learned denoiser,
then evaluate its use in joint activity detection and channel estimation.
The receiver comparisons address estimation accuracy, pilot requirements,
access load, and transfer across channel profiles.

Simulation Settings
 

We consider the satellite uplink in Section with the
parameters in Table . Terminal locations
are sampled uniformly over the beam footprint. The propagation delays,
Doppler shifts, and array responses are determined by the same satellite
and terminal geometry. Large-scale propagation effects are compensated.
The channel follows the NTN-TDL-D power delay profile , with the delay
spread drawn uniformly from ns. The line-of-sight component has
a uniformly distributed phase and fixed amplitude, while the diffuse
path gains are proper complex Gaussian. The path parameters remain fixed over each
transmission block. Unless otherwise stated, the access configuration uses
 , , and .

For , the pilots are constructed from distinct rows and
permuted columns of a -point discrete Fourier transform (DFT)
matrix. Let be the selected row indices,
let be a permutation of ,
and let be independent uniform phases on .
The pilot symbols satisfy
 
where is the pilot energy of each terminal in each frame.

Terminal activities are generated independently with nominal
probability , conditioned on at least one active terminal.
The resulting marginal probability is
 . The receiver uses this marginal in its
independent Bernoulli prior approximation.
For the clean received signal ,
the signal-to-noise ratio (SNR) specifies the noise variance as
 

 

Channel Samples and Training
The training and validation sets contain and 
clean channel tensors of size , respectively.
Four candidate channels are sampled from each physical scene before
activity masking, and the two sets use disjoint scenes. All channels
use the same fixed training normalization.
The first-order network uses Adam with a batch size of , an
initial learning rate of , and an exponential moving average
with decay . Training lasts epochs, with the checkpoint
selected by the minimum fixed-noise validation loss. The white-noise
reference uses the same channel bank and epoch budget.

For colored-noise training, the perturbation is proper complex Gaussian
with covariance in
antenna--output--input tensor order. The variance is sampled uniformly
on a logarithmic scale over . The two covariance factors
are sampled independently as
 
where has independent entries
and is uniform on . Thus, each factor has trace ,
while its eigenvectors and eigenvalues vary across samples. The
covariance-conditioned network is trained with a covariance-weighted
denoising loss. With this network frozen,
the activity classifier is trained from random initialization using
balanced binary cross-entropy, batch size , initial learning rate
 , and epochs, with the checkpoint selected by validation.
Its training queries use and the frozen conditional-mean features.
The receiver evaluations also use this scalar query covariance.
The normalization scale and selected checkpoints are given in
Appendix .

Compared Receivers
We compare GP-CCD-MP-DRE with STMP and four sparse-recovery baselines:
simultaneous orthogonal matching pursuit (SOMP)
 , generalized approximate message
passing based sparse Bayesian learning (GAMP-SBL)
 , GNN-ASPL , and off-grid
SBL . SOMP, GAMP-SBL, and GNN-ASPL use an
integer delay--Doppler dictionary; off-grid SBL additionally estimates
continuous offsets through a first-order atom approximation. Their
AFDM and multiantenna adaptations, trained weights, and activity
readout rules are fixed throughout the reported comparisons.
SOMP selects at most atoms, GAMP-SBL allows iterations,
GNN-ASPL uses layers, and off-grid SBL uses iterations.

All receiver comparisons use known inter-frame phases and
observation-based noise estimates, with SNR defined by
 . STMP and GP-CCD-MP-DRE use activity threshold , a minimum
of and a maximum of iterations, and relative-change tolerance
 together with activity and message-stability checks.
The default new-message weights are and , respectively.
Numerical derivative and stopping parameters are given in
Appendix .

The SNR and pilot-frame comparisons use and physical
scenes per point, respectively, with scenes reused across conditions.
The user-count, activity-probability, and cross-channel comparisons each
use paired physical scenes per point.

Evaluation Metrics
For channel estimation, we report the normalized mean-squared error
(NMSE) by pooling error and channel energies over the evaluated scenes:
 
where . Errors on inactive terminals are
included. For direct channel denoising, is replaced by and
the sums run over the individual channel samples. The activity error
rate (AER) is
 
where and count missed detections and false
alarms, respectively. AER is reported for the SNR and pilot-frame comparisons.

Channel Denoising Performance
 

We first evaluate the channel mean independently of activity detection
and receiver iterations, following the separate denoising evaluation
in . The direct observation is with
 and known . The nominal denoising
SNR is in the fixed training coordinates. At each of
six SNR values from to dB, we use physical scenes with
four channels per scene, giving channel samples. The two
neural estimators receive identical channels and noise realizations.
The labels AWGN and colored distinguish their training perturbations;
the test noise is white in both cases.

The reference estimators are least squares (LS), which returns ;
the Gaussian-prior estimate , where
 is the mean element power of the normalized training
channels; and a genie-aided conditional MMSE reference. The genie is
given the true path geometry, path powers, and line-of-sight complex
gain, and its curve reports the analytic conditional MSE of the
remaining Gaussian path gains. The four sparse-recovery kernels are
also evaluated with an identity observation operator and known AWGN
variance, retaining their receiver settings and GNN weights;
GAMP-SBL retains its internal noise update.

 

Figure highlights the value of channel structure
beyond average coefficient power. The Gaussian-prior estimator rescales
all coefficients by a common factor, whereas the neural
estimators process the full channel tensor. At dB, the colored-trained
estimator attains dB NMSE, compared with dB for the
Gaussian-prior estimator. Both learned estimators also improve at high SNR,
while the sparse-recovery curves flatten under their adopted models and
settings. This behavior is consistent with residual approximation error
from the fixed dictionary and first-order offset model: reducing
observation noise alone does not remove these representation constraints.

The comparison between the two neural estimators reveals a tradeoff
across noise levels. Colored training gives a dB advantage at
 dB, while white-noise training performs better at high SNR.
The benefit of the modified denoiser is thus concentrated
at high input uncertainty, which motivates examining the receiver under
limited pilots and heavier access loads. The genie retains a substantial
advantage and has additional path information unavailable to either
learned estimator.

JADCE Performance
 

Convergence Behavior
Figure compares the iteration trajectories
at dB for one scene with five active terminals.

 

Both trajectories initially increase in NMSE before entering a sustained
error-reduction phase. The approximate extrinsic updates do not enforce
a decrease in channel NMSE at each iteration. GP-CCD-MP-DRE approaches
its final accuracy by approximately iterations, while STMP continues
to improve over a longer interval. Their final NMSEs are and
 dB, respectively. Thus, in this scene, the proposed receiver
reaches a lower error level earlier.

Effect of SNR
Figure compares channel NMSE and AER over
 to dB.

 

The NMSE curves exhibit two distinct trends. GP-CCD-MP-DRE and STMP
continue to benefit from increasing SNR, while the improvements of the
sparse-recovery baselines become smaller, widening the proposed
receiver's advantage over off-grid SBL. Together with the direct denoising
results, this separation
suggests that the retained sparse representations limit the benefit of
more accurate observations. In contrast, the gain over STMP narrows from
 dB at dB to dB at dB. Both receivers use learned
channel priors; the additional benefit of the proposed receiver is most
visible when the observations leave greater uncertainty about the channel.

Channel estimation and activity detection are coupled through
the joint moments in : the activity probability weights
the conditional channel estimate, and the resulting estimate is fed back
through MFLE. At dB, the proposed receiver reduces STMP's AER by about
 , mainly through fewer missed active terminals. At dB,
off-grid SBL has slightly lower AER but substantially higher NMSE:
correct activity decisions alone do not ensure accurate channel estimates.

Effect of Pilot-Frame Count
Figure investigates the effect of pilot-frame
count at dB, with and .

 

Increasing provides more measurements of the same effective channel
at fixed per-frame pilot energy. The gain over STMP decreases from
 dB at to dB at , indicating that the proposed
receiver is most useful when the pilot observations provide weaker
constraints. This advantage translates into a lower pilot requirement:
on the evaluated grid, reaching dB NMSE requires frames with
GP-CCD-MP-DRE and with STMP, a reduction. At , the two
methods attain the same AER while a channel-NMSE gap remains. Once most
activity errors have been removed, the accuracy of the estimated channel
coefficients still distinguishes the receivers.

Effect of User Count
Figure compares GP-CCD-MP-DRE, STMP, and the four baselines for
 -- at dB, with and .

 

At fixed , increasing enlarges both the set of candidate channels
and the expected active population. Each column of the observation model
still provides only measurements, while the number of candidate
coefficients grows as . At the fixed aggregate SNR in ,
the typical per-terminal SNR also decreases as more terminals become active.
The resulting increase in estimation difficulty is visible in all six
curves, even though the nominal activity probability is unchanged.
GP-CCD-MP-DRE retains the lowest NMSE, with a widening advantage
over STMP. For a target NMSE of
 dB, the largest tested candidate populations meeting the target are
 and for GP-CCD-MP-DRE and STMP, respectively. At , the
proposed receiver also retains a dB advantage over off-grid SBL.
Thus, with the same number of pilot frames, the evaluated configuration accommodates
a larger candidate population at a prescribed estimation accuracy.

Effect of Activity Probability
Figure compares GP-CCD-MP-DRE, STMP, and the four
baselines for nominal activity probabilities from to ,
with , , and an SNR of dB.

 

With fixed, this experiment keeps the candidate-channel dimension
unchanged and increases the fraction of active blocks. More channel
coefficients must be recovered from the same pilot and antenna resources,
with less activity sparsity available to constrain the solution. The
increasing NMSE is consistent with this reduced sparsity and the greater
load at fixed aggregate SNR. The proposed receiver
remains the most accurate, and its NMSE advantage over STMP grows from
 dB at to dB at . At the latter point,
off-grid SBL slightly surpasses STMP, while GP-CCD-MP-DRE still has a
 dB advantage over off-grid SBL. Together with the user-count
experiment, these results show that the receiver retains its advantage
both as the candidate population expands and as simultaneous access
becomes denser within a fixed population.

Comparison Across Channel Models
The preceding comparisons use profile D, which also supplies the
training channels. Figure examines whether the fixed
receivers retain their accuracy when the power-delay and fading profiles
change to A, B, and C, without retraining. Geometry and the receiver
settings remain fixed across profiles; each of the channel--SNR
conditions uses paired scenes. This comparison tests transfer of
the learned channel structure beyond the training profile.

 

GP-CCD-MP-DRE remains substantially more accurate than the four
sparse-recovery baselines on every evaluated profile. Its advantage over
STMP, however, depends on the profile and SNR. At dB, the gains range
from to dB across the four profiles. The proposed receiver
remains better on D and C throughout the SNR range, but the curves cross
on A and B as noise decreases. On B they nearly coincide at dB;
at dB, STMP is better by and dB on A and B,
respectively. Thus, the fixed learned prior remains useful beyond the
training profile, while the high-SNR ordering of the two learned
receivers is profile-dependent.