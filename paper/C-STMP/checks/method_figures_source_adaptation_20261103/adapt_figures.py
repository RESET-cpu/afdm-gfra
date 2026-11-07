"""Adapt the supplied paper figures, retaining their vector artwork.

Run with the project's Python. PyMuPDF is installed in the user's cache.
This script changes only the three standalone method figures and run artifacts.
"""
from pathlib import Path
import sys, io, re, json, hashlib, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.append(str(Path.home()/'.cache/codex-pymupdf'))
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
OUT = ROOT/'paper/C-STMP/figures'
REF = ROOT/'reference/literature'
BLUE = (0.26, 0.47, 0.59)
TEAL = (0.43, 0.64, 0.62)
PALE = (0.78, 0.86, 0.88)
OCHRE = (0.72, 0.57, 0.36)
GREY = (0.47,)*3
plt.rcParams.update({'font.family':'Times New Roman','mathtext.fontset':'stix',
                     'pdf.fonttype':42,'axes.unicode_minus':False})

def recolor(doc, mappings):
    pattern = re.compile(rb'(?<![\d.])([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(sc|SC|rg|RG)\b')
    for x in range(1, doc.xref_length()):
        if not doc.xref_is_stream(x): continue
        if '/Subtype /Image' in doc.xref_object(x): continue
        data = doc.xref_stream(x)
        def replace(m):
            old = tuple(float(m.group(i)) for i in (1,2,3))
            for src,dst in mappings:
                if max(abs(a-b) for a,b in zip(old,src))<0.001:
                    return ('%.6f %.6f %.6f '%dst).encode()+m.group(4)
            return m.group(0)
        changed=pattern.sub(replace,data)
        if changed!=data: doc.update_stream(x,changed)

def erase_text(page, boxes):
    for box in boxes:
        page.add_redact_annot(fitz.Rect(box), fill=False, cross_out=False)
    page.apply_redactions(images=0, graphics=0, text=0)

def isolate(page, rect):
    # Remove surrounding manuscript material, instead of merely hiding it.
    r=fitz.Rect(rect);w,h=page.rect.width,page.rect.height
    for b in [(0,0,w,r.y0),(0,r.y1,w,h),(0,r.y0,r.x0,r.y1),(r.x1,r.y0,w,r.y1)]:
        if b[2]>b[0] and b[3]>b[1]:
            page.add_redact_annot(fitz.Rect(b),fill=False,cross_out=False)
    page.apply_redactions(images=1,graphics=1,text=0)

def crop(doc, number, box):
    r=fitz.Rect(box); new=fitz.open();p=new.new_page(width=r.width,height=r.height)
    p.show_pdf_page(p.rect,doc,number,clip=r)
    return new

class Labels:
    def __init__(self,w,h):
        self.fig=plt.figure(figsize=(w/72,h/72));self.ax=self.fig.add_axes([0,0,1,1])
        self.ax.set(xlim=(0,w),ylim=(h,0));self.ax.axis('off')
    def text(self,x,y,s,size=7,ha='center',**kw):
        self.ax.text(x,y,s,fontsize=size,ha=ha,va='center',**kw)
    def put(self,page):
        b=io.BytesIO();self.fig.savefig(b,format='pdf',transparent=True)
        plt.close(self.fig);o=fitz.open(stream=b.getvalue(),filetype='pdf')
        page.show_pdf_page(page.rect,o,0)

def line(p,pts,color=GREY,width=.6,dash=None,arrow=False):
    shape=p.new_shape()
    for a,b in zip(pts,pts[1:]):shape.draw_line(a,b)
    shape.finish(color=color,width=width,dashes=dash,closePath=False);shape.commit()
    if arrow:
        a,b=pts[-2:];dx,dy=b[0]-a[0],b[1]-a[1];v=math.hypot(dx,dy);dx/=v;dy/=v
        tip=fitz.Point(*b);l=3.1;z=1.4
        sh=p.new_shape();sh.draw_polyline([tip,fitz.Point(b[0]-l*dx+z*dy,b[1]-l*dy-z*dx),
            fitz.Point(b[0]-l*dx-z*dy,b[1]-l*dy+z*dx),tip])
        sh.finish(color=color,fill=color,width=.2,closePath=True);sh.commit()

