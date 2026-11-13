"""Lê o SVG do VTracer e devolve geometria shapely em mm (x=0 no centro da base, y=0 no apoio)."""
import numpy as np
from svgelements import SVG, Path, Move, Close
from shapely.geometry import Polygon
from shapely.ops import unary_union
UP, S, CXCOL = 6, 0.352, 175
def ler(svg_path, H, passo=1.5):
    svg = SVG.parse(svg_path)
    geo = Polygon()
    for el in svg.elements():
        if not isinstance(el, Path): continue
        aneis, atual = [], []
        for seg in el:
            if isinstance(seg, Move):
                if len(atual) > 2: aneis.append(atual)
                atual = [(seg.end.x, seg.end.y)]; continue
            if isinstance(seg, Close):
                if len(atual) > 2: aneis.append(atual)
                atual = []; continue
            L = seg.length(error=1e-2) if hasattr(seg, 'length') else 1
            n = max(2, int(L/passo))
            for t in np.linspace(0, 1, n)[1:]:
                p = seg.point(t); atual.append((p.x, p.y))
        if len(atual) > 2: aneis.append(atual)
        for a in aneis:
            a = np.array(a)
            mm = np.stack([(a[:,0]/UP - CXCOL)*S, (H - a[:,1])/UP*S], 1)
            pg = Polygon(mm).buffer(0)
            if pg.area > 0.05: geo = geo.symmetric_difference(pg)
    return geo
