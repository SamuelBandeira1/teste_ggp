import sys; sys.path.insert(0,'.')
import numpy as np
from PIL import Image
import zoom2d as z
i=int(sys.argv[1]); x0,x1,y0,y1=map(float,sys.argv[3:7]); k=float(sys.argv[7])
P,B=z.geo(i); W,H=int((x1-x0)*k),int((y1-y0)*k)
img=np.full((H,W,3),(175,190,205),np.uint8); img[z.mask(B,x0,y1,k,W,H)]=255; img[z.mask(P,x0,y1,k,W,H)]=20
import camadas as c
# referência no mesmo recorte
cx,ap=c.CX[i],c.APOIO[i]; S=c.S
r=c.REF[int(ap-y1/S):int(ap-y0/S), int(cx+x0/S):int(cx+x1/S)].astype(np.uint8)
ref=Image.fromarray(r).convert('RGB').resize((W,H))
s=Image.new('RGB',(W*2+10,H),'white'); s.paste(ref,(0,0)); s.paste(Image.fromarray(img),(W+10,0)); s.save(sys.argv[2])
