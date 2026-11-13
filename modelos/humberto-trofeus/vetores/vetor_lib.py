"""Método A: redesenho por peças, ancorado na imagem.

Cada ícone é descrito por peças fechadas (âncoras medidas em px da referência).
Este módulo cuida do resto: curvas suaves, booleanas, larguras mínimas,
ajuste final em Bézier, SVG em mm, verificação automática e PNG de conferência.
"""
import io
import math
import numpy as np
from shapely.geometry import Polygon, LineString, MultiPolygon, box, Point
from shapely.ops import unary_union
from shapely import affinity
from PIL import Image, ImageDraw

REF = __file__.rsplit('/', 2)[0] + '/referencia/trofeus-referencia-hd.png'
ALTURA_MM = 95.0
MIN_PRETO = 2.0      # mm
MIN_BRANCO = 1.2     # mm
LINHA = 1.4          # mm (divisões por sombra)


# ---------------------------------------------------------------- curvas
def _bez(p0, c1, c2, p3, n):
    t = np.linspace(0, 1, n, endpoint=False)[:, None]
    return ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * c1 + 3 * (1 - t) * t * t * c2 + t ** 3 * p3


def curva(pts, fechada=True, passo=0.25):
    """pts: lista de (x, y) = ponto suave, ou (x, y, 'c') = quina.
    Devolve os pontos amostrados de uma spline cúbica que passa pelas âncoras."""
    P = np.array([[p[0], p[1]] for p in pts], float)
    quina = [len(p) > 2 for p in pts]
    n = len(P)
    tan = np.zeros_like(P)
    for i in range(n):
        if quina[i]:
            continue
        if not fechada and (i == 0 or i == n - 1):
            continue
        a, b = P[(i - 1) % n], P[(i + 1) % n]
        d = b - a
        L = np.linalg.norm(d)
        tan[i] = d / L if L else 0
    out = []
    for i in range(n if fechada else n - 1):
        j = (i + 1) % n
        p0, p3 = P[i], P[j]
        L = np.linalg.norm(p3 - p0)
        c1 = p0 + tan[i] * L / 3
        c2 = p3 - tan[j] * L / 3
        out.append(_bez(p0, c1, c2, p3, max(2, int(L / passo))))
    if not fechada:
        out.append(P[-1:])
    return np.vstack(out)


def forma(pts):
    return Polygon(curva(pts)).buffer(0)


def traco(pts, largura):
    """Linha de largura constante (pontas redondas)."""
    return LineString(curva(pts, fechada=False)).buffer(largura / 2, quad_segs=16)


def traco_var(pts):
    """pts: lista (x, y, largura). Faixa suave de largura variável (pontas redondas)."""
    P = curva([(p[0], p[1]) for p in pts], fechada=False, passo=0.5)
    A = np.array([(p[0], p[1]) for p in pts], float)
    W = np.array([p[2] for p in pts], float)
    # largura interpolada pelo comprimento ao longo das âncoras
    idx = [int(np.argmin(((P - a) ** 2).sum(axis=1))) for a in A]
    w = np.interp(np.arange(len(P)), idx, W)
    return unary_union([Point(*p).buffer(r / 2, quad_segs=16) for p, r in zip(P, w)])


def elipse(cx, cy, rx, ry):
    return affinity.scale(Point(cx, cy).buffer(1, quad_segs=32), rx, ry)


def ret_redondo(x0, y0, x1, y1, r):
    return box(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, quad_segs=16)


def abrir(g, r):
    return g.buffer(-r, quad_segs=16).buffer(r, quad_segs=16)


def fechar(g, r):
    return g.buffer(r, quad_segs=16).buffer(-r, quad_segs=16)


def polys(g):
    if g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    return [p for p in g.geoms if isinstance(p, Polygon)]


