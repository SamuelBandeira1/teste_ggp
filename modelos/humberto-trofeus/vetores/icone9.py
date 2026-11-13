"""Troféu 9: pessoa lendo livro com relógio atrás. Coordenadas em px da referência."""
import os
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
from shapely import affinity
from vetor_lib import *

AQUI = os.path.dirname(os.path.abspath(__file__))
EIXO_X, Y_BASE = 1191, 858
CX = 1186                      # eixo de simetria do leitor e do livro
esp = lambda g: affinity.scale(g, -1, 1, origin=(CX, 0))

# relógio
C = (1262, 695)
aro = Point(*C).buffer(90, quad_segs=64)
mostrador = Point(*C).buffer(74, quad_segs=64)
ponteiros = unary_union([traco([(1265, 635, 'c'), (1265, 684, 'c')], 10.5),
                         traco([(1265, 684, 'c'), (1313, 664.5, 'c')], 10.5)])

# leitor
cabelo = elipse(CX, 738, 79, 95).intersection(box(0, 0, 2000, 739.5))
rosto = Polygon([(1136, 730), (1236, 730), (1236, 741), (1200, 751), (CX, 763), (1172, 751), (1136, 741)])
franja = traco([(1133, 741, 'c'), (1150, 716, 'c'), (1163, 728.5, 'c'), (CX, 706, 'c'),
                (1209, 728.5, 'c'), (1222, 716, 'c'), (1239, 741, 'c')], LW)

# livro
capa_e = Polygon([(1090, 752), (1120, 757), (1172, 772), (CX, 778), (CX, 880), (1172, 880), (1092, 827)])
livro = abrir(capa_e.union(esp(capa_e)), 3)
pagina_e = Polygon([(1091, 745.5), (1150, 743), (1176, 749), (CX, 762), (CX, 777), (1172, 772.5), (1120, 757.5), (1091, 753.5)])
paginas = pagina_e.union(esp(pagina_e))
lombada = unary_union([traco([(1172, 771, 'c'), (1172, 880, 'c')], LW), traco([(1200, 771, 'c'), (1200, 880, 'c')], LW)])
joelhos = unary_union([elipse(1131, 862, 40, 30), elipse(1243, 862, 42, 30)])

camadas = [
    ('P', aro), ('B', mostrador), ('P', ponteiros),
    ('P', joelhos), ('P', livro), ('B', paginas),
    ('P', rosto), ('P', cabelo),
    ('L', franja), ('L', lombada),
]
relevo = [('cabeca', cabelo.union(rosto)), ('livro', livro), ('relogio', aro)]
finalizar(9, 'pessoa lendo livro com relógio atrás', camadas, EIXO_X, Y_BASE, relevo,
          (1075, 598, 1365, 872), [('topo', (1075, 600, 1365, 705)), ('meio', (1075, 690, 1365, 795)),
                                   ('base', (1075, 765, 1365, 872))], AQUI)
