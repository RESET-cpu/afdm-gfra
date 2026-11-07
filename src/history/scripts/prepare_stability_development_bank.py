"""Generate one disjoint development scene across all declared user counts."""
import argparse
from threadpoolctl import threadpool_limits
import repair_stability_development as development

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene',type=int,required=True,choices=range(4))
    args=parser.parse_args()
    development.prepare()
    with threadpool_limits(1):
        for users in (20,40,60,80,100):
            development.bank('development',args.scene,users)
            print('READY',args.scene,users,flush=True)
