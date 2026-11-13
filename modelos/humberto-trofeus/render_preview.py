import sys, glob, numpy as np, trimesh
from PIL import Image
def render(mesh, yaw=30, pitch=15, size=420, scale=3.2):
    pts, fi = trimesh.sample.sample_surface(mesh, 1_500_000)
    nrm = mesh.face_normals[fi]
    a, b = np.radians(yaw), np.radians(pitch)
    Rz = np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]])
    Rx = np.array([[1,0,0],[0,np.cos(b),-np.sin(b)],[0,np.sin(b),np.cos(b)]])
    M = Rx @ Rz
    p = pts @ M.T; n = nrm @ M.T
    # câmera olhando para +y; tela x->u, z->v
    u = ((p[:,0]) * scale + size/2).astype(int)
    v = ((-p[:,2] + 60) * scale + size/2).astype(int)
    depth = p[:,1]
    ok = (u>=0)&(u<size)&(v>=0)&(v<size)&(n[:,1] < 0.05)
    u,v,depth,n = u[ok],v[ok],depth[ok],n[ok]
    order = np.argsort(-depth)
    zb = np.full((size,size), np.inf); img = np.full((size,size), 245.0)
    light = np.array([-0.4,-0.8,0.5]); light/=np.linalg.norm(light)
    shade = np.clip(n@light, 0, 1)
    col = 25 + 150*shade**1.5
    img[v[order], u[order]] = col[order]
    return Image.fromarray(img.astype(np.uint8))
if __name__=='__main__':
    files = sorted(glob.glob('stl/*.stl'))
    ims = [render(trimesh.load(f)) for f in files]
    cols = min(5, len(ims)); rows = (len(ims)+cols-1)//cols
    sheet = Image.new('L', (420*cols, 420*rows), 245)
    for k, im in enumerate(ims): sheet.paste(im, ((k%cols)*420, (k//cols)*420))
    sheet.save(sys.argv[1] if len(sys.argv)>1 else 'preview.png')
