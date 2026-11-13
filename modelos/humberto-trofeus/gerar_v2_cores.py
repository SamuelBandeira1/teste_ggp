import sys, os, warnings, numpy as np, trimesh
warnings.filterwarnings('ignore')
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
from skimage import measure, morphology, draw

HERE = os.path.dirname(os.path.abspath(__file__))
ref = np.asarray(Image.open(os.path.join(HERE, '../ref_crop.png')).convert('L')).astype(float)
BOX = {1:(70,90,232,262),2:(240,95,390,262),3:(400,95,556,264),4:(575,88,720,266),5:(740,95,875,262),
       6:(90,378,242,540),7:(265,380,425,542),8:(462,380,632,540),9:(668,372,842,542)}
NOME = {1:'engrenagem-codigo',2:'escudo-aperto-de-mao',3:'formatura-anime',4:'sol-calculadora-grafico',
        5:'cafe-oculos',6:'capacete-bandeira',7:'camaleao',8:'haltere-folha-oculos',9:'leitura-relogio'}
# como cada troféu usa o branco
FUNDO = {1,2,3,4,5,8}        # fundo + borda brancos segurando as partes soltas
SO_OLHO = {7}                # camaleão: todo preto, só o olho branco
# 6 e 9: pretos com pontes; detalhes brancos embutidos

ALTURA, BASE_H, BASE_R1, BASE_R2, BASE_STEP = 120.0, 25.0, 31.0, 28.0, 20.0
ICON_H, MAX_W = ALTURA - BASE_H, 100.0
C, R, D = 4.0, 3.0, 2.0       # preto: meia-espessura 4 + arredondado 3 = 14 mm no total; gravação 2 mm
HW_FUNDO, HW_INLAY = 3.0, 6.0 # branco: fundo com 6 mm de espessura; detalhes embutidos 1 mm abaixo do preto
BORDA, FECHA = 2.5, 6.0       # borda branca em volta e raio para fechar vãos entre partes
EMBED = 1.5
NFC_R, NFC_H = 13.25, 1.0
ANO, TXT_H, TXT_D = '2026', 9.0, 1.0
FONT = '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
F2, RES = 0.1, 0.3

def sdist(m):
    return (ndi.distance_transform_edt(m) - ndi.distance_transform_edt(~m)) * F2

def masks(i):
    x0,y0,x1,y1 = BOX[i]
    g = ref[y0:y1, x0:x1]
    dark = ndi.gaussian_filter(g,0.6) < 110
    rows = np.where(dark.any(1))[0]; top = rows.min(); cols = np.where(dark.any(0))[0]
    px = ICON_H / (g.shape[0] - top)
    if (cols.max()-cols.min()+1)*px > MAX_W: px = MAX_W/(cols.max()-cols.min()+1)
    g = g[top:, cols.min():cols.max()+1]
    n_z, n_x = int(round(g.shape[0]*px/F2)), int(round(g.shape[1]*px/F2))
    gi = np.asarray(Image.fromarray(g.astype(np.uint8)).resize((n_x,n_z), Image.BICUBIC)).astype(float)
    gi = ndi.gaussian_filter(gi, 0.12*px/F2)
    m = morphology.remove_small_objects(gi < 110, int(4/F2**2))
    filled = ndi.binary_fill_holes(m)
    holes = morphology.remove_small_objects(filled & ~m, int(1.0/F2**2))
    B = filled & ~holes
    pad = int(round(EMBED/F2))+1
    z = np.zeros((pad, n_x), bool)
    B = np.vstack([B, z]); holes = np.vstack([holes, z])
    ground = np.zeros_like(B); cx = n_x/2; rb = BASE_R2/F2*0.9
    ground[-pad:, max(0,int(cx-rb)):min(n_x,int(cx+rb))] = True
    return B, holes, ground, pad

