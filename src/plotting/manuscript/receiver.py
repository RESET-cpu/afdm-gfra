"""Fig. 3; approved compact receiver with a saved input/output example."""
from plotting.manuscript import vector as b
from plotting.manuscript.vector import fitz
from plotting.manuscript.vector import Labels
from plotting.manuscript.vector import line
from plotting.manuscript.vector import copy_paths
import numpy as np
import matplotlib as mpl
import re
ROOT = b.ROOT
BLACK=(0,0,0)
GREEN=(0,112/255,74/255)
RED=(1,0,0)
PALE_GREEN=(.89,.96,.92)
PALE_RED=(1,.93,.93)
# Network colors follow Cai's blue / light-green / orange layer coding.
NODE_BLUE=(.31,.57,.78)
NODE_GREEN=(.64,.80,.52)
NODE_ORANGE=(.92,.63,.44)

SOURCE=ROOT/'result/channel_denoising/figures/white_mainline_500_20261107'
SAVED=SOURCE/'scene000_example.npz'
data=np.load(SAVED,allow_pickle=False)
# Fixed illustrative selection: first stored scene/device, v=1, antennas 0-2.
INPUT=np.abs(data['query'][3,0,:3])
OUTPUT=np.abs(data['estimate'][3,0,:3])
VMAX=float(max(INPUT.max(),OUTPUT.max()))
CMAP=mpl.colormaps['viridis']


def box(p,l,bounds,labels,color=BLACK,width=.65,bold=False,fill=None):
    p.draw_rect(fitz.Rect(bounds),color=color,fill=fill,width=width)
    x=(bounds[0]+bounds[2])/2
    for y,text,size in labels:
        l.text(x,y,text,size,color=BLACK,fontweight='bold' if bold else 'normal')


def arrow(p,pts,width=.6):
    line(p,pts,color=BLACK,width=width,arrow=True)


def classifier(p,x,y):
    layers=[]
    for i,n in enumerate((3,5,1)):
        xx=x+17*i
        ys=[y] if n==1 else [y-10+j*20/(n-1) for j in range(n)]
        layers.append([(xx,yy) for yy in ys])
    for left,right in zip(layers,layers[1:]):
        for a in left:
            for z in right:line(p,[a,z],color=(.68,)*3,width=.25)
    for i,layer in enumerate(layers):
        for pt in layer:p.draw_circle(pt,2.05,color=None,fill=(NODE_BLUE,NODE_GREEN,NODE_ORANGE)[i])


def channel_stack(p,x,y,values):
    """Real saved magnitudes, identical normalization, vector cells, no filtering."""
    side=25
    for i in reversed(range(3)):
        xx,yy=x+2.5*i,y-2.5*i
        for row in range(16):
            for col in range(16):
                r=fitz.Rect(xx+side*col/16,yy+side*row/16,
                            xx+side*(col+1)/16,yy+side*(row+1)/16)
                p.draw_rect(r,color=None,fill=CMAP(values[i,row,col]/VMAX)[:3],width=0)
        p.draw_rect(fitz.Rect(xx,yy,xx+side,yy+side),color=(.27,.37,.43),width=.35)


