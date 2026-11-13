"""Troféu 8: haltere com folhas, óculos redondos e raio. Coordenadas em px da referência."""
import os
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
from shapely import affinity
from vetor_lib import *

AQUI = os.path.dirname(os.path.abspath(__file__))
EIXO_X, Y_BASE = 874, 860

# óculos redondos
ARO = mm(3.3)
aro_e, aro_d = Point(861, 708).buffer(36, quad_segs=48), Point(950.5, 708).buffer(36, quad_segs=48)
lente_e, lente_d = Point(861, 708).buffer(36 - ARO, quad_segs=48), Point(950.5, 708).buffer(36 - ARO, quad_segs=48)
ponte = traco([(890, 704, 'c'), (898, 698.5), (905.7, 697), (913.5, 698.5), (921.5, 704, 'c')], ARO)
haste = ret_redondo(981, 700, 993, 714, 4)

# raio
raio = Polygon([(914, 613.5), (921, 617), (913, 643), (931.5, 645), (931.5, 650), (903, 688), (898.5, 686),
                (906, 660.5), (887, 659), (887, 654.5)])

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
rodape = box(772, 851, 948, 880)

pretos = [aro_e, aro_d, ponte, haste, raio, folha_g, folha_p, talos, barra, anilhas, rodape]
# o branco segura as partes soltas (raio, óculos): preenche os vãos estreitos entre as peças
fundo = fechar(unary_union(pretos), 34)
# embaixo da barra fica vazado, como na referência (senão o branco parece ser a barra)
vao_barra = affinity.rotate(box(HC[0] - 44, HC[1] + 11, HC[0] + 42, HC[1] + 80), ANG, origin=HC)
fundo = fundo.difference(vao_barra)

camadas = [('B', fundo)] + [('P', g) for g in pretos] + [('B', lente_e), ('B', lente_d), ('L', nervura)]
relevo = [('oculos', unary_union([aro_e, aro_d, ponte, haste])), ('raio', raio),
          ('folhas', unary_union([folha_g, folha_p])), ('haltere', unary_union([barra, anilhas]))]
finalizar(8, 'haltere com folhas, óculos redondos e raio', camadas, EIXO_X, Y_BASE, relevo,
          (742, 604, 1002, 874), [('topo', (742, 606, 1002, 715)), ('meio', (742, 690, 1002, 800)),
                                  ('base', (742, 765, 1002, 874))], AQUI, vazados_brancos=False)
