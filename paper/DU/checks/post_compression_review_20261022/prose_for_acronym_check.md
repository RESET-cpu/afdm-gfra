# Abstract

This paper investigates joint activity detection and channel estimation (JADCE) for grant-free random access in a low Earth orbit satellite Internet-of-Things system without global navigation satellite system (GNSS) assistance. Large differential delays and Doppler shifts complicate the pilot observation model, while fractional offsets weaken sparse channel representations. We propose a multi-frame affine frequency division multiplexing (AFDM) transmission scheme and derive its input--output relationship, which retains the prefix phase for delays beyond the useful symbol interval and separates the Doppler-induced phase evolution across frames, yielding multiple observations of a shared effective channel under integer and fractional offsets. We then learn a score-based generative channel prior from multiantenna AFDM effective-channel samples generated with continuous delays and Doppler shifts, thereby representing off-grid effects and the dependence among channel coefficients without prescribing a sparsity pattern. Using the posterior factorization, we develop a deep-unfolded message-passing (MP) receiver that combines linear estimation with channel and activity denoising. Since the activity probabilities weight the channel estimates used to form subsequent messages, errors in either estimate affect later layers, motivating joint training of the channel denoisers, activity classifiers, and message parameters from received pilots. Score pretraining initializes the channel denoisers, while progressive training adapts the complete sequence of updates to the inputs encountered at each layer.

# Main Text

## Introduction

Low Earth orbit (LEO) satellites extend Internet-of-Things (IoT) services to remote areas, where grant-free random access (GFRA) can reduce signaling overhead by allowing active devices to transmit without first obtaining a grant. Since device activities are unknown and limited pilot resources preclude mutually orthogonal pilots, the receiver must perform joint activity detection and channel estimation (JADCE) , which is further complicated by large propagation delays and Doppler shifts in LEO links.

The new radio non-terrestrial network (NR-NTN) framework in Release 17 of the 3rd Generation Partnership Project (3GPP) uses position information from a global navigation satellite system (GNSS) receiver, satellite ephemeris, and a broadcast common timing advance for uplink delay and Doppler pre-compensation . To support devices without GNSS receivers or access to GNSS services, Release 19 includes a study of GNSS-independent operation . Handling differential delays and Doppler shifts at the satellite reduces the GNSS hardware and pre-compensation burden on IoT devices, but these offsets can exceed one symbol duration and one subcarrier spacing, respectively. Consequently, terrestrial orthogonal frequency division multiplexing (OFDM)-based GFRA schemes designed for small offsets and block-fading channels cannot be directly applied.

Waveforms for doubly selective channels offer a starting point: orthogonal time-frequency space (OTFS) modulation exploits diversity through a delay--Doppler representation , whereas affine frequency division multiplexing (AFDM) uses a one-dimensional discrete affine Fourier transform (DAFT) whose chirp parameters can separate multipath components. Requiring only an inverse fast Fourier transform and chirp multiplications, AFDM is suitable for terminals with limited computational resources . The multi-frame OTFS scheme in collects additional observations of a shared channel; applying this principle to AFDM requires an input--output relationship that retains the prefix phase under long delays and the effects of fractional delay and Doppler.

Beyond the waveform, JADCE requires a channel model suited to limited pilot observations. Compressed sensing methods exploit sparse user activity and channel structure, as in the joint activity and virtual angular-domain sparsity model for massive multiple-input multiple-output (MIMO) JADCE in . For LEO AFDM access, a graph neural network refines a sparse delay--Doppler prior in . When physical delays and Doppler shifts fall between grid points, however, each path spreads over several coefficients. A finer grid increases the dictionary size, while estimating continuous offsets introduces additional unknowns coupled with the path gains.

Score-based generative models learn the channel distribution from samples . By learning the score directly on AFDM effective channels that include fractional delay and Doppler effects, represents these effects without prescribing a sparsity pattern. In multiuser GFRA, such a score-based generative channel prior must be combined with the activity prior to recover channels and identify active users from their superimposed signals.

