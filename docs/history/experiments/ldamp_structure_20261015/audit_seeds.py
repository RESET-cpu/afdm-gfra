"""Check new reserved seeds against bound previous cohorts and test scenes."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];F=ROOT/'results/ldamp_structure_20261015'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    plan=json.loads((F/'PLAN.json').read_text());target=plan['reserved_new_test_seeds']
    source=ROOT/'results/ldamp_complete_20261015/COMPARISON_SEED_AUDIT.json';prior=json.loads(source.read_text())
    assert prior['status']=='PASS_SEED_SEPARATION'
    for path,digest in prior['source_sha256'].items():
        assert sha(ROOT/path)==digest,path
    checks=[]
    for record in prior['checks']:
        # Outside the enclosing interval proves disjointness without assuming
        # the original cohort contained every seed in that interval.
        outside=all(not record['minimum']<=s<=record['maximum'] for s in target)
        checks.append(dict(source=record['source'],minimum=record['minimum'],maximum=record['maximum'],passed=outside))
        assert outside,record['source']
    assert not set(target)&set(prior['evaluation_seeds'])
    assert not set(target)&set(plan['allowed_development_seeds'])
    report=dict(status='PASS',new_seeds=target,checks=checks,previous_test_disjoint=True,development_disjoint=True,
        prior_audit_sha256=sha(source),bound_sources=prior['source_sha256'],script_sha256=sha(Path(__file__)),
        limitation='Uses verified seed-cohort enclosing intervals; two previously missing historical configuration references remain missing and are not claimed verified.')
    (F/'SEED_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='PASS',cohorts=len(checks),new_scenes=len(target))))
if __name__=='__main__':main()
