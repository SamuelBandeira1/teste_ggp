"""Ajustes por peça sobre o traçado do VTracer (v8). Desenhos em px da referência (u, v da grade de medição)."""
import numpy as np
from shapely.geometry import Point, Polygon, LineString, box
from shapely.ops import unary_union
from shapely import affinity
import desenho6 as d6
from desenho6 import C, E, RR, T, arred, bez, cub, catmull, esp, Q
S = 0.352
import shapely as _shp
def ok(g): return _shp.set_precision(_shp.make_valid(g).buffer(0), 0.002)
TOPO = d6.TOPO
def conv(i, apoio):
    """px da grade (u, v) -> mm da peça"""
    return lambda g: affinity.scale(affinity.translate(g, 0, apoio - TOPO[i]), S, S, origin=(0, 0))

def a1(p, b, f, cv):
    gc = (-14, 161)
    a, bb = np.array((-12, 22)), np.array((80, 98)); d = (bb-a)/np.linalg.norm(bb-a); n = np.array((-d[1], d[0]))
    def cabeca(c, s):
        c = np.array(c); h = C(tuple(c), 24)
        boca = Polygon([tuple(c+s*d*5+n*8), tuple(c+s*d*34+n*8), tuple(c+s*d*34-n*8), tuple(c+s*d*5-n*8)])
        return h.difference(boca.union(C(tuple(c+s*d*5), 8)))
    chave = cv(arred(unary_union([T([tuple(a), tuple(bb)], 20), cabeca(a, -1), cabeca(bb, 1)]), 2))
    gap = chave.buffer(1.1, quad_segs=Q)
    p2 = unary_union([p.difference(gap), chave])
    b2 = unary_union([b, gap.difference(chave).intersection(p.buffer(0.5))])
    return p2, b2.difference(p2), f

def refinar(p, br, fio=0.45, curva=0.6, min_area=1.5):
    """acabamento: tira fiapos (brancos e pretos mais finos que 2*fio mm), arredonda cantos e remove pontinhos"""
    def limpa(g, a):
        g = ok(g)
        return ok(unary_union([q for q in (g.geoms if hasattr(g, 'geoms') else [g]) if q.area > a]))
    C = ok(unary_union([p, br]))
    C = ok(C.buffer(curva, quad_segs=24).buffer(-2*curva, quad_segs=24).buffer(curva, quad_segs=24))   # contorno externo liso
    W = ok(br.intersection(C))
    W = ok(W.buffer(-fio, quad_segs=24).buffer(fio, quad_segs=24))          # some fiapo branco
    W = ok(W.buffer(fio, quad_segs=24).buffer(-fio, quad_segs=24))          # some fiapo preto dentro do branco
    W = limpa(W.buffer(curva/2, quad_segs=24).buffer(-curva/2, quad_segs=24), min_area).intersection(C.buffer(-0.01))
    P = ok(C.difference(W))
    P = limpa(ok(P.buffer(-fio, quad_segs=24).buffer(fio, quad_segs=24)).union(P.intersection(C.difference(C.buffer(-fio*2.2)))), min_area)
    W = ok(C.difference(P))
    return P, W

def fiel(p, r_fecho=1.5, faixa_base=4.0):
    """método aprovado: preto = traçado pelo limiar do branco; branco = tudo dentro do contorno que não é preto"""
    p = ok(p)
    if faixa_base > 0:
        faixa = box(-80, -5, 80, faixa_base)      # tira lasquinhas da borda da base que grudaram embaixo
        p = ok(unary_union([p.difference(faixa), ok(p.intersection(faixa).buffer(-0.9, quad_segs=16).buffer(0.9, quad_segs=16)).intersection(faixa)]))
    p = unary_union([g for g in (p.geoms if hasattr(p, 'geoms') else [p]) if g.area > 2.0])
    fech = ok(p.buffer(r_fecho, quad_segs=16).buffer(-r_fecho, quad_segs=16))
    contorno = ok(unary_union([Polygon(g.exterior) for g in (fech.geoms if hasattr(fech, 'geoms') else [fech])]))
    return p, ok(contorno.difference(p))

