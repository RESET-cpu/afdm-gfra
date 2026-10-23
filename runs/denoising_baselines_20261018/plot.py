"""Render the completed comparison with all methods on a common SNR axis."""
from run import OUT, read
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    summary = read(OUT / 'SUMMARY.json')
    assert summary['status'] == 'COMPLETE'
    styles = {
        'noisy': ('LS (noisy input)', '#999999', ':', 'o'),
        'gaussian': ('Gaussian prior', '#b08b35', '--', 'o'),
        'somp': ('SOMP', '#8b5da5', '-', '^'),
        'gamp': ('GAMP-SBL', '#57a0a0', '-', 'v'),
        'gnn': ('GNN-ASPL (existing weights)', '#de8b40', '-', 'D'),
        'offgrid_sbl': ('Off-grid SBL', '#515d90', '-', 'P'),
        'proposed_small': ('Proposed (5,000 training channels)', '#2775b6', '-', 'o'),
        'proposed': ('Proposed (50,000 training channels)', '#d2493d', '-', 'o'),
        'genie_bound': ('Genie conditional MMSE (oracle)', '#299568', '--', 's')}
    fig, ax = plt.subplots(figsize=(9, 6), layout='constrained')
    for method, (label, color, line, marker) in styles.items():
        rows = sorted([r for r in summary['rows'] if r['method'] == method], key=lambda r:r['snr_db'])
        assert len(rows) == 6
        ax.plot([r['snr_db'] for r in rows], [r['nmse_db'] for r in rows],
            label=label, color=color, linestyle=line, marker=marker,
            linewidth=2.2 if method.startswith('proposed') else 1.5, markersize=5)
    ax.set(xlabel='SNR (dB)', ylabel='Channel NMSE (dB)',
        title='Direct channel denoising\n500 physical scenes × 4 channels; known input noise')
    ax.set_xticks([-20, -10, 0, 10, 20, 30])
    ax.grid(alpha=.22)
    ax.legend(fontsize=8.5, loc='upper right', ncol=1)
    fig.get_layout_engine().set(rect=(0, .045, 1, .955))
    fig.text(.5, .014, r'SNR = $-10\log_{10}v$; unit reference channel power in fixed training coordinates.',
             ha='center', fontsize=8.5, color='#555555')
    for ext in ['png', 'pdf']:
        fig.savefig(OUT / ('denoising.' + ext), dpi=200)
    plt.close(fig)


if __name__ == '__main__':
    main()
