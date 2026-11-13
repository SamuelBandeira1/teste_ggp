"""Troféu 3: menina de orelhas de gato, chapéu de formatura e livros.
Todas as coordenadas abaixo são px da referência (trofeus-referencia-hd.png)."""
import os
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from vetor_lib import *

AQUI = os.path.dirname(os.path.abspath(__file__))
EIXO_X = 766          # centro da base (referencia/LEIAME.md)
Y_BASE = 424          # linha onde o ícone encosta na base
S0 = 95 / 272.5       # mm por px (aprox.; a escala final é acertada pela altura real)
LW = LINHA / S0       # linha de 1,4 mm em px
HALO = 2.8 / S0       # halo da menina: 2,8 mm constantes
HALO_CABECA = 1.7 / S0  # linha branca entre cabeça e orelhas

# ------------------------------------------------------------ chapéu
tampo = Polygon([(763, 151.5), (875, 198), (871, 207), (831, 225),
                 (710, 229.5), (673, 214), (668, 203)])
faixa = Polygon([(710, 200), (831, 200), (831, 253), (710, 257)])
l_quina = traco([(710, 229.5, 'c'), (710, 213, 'c'), (765, 183, 'c'), (831, 207, 'c'), (831, 225, 'c')], LW)
l_aresta = traco([(765.3, 183, 'c'), (769, 246, 'c')], LW)
l_faixa_corpo = traco([(705, 256.5), (740, 248), (770, 245), (802, 246.5), (836, 252.5)], LW)

# ------------------------------------------------------------ cordão e borla
cordao = box(673, 205, 686, 246)
no = elipse(679.5, 249, 10.5, 7.5)
borla = forma([(671, 254, 'c'), (688, 254, 'c'), (689.5, 268), (690.5, 282),
               (687, 288.5), (671.5, 288.5), (667.5, 282), (669, 268)])
l_cordao = traco([(664, 212.6, 'c'), (694, 225.2, 'c')], LW).intersection(box(672, 200, 687, 240))
l_no1 = traco([(664, 243, 'c'), (695, 243, 'c')], LW)
l_no2 = traco([(664, 255.5, 'c'), (695, 255.5, 'c')], LW)

# ------------------------------------------------------------ corpo escuro de trás
corpo = forma([(710, 257, 'c'), (703, 269), (698, 284), (694, 305), (692, 325), (692, 350, 'c'),
               (692, 440, 'c'), (835, 440, 'c'), (835, 300, 'c'), (830, 281, 'c'), (844, 267, 'c'),
               (831, 252, 'c'), (831, 240, 'c'), (710, 240, 'c')])

# ------------------------------------------------------------ livros
livro1 = ret_redondo(657, 346, 790, 385, 16)
pag1 = ret_redondo(673, 360, 790, 376, 6)
livro2 = ret_redondo(649, 387, 800, 425, 16).union(box(700, 400, 800, 440))
pag2 = ret_redondo(665.5, 398, 800, 412, 6)

# ------------------------------------------------------------ menina
cabeca = forma([(800, 291), (818, 294), (834, 304), (846, 317), (855, 333), (860, 349), (866, 367),
                (873, 386, 'c'), (858, 375, 'c'), (852, 391), (841, 404, 'c'), (834, 396, 'c'),
                (800, 408), (766, 396, 'c'), (758, 403, 'c'), (750, 389), (744, 374, 'c'),
                (722, 383, 'c'), (730, 362), (736, 345), (741, 330), (748, 314), (760, 300), (780, 293)])
orelha_e = forma([(726, 271, 'c'), (743, 279), (759, 294, 'c'), (770, 310, 'c'), (748, 335, 'c'),
                  (733, 329, 'c'), (725.5, 310), (723.5, 290)])
orelha_d = forma([(861, 266, 'c'), (866, 284), (865, 304), (858, 323, 'c'), (840, 325, 'c'),
                  (818, 300, 'c'), (822, 291, 'c'), (841, 277)])
