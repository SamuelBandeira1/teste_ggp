"""Desenho 2D dos 9 troféus (v6). Coordenadas em px da referência: u para a direita a partir do centro da base,
v para cima a partir da linha de topo da base usada na grade de medição."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.ndimage import gaussian_filter1d
from skimage import measure
from shapely.geometry import Point, Polygon, LineString, box, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity

REF = np.asarray(Image.open('ref_hd2.png').convert('L')).astype(float)
CX = {1:247,2:501,3:766,4:1030,5:1290,6:220,7:541,8:874,9:1191}
TOPO = {1:422,2:435,3:435,4:421,5:413,6:834,7:879,8:879,9:879}   # topo da grade em que medi cada um
Q = 32

def C(c, r): return Point(*c).buffer(r, quad_segs=Q)
def E(c, rx, ry, rot=0): return affinity.rotate(affinity.scale(C(c, 1), rx, ry), rot)
def RR(x0, y0, x1, y1, r):
    return box(x0+r, y0+r, x1-r, y1-r).buffer(r, quad_segs=Q) if r > 0 else box(x0, y0, x1, y1)
def T(pts, w): return LineString(pts).buffer(w/2, cap_style='round', join_style='round', quad_segs=Q)
def suave(g, r): return g.buffer(r, quad_segs=Q).buffer(-2*r, quad_segs=Q).buffer(r, quad_segs=Q)
def arred(g, r): return g.buffer(-r, quad_segs=Q).buffer(r, quad_segs=Q)
def bez(p0, p1, p2, n=40):
    t = np.linspace(0, 1, n)[:, None]; p0, p1, p2 = map(np.array, (p0, p1, p2))
    return (1-t)**2*p0 + 2*(1-t)*t*p1 + t**2*p2
def cub(p0, p1, p2, p3, n=50):
    t = np.linspace(0, 1, n)[:, None]; p0, p1, p2, p3 = map(np.array, (p0, p1, p2, p3))
    return (1-t)**3*p0 + 3*(1-t)**2*t*p1 + 3*(1-t)*t**2*p2 + t**3*p3
def catmull(pts, n=14):
    P = np.array(pts, float); P = np.vstack([P[0], P, P[-1]]); out = []
    for k in range(1, len(P)-2):
        p0, p1, p2, p3 = P[k-1], P[k], P[k+1], P[k+2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5*((2*p1) + (-p0+p2)*t + (2*p0-5*p1+4*p2-p3)*t*t + (-p0+3*p1-3*p2+p3)*t**3))
    out.append(P[-2]); return np.array(out)
def rot(g, ang, c): return affinity.rotate(g, ang, origin=c)
def esp(g, x0=0): return affinity.scale(g, -1, 1, origin=(x0, 0))
def contorno(frente, atras, w=3.0):
    """linha branca onde a peça da frente cruza a de trás"""
    return frente.exterior.buffer(w/2, quad_segs=Q).intersection(atras) if hasattr(frente, 'exterior') else \
        unary_union([p.exterior for p in frente.geoms]).buffer(w/2, quad_segs=Q).intersection(atras)

def tracado(i, regiao, nivel=110, suav=0.8):
    """polígonos escuros da referência dentro de 'regiao' (u,v), contornos suavizados"""
    cx, top = CX[i], TOPO[i]
    x0, x1, y0, y1 = cx-170, cx+170, top-310, top+40
    g = REF[y0:y1, x0:x1]
    UP = 4
    G = np.asarray(Image.fromarray(g.astype(np.uint8)).resize((g.shape[1]*UP, g.shape[0]*UP), Image.BICUBIC)).astype(float)
    G = ndi.gaussian_filter(np.pad(G, 8, constant_values=255), 1.2)
    geo = Polygon()
    for c in measure.find_contours(G, nivel):
        p = (c - 8) / UP                          # (linha, coluna) em px da ref
        uv = np.stack([p[:,1] + x0 - cx, top - (p[:,0] + y0)], 1)
        seg = np.sqrt((np.diff(uv, axis=0)**2).sum(1)); L = seg.sum()
        if L < 6: continue
        s = np.concatenate([[0], np.cumsum(seg)]); n = max(int(L/0.4), 12)
        t = np.linspace(0, L, n, endpoint=False)
        r = np.stack([np.interp(t, s, uv[:,0]), np.interp(t, s, uv[:,1])], 1)
        r = gaussian_filter1d(r, suav/0.4, axis=0, mode='wrap')
        pg = Polygon(r).buffer(0)
        geo = geo.symmetric_difference(pg)
    return geo.intersection(regiao)

# ------------------------------------------------------------------ 1
def t1():
    gc = (-14, 161)
    corpo = C(gc, 93)
    dentes = unary_union([rot(RR(gc[0]-17, gc[1]+80, gc[0]+17, gc[1]+111, 5), a, gc) for a in range(0, 360, 45)])
    eng = arred(unary_union([corpo, dentes]), 3).difference(C(gc, 61))
    mon = RR(-111, 56, 49, 169, 11)
    tela_borda = RR(-98, 61, 39, 158, 7)
    tela = RR(-89, 69, 31, 149, 3)
    codigo = unary_union([T([(-49,127),(-67,110),(-49,93)], 6), T([(-20,128),(-37,91)], 6), T([(-10,127),(8,110),(-10,93)], 6)])
    placa = arred(Polygon([(-122,39),(-114,53),(14,53),(20,39)]), 4)
    pedestal = unary_union([E((-4, 4), 64, 30).intersection(box(-200, 0, 200, 60)), RR(-52,20,-18,44,4)])
    # chave inglesa (branca com contorno preto), na frente de tudo
    a, b = np.array((-12, 22)), np.array((80, 98))
    d = (b - a)/np.linalg.norm(b - a); n = np.array((-d[1], d[0]))
    cabo = T([tuple(a), tuple(b)], 20)
    def cabeca(c, sentido):
        c = np.array(c); h = C(tuple(c), 24)
        boca = Polygon([tuple(c + sentido*d*5 + n*8), tuple(c + sentido*d*34 + n*8), tuple(c + sentido*d*34 - n*8), tuple(c + sentido*d*5 - n*8)])
        return h.difference(boca.union(C(tuple(c + sentido*d*5), 8)))
    chave = arred(unary_union([cabo, cabeca(a, -1), cabeca(b, 1)]), 2)
    fundo_preto = unary_union([eng, mon, placa, pedestal])
    gap = chave.buffer(3.2, quad_segs=Q)
    preto = unary_union([fundo_preto.difference(gap), chave])
    branco = unary_union([tela_borda.difference(tela), codigo.intersection(tela), gap.difference(chave).intersection(fundo_preto),
                          contorno(placa, mon, 3.0)])
    preto = preto.difference(branco)
    return preto, branco

# ------------------------------------------------------------------ 2
def t2():
    lado = cub((106,150),(106,92),(62,44),(0,20))
    contorno_ext = np.vstack([[(0,289),(98,247)], [(106,236)], lado, esp(LineString(lado[::-1])).coords, [(-106,236),(-98,247)]])
    esc = arred(Polygon(contorno_ext).buffer(0), 4)
    dentro = esc.buffer(-18, quad_segs=Q, join_style='mitre')
    dentro = arred(dentro, 3)
    moldura = esc.difference(dentro)
    faixa_baixa = dentro.difference(dentro.buffer(-8, quad_segs=Q)).intersection(box(-200, -50, 200, 118))
    miolo = dentro.buffer(-8, quad_segs=Q).union(dentro.intersection(box(-200, 118, 200, 400)))
    # parte de cima (mangas + costas da mão) em curva limpa; os vãos brancos dos dedos vêm da referência
    curva = np.vstack([[(-130,213)], [(-40,169)], cub((-40,169),(-24,192),(30,193),(52,169))[1:], [(130,214), (130,-60), (-130,-60)]])
    massa = Polygon(curva).intersection(miolo)
    escuro = tracado(2, miolo, nivel=122, suav=0.5)
    vaos = massa.buffer(-2.2, quad_segs=Q).difference(escuro)
    vaos = vaos.buffer(-0.9, quad_segs=Q).buffer(0.9, quad_segs=Q)
    vaos = unary_union([g for g in (vaos.geoms if hasattr(vaos, 'geoms') else [vaos]) if g.area > 15])
    maos = arred(massa.difference(vaos), 0.8)
    preto = unary_union([moldura, maos])
    branco = dentro.difference(maos)          # painel de cima + faixa de baixo + vãos dos dedos
    return preto, branco

# ------------------------------------------------------------------ 3
def t3():
    tabua = arred(Polygon([(-101,233),(-9,286),(109,240),(42,203),(-58,207)]), 5)
    copa = RR(-56, 175, 63, 212, 6)
    cordao = RR(-91, 186, -84, 236, 3)
    no = E((-87.5, 187), 10, 6)
    borla = arred(Polygon([(-95,184),(-80,184),(-76,150),(-99,150)]), 5)
    livro_c = RR(-110, 52, -30, 90, 13); folhas_c = RR(-94, 60, -20, 73, 6.5)
    livro_b = RR(-118, 21, 10, 56, 15); folhas_b = RR(-101, 29, 15, 43, 7)
    livros = unary_union([livro_c.difference(folhas_c.intersection(box(-200,0,-32,300))), livro_b.difference(folhas_b.intersection(box(-200,0,-2,300)))])
    folhas = unary_union([folhas_c.intersection(box(-200,0,-32,300)), folhas_b.intersection(box(-200,0,-2,300))])
    regiao_menina = unary_union([box(-96, 22, 115, 148), box(-79, 148, 115, 212)]).difference(box(-140, -10, -33, 92)).difference(box(-140, -10, -6, 57))
    menina = tracado(3, regiao_menina, nivel=105, suav=0.6)
    menina = arred(menina, 1.0)
    chapeu = unary_union([tabua, copa, cordao, no, borla])
    preto = unary_union([chapeu.difference(menina.buffer(0.01)), menina, livros.difference(menina.buffer(3, quad_segs=Q))])
    branco = unary_union([folhas.difference(menina.buffer(3, quad_segs=Q)),
                          tabua.exterior.buffer(1.4).intersection(copa).intersection(box(-200,205,200,300))])
    preto = preto.difference(branco)
    return preto, branco

# ------------------------------------------------------------------ 4
def t4():
    sc = (0, 177)
    sol = C(sc, 63); rosto = C(sc, 54)
    raios = unary_union([T([(sc[0]+r0*np.cos(np.radians(a)), sc[1]+r0*np.sin(np.radians(a))),
                            (sc[0]+r1*np.cos(np.radians(a)), sc[1]+r1*np.sin(np.radians(a)))], 11)
                         for a, r0, r1 in [(92,72,104),(128,72,106),(162,72,106),(200,72,106),(236,72,103),(52,72,106),(18,72,104)]])
    olhos = unary_union([T(bez((x-11,181),(x,198),(x+11,181)), 6) for x in (-27, 20)])
    boca = T(bez((-21,165),(0,140),(21,165)), 6)
    corpo_seta = T(cub((-4,104),(30,112),(55,132),(78,160)), 13)
    ponta = arred(Polygon([(104,194),(62,180),(98,145)]), 2.5)
    seta = unary_union([corpo_seta, ponta])
    barras = unary_union([RR(-2,25,12,74,3), RR(20,25,48,93,4), RR(58,25,87,128,4)])
    cc, ang = (-50, 69), 6.5
    def L(g): return rot(affinity.translate(g, *cc), ang, cc)
    calc_ext = L(RR(-43, -47, 43, 47, 10))
    calc_face = L(RR(-34, -38, 34, 38, 5))
    visor = L(RR(-26, 12, 26, 31, 3.5))
    teclas = unary_union([L(RR(x-7, y-6.5, x+7, y+6.5, 3)) for x in (-19, 0, 19) for y in (-7, -27)])
    calc = calc_ext.difference(calc_face).union(visor).union(teclas)
    preto = unary_union([sol.difference(rosto), raios.difference(C(sc, 66)), olhos, boca,
                         seta.difference(sol.buffer(3)), barras.difference(seta.buffer(3)).difference(calc_ext.buffer(3)), calc])
    preto = unary_union([preto, seta.difference(sol.buffer(3))])
    branco = unary_union([rosto.difference(unary_union([olhos, boca])), calc_face.difference(unary_union([visor, teclas]))])
    return preto, branco

# ------------------------------------------------------------------ 5
def t5():
    caneca = unary_union([RR(-80, 6, 57, 162, 14), E((-11.5, 161), 68.5, 12)])
    liquido = E((-11.5, 156), 58, 6.5)
    alca = E((60, 108), 38, 44).difference(E((60, 108), 20, 27)).intersection(box(48, -50, 300, 300))
    vapor = unary_union([T(catmull([(-30,176),(-42,194),(-30,214),(-40,236)]), 15),
                         T(catmull([(5,176),(-9,200),(6,228),(-5,256)]), 17)])
    lente = arred(Polygon(np.vstack([[(-90,77),(-12,77)], cub((-12,77),(-14,40),(-24,22),(-48,22))[1:], cub((-48,22),(-70,22),(-84,36),(-90,77))[1:-1]])), 6)
    lente_d = esp(lente, -3)
    aro = unary_union([lente.buffer(9, quad_segs=Q), lente_d.buffer(9, quad_segs=Q), RR(-14, 62, 8, 80, 5),
                       RR(-110, 62, -92, 80, 5), RR(86, 62, 104, 80, 5)])
    aro = arred(aro, 2)
    oculos_ext = aro.buffer(3.2, quad_segs=Q)
    preto = unary_union([caneca.difference(liquido).difference(oculos_ext), alca.difference(oculos_ext),
                         vapor, oculos_ext.difference(aro), lente, lente_d])
    branco = unary_union([liquido, aro.difference(unary_union([lente, lente_d]))])
    preto = preto.difference(branco)
    return preto, branco

# ------------------------------------------------------------------ 6
def t6():
    casco = arred(Polygon(np.vstack([cub((-100,-16),(-105,60),(-60,110),(-5,111)), cub((-5,111),(60,111),(90,60),(84,0))[1:],
                                     [(84,-12),(70,-22),(-90,-22)]])), 6)
    viseira_ext = arred(Polygon(np.vstack([[(-92,8)], cub((-92,8),(-90,50),(-82,76),(-60,78))[1:], cub((-60,78),(10,82),(52,78),(56,58))[1:],
                                           cub((56,58),(58,38),(52,26),(40,24))[1:], [(-92,8)]])), 4)
    viseira_int = viseira_ext.buffer(-8, quad_segs=Q)
    lente = arred(Polygon([(-72,64),(4,64),(-6,27),(-74,22)]), 4)
    respiro = unary_union([C((31, 51), 10), T([(31,46),(18,33)], 7)])
    friso = T(cub((-60,-12),(-20,-8),(30,-6),(70,-2)), 5).intersection(casco.buffer(-3))
    bandeira = tracado(6, Polygon([(-70,100),(-40,240),(160,240),(160,60),(60,60),(-70,100)]).difference(casco.buffer(5)), nivel=110)
    bandeira = arred(bandeira, 1.0)
    # haste da bandeira encosta no capacete
    preto = unary_union([casco.difference(viseira_int).difference(friso), lente, respiro, bandeira])
    branco = unary_union([viseira_int.difference(unary_union([lente, respiro])), friso])
    preto = preto.difference(branco)
    return preto, branco

# ------------------------------------------------------------------ 7
def t7():
    sil = suave(arred(tracado(7, box(-160, 21, 160, 300), nivel=160, suav=1.3), 1.6), 1.2)   # contorno externo liso
    det = tracado(7, box(-160, 21, 160, 300), nivel=110, suav=0.7)
    vaos = sil.buffer(-2.5, quad_segs=Q).difference(det)
    vaos = vaos.buffer(-1.6, quad_segs=Q).buffer(1.6, quad_segs=Q)        # tira riscos finos de brilho
    vaos = unary_union([g for g in (vaos.geoms if hasattr(vaos, 'geoms') else [vaos]) if g.area > 40])
    cam = arred(sil.difference(vaos), 0.6)
    olho = C((80, 217), 12)
    preto = cam.difference(olho.buffer(0.1))
    return preto, olho

# ------------------------------------------------------------------ 8
def t8():
    cl, cr, r = (-13, 172), (75, 172), 34
    oculos = unary_union([C(cl, r).difference(C(cl, r-10)), C(cr, r).difference(C(cr, r-10)),
                          T(bez((19,172),(30,186),(42,172)), 9), T([(107,172),(117,172)], 9)])
    raio = arred(Polygon([(45,267),(14,223),(36,226),(27,193),(59,235),(38,232)]), 2)
    def folha(base, ponta, larg):
        base, ponta = np.array(base), np.array(ponta); L = np.linalg.norm(ponta-base); a = np.degrees(np.arctan2(*(ponta-base)[::-1]))
        R = (L**2/4 + larg**2)/(2*larg)
        f = C((L/2, larg-R), R).intersection(C((L/2, R-larg), R))
        f = affinity.translate(affinity.rotate(f, a, origin=(0,0)), *base)
        nerv = affinity.translate(affinity.rotate(T([(L*0.12,0),(L*0.85,0)], 3.2), a, origin=(0,0)), *base)
        return f, nerv
    f1, n1 = folha((-52,104), (-118,176), 24)
    f2, n2 = folha((-36,76), (14,128), 18)
    caule = unary_union([T(cub((-36,25),(-36,50),(-44,80),(-52,104)), 7), T(bez((-38,50),(-38,66),(-36,76)), 6)])
    barra = T([(-58,62),(40,80)], 18)
    placas = unary_union([RR(27,25,55,127,12), RR(60,32,88,120,11), RR(91,50,107,101,7),
                          RR(-104,25,-78,92,10), RR(-127,30,-106,70,8), RR(-75,25,-50,88,10)])
    vaos = unary_union([p.exterior.buffer(1.8, quad_segs=Q) for p in placas.geoms]) if isinstance(placas, MultiPolygon) else placas.exterior.buffer(1.8)
    preto = unary_union([oculos, raio, f1.difference(n1), f2.difference(n2), caule.difference(placas.buffer(3)),
                         barra.difference(placas.buffer(3)), placas])
    preto = preto.difference(vaos.difference(placas))
    branco = unary_union([n1.intersection(f1.buffer(-2)), n2.intersection(f2.buffer(-2))])
    return preto, branco

# ------------------------------------------------------------------ 9 (leitor em vetor, mm já ajustado em px)
def t9():
    k = 2.95   # mm do desenho original -> px da referência
    def S(g): return affinity.scale(g, k, k, origin=(0, 0))
    def bz(p0, p1, p2): return bez(p0, p1, p2, 60)
    pagina = Polygon(np.vstack([bz((-34,40),(-15,44),(0,34)), [(0,6)], bz((0,6),(-15,14),(-34,12))[1:]]))
    livro = arred(unary_union([pagina, esp(pagina)]), 1.0)
    colo = arred(RR(-21, 0, 21, 12, 3.5), 0.5)
    cabeca = C((0, 55), 20.5)
    crc = (27, 63)
    rel = C(crc, 16).difference(C(crc, 11.8))
    ponteiros = unary_union([T([crc, (crc[0], crc[1]+8.5)], 3.0), T([crc, (crc[0]+7, crc[1]-4)], 3.0), C(crc, 2.3)])
    U = unary_union([livro, colo, cabeca, rel, ponteiros])
    dentro = U.buffer(-1.1, quad_segs=Q)
    seps = [cabeca.exterior.buffer(0.8, quad_segs=Q).intersection(rel), livro.exterior.buffer(0.8, quad_segs=Q).intersection(unary_union([cabeca, rel, colo]))]
    det = [T([(0,32.6),(0,8.4)], 1.5), T(bz((-31.5,36.6),(-15,40.2),(-1.6,31.4)), 1.3)]
    for off in (8.5, 13.5, 18.5): det.append(T(bz((-28,40-off),(-15,43.5-off),(-5,33.5-off)), 1.2))
    det = unary_union(det); det = unary_union([det, esp(det)]).intersection(livro.buffer(-1.2, quad_segs=Q))
    franja = catmull([(-22,56),(-12,47),(-7,52.5),(0,45.5),(7,52.5),(12,47),(22,56)], n=24)
    abaixo = Polygon(np.vstack([franja, [(22,20),(-22,20)]]))
    rosto = cabeca.buffer(-1.4, quad_segs=Q).intersection(abaixo).difference(livro.buffer(1.9, quad_segs=Q))
    olhos = unary_union([T(bez((x-3,44.6),(x,42.4),(x+3,44.6)), 1.4) for x in (-6.5, 6.5)])
    rosto = arred(rosto, 0.5).difference(olhos)
    face_rel = C(crc, 11.8).difference(cabeca.buffer(0.8, quad_segs=Q)).difference(ponteiros.buffer(0.01))
    brancos = unary_union(seps + [det, rosto]).intersection(dentro)
    preto = U.difference(brancos).difference(face_rel)
    branco = unary_union([brancos, face_rel])
    return S(preto), S(branco)

DESENHOS = {1:t1, 2:t2, 3:t3, 4:t4, 5:t5, 6:t6, 7:t7, 8:t8, 9:t9}
FUNDO = {1, 2, 3, 4, 5, 8}
