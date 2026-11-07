"""Keep phase alternatives only when their local query supports activity.

Every user is still queried. The current activity decision does not gate
search, so a currently missed user can recover at an alternative phase.
This local classifier rule is not a joint observation-likelihood guarantee.
"""
from receiver.stmp.phase_hypotheses import select_activity_hypothesis as select_by_gain


def select_activity_hypothesis(result,activity_prior,probability_tolerance,decision_threshold):
    if not 0<decision_threshold<1:raise ValueError('Activity decision threshold must lie in(0,1)')
    supported=[]
    for row in result['users']:
        if row['status']!='COMPLETE':continue
        best=max((d for d in row['candidates'] if d['supported']),key=lambda d:d['log_bayes_factor'])
        if best['probability']>=decision_threshold:supported.append(row)
    return select_by_gain(dict(result,users=supported),activity_prior,probability_tolerance)
