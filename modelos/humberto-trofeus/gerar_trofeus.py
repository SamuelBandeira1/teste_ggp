import sys, warnings, numpy as np, trimesh
warnings.filterwarnings('ignore')
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure, morphology, draw

ref = np.asarray(Image.open('../ref_crop.png').convert('L')).astype(float)
BOX = {1:(70,90,232,262),2:(240,95,390,262),3:(400,95,556,264),4:(575,88,720,266),5:(740,95,875,262),
       6:(90,378,242,540),7:(265,380,425,542),8:(462,380,632,540),9:(668,372,842,542)}
NOME = {1:'engrenagem-codigo',2:'escudo-aperto-de-mao',3:'formatura-anime',4:'sol-calculadora-grafico',
        5:'cafe-oculos',6:'capacete-bandeira',7:'camaleao',8:'haltere-folha-oculos',9:'leitura-relogio'}
# medidas em mm
ALTURA, BASE_H, BASE_R1, BASE_R2, BASE_STEP = 120.0, 25.0, 31.0, 28.0, 20.0
ICON_H = ALTURA - BASE_H          # 95 mm de ícone acima da base
MAX_W = 100.0
C, R, D = 4.0, 3.0, 2.0           # meia-espessura do núcleo, raio do arredondado, profundidade da gravação
EMBED = 1.5
NFC_R, NFC_H = 13.25, 1.0
F2, RES = 0.1, 0.3                # grade 2D fina e grade 3D
DECIM = int(__import__("os").environ.get("DECIM", "0"))

