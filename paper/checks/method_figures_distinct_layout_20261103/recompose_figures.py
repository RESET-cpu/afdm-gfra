"""Recompose the source-based figures around the present manuscript's model."""
import json
import vector_base as b
from vector_base import fitz, Labels, line, copy_paths, stack

BLUE=(.23,.41,.53)
TEAL=(.37,.58,.55)
COPPER=(.66,.43,.32)
INK=(.13,.13,.13)
GREY=(.49,.49,.49)
PALE=(.84,.90,.92)
b.BLUE=BLUE;b.TEAL=TEAL;b.OCHRE=COPPER;b.PALE=PALE

def node(p,x,y,fill=None,r=3.7,square=False):
    rect=fitz.Rect(x-r,y-r,x+r,y+r)
    if square:p.draw_rect(rect,color=INK,fill=fill or INK,width=.55)
    else:p.draw_circle((x,y),r,color=INK,fill=fill or (1,1,1),width=.55)

def box(p,l,rect,title,sub=None):
    r=fitz.Rect(rect);p.draw_rect(r,color=GREY,width=.55)
    if sub:
        l.text((r.x0+r.x1)/2,r.y0+r.height*.31,title,7.5)
        l.text((r.x0+r.x1)/2,r.y0+r.height*.72,sub,8.5)
    else:l.text((r.x0+r.x1)/2,(r.y0+r.y1)/2,title,8)

def system():
    d=fitz.open(b.REF/'shen2025.pdf');src=d[2]
    out=fitz.open();p=out.new_page(width=504,height=218);l=Labels(504,218)
    cmap=[((.470947,.580078,.250977),BLUE),((.875,.783203,.501953),(.91,.94,.945))]
    # Original vector satellite and footprint are repositioned independently.
    copy_paths(src,p,(525,102,558,134),(61,27,105,70),cmap)
    copy_paths(src,p,(312,171,506,222),(10,119,252,181),cmap,
               path_filter=lambda d:d['rect'].width>100)
    for x,y in [(35.3,153),(130.8,163.7)]:node(p,x,y,BLUE,r=4.1)
    for x,y in [(54,136),(99,134),(155,133),(202,147),(182,165),(83,172),(218,161)]:
        node(p,x,y,r=4.1)
    # Same source UPA, moved next to the satellite; edited dimension notation.
    updoc=fitz.open(b.REF/'shen2025.pdf');up=updoc[2]
    b.recolor(updoc,[((.611328,.290039,.0353088),(1,1,1)),
                    ((.917969,.438965,.0509949),(1,1,1))])
    b.erase_text(up,[(519.5,176.8,525.2,183),(550.8,202.5,556,209),
                     (524,194,530,199),(523,205,529,210)])
    upbounds=(508,169,565,222);b.isolate(up,upbounds)
    upa=b.crop(updoc,2,upbounds);ul=Labels(57,53)
    ul.text(15,10,r'$M_z$',5.5);ul.text(45,38,r'$M_y$',5.5);ul.put(upa[0])
    p.show_pdf_page(fitz.Rect(184,33,245,90),upa,0)
    l.text(82,16,'LEO satellite',8.2)
    l.text(214,22,r'UPA: $M=M_yM_z$',7.9)
    line(p,[(102,48),(175,48)],color=GREY,width=.45,dash='[2 2] 0')
    # Uplink arrows terminate at the receiving satellite.
    line(p,[(35.3,148.9),(65,68)],color=INK,width=.6,arrow=True)
    line(p,[(130.8,159.7),(68,68)],color=INK,width=.6,arrow=True)
    l.text(30,105,r'$\widetilde\tau_{k\ell},\nu_k$',7.8)
    l.text(161,103,r'$\tau_{k\ell}=\widetilde\tau_{k\ell}-\tau_c$',8.6)
    l.text(132,65,r'$\tau_c$ compensation',7.1)
    node(p,35,193,BLUE,r=3);l.text(45,193,'Active',7.4,ha='left')
    node(p,102,193,r=3);l.text(112,193,'Inactive',7.4,ha='left')
    l.text(220,193,r'$K$ devices',7.6)
    l.text(15,210,'(a) Satellite access',8,ha='left')
    # The frame train replaces the original subcarrier-time grid.
    l.text(390,17,r'$Q$ consecutive pilot frames',8.6)
    l.text(390,39,r'$p_{qk}\ \longrightarrow\ {\rm IDAFT}\ \longrightarrow\ {\rm CPP}$',8.2)
    for x,q,phase in [(285,'0',r'$1$'),(345,'1',r'$e^{\mathrm{j}\beta_k}$'),
                      (437,'Q-1',r'$e^{\mathrm{j}(Q-1)\beta_k}$')]:
        l.text(x+25,56,rf'$q={q}$',7.4)
        p.draw_rect(fitz.Rect(x,65,x+15,85),color=INK,fill=(.94,)*3,width=.55)
        p.draw_rect(fitz.Rect(x+15,65,x+50,85),color=INK,fill=PALE,width=.55)
        l.text(x+7.5,75,'CPP',5.9);l.text(x+32.5,75,'AFDM',7.2)
        l.text(x+25,105,phase,8)
    l.text(416,75,r'$\cdots$',11)
    line(p,[(285,90),(490,90)],color=GREY,width=.45,arrow=True)
    line(p,[(285,115),(285,120),(487,120),(487,115)],color=GREY,width=.45)
    l.text(386,132,r'Shared $\alpha_k$ and reference $H_k$',8)
    l.text(386,156,r'$A_{q,kn}=P_{qkn}e^{\mathrm{j}q\beta_k}$',10)
    l.text(386,180,r'$\mathbf{Y}=\mathbf{A}\mathbf{X}+\mathbf{W}$',11)
    l.text(386,197,r'$T_{\rm frame}=(N+N_{\rm CPP})T_s$',8)
    l.text(285,210,'(b) Multi-frame AFDM observation',8,ha='left')
    l.put(p);return out

