"""Render verified pilot NMSE with the accepted manuscript user-count style."""
from pathlib import Path
import json
from copy import deepcopy
from plotting.manuscript import experiments as engine
import hashlib

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = HERE


def main():
    read = lambda p: json.loads(p.read_text(encoding='utf-8'))
    raw = read(HERE / 'SUMMARY.json')
    assert raw['status'] == 'VERIFIED'
    assert sha(HERE / 'SUMMARY.json') == read(HERE / 'COMPLETION.json')['summary_sha256']
    all_cfg = read(ROOT / 'src/configs/plots/manuscript.json')['figures']
    cfg = deepcopy(all_cfg['user_count'])
    mapping = dict(GP_MP='C_STMP', GP_MP_EP='C_STMP_phase_frontend_marginal_20261104',
                   offgrid13='offgrid_sbl_13', offgrid25='offgrid_sbl_25')
    methods = ['GP_MP','GP_MP_EP','STMP','offgrid_sbl','offgrid13','offgrid25','gnn','gamp','somp']
    cfg.update(methods=methods, x='frames', point_count=45)
    cfg['styles'] = {m: deepcopy(all_cfg['snr_comparison']['styles'][mapping.get(m,m)]) for m in methods}
    cfg['labels'] = {m: all_cfg['snr_comparison']['labels'][mapping.get(m,m)] for m in methods}
    fig, curves = engine.draw('user_count', raw, cfg)
    ax = fig.axes[0]
    ax.set_xlabel('Number of pilot frames', labelpad=1)
    ax.set_ylim(-15,0)
    ax.set_yticks([-15,-10,-5,0])
    for line in ax.lines:
        line.set_clip_on(True)
        line.set_clip_path(ax.patch)
    for legend in list(fig.legends):
        legend.remove()
    # Match the main SNR figure's three-column legend and handle spacing.
    fig.subplots_adjust(left=.155, right=.965, bottom=.28925023748689727, top=.9754716981132076)
    fig.legend(*ax.get_legend_handles_labels(),loc='lower center',
               bbox_to_anchor=(.5,.008),ncol=3,borderaxespad=0,
               **dict(engine.LEGEND, **all_cfg['snr_comparison']['legend_style']))
    engine.validate(fig, curves, cfg)
    OUT.mkdir(exist_ok=True)
    for ext in ('png','pdf'):
        fig.savefig(OUT / ('pilot_frames_nmse.'+ext), dpi=600)
    receipt = dict(summary_sha256=sha(HERE/'SUMMARY.json'), renderer_sha256=sha(Path(__file__)),
                   reference='src/plotting/manuscript/experiments.py:draw(user_count)',
                   size_inches=list(fig.get_size_inches()), curves=curves, data_unchanged=True,
                   axes_limits=[-15,0], legend_columns=3,
                   points_outside_display=[r for r in raw['rows'] if not -15<=r['nmse_db']<=0])
    (OUT/'PLOT_CHECKS.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(OUT/'pilot_frames_nmse.png')


if __name__ == '__main__':
    main()