def build(i, out):
    x0,y0,x1,y1 = BOX[i]
    g = ref[y0:y1, x0:x1]
    dark = ndi.gaussian_filter(g,0.6) < 110
    rows = np.where(dark.any(1))[0]; top = rows.min()
    cols = np.where(dark.any(0))[0]
    px = ICON_H / (g.shape[0] - top)                      # mm por pixel original
    if (cols.max()-cols.min()+1)*px > MAX_W: px = MAX_W/(cols.max()-cols.min()+1)
    g = g[top:, cols.min():cols.max()+1]
    Hmm, Wmm = g.shape[0]*px, g.shape[1]*px
    n_z, n_x = int(round(Hmm/F2)), int(round(Wmm/F2))
    gi = np.asarray(Image.fromarray(g.astype(np.uint8)).resize((n_x,n_z), Image.BICUBIC)).astype(float)
    gi = ndi.gaussian_filter(gi, 0.12*px/F2)
    m = gi < 110
    m = morphology.remove_small_objects(m, int(4/F2**2))
    # buracos: brancos fechados dentro do contorno
    filled = ndi.binary_fill_holes(m)
    holes = filled & ~m
    holes = morphology.remove_small_objects(holes, int(1.0/F2**2))
    m = filled & ~holes
    sil = m | holes                                       # contorno externo
    # pontes: tudo ligado à base
    pad = int(round(EMBED/F2))+1
    sil = np.vstack([sil, np.zeros((pad, n_x), bool)])
    cx = n_x/2; rbase = BASE_R2/F2*0.9
    ground = np.zeros_like(sil); ground[-pad:, max(0,int(cx-rbase)):min(n_x,int(cx+rbase))] = True
    # estende a última linha do ícone para dentro da base
    lastrow = sil[-pad-1].copy()
    for k in range(pad): sil[-pad+k] |= lastrow & ground[-pad+k]
    bw = int(round(3.0/F2))
    pontes = 0
    while True:
        lab, n = ndi.label(sil | ground, np.ones((3,3)))
        gl = lab[ground].max()
        main = lab == gl
        others = [k for k in range(1, n+1) if k != gl]
        if not others: break
        dt, (iz, ix) = ndi.distance_transform_edt(~main, return_indices=True)
        best = None
        for k in others:
            comp = lab == k
            d = np.where(comp, dt, np.inf); a = np.unravel_index(np.argmin(d), d.shape)
            if best is None or d[a] < best[0]: best = (d[a], a, (iz[a], ix[a]))
        _, (az, ax), (bz, bx) = best
        rr, cc = draw.line(int(az), int(ax), int(bz), int(bx))
        line = np.zeros_like(sil); line[rr, cc] = True
        sil |= ndi.binary_dilation(line, iterations=bw//2)
        pontes += 1
    holes = np.vstack([holes, np.zeros((pad, n_x), bool)]) & sil
    # distâncias em mm
    sd = (ndi.distance_transform_edt(sil) - ndi.distance_transform_edt(~sil)) * F2
    rd = (ndi.distance_transform_edt(holes) - ndi.distance_transform_edt(~holes)) * F2
    din = np.clip(sd, 0, R)
    h = C + R*np.sqrt(np.clip(1 - (1 - din/R)**2, 0, 1))
    h = h - D*np.clip(rd/0.4 + 0.5, 0, 1)
    # reamostra para a grade 3D
    f = F2/RES
    sd3 = ndi.zoom(sd, f, order=1); h3 = ndi.zoom(h, f, order=1)
    nz, nx = sd3.shape
    Wtot = max(nx*RES, 2*BASE_R1+4); nX = int(np.ceil(Wtot/RES))+4
    nY = int(np.ceil((2*BASE_R1+4)/RES))+4
    z_icon_bottom = BASE_H - EMBED
    nZ = int(np.ceil((z_icon_bottom + nz*RES)/RES))+3
    X = (np.arange(nX) - nX/2)*RES; Y = (np.arange(nY) - nY/2)*RES; Z = np.arange(nZ)*RES - RES
    # campo do ícone em (x,z): linha k do sd3 (k=0 topo) -> z = z_icon_bottom + (nz-1-k)*RES
    SD = np.full((nX, nZ), -5.0); HH = np.zeros((nX, nZ))
    xo = (nX - nx)//2
    zi = ((z_icon_bottom - Z[0])/RES)
    zi = int(round(zi))
    SD[xo:xo+nx, zi:zi+nz] = sd3[::-1].T; HH[xo:xo+nx, zi:zi+nz] = h3[::-1].T
    F = np.minimum(SD[:, None, :], HH[:, None, :] - np.abs(Y)[None, :, None]).astype(np.float32)
    rho = np.sqrt(X[:, None]**2 + Y[None, :]**2)[:, :, None]
    Zb = Z[None, None, :]
    cyl1 = np.minimum(np.minimum(BASE_R1 - rho - np.clip(1.0 - Zb, 0, None), Zb), BASE_STEP - Zb)   # chanfro de 1 mm embaixo
    cyl2 = np.minimum(np.minimum(BASE_R2 - rho - np.clip(Zb - (BASE_H-1.0), 0, None), Zb - BASE_STEP + 0.5), BASE_H - Zb)
    base = np.maximum(cyl1, cyl2)
    nfc = np.minimum(NFC_R - rho, NFC_H - Zb)               # rebaixo da tag por baixo
    base = np.minimum(base, -nfc)
    F = np.maximum(F, base.astype(np.float32))
    F = ndi.gaussian_filter(F, 0.9)
    F = np.pad(F, 1, constant_values=-1)
    v, fcs, _, _ = measure.marching_cubes(F, 0, spacing=(RES,)*3)
    v -= RES; v[:, 0] += X[0]; v[:, 1] += Y[0]; v[:, 2] += Z[0]
    mesh = trimesh.Trimesh(v[:, [0,1,2]], fcs[:, ::-1], process=True)
    mesh = max(mesh.split(only_watertight=False), key=lambda b: len(b.faces))
    if mesh.volume < 0: mesh.invert()
    print("antes", len(mesh.faces), mesh.is_watertight)
    if DECIM: mesh = mesh.simplify_quadric_decimation(face_count=DECIM)
    trimesh.repair.fix_normals(mesh)
    mesh.export(out); mesh.export(out.replace('.stl','.3mf'))
    ext = mesh.extents
    print(f"{i} {NOME[i]:<26} {ext[0]:.1f}x{ext[1]:.1f}x{ext[2]:.1f} mm  vol {mesh.volume/1000:.1f} cm3  area {mesh.area/100:.0f} cm2  pontes {pontes}  estanque {mesh.is_watertight}")
    return mesh

if __name__ == '__main__':
    import os; os.makedirs('stl', exist_ok=True)
    ids = [int(a) for a in sys.argv[1:]] or list(BOX)
    for i in ids: build(i, f'stl/trofeu-{i}-{NOME[i]}.stl')