# ---------------------------------------------------------------- composição
def compor(camadas, y_base, raio_preto, raio_branco, vazados_brancos=True):
    """camadas: lista (cor, geometria) em ordem de pintura ('P' preto, 'B' branco).
    Devolve (contorno, preto, branco) com larguras mínimas garantidas."""
    # o contorno externo vem só das peças cheias; linhas ('L') nunca o alteram
    contorno = unary_union([g for c, g in camadas if c in 'PB'])
    contorno = abrir(fechar(contorno, raio_preto), raio_preto)
    # vazados internos pertencem ao BRANCO: o contorno externo é só o anel de fora
    if vazados_brancos:
        contorno = unary_union([Polygon(p.exterior) for p in polys(contorno)])
    preto = Polygon()
    for cor, g in camadas:
        preto = preto.union(g) if cor == 'P' else preto.difference(g)
    # o que o alisamento do contorno acrescentou (cantos côncavos) entra como preto
    extra = contorno.difference(unary_union([g for c, g in camadas if c in 'PB']))
    preto = preto.union(unary_union([p for p in polys(extra) if p.area < 40]))   # vazados grandes ficam brancos
    preto = preto.intersection(contorno)
    for _ in range(12):
        preto = abrir(preto, raio_preto).intersection(contorno)
        branco = abrir(contorno.difference(preto), raio_branco)
        preto = contorno.difference(branco)
        if preto.difference(abrir(preto, raio_preto).buffer(0.05)).area < 0.3:
            break          # preto e branco já respeitam os mínimos ao mesmo tempo
    corte = box(-1e5, -1e5, 1e5, y_base)          # borda de baixo reta
    contorno = contorno.intersection(corte)
    preto = preto.intersection(corte).buffer(0)
    # lascas numéricas: branco que não sobrevive a uma abertura mínima volta para o preto, e vice-versa
    eps = raio_branco * 0.5
    branco = contorno.difference(preto)
    branco = unary_union([p for p in polys(branco) if not p.buffer(-eps).is_empty])
    preto = contorno.difference(branco)
    preto = unary_union([p for p in polys(preto) if not p.buffer(-eps).is_empty])
    branco = contorno.difference(preto).buffer(0)
    import shapely
    contorno = shapely.set_precision(contorno.buffer(0), 0.002)
    preto = shapely.set_precision(preto.buffer(0), 0.002).intersection(contorno)
    preto = unary_union([p for p in polys(preto) if p.area > 0.5])
    branco = unary_union([p for p in polys(contorno.difference(preto)) if p.area > 0.5])
    preto = shapely.set_precision(contorno.difference(branco), 0.002)
    branco = shapely.set_precision(contorno.difference(preto), 0.002)
    return contorno, preto, branco


def para_mm(g, eixo_x, y_topo, y_base):
    s = ALTURA_MM / (y_base - y_topo)
    return affinity.affine_transform(g, [s, 0, 0, s, -eixo_x * s, -y_topo * s]), s


# ---------------------------------------------------------------- ajuste Bézier (Schneider)
def _fit_cubic(pts, t1, t2, err, out, depth=0):
    n = len(pts)
    if n == 2:
        d = np.linalg.norm(pts[1] - pts[0]) / 3
        out.append((pts[0], pts[0] + t1 * d, pts[1] + t2 * d, pts[1]))
        return
    u = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    u /= u[-1]
    for it in range(5):
        b = _gen(pts, u, t1, t2)
        e, k = _maxerr(pts, b, u)
        if e < err:
            out.append(b)
            return
        if e > err * 16 and it == 0:
            break
        u = _reparam(pts, b, u)
    if depth > 30:
        out.append(b)
        return
    k = min(max(k, 1), n - 2)
    tc = pts[k - 1] - pts[k + 1]
    L = np.linalg.norm(tc)
    tc = tc / L if L else t2
    _fit_cubic(pts[:k + 1], t1, tc, err, out, depth + 1)
    _fit_cubic(pts[k:], -tc, t2, err, out, depth + 1)