In , a turbo message-passing (MP) receiver for MIMO-OFDM JADCE combines linear estimation, score-based channel denoising, and an activity update without online reverse diffusion sampling. The equivalent Gaussian observation used for denoising is an approximation whose accuracy depends on the sensing matrix and system dimensions . We therefore use score pretraining to learn the channel prior and receiver training to adapt the denoisers to the messages encountered during multiuser inference.

Deep unfolding converts the MP iterations into a trainable network . Since the activity probability weights the conditional channel mean , both estimates determine the observation residual and the message returned to the linear estimator. An inaccurate activity probability can thus distort interference estimation even when the conditional channel estimate is accurate, motivating joint training of the channel denoisers, activity classifiers, and message parameters from received pilots.

In this paper, we investigate GNSS-independent GFRA in multiuser MIMO-AFDM satellite IoT systems, for which we develop a multi-frame AFDM transmission scheme and a deep-unfolded MP receiver with a score-based generative channel prior. The main contributions are summarized as follows. enumerate[label= *)] We propose a multi-frame AFDM transmission scheme and derive its input--output relationship, retaining the prefix phase for delays beyond the useful symbol interval and including fractional delay and Doppler in the channel operator. Under the blockwise channel model, separating the inter-frame phase yields a multiple measurement vector (MMV) model with one shared effective channel, so that additional pilot frames increase observations without increasing the channel dimension.

We learn a score-based generative channel prior on the multiantenna AFDM effective channel for JADCE, using samples generated with continuous delays and Doppler shifts to account for off-grid effects. The denoiser jointly processes each user's complete channel tensor, exploiting dependence across DAFT input and output coordinates and receive antennas to estimate the channel under the active hypothesis.

We develop a deep-unfolded MP receiver from the factorized posterior, combining linear estimation with channel and activity denoising through Gaussian extrinsic messages. Since the two estimates jointly determine subsequent messages, we jointly optimize the denoisers, classifiers, and message parameters using channel and activity supervision. Progressive training initializes each new layer's score network from the pretrained network and jointly fine-tunes the available layers at each depth. enumerate

We also analyze the computational complexity of the complete receiver, including phase and noise estimation.

Section presents the system model. Sections -- develop the receiver, its training procedure, and complexity analysis. Sections VI and VII present numerical results and conclusions, respectively.

## System Model

We consider a grant-free uplink from single-antenna terminals to a LEO satellite with a uniform planar array (UPA) of elements. Each access block contains AFDM pilot frames with useful samples per frame, over which activities, channel geometry, and path coefficients are held fixed. With common block timing and compensation of a reference delay , differential delays and Doppler shifts are handled at the satellite without user-specific pre-compensation . The receiver estimates activities, channels, inter-frame phases, and noise power from the superimposed pilots.

Let denote terminal activity. Independent activations with probability are conditioned on at least one transmission, giving the marginal supplied to the receiver.

## Terrestrial-Satellite Link Model

The propagation geometry is specified by the satellite position , its velocity , and the position of terminal . With carrier frequency and propagation speed , define With the convention , a path contributes up to its gain, giving the Doppler factor in . We retain this carrier phase variation while holding envelope delays and array directions fixed over the block.

After compensation of the common reference delay , the residual delay of path is given by where is the propagation time to the closest ground point in the beam footprint, and is the excess multipath delay. We adopt a common spatial response and a common Doppler shift for the paths of each terminal , while the path gains and excess delays remain path-dependent. This common Doppler allows the phase evolution across frames to be separated from the sum of the path contributions.

Let and , where and are the array axes. For element position , the array response is where , , and . The unknown array response is included in the channel to be estimated.

## Transmission Scheme

Each active terminal sends known pilots that vary across the frames, providing measurements of a shared channel after the inter-frame phase is separated from the single-frame operator. Let be the sampling interval, where denotes the subcarrier spacing. The DAFT matrix is For pilot vector with , the useful time samples are . A chirp-periodic prefix (CPP) of length extends these samples as where . We choose and . The frame duration is . The prefix covers the residual propagation delays, including delays longer than the useful interval , so that each useful window contains samples from the corresponding transmitted frame.