def copy_paths(source, page, clip, target, mappings=()):
    """Copy exact original Bezier paths; no tracing of a raster screenshot."""
    clip=fitz.Rect(clip);target=fitz.Rect(target)
    sx,sy=target.width/clip.width,target.height/clip.height
    def point(p):return fitz.Point(target.x0+(p.x-clip.x0)*sx,target.y0+(p.y-clip.y0)*sy)
    def color(c):
        if c is None:return None
        for a,b in mappings:
            if max(abs(x-y) for x,y in zip(c,a))<.002:return b
        return c
    count=0
    for d in source.get_drawings():
        r=d['rect']
        if not clip.contains(r):continue
        sh=page.new_shape()
        for item in d['items']:
            if item[0]=='l':sh.draw_line(point(item[1]),point(item[2]))
            elif item[0]=='c':sh.draw_bezier(*[point(v) for v in item[1:]])
            elif item[0]=='re':
                z=item[1];sh.draw_rect(fitz.Rect(point(z.tl),point(z.br)))
            elif item[0]=='qu':sh.draw_quad(fitz.Quad(*[point(z) for z in item[1]]))
            else:raise ValueError(item[0])
        sh.finish(color=color(d['color']),fill=color(d['fill']),
            width=(d['width'] or .5)*min(sx,sy),dashes=d['dashes'],
            closePath=d['closePath'],even_odd=d['even_odd'],
            fill_opacity=d['fill_opacity'] if d['fill_opacity'] is not None else 1,
            stroke_opacity=d['stroke_opacity'] if d['stroke_opacity'] is not None else 1)
        sh.commit();count+=1
    return count

def stack(p,x,y,w=23,h=31,n=3):
    """Symbolic tensor slices, not channel samples or measured values."""
    for i in reversed(range(n)):
        r=fitz.Rect(x+3*i,y-3*i,x+w+3*i,y+h-3*i)
        p.draw_rect(r,color=BLUE,fill=(.95,.97,.975),width=.45)
        for j in range(1,5):
            xx=r.x0+w*j/5;line(p,[(xx,r.y0),(xx,r.y1)],color=PALE,width=.3)
        for j in range(1,7):
            yy=r.y0+h*j/7;line(p,[(r.x0,yy),(r.x1,yy)],color=PALE,width=.3)

def export(doc,name):
    path=OUT/(name+'.pdf');doc.set_metadata({'title':name.replace('_',' '),
        'subject':'Adapted from supplied Cai and Shen paper artwork; see source record',
        'creator':'Source-vector adaptation, 2026-11-03'})
    doc.subset_fonts();doc.save(path,garbage=4,deflate=True)
    d=fitz.open(path);p=d[0]
    (OUT/(name+'.svg')).write_text(p.get_svg_image(text_as_path=True),encoding='utf8')
    pix=p.get_pixmap(dpi=600);pix.save(OUT/(name+'.png'))
    p.get_pixmap(dpi=180).save(RUN/'preview'/(name+'.png'))
    return {'name':name,'points':[p.rect.width,p.rect.height],
        'png_pixels':[pix.width,pix.height],'dpi':600,
        'pdf_images':len(p.get_images()),'drawing_paths':len(p.get_drawings()),
        'sha256':{e:hashlib.sha256((OUT/(name+'.'+e)).read_bytes()).hexdigest() for e in ['pdf','svg','png']}}

