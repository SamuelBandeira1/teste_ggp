"""v6: desenho em vetor (desenho6.py), peça direto na base, base cilíndrica centrada como na referência."""
import sys, os, numpy as np, trimesh
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from shapely import affinity
from shapely.geometry import box
from shapely.ops import unary_union
import gerar_v2_cores as b2
b2.F2 = 0.05; b2.RES = 0.25
import gerar_v3_encaixe as b3
import desenho_v6 as d6
F2, RES = b2.F2, b2.RES
S = 0.352                      # mm por px da referência
BASE_H, R_BASE, FILETE = 25.0, 33.0, 2.0
PINO = (15.0, 8.0, 8.0)        # meia-largura, espessura, profundidade
FOLGA = 0.2
TRAS = 7.0
CORTE = 1.0                    # mm cortados embaixo para o apoio ficar reto
NOME = b2.NOME

def raster(geo, minx, maxz, shape):
    acc = np.zeros(shape, bool)
    gs = geo.geoms if hasattr(geo, 'geoms') else [geo]
    for p in gs:
        if p.is_empty or p.geom_type != 'Polygon': continue
        for r in [p.exterior] + list(p.interiors):
            xy = np.array(r.coords)
            im = Image.new('1', (shape[1], shape[0]), 0)
            ImageDraw.Draw(im).polygon([((x-minx)/F2, (maxz-z)/F2) for x, z in xy], fill=1)
            acc ^= np.asarray(im)
    return acc

def close_(S_, r):
    d = ndi.distance_transform_edt(~S_)*F2 <= r
    return ndi.distance_transform_edt(d)*F2 > r

def icone(i, outdir, mont):
    preto, branco = d6.DESENHOS[i]()
    vmin = min(g.bounds[1] for g in [preto])
    tr = lambda g: affinity.scale(affinity.translate(g, 0, -vmin), S, S, origin=(0, 0))
    preto, branco = tr(preto), tr(branco)
    preto = preto.intersection(box(-500, CORTE, 500, 500)); branco = branco.intersection(box(-500, CORTE, 500, 500))
    preto, branco = affinity.translate(preto, 0, -CORTE), affinity.translate(branco, 0, -CORTE)
    allg = unary_union([preto, branco])
    minx, minz, maxx, maxz = allg.bounds
    m = 4.0; minx -= m; maxx += m; maxz += m; minz = -0.5
    shape = (int(np.ceil((maxz-minz)/F2)), int(np.ceil((maxx-minx)/F2)))
    B = raster(preto, minx, maxz, shape); Wx = raster(branco, minx, maxz, shape) & ~B
    zrow = maxz - np.arange(shape[0])*F2            # z de cada linha
    xcol = minx + np.arange(shape[1])*F2
    ground = (zrow[:, None] < 0.3) & (np.abs(xcol)[None, :] < PINO[0] - 1)
    contato = (B & ground).sum()*F2*F2
    holes = ndi.binary_fill_holes(B) & ~B
    if i in d6.FUNDO:
        U = B | Wx | holes
        W = ndi.binary_fill_holes(close_(U, 6.0) | U)
        W = ndi.distance_transform_edt(~W)*F2 <= 2.5
        W &= (zrow[:, None] > 1.5)                     # o branco não encosta na base
        inlay = (holes | Wx) & ~B
        fundo = W & ~B & ~inlay
    else:
        inlay = (Wx if i == 7 else (holes | Wx)) & ~B
        fundo = np.zeros_like(B)
    Sx = B | inlay | fundo
    S2, pontes = b2.ligar(Sx.copy(), ground)
    B = B | (S2 & ~Sx)
    sd = b2.sdist
    din = np.clip(sd(B | inlay), 0, b2.R)
    h = b2.C + b2.R*np.sqrt(np.clip(1 - (1 - din/b2.R)**2, 0, 1))
    f = F2/RES
    sd_b, hb, sd_f, sd_i = [ndi.zoom(a, f, order=1) for a in (sd(B), h, sd(fundo), sd(inlay))]
    nz, nx = sd_b.shape
    X = minx + np.arange(nx)*RES
    Y = (np.arange(int(np.ceil(18/RES))+4) - (int(np.ceil(18/RES))+4)/2)*RES
    Zi = BASE_H + (maxz - np.arange(nz)*RES)          # z absoluto de cada linha da grade 2D
    z0 = BASE_H - PINO[2] - 1.0
    Z = np.arange(z0, Zi.max() + 1.0, RES)
    # reamostra as grades 2D (linhas = z decrescente) para Z crescente
    def para_Z(a, fill):
        idx = (Zi[0] - Z)/RES
        out = np.full((len(X), len(Z)), fill, np.float32)
        ok = (idx >= 0) & (idx <= nz-1)
        out[:, ok] = ndi.map_coordinates(a, [idx[ok][None, :].repeat(len(X), 0), np.arange(len(X))[:, None].repeat(ok.sum(), 1)], order=1)
        return out
    SDb, HB, SDf, SDi = para_Z(sd_b, -5), para_Z(hb, 0), para_Z(sd_f, -5), para_Z(sd_i, -5)
    Xb = X[:, None, None]; Yb = Y[None, :, None]; Zb = Z[None, None, :]; o = 0*Xb + 0*Yb + 0*Zb
    tras = TRAS - Yb
    Fb = np.minimum(np.minimum(SDb[:, None, :], HB[:, None, :] + Yb), tras)
    Fb = np.minimum(Fb, Zb - BASE_H + 0*Xb + 0*Yb)                     # nada abaixo do topo da base, só o pino
    pino = np.minimum.reduce([PINO[0] - np.abs(Xb) + o, Zb - (BASE_H - PINO[2]) + o, BASE_H + 0.6 - Zb + o,
                              Yb - (TRAS - PINO[1]) + o, tras + o])
    pino = np.minimum(pino, (Zb - (BASE_H - PINO[2])) + (PINO[0] - np.abs(Xb)) - 1.0 + o)
    Fpreto = np.maximum(Fb, pino)
    Fw = np.maximum(np.minimum(np.minimum(SDf[:, None, :], Yb - b3.FUNDO_FRENTE), tras),
                    np.minimum(np.minimum(SDi[:, None, :], b2.HW_INLAY + Yb), tras))
    Fw = np.minimum(np.minimum(Fw, -Fpreto), Zb - BASE_H + 0*Xb + 0*Yb)
    meshes = {k: g for k, g in (('preto', b3.malha(Fpreto, X, Y, Z)), ('branco', b3.malha(Fw, X, Y, Z))) if g is not None}
    nome = f'trofeu-{i}-{NOME[i]}'
    for k, g in meshes.items(): g.export(os.path.join(mont, f'{nome}-{k}.stl'))
    rotm = np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,TRAS],[0,0,0,1]], float)
    dei = {k: g.copy().apply_transform(rotm) for k, g in meshes.items()}
    zmin = min(g.bounds[0][2] for g in dei.values())
    for g in dei.values(): g.apply_translation([0, 0, -zmin])
    b3.salvar(dei, os.path.join(outdir, nome + '.3mf'))
    ext = meshes['preto'].bounds
    print(f"{i} {NOME[i]:<24} contato_no_pino {contato:.0f} mm2  pontes {pontes}  altura {ext[1][2]:.0f} mm  largura {ext[1][0]-ext[0][0]:.0f} mm  "
          + ' '.join(f"{k}:{g.volume/1000:.0f}cm3 ok={g.is_watertight}" for k, g in dei.items()), flush=True)

