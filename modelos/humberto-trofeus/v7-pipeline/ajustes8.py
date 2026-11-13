"""Ajustes por peça sobre o traçado do VTracer (v8). Desenhos em px da referência (u, v da grade de medição)."""
import numpy as np
from shapely.geometry import Point, Polygon, LineString, box
from shapely.ops import unary_union
from shapely import affinity
import desenho6 as d6
from desenho6 import C, E, RR, T, arred, bez, cub, catmull, esp, Q
S = 0.352
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

def a3(p, b, f, cv):
    tabua = arred(Polygon([(-101,233),(-9,286),(109,240),(42,203),(-58,207)]), 5)
    copa = RR(-56, 175, 63, 212, 6)
    cordao = RR(-91, 186, -84, 236, 3); no = E((-87.5, 187), 10, 6)
    borla = arred(Polygon([(-95,184),(-80,184),(-76,150),(-99,150)]), 5)
    livro_c = RR(-110, 52, -30, 90, 13); folhas_c = RR(-94, 60, -20, 73, 6.5).intersection(box(-200, 0, -32, 300))
    livro_b = RR(-118, 21, 10, 56, 15); folhas_b = RR(-101, 29, 15, 43, 7).intersection(box(-200, 0, -2, 300))
    chapeu = cv(unary_union([tabua, copa, cordao, no, borla]))
    livros = cv(unary_union([livro_c, livro_b])); folhas = cv(unary_union([folhas_c, folhas_b]))
    zona = cv(unary_union([tabua.buffer(3), box(-125, 150, -70, 240), livro_c.buffer(3), livro_b.buffer(3)]))
    menina = p.difference(zona)
    linha_aba = cv(tabua).exterior.buffer(0.45).intersection(cv(copa))
    p2 = unary_union([menina, chapeu.difference(linha_aba), livros.difference(folhas).difference(menina.buffer(1.0))])
    b2 = unary_union([b.difference(zona), folhas.difference(menina.buffer(1.0)), linha_aba])
    return p2, b2.difference(p2), f

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
    # moldura do escudo em vetor (simétrica); mãos e dedos vêm da referência
    lado = cub((106,150),(106,92),(62,44),(0,20))
    ext = np.vstack([[(0,289),(98,247)], [(106,236)], lado, np.array(LineString(lado[::-1]).coords)*[-1,1], [(-106,236),(-98,247)]])
    esc = arred(Polygon(ext).buffer(0), 4)
    dentro = arred(esc.buffer(-18, quad_segs=Q, join_style='mitre'), 3)
    curva = Polygon(np.vstack([[(-130,214)], [(-40,170)], cub((-40,170),(-24,193),(30,194),(52,170))[1:], [(130,215),(130,-60),(-130,-60)]]))
    ESC, DEN, CUR = cv(esc), cv(dentro), cv(curva)
    massa = DEN.intersection(CUR)
    vaos = massa.buffer(-0.6).difference(p)
    vaos = vaos.buffer(-0.25).buffer(0.25)
    faixa_topo = CUR.exterior.buffer(4.0).intersection(box(-200, cv(box(0, 120, 1, 121)).bounds[1], 200, 300))
    vaos = vaos.difference(faixa_topo).buffer(-0.2).buffer(0.2)      # linha das mangas fica lisa
    vaos = unary_union([g for g in (vaos.geoms if hasattr(vaos, 'geoms') else [vaos]) if g.area > 1.0])
    p2 = unary_union([ESC.difference(DEN), massa.difference(vaos)])
    return p2, DEN.difference(p2), f

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