def ligar(S, ground):
    """liga componentes soltos de S ao chão com pontes de 3 mm"""
    bw = int(round(3.0/F2)); n_p = 0
    while True:
        lab, n = ndi.label(S | ground, np.ones((3,3)))
        gl = lab[ground].max(); main = lab == gl
        others = [k for k in range(1, n+1) if k != gl]
        if not others: return S, n_p
        dt, (iz, ix) = ndi.distance_transform_edt(~main, return_indices=True)
        best = None
        for k in others:
            d = np.where(lab == k, dt, np.inf); a = np.unravel_index(np.argmin(d), d.shape)
            if best is None or d[a] < best[0]: best = (d[a], a, (iz[a], ix[a]))
        _, (az, ax), (bz, bx) = best
        rr, cc = draw.line(int(az), int(ax), int(bz), int(bx))
        line = np.zeros_like(S); line[rr, cc] = True
        S |= ndi.binary_dilation(line, iterations=bw//2); n_p += 1

def olho(holes):
    lab, n = ndi.label(holes)
    H, W = holes.shape; best = None
    for k in range(1, n+1):
        zz, xx = np.where(lab == k)
        if zz.mean() < 0.45*H and xx.mean() > 0.5*W:
            if best is None or len(zz) > best[1]: best = (k, len(zz))
    return lab == best[0] if best else np.zeros_like(holes)

def texto_mask(nS, nZ):
    """máscara 2D (z, s) do ano em mm, s = comprimento de arco"""
    sc = 10
    font = ImageFont.truetype(FONT, int(TXT_H*sc*1.35))
    im = Image.new('L', (int(nS*sc), int(nZ*sc)), 0); d = ImageDraw.Draw(im)
    bb = d.textbbox((0,0), ANO, font=font)
    w, h = bb[2]-bb[0], bb[3]-bb[1]
    d.text(((im.width-w)/2 - bb[0], (im.height-h)/2 - bb[1]), ANO, fill=255, font=font)
    a = np.asarray(im) > 127
    return a, sc, h/sc, w/sc

def build(i, outdir):
    B, holes, ground, pad = masks(i)
    S_out = B | holes                          # contorno externo do ícone
    lastrow = S_out[-pad-1].copy()
    for k in range(pad):
        B[-pad+k] |= lastrow & ground[-pad+k]
    pontes = 0
    if i in FUNDO:
        W = ndi.binary_closing(np.pad(S_out, int(FECHA/F2)), morphology.disk(int(FECHA/F2)))[int(FECHA/F2):-int(FECHA/F2), int(FECHA/F2):-int(FECHA/F2)]
        W = ndi.binary_fill_holes(W | S_out)
        W = ndi.binary_dilation(np.pad(W, int(BORDA/F2)+2), morphology.disk(int(BORDA/F2)))
        cut = int(BORDA/F2)+2
        W = W[cut:-cut, cut:-cut] if False else W
        # a borda pode passar dos limites do recorte: trabalhar na grade ampliada
        Bp = np.pad(B, cut); Hp = np.pad(holes, cut); Gp = np.pad(ground, cut)
        B, holes, ground = Bp, Hp, Gp
        W[-cut:] = False                         # nada abaixo da base
        last = W[-cut-pad-1].copy()
        for k in range(pad): W[-cut-pad+k] |= last & ground[-cut-pad+k]
        W, pontes = ligar(W, ground)             # o fundo branco tem que encostar na base
        inlay = holes
        white_fundo = W & ~B & ~holes
        recesso = np.zeros_like(holes)
    else:
        if i in SO_OLHO:
            inlay = olho(holes); recesso = holes & ~inlay
        else:
            inlay = holes; recesso = np.zeros_like(holes)
        B, pontes = ligar(B, ground)
        white_fundo = np.zeros_like(B)
    S_out = B | holes
    sd_out = sdist(S_out)
    din = np.clip(sd_out, 0, R)
    h = C + R*np.sqrt(np.clip(1 - (1 - din/R)**2, 0, 1))
    h_b = h - D*np.clip(sdist(recesso)/0.4 + 0.5, 0, 1)      # recesso preto (só no camaleão)
    sd_b = sdist(B | recesso)
    sd_wf = sdist(white_fundo); sd_in = sdist(inlay)
    f = F2/RES
    Z2 = lambda a: ndi.zoom(a, f, order=1)
    sd_b, h_b, sd_wf, sd_in = map(Z2, (sd_b, h_b, sd_wf, sd_in))
    nz, nx = sd_b.shape
    nX = int(np.ceil(max(nx*RES, 2*BASE_R1+4)/RES))+4
    nY = int(np.ceil((2*BASE_R1+4)/RES))+4
    zb = BASE_H - EMBED
    nZ = int(np.ceil((zb + nz*RES)/RES))+3
    X = (np.arange(nX)-nX/2)*RES; Y = (np.arange(nY)-nY/2)*RES; Z = np.arange(nZ)*RES - RES
    def place(a, fill):
        out = np.full((nX, nZ), fill, np.float32); xo = (nX-nx)//2; zi = int(round((zb - Z[0])/RES))
        out[xo:xo+nx, zi:zi+nz] = a[::-1].T; return out
    SDb, HB, SDwf, SDin = place(sd_b,-5), place(h_b,0), place(sd_wf,-5), place(sd_in,-5)
    aY = np.abs(Y)[None,:,None]
    Fb = np.minimum(SDb[:,None,:], HB[:,None,:] - aY)
    Fw = np.maximum(np.minimum(SDwf[:,None,:], HW_FUNDO - aY), np.minimum(SDin[:,None,:], HW_INLAY - aY))
    rho = np.sqrt(X[:,None]**2 + Y[None,:]**2)[:,:,None]; Zc = Z[None,None,:]
    cyl1 = np.minimum(np.minimum(BASE_R1 - rho - np.clip(1.0 - Zc, 0, None), Zc), BASE_STEP - Zc)
    cyl2 = np.minimum(np.minimum(BASE_R2 - rho - np.clip(Zc - (BASE_H-1.0), 0, None), Zc - BASE_STEP + 0.5), BASE_H - Zc)
    base = np.maximum(cyl1, cyl2)
    base = np.minimum(base, -np.minimum(NFC_R - rho, NFC_H - Zc))
    # ano na frente da base (lado -y), embutido em branco
    arc = 60.0
    tm, sc, th, tw = texto_mask(arc, BASE_STEP)
    sdt = (ndi.distance_transform_edt(tm) - ndi.distance_transform_edt(~tm)) / sc
    s = BASE_R1*np.arctan2(X[:,None], -Y[None,:])                    # arco a partir da frente
    si = (s + arc/2)*sc; zi = (BASE_STEP - Z)*sc                      # linha 0 = topo do degrau
    sh = (nX, nY, nZ)
    SI = np.broadcast_to(si[:,:,None], sh); ZI = np.broadcast_to(zi[None,None,:], sh)
    sel = np.broadcast_to((np.abs(si/sc - arc/2) < arc/2)[:,:,None] & (Z[None,None,:] < BASE_STEP) & (Z[None,None,:] > 0) & (Y[None,:,None] < 0) & (rho > BASE_R1 - 3), sh)
    T = np.full(sh, -5.0, np.float32)
    T[sel] = ndi.map_coordinates(sdt, [ZI[sel], SI[sel]], order=1, mode='constant', cval=-5)
    Ftxt = np.minimum(T, rho - (BASE_R1 - TXT_D))
    Ftxt = np.minimum(Ftxt, base)                                     # só dentro da base
    base = np.minimum(base, -Ftxt)
    Fblack = np.maximum(Fb, base)
    Fwhite = np.maximum(np.minimum(Fw, -np.maximum(base, Fb)), Ftxt)  # branco fora do preto
    meshes = {}
    for nome, F in (('preto', Fblack), ('branco', Fwhite)):
        F = ndi.gaussian_filter(F.astype(np.float32), 0.9)
        F = np.pad(F, 1, constant_values=-1)
        if F.max() <= 0: continue
        v, fc, _, _ = measure.marching_cubes(F, 0, spacing=(RES,)*3)
        v -= RES; v[:,0] += X[0]; v[:,1] += Y[0]; v[:,2] += Z[0]
        m = trimesh.Trimesh(v, fc[:, ::-1], process=True)
        parts = [p for p in m.split(only_watertight=False) if len(p.faces) > 200]
        m = trimesh.util.concatenate(parts)
        if m.volume < 0: m.invert()
        meshes[nome] = m
    sc3 = trimesh.Scene()
    for nome, m in meshes.items():
        m.visual.face_colors = [20,20,20,255] if nome == 'preto' else [245,245,245,255]
        sc3.add_geometry(m, node_name=nome, geom_name=nome)
    base_nome = f'trofeu-{i}-{NOME[i]}'
    sc3.export(os.path.join(outdir, base_nome + '.3mf'))
    for nome, m in meshes.items(): m.export(os.path.join(outdir, f'{base_nome}-{nome}.stl'))
    info = '  '.join(f"{n}: {m.volume/1000:.0f} cm3 estanque={m.is_watertight}" for n, m in meshes.items())
    print(f"{i} {NOME[i]:<24} pontes {pontes}  {info}")
    return meshes

if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    ids = [int(a) for a in sys.argv[2:]] or list(BOX)
    for i in ids: build(i, out)