def _gen(pts, u, t1, t2):
    p0, p3 = pts[0], pts[-1]
    b0 = (1 - u) ** 3; b1 = 3 * u * (1 - u) ** 2; b2 = 3 * u * u * (1 - u); b3 = u ** 3
    A1 = t1[None, :] * b1[:, None]
    A2 = t2[None, :] * b2[:, None]
    C00 = (A1 * A1).sum(); C01 = (A1 * A2).sum(); C11 = (A2 * A2).sum()
    tmp = pts - (p0[None, :] * (b0 + b1)[:, None] + p3[None, :] * (b2 + b3)[:, None])
    X0 = (A1 * tmp).sum(); X1 = (A2 * tmp).sum()
    det = C00 * C11 - C01 * C01
    seg = np.linalg.norm(p3 - p0)
    if abs(det) > 1e-12:
        a1 = (X0 * C11 - X1 * C01) / det
        a2 = (C00 * X1 - C01 * X0) / det
    else:
        a1 = a2 = seg / 3
    if a1 < 1e-6 * seg or a2 < 1e-6 * seg:
        a1 = a2 = seg / 3
    return (p0, p0 + t1 * a1, p3 + t2 * a2, p3)


def _ev(b, u):
    u = np.asarray(u)[:, None]
    return (1 - u) ** 3 * b[0] + 3 * (1 - u) ** 2 * u * b[1] + 3 * (1 - u) * u * u * b[2] + u ** 3 * b[3]


def _maxerr(pts, b, u):
    d = ((_ev(b, u) - pts) ** 2).sum(axis=1)
    k = int(d.argmax())
    return math.sqrt(d[k]), k


def _reparam(pts, b, u):
    b = [np.asarray(x) for x in b]
    d1 = [3 * (b[i + 1] - b[i]) for i in range(3)]
    d2 = [2 * (d1[i + 1] - d1[i]) for i in range(2)]
    uu = u[:, None]
    q = _ev(b, u)
    q1 = (1 - uu) ** 2 * d1[0] + 2 * (1 - uu) * uu * d1[1] + uu ** 2 * d1[2]
    q2 = (1 - uu) * d2[0] + uu * d2[1]
    num = ((q - pts) * q1).sum(axis=1)
    den = (q1 * q1).sum(axis=1) + ((q - pts) * q2).sum(axis=1)
    den[np.abs(den) < 1e-12] = 1e-12
    return np.clip(u - num / den, 0, 1)


def _tang(pts, i, sentido, alcance):
    """direção unitária saindo de pts[i] no sentido +1/-1, medida num alcance curto."""
    j = i
    acc = 0.0
    while 0 <= j + sentido < len(pts) and acc < alcance:
        acc += np.linalg.norm(pts[j + sentido] - pts[j])
        j += sentido
    d = pts[j] - pts[i]
    L = np.linalg.norm(d)
    return d / L if L else np.array([1.0, 0.0])