def receiver():
    # Compile the manuscript first so figure references follow its equation labels.
    aux=(ROOT/'paper/build/main.aux').read_text(encoding='utf-8')
    numbers=dict(re.findall(r'\\newlabel\{(eq:[^}]+)\}\{\{([^}]+)\}',aux))

    def eqref(first,last=None):
        start=f'({numbers[first]})'
        return start if last is None else f'{start}–({numbers[last]})'

    out=fitz.open();p=out.new_page(width=468,height=158);l=Labels(468,158)
    box(p,l,(21,26,83,54),[(40,'MFLE',9.5)],GREEN,1.4,True,fill=PALE_GREEN)
    box(p,l,(21,110,83,138),[(124,'GPJD',9.5)],RED,1.4,True,fill=PALE_RED)
    l.text(52,12,r'$\mathbf{Y},\widehat{\mathbf{A}}$',8.5)
    arrow(p,[(52,19),(52,26)])
    arrow(p,[(31,54),(31,110)],.7)
    l.text(15,82,r'$\mathbf{R}_k,v$',8.3)
    arrow(p,[(73,110),(73,54)],.7)
    l.text(52,82,r'$\mathbf{X}^{\rm pri},\gamma$',8.2)

    line(p,[(83,110),(116,8)],color=BLACK,width=.45,dash='[2 2] 0')
    line(p,[(83,138),(116,153)],color=BLACK,width=.45,dash='[2 2] 0')
    p.draw_rect(fitz.Rect(116,8,466,153),color=BLACK,width=1.4)

    # The same antenna slices enter and leave the denoiser, as in Cai Fig. 3.
    channel_stack(p,125,52,INPUT)
    l.text(140,87,r'$\mathbf{R}_k,v$',8.5)
    arrow(p,[(155,65),(173,65)])
    p.draw_circle((164,65),1.05,color=None,fill=BLACK)
    line(p,[(164,65),(164,125),(197,125)],color=BLACK,width=.6)
    l.text(181,115,r'$\mathbf{R}_k,v$',8.2)

    cd=fitz.open(b.REF/'cai2026_stmp_v2.pdf')
    mappings=[((.3568628,.6,.827451),NODE_BLUE),
              ((.6666667,.8196079,.5568628),NODE_GREEN),
              ((.9254902,.6705883,.4941176),NODE_ORANGE)]
    copy_paths(cd[9],p,(345,86,402,124),(173,49,207,77),mappings)
    l.text(190,86,r'$\mathbf{F}_\theta(\,\cdot\,,v\mathbf{I}_D)$',8.3)
    arrow(p,[(207,65),(225,65)])
    channel_stack(p,225,52,OUTPUT)
    l.text(240,87,r'$\mathbf{F}_k$',8.5)
    arrow(p,[(255,65),(281,65)])

    # Keep the variance estimate and device pooling visible.
    # Center the box between the two vertical branches; both horizontal arms are 19.25 pt.
    box(p,l,(183.25,16,287.25,39),[(24,r'$\{\widehat\tau_k\}_{k=1}^{K}\ \to\ \tau^{\rm post}$',8.5),
        (34,eqref('eq:derivative-trace'),8)])
    arrow(p,[(164,65),(164,28),(183.25,28)],.5)
    arrow(p,[(287.25,28),(306.5,28),(306.5,48)],.5)
    box(p,l,(281,48,332,90),[(56,'Gaussian site',8),
        (69,r'$\mathbf{H}_k^{\rm post},t_k$',8.5),
        (82,eqref('eq:site-update','eq:conditional-channel-mean'),8)])
    l.text(306.5,99,r'$(\mathbf{R}_k,v)$',8)
    arrow(p,[(306.5,95),(306.5,90)],.45)

    # Both inputs meet outside the classifier. Neither enters a hidden neuron.
    line(p,[(240,94),(240,106),(197,106),(197,125)],color=BLACK,width=.5)
    p.draw_circle((197,125),1.05,color=None,fill=BLACK)
    arrow(p,[(197,125),(208.9,125)],.6)
    classifier(p,211,125)
    l.text(228,143,r'$z_\phi$',8.5)
    arrow(p,[(247,125),(281,125)])
    l.text(264,116,r'$\ell_k$',8.3)
    box(p,l,(281,113,332,138),[(120,r'$p_k$',8.5),
        (131,eqref('eq:activity-probability'),8)])
    l.text(306.5,146,r'$\rho$',8)
    arrow(p,[(306.5,142.5),(306.5,138)],.4)

    box(p,l,(347,67,394,103),[(78,r'$\widehat{\mathbf{X}}_k,\overline{t}_X$',8.5),
        (94,eqref('eq:mixture','eq:joint-average-variance'),8)])
    arrow(p,[(332,68),(339,68),(339,75),(347,75)])
    arrow(p,[(332,125),(339,125),(339,94),(347,94)])
    box(p,l,(405,67,461,103),[(78,'Extrinsic',8.3),
        (94,eqref('eq:nonlinear-extrinsic','eq:nonlinear-extrinsic-mean'),8)])
    arrow(p,[(394,85),(405,85)])
    l.text(433,55,r'$(\mathbf{R}_k,v)$',8)
    arrow(p,[(433,61),(433,67)],.45)
    arrow(p,[(433,103),(433,116)],.5)
    l.text(433,128,r'$\mathbf{X}_{k,\rm out},\gamma_{\rm out}$',8.2)
    l.put(p)
    return out