vestido = forma([(776, 396, 'c'), (832, 396, 'c'), (839, 410), (842, 440, 'c'), (755, 440, 'c'), (762, 410)])
menina = unary_union([cabeca, orelha_e, orelha_d, vestido])
halo = menina.buffer(HALO, quad_segs=24)
# contorno externo liso do lado direito: preenche as reentrâncias do halo (entre a ponta do cabelo e o vestido)
halo = halo.union(fechar(halo, 6.0 / S0).intersection(box(805, 0, 2000, 2000)))
orelhas = unary_union([orelha_e, orelha_d]).difference(cabeca.buffer(HALO_CABECA, quad_segs=24))
rosto = forma([(759, 359, 'c'), (759, 373), (764, 386), (779, 395), (800, 398), (822, 395),
               (837, 386), (843, 373), (843, 360, 'c'), (814, 331, 'c'), (796, 362, 'c'), (778, 334, 'c')])
ESP_OLHO = 2.1 / S0
olho_e = traco([(767.5, 370, 'c'), (771, 365), (776, 363.5), (781, 365), (784.5, 370, 'c')], ESP_OLHO)
olho_d = traco([(810.5, 370, 'c'), (814.5, 365), (820, 363.5), (825.5, 365), (829.5, 370, 'c')], ESP_OLHO)

# ------------------------------------------------------------ ordem de pintura
camadas = [
    ('P', corpo), ('P', faixa), ('P', tampo),
    ('P', cordao), ('P', no), ('P', borla),
    ('L', l_quina), ('L', l_aresta), ('L', l_faixa_corpo),
    ('L', l_cordao), ('L', l_no1), ('L', l_no2),
    ('P', livro1), ('B', pag1), ('P', livro2), ('B', pag2),
    ('B', halo), ('P', orelhas), ('P', cabeca), ('P', vestido),
    ('B', rosto), ('P', olho_e), ('P', olho_d),
]

contorno, preto, branco = compor(camadas, Y_BASE, MIN_PRETO / 2 / S0, MIN_BRANCO / 2 / S0)
y_topo = contorno.bounds[1]
contorno_mm, s = para_mm(contorno, EIXO_X, y_topo, Y_BASE)
preto_mm, _ = para_mm(preto, EIXO_X, y_topo, Y_BASE)
branco_mm, _ = para_mm(branco, EIXO_X, y_topo, Y_BASE)


def rel(g):
    g = g.intersection(contorno)
    return para_mm(g, EIXO_X, y_topo, Y_BASE)[0]


relevo = [
    ('menina', rel(halo)),
    ('cabeca', rel(cabeca)),
    ('livros', rel(unary_union([livro1, livro2]).difference(halo))),
    ('borla', rel(unary_union([no, borla]))),
]

svg = os.path.join(AQUI, 'trofeu-3-vetor.svg')
info = escrever_svg(svg, contorno_mm, preto_mm, branco_mm, relevo,
                    'Troféu 3: menina de orelhas de gato, chapéu de formatura e livros')
ok, linhas = verificar(contorno_mm, preto_mm, branco_mm)
print('Troféu 3  escala %.4f mm/px  nós: preto %d, branco %d, relevo %d'
      % (s, info['nos_preto'], info['nos_branco'], info['nos_relevo']))
print('\n'.join(linhas))
print('VERIFICAÇÃO:', 'APROVADA' if ok else 'REPROVADA')

a = (svg, info, s, EIXO_X, y_topo)
conferencia(*a, (636, 140, 890, 436), 5, os.path.join(AQUI, 'trofeu-3-conferencia.png'), contorno_mm, preto_mm)
conferencia(*a, (655, 145, 885, 262), 6, os.path.join(AQUI, 'trofeu-3-zoom-topo.png'), contorno_mm, preto_mm, 'TOPO')
conferencia(*a, (655, 240, 885, 350), 6, os.path.join(AQUI, 'trofeu-3-zoom-meio.png'), contorno_mm, preto_mm, 'MEIO')
conferencia(*a, (636, 330, 890, 436), 6, os.path.join(AQUI, 'trofeu-3-zoom-base.png'), contorno_mm, preto_mm, 'BASE')
