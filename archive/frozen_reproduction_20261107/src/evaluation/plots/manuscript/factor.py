"""A block-variable factor graph of the manuscript's posterior factorization."""
import json
from . import vector as b
from .vector import fitz, Labels, line

INK=(.12,)*3
GREY=(.52,)*3
BLUE=(0,112/255,74/255)
COPPER=(1,0,0)
PALE=(.89,.96,.92)
ACTIVITY=(1,.93,.93)
OBSERVATIONS=[('1',52),('2',76),('MN',108)]
DEVICES=[('1',52),('2',76),('K',108)]
OBS_X=48
BLOCK_X=102
CONSTRAINT_X=158
BRANCH_X=164
LATENT_X=212
PRIOR_X=244
OFFSET=36
EDGES=[]

def node(page,x,y,fill=None,square=False):
    r=2.7
    if square:
        page.draw_rect(fitz.Rect(x-r,y-r,x+r,y+r),color=INK,fill=INK,width=.45)
    else:
        page.draw_circle((x,y),r,color=INK,fill=fill or (1,1,1),width=.5)

def edge(page,source,target,points,color=INK,width=.5):
    line(page,points,color=color,width=width)
    EDGES.append({'source':source,'target':target,'points':points})

def factor():
    EDGES.clear()
    out=fitz.open();p=out.new_page(width=252,height=167);l=Labels(252,167)
    # Dashed region outlines follow the grouping style of Shen Fig. 2.
    for bounds,color in [((1.5,1.5,118.5,150),BLUE),
                         ((122.5,1.5,250.5,150),COPPER)]:
        p.draw_rect(fitz.Rect(bounds),color=color,width=.65,dashes='[3 2] 0')
    # Every observation column contains entries from all device blocks.
    for j,oy in OBSERVATIONS:
        for k,ky in DEVICES:
            edge(p,f'likelihood_{j}',rf'\mathbf{{X}}_{k}',[(OBS_X,oy),(BLOCK_X,ky)],
                 color=(.38,)*3,width=.45)
    for k,y in DEVICES:
        edge(p,rf'\mathbf{{X}}_{k}',f'constraint_{k}',[(BLOCK_X,y),(CONSTRAINT_X,y)],
             color=BLUE,width=.55)
        for kind,yy in [('H',y-OFFSET),('alpha',y+OFFSET)]:
            edge(p,f'constraint_{k}',f'{kind}_{k}',
                 [(CONSTRAINT_X,y),(BRANCH_X,y),(LATENT_X,yy)])
            edge(p,f'{kind}_{k}',f'{kind}_prior_{k}',
                 [(LATENT_X,yy),(PRIOR_X,yy)])

    # Draw variable/factor symbols over the edges; crossings receive no symbols.
    for j,y in OBSERVATIONS:
        node(p,OBS_X,y,square=True)
        l.text(41,y,rf'$p(\mathbf{{y}}_{{{j}}}|\mathbf{{x}}_{{{j}}})$',7,ha='right')
    for k,y in DEVICES:
        node(p,BLOCK_X,y,PALE)
        node(p,CONSTRAINT_X,y,square=True)
        l.text(BLOCK_X+8,y+7,rf'$\mathbf{{X}}_{k}$',7.8)
        l.text(143.5,y-8,rf'$p(\mathbf{{X}}_{k}|\mathbf{{H}}_{k},\alpha_{k})$',7)
        for kind,yy in [('H',y-OFFSET),('alpha',y+OFFSET)]:
            is_h=kind=='H'
            node(p,LATENT_X,yy,ACTIVITY)
            node(p,PRIOR_X,yy,square=True)
            l.text(LATENT_X,yy-7,rf'$\mathbf{{H}}_{k}$' if is_h else rf'$\alpha_{k}$',7.1)
            l.text(237,yy-7,rf'$q_{{\rm tr}}(\mathbf{{H}}_{k})$' if is_h else rf'$p(\alpha_{k})$',6.8)
    for x in [OBS_X,BLOCK_X,CONSTRAINT_X]:l.text(x,92,r'$\vdots$',7.1)
    for x in [LATENT_X,PRIOR_X]:
        l.text(x,54,r'$\vdots$',6.8)
        l.text(x,126,r'$\vdots$',6.8)
    l.text(60,160.5,'Linear estimation',8.2,color=BLUE,fontweight='bold')
    l.text(186.5,160.5,'Joint denoising',8.2,color=COPPER,fontweight='bold')
    l.put(p)
    out.set_metadata({'title':'Factor graph with device blocks',
                      'subject':'Device-block graph of the manuscript posterior factorization; prior branches follow Cai Fig. 2',
                      'creator':'Recomposed scientific figure, 2026-11-03'})
    return out