def factor_graph():
    d=fitz.open(REF/'cai2026_stmp_v2.pdf');p=d[4]
    recolor(d,[((.3529412,.6,.8274510),BLUE)])
    # Retain Cai's matrix, node positions, branches, circles and square factors.
    erase_text(p,[(47,148,96,158),(151,69,168,194),
        (278,52,307,65),(278,70,307,83),(278,102,307,115),
        (48,198,304,208)])
    bounds=(40,50,309,210);isolate(p,bounds)
    out=crop(d,4,bounds);q=out[0];lab=Labels(q.rect.width,q.rect.height)
    def t(x,y,s,sz=6.7,**kw):lab.text(x-40,y-50,s,sz,**kw)
    # Matrix brackets were font glyphs in the source, adjacent to edited indices.
    line(q,[(59.5,20),(57.5,20),(57.5,142),(59.5,142)],color=(0,0,0),width=.35)
    line(q,[(127.3,20),(129.3,20),(129.3,142),(127.3,142)],color=(0,0,0),width=.35)
    # Last matrix column is indexed by MN in the AFDM representation.
    for y,a,b in [(73,'1','1'),(80,'1','2'),(97,'1','N'),(103.5,'2','1'),
                  (110.5,'2','2'),(127.5,'2','N'),(165,'K','1'),(171.5,'K','2'),(189,'K','N')]:
        t(159,y,rf'$x_{{{a}{b},MN}}$',5.15)
    for y in [87.7,118,135,145.5,156,179.5]:t(159,y,r'$\vdots$',5.3)
    t(60.5,152,r'$p(\mathbf{y}_{MN}|\mathbf{x}_{MN})$',6.25)
    t(85.5,153,r'$\mathbf{x}_{MN}$',6.4)
    for y,k in [(58.6,'1'),(76.7,'2'),(108.4,'K')]:t(291.5,y,rf'$q_{{\rm tr}}(H_{k})$',6.5)
    t(72,204,'Linear estimation',6.4)
    t(135,204,'Column-block reorganization',6.1)
    t(233,204,'Joint denoising',6.6)
    lab.put(q)
    return out

def system():
    d=fitz.open(REF/'shen2025.pdf');p=d[2]
    recolor(d,[((.875,.783203,.501953),(.87,.91,.92)),
        ((.470947,.580078,.250977),BLUE),
        ((.611328,.290039,.0353088),OCHRE),
        ((.917969,.438965,.0509949),OCHRE)])
    erase_text(p,[(325,112,444,133),(416,158,426,167),(509,161,516,170),
        (519.5,176.8,525.2,183),(550.8,202.5,556,209),
        (374,204,403,210),(444,195,473,201),(463,161,475,167),
        (524,194,530,199),(523,205,529,210)])
    # Replace the source's grey explanatory box with compact manuscript notation.
    p.draw_rect(fitz.Rect(324,110,447,135),color=None,fill=(1,1,1),overlay=True)
    bounds=(310,101,565,223);isolate(p,bounds)
    scene=crop(d,2,bounds);sp=scene[0];l=Labels(255,122)
    def t(x,y,s,sz=6.2,**kw):l.text(x-310,y-101,s,sz,**kw)
    t(327,116,r'$\tau_{k\ell}=\widetilde\tau_{k\ell}-\tau_c$',7.3,ha='left')
    t(327,129,'Common-delay compensation at satellite',5.9,ha='left')
    t(422,161,r'$\widetilde\tau_{k\ell},\ \nu_k$',6.7)
    t(511,165,r'$\tau_c$',6.4)
    t(524,179,r'$M_z$',5.4);t(552.5,207,r'$M_y$',5.4)
    t(388,207,'Active device',5.6);t(450,198,'Inactive device',5.6)
    t(470,163,'Uplink',5.7)
    l.put(sp)
    out=fitz.open();q=out.new_page(width=504,height=207)
    q.show_pdf_page(fitz.Rect(2,26,290,164),scene,0)
    lab=Labels(504,207)
    lab.text(134,16,'LEO satellite with a uniform planar array',8.3)
    lab.text(134,174,r'$M=M_yM_z$ antennas; $K$ ground devices',7.5)
    # Retain the source grid's exact cell and axis geometry; replace its labels.
    c=fitz.open(REF/'cai2026_stmp_v2.pdf')
    src=fitz.Rect(223,63,294,125);dst=fitz.Rect(341,25,459,134)
    copy_paths(c[3],q,src,dst,[((.3529412,.6,.827451),PALE)])
    line(q,[(346,132),(346,24)],color=(0,0,0),width=.55,arrow=True)
    lab.text(398,15,r'$Q$ consecutive AFDM frames',8.2)
    lab.text(333,80,'Chirp subcarrier',7.4,rotation=90)
    lab.text(471,80,r'$N$',8.2)
    lab.text(397,75,r'$\vdots$',8)
    lab.text(398,141,'Frame index',7.5)
    lab.text(350,141,'0',6.5);lab.text(446,141,r'$Q-1$',6.5)
    lab.text(397,155,r'$p_{qk}\ \longrightarrow\ {\rm IDAFT}\ \longrightarrow\ {\rm CPP}$',8)
    line(q,[(286,46),(341,46)],color=GREY,width=.5,arrow=True)
    lab.text(310,38,r'$p_{qk}$',7.5)
    lab.text(398,172,r'Shared $\alpha_k$ and $H_k$',7.5)
    lab.text(250,190,r'$H_k^{(q)}=e^{\mathrm{j}q\beta_k}H_k,\qquad A_{q,kn}=P_{qkn}e^{\mathrm{j}q\beta_k},\qquad\mathbf{Y}=\mathbf{A}\mathbf{X}+\mathbf{W}$',9)
    lab.put(q);return out

