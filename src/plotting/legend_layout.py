"""Place legends in measured whitespace without changing data-axis limits."""
from matplotlib.legend import Legend

POSITIONS = ['upper right', 'lower left', 'upper left', 'lower right',
             'center right', 'center left', 'upper center', 'lower center']


def automatic_legend(ax, methods, options):
    """Try a whole legend, then two groups, then an outside legend.

    Called after the figure's initial layout, so collisions are checked in
    display coordinates, including marker clearance, rather than data units.
    No axis limit or tick is modified to make room for a legend.
    """
    renderer = ax.figure.canvas.get_renderer()
    handles = dict(zip(methods, ax.lines))
    base = {k:v for k,v in options.items() if k not in ('show','groups','loc','bbox_to_anchor','combined_metrics')}
    columns = list(dict.fromkeys([base.pop('ncol',1),1,2]))
    paths = [(line.get_path().transformed(line.get_transform()),
              max(line.get_markersize()/2, line.get_linewidth())*ax.figure.dpi/72+1)
             for line in ax.lines]

    def make(group, loc, ncol, anchor=None):
        kw = dict(base,loc=loc,ncol=ncol)
        if anchor is not None: kw['bbox_to_anchor']=anchor
        legend=Legend(ax,[handles[m] for m in group],[handles[m].get_label() for m in group],**kw)
        legend.set_in_layout(False)
        return legend

    def candidates(group):
        for ncol in columns:
            if ncol>len(group):continue
            for loc in POSITIONS:
                legend=make(group,loc,ncol)
                box=legend.get_window_extent(renderer)
                if not (ax.bbox.contains(box.x0,box.y0) and ax.bbox.contains(box.x1,box.y1)):
                    continue
                if any(path.intersects_bbox(box.padded(pad),filled=False) for path,pad in paths):
                    continue
                if any(text.get_visible() and text.get_window_extent(renderer).overlaps(box) for text in ax.texts):
                    continue
                yield legend,box,dict(methods=group,loc=loc,ncol=ncol)

    selected=None
    for legend,box,record in candidates(methods):
        selected=[(legend,record)]
        break
    if selected is None and len(methods)>1:
        primary=[m for m in methods if m in ('GP_MP','GP_MP_EP','C_STMP','STMP')]
        other=[m for m in methods if m not in primary]
        splits=[]
        if len(primary)>=2 and len(other)>=2:splits.append((primary,other))
        midpoint=(len(methods)+1)//2
        splits.append((methods[:midpoint],methods[midpoint:]))
        for left,right in splits:
            a,b=list(candidates(left)),list(candidates(right))
            for la,ba,ra in a:
                for lb,bb,rb in b:
                    if not ba.padded(2).overlaps(bb):
                        selected=[(la,ra),(lb,rb)]
                        break
                if selected:break
            if selected:break
    if selected is None:
        # Constrained layout reserves space outside the axes, not extra data range.
        columns = min(2, len(methods))
        legend = make(methods, 'upper center', columns, (.5, -.20))
        if legend.get_window_extent(renderer).width > ax.figure.bbox.width - 8:
            columns = 1
            legend = make(methods, 'upper center', columns, (.5, -.20))
        legend.set_in_layout(True)
        selected = [(legend, dict(methods=methods, loc='outside below', ncol=columns))]
    for legend,_ in selected[:-1]:ax.add_artist(legend)
    ax.legend_=selected[-1][0]
    return [record for _,record in selected]