def a3(p, b, f, cv):
    p = ok(p)
    # o livro de baixo passa à frente da base na foto: fecha a borda de baixo dele, reta, na largura do livro
    livro = p.intersection(box(-80, 0, -1, 6)).bounds
    if len(livro) == 4:
        p = ok(unary_union([p, box(livro[0] + 2.5, 0, livro[2], 1.6).buffer(0.8, quad_segs=16).intersection(box(-80, 0, 80, 3))]))
    p, br = fiel(p, r_fecho=3.0, faixa_base=0)
    # linhas brancas que demarcam o chapéu, medidas com zoom na referência (em mm, já no sistema da peça)
    linhas = unary_union([
        T([(-19.3,79.0),(0.9,81.4),(22.5,78.6)], 1.4),     # topo da copa / aba
        T([(-32.5,71.0),(-19.3,66.3)], 1.4),               # borda de baixo da aba (esquerda)
        T([(23.0,68.6),(36.5,74.0)], 1.4),                 # borda de baixo da aba (direita)
        T([(1.4,79.6),(1.4,61.2)], 1.4),                   # quina da frente da copa
        T(bez((-18.8,59.8),(1.6,59.6),(22.7,59.4)), 1.4),  # base da copa
    ])
    linhas = ok(linhas.intersection(p.buffer(-1.0)))
    P, W = refinar(ok(p.difference(linhas)), ok(unary_union([br, linhas])))
    # embaixo (pontas do cabelo): some com os pedacinhos brancos irregulares entre as pontas e o corpo
    from shapely.geometry import Point as _Pt
    gs = list(W.geoms) if hasattr(W, 'geoms') else [W]
    rosto = [g for g in gs if g.contains(_Pt(10, 12))]
    zona = ok(unary_union([box(-6.5, -1, 8, 5.5), box(21, -1, 40, 14)]))
    lixo = [ok(W.intersection(zona).difference(unary_union(rosto).buffer(0.3) if rosto else Polygon()))] + [g for g in gs if g.area < 8 and g.centroid.y < 9]
    if lixo:
        L = ok(unary_union(lixo)).buffer(0.05)
        tudo = ok(unary_union([P, W]))
        W = ok(W.difference(L)); P = ok(unary_union([P, L]).intersection(tudo))
        P, W = refinar(P, W)
    return P, W, f

def a6(p, b, f, cv):
    b = b.buffer(-0.45).buffer(0.45)                    # tira o risco fino de brilho no topo do capacete
    friso = cv(T(cub((-42,-9),(-5,-6),(35,-3),(66,2)), 5)).intersection(p.buffer(-0.8))
    return p.difference(friso), unary_union([b, friso]), f

def a7(p, b, f, cv):
    boca = cv(T(bez((82,187),(100,183),(116,186)), 3.2)).intersection(p.buffer(-0.8))
    return p.difference(boca), unary_union([b, boca]), f

def a8(p, b, f, cv):
    # anilhas e barra: traçado com limiar mais baixo, que mantém os vãos brancos entre as anilhas
    import vetor, camadas
    H = int(open('i8_altura.txt').read())
    p105 = vetor.ler('i8_preto105.svg', H).buffer(0)
    zona = cv(unary_union([RR(20,0,115,135,0), RR(-135,0,-45,100,0), T([(-58,62),(40,80)], 26)]))
    folhas = p.difference(zona)
    p2 = unary_union([folhas, p105.intersection(zona)])
    p2 = p2.buffer(0.25).buffer(-0.25)
    return p2, b.difference(zona).difference(p2), f

def a4(p, b, f, cv):
    cc, ang = (-50, 69), 6.5
    from desenho6 import rot
    def L(g): return rot(affinity.translate(g, *cc), ang, cc)
    ext = L(RR(-43, -47, 43, 47, 10)); face = L(RR(-34, -38, 34, 38, 5))
    visor = L(RR(-26, 12, 26, 31, 3.5))
    teclas = unary_union([L(RR(x-7, y-6.5, x+7, y+6.5, 3)) for x in (-19, 0, 19) for y in (-7, -27)])
    calc = cv(unary_union([ext.difference(face), visor, teclas])); face_b = cv(face.difference(unary_union([visor, teclas])))
    zona = cv(ext.buffer(2))
    p2 = unary_union([p.difference(zona), calc])
    return p2, unary_union([b.difference(zona), face_b]).difference(p2), f

