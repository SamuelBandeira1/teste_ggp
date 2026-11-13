"""Versão 5: contornos vetorizados e suavizados, simetria, leitor redesenhado em vetor, malha mais fina."""
import sys, os, numpy as np, trimesh
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.ndimage import gaussian_filter1d
from skimage import measure, morphology
from shapely.geometry import Point, Polygon, LineString, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity
import gerar_v2_cores as b2
b2.F2 = 0.05
b2.RES = 0.25
import gerar_v3_encaixe as b3
F2, RES = b2.F2, b2.RES
ICON_H = 90.0
SIMETRIA = {2}
SUAVE = 0.2            # mm: suavização do contorno

def edt_close(S, r):
    d = ndi.distance_transform_edt(~S) * F2 <= r
    return ndi.distance_transform_edt(d) * F2 > r
def edt_dilate(S, r):
    return ndi.distance_transform_edt(~S) * F2 <= r

def raster_rings(rings, shape):
    """rings em px da grade (x, z_de_cima); preenchimento par-ímpar"""
    acc = np.zeros(shape, bool)
    for r in rings:
        im = Image.new('1', (shape[1], shape[0]), 0)
        ImageDraw.Draw(im).polygon([tuple(p) for p in r], fill=1)
        acc ^= np.asarray(im)
    return acc

def tracado(i):
    x0,y0,x1,y1 = b2.BOX[i]
    g = b2.ref[y0:y1, x0:x1]
    dark = ndi.gaussian_filter(g, 0.6) < 110
    rows = np.where(dark.any(1))[0]; top = rows.min(); cols = np.where(dark.any(0))[0]
    px = ICON_H / (g.shape[0] - top)
    if (cols.max()-cols.min()+1)*px > 100: px = 100/(cols.max()-cols.min()+1)
    g = g[top:, cols.min():cols.max()+1]
    P, UP = 6, 4
    gp = np.pad(g, P, constant_values=255)
    G = np.asarray(Image.fromarray(gp.astype(np.uint8)).resize((gp.shape[1]*UP, gp.shape[0]*UP), Image.BICUBIC)).astype(float)
    G = ndi.gaussian_filter(G, 1.0)
    shape = (int(round(g.shape[0]*px/F2)), int(round(g.shape[1]*px/F2)))
    rings = []
    for c in measure.find_contours(G, 110):
        mm = (c/UP - P) * px                       # (z_de_cima, x) em mm
        seg = np.sqrt((np.diff(mm, axis=0)**2).sum(1)); L = seg.sum()
        if L < 2.0: continue
        s = np.concatenate([[0], np.cumsum(seg)]); n = max(int(L/0.1), 8)
        t = np.linspace(0, L, n, endpoint=False)
        r = np.stack([np.interp(t, s, mm[:,0]), np.interp(t, s, mm[:,1])], 1)
        r = gaussian_filter1d(r, SUAVE/0.1, axis=0, mode='wrap')
        rings.append(np.stack([r[:,1]/F2, r[:,0]/F2], 1))
    m = raster_rings(rings, shape)
    if i in SIMETRIA:
        # só o contorno externo fica simétrico; o desenho de dentro (aperto de mão) é mantido
        m = edt_close(np.pad(m, 20), 0.35)[20:-20, 20:-20]          # some com riscos finos de brilho da referência
        S = ndi.binary_fill_holes(edt_close(np.pad(m, 80), 3.0)[80:-80, 80:-80])
        cc = np.where(S.any(0))[0]; sh = int(round(shape[1]/2 - (cc.min()+cc.max())/2))
        S = np.roll(S, sh, 1); m = np.roll(m, sh, 1)
        sd = b2.sdist(S); S2 = (sd + sd[:, ::-1])/2 > 0
        m = (m | (S2 & ~S)) & S2
        borda = b2.sdist(S2) < 3.0                                     # faixa de 3 mm junto da borda: fecha riscos de brilho
        m = (m | (edt_close(np.pad(m, 40), 1.0)[40:-40, 40:-40] & borda)) & S2
    return m

# ---------- leitor (9) desenhado em vetor ----------
def bez(p0, p1, p2, n=60):
    t = np.linspace(0, 1, n)[:, None]
    return (1-t)**2*np.array(p0) + 2*(1-t)*t*np.array(p1) + t**2*np.array(p2)
def catmull(pts, n=16):
    P = np.array(pts, float); P = np.vstack([P[0], P, P[-1]]); out = []
    for k in range(1, len(P)-2):
        p0, p1, p2, p3 = P[k-1], P[k], P[k+1], P[k+2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5*((2*p1) + (-p0+p2)*t + (2*p0-5*p1+4*p2-p3)*t*t + (-p0+3*p1-3*p2+p3)*t**3))
    out.append(P[-2]); return np.array(out)
def traco(pts, w): return LineString(pts).buffer(w/2, cap_style='round', join_style='round', quad_segs=24)
def espelho(geo): return affinity.scale(geo, -1, 1, origin=(0, 0))
def suave(geo, r=0.8): return geo.buffer(-r, quad_segs=24).buffer(r, quad_segs=24)

