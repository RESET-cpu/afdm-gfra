## Introduction

Low Earth orbit (LEO) satellites extend Internet-of-Things (IoT)
services to remote areas, where grant-free random access (GFRA) can
reduce signaling overhead by allowing active devices to transmit
without first obtaining a grant. Since device activities are unknown
and limited pilot resources preclude mutually orthogonal pilots,
the receiver must perform joint activity detection and channel
estimation (JADCE) , which is further complicated by
large propagation delays and Doppler shifts in LEO links.

The new radio non-terrestrial network (NR-NTN) framework in Release 17
of the 3rd Generation Partnership Project (3GPP) uses position information
from a global navigation satellite system (GNSS) receiver, satellite
ephemeris, and a broadcast common timing advance for uplink delay and
Doppler pre-compensation . To support devices without
GNSS receivers or access to GNSS services, Release 19 includes a study
of GNSS-independent operation . Handling differential
delays and Doppler shifts at the satellite reduces the GNSS hardware
and pre-compensation burden on IoT devices, but these offsets can
exceed one symbol duration and one subcarrier spacing, respectively.
Consequently, terrestrial orthogonal frequency division multiplexing
(OFDM)-based GFRA schemes designed for small offsets and block-fading
channels cannot be directly applied.

Waveforms for doubly selective channels offer a starting point:
orthogonal time-frequency space (OTFS) modulation exploits diversity
through a delay--Doppler representation , whereas
affine frequency division multiplexing (AFDM) uses a one-dimensional
discrete affine Fourier transform (DAFT) whose chirp parameters can
separate multipath components. Requiring only an inverse fast Fourier
transform and chirp multiplications, AFDM is suitable for terminals
with limited computational resources . The multi-frame
OTFS scheme in  collects additional observations of a
shared channel; applying this principle to AFDM requires an input--output
relationship that retains the prefix phase under long delays and
the effects of fractional delay and Doppler.

Beyond the waveform, JADCE requires a channel model suited to limited
pilot observations. Compressed sensing methods exploit sparse user
activity and channel structure, as in the joint activity and virtual
angular-domain sparsity model for massive multiple-input multiple-output
(MIMO) JADCE in . For LEO AFDM access, a graph neural
network refines a sparse delay--Doppler prior in .
When physical delays and Doppler shifts fall between grid points,
however, each path spreads over several coefficients. A finer grid
increases the dictionary size, while estimating continuous offsets
introduces additional unknowns coupled with the path gains.

Score-based generative models learn the channel distribution from
samples . By learning the score directly on AFDM
effective channels that include fractional delay and Doppler effects,
 represents these effects without prescribing a
sparsity pattern. In multiuser GFRA, such a score-based generative
channel prior must be combined with the activity prior to recover
channels and identify active users from their superimposed signals.

In , a turbo message-passing (MP) receiver for MIMO-OFDM
JADCE combines linear estimation, score-based channel denoising, and
an activity update without online reverse diffusion sampling. The
equivalent Gaussian observation used for denoising is an approximation
whose accuracy depends on the sensing matrix and system dimensions
. We therefore train the channel denoiser with
covariance-conditioned colored Gaussian noise, while retaining the
iterative MP receiver.

Training with colored Gaussian noise conditions the denoiser on
the perturbation covariance . Since the activity
probability weights the conditional channel mean , both
estimates determine the observation residual and the message returned
to the linear estimator. An inaccurate activity probability can thus
distort interference estimation even when the conditional channel
estimate is accurate, motivating training of the activity classifier
using conditional-mean features from the pretrained denoiser.

In this paper, we investigate GNSS-independent GFRA in multiuser
MIMO-AFDM satellite IoT systems, for which we develop a multi-frame
AFDM transmission scheme and an MP receiver with a score-based
generative channel prior trained using colored Gaussian noise.
The main contributions are summarized as follows.
enumerate[label=*)]
 We propose a multi-frame AFDM transmission scheme and derive its