def factor():
    # Reuse the edited left half of the last figure; replace its crossing tree.
    old=fitz.open(b.RUN/'before/factor_graph.pdf')
    bracket_boxes=[]
    for block in old[0].get_text('dict')['blocks']:
        for row in block.get('lines',[]):
            for span in row['spans']:
                if 'CMEX10' in span['font']:bracket_boxes.append(span['bbox'])
    b.erase_text(old[0],bracket_boxes)
    out=fitz.open();p=out.new_page(width=344,height=212);l=Labels(344,212)
    p.show_pdf_page(fitz.Rect(0,8,154.8,183.2),old,0,clip=fitz.Rect(0,0,129,146))
    line(p,[(152.76,32),(155.16,32),(155.16,178.4),(152.76,178.4)],color=INK,width=.42)
    l.text(111,15,r'$\mathbf X\in\mathbb C^{KN\times MN}$'.replace(r'\mathbf X',r'\mathbf{X}').replace(r'\mathbb C',r'\mathbb{C}'),8)
    for k,ym,y in [('1',50,44),('2',86,102),('K',160,169)]:
        # Device blocks each receive a local pair of channel/activity branches.
        line(p,[(155.2,ym),(169.3,y)],color=INK,width=.55)
        line(p,[(176.7,y),(213.5,y)],color=INK,width=.55)
        node(p,173,y,PALE);node(p,217,y,square=True,r=3.5)
        l.text(173,y-9,rf'$X_{k}$',8.1)
        l.text(214,y-13,rf'$p(X_{k}|H_{k},\alpha_{k})$',7)
        for sign,kind in [(-1,'H'),(1,'a')]:
            yy=y+sign*12
            line(p,[(220.5,y),(261.3,yy)],color=INK,width=.55)
            line(p,[(268.7,yy),(318.5,yy)],color=INK,width=.55)
            node(p,265,yy,PALE if kind=='H' else (.95,.89,.85))
            node(p,322,yy,square=True,r=3.5)
            label=rf'$H_{k}$' if kind=='H' else rf'$\alpha_{k}$'
            prior=rf'$q_{{\rm tr}}(H_{k})$' if kind=='H' else rf'$p(\alpha_{k})$'
            l.text(265,yy+sign*9,label,8)
            l.text(313,yy+sign*9,prior,7.7)
    l.text(217,137,r'$\vdots$',8.5)
    l.text(293,137,r'$\vdots$',8.5)
    l.text(69,203,'Linear estimation',8)
    l.text(250,203,'Joint denoising',8)
    l.put(p);return out

def small_classifier(p,x,y):
    # A scalar-output classifier icon, distinct from the channel mean network.
    layers=[[(x,y-10),(x,y),(x,y+10)],
            [(x+20,y-14),(x+20,y-5),(x+20,y+5),(x+20,y+14)],[(x+42,y)]]
    for a,c in zip(layers,layers[1:]):
        for z in a:
            for v in c:line(p,[z,v],color=(.7,)*3,width=.35)
    for i,layer in enumerate(layers):
        for z in layer:p.draw_circle(z,2.9,color=None,fill=[BLUE,TEAL,COPPER][i])

