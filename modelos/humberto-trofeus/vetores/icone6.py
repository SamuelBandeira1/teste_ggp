"""Troféu 6: capacete com bandeira quadriculada. Coordenadas em px da referência."""
import os
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
from vetor_lib import *

AQUI = os.path.dirname(os.path.abspath(__file__))
EIXO_X, Y_BASE = 220, 858

# bandeira: malha 5 x 3 (nós medidos na referência); N[u][v], u = coluna, v = linha
DY = -6     # a bandeira sobe 6 px para a borda de baixo não encostar no filete do capacete
N = [[(198, 628), (192, 662), (184, 697), (176, 722)],
     [(237, 622), (228, 654), (219, 691), (214, 718)],
     [(272, 627), (266, 654), (257, 694), (251, 722)],
     [(308, 648), (301, 675), (292, 707), (288, 742)],
     [(333, 658), (327, 690), (321, 722), (314, 752)],
     [(358, 652), (351, 688), (346, 718), (341, 742)]]
N = [[(x, y + DY) for x, y in col] for col in N]
borda_malha = ([N[u][0] for u in range(6)] + [N[5][v] for v in (1, 2)] +
               [N[u][3] for u in range(5, -1, -1)] + [N[0][v] for v in (2, 1)])
cantos = {N[0][0], N[5][0], N[5][3], N[0][3]}
malha = forma([p + ('c',) if p in cantos else p for p in borda_malha])
bandeira = malha.buffer(8, join_style='mitre', mitre_limit=3)
casas = []
for u in range(5):
    for v in range(3):
        if (u + v) % 2 == 1:
            q = Polygon([N[u][v], N[u + 1][v], N[u + 1][v + 1], N[u][v + 1]])
            casas.append(q.buffer(-mm(0.5) - mm(1.2)).buffer(mm(1.2), quad_segs=16))
casas = unary_union(casas)

# capacete
capacete = forma([(128, 880, 'c'), (117.5, 842), (119, 825), (126, 800), (136, 775), (146, 757),
                  (159, 745), (180, 734), (205, 727), (232, 726), (258, 733), (280, 748), (295, 772),
                  (303, 800), (305, 825), (300, 846), (292, 880, 'c')])
viseira_br = forma([(153, 764, 'c'), (215, 762), (266, 764), (277, 773), (276, 787), (266, 803),
                    (250, 814), (220, 821), (180, 827), (135, 833.5, 'c'), (127.5, 829, 'c')])
viseira = forma([(158.5, 777, 'c'), (224, 780, 'c'), (231, 788), (226, 802), (214, 811), (139.5, 824, 'c')])
ventilacao = Point(249, 785).buffer(10.5, quad_segs=24).union(Polygon([(240, 788), (254, 795), (239, 804)]))
ventilacao = abrir(fechar(ventilacao, 5), 2.5)
faixa = Polygon([(206, 846.5), (288, 830.5), (280, 848), (206, 851.5)])

# filete branco que separa o capacete da bandeira (como na referência)
filete = capacete.buffer(mm(2.2), quad_segs=24).intersection(bandeira.buffer(1))

vao = Polygon([(166, 722), (214, 720), (251, 724), (283, 744), (283, 768), (150, 768), (150, 752)])   # vão claro entre a bandeira e o capacete

# branco entre capacete e bandeira: termina reto na linha da borda esquerda da bandeira e respeita a borda dela
corte_esq = Polygon([(175.5, 690), (400, 690), (400, 800), (152.5, 800)])
entre = unary_union([vao.difference(bandeira), filete]).intersection(corte_esq).difference(casas.buffer(mm(2.1)))

camadas = [
    ('P', bandeira), ('B', casas),
    ('B', entre),
    ('P', capacete), ('B', viseira_br), ('P', viseira), ('P', ventilacao), ('B', faixa),
]
relevo = [('capacete', capacete), ('bandeira', bandeira)]
finalizar(6, 'capacete com bandeira quadriculada', camadas, EIXO_X, Y_BASE, relevo,
          (105, 600, 385, 872), [('topo', (105, 602, 385, 705)), ('meio', (105, 690, 385, 790)),
                                 ('base', (105, 765, 385, 872))], AQUI)
