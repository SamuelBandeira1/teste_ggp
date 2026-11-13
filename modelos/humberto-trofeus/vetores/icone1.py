"""Troféu 1: engrenagem com monitor </> e chave inglesa. Coordenadas em px da referência."""
import os, math
import numpy as np
from shapely.geometry import Polygon, box, Point, LineString
from shapely.ops import unary_union
from shapely import affinity
from vetor_lib import *

AQUI = os.path.dirname(os.path.abspath(__file__))
EIXO_X, Y_BASE = 247, 420

# engrenagem: 8 dentes iguais em volta de um centro
C = (235, 262)
R_FURO, R_CORPO, R_DENTE = 62, 87, 113
dente = Polygon([(-27, -(R_CORPO - 6)), (-22, -R_DENTE), (22, -R_DENTE), (27, -(R_CORPO - 6))])
dente = abrir(dente.buffer(3, quad_segs=12).buffer(-3), 0.1)
eng = Point(0, 0).buffer(R_CORPO, quad_segs=48)
for k in range(8):
    eng = eng.union(affinity.rotate(dente, 45 * k, origin=(0, 0)))
eng = fechar(eng, 4)                       # raiz dos dentes arredondada
eng = affinity.translate(eng, *C)
furo = Point(*C).buffer(R_FURO, quad_segs=48)

# monitor
monitor = ret_redondo(137, 254, 297, 372, 11)
moldura = ret_redondo(150, 265, 286, 364, 6)
tela = ret_redondo(159, 274.5, 277, 351.5, 2.5)
G = mm(2.2)
g_menor = traco([(198.5, 298.5, 'c'), (179.5, 313, 'c'), (198.5, 327.5, 'c')], G)
g_barra = traco([(225, 296, 'c'), (211.5, 331.5, 'c')], G)
g_maior = traco([(238.5, 298.5, 'c'), (257.5, 313, 'c'), (238.5, 327.5, 'c')], G)

# base do notebook
base_nb = forma([(140, 366, 'c'), (121, 380), (124, 391), (133, 394, 'c'), (250, 394, 'c'), (250, 366, 'c')])
base_nb = abrir(base_nb, 3)
base_br = abrir(Polygon([(141, 373.5), (240, 373.5), (240, 384.5), (129, 384.5)]), 2)

# pés
pe_e = Polygon([(186, 388), (212, 388), (197, 430), (171, 430)])
pe_d = Polygon([(280, 380), (301, 380), (324, 430), (297, 430)])

suporte = Polygon([(192, 388), (294, 380), (324, 430), (170, 430)])   # pé único e reto sobre a base

# chave inglesa (peça paramétrica ao longo do eixo A→B)
A, B = np.array([233.0, 406.0]), np.array([322.0, 328.0])
u = (B - A) / np.linalg.norm(B - A)
RW, HW, T, BOCA = 24.5, 10.5, mm(2.5), 9.5
ch_br = unary_union([Point(*A).buffer(RW, quad_segs=32), Point(*B).buffer(RW, quad_segs=32),
                     LineString([A, B]).buffer(HW, cap_style='flat')])
ch_br = fechar(ch_br, 5)                   # concordância suave entre haste e cabeça
for P, d in ((A, -u), (B, u)):
    boca = LineString([P + d * 1.0, P + d * 60]).buffer(BOCA, quad_segs=24)
    ch_br = ch_br.difference(boca)
ch_br = abrir(ch_br.difference(box(0, 413.5, 999, 999)), 2.5)   # o branco para antes da borda de apoio
ch_pr = unary_union([ch_br.buffer(T, quad_segs=24), Point(*A).buffer(RW + T, quad_segs=32),
                     Point(*B).buffer(RW + T, quad_segs=32)])

camadas = [
    ('P', eng), ('B', furo),
    ('P', suporte),
    ('L', contorno_de(unary_union([monitor, base_nb]))),
    ('P', base_nb), ('B', base_br),
    ('P', monitor), ('B', moldura), ('P', tela),
    ('L', g_menor), ('L', g_barra), ('L', g_maior),
    ('L', contorno_de(ch_pr)), ('P', ch_pr), ('B', ch_br),
]
relevo = [('monitor', unary_union([monitor, base_nb])), ('chave', ch_pr)]
finalizar(1, 'engrenagem com monitor </> e chave inglesa', camadas, EIXO_X, Y_BASE, relevo,
          (110, 138, 362, 432), [('topo', (110, 140, 362, 250)), ('meio', (110, 240, 362, 350)),
                                 ('base', (110, 325, 362, 432))], AQUI)
