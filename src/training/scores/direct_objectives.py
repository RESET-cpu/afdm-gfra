"""Original direct first-score DSM and frozen-first second-score trace losses."""
from training.scores.score_matching import scalar_real_variance


def direct_first_loss(score, noisy, clean, complex_variance):
    """Cai Eq.48-49, lambda_1(v)=v, normalized by real dimension."""
    v = scalar_real_variance(complex_variance)[:, None, None, None, None]
    return (v.sqrt()*score+(noisy-clean)/v.sqrt()).square().mean()


def direct_second_loss(score, frozen_first_score, noisy, clean, complex_variance):
    """Cai Eq.53-54: square AFTER the whole-sample trace, lambda_2(v)=v²."""
    v = scalar_real_variance(complex_variance)[:, None, None, None, None]
    b_scaled = v.sqrt()*frozen_first_score.detach()+(noisy-clean)/v.sqrt()
    residual = v*score-b_scaled.square()+1
    return residual.flatten(1).mean(1).square().mean()