input--output relationship, retaining the prefix phase for delays beyond
the useful symbol interval and including fractional delay and Doppler
in the channel operator. Under the blockwise channel model, separating
the inter-frame phase yields a multiple measurement vector (MMV) model
with one shared effective channel, so that additional pilot frames
increase observations without increasing the channel dimension.

 We learn a score-based generative channel prior on the multiantenna
AFDM effective channel for JADCE, using samples generated with
continuous delays and Doppler shifts to account for off-grid effects.
The denoiser jointly processes each user's complete channel tensor,
exploiting dependence across DAFT input and output coordinates and
receive antennas to estimate the channel under the active hypothesis.

 We develop an MP receiver from the factorized posterior,
combining linear estimation with channel and activity denoising through
Gaussian extrinsic messages. The channel denoiser is pretrained using
colored Gaussian perturbations, and the activity classifier is trained
using the resulting conditional-mean features. The implemented receiver,
denoted C-STMP, uses the scalar query covariance .
enumerate

We also analyze the computational complexity of the complete receiver,
including phase and noise estimation.

Section  presents the system model.
Sections -- develop the receiver,
its training procedure, and complexity analysis. Sections VI and VII
present numerical results and conclusions, respectively.

## System Model

We consider a grant-free uplink from  single-antenna terminals to a
LEO satellite with a uniform planar array (UPA) of  elements.
Each access block contains  AFDM pilot frames with  useful samples
per frame, over which activities, channel geometry, and path coefficients
are held fixed. With common block timing and compensation of a reference
delay , differential delays and Doppler shifts are handled at
the satellite without user-specific pre-compensation .
The receiver estimates activities, channels, inter-frame phases, and
noise power from the superimposed pilots.

Let  denote terminal activity. Independent
activations with probability  are conditioned on at least one
transmission, giving the marginal  supplied to
the receiver.

## Terrestrial-Satellite Link Model

The propagation geometry is specified by the satellite position
, its velocity , and the position
 of terminal .
With carrier frequency  and propagation speed , define

With the convention ,
a path contributes  up to its gain,
giving the Doppler factor  in .
We retain this carrier phase variation while holding envelope delays
and array directions fixed over the block.

After compensation of the common reference delay , the residual
delay of path  is given by

where  is the propagation time to the closest ground point in the
beam footprint, and  is the excess
multipath delay. We adopt a common spatial response and a common Doppler
shift for the paths of each terminal
, while the path gains and excess delays remain
path-dependent. This common Doppler allows the phase evolution across
frames to be separated from the sum of the path contributions.

Let  and
, where  and
 are the array axes. For element position
, the array response is

where , , and .
The unknown array response is included in the channel to be estimated.

## Transmission Scheme

Each active terminal sends known pilots that vary across the 
frames, providing measurements of a shared channel after the
inter-frame phase is separated from the single-frame operator.
Let  be the sampling interval, where 
denotes the subcarrier spacing. The DAFT matrix is 

For pilot vector  with ,
the useful time samples are
.
A chirp-periodic prefix (CPP) of length  extends these samples as

where .
We choose  and
. The frame duration is
.
The prefix covers the residual propagation delays, including delays
longer than the useful interval , so that each useful window
contains samples from the corresponding transmitted frame.

Fractional delay is retained in constructing the AFDM effective channel
. Let  and
. We write the AFDM basis as

It agrees with the inverse DAFT at integer useful-sample times and
extends across prefix periods according to .
For delay , the delayed basis
 gives the DAFT-domain path
operator at useful-window start index  as

With , expanding this
operator gives

The last factor equals one for integer , while continuous  and
 retain fractional delay and Doppler effects in the channel
coefficients without assigning paths to delay--Doppler grid points.

For integer ,  reduces to
align
  G(d,;g)
 &= F_ A D_,g_d
   _d N F_ A^ H,
 \\
 [_d]_tt
 &=e^j2 c_1[(t-d)^2- t-d_N^2],
 
align
where .
The full delay enters the prefix phase, and its remainder determines
the cyclic shift.

At the reference frame, the channel of terminal  is given by

where  is the path gain after large-scale power compensation
and  indexes antennas, DAFT
outputs, and DAFT inputs. The common spatial response makes its
 reshaping rank at most one, which is also used for
