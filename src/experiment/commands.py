"""Workspace entry points, with explicit dispatch for frozen experiment batches."""
import sys


def main(argv=None):
    try:
        return dispatch(argv)
    except FileNotFoundError as error:
        print(f'Missing resource: {error.filename or error}. '
              'Run "python run_experiments.py assets --scope gp-mp" for the required files; '
              'see REPRODUCING.md for installation and asset preparation.', file=sys.stderr)
        return 2


def dispatch(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == 'demo':
        from experiment.demo import main as demo
        return demo(argv[1:])
    if argv and argv[0] == 'assets':
        from experiment.assets import main as assets
        return assets(argv[1:])
    if argv and argv[0] == 'train':
        from training.cli import main as train
        return train(argv[1:])
    if argv in (['-h'], ['--help']):
        print('Additional commands:')
        print('  demo --output <directory>  One synthetic CPU example; no weights')
        print('  assets --scope gp-mp       Inspect required assets; no downloads or inference')
        print('  train --help               Explicit GP-MP, STMP and GNN training commands')
        print('  plot --list / --check       Read saved figures or compare temporary renders')
        print('  white_followup inspect     Inspect the original frozen follow-up queue')
        print('  convergence                Original closed convergence study')
        print()
    if argv and argv[0] == 'white_followup':
        # Frozen asset identities are verified through the recorded source archive.
        from experiment.studies.white_followup.run import main as frozen
        return frozen(argv[1:])
    if argv and argv[0] == 'convergence':
        from experiment.studies.convergence.run import main as frozen
        return frozen(argv[1:])
    if argv and argv[0] == 'plot':
        from plotting.render_paper import main as plot
        return plot(argv[1:])
    from experiment.cli import main as experiment
    return experiment(argv)
