"""Troféu 4: sol sorrindo com calculadora e gráfico. Coordenadas em px da referência."""
import os, math
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
from shapely import affinity
from vetor_lib import *

AQUI = os.path.dirname(os.path.abspath(__file__))
EIXO_X, Y_BASE = 1030, 421

# sol
C = (1028, 247)
R_FORA, R_DENTRO, RAIO_W = 66, 55, 13
disco = Point(*C).buffer(R_FORA, quad_segs=48)
rosto = Point(*C).buffer(R_DENTRO, quad_segs=48)


def raio(ang, r1=62, r2=95):
    a = math.radians(ang)
    p = lambda r: (C[0] + r * math.cos(a), C[1] + r * math.sin(a))
    return traco([p(r1) + ('c',), p(r2) + ('c',)], RAIO_W)


raios = unary_union([raio(a) for a in (-88, -58, -22, 127, 158, 195, 232)])
E_OLHO = mm(2.4)
olho_e = traco([(994, 242, 'c'), (999, 234.5), (1005.5, 232), (1012, 234.5), (1017, 242, 'c')], E_OLHO)
olho_d = traco([(1040.5, 242, 'c'), (1045.5, 234.5), (1052, 232), (1058.5, 234.5), (1063.5, 242, 'c')], E_OLHO)
sorriso = traco([(1011, 263, 'c'), (1019, 272), (1030, 275.5), (1041, 272), (1049, 263, 'c')], mm(2.7))

# seta
haste = traco([(1010, 351, 'c'), (1035, 342), (1055, 331), (1075, 315), (1091, 297), (1106, 280, 'c')], 21)
ponta = Polygon([(1133, 249), (1087, 265), (1128, 299)])
seta = fechar(haste.union(ponta), 2)

# barras e rodapé
barras = unary_union([box(1030, 370, 1046, 440), box(1054, 352, 1079, 440), box(1088, 319, 1117, 440)])
rodape = box(1030, 412, 1117, 440)

# calculadora (retângulo inclinado)
CC, ANG = (986, 377), -7


def ret(u0, v0, u1, v1, r):
    g = ret_redondo(CC[0] + u0, CC[1] + v0, CC[0] + u1, CC[1] + v1, r)
    return affinity.rotate(g, ANG, origin=CC)


calc = ret(-44, -50, 44, 70, 9)
face = ret(-33, -40.5, 33, 32.5, 5)
visor = ret(-27, -32, 27, -15, 2.5)
teclas = unary_union([ret(u - 6.5, v - 5.5, u + 6.5, v + 5.5, 2.5) for v in (4.5, 22) for u in (-19, 0, 19)])

camadas = [
    ('P', raios), ('P', disco), ('B', rosto), ('P', olho_e), ('P', olho_d), ('P', sorriso),
    ('P', barras), ('P', rodape),
    ('P', seta), ('P', fechar(unary_union([disco.difference(rosto), seta]), 5).difference(rosto)),
    ('P', fechar(unary_union([box(1088, 319, 1117, 440), seta]), 3.5)),
    ('L', contorno_de(calc)), ('P', calc), ('B', face), ('P', visor), ('P', teclas),
]
relevo = [('seta', seta), ('calculadora', calc), ('sol', disco)]
finalizar(4, 'sol sorrindo com calculadora e gráfico', camadas, EIXO_X, Y_BASE, relevo,
          (915, 132, 1150, 432), [('topo', (915, 134, 1150, 240)), ('meio', (915, 225, 1150, 335)),
                                  ('base', (915, 318, 1150, 432))], AQUI)