def base(outdir, mont):
    n = int(np.ceil((2*R_BASE+4)/RES))+4
    X = (np.arange(n)-n/2)*RES; Y = X.copy(); Z = np.arange(-RES, BASE_H+1, RES)
    rho = np.sqrt(X[:, None]**2 + Y[None, :]**2)[:, :, None]; Zc = Z[None, None, :]
    # cilindro com filete de 2 mm em cima e chanfro de 1 mm embaixo
    dz = np.clip(Zc - (BASE_H - FILETE), 0, None); dr = np.clip(rho - (R_BASE - FILETE), 0, None)
    topo = FILETE - np.sqrt(dz**2 + dr**2)
    lado = np.minimum(R_BASE - rho, BASE_H - Zc)
    F = np.where((dz > 0) & (dr > 0), topo, lado)
    F = np.minimum(F, Zc + np.minimum(0, R_BASE - 1.0 - rho + Zc) * 0 + 0)
    F = np.minimum(F, (R_BASE - rho) + Zc - 1.0)          # chanfro embaixo
    F = np.minimum(F, Zc)
    F = np.minimum(F, -np.minimum(b2.NFC_R - rho, b2.NFC_H - Zc))
    Xb = X[:, None, None]; Yb = Y[None, :, None]
    enc = np.minimum.reduce([PINO[0]+FOLGA - np.abs(Xb) + 0*Yb + 0*Zc, Zc - (BASE_H - PINO[2] - 0.5) + 0*Xb + 0*Yb,
                             Yb - (TRAS - PINO[1] - FOLGA) + 0*Xb + 0*Zc, TRAS + FOLGA - Yb + 0*Xb + 0*Zc])
    F = np.minimum(F, -enc)
    arc = 64.0; ALT = BASE_H - FILETE
    tm, sc, th, tw = b2.texto_mask(arc, ALT)
    sdt = (ndi.distance_transform_edt(tm) - ndi.distance_transform_edt(~tm))/sc
    s = R_BASE*np.arctan2(X[:, None], -Y[None, :]); si = (s + arc/2)*sc; zi = (ALT - Z)*sc
    sh = F.shape
    SI = np.broadcast_to(si[:, :, None], sh); ZI = np.broadcast_to(zi[None, None, :], sh)
    sel = np.broadcast_to((np.abs(s) < arc/2)[:, :, None] & (Zc < ALT) & (Zc > 1) & (Yb < 0) & (rho > R_BASE - 3), sh)
    Tt = np.full(sh, -5.0, np.float32)
    Tt[sel] = ndi.map_coordinates(sdt, [ZI[sel], SI[sel]], order=1, mode='constant', cval=-5)
    Ft = np.minimum(np.minimum(Tt, rho - (R_BASE - b2.TXT_D)), F)
    F = np.minimum(F, -Ft)
    meshes = {'preto': b3.malha(F, X, Y, Z), 'branco': b3.malha(Ft, X, Y, Z)}
    for k, g in meshes.items(): g.export(os.path.join(mont, f'base-{k}.stl'))
    b3.salvar(meshes, os.path.join(outdir, 'base-padrao-2026.3mf'))
    print('base', ' '.join(f"{k}:{g.volume/1000:.0f}cm3 ok={g.is_watertight}" for k, g in meshes.items()))

if __name__ == '__main__':
    out, mont = sys.argv[1], sys.argv[1] + '_montado'
    os.makedirs(out, exist_ok=True); os.makedirs(mont, exist_ok=True)
    ids = [int(a) for a in sys.argv[2:]]
    if not ids: base(out, mont); ids = list(range(1, 10))
    for i in ids: icone(i, out, mont)