Fractional delay is retained in constructing the AFDM effective channel . Let and . We write the AFDM basis as It agrees with the inverse DAFT at integer useful-sample times and extends across prefix periods according to . For delay , the delayed basis gives the DAFT-domain path operator at useful-window start index as With , expanding this operator gives The last factor equals one for integer , while continuous and retain fractional delay and Doppler effects in the channel coefficients without assigning paths to delay--Doppler grid points.

For integer , reduces to where . The full delay enters the prefix phase, and its remainder determines the cyclic shift.

At the reference frame, the channel of terminal is given by where is the path gain after large-scale power compensation and indexes antennas, DAFT outputs, and DAFT inputs. The common spatial response makes its reshaping rank at most one, which is also used for noise estimation in Appendix .

For , pilots are formed from selected rows and permuted columns of a -point discrete Fourier transform (DFT). With distinct row indices , a column permutation , and independent uniform phases , set The common terminal Doppler introduces the phase increment between consecutive frames, where maps an angle to . To obtain the channel in frame , its useful-window start in is set to . Since , the channel operator satisfies The prefix condition removes interference from adjacent frames, while the blockwise constant gains and common Doppler preserve , so the frame-dependent phase can be included in the pilot operator as The delay and within-frame Doppler effects remain in .

Let denote the channel multiplied by its activity indicator, so that vanishes for an inactive terminal. After prefix removal and DAFT demodulation, the received signal can be expressed as with conditionally independent noise entries. Using the indexing the MMV model can be written as All measurement vectors share the activity pattern, while increasing adds observation rows without changing . This requires a longer block , over which delays, directions, gains, and Doppler shifts are approximated as constant, with carrier phase evolution retained in .

To assess this block approximation, as in , consider a fixed ground terminal and a circular orbit of altitude . Differentiating gives where and is the Earth radius. With fixed and initial Doppler magnitude at most , the delay change is bounded by and the phase error from holding Doppler at its initial value by . For , kHz, , and , ms. Taking km, GHz, km, km/s, and kHz gives bounds of s ( ), Hz, and rad for delay and Doppler changes and the phase error, respectively. Thus additional frames provide more observations at the cost of greater within-block variation, with the phase-error bound growing quadratically.

For , the linear system for each measurement vector is underdetermined, so we exploit the shared activity pattern and the distribution of the effective-channel coefficients to estimate . The pilot matrix also affects the linear estimator: although the original DFT pilots have orthogonal rows, the row inner products of contain the user-dependent factors , which generally remove row orthogonality. The linear estimator therefore uses the full matrix .

From the observations, pilots , and activity marginal , the complete receiver estimates and and constructs as described in Appendix . For simulations, the signal-to-noise ratio (SNR) is defined using the clean superposition : The parameters held fixed during message updates are for the complete receiver and the supplied for training.

## Problem Formulation

Let and let be the distribution of channel tensors generated by before activity masking, normalized by the training-channel root mean square . We divide by and by , leaving the pilot operators unchanged; the same symbols denote normalized quantities below, and channel outputs are rescaled by .

We retain the joint distribution of the coefficients in each user block and approximate the prior across users and activity states by the product of its marginals. Conditioned on and , this gives the posterior where enforces . Under this posterior, the minimum mean-squared error (MMSE) target and the activity decision are given by The threshold assigns equal costs to missed detections and false alarms. Since the likelihood couples users through their superimposed pilots, marginalization requires integration over all user channels and summation over their activities. We therefore use message passing to separate linear estimation under the observation factor from user-level estimation under the channel and activity factors.

## Deep-Unfolded Receiver Design

From the posterior factorization in , we derive Gaussian messages linking linear estimation to channel and activity denoising, then parameterize the denoisers and message variances to obtain trainable layers.

## Factor Graph Representation

