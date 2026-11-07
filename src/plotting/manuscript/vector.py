"""Vector primitives shared by the three approved method figures."""
from pathlib import Path
import io
import re
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pymupdf as fitz
from workspace import ROOT
REF = ROOT/'reference/literature'
GREY = (.47,)*3

def configure():
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

def copy_paths(source, page, clip, target, mappings=(), path_filter=None):
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
        if path_filter is not None and not path_filter(d):continue
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
