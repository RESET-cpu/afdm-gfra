"""Diagnostic figures drawn from already aggregated experiment results."""
def plot(out,plan,rows,records):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    labels={name: spec['label'] for name,spec in plan['algorithm_specs'].items()}
    name=plan['experiment']; denoise=plan['experiment_kind']=='denoiser'
    fig,axes=plt.subplots(1,1 if denoise else 2,figsize=(11,5),layout='constrained',squeeze=False)
    for method in plan['methods']:
        group=[r for r in rows if r['method']==method]
        x=[r['parameters']['variance'] if denoise else r['condition'] for r in group]
        label=labels[method]
        axes[0,0].plot(x,[r['nmse_db'] for r in group],marker='o',label=label)
        if not denoise:axes[0,1].plot(x,[100*r['aer'] for r in group],marker='o',label=label)
    for ax in axes.flat:
        ax.grid(alpha=.25)
        ax.set_xlabel('Known complex AWGN variance' if denoise else 'Condition index (see report)')
    axes[0,0].set_ylabel('Channel NMSE (dB)')
    if denoise:axes[0,0].set_xscale('log')
    else:axes[0,1].set_ylabel('Activity error rate (%)')
    axes[0,-1].legend(fontsize=7,loc='upper left',bbox_to_anchor=(1,1))
    information = '' if denoise else f" | phase: {plan['phase_mode']} | noise: {plan['noise_mode']}"
    fig.suptitle(f"{name} | {plan['scene_count']} scenes/condition | {plan['mode']}"+information,fontsize=10)
    for ext in ('png','pdf'):fig.savefig(out/f'comparison.{ext}',dpi=160)
    plt.close(fig)
    if name!='runtime_comparison':return
    fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    for method in plan['methods']:
        group=[r for r in rows if r['method']==method]
        label=labels[method]+' / '+group[0]['backend']
        x=[r['mean_end_to_end_seconds'] for r in group]
        axes[0].plot(x,[r['nmse_db'] for r in group],marker='o',label=label)
        axes[1].plot(x,[100*r['aer'] for r in group],marker='o',label=label)
    for ax in axes:
        ax.set_xscale('log');ax.set_xlabel('Mean end-to-end time including phase (s)');ax.grid(alpha=.25)
    axes[0].set_ylabel('Channel NMSE (dB)');axes[1].set_ylabel('Activity error rate (%)')
    axes[1].legend(loc='upper left',bbox_to_anchor=(1,1),fontsize=7)
    fig.suptitle(f"Runtime and accuracy | {plan['mode']} | native backends labelled")
    for ext in ('png','pdf'):fig.savefig(out/f'runtime_accuracy.{ext}',dpi=160)
    plt.close(fig)
