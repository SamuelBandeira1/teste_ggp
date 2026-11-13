"""Versão 3: ícone impresso deitado + base padrão com encaixe."""
import sys, os, numpy as np, trimesh
from scipy import ndimage as ndi
from skimage import measure
import gerar_v2_cores as b2

BASE_H, R1, R2, STEP = 25.0, 31.0, 28.0, 20.0
PE_H, PE_W = 5.0, 25.0                 # pé do ícone: 50 x 14 x 5 mm, apoiado no topo da base
PINO = (10.0, 8.0, 8.0)                # meia-largura x, espessura, altura do pino
FOLGA = 0.2
TRAS = 7.0                             # costas retas do ícone (lado que vai na mesa)
FUNDO_FRENTE = 1.0                     # fundo branco ocupa de y=1 até as costas (6 mm)
b2.ICON_H = 120.0 - BASE_H - PE_H      # 90 mm de ícone
b2.EMBED = 1.5
RES = b2.RES

def malha(F, X, Y, Z):
    F = ndi.gaussian_filter(F.astype(np.float32), 0.9)
    F = np.pad(F, 1, constant_values=-1)
    if F.max() <= 0: return None
    v, fc, _, _ = measure.marching_cubes(F, 0, spacing=(RES,)*3)
    v -= RES; v[:,0] += X[0]; v[:,1] += Y[0]; v[:,2] += Z[0]
    m = trimesh.Trimesh(v, fc[:, ::-1], process=True)
    m = trimesh.util.concatenate([p for p in m.split(only_watertight=False) if len(p.faces) > 200])
    if m.volume < 0: m.invert()
    return m

def salvar(meshes, path):
    sc = trimesh.Scene()
    for nome, m in meshes.items():
        m.visual.face_colors = [20,20,20,255] if nome == 'preto' else [245,245,245,255]
        sc.add_geometry(m, node_name=nome, geom_name=nome)
    sc.export(path)
    for nome, m in meshes.items(): m.export(path.replace('.3mf', f'-{nome}.stl'))

def icone(i, outdir, montado_dir):
    B, holes, ground, pad = b2.masks(i)
    S_out = B | holes
    last = S_out[-pad-1].copy()
    for k in range(pad): B[-pad+k] |= last & ground[-pad+k]
    if i in b2.FUNDO:
        F2 = b2.F2; cut = int(b2.BORDA/F2)+2; fc = int(b2.FECHA/F2)
        W = ndi.binary_closing(np.pad(S_out, fc), b2.morphology.disk(fc))[fc:-fc, fc:-fc]
        W = ndi.binary_fill_holes(W | S_out)
        W = ndi.binary_dilation(np.pad(W, cut), b2.morphology.disk(int(b2.BORDA/F2)))
        B, holes, ground = np.pad(B, cut), np.pad(holes, cut), np.pad(ground, cut)
        W[-cut:] = False
        lw = W[-cut-pad-1].copy()
        for k in range(pad): W[-cut-pad+k] |= lw & ground[-cut-pad+k]
        W, pontes = b2.ligar(W, ground)
        inlay, fundo, recesso = holes, W & ~B & ~holes, np.zeros_like(holes)
    else:
        inlay = b2.olho(holes) if i in b2.SO_OLHO else holes
        recesso = np.zeros_like(holes)          # camaleão: o resto fica vazado, como na foto
        B, pontes = b2.ligar(B, ground)
        fundo = np.zeros_like(B)
    sdist = b2.sdist
    din = np.clip(sdist(B | holes), 0, b2.R)
    h = b2.C + b2.R*np.sqrt(np.clip(1 - (1 - din/b2.R)**2, 0, 1))
    h = h - b2.D*np.clip(sdist(recesso)/0.4 + 0.5, 0, 1)
    f = b2.F2/RES
    sd_b, hb, sd_f, sd_i = [ndi.zoom(a, f, order=1) for a in (sdist(B | recesso), h, sdist(fundo), sdist(inlay))]
    nz, nx = sd_b.shape
    nX = int(np.ceil(max(nx*RES, 2*R1+4)/RES))+4; nY = int(np.ceil(18/RES))+4
    z0 = BASE_H - PINO[2] - 1
    zb = BASE_H + PE_H - b2.EMBED
    nZ = int(np.ceil((zb + nz*RES - z0)/RES))+3
    X = (np.arange(nX)-nX/2)*RES; Y = (np.arange(nY)-nY/2)*RES; Z = z0 + np.arange(nZ)*RES - RES
    def place(a, fill):
        out = np.full((nX, nZ), fill, np.float32); xo = (nX-nx)//2; zi = int(round((zb - Z[0])/RES))
        out[xo:xo+nx, zi:zi+nz] = a[::-1].T; return out
    SDb, HB, SDf, SDi = place(sd_b,-5), place(hb,0), place(sd_f,-5), place(sd_i,-5)
    Yb = Y[None,:,None]; Xb = X[:,None,None]; Zb = Z[None,None,:]
    tras = TRAS - Yb
    Fb = np.minimum(np.minimum(SDb[:,None,:], HB[:,None,:] + Yb), tras)
    pe = np.minimum.reduce([PE_W - np.abs(Xb) + 0*Yb + 0*Zb, Zb - BASE_H + 0*Xb + 0*Yb, BASE_H + PE_H - Zb + 0*Xb + 0*Yb, TRAS - np.abs(Yb) + 0*Xb + 0*Zb])
    pino = np.minimum.reduce([PINO[0] - np.abs(Xb) + 0*Yb + 0*Zb, Zb - (BASE_H - PINO[2]) + 0*Xb + 0*Yb, BASE_H + 0.5 - Zb + 0*Xb + 0*Yb,
                              Yb - (TRAS - PINO[1]) + 0*Xb + 0*Zb, tras + 0*Xb + 0*Zb])
    pino = np.minimum(pino, (Zb - (BASE_H - PINO[2])) + (PINO[0] - np.abs(Xb)) - 1.0 + 0*Yb)   # chanfro de 1 mm na ponta
    Fpreto = np.maximum.reduce([Fb, pe, pino])
    Fw = np.maximum(np.minimum(np.minimum(SDf[:,None,:], Yb - FUNDO_FRENTE), tras),
                    np.minimum(np.minimum(SDi[:,None,:], b2.HW_INLAY + Yb), tras))
    Fw = np.minimum(Fw, -Fpreto)
    meshes = {k: m for k, m in (('preto', malha(Fpreto, X, Y, Z)), ('branco', malha(Fw, X, Y, Z))) if m is not None}
    nome = f'trofeu-{i}-{b2.NOME[i]}'
    for k, m in meshes.items(): m.export(os.path.join(montado_dir, f'{nome}-{k}.stl'))
    # deitado: costas (y = TRAS) na mesa
    rot = np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,TRAS],[0,0,0,1]], float)
    dei = {k: m.copy().apply_transform(rot) for k, m in meshes.items()}
    zmin = min(m.bounds[0][2] for m in dei.values())
    for m in dei.values(): m.apply_translation([0, 0, -zmin])
    salvar(dei, os.path.join(outdir, nome + '.3mf'))
    p = dei['preto']
    print(f"{i} {b2.NOME[i]:<24} pontes {pontes}  " + '  '.join(f"{k}: {m.volume/1000:.0f} cm3 ok={m.is_watertight}" for k, m in dei.items())
          + f"  deitado {p.extents[0]:.0f}x{p.extents[1]:.0f}x{p.extents[2]:.0f} mm")

