"""Troféu 7: camaleão no galho (todo preto, só o olho branco). Coordenadas em px da referência."""
import os
import numpy as np
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
from vetor_lib import *

AQUI = os.path.dirname(os.path.abspath(__file__))
EIXO_X, Y_BASE = 541, 861

import math
corpo = forma([(566, 622), (580, 620), (600, 625), (625, 639), (648, 659), (662, 679), (669, 689),
               (667, 696), (658, 704), (640, 711), (618, 716), (598, 716), (580, 714, 'c'),
               (565, 725), (552, 735), (535, 743), (520, 750), (505, 755, 'c'), (487, 758), (477, 768),
               (471, 785), (470, 800, 'c'), (452, 806, 'c'), (433.5, 792, 'c'),
               (433.5, 776), (434.5, 760), (437, 738), (447, 708), (462, 682), (482, 662), (505, 650),
               (530, 645), (552, 645), (563, 648, 'c'), (561, 636), (562, 627)])

# cauda: espiral logarítmica regular (raio e largura diminuem de forma contínua)
CE = (511, 815)
def esp_pt(f):
    r = 58.0 * math.exp(-0.9515 * f)             # 58 px na esquerda; 0,386x a cada volta
    a = math.radians(180 - 360 * f)
    return CE[0] + r * math.cos(a), CE[1] + r * math.sin(a)
def esp_w(f):
    return float(np.interp(f, [0, .25, .5, .75, 1, 1.25, 1.5, 1.72], [37, 27, 19.5, 16.5, 14, 11.5, 9, 7]))
cauda = traco_var([(452.5, 790, 38)] +
                  [esp_pt(f) + (esp_w(f),) for f in np.arange(0, 1.7201, 0.04)])
olho = Point(622, 665).buffer(14.5, quad_segs=32)

# patas
pata_tras = traco_var([(509, 728, 36), (512, 750, 27), (515, 768, 23), (517, 777, 22)])
pata_frente = traco_var([(566, 702, 26), (570, 725, 23), (581, 742, 17), (598, 753, 16), (601, 760, 19)])

# galho, haste e folha
galho = abrir(Polygon([(522, 768), (661, 732), (664, 741), (656, 752), (542, 786), (526, 786)]), 3)
haste = Polygon([(601, 768), (624, 762), (584, 880), (556, 880)])
folha = forma([(588, 812, 'c'), (600, 796), (620, 787), (640, 783), (656, 784.5, 'c'),
               (652, 801), (639, 816), (620, 826), (602, 829), (590, 823, 'c')])
uniao = fechar(unary_union([galho, haste, folha, pata_tras, pata_frente]), 4)   # encontros com concordância

camadas = [
    ('P', uniao), ('P', galho), ('P', haste), ('P', folha),
    ('P', cauda), ('P', corpo), ('P', pata_tras), ('P', pata_frente),
    ('B', olho),
]
relevo = [('corpo', corpo), ('pata-de-tras', pata_tras), ('pata-da-frente', pata_frente), ('cauda', cauda)]
finalizar(7, 'camaleão no galho', camadas, EIXO_X, Y_BASE, relevo,
          (422, 606, 682, 874), [('topo', (422, 608, 682, 715)), ('meio', (422, 695, 682, 800)),
                                 ('base', (422, 765, 682, 874))], AQUI, vazados_brancos=False)
