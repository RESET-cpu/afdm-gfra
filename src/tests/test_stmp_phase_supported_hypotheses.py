from copy import deepcopy
from scipy.special import logit
from algorithm.STMP.phase_supported_hypotheses import select_activity_hypothesis


def row(user,before,after):
    def candidate(p,slope):
        return dict(probability=p,log_bayes_factor=float(logit(p)-logit(.1)),slope=slope,supported=True)
    return dict(user=user,status='COMPLETE',candidates=[candidate(before,0.),candidate(after,1.)])


def test_inactive_alternatives_do_not_displace_gaussian_phase_refinement():
    # Cases include the observed weak alternative and a much larger change
    # that nevertheless leaves the inactive branch more probable.
    result=dict(users=[row(23,.000128,.002354),row(0,.0083,.3288)])
    before=deepcopy(result)
    assert select_activity_hypothesis(result,.1,.001,.5) is None
    assert result==before


def test_currently_missed_user_is_still_searched_and_can_recover():
    result=dict(users=[row(18,.000030,.999999),row(2,.001,.02),row(9,.6,.8)])
    chosen=select_activity_hypothesis(result,.1,.001,.5)
    assert chosen['user']==18 and chosen['before_probability']<.5 and chosen['after_probability']>.5


def test_already_confident_user_does_not_force_indefinite_phase_search():
    assert select_activity_hypothesis(dict(users=[row(2,.9998,.9999)]),.1,.001,.5) is None
