"""Explicit training commands; displaying help never starts training."""
import argparse
from importlib import import_module
import sys

MODULES = {
    'gp-mp-first': 'training.gp_mp.first',
    'gp-mp-activity': 'training.gp_mp.activity',
    'stmp': 'training.stmp.cli',
    'gnn': 'training.gnn.cli',
}


def main(argv=None):
    tokens = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('method', choices=tuple(MODULES))
    args = parser.parse_args(tokens[:1])
    return import_module(MODULES[args.method]).main(tokens[1:])
