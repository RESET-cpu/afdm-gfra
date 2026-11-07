"""Train the shared GNN-ASPL network using an explicit training recipe."""

import argparse
import importlib
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "recipe", choices=("mixed", "per-snr"), help="Use RECIPE --help for that recipe's options."
    )
    tokens = sys.argv[1:] if argv is None else list(argv)
    # Parse only the recipe here so --help and all training options reach its parser.
    args = parser.parse_args(tokens[:1])
    module_name = {"mixed": "mixed", "per-snr": "per_snr"}[args.recipe]
    trainer = importlib.import_module(f".{module_name}", package=__package__)
    return trainer.main(tokens[1:])
