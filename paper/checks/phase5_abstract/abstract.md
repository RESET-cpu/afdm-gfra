# Abstract

This paper investigates joint activity detection and channel estimation
(JADCE) for grant-free random access in low Earth orbit satellite
Internet-of-Things systems without global navigation satellite system
(GNSS) assistance. Large differential delays and Doppler shifts
complicate the pilot observation model, while fractional offsets weaken
sparse channel representations. We propose a multi-frame affine frequency
division multiplexing (AFDM) transmission scheme and derive its
input--output relationship, which retains the prefix phase for delays
beyond the useful symbol interval and separates the Doppler-induced
phase evolution across frames, yielding multiple observations of a
shared effective channel. A score-based generative prior is then
learned from multiantenna AFDM effective-channel samples generated with
continuous delays and Doppler shifts, thereby representing off-grid
effects and dependence among channel coefficients without a prescribed
sparsity pattern. From the posterior factorization, we develop a
message-passing receiver that combines linear estimation
with channel and activity denoising. The channel denoiser is pretrained
using covariance-conditioned colored Gaussian noise, and the activity
classifier is trained using conditional-mean features from the pretrained
denoiser. The receiver combines these estimates through iterative
Gaussian message updates.