def receiver():
    out=fitz.open();p=out.new_page(width=504,height=282);l=Labels(504,282)
    # A compact exchange diagram precedes, rather than sits beside, the details.
    l.text(12,13,'(a) Message exchange',8.4,ha='left')
    box(p,l,(100,22,175,49),'MFLE')
    box(p,l,(340,22,415,49),'GPJD')
    line(p,[(175,29),(340,29)],color=BLUE,arrow=True)
    line(p,[(340,43),(175,43)],color=BLUE,arrow=True)
    l.text(258,21,r'$R_k,\ v$',8)
    l.text(258,51,r'$\mathbf{X}^{\rm pri},\ \gamma$',8)
    line(p,[(12,65),(492,65)],color=(.78,)*3,width=.45)
    l.text(12,76,'(b) Learned updates in GPJD',8.4,ha='left')
    # Preserve the original mean-network vector glyph, in a new arrangement.
    cd=fitz.open(b.REF/'cai2026_stmp_v2.pdf')
    cmap=[((.3568628,.6,.827451),BLUE),((.6666667,.8196079,.5568628),TEAL),
          ((.9254902,.6705883,.4941176),COPPER)]
    copy_paths(cd[9],p,(345,86,402,124),(118,105,175,143),cmap)
    stack(p,26,106,24,31);l.text(41,152,r'$R_k$',8.8)
    stack(p,212,106,23,31);l.text(226,152,r'$F_k$',8.8)
    line(p,[(56,123),(118,123)],color=BLUE,arrow=True)
    line(p,[(175,123),(212,123)],color=BLUE,arrow=True)
    l.text(147,96,r'$F_\theta(\,\cdot\,,vI_D)$',9)
    l.text(147,85,'Colored-noise training',6.8)
    # Mean and derivative variance meet at the channel site.
    box(p,l,(302,108,369,143),'Gaussian site',r'$\mu_k,\ t_k$')
    line(p,[(241,123),(302,123)],color=BLUE,arrow=True)
    l.text(335,97,r'$(R_k,v)$',7.5)
    line(p,[(335,101),(335,108)],color=GREY,arrow=True)
    box(p,l,(115,165,179,189),'Finite differences',r'of $F_\theta$')
    line(p,[(147,143),(147,165)],color=GREY,arrow=True)
    # A gap at x=250 marks a crossing, not a junction, with the feature branch.
    line(p,[(179,177),(247,177)],color=GREY)
    line(p,[(253,177),(274,177),(274,136),(302,136)],color=GREY,arrow=True)
    l.text(224,166,r'$\widehat\tau_k\ \longrightarrow\ \tau$',8.4)
    l.text(213,187,'Average over devices',6.7)
    # Shared observation and noise inputs.
    line(p,[(77,123),(77,244),(123,244)],color=BLUE,arrow=True)
    p.draw_rect(fitz.Rect(28,174,53,181),fill=(.90,)*3,color=GREY,width=.45)
    l.text(40,194,r'$v$',8.5)
    line(p,[(53,177),(87,177),(87,138),(120,138)],color=GREY,arrow=True)
    line(p,[(87,177),(87,255),(123,255)],color=GREY,arrow=True)
    # A denoiser-derived feature enters the scalar classifier.
    line(p,[(226,156),(250,156),(250,206),(99,206),(99,234),(123,234)],color=BLUE,arrow=True)
    l.text(231,200,r'$F_k$',7.7,ha='left')
    small_classifier(p,126,244)
    l.text(147,217,r'$z_\phi(R_k,v,F_k)$',8.8)
    line(p,[(171,244),(211,244)],color=COPPER,arrow=True)
    box(p,l,(211,231,269,258),'Bayes rule',r'$p_k$')
    l.text(242,218,r'$\rho,\ \pi_{\rm tr}$',7.8)
    line(p,[(242,222),(242,231)],color=GREY,arrow=True)
    l.text(147,273,'Density-ratio estimation',7.6)
    # Both paths end at the same joint posterior moments and feedback update.
    p.draw_rect(fitz.Rect(405,173,482,221),color=GREY,width=.55)
    l.text(443.5,183,'Joint moments',7.8)
    l.text(443.5,197,r'$\widehat{X}_k,\ \mathbf{C}_{X,k}$',9)
    l.text(443.5,212,'Extrinsic message',7.4)
    line(p,[(369,123),(387,123),(387,184),(405,184)],color=BLUE,arrow=True)
    l.text(388,153,r'$\mu_k,t_k$',8,ha='left')
    line(p,[(269,244),(387,244),(387,210),(405,210)],color=COPPER,arrow=True)
    l.text(335,236,r'$p_k$',8.5)
    l.text(445,159,r'$(R_k,v)$',7.7)
    line(p,[(445,164),(445,173)],color=GREY,arrow=True)
    line(p,[(482,198),(497,198)],color=BLUE,arrow=True)
    l.put(p);return out

if __name__=='__main__':
    records=[b.export(system(),'system_multiframe'),b.export(factor(),'factor_graph'),
             b.export(receiver(),'learned_receiver')]
    (b.RUN/'EXPORTS.json').write_text(json.dumps(records,indent=2),encoding='utf8')
    print(json.dumps(records,indent=2))