Let and , and denote column of and by and , respectively. The observation factor is while each user's factors comprise the activity prior , the channel prior , and the constraint enforcing . Figure shows their connections, with each node retaining the joint distribution of the complete channel tensor.

Following , module A groups for column-wise linear estimation, while module B groups the user constraints and priors for channel and activity denoising. Conditioned on the messages from A, the factors in B separate over users, whose blocks are obtained by . The modules exchange Gaussian extrinsic messages , denoted by and at layer . Each module combines its factors with the incoming message to form a local belief, then divides its Gaussian approximation by that message to remove the incoming contribution, following the flow in Fig. .

## Linear Estimation

At layer , the input Gaussian messages have means collected in and a common covariance for each column of . Let be column of . The input message and the belief at are Completing the square in gives the mean and average marginal variance , where Matching these moments gives a Gaussian approximation with covariance per column, whose quotient with gives the extrinsic variance and mean : Because the Gaussian quotient links the mean and variance, we adjust both when introducing the trainable scale . With , requiring the product of the incoming and outgoing messages to retain mean gives , and hence The pair is passed to module B, reducing to when .

## Channel and Activity Denoising

Rearrange into user blocks according to , and let be the vectorized block for user . The Gaussian message passed to module B is At , the constraint gives the likelihood , where we omit the user and layer indices and write and . Integrating over the channel under each activity hypothesis gives Multiplying by the activity prior and normalizing gives the joint channel and activity belief Conditioning on the active hypothesis gives the conditional channel mean The activity probability follows from Bayes' rule as Since vanishes under the inactive hypothesis, averaging over the two activity states gives Evaluating and requires integration over the -dimensional channel distribution for every user and layer, so we approximate them with a score-based denoiser and an activity classifier.

Let denote the real and imaginary parts of the denoiser input for user . Based on the score representation developed in Section , the channel estimate is Here is the score network in layer , is the noise variance per real coordinate, and controls the denoising correction.

For the classifier, rewriting in terms of posterior odds gives Representing the likelihood-ratio term by a trainable log-odds correction , the classifier uses the input and conditional channel estimate to compute where denotes the classifier parameters. Substituting the channel and activity estimates into gives The estimates form after conversion to complex form and rearrangement by . All users share the networks within a layer, with soft probabilities retained until the final activity decision.

## Extrinsic Message Update

To form the Gaussian return message, we associate with a common scalar variance, which we estimate from the observation residual. Under the fixed-parameter model, a zero-mean error with covariance per column and uncorrelated with the noise would satisfy This relation motivates the normalized residual quantity To keep the return variance positive, we map to a ratio with a trainable scale: where , , and are fixed. The softplus handles negative residual values, while keeps the output variance below , giving positive extrinsic precision. With denoting column of , the Gaussian output and return message are Evaluating this Gaussian quotient gives We damp the resulting message in its natural parameters : Here and , with denoting the average channel power per coefficient. Messages with variance above the prior value receive less weight, while averaging positive precisions preserves a positive variance. The resulting defines in , completing the layer update.

## Score Pretraining and Joint Receiver Training

We first learn the channel score from perturbed channel samples and then train the unfolded receiver on received pilots, jointly adapting the channel denoisers, activity classifiers, and message parameters.

## First-Order Score Matching

For a normalized channel sample , we form the perturbed observation , where . Denote the perturbed density, the real-coordinate form of in , by and its score by . Tweedie's formula relates this score to the conditional channel mean : Replacing by a score network gives the denoiser in , initially with , without direct integration over the channel distribution. To learn the unknown marginal score, denoising score matching uses the Gaussian perturbation score as the training target while preserving the score-matching minimizers . With variance weighting, the loss is Samples are drawn before activity masking and perturbed over a range of noise levels, with continuous delays and Doppler shifts represented in their effective-channel coefficients. The learned score supplies the conditional channel mean under the active hypothesis; activity probabilities are learned from received pilots in the next stage.

## Joint Channel and Activity Training

