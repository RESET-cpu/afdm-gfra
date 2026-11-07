\section{GP-CCD-MP-DRE Algorithm}


\subsection{Overall Algorithm}


Substituting the estimators developed in Section~
into the framework of Section~ yields
GP-CCD-MP-DRE, which
combines a generative prior (GP), covariance-conditioned denoising
(CCD), message passing (MP), and density ratio estimation (DRE).
The linear estimation in Section~
forms the multi-frame linear estimation (MFLE) module. The joint
denoising in Section~, implemented with
the learned channel and activity estimators, forms the
generative-prior-aided joint denoising (GPJD) module.

For a Gaussian input , the denoiser gives
, and the classifier gives  in
. With
 from
, we use the common conditional variance



Here  is a numerical floor.

To represent the learned channel moments in Gaussian messages,
we use a site approximation to the channel prior
, of the form
.
Dividing the Gaussian approximation with mean  and variance
 by the input likelihood gives




Combining the site with the current input then yields




We accept the update within the training variance range when
; otherwise, the previous site is retained.

Combining  with  gives the joint estimate in
 and covariance in .
The Gaussian extrinsic message in  is then
passed to MFLE.
Algorithm~1 summarizes the iteration. In normalized coordinates,
we initialize ,
, , , and
, where  is the training average
of . The parameter estimates, normalization,
and message damping are specified below.





\subsection{Parameter Estimation and Numerical Implementation}




The preceding posterior calculations use a fixed observation matrix
 and physical noise variance
. The matrix is formed from the available
inter-frame phases through ; when the
phases are unknown, they are estimated by variable projection
. For the noise variance, the spatial sample
covariance separates the signal subspace from the trailing
eigenvalues under a lower-rank spatial signal plus white noise.
The minimum description length (MDL) criterion selects the signal
rank, and the mean of the remaining eigenvalues gives
 .
Appendix~ gives both estimators. Their outputs
remain fixed throughout message passing.

The input variance  in the local model
 describes the uncertainty after linear
estimation. Its update follows from the expected Gaussian
negative log likelihood with the current approximate posterior
 held fixed .
For a candidate variance , the terms depending on it
are .
Minimizing this expression and expanding the expected squared
error gives




The residual measures the error of the posterior mean, while
 accounts for the remaining channel and activity
uncertainty. Let  denote the damped MFLE variance
and use  during iteration .
With new-message weight , the next scale is




The current  is used for both joint denoising and the
extrinsic update; the updated scale enters the following iteration.

The channel prior and online observations use the same fixed
normalization. If  is the root mean square of the training-channel
coefficients, we divide  by 
and the physical noise variance by , retaining the same symbols
for normalized quantities. The pilot matrix is unchanged.
To moderate changes between successive Gaussian messages, we apply
damping  to the MFLE output for :




For numerical evaluation of , we
replace  by
, where
. The feedback is then damped with the same weight:




The first input and feedback messages are used without damping.
Outside the training variance range, the retained Gaussian sites
provide the activity density ratio specified in
. Iteration stops when the estimates
and accepted site updates have stabilized, or at the maximum
iteration count. The corresponding checks and numerical settings
are given in Section~.

\subsection{Computational Complexity Analysis}


The observation matrix is fixed within a transmission block, so its
thin singular value decomposition (SVD),
,
can be reused across iterations. In particular,
-- become




Here .
For , the SVD costs  once per block.
Noise estimation costs ; let  denote
the phase-search, refinement, and gain-refitting cost in
Appendix~. Per iteration, MFLE transformations
cost , spatial covariance operations cost
, and matrix factorizations cost .
If  denote the per-device denoiser and classifier
costs, GPJD uses  denoiser evaluations and one classifier
evaluation within the training interval. Hence,





For  iterations, the total online complexity is bounded by




For supplied phases, .
All devices share the trained parameters.
Excluding these parameters and network activations,
the pilot/SVD factors, channel messages, and spatial covariance
matrices require  working storage.
