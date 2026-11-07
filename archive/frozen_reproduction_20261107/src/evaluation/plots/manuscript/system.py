"""Fig. 1; original vector artwork from Shen Fig. 1, PDF page 3."""
from . import vector as b
from .vector import fitz, Labels, line, copy_paths
BLUE=(.18,.36,.48); TEAL=(.42,.61,.59); COPPER=(.63,.38,.27)
INK=(.12,)*3; GREY=(.52,)*3; PALE=(.84,.90,.93)
ACTIVE=[(40,132),(151,135)]
INACTIVE=[(23,122),(84,116),(117,117),(169,121),(87,140),(128,141),(181,132)]
# Lower satellite-body corner and top-right array element; one straight segment.
UPA_LEADER=[(188+(537.56201171875-525)*38/33,
             16+(126.88800048828125-102)*37/32),
            (237.6709442138672,99.26016235351562)]
FRAME_WIDTH=.5
FRAME_COLOR=(.3,)*3

def node(p,x,y,fill=None,r=2.7,square=False):
    if square:p.draw_rect(fitz.Rect(x-r,y-r,x+r,y+r),color=INK,fill=INK,width=.45)
    else:p.draw_circle((x,y),r,color=INK,fill=fill or (1,1,1),width=.5)

def system():
    srcdoc=fitz.open(b.REF/'shen2025.pdf');src=srcdoc[2]
    out=fitz.open();p=out.new_page(width=252,height=166);l=Labels(252,166)
    cmap=[((.470947,.580078,.250977),BLUE),((.875,.783203,.501953),(.92,.945,.95))]
    copy_paths(src,p,(312,171,506,222),(5,105,198,151),cmap,
               path_filter=lambda d:d['rect'].width>100)
    copy_paths(src,p,(525,102,558,134),(188,16,226,53),cmap)
    l.text(207,8,'LEO satellite',8)
    line(p,[(40,132),(194,49)],color=BLUE,width=.75,arrow=True)
    line(p,[(151,135),(197,51)],color=BLUE,width=.75,arrow=True)
    l.text(123,78,'TSL',7.4,rotation=27,rotation_mode='anchor')
    for x,y in ACTIVE:node(p,x,y,BLUE,r=3)
    for x,y in INACTIVE:
        node(p,x,y,r=3)
    l.text(61,137,r'Device $k$',7.1)
    for x,q in [(6,'0'),(56,'1'),(119,'Q-1')]:
        l.text(x+20.5,16,rf'$q={q}$',7.1)
        # Fills have no strokes; each boundary is drawn only once at a common width.
        p.draw_rect(fitz.Rect(x,26,x+41,44),color=None,fill=PALE)
        p.draw_rect(fitz.Rect(x,26,x+13,44),color=None,fill=(.95,)*3)
        p.draw_rect(fitz.Rect(x,26,x+41,44),color=FRAME_COLOR,width=FRAME_WIDTH)
        line(p,[(x+13,26),(x+13,44)],color=FRAME_COLOR,width=FRAME_WIDTH)
        if q=='0':
            l.text(x+6.5,35,'CPP',5.7);l.text(x+27,35,'AFDM',6.6)
    l.text(108,35,r'$\cdots$',8.5)
    line(p,[(6,50),(6,55),(160,55),(160,50)],color=FRAME_COLOR,width=FRAME_WIDTH)
    l.text(83,65,r'$Q$ AFDM frames',7.5)
    line(p,[(37.6,130.2),(8,87),(8,59)],color=GREY,width=.45,dash='[2 2] 0')
    # UPA dimensions are relabelled at the final column scale.
    ud=fitz.open(b.REF/'shen2025.pdf');up=ud[2]
    b.recolor(ud,[((.611328,.290039,.0353088),(1,1,1)),
                  ((.917969,.438965,.0509949),(1,1,1))])
    b.erase_text(up,[(519.5,176.8,525.2,183),(550.8,202.5,556,209),
                    (524,194,530,199),(523,205,529,210)])
    clip=(508,169,565,222);b.isolate(up,clip)
    a=b.crop(ud,2,clip);al=Labels(57,53)
    al.text(15,10,r'$M_z$',7.4);al.text(45,38,r'$M_y$',7.4);al.put(a[0])
    # Draw the leader first so its final point meets the array element beneath it.
    line(p,UPA_LEADER,color=(.65,)*3,width=.4,dash='[2 2] 0')
    p.show_pdf_page(fitz.Rect(201,87,251,133.5),a,0)
    l.text(212,78,'UPA',7.4)
    node(p,11,159,BLUE,r=2.4);l.text(17,159,'Active',7,ha='left')
    node(p,50,159,r=2.4);l.text(56,159,'Inactive',7,ha='left')
    l.text(139,159,r'$K$ devices',7.6)
    l.put(p);return out
