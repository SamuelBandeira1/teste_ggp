"""Troféu 5: xícara de café com óculos. Coordenadas em px da referência."""
import os
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
from shapely import affinity
from vetor_lib import *

AQUI = os.path.dirname(os.path.abspath(__file__))
EIXO_X, Y_BASE = 1290, 414

# xícara
borda = elipse(1278, 255, 68, 13)
cafe = elipse(1278, 262.5, 50, 6.5)
corpo = Polygon([(1210, 255), (1346, 255), (1342, 350), (1338, 440), (1236, 440), (1216, 350)])
alca = elipse(1346, 308, 41, 39)
furo_alca = elipse(1346, 311, 23, 23).difference(box(0, 0, 1348.5, 999))
pe = box(1236, 398, 1347, 440)

# vapor (as pontas de baixo entram na borda para a peça ficar inteira)
vapor_e = forma([(1254, 174, 'c'), (1253, 185), (1252, 196), (1262, 208), (1270, 222), (1267, 236),
                 (1263, 249, 'c'), (1251, 249, 'c'), (1256, 232), (1254, 220), (1243, 208), (1237, 196), (1240, 184)])
vapor_d = forma([(1298, 153, 'c'), (1297, 165), (1293, 178), (1296, 190), (1305, 203), (1309, 216), (1305, 230),
                 (1298, 248, 'c'), (1285, 248, 'c'), (1291, 230), (1291, 216), (1281, 204), (1272, 190),
                 (1272, 177), (1281, 163)])

# óculos: modelo simétrico, depois inclinado como na referência
OC, ANG = (1286, 370), 3.2
lente_d = forma([(17, -12), (22, -19), (45, -20.5), (66, -19), (72, -12), (70, 2), (62, 15),
                 (48, 22), (33, 21), (22, 13), (17, 0)])
lente_e = affinity.scale(lente_d, -1, 1, origin=(0, 0))
lentes = unary_union([lente_d, lente_e])
armacao = fechar(unary_union([lentes.buffer(mm(3.0), quad_segs=24), box(-12, -26.5, 12, -11)]), 9)
hastes = unary_union([ret_redondo(79, -30, 97, -9, 4), ret_redondo(-97, -30, -79, -9, 4)])
fundo_oc = fechar(armacao.buffer(mm(2.6), quad_segs=24).union(hastes), 3)
pos = lambda g: affinity.rotate(affinity.translate(g, *OC), ANG, origin=OC)
lentes, armacao, fundo_oc = pos(lentes), pos(armacao), pos(fundo_oc)

camadas = [
    ('P', vapor_e), ('P', vapor_d),
    ('P', alca), ('B', furo_alca),
    ('P', corpo), ('P', borda), ('B', cafe), ('P', pe),
    ('P', fundo_oc), ('B', armacao), ('P', lentes),
]
relevo = [('oculos', fundo_oc), ('borda-da-xicara', borda)]
finalizar(5, 'xícara de café com óculos', camadas, EIXO_X, Y_BASE, relevo,
          (1180, 142, 1402, 428), [('topo', (1180, 144, 1402, 255)), ('meio', (1180, 235, 1402, 345)),
                                   ('base', (1180, 322, 1402, 428))], AQUI)