noise estimation in Appendix .

For , pilots are formed from selected rows and permuted columns
of a -point discrete Fourier transform (DFT). With distinct row indices
, a column permutation , and independent uniform phases
, set

The common terminal Doppler introduces the phase increment
 between consecutive
frames, where  maps an angle to .
To obtain the channel in frame , its useful-window start in
 is set to
. Since
,
the channel operator satisfies

The prefix condition removes interference from adjacent frames, while
the blockwise constant gains and common Doppler preserve ,
so the frame-dependent phase can be included in the pilot operator as

The delay and within-frame Doppler effects remain in .

Let  denote the channel multiplied by its activity
indicator, so that  vanishes for an inactive terminal.
After prefix removal and DAFT demodulation, the received signal can be expressed as

with conditionally independent noise entries.
Using the indexing

the MMV model can be written as

All  measurement vectors share the activity pattern, while
increasing  adds observation rows without changing .
This requires a longer block , over which
delays, directions, gains, and Doppler shifts are approximated as
constant, with carrier phase evolution retained in
.

To assess this block approximation, as in , consider a
fixed ground terminal and a circular orbit of altitude .
Differentiating  gives
\[
 |_k| B_
 =f_cc_0(v_ sat^2h_ sat
       +v_ sat^2R_ E+h_ sat),
\]
where  and  is the
Earth radius. With fixed  and initial Doppler magnitude at
most , the delay change is bounded by
 and the phase error
from holding Doppler at its initial value by . For ,
 kHz, , and ,  ms.
Taking  km,  GHz,  km,
 km/s, and  kHz gives bounds of
s (),  Hz, and  rad for delay
and Doppler changes and the phase error, respectively. Thus additional frames
provide more observations at the cost of greater within-block
variation, with the phase-error bound growing quadratically.

For , the linear system for each measurement vector is
underdetermined, so we exploit the shared activity pattern and the
distribution of the effective-channel coefficients to estimate .
The pilot matrix also affects the linear estimator: although the
original DFT pilots have orthogonal rows, the row inner products of
 contain the user-dependent factors
, which generally remove row orthogonality.
The linear estimator therefore uses the full matrix
.

From the observations, pilots , and activity marginal , the
complete receiver estimates  and 
and constructs 
as described in Appendix .
For simulations, the signal-to-noise ratio (SNR)
is defined using the clean superposition :

The parameters  held fixed during
message updates are  for the
complete receiver and the supplied  for training.

## Problem Formulation

Let  and let  be the distribution of channel tensors
generated by  before activity masking, normalized by
the training-channel root mean square .
We divide  by  and
 by , leaving the pilot operators
unchanged; the same symbols denote normalized quantities below, and
channel outputs are rescaled by .

We retain the joint distribution of the  coefficients in each user
block and approximate the prior across users and activity states by
the product of its marginals. Conditioned on  and
, this gives the posterior

where  enforces .
Under this posterior, the minimum mean-squared error (MMSE) target
and the activity decision are given by

The threshold assigns equal costs to missed detections and false
alarms. Since the likelihood couples users through their superimposed
pilots, marginalization requires integration over all user channels
and summation over their activities. We therefore use message passing
to separate linear estimation under the observation factor from
user-level estimation under the channel and activity factors.

## Bayesian Receiver Design

We first estimate the phase increments and noise variance from the
received pilots. With these estimates fixed, the receiver uses message
passing (MP) between a linear estimator and a nonlinear denoiser.
The two modules iteratively exchange extrinsic messages . These messages are obtained
by Gaussian projection and message division . The nonlinear denoiser uses the
learned channel moments and the density ratio for activity detection. The corresponding
learning objectives are presented in Section .

## Parameter Estimation

## Inter-frame phase estimation

Stack the received samples as
, so that
.
To estimate the phase increments, we approximate the contribution of each
candidate terminal by one dominant path with an unconstrained complex
gain at each antenna.
Absorbing the common scalar phase into the gain, we define the path matrix as

The delay search is restricted to  and the Doppler search to . Under , shifting
the delay by an integer multiple of  changes the path operator by
a scalar phase, which the fitted gains absorb. With
 and gain vector
