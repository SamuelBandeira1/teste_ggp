"""Troféu 8: haltere com folhas, óculos redondos e raio. Coordenadas em px da referência."""
import os
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
from shapely import affinity
from vetor_lib import *

AQUI = os.path.dirname(os.path.abspath(__file__))
EIXO_X, Y_BASE = 874, 874

# óculos redondos
ARO = mm(3.3)
aro_e, aro_d = Point(861, 708).buffer(36, quad_segs=48), Point(950.5, 708).buffer(36, quad_segs=48)
lente_e, lente_d = Point(861, 708).buffer(36 - ARO, quad_segs=48), Point(950.5, 708).buffer(36 - ARO, quad_segs=48)
ponte = traco([(890, 704, 'c'), (898, 698.5), (905.7, 697), (913.5, 698.5), (921.5, 704, 'c')], ARO)
haste = ret_redondo(981, 700, 993, 714, 4)
oculos = fechar(unary_union([aro_e, aro_d, ponte, haste]), 5)   # concordância suave da ponte com os aros

# raio
raio = Polygon([(918, 612), (912.5, 644), (931.5, 646), (902, 689), (906.5, 660), (886.5, 658)])

# folhas e talos
folha_g = forma([(757, 702, 'c'), (776, 703), (800, 712), (819, 728), (828, 748), (827, 768), (822, 782, 'c'),
                 (806, 783), (790, 776), (773, 757), (761, 732)])
nervura = traco([(772, 716, 'c'), (790, 737), (806, 760), (818, 784, 'c')], LW)
folha_p = forma([(887, 750, 'c'), (887, 766), (880, 782), (866, 795), (850, 801), (835, 802, 'c'),
                 (834, 789), (841, 772), (855, 758), (872, 751)])
talos = unary_union([traco([(816, 780, 'c'), (826, 798), (833, 818), (837, 845), (839, 875, 'c')], mm(2.6)),
                     traco([(838, 800, 'c'), (834, 812), (834, 824, 'c')], mm(2.6))])

# haltere (modelo reto, depois inclinado como na referência)
HC, ANG = (862, 817), -10
def peca(u0, u1, v, r):
    return affinity.rotate(ret_redondo(HC[0] + u0, HC[1] - v, HC[0] + u1, HC[1] + v, r), ANG, origin=HC)
barra = peca(-50, 50, 11, 3)
anilhas = unary_union([peca(-80, -44, 41, 7), peca(-102, -84, 36, 6), peca(-118, -106, 24, 5),
                       peca(42, 78, 50, 7), peca(82, 102, 47, 6), peca(106, 121, 28, 5)])
haltere = fechar(unary_union([barra, anilhas, talos]), 5).difference(  # talos fundidos ao haltere, sem frestas
    fechar(anilhas, 5).symmetric_difference(anilhas).buffer(0.01)) if False else unary_union([barra, anilhas])
juncao = fechar(unary_union([barra, peca(-80, -44, 41, 7), talos.intersection(box(0, 0, 2000, 818))]), 5)
pretos = [oculos, raio, folha_g, folha_p, talos, juncao, barra, anilhas]
# placa branca retangular de cantos redondos, centrada no eixo da base: os elementos ficam todos dentro dela
placa = ret_redondo(EIXO_X - 137, 601, EIXO_X + 137, Y_BASE + 40, 24)

camadas = [('B', placa)] + [('P', g) for g in pretos] + [('B', lente_e), ('B', lente_d), ('L', nervura)]
relevo = [('placa', placa), ('oculos', oculos), ('raio', raio),
          ('folhas', unary_union([folha_g, folha_p])), ('haltere', unary_union([barra, anilhas]))]
finalizar(8, 'haltere com folhas, óculos redondos e raio', camadas, EIXO_X, Y_BASE, relevo,
          (730, 594, 1018, 884), [('topo', (730, 596, 1018, 705)), ('meio', (730, 685, 1018, 795)),
                                  ('base', (730, 770, 1018, 884))], AQUI)