def base(outdir, montado_dir):
    nX = nY = int(np.ceil((2*R1+4)/RES))+4; nZ = int(np.ceil((BASE_H+2)/RES))+2
    X = (np.arange(nX)-nX/2)*RES; Y = (np.arange(nY)-nY/2)*RES; Z = np.arange(nZ)*RES - RES
    rho = np.sqrt(X[:,None]**2 + Y[None,:]**2)[:,:,None]; Zc = Z[None,None,:]
    cyl1 = np.minimum(np.minimum(R1 - rho - np.clip(1.0 - Zc, 0, None), Zc), STEP - Zc)
    cyl2 = np.minimum(np.minimum(R2 - rho - np.clip(Zc - (BASE_H-1.0), 0, None), Zc - STEP + 0.5), BASE_H - Zc)
    F = np.maximum(cyl1, cyl2)
    F = np.minimum(F, -np.minimum(b2.NFC_R - rho, b2.NFC_H - Zc))
    Xb = X[:,None,None]; Yb = Y[None,:,None]
    enc = np.minimum.reduce([PINO[0]+FOLGA - np.abs(Xb) + 0*Yb + 0*Zc, Zc - (BASE_H - PINO[2] - 0.5) + 0*Xb + 0*Yb,
                             Yb - (TRAS - PINO[1] - FOLGA) + 0*Xb + 0*Zc, TRAS + FOLGA - Yb + 0*Xb + 0*Zc])
    F = np.minimum(F, -enc)
    # ano na frente
    arc = 60.0
    tm, sc, th, tw = b2.texto_mask(arc, STEP)
    sdt = (ndi.distance_transform_edt(tm) - ndi.distance_transform_edt(~tm)) / sc
    s = R1*np.arctan2(X[:,None], -Y[None,:]); si = (s + arc/2)*sc; zi = (STEP - Z)*sc
    sh = (nX, nY, nZ)
    SI = np.broadcast_to(si[:,:,None], sh); ZI = np.broadcast_to(zi[None,None,:], sh)
    sel = np.broadcast_to((np.abs(s) < arc/2)[:,:,None] & (Zc < STEP) & (Zc > 0) & (Yb < 0) & (rho > R1 - 3), sh)
    T = np.full(sh, -5.0, np.float32)
    T[sel] = ndi.map_coordinates(sdt, [ZI[sel], SI[sel]], order=1, mode='constant', cval=-5)
    Ft = np.minimum(np.minimum(T, rho - (R1 - b2.TXT_D)), F)
    F = np.minimum(F, -Ft)
    meshes = {'preto': malha(F, X, Y, Z), 'branco': malha(Ft, X, Y, Z)}
    for k, m in meshes.items(): m.export(os.path.join(montado_dir, f'base-{k}.stl'))
    salvar(meshes, os.path.join(outdir, 'base-padrao-2026.3mf'))
    print('base', '  '.join(f"{k}: {m.volume/1000:.0f} cm3 ok={m.is_watertight}" for k, m in meshes.items()))

if __name__ == '__main__':
    out, mont = sys.argv[1], sys.argv[1] + '_montado'
    os.makedirs(out, exist_ok=True); os.makedirs(mont, exist_ok=True)
    ids = [int(a) for a in sys.argv[2:]]
    if not ids: base(out, mont); ids = list(b2.BOX)
    for i in ids: icone(i, out, mont)