, the fitting objective is

When updating terminal , we fix the other contributions and define
. For a given , the
least-squares gain and the resulting objective are given by

The gains are eliminated from the separable nonlinear least-squares
problem by variable projection . Coarse correlations over
delay, within-frame Doppler, and frame phase provide initial candidates.
A phase candidate  corresponds to Doppler aliases

Candidates are ranked using the pilot response vector in
, which enforces the same Doppler within and across
frames. The selected candidates undergo bounded local refinement by
L-BFGS-B , with delay restricted to one differentiable
branch of the wrapped waveform. Each coordinate update is accepted
when it does not increase the residual energy, up to numerical tolerance.
After each sweep, all antenna gains are refitted jointly by least squares.

The receiver uses a fixed number of complete sweeps, retaining the previous
position as an additional refinement starting point after the first sweep.
It sets  and constructs
 by .
This local fit provides phase estimates for all candidate terminals.
The nonlinear denoiser then estimates the full channel tensor in
.

## Noise variance estimation

Let  and form the spatial sample covariance

Write its eigenvalues in descending order as
; values below
 are floored at that level before
taking logarithms. For a candidate spatial signal rank , define

The Wax--Kailath minimum description length (MDL) criterion, as reviewed
in , gives

Under a lower-rank spatial signal plus white-noise model, the criterion
selects the spatial signal rank and estimates the noise variance from
the remaining eigenvalues. Both  and
 remain fixed throughout the MP iterations.

## Linear Estimation

Let the incoming Gaussian message have mean
 and covariance
 per measurement vector, where .
For , the posterior mean and covariance under
the estimated operator in  are given by
align
  X_ L
 &= X^ pri
 + A^ H
 (^2_Q+ A A^ H)^-1
 ( Y- A X^ pri),
 \\
 _ L
 &=(^-1_KN+^-2 A^ H A)^-1,
  t_ L=_ LKN.
 
align
We approximate  by , where
 is its normalized trace. Dividing the resulting Gaussian
approximation by the incoming Gaussian message gives

For , the eigenvalues in
 give , so
 is positive.

A thin singular value decomposition (SVD)
 gives

Then .
The SVD is reused throughout the block. After reshaping by
 and applying the damping in
Section , the nonlinear estimator receives
 for each terminal.

## Channel and Activity Denoising

For channel and activity denoising, we use the following additive white
Gaussian noise (AWGN) observation model
:

This model generates the training samples and approximates the
iterative receiver inputs. Before damping, the linear extrinsic mean
satisfies

The three terms represent feedback error, error in the observation
matrix due to phase estimation, and filtered thermal noise. Equation  approximates their
sum by isotropic Gaussian noise independent of the channel.

The input densities for active and inactive terminals are given by

Bayes' rule gives the local joint posterior

Hence the local activity probability is

Let  and
.
Using the laws of total expectation and covariance, we have

This activity-weighted conditional mean is the standard Bayesian
denoising construction .
Its evaluation requires channel moments and the density ratio
, supplied by the channel and activity estimators,
respectively.

We approximate these quantities using a channel mean
, a scalar conditional mean-squared error
, and an activity logit
. We average the conditional mean-squared error
estimates over the  terminals and apply a positive lower bound:

where . The resulting scalar  is used as the
variance per coordinate in the Gaussian approximation for each terminal.
The training targets
are specified in Section ; Appendix 
derives this averaging operation by fitting the Gaussian approximations.

For each terminal, retain a Gaussian approximation to the channel-prior
factor, called a site , of the form
.
For an input variance within the training range and , dividing the Gaussian approximation to the conditional posterior
by the input likelihood gives

This condition ensures positive site precision; otherwise, the previous
site is retained as described in Section .
Combining the Gaussian site with the current input, the conditional
variance and mean are respectively given by

For an accepted update,  and .
If the update is rejected, these quantities instead combine the retained
site with the current input.

Within the training variance range, the activity probability is

where  is the training class prior,
, and .
Section  derives this prior correction.
The resulting local posterior approximation can be expressed as