def a2(p, b, f, cv):
    # traçado fiel (limiar do branco). Branco = tudo dentro do escudo que não é preto
    # (painel, contorno do polegar, vãos dos dedos e o "V" entre os braços que encostam na base)
    p = ok(p)
    faixa = box(-80, -5, 80, 4)       # tira as lasquinhas finas da borda da base que grudaram embaixo
    p = ok(unary_union([p.difference(faixa), ok(p.intersection(faixa).buffer(-0.9, quad_segs=16).buffer(0.9, quad_segs=16)).intersection(faixa)]))
    bracos = sorted([g for g in (lambda q: q.geoms if hasattr(q, 'geoms') else [q])(p.intersection(box(-60, 0, 60, 3))) if g.area > 0.5], key=lambda g: g.bounds[0])
    xi, xf = (bracos[0].bounds[2], bracos[-1].bounds[0]) if len(bracos) >= 2 else (-1, 1)
    fechado = ok(unary_union([p, box(xi - 0.5, -5, xf + 0.5, 3)]))   # fecha só o vão entre os dois braços
    gs = [g for g in (fechado.geoms if hasattr(fechado, 'geoms') else [fechado])]
    contorno = ok(Polygon(max(gs, key=lambda g: g.area).exterior))
    return p, ok(contorno.difference(p)), f

def a9(p, b, f, cv):
    cabeca = E((-6, 148), 79, 90).intersection(box(-200, 148, 200, 400))
    cabeca = arred(cabeca, 6)
    rosto = arred(Polygon([(-56,150),(-38,173),(-24,164),(-5,179),(12,164),(24,173),(43,150),(26,138),(-5,117),(-37,138)]), 2)
    # relógio: círculo pelos pontos medidos
    pts = np.array([(72,273),(143,192),(104,104)], float)
    A = np.array([[2*(pts[1]-pts[0])[0], 2*(pts[1]-pts[0])[1]], [2*(pts[2]-pts[0])[0], 2*(pts[2]-pts[0])[1]]])
    bv = np.array([pts[1]@pts[1]-pts[0]@pts[0], pts[2]@pts[2]-pts[0]@pts[0]]); cc = np.linalg.solve(A, bv)
    rr = np.linalg.norm(pts[0]-cc)
    anel = C(tuple(cc), rr).difference(C(tuple(cc), rr-16))
    ponteiros = unary_union([T([(76,247),(76,201)], 10), T([(84,198),(122,218)], 10)])
    capa_e = arred(Polygon([(-103,130),(-20,111),(-20,40),(-100,54)]), 6)
    capa_d = arred(Polygon([(93,134),(14,112),(14,42),(96,58)]), 6)
    lombada = RR(-21, 32, 15, 110, 9)
    paginas = unary_union([Polygon([(-96,131),(-20,114),(-8,121),(-8,127),(-20,121),(-94,138)]),
                           Polygon([(86,136),(14,115),(2,121),(2,127),(14,122),(84,143)])]).buffer(1.5).buffer(-1.5)
    colo = RR(-100, 25, 96, 62, 24)
    livro = unary_union([capa_e, capa_d, lombada])
    frente = unary_union([livro, paginas])
    preto_v = unary_union([anel.difference(cabeca.buffer(4)).difference(frente.buffer(3)), ponteiros,
                           cabeca.difference(frente.buffer(2)), livro, colo.difference(livro.buffer(2.5))])
    linhas = unary_union([capa_e.exterior.buffer(1.3).intersection(lombada), capa_d.exterior.buffer(1.3).intersection(lombada),
                          rosto.exterior.buffer(1.4).intersection(cabeca.buffer(-2)).difference(frente.buffer(2.5))])
    preto_v = preto_v.difference(linhas)
    branco_v = unary_union([paginas.difference(livro), linhas, C(tuple(cc), rr-16).difference(cabeca.buffer(4)).difference(frente.buffer(3)).difference(ponteiros)])
    return cv(preto_v), cv(branco_v).difference(cv(preto_v)), f

AJUSTES = {1: a1, 2: a2, 3: a3, 4: a4, 6: a6, 7: a7, 8: a8, 9: a9}
