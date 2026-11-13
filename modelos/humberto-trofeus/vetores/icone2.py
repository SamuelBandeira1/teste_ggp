"""Troféu 2: escudo com aperto de mão. Coordenadas em px da referência."""
import os
import numpy as np
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
from vetor_lib import *

AQUI = os.path.dirname(os.path.abspath(__file__))
EIXO_X, Y_BASE = 501, 421
CX = 500.5                     # eixo de simetria do escudo


def espelhar(meio):
    """meio: âncoras do lado esquerdo, do topo até a ponta de baixo (ambos no eixo)."""
    dir_ = [((2 * CX - p[0]), p[1]) + tuple(p[2:]) for p in meio[-2:0:-1]]
    return forma(list(meio) + dir_)


fora = espelhar([(CX, 151, 'c'), (450, 181.5), (412, 196), (398, 200), (392.5, 205.5), (391, 215),
                 (391, 290), (396, 322), (410, 351), (432, 379), (462, 402.5), (CX, 421.5, 'c')])
dentro = espelhar([(CX, 181, 'c'), (421, 214, 'c'), (421, 300, 'c'), (423.5, 322), (434, 347),
                   (454, 372), (477, 392), (CX, 404.5, 'c')])
rodape = box(457.5, 412, 543.5, 440)

# mão de cima (vem da manga direita, com o polegar à esquerda)
mao_cima = forma([(452, 300), (458, 285), (468, 272), (480, 263.5), (495, 258.5), (510, 257.5), (530, 260),
                  (550, 266.5, 'c'), (594, 236, 'c'), (606, 236, 'c'), (606, 316, 'c'), (581, 318, 'c'),
                  (563, 336.5, 'c'), (545, 319), (523, 297.5), (510, 288.5), (498, 288), (486, 296),
                  (474, 308.5), (464, 313), (456, 311), (452, 305.5)])
FILETE = mm(2.2)
filete = mao_cima.buffer(FILETE, quad_segs=24).intersection(dentro)

# mão de baixo (vem da manga esquerda, dedos para baixo e para a direita)
palma = forma([(396, 236, 'c'), (406, 236, 'c'), (448, 266, 'c'), (466, 266, 'c'), (470, 272, 'c'),
               (535, 300, 'c'), (535, 322, 'c'), (523, 333, 'c'), (497, 366, 'c'), (491, 377, 'c'),
               (479.6, 372.9, 'c'), (447.5, 345, 'c'), (436, 333, 'c'), (421, 322, 'c'), (396, 322, 'c')])
DEDO = 12.5
dedos = unary_union([traco([(a, b, 'c'), (c, d, 'c')], DEDO) for a, b, c, d in [
    (515, 317.5, 549.5, 346.5), (503, 331, 537, 359.5), (490, 342.5, 522.5, 369.5), (478, 353.5, 508, 378.5)]])
mao_baixo = palma.union(dedos)

# nós dos dedos da outra mão
nos = unary_union([Point(447.5 + 10.7 * k, 345 + 9.3 * k).buffer(8, quad_segs=24) for k in range(4)])
filete_nos = nos.buffer(mm(1.5), quad_segs=24)

camadas = [
    ('P', fora), ('P', rodape), ('B', dentro),
    ('P', mao_baixo.intersection(fora)),
    ('L', filete_nos), ('P', nos),
    ('L', filete), ('P', mao_cima.intersection(fora)),
]
relevo = [('mao-de-cima', mao_cima.intersection(fora)), ('mao-de-baixo', mao_baixo.intersection(dentro)), ('nos', nos)]
finalizar(2, 'escudo com aperto de mão', camadas, EIXO_X, Y_BASE, relevo,
          (376, 140, 626, 432), [('topo', (376, 142, 626, 250)), ('meio', (376, 228, 626, 340)),
                                 ('base', (376, 318, 626, 432))], AQUI)