Let  be obtained by reshaping
 with one row per antenna. Averaging the covariance across its  columns gives

The first term represents conditional channel uncertainty; the second
accounts for uncertainty in terminal activity.

## Extrinsic Message Update

Averaging the traces of  over terminals and dividing
by the number of antennas gives the scalar variance used for feedback:

Let ,
with . Dividing the Gaussian with mean
 and variance  by the incoming Gaussian message gives

Clipping bounds the variance ratio and keeps the outgoing precision
positive. When clipping is inactive, .
The damped outgoing parameters become the next linear prior.

## Learning Channel and Activity Denoisers with Score-Based Generative Priors

The channel prior is learned through the scores of its
Gaussian-perturbed distributions .
Following , we train two score networks to
estimate the conditional channel moments. We also train a classifier
to estimate the density ratio for activity detection in .
The training samples are generated according to the Gaussian
observation model in .

## First-Order Denoising Score Matching

For an active terminal, let
 and define
 similarly. The real noise variance is
, so that
,
with .
Let  denote the smooth positive density obtained
by Gaussian perturbation.
Assuming finite moments, the conditional mean is given by Tweedie's formula

We parameterize the score by 
and minimize the denoising score matching objective

At each positive noise level, its unrestricted population minimizer is
.
The corresponding complex channel estimate is given by

where the two score components are reshaped to .
The channel mean estimate in  is thus obtained by a single network evaluation.

## Second-Order Denoising Score Matching

Using the second-order form of Tweedie's formula, the conditional covariance
can be expressed as

To estimate the scalar error required by the receiver, we adopt the
trace objective for second-order denoising score matching
.
For a network , define

Fix  and let
.
We train the second network by minimizing
align
  L_2()
 &=\\*
 &=.
 
align
The average over coordinates is taken before squaring. The scalar
output in  estimates the conditional mean-squared
error of the channel estimator. Averaging these estimates over
terminals and applying the lower bound in 
gives , the variance per coordinate used in the Gaussian
approximation for each terminal in .
Appendix  derives the learning target
and the Gaussian fitting objective that yields this average.

## Density Ratio Estimation

The activity posterior in  depends on
. We learn this ratio from active-channel and noise-only
samples using the relationship between density ratios and class
probabilities .
Both classes use the same sampling law for , and the training class
prior is .
For label , we minimize the binary cross-entropy (BCE) loss

The mean network remains fixed during this training.

Let .
The derivative of the conditional BCE risk with respect to the logit is
, with strictly positive second derivative.
Applying Bayes' rule, the optimal logit is given by

The sampling density of  is identical for both classes and cancels
in these odds.
Since the classifier observes , the deterministic feature
 does not change the optimal logit.
Subtracting  and adding  yields the receiver
probability in . For fixed class-conditional
input distributions, the same classifier thus accommodates a different
access marginal through the prior-odds correction.

## Offline Training

Training channels are drawn before activity masking, and training and
validation sets use disjoint physical scenes.
For the channel networks, draw , sample 
uniformly over , and generate
 with .
The real and imaginary antenna maps form  input channels over
the  DAFT coordinates; the networks are conditioned on
the input noise variance. The output of  has the same shape,
while  is reduced to the scalar in .

For classifier training, active and inactive samples at a sampled
variance are  and , with independent Gaussian
noises. The classifier receives the real and imaginary maps of
 and , scaled by , together with

where  is a fixed conditioning scale,
, ,
, and
.
The feature maps have  channels, and the classifier returns one
logit per terminal.

We first train  using .
We then freeze it and train  and  using
 and , respectively.
All networks remain fixed during online inference. They are conditioned
on the denoiser input variance , while the linear module uses the
physical noise estimate . Each network operates on a terminal's channel
input at fixed dimensions  and , allowing the same networks to
be evaluated for different  and .
Dataset sizes, network dimensions, and optimization settings are
specified in the simulation setup.

## Overall Algorithm

The receiver combines the estimators and message updates in
Section  with the trained networks in
Section . The phase
increments and noise variance are estimated once per access block,
followed by MP iterations between linear estimation and channel and
activity denoising.

## Message Scheduling

