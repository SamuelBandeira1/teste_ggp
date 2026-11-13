"""Camadas (preto, branco embutido, fundo branco) de cada ícone a partir da referência HD, vetorizadas com VTracer."""
import sys, warnings, numpy as np, vtracer
warnings.filterwarnings('ignore')
from PIL import Image
from scipy import ndimage as ndi
from skimage import morphology, segmentation
REF = np.asarray(Image.open('../trofeus/ref_hd2.png').convert('L')).astype(float)
CX = {1:247,2:501,3:766,4:1030,5:1290,6:220,7:541,8:874,9:1191}
APOIO = {1:411,2:415,3:413,4:411,5:406,6:851,7:851,8:851,9:851}
LIMIAR = {i: 110 for i in CX}; LIMIAR.update({7: 140, 2: 195, 3: 195, 8: 150})
FUNDO = {1,2,3,4,5,8}
FIEL = {2, 3}                     # troféus traçados pelo limiar do branco (método aprovado)
UP, S = 6, 0.352
PX = S/UP
def camadas(i):
    cx, ap = CX[i], APOIO[i]
    x0, x1, y0 = cx-175, cx+175, ap-300
    g = REF[y0:ap, x0:x1]
    G = np.asarray(Image.fromarray(g.astype(np.uint8)).resize((g.shape[1]*UP, g.shape[0]*UP), Image.BICUBIC)).astype(float)
    G = ndi.gaussian_filter(G, UP*(0.2 if i in FIEL else 0.35))
    preto = G < LIMIAR[i]
    # tira o que encosta nas laterais do recorte (pedaços dos troféus vizinhos)
    lab, n = ndi.label(preto)
    borda = set(np.unique(np.concatenate([lab[:, :3].ravel(), lab[:, -3:].ravel()]))) - {0}
    for k in borda: preto[lab == k] = False
    preto = morphology.remove_small_objects(preto, int((1.5/PX)**2))
    if i in FIEL:
        pass                                    # traçado fiel pelo branco, sem filtro de riscos
    else:
        # fecha riscos brancos finos de brilho (< 0,7 mm)
        d = ndi.distance_transform_edt(~preto)*PX <= 0.35
        preto = ndi.distance_transform_edt(d)*PX > 0.35
    cheio = ndi.binary_fill_holes(preto)
    buracos = morphology.remove_small_objects(cheio & ~preto, int((1.0/PX)**2))
    preto = cheio & ~buracos
    if i == 7:                                  # camaleão: só o olho branco, resto vazado
        lab, n = ndi.label(buracos); H, W = buracos.shape; best = None
        for k in range(1, n+1):
            zz, xx = np.where(lab == k)
            if zz.mean() < 0.45*H and xx.mean() > 0.55*W and (best is None or len(zz) > best[1]): best = (k, len(zz))
        buracos = (lab == best[0]) if best else np.zeros_like(buracos)
    fundo = np.zeros_like(preto)
    if i in FUNDO:
        U = preto | buracos
        dd = ndi.distance_transform_edt(~U)*PX <= 6.0
        W = ndi.binary_fill_holes((ndi.distance_transform_edt(dd)*PX > 6.0) | U)
        W = ndi.distance_transform_edt(~W)*PX <= 2.5
        rows = (W.shape[0] - np.arange(W.shape[0]))*PX
        W &= rows[:, None] > 1.5
        fundo = W & ~preto & ~buracos
    return preto, buracos, fundo
def salvar_svg(mask, path):
    Image.fromarray(np.where(mask, 0, 255).astype(np.uint8)).save(path.replace('.svg', '.png'))
    vtracer.convert_image_to_svg_py(path.replace('.svg', '.png'), path, colormode='binary', mode='spline', filter_speckle=6,
                                    corner_threshold=70, length_threshold=5.0, splice_threshold=45, path_precision=3)
if __name__ == '__main__':
    for i in [int(a) for a in sys.argv[1:]] or list(CX):
        p, b, f = camadas(i)
        open(f'i{i}_altura.txt', 'w').write(str(p.shape[0]))
        for nome, m in (('preto', p), ('branco', b), ('fundo', f)):
            if m.any(): salvar_svg(m, f'i{i}_{nome}.svg')
        print(i, 'ok', flush=True)