def leitor():
    pagina = Polygon(np.vstack([bez((-34,40),(-15,44),(0,34)), [(0,6)], bez((0,6),(-15,14),(-34,12))[1:]]))
    livro = suave(unary_union([pagina, espelho(pagina)]), 1.0)
    colo = suave(Polygon([(-21,0),(21,0),(21,12),(-21,12)]), 3.5)
    cabeca = Point(0, 55).buffer(20.5, quad_segs=64)
    cr = (23, 59)
    rel = Point(*cr).buffer(17, quad_segs=64).difference(Point(*cr).buffer(12.6, quad_segs=64))
    rel = unary_union([rel, traco([cr, (cr[0], cr[1]+9.5)], 3.2), traco([cr, (cr[0]+7.5, cr[1]-4.5)], 3.2), Point(*cr).buffer(2.4)])
    U = unary_union([livro, colo, cabeca, rel])
    dentro = U.buffer(-1.1)
    seps = [cabeca.exterior.buffer(0.75).intersection(rel), livro.exterior.buffer(0.75).intersection(unary_union([cabeca, rel, colo]))]
    # páginas: lombada, borda das folhas e linhas de texto (simétricas)
    det = [traco([(0,32.6),(0,8.4)], 1.5)]
    borda = bez((-31.5,36.6),(-15,40.2),(-1.6,31.4)); det.append(traco(borda, 1.3))
    for k, off in enumerate((8.5, 13.5, 18.5)):
        ln = bez((-28,40-off),(-15,43.5-off),(-5,33.5-off)); det.append(traco(ln, 1.2))
    det = unary_union(det); det = unary_union([det, espelho(det)]).intersection(livro.buffer(-1.2))
    # rosto branco abaixo da franja (franja com três pontas, simétrica), espiando por cima do livro
    franja = catmull([(-22,56),(-12,47),(-7,52.5),(0,45.5),(7,52.5),(12,47),(22,56)], n=24)
    abaixo = Polygon(np.vstack([franja, [(22,20),(-22,20)]]))
    rosto = cabeca.buffer(-1.4, quad_segs=48).intersection(abaixo).difference(livro.buffer(0.75 + 1.1))
    olhos = unary_union([traco(bez((x-3,44.6),(x,42.4),(x+3,44.6)), 1.4) for x in (-6.5, 6.5)])
    rosto = suave(rosto, 0.5).difference(olhos)
    brancos = unary_union(seps + [det, rosto]).intersection(dentro)
    preto = U.difference(brancos)
    return preto, brancos

def vetor_mask(preto):
    minx, miny, maxx, maxy = preto.bounds
    s = min(ICON_H/(maxy - 0), 95/(maxx-minx))
    geo = affinity.scale(preto, s, s, origin=(0,0))
    minx, miny, maxx, maxy = geo.bounds
    W, H = maxx-minx, maxy
    shape = (int(round(H/F2)), int(round(W/F2)))
    rings = []
    polys = geo.geoms if isinstance(geo, MultiPolygon) else [geo]
    for p in polys:
        for r in [p.exterior] + list(p.interiors):
            xy = np.array(r.coords)
            rings.append(np.stack([(xy[:,0]-minx)/F2, (H - xy[:,1])/F2], 1))
    return raster_rings(rings, shape)

def masks(i):
    m = vetor_mask(leitor()[0]) if i == 9 else tracado(i)
    m = morphology.remove_small_objects(m, int(4/F2**2))
    filled = ndi.binary_fill_holes(m)
    holes = morphology.remove_small_objects(filled & ~m, int(0.6/F2**2))
    B = filled & ~holes
    pad = int(round(b2.EMBED/F2))+1
    z = np.zeros((pad, B.shape[1]), bool)
    B = np.vstack([B, z]); holes = np.vstack([holes, z])
    ground = np.zeros_like(B); cx = B.shape[1]/2; rb = b3.PE_W/F2
    ground[-pad:, max(0,int(cx-rb)):min(B.shape[1],int(cx+rb))] = True
    return B, holes, ground, pad

b2.masks = masks
b2.DETALHES = {}
b2.morphology.disk = lambda r: None   # não usado: fechamentos via distância abaixo