From the original received pilots, estimate  by
, fit the inter-frame phase increments using
, and form
. Normalize the observation and estimated noise variance
by  and , respectively. Initialize
 and
, where  is the training
average of  in normalized units.
The initial sites are  and  in these units.
An activity history  is maintained for the stopping
check in Section .

At each iteration, the linear estimator produces a Gaussian extrinsic message
using --.
For , each trained network is evaluated once
per terminal. The channel error estimates are averaged according to
, and the sites are replaced using
 if ; otherwise, the previous sites
are retained. The classifier uses the current  in
either case.

For  outside the training range, the sites are retained and the
activity probability is obtained from their Gaussian densities:

The active density is ,
obtained by integrating the Gaussian site against the Gaussian likelihood.
Its ratio to  gives the approximate activity evidence in
.

The joint estimate and feedback message are then calculated from the
conditional moments and activity probabilities. The complete procedure
is summarized in Algorithm 1.

center
minipage0.96
5pt
Algorithm 1: Joint activity detection and channel estimation
Input: received pilots , original pilot tensor ,
and activity marginal ;
trained  and fixed receiver settings.
Output: channel estimates, activity probabilities and decisions.
enumerate[leftmargin=1.8em,itemsep=2pt,topsep=4pt]
  Estimate  using .
 Fit  by the coordinate sweeps and joint gain
 refits in Section ; construct .
  Normalize  and  by  and .
 Initialize the prior, sites, activity history, and stability counters.
 Compute the thin SVD of  and hold both estimated
 observation parameters fixed.
  For , compute the linear extrinsic message using
 -- and damp it by
 .
  If  is within the training range, evaluate , , and
 ; average the conditional mean-squared error
 estimates over terminals and apply the lower bound in
 . Accept the site update
  when  and otherwise retain the sites.
 Compute  by .
  If  is outside the training range, retain the sites and compute 
 by .
  Compute  by  and
  by
 --.
  Form the outgoing message using
 --
 and apply .
  Update the stability counters and activity history.
 Stop when the criterion in Section  is satisfied.
 end for
  Return , , ,
 , and the stopping status.
 Rescale covariance outputs by .
enumerate
3pt
minipage
center

## Damping and Stopping Criteria

We apply damping to the means and variances of both the denoiser input
and the feedback message.
With new-message weight , the input update for  is

Similarly, the feedback parameters are updated as

The first updates are used without damping.

The stopping rule tracks the estimate, activity probabilities, and
input variance. For , define

where  prevents division by zero.
The estimate-stability counter increases when
,
, and
, and resets otherwise.

We also check the accepted, undamped site parameters.
Let  and , and define

The site-stability counter increases only if the current site update is
accepted, , and
; it resets otherwise.
After this check, update

This history is used only for stopping; the receiver reports 
and retains the fixed prior  in .

Iteration stops after at least  iterations when both stability
counters reach  and the hard activity vector has remained unchanged
for  consecutive iterates. The two stability counters reset
independently. If the iteration limit  is reached first, the
final iterate is returned with that status. The damping weights,
tolerances, and window lengths are given in the simulation setup.

## Computational Complexity Analysis

We analyze the costs of phase estimation, noise estimation, and the
subsequent MP iterations. Let  be the number of path matrices on the coarse
delay--Doppler grid,  the number of phase bins, and  the
number of coordinate sweeps. With dense path-matrix evaluation,
precomputing these path matrices and their pilot responses costs
. Each user search forms correlations
at cost  and evaluates phase bins by fast Fourier
transforms (FFTs) at cost . An initial search
orders the users, followed by  sweeps.

Let  count all path-matrix evaluations for alias ranking and
local refinement across the block, including derivative evaluations
up to a constant factor. Evaluating a path matrix, computing its pilot response,
and fitting the gain cost . For , each joint
gain refit costs . The resulting complexity of phase estimation is

The local iteration budget bounds optimizer iterations; the actual
number of objective evaluations also depends on line searches.
Noise estimation costs , and the thin SVD of
 costs  for .

In each MP iteration, the dense linear transforms on 
measurement vectors cost . The factors in
 reuse the initial SVD.

