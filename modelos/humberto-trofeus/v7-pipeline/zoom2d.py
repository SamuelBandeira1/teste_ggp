import sys; sys.path.insert(0,'.')
import camadas as c, numpy as np, ajustes8 as a, vetor
from PIL import Image, ImageDraw
def geo(i):
    H=int(open(f'i{i}_altura.txt').read())
    P=vetor.ler(f'i{i}_preto.svg',H).buffer(0); B=vetor.ler(f'i{i}_branco.svg',H).buffer(0)
    return a.AJUSTES[i](P,B,None,a.conv(i,c.APOIO[i]))[:2]
def mask(g, x0, y1, k, W, Hh):
    acc=np.zeros((Hh,W),bool)
    for q in (g.geoms if hasattr(g,'geoms') else [g]):
        if q.is_empty or q.geom_type!='Polygon': continue
        for r in [q.exterior]+list(q.interiors):
            im=Image.new('1',(W,Hh),0); ImageDraw.Draw(im).polygon([((x-x0)*k, (y1-y)*k) for x,y in r.coords],fill=1); acc^=np.asarray(im)
    return acc
def quadros(i, P, B, nome, k=14):
    minx,miny,maxx,maxy = P.union(B).bounds
    xm, ym = (minx+maxx)/2, (miny+maxy)/2
    tiles=[]
    for (x0,x1) in ((minx-1,xm+3),(xm-3,maxx+1)):
        for (y0,y1) in ((ym-3,maxy+1),(miny-1,ym+3)):
            W,Hh=int((x1-x0)*k),int((y1-y0)*k)
            img=np.full((Hh,W,3),(175,190,205),np.uint8)
            img[mask(B,x0,y1,k,W,Hh)]=255; img[mask(P,x0,y1,k,W,Hh)]=20
            # grade de 5 mm
            im=Image.fromarray(img); d=ImageDraw.Draw(im)
            for gx in np.arange(np.ceil(x0/5)*5, x1, 5): d.line([((gx-x0)*k,0),((gx-x0)*k,Hh)], fill=(255,120,120))
            for gy in np.arange(np.ceil(y0/5)*5, y1, 5): d.line([(0,(y1-gy)*k),(W,(y1-gy)*k)], fill=(255,120,120))
            tiles.append(im)
    w=max(t.width for t in tiles); h=max(t.height for t in tiles)
    s=Image.new('RGB',(2*w,2*h),'white')
    s.paste(tiles[0],(0,0)); s.paste(tiles[1],(0,h)); s.paste(tiles[2],(w,0)); s.paste(tiles[3],(w,h))
    s.save(nome)
if __name__=='__main__':
    i=int(sys.argv[1]); P,B=geo(i); quadros(i,P,B,sys.argv[2])