To adapt the pretrained denoisers to their layer inputs, each training observation passes through the updates in Section , using the sensing matrix and noise variance supplied by the physical model. The trainable parameters are , , , , and, for layers that return a message, . For a fixed distribution of denoiser inputs, expected squared error on active users and expected binary cross-entropy on all users are minimized by the conditional channel mean and activity probability, respectively , matching the two targets in .

Suppose the receiver training set contains scenes, with candidate users in scene . Let and denote the channel and activity label of user in scene . Training and validation use disjoint physical scenes. The channel and activity losses at layer are respectively given by Here and are the training set's active-channel energy and user count, which are held fixed so that scenes with different numbers of users retain the same normalization. The two normalized losses receive equal coefficients in both training and model selection.

For a receiver with layers, the joint training objective is where weights the loss at layer , including intermediate estimates used to form subsequent messages. Since the classifier takes as an input, gradients from the activity loss update the channel denoiser within the same layer. Across layers, the product determines the residual and return message, through which later channel losses update earlier activity classifiers and message parameters. Joint training thus accounts for both the current estimation errors and their effects on later layers.

## Progressive Training

Each newly added layer has independent parameters and receives the messages produced by the preceding layers. Its score network is initialized from the same pretrained network, while its log-odds correction and , , and start at zero, giving an initial activity probability of . Earlier layers retain their selected parameters.

At depth , we first train the new layer with the earlier parameters fixed, except for when , since the preceding layer's return message first contributes to the loss when layer is added. We then fine-tune all layers jointly at a reduced learning rate, with both stages minimizing . The checkpoint minimizing the validation sum , using the training normalization constants, initializes the next depth; after depth , the selected parameters are fixed for inference.

## Network Structure and Inputs

Each user's real and imaginary antenna maps form feature channels over the input and output DAFT coordinates, allowing convolutions to learn dependencies across antennas and coefficients affected by continuous delays and Doppler shifts. The score network uses conditional RefineNet , with the structure in Table . Two fully connected layers embed into 64 features, from which each conditional normalization layer obtains three coefficients per channel: a weight for the normalized channel means added to the normalized features, and a scale and shift for the result.

The classifier combines the denoiser input and conditional channel estimate into channels, scaled by , and processes them with the convolutions and pooling in Table . Its fully connected layers combine the pooled features with to produce the log-odds correction in . These energy terms describe the input, channel estimate, and residual relative to the noise level. Since both networks act on individual users with shared parameters within a layer, their input dimensions depend on and , whereas determines the number of evaluations and enters through the linear estimator.

## Overall Algorithm

## Message Scheduling

The receiver first estimates the phase increments and noise variance as described in Appendix , after which the resulting and remain fixed throughout the unfolded layers. Although the phase fit uses one dominant path per candidate terminal, the denoisers recover the full multipath channel. Table summarizes the complete receiver, where denotes the complex channel tensor obtained from and the final channel outputs are restored to their original scale.

## Computational Complexity Analysis

Since is fixed, one thin singular value decomposition (SVD), at cost with , , and , suffices to evaluate the general linear estimator in across all layers. Computing the residuals and applying the singular vectors then cost and per layer, respectively. Denoting the costs of one user's score network and activity classifier in Table by and , we obtain For the phase estimator, let be the number of coarse delay--Doppler path matrices, the number of phase bins, the number of coordinate sweeps, and the number of path-matrix evaluations for Doppler ranking and local refinement, including derivative evaluations up to a constant factor. The costs of precomputing the path responses, searching users by correlation and fast Fourier transforms (FFTs), refining the paths, and jointly refitting the gains give, for , Since phase estimation and the spatial covariance eigendecomposition for noise estimation are performed once per block, the complete online cost is For , the SVD and unfolded layers contribute , including the residual used for variance estimation. Reducing therefore saves repeated linear updates and network evaluations, while the front-end and SVD costs remain fixed. With score-network and classifier parameters per layer, the receiver stores parameter scalars; the operator, SVD, and messages require additional storage, excluding network activations and the phase-estimation cache.