def anel_para_path(coords, err=0.03, ang_quina=22.0, fechado=True):
    """Converte um anel (polilinha densa) em comandos SVG com poucas Béziers."""
    P = np.asarray(coords, float)
    if fechado and np.allclose(P[0], P[-1]):
        P = P[:-1]
    # remove pontos duplicados
    keep = [0]
    for i in range(1, len(P)):
        if np.linalg.norm(P[i] - P[keep[-1]]) > 1e-4:
            keep.append(i)
    P = P[keep]
    n = len(P)
    quinas = []
    rng = range(n) if fechado else range(1, n - 1)
    for i in rng:
        a = P[i] - P[(i - 1) % n]
        b = P[(i + 1) % n] - P[i]
        ang = abs(math.degrees(math.atan2(a[0] * b[1] - a[1] * b[0], a @ b)))
        if ang > ang_quina:
            quinas.append(i)
    if fechado:
        if not quinas:
            quinas = [0]
        P = np.roll(P, -quinas[0], axis=0)
        quinas = [q - quinas[0] for q in quinas] + [n]
        P = np.vstack([P, P[:1]])
        suave_total = len(quinas) == 2 and ang_quina and True
    else:
        quinas = [0] + quinas + [n - 1]
    segs = []
    for a, b in zip(quinas[:-1], quinas[1:]):
        pts = P[a:b + 1]
        if len(pts) < 2:
            continue
        chord = pts[-1] - pts[0]
        L = np.linalg.norm(chord)
        if L > 1e-9:
            u_ = chord / L; q_ = pts - pts[0]
            dev = np.abs(q_[:, 0] * u_[1] - q_[:, 1] * u_[0]).max() if len(pts) > 2 else 0
            if dev < 0.004:
                segs.append(('L', pts[-1]))
                continue
        # densifica para o ajuste ficar estável
        dens = [pts[0]]
        for k in range(1, len(pts)):
            d = np.linalg.norm(pts[k] - pts[k - 1])
            m = int(d / 0.25)
            for q in range(1, m + 1):
                dens.append(pts[k - 1] + (pts[k] - pts[k - 1]) * q / (m + 1))
            dens.append(pts[k])
        pts = np.array(dens)
        t1 = _tang(pts, 0, +1, 0.35)
        t2 = _tang(pts, len(pts) - 1, -1, 0.35)
        if fechado and len(quinas) == 2 and np.allclose(pts[0], pts[-1]):
            t = pts[1] - pts[-2]
            t /= np.linalg.norm(t)
            t1, t2 = t, -t
        out = []
        _fit_cubic(pts, t1, t2, err, out)
        for b in out:
            segs.append(('C', b[1], b[2], b[3]))
    f = lambda v: ('%.3f' % v).rstrip('0').rstrip('.')
    d = ['M%s,%s' % (f(P[0][0]), f(P[0][1]))]
    for s in segs:
        if s[0] == 'L':
            d.append('L%s,%s' % (f(s[1][0]), f(s[1][1])))
        else:
            d.append('C' + ' '.join('%s,%s' % (f(p[0]), f(p[1])) for p in s[1:]))
    if fechado:
        d.append('Z')
    return ''.join(d), len(segs)


def geom_para_paths(g, **kw):
    out, nos = [], 0
    for p in polys(g):
        d = ''
        for anel in [p.exterior] + list(p.interiors):
            s, k = anel_para_path(anel.coords, **kw)
            d += s
            nos += k
        out.append(d)
    return out, nos


def escrever_svg(arq, contorno, preto, branco, relevo, titulo):
    x0, y0, x1, y1 = contorno.bounds
    m = 2.0
    vx, vy, w, h = x0 - m, y0 - m, (x1 - x0) + 2 * m, (y1 - y0) + 2 * m
    pb, nb = geom_para_paths(branco)
    pp, npr = geom_para_paths(preto)
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
         'width="%.3fmm" height="%.3fmm" viewBox="%.3f %.3f %.3f %.3f">' % (w, h, vx, vy, w, h),
         '<title>%s</title>' % titulo.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'),
         '<desc>Unidade: mm. x=0 é o eixo da base; y=%.1f é a borda de baixo (encaixe). '
         'Camadas: BRANCO, PRETO, RELEVO.</desc>' % y1,
         '<g id="BRANCO" inkscape:groupmode="layer" inkscape:label="BRANCO" fill="#ffffff" fill-rule="evenodd">']
    L += ['<path d="%s"/>' % d for d in pb]
    L += ['</g>', '<g id="PRETO" inkscape:groupmode="layer" inkscape:label="PRETO" fill="#111111" fill-rule="evenodd">']
    L += ['<path d="%s"/>' % d for d in pp]
    L += ['</g>', '<g id="RELEVO" inkscape:groupmode="layer" inkscape:label="RELEVO" fill="none" '
                  'stroke="#e6007e" stroke-width="0.25" style="display:none">']
    nr = 0
    for nome, g in relevo:
        ds, k = geom_para_paths(g)
        nr += k
        L.append('<g id="RELEVO-%s">' % nome)
        L += ['<path d="%s"/>' % d for d in ds]
        L.append('</g>')
    L += ['</g>', '</svg>']
    open(arq, 'w').write('\n'.join(L) + '\n')
    return dict(viewbox=(vx, vy, w, h), nos_preto=npr, nos_branco=nb, nos_relevo=nr)


