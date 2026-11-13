"""Gera os arquivos de impressão (.3mf) a partir dos vetores aprovados (.geo-N.pkl, em mm).

Mesmo padrão do troféu 2 da v9 e do PADRAO-ENCAIXE.md:
- peça deitada, costas na mesa (z = 0), frente para cima;
- parte "preto": 14 mm de espessura; parte "branco": 13 mm (1 mm rebaixado na frente);
- pino de 30 x 8 x 8 mm, centrado no eixo da base (x de -15 a +15), rente às costas (z de 0 a 8),
  saindo 8 mm abaixo da linha de apoio (y de -8 a 0). Igual em todos os troféus.
"""
import os, pickle, zipfile, uuid
import numpy as np
import trimesh
from shapely.geometry import box, Polygon
from shapely import affinity
from shapely.ops import unary_union

AQUI = os.path.dirname(os.path.abspath(__file__))
NOME = {1: 'engrenagem-codigo', 2: 'escudo-aperto-de-mao', 3: 'formatura-anime', 4: 'sol-calculadora-grafico',
        5: 'cafe-oculos', 6: 'capacete-bandeira', 7: 'camaleao', 8: 'haltere-folha-oculos', 9: 'leitura-relogio'}
ESP_PRETO, ESP_BRANCO = 14.0, 13.0
PINO_X, PINO_Y, PINO_Z = 15.0, 8.0, 8.0      # meia largura, altura para baixo, espessura
ENTRA = 0.3                                   # o pino entra 0,3 mm na peça para fundir com ela


def polys(g):
    if g.is_empty:
        return []
    return [p for p in (g.geoms if hasattr(g, 'geoms') else [g]) if p.geom_type == 'Polygon' and p.area > 0.05]


def prisma(g, h):
    ms = []
    for p in polys(g.simplify(0.01)):
        ms.append(trimesh.creation.extrude_polygon(p, h))
    return ms


def escrever_3mf(arq, partes):
    ns = ('xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
          'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06"')
    L = ['<?xml version="1.0" encoding="utf-8"?>', '<model %s unit="millimeter"><resources>' % ns]
    for i, (nome, m) in enumerate(partes, 1):
        L.append('<object id="%d" name="%s" type="model" p:UUID="%s"><mesh><vertices>' % (i, nome, uuid.uuid4()))
        L.append(''.join('<vertex x="%.4f" y="%.4f" z="%.4f"/>' % tuple(v) for v in m.vertices))
        L.append('</vertices><triangles>')
        L.append(''.join('<triangle v1="%d" v2="%d" v3="%d"/>' % tuple(f) for f in m.faces))
        L.append('</triangles></mesh></object>')
    L.append('</resources><build>')
    for i, (nome, m) in enumerate(partes, 1):
        L.append('<item objectid="%d" transform="1 0 0 0 1 0 0 0 1 0 0 0" p:UUID="%s" partnumber="%s"/>'
                 % (i, uuid.uuid4(), nome))
    L.append('</build></model>')
    with zipfile.ZipFile(arq, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model', '\n'.join(L))


def gerar(n):
    geo = pickle.load(open(os.path.join(AQUI, '.geo-%d.pkl' % n), 'rb'))
    assert geo['ok'], 'vetor %d não passou na verificação' % n
    alt = geo['contorno'].bounds[3]
    T = [1, 0, 0, -1, 0, alt]                 # y para cima, linha de apoio em y = 0
    preto = affinity.affine_transform(geo['preto'], T).buffer(0)
    branco = affinity.affine_transform(geo['branco'], T).buffer(0)
    encaixe = box(-PINO_X, 0, PINO_X, ENTRA)
    branco = branco.difference(encaixe).buffer(0)
    shells_p = prisma(preto, ESP_PRETO)
    pino = trimesh.creation.box(extents=(2 * PINO_X, PINO_Y + ENTRA, PINO_Z))
    pino.apply_translation((0, (ENTRA - PINO_Y) / 2, PINO_Z / 2))
    shells_b = prisma(branco, ESP_BRANCO)
    estanque = all(m.is_watertight for m in shells_p + shells_b + [pino])
    mp = trimesh.util.concatenate(shells_p + [pino])
    partes = [('preto', mp)]
    if shells_b:
        partes.append(('branco', trimesh.util.concatenate(shells_b)))
    os.makedirs(os.path.join(AQUI, '3mf'), exist_ok=True)
    arq = os.path.join(AQUI, '3mf', 'trofeu-%d-%s.3mf' % (n, NOME[n]))
    escrever_3mf(arq, partes)
    # conferência por medição
    bp = mp.bounds
    apoio = unary_union([preto, branco]).intersection(box(-PINO_X, 0, PINO_X, 0.6))
    cob = apoio.intersection(box(-PINO_X, 0.25, PINO_X, 0.35)).area / (2 * PINO_X * 0.1)
    vol_p = sum(m.volume for m in shells_p) + pino.volume
    vol_b = sum(m.volume for m in shells_b)
    print('Troféu %d  %-26s pino x %.2f a %.2f | y %.2f a 0 | z 0 a %.2f | altura %.2f | preto %.1f cm3, branco %.1f cm3 '
          '| malhas fechadas: %s | apoio sobre o pino: %d%%'
          % (n, NOME[n], pino.bounds[0][0], pino.bounds[1][0], pino.bounds[0][1], pino.bounds[1][2],
             bp[1][1], vol_p / 1000, vol_b / 1000, 'sim' if estanque else 'NÃO', round(cob * 100)))
    return arq


if __name__ == '__main__':
    import sys
    for n in ([int(a) for a in sys.argv[1:]] or range(1, 10)):
        gerar(n)