Let , , and  denote the costs of one
terminal-wise forward pass through the mean, error, and activity
networks. Within the training variance range, each iteration evaluates the
networks once per terminal and reuses  in the classifier.
Taking into account the spatial covariance products and small-matrix
operations, the computational complexity per iteration is given by

The networks are not evaluated outside the training variance range.
For  MP iterations, the complete online cost is

Excluding trained parameters and network activations, MP
requires storage of  entries. The phase estimator additionally
caches  entries for the coarse path matrices and
pilot responses, with  temporary FFT storage.

## Simulation Results

The following four figures present the current saved evaluations in the
order of denoising, convergence, SNR, and pilot-frame count. The receiver
comparisons use known inter-frame phases and observation-based noise
estimates. Unless varied, , , and ; the pilot-frame
comparison is evaluated at  dB. The direct denoising experiment uses
additive white Gaussian noise (AWGN) with known variance. In its legend,
AWGN and colored refer to the training perturbations.

The SNR and pilot-frame panels include previously inspected development
scenes, and baseline threshold development overlaps evaluation scenes;
they are retrospective paired comparisons. Finite nonconverged outputs
are retained. The convergence plot describes one scene, and iteration
counts are not measurements of runtime. Further numerical discussion
will be added as the manuscript is developed.

## Second-Order Training Objective

The second equality in  follows from
 and .

For the fixed mean estimator , minimizing over scalar
functions gives the population target

Indeed, with , conditioning
 on  gives
.
Moreover, expanding the squared error about the conditional mean gives

where .
The scalar output in  therefore learns the
conditional mean-squared error of the deployed mean estimator. This
target reduces to the posterior covariance trace per complex coordinate
when .

To derive the average in , fit Gaussian
distributions with fixed means  and covariance  for
every terminal. Giving equal weight to each terminal's channel
distribution conditioned on being active yields
the expected negative log density, up to a constant,

Its derivative is
.
The minimizer under  is the average conditional
error clipped below by .
Equation  approximates this fit with the learned
error estimates. Equal weighting concerns each terminal's distribution
conditioned on being active; activity probabilities enter later through
the mixture in .

## Phase and Noise Estimation

## Inter-frame phase estimation

Stack the received samples as
, so that
.
To estimate the phase increments, we approximate the contribution of each
candidate terminal by one dominant path with an unconstrained complex
gain at each antenna.
Absorbing the common scalar phase into the gain, we define the path matrix as

The delay search is restricted to  and the Doppler search to . Under , shifting
the delay by an integer multiple of  changes the path operator by
a scalar phase, which the fitted gains absorb. With
 and gain vector
, the fitting objective is

When updating terminal , we fix the other contributions and define
. For a given , the
least-squares gain and the resulting objective are given by

The gains are eliminated from the separable nonlinear least-squares
problem by variable projection . Coarse correlations over
delay, within-frame Doppler, and frame phase provide initial candidates.
A phase candidate  corresponds to Doppler aliases

Candidates are ranked using the pilot response vector in
, which enforces the same Doppler within and across
frames. The selected candidates undergo bounded local refinement by
L-BFGS-B , with delay restricted to one differentiable
branch of the wrapped waveform. Each coordinate update is accepted
when it does not increase the residual energy, up to numerical tolerance.
After each sweep, all antenna gains are refitted jointly by least squares.

The receiver uses a fixed number of complete sweeps, retaining the previous
position as an additional refinement starting point after the first sweep.
It sets  and constructs
 by .
This local fit provides phase estimates for all candidate terminals.
The nonlinear denoiser then estimates the full channel tensor in
.

## Noise variance estimation

Let  and form the spatial sample covariance

Write its eigenvalues in descending order as
; values below
 are floored at that level before
taking logarithms. For a candidate spatial signal rank , define

The Wax--Kailath minimum description length (MDL) criterion, as reviewed
in , gives

Under a lower-rank spatial signal plus white-noise model, the criterion
selects the spatial signal rank and estimates the noise variance from
the remaining eigenvalues. Both  and
 remain fixed throughout the MP iterations.