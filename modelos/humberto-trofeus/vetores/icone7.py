"""Troféu 7: camaleão no galho (todo preto, só o olho branco). Coordenadas em px da referência."""
import os
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
from vetor_lib import *

AQUI = os.path.dirname(os.path.abspath(__file__))
EIXO_X, Y_BASE = 541, 861

corpo = forma([(566, 622), (580, 620), (600, 625), (625, 639), (648, 659), (662, 679), (669, 689),
               (667, 696), (658, 704), (640, 711), (618, 716), (598, 716), (580, 714, 'c'),
               (565, 725), (552, 735), (535, 743), (520, 750), (505, 755, 'c'), (487, 758), (477, 768),
               (471, 785), (470, 800, 'c'), (455, 812, 'c'),
               (434, 790), (433, 765), (437, 738), (447, 708), (462, 682), (482, 662), (505, 650),
               (530, 645), (552, 645), (563, 648, 'c'), (561, 636), (562, 627)])
cauda = traco_var([(450, 770, 38), (451.5, 800, 37), (458, 832, 34), (478, 853, 28), (510, 860, 22),
                   (537, 850, 19), (547, 828, 18), (546, 806, 17), (533, 791, 16), (512, 790.5, 15),
                   (494, 799, 15), (488.5, 816, 15), (494, 829, 15), (508, 832, 14.5), (519, 826, 11),
                   (522.5, 816, 8.5), (518, 809, 7), (511.5, 810.5, 6.6)])
olho = Point(622, 665).buffer(14.5, quad_segs=32)

# patas
pata_tras = unary_union([traco_var([(512, 728, 34), (514, 752, 26), (516, 772, 24)]),
                         traco_var([(510, 776, 20), (528, 774, 17), (543, 768, 15)])])
pata_tras = fechar(pata_tras, 7)
pata_frente = unary_union([traco_var([(566, 702, 26), (570, 725, 23), (580, 742, 17), (596, 752, 15)]),
                           elipse(600, 757, 11, 16)])

# galho, haste e folha
galho = abrir(Polygon([(522, 768), (661, 732), (664, 741), (656, 752), (542, 786), (526, 786)]), 3)
haste = Polygon([(601, 768), (624, 762), (584, 880), (556, 880)])
folha = forma([(588, 812, 'c'), (600, 796), (620, 787), (640, 783), (656, 784.5, 'c'),
               (652, 801), (639, 816), (620, 826), (602, 829), (590, 823, 'c')])

camadas = [
    ('P', galho), ('P', haste), ('P', folha),
    ('P', cauda), ('P', corpo), ('P', pata_tras), ('P', pata_frente),
    ('B', olho),
]
relevo = [('corpo', corpo), ('pata-de-tras', pata_tras), ('pata-da-frente', pata_frente), ('cauda', cauda)]
finalizar(7, 'camaleão no galho', camadas, EIXO_X, Y_BASE, relevo,
          (422, 606, 682, 874), [('topo', (422, 608, 682, 715)), ('meio', (422, 695, 682, 800)),
                                 ('base', (422, 765, 682, 874))], AQUI, vazados_brancos=False)