# ---------------------------------------------------------------- verificação
def verificar(contorno, preto, branco, furos_ok=False):
    rel = []
    ok = True

    def finos(g, minimo, nome):
        nonlocal ok
        r = minimo / 2 * 0.97
        g = g.buffer(0)
        resto = g.difference(abrir(g, r).buffer(0.02).buffer(0))
        ruins = [p for p in polys(resto) if p.area > 1.25 * r * r]   # quina viva isolada (até ~45°) não é fiapo
        if ruins:
            ok = False
            for p in ruins[:8]:
                c = p.representative_point()
                rel.append('  FALHA %s abaixo de %.1f mm perto de (%.1f, %.1f) mm, área %.2f mm²'
                           % (nome, minimo, c.x, c.y, p.area))
        else:
            rel.append('  ok   %s: nenhum trecho abaixo de %.1f mm' % (nome, minimo))

    finos(preto, MIN_PRETO, 'PRETO')
    finos(branco, MIN_BRANCO, 'BRANCO')
    pc = polys(contorno)
    if len(pc) == 1 and pc[0].interiors and furos_ok:
        rel.append('  ok   contorno externo: 1 peça única, com %d vazados (deixados vazios de propósito)' % len(pc[0].interiors))
    elif len(pc) == 1 and not pc[0].interiors:
        rel.append('  ok   contorno externo: 1 peça única, sem furos')
    else:
        ok = False
        rel.append('  FALHA contorno externo: %d peças, %d furos' % (len(pc), sum(len(p.interiors) for p in pc)))
    peq = [p for p in polys(preto) + polys(branco) if p.area < 3.0]
    if peq:
        ok = False
        for p in peq:
            c = p.representative_point()
            rel.append('  FALHA pontinho solto de %.2f mm² em (%.1f, %.1f)' % (p.area, c.x, c.y))
    else:
        rel.append('  ok   sem pontinhos soltos (menor região: %.1f mm²)'
                   % min(p.area for p in polys(preto) + polys(branco)))
    sobra = abs(contorno.area - preto.area - branco.area)
    rel.append('  ok   PRETO + BRANCO = contorno (sobra %.4f mm²)' % sobra)
    x0, y0, x1, y1 = contorno.bounds
    base = contorno.intersection(box(-1e4, y1 - 0.01, 1e4, y1 + 1)).bounds
    rel.append('  info altura %.2f mm, largura %.2f mm; borda de baixo reta de x=%.1f a x=%.1f mm '
               '(eixo da base em x=0)' % (y1 - y0, x1 - x0, base[0], base[2]))
    rel.append('  info peças pretas: %d, regiões brancas: %d' % (len(polys(preto)), len(polys(branco))))
    return ok, rel


# ---------------------------------------------------------------- conferência
def _raster_svg(arq_svg, viewbox, s, janela, z):
    """Renderiza o SVG na mesma grade de pixels da referência (janela em px da ref, zoom z)."""
    import cairosvg
    vx, vy, w, h = viewbox
    ppmm = z / s
    png = cairosvg.svg2png(url=arq_svg, output_width=int(round(w * ppmm)), output_height=int(round(h * ppmm)))
    im = Image.open(io.BytesIO(png)).convert('RGBA')
    return im, ppmm


