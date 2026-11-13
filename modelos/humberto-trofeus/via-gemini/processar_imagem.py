"""Processa uma imagem 3 cores (preto/branco/cinza) do Gemini para o pipeline 3D (VTracer + Blender)."""
import sys, os, numpy as np, vtracer
from PIL import Image
from scipy import ndimage as ndi
from svgelements import SVG, Path, Move, Close
from shapely.geometry import Polygon
ICON_H = 95.0
def mascaras(path):
    g = np.asarray(Image.open(path).convert('L')).astype(float)
    preto, branco = g < 80, g > 215
    ys, xs = np.where(preto | branco)
    y0, y1 = ys.min(), ys.max()
    s = ICON_H / (y1 - y0 + 1)
    # centro do apoio = meio da linha de baixo
    fundo_linha = np.where((preto | branco)[y1-3:y1+1].any(0))[0]
    cx = (fundo_linha.min() + fundo_linha.max())/2
    # engrossa só os detalhes brancos finos (< 1 mm) para imprimirem bem
    r = lambda mm: max(1, int(round(mm/s)))
    aberto = ndi.binary_opening(branco, structure=np.ones((r(0.5)*2+1,)*2))
    fino = branco & ~aberto
    branco2 = branco | (ndi.binary_dilation(fino, iterations=r(0.35)) & preto)
    preto2 = preto & ~branco2
    return preto2, branco2, s, cx, y1
def vetorizar(mask, nome):
    Image.fromarray(np.where(mask, 0, 255).astype(np.uint8)).save(nome + '.png')
    vtracer.convert_image_to_svg_py(nome + '.png', nome + '.svg', colormode='binary', mode='spline', filter_speckle=4,
                                    corner_threshold=60, length_threshold=4.0, splice_threshold=45, path_precision=3)
def ler(svg_path, s, cx, ybase, passo=1.0):
    geo = Polygon()
    for el in SVG.parse(svg_path).elements():
        if not isinstance(el, Path): continue
        aneis, atual = [], []
        for seg in el:
            if isinstance(seg, Move):
                if len(atual) > 2: aneis.append(atual)
                atual = [(seg.end.x, seg.end.y)]; continue
            if isinstance(seg, Close):
                if len(atual) > 2: aneis.append(atual)
                atual = []; continue
            n = max(2, int(seg.length(error=1e-2)/passo))
            for t in np.linspace(0, 1, n)[1:]:
                p = seg.point(t); atual.append((p.x, p.y))
        if len(atual) > 2: aneis.append(atual)
        for a in aneis:
            a = np.array(a); pg = Polygon(np.stack([(a[:,0]-cx)*s, (ybase-a[:,1])*s], 1)).buffer(0)
            if pg.area > 0.05: geo = geo.symmetric_difference(pg)
    return geo