def receiver(factor):
    out=fitz.open();p=out.new_page(width=504,height=253);lab=Labels(504,253)
    # The small graph is the adapted Cai Fig.2, not a new block-flow drawing.
    small=fitz.Rect(2,66,192,66+190*151/269)
    p.show_pdf_page(small,factor,0,clip=fitz.Rect(0,0,269,151))
    lab.text(31,181,'MFLE',7.2)
    lab.text(146,181,'GPJD',7.2)
    lab.text(95,202,'Gaussian extrinsic message exchange',7.4)
    line(p,[(29,190),(166,190)],color=BLUE,width=.6,arrow=True)
    line(p,[(166,212),(29,212)],color=BLUE,width=.6,arrow=True)
    lab.text(96,185,r'$R_k,\ v$',7.3)
    lab.text(96,220,r'$\mathbf{X}^{\rm pri},\ \gamma$',7.3)
    # Same local enlargement construction as Cai Fig.3.
    p.draw_rect(fitz.Rect(95,68,192,176),color=GREY,width=.7)
    p.draw_rect(fitz.Rect(211,8,501,245),color=GREY,width=.75)
    line(p,[(192,68),(211,8)],dash='[3 2] 0',width=.7)
    line(p,[(192,176),(211,245)],dash='[3 2] 0',width=.7)
    lab.text(357,19,'Learned updates in joint denoising',8.2)
    # Preserve the original network glyph paths, layer spacing and arrow edges.
    source_doc=fitz.open(REF/'cai2026_stmp_v2.pdf');source=source_doc[9]
    netclip=fitz.Rect(345,86,402,124)
    cmap=[((.3568628,.6,.827451),BLUE),((.6666667,.8196079,.5568628),TEAL),
          ((.9254902,.6705883,.4941176),OCHRE)]
    n1=copy_paths(source,p,netclip,(278,57,335,95),cmap)
    n2=copy_paths(source,p,netclip,(278,181,335,219),cmap)
    stack(p,228,54,22,34);lab.text(242,102,r'$R_k$',8)
    stack(p,353,54,21,34);lab.text(367,102,r'$F_k$',8)
    line(p,[(257,75),(278,75)],color=BLUE,arrow=True)
    line(p,[(335,75),(353,75)],color=BLUE,arrow=True)
    lab.text(306,45,r'$F_\theta(\,\cdot\,,vI_D)$',8.3)
    lab.text(306,33,'Colored-noise training',6.8)
    # Variance comes from evaluations of this same mean function.
    p.draw_rect(fitz.Rect(279,121,336,146),color=GREY,width=.55)
    lab.text(307.5,129,'Finite differences',6.4)
    lab.text(307.5,139,r'of $F_\theta$',6.8)
    line(p,[(307,95),(307,121)],color=GREY,arrow=True)
    line(p,[(336,134),(369,134)],color=GREY,arrow=True)
    lab.text(357,125,r'$\widehat\tau_k$',7.6)
    lab.text(379,134,r'$\tau$',8.3)
    lab.text(363,146,'Average over devices',6.1)
    # Conditional channel moments use the site and the current input.
    p.draw_rect(fitz.Rect(411,61,481,96),color=GREY,width=.55)
    lab.text(446,70,'Gaussian site',7.1)
    lab.text(446,85,r'$\mu_k,\ t_k$',8.7)
    line(p,[(381,75),(411,75)],color=BLUE,arrow=True)
    line(p,[(387,134),(399,134),(399,88),(411,88)],color=GREY,arrow=True)
    # The observation and noise-level branch, also reused by DRE.
    line(p,[(266,75),(266,201),(278,201)],color=BLUE,arrow=True)
    p.draw_rect(fitz.Rect(229,124,251,130),fill=(.87,)*3,color=GREY,width=.4)
    lab.text(240,141,r'$v$',8)
    line(p,[(251,127),(270,127),(270,91),(281,91)],color=GREY,arrow=True)
    line(p,[(270,127),(270,214),(281,214)],color=GREY,arrow=True)
    # Explicit observation/noise dependence of the site and extrinsic update.
    lab.text(446,51,r'$(R_k,v)$',7)
    line(p,[(446,55),(446,61)],color=GREY,arrow=True)
    # The denoised channel is an additional classifier input.
    line(p,[(367,105),(367,162),(294,162),(294,181)],color=BLUE,arrow=True)
    lab.text(335,156,r'$F_k$',7.3)
    lab.text(306,173,r'$z_\phi(R_k,v,F_k)$',8.1)
    line(p,[(335,201),(350,201)],color=BLUE,arrow=True)
    p.draw_rect(fitz.Rect(350,189,394,215),color=GREY,width=.55)
    lab.text(372,197,'Bayes rule',6.6)
    lab.text(372,208,r'$p_k$',8.4)
    lab.text(372,180,r'$\rho,\ \pi_{\rm tr}$',7.3)
    line(p,[(372,184),(372,189)],color=GREY,arrow=True)
    # A single pair of joint moments yields the feedback Gaussian message.
    p.draw_rect(fitz.Rect(411,170,481,215),color=GREY,width=.55)
    lab.text(446,179,'Joint moments',7)
    lab.text(446,191,r'$\widehat{X}_k,\ \mathbf{C}_{X,k}$',8)
    lab.text(446,205,'Extrinsic message',6.8)
    line(p,[(446,96),(446,170)],color=BLUE,arrow=True)
    lab.text(462,133,r'$\mu_k,t_k$',7.5)
    line(p,[(394,202),(411,202)],color=BLUE,arrow=True)
    lab.text(485,159,r'$(R_k,v)$',6.5)
    line(p,[(487,165),(487,204),(481,204)],color=GREY,arrow=True)
    line(p,[(446,215),(446,230),(493,230)],color=BLUE,arrow=True)
    lab.text(369,233,'Density-ratio estimation',7.1)
    lab.put(p)
    (RUN/'NETWORK_PATH_COUNTS.json').write_text(json.dumps({'mean':n1,'classifier':n2},indent=2))
    return out

if __name__=='__main__':
    for folder in [OUT,RUN/'preview']:folder.mkdir(exist_ok=True,parents=True)
    f=factor_graph();s=system();r=receiver(f)
    records=[export(s,'system_multiframe'),export(f,'factor_graph'),export(r,'learned_receiver')]
    (RUN/'EXPORTS.json').write_text(json.dumps(records,indent=2),encoding='utf8')
    print(json.dumps(records,indent=2))