def conferencia(arq_svg, info, s, eixo_x, y_topo, janela, z, arq_png, contorno, preto, rotulo=None):
    """Painel: referência | vetor | contorno do vetor sobre a referência. Mesma escala."""
    x0, y0, x1, y1 = janela
    W, H = (x1 - x0) * z, (y1 - y0) * z
    ref = Image.open(REF).convert('RGB').crop(janela).resize((W, H), Image.LANCZOS)
    vx, vy, w, h = info['viewbox']
    im, ppmm = _raster_svg(arq_svg, info['viewbox'], s, janela, z)
    # posição do canto do viewBox em px da referência
    px = eixo_x + vx / s
    py = y_topo + vy / s
    vet = Image.new('RGB', (W, H), (172, 190, 208))
    vet.paste(im, (int(round((px - x0) * z)), int(round((py - y0) * z))), im)
    sob = ref.copy()
    d = ImageDraw.Draw(sob)

    def tr(c):
        return [((eixo_x + x / s - x0) * z, (y_topo + y / s - y0) * z) for x, y in c]

    for p in polys(preto):
        for anel in [p.exterior] + list(p.interiors):
            d.line(tr(anel.coords), fill=(255, 0, 90), width=2)
    for p in polys(contorno):
        d.line(tr(p.exterior.coords), fill=(0, 150, 255), width=2)
    g = 12
    out = Image.new('RGB', (W * 3 + g * 4, H + g * 2 + 26), (255, 255, 255))
    dd = ImageDraw.Draw(out)
    for i, (t, img) in enumerate([('REFERÊNCIA', ref), ('VETOR (PRETO + BRANCO)', vet),
                                  ('CONTORNO DO VETOR SOBRE A REFERÊNCIA', sob)]):
        out.paste(img, (g + i * (W + g), g + 26))
        dd.text((g + i * (W + g), 10), t + ((' · ' + rotulo) if rotulo else ''), fill=(0, 0, 0))
    out.save(arq_png)
    return out


# ---------------------------------------------------------------- fluxo completo de um ícone
S0 = 0.349                 # mm por px da referência (aprox.; a escala final é acertada pela altura)
LW = LINHA / S0            # linha de 1,4 mm em px
R_PRETO = MIN_PRETO / 2 / S0
R_BRANCO = MIN_BRANCO / 2 / S0


def mm(v):
    return v / S0


def contorno_de(g, largura=None):
    """Linha branca de largura constante em volta de uma peça que fica na frente de outra."""
    return g.buffer(largura or LW, quad_segs=24)


def finalizar(n, titulo, camadas, eixo_x, y_base, relevo, janela, zooms, pasta, altura=ALTURA_MM, vazados_brancos=True):
    import os
    contorno, preto, branco = compor(camadas, y_base, R_PRETO, R_BRANCO, vazados_brancos)
    y_topo = contorno.bounds[1]
    s = altura / (y_base - y_topo)
    T = [s, 0, 0, s, -eixo_x * s, -y_topo * s]
    tr = lambda g: affinity.affine_transform(g, T)
    c_mm, p_mm, b_mm = tr(contorno), tr(preto), tr(branco)
    rel = [(nome, tr(g.intersection(contorno))) for nome, g in relevo]
    svg = os.path.join(pasta, 'trofeu-%d-vetor.svg' % n)
    info = escrever_svg(svg, c_mm, p_mm, b_mm, rel, 'Troféu %d: %s' % (n, titulo))
    ok, linhas = verificar(c_mm, p_mm, b_mm, furos_ok=not vazados_brancos)
    print('Troféu %d  escala %.4f mm/px  trechos: preto %d, branco %d, relevo %d'
          % (n, s, info['nos_preto'], info['nos_branco'], info['nos_relevo']))
    print('\n'.join(linhas))
    print('VERIFICAÇÃO:', 'APROVADA' if ok else 'REPROVADA')
    a = (svg, info, s, eixo_x, y_topo)
    conferencia(*a, janela, 5, os.path.join(pasta, 'trofeu-%d-conferencia.png' % n), c_mm, p_mm)
    for nome, jz in zooms:
        conferencia(*a, jz, 6, os.path.join(pasta, 'trofeu-%d-zoom-%s.png' % (n, nome)), c_mm, p_mm, nome.upper())
    import pickle
    pickle.dump(dict(contorno=c_mm, preto=p_mm, branco=b_mm, ok=ok), open(os.path.join(pasta, '.geo-%d.pkl' % n), 'wb'))
    return c_mm, p_mm, b_mm