def icone(i, outdir, montado_dir):
    B, holes, ground, pad = masks(i)
    S_out = B | holes
    last = S_out[-pad-1].copy()
    for k in range(pad): B[-pad+k] |= last & ground[-pad+k]
    if i in b2.FUNDO:
        cut = int(b2.BORDA/F2)+2
        W = edt_close(np.pad(S_out, int(b2.FECHA/F2)+2), b2.FECHA)[int(b2.FECHA/F2)+2:-int(b2.FECHA/F2)-2, int(b2.FECHA/F2)+2:-int(b2.FECHA/F2)-2]
        W = ndi.binary_fill_holes(W | S_out)
        W = edt_dilate(np.pad(W, cut), b2.BORDA)
        B, holes, ground = np.pad(B, cut), np.pad(holes, cut), np.pad(ground, cut)
        W[-cut:] = False
        lw = W[-cut-pad-1].copy()
        for k in range(pad): W[-cut-pad+k] |= lw & ground[-cut-pad+k]
        W, pontes = b2.ligar(W, ground)
        W = ndi.binary_fill_holes(W | ground) & ~(ground & ~W)   # sem furinho entre a peça e o pé
        inlay, fundo = holes, W & ~B & ~holes
    else:
        inlay = b2.olho(holes) if i in b2.SO_OLHO else holes
        S = B | inlay                       # peça preta cercada de branco embutido já fica presa nele
        S2, pontes = b2.ligar(S.copy(), ground)
        B = B | (S2 & ~S)
        fundo = np.zeros_like(B)
    sdist = b2.sdist
    din = np.clip(sdist(B | inlay), 0, b2.R)
    h = b2.C + b2.R*np.sqrt(np.clip(1 - (1 - din/b2.R)**2, 0, 1))
    f = F2/RES
    sd_b, hb, sd_f, sd_i = [ndi.zoom(a, f, order=1) for a in (sdist(B), h, sdist(fundo), sdist(inlay))]
    nz, nx = sd_b.shape
    R1, BASE_H, PE_H, PE_W, PINO, TRAS = b3.R1, b3.BASE_H, b3.PE_H, b3.PE_W, b3.PINO, b3.TRAS
    nX = int(np.ceil(max(nx*RES, 2*R1+4)/RES))+4; nY = int(np.ceil(18/RES))+4
    z0 = BASE_H - PINO[2] - 1; zb = BASE_H + PE_H - b2.EMBED
    nZ = int(np.ceil((zb + nz*RES - z0)/RES))+3
    X = (np.arange(nX)-nX/2)*RES; Y = (np.arange(nY)-nY/2)*RES; Z = z0 + np.arange(nZ)*RES - RES
    def place(a, fill):
        out = np.full((nX, nZ), fill, np.float32); xo = (nX-nx)//2; zi = int(round((zb - Z[0])/RES))
        out[xo:xo+nx, zi:zi+nz] = a[::-1].T; return out
    SDb, HB, SDf, SDi = place(sd_b,-5), place(hb,0), place(sd_f,-5), place(sd_i,-5)
    Yb = Y[None,:,None]; Xb = X[:,None,None]; Zb = Z[None,None,:]
    tras = TRAS - Yb
    Fb = np.minimum(np.minimum(SDb[:,None,:], HB[:,None,:] + Yb), tras)
    o = 0*Xb + 0*Yb + 0*Zb
    pe = np.minimum.reduce([PE_W - np.abs(Xb) + o, Zb - BASE_H + o, BASE_H + PE_H - Zb + o, TRAS - np.abs(Yb) + o])
    pe = np.minimum(pe, (PE_W - np.abs(Xb)) + (BASE_H + PE_H - Zb) - 1.0 + o)          # chanfro nas quinas de cima do pé
    pino = np.minimum.reduce([PINO[0] - np.abs(Xb) + o, Zb - (BASE_H - PINO[2]) + o, BASE_H + 0.5 - Zb + o, Yb - (TRAS - PINO[1]) + o, tras + o])
    pino = np.minimum(pino, (Zb - (BASE_H - PINO[2])) + (PINO[0] - np.abs(Xb)) - 1.0 + o)
    Fpreto = np.maximum.reduce([Fb, pe, pino])
    Fw = np.maximum(np.minimum(np.minimum(SDf[:,None,:], Yb - b3.FUNDO_FRENTE), tras),
                    np.minimum(np.minimum(SDi[:,None,:], b2.HW_INLAY + Yb), tras))
    Fw = np.minimum(Fw, -Fpreto)
    meshes = {k: m for k, m in (('preto', b3.malha(Fpreto, X, Y, Z)), ('branco', b3.malha(Fw, X, Y, Z))) if m is not None}
    nome = f'trofeu-{i}-{b2.NOME[i]}'
    for k, m in meshes.items(): m.export(os.path.join(montado_dir, f'{nome}-{k}.stl'))
    rot = np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,TRAS],[0,0,0,1]], float)
    dei = {k: m.copy().apply_transform(rot) for k, m in meshes.items()}
    zmin = min(m.bounds[0][2] for m in dei.values())
    for m in dei.values(): m.apply_translation([0, 0, -zmin])
    b3.salvar(dei, os.path.join(outdir, nome + '.3mf'))
    print(f"{i} {b2.NOME[i]:<24} pontes {pontes} " + ' '.join(f"{k}:{m.volume/1000:.0f}cm3 ok={m.is_watertight} faces={len(m.faces)}" for k, m in dei.items()), flush=True)

if __name__ == '__main__':
    out, mont = sys.argv[1], sys.argv[1] + '_montado'
    os.makedirs(out, exist_ok=True); os.makedirs(mont, exist_ok=True)
    ids = [int(a) for a in sys.argv[2:]]
    if not ids: b3.base(out, mont); ids = list(b2.BOX)
    for i in ids: icone(i, out, mont)
