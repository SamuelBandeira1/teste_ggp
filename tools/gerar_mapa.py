#!/usr/bin/env python3
"""
Gerador do mapa "Usina Aço Cearense" para o WorkAdventure.

Desenha o mapa inteiro em pixel art (Pillow), corta em tiles de 32x32,
remove tiles repetidos e grava:
  - map.json      -> mapa Tiled (formato JSON) que o WorkAdventure lê
  - tileset.png   -> imagem com todos os tiles usados
  - preview.png   -> imagem do mapa completo, só para visualizar

Uso:  python3 tools/gerar_mapa.py
"""
import hashlib
import json
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

T = 32                      # tamanho do tile
W, H = 66, 46               # tamanho do mapa em tiles
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

bg = Image.new("RGBA", (W * T, H * T), (0, 0, 0, 255))   # chão + objetos (abaixo do Woka)
fg = Image.new("RGBA", (W * T, H * T), (0, 0, 0, 0))     # copas, ponte rolante (acima do Woka)
dbg = ImageDraw.Draw(bg)
dfg = ImageDraw.Draw(fg)
col = [[False] * W for _ in range(H)]                       # colisões

NF = 128        # quadros do ciclo completo (128 x 125 ms = 16 s)
FRAME_MS = 125  # duração de cada quadro (ms)
LOOP = 8        # ciclo curto do fogo/faíscas (divide NF)
F = 0           # quadro sendo desenhado agora


def wave(phase=0.0):
    """Oscila de -1 a 1 a cada LOOP quadros."""
    return math.sin(((F % LOOP) + phase) * 2 * math.pi / LOOP)


def frnd(*seed):
    """Aleatório que muda a cada quadro (repete a cada LOOP)."""
    return random.Random(int(hashlib.md5(repr(seed).encode()).hexdigest()[:8], 16) + (F % LOOP) * 7919)


def seg(f, a, b):
    """Progresso 0..1 de f dentro do intervalo [a, b]."""
    return min(1.0, max(0.0, (f - a) / (b - a)))


def ease(t):
    return t * t * (3 - 2 * t)


def tri(period):
    """Vai de 0 a 1 e volta a 0 a cada 'period' quadros."""
    k = F % period
    return 1 - abs(2 * k / period - 1)


def font(size, weight="ExtraBold"):
    for p in (f"/usr/share/fonts/opentype/inter/Inter-{weight}.otf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


# ---------------------------------------------------------------- utilidades
def P(v):
    return int(round(v * T))


def rect(d, x, y, w, h, fill, outline=None, width=1):
    """Retângulo em coordenadas de tile (aceita frações)."""
    d.rectangle([P(x), P(y), P(x + w) - 1, P(y + h) - 1], fill=fill, outline=outline, width=width)


def prect(d, x0, y0, x1, y1, fill, outline=None):
    d.rectangle([x0, y0, x1, y1], fill=fill, outline=outline)


def solid(x, y, w=1, h=1):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if 0 <= xx < W and 0 <= yy < H:
                col[yy][xx] = True


def free(x, y, w=1, h=1):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            col[yy][xx] = False


def text(d, s, cx, cy, size, fill, outline=(0, 0, 0), stroke=2, weight="ExtraBold"):
    """Texto centralizado em (cx, cy) em coordenadas de tile."""
    f = font(size, weight)
    d.text((P(cx), P(cy)), s, font=f, fill=fill, anchor="mm",
           stroke_width=stroke if outline else 0, stroke_fill=outline)


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c[:3])


# ------------------------------------------------------------------ texturas
_tex = {}


def texture(name, v=0):
    key = (name, v)
    if key in _tex:
        return _tex[key]
    im = Image.new("RGBA", (T, T))
    d = ImageDraw.Draw(im)
    rnd = random.Random(int(hashlib.md5(f"{name}{v}".encode()).hexdigest()[:8], 16))
    if name == "grass":
        d.rectangle([0, 0, T, T], fill=(86, 148, 62))
        for _ in range(14):
            x, y = rnd.randrange(T), rnd.randrange(T)
            c = rnd.choice([(70, 126, 50), (104, 168, 74), (76, 138, 56)])
            d.line([x, y, x + rnd.choice([-1, 0, 1]), y - 2], fill=c)
        if v == 2:
            for _ in range(2):
                x, y = rnd.randrange(4, 28), rnd.randrange(4, 28)
                c = rnd.choice([(240, 220, 90), (240, 240, 240), (230, 120, 150)])
                d.point([(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)], fill=c)
    elif name == "asphalt":
        d.rectangle([0, 0, T, T], fill=(66, 70, 76))
        for _ in range(22):
            d.point((rnd.randrange(T), rnd.randrange(T)), fill=rnd.choice([(58, 62, 68), (78, 82, 88)]))
    elif name == "concrete":
        d.rectangle([0, 0, T, T], fill=(150, 153, 156))
        for _ in range(12):
            d.point((rnd.randrange(T), rnd.randrange(T)), fill=rnd.choice([(140, 143, 146), (160, 163, 166)]))
        d.line([0, T - 1, T, T - 1], fill=(136, 139, 142))
        d.line([T - 1, 0, T - 1, T], fill=(136, 139, 142))
    elif name == "grate":
        d.rectangle([0, 0, T, T], fill=(84, 86, 92))
        for i in range(0, T, 8):
            d.line([i, 0, i, T], fill=(64, 66, 72))
            d.line([0, i, T, i], fill=(64, 66, 72))
        for i in range(4, T, 8):
            for j in range(4, T, 8):
                d.point((i, j), fill=(104, 106, 112))
    elif name == "paving":
        d.rectangle([0, 0, T, T], fill=(198, 190, 174))
        for r in range(4):
            y = r * 8
            d.line([0, y, T, y], fill=(176, 168, 152))
            off = 0 if r % 2 == 0 else 8
            for x in range(off, T, 16):
                d.line([x, y, x, y + 7], fill=(176, 168, 152))
    elif name == "plaza":
        d.rectangle([0, 0, T, T], fill=(214, 206, 188))
        d.rectangle([0, 0, 15, 15], fill=(204, 196, 178))
        d.rectangle([16, 16, 31, 31], fill=(204, 196, 178))
        d.line([0, T - 1, T, T - 1], fill=(184, 176, 160))
        d.line([T - 1, 0, T - 1, T], fill=(184, 176, 160))
    elif name == "wood":
        d.rectangle([0, 0, T, T], fill=(176, 128, 82))
        for r in range(4):
            y = r * 8
            d.line([0, y, T, y], fill=(146, 102, 62))
            x = (r * 13 + v * 7) % T
            d.line([x, y, x, y + 7], fill=(146, 102, 62))
            d.line([0, y + 3, T, y + 3], fill=(184, 136, 90))
    elif name in ("carpet_blue", "carpet_gray", "carpet_green", "carpet_red"):
        base = {"carpet_blue": (48, 84, 140), "carpet_gray": (118, 122, 132),
                "carpet_green": (68, 118, 92), "carpet_red": (130, 52, 52)}[name]
        d.rectangle([0, 0, T, T], fill=base)
        for i in range(0, T, 4):
            for j in range((i // 4) % 2 * 2, T, 4):
                d.point((i, j), fill=shade(base, 1.1))
    elif name == "checker":
        d.rectangle([0, 0, T, T], fill=(228, 224, 214))
        d.rectangle([0, 0, 15, 15], fill=(196, 74, 56))
        d.rectangle([16, 16, 31, 31], fill=(196, 74, 56))
    elif name == "lobby":
        d.rectangle([0, 0, T, T], fill=(226, 222, 214))
        d.line([0, T - 1, T, T - 1], fill=(206, 202, 194))
        d.line([T - 1, 0, T - 1, T], fill=(206, 202, 194))
        d.line([2, 2, 6, 2], fill=(240, 238, 232))
    elif name == "walkway":
        d.rectangle([0, 0, T, T], fill=(60, 132, 86))
        for _ in range(8):
            d.point((rnd.randrange(T), rnd.randrange(T)), fill=(54, 120, 78))
    _tex[key] = im
    return im


def fill(x, y, w, h, name, variants=1):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            v = ((xx * 7 + yy * 13) % 11) % variants if variants > 1 else 0
            bg.paste(texture(name, v), (xx * T, yy * T))


# -------------------------------------------------------------------- paredes
WALLS = {
    # cap (topo), face, detalhe, rodapé
    "galpao": ((36, 46, 60), (58, 92, 138), (48, 78, 120), (30, 38, 50)),
    "office": ((92, 86, 80), (234, 228, 216), (214, 208, 196), (150, 126, 100)),
    "refeit": ((92, 86, 80), (238, 214, 170), (222, 196, 150), (150, 110, 70)),
}


def hwall(x, y, w, style, doors=()):
    cap, face, det, base = WALLS[style]
    for xx in range(x, x + w):
        if xx in doors:
            continue
        x0, y0 = xx * T, y * T
        prect(dbg, x0, y0, x0 + T - 1, y0 + 7, cap)
        prect(dbg, x0, y0 + 8, x0 + T - 1, y0 + T - 1, face)
        if style == "galpao":
            for i in range(0, T, 4):
                dbg.line([x0 + i, y0 + 8, x0 + i, y0 + T - 4], fill=det)
        else:
            dbg.line([x0, y0 + 20, x0 + T, y0 + 20], fill=det)
        prect(dbg, x0, y0 + T - 3, x0 + T - 1, y0 + T - 1, base)
        solid(xx, y)


def vwall(x, y, h, style, doors=()):
    cap, face, det, base = WALLS[style]
    for yy in range(y, y + h):
        if yy in doors:
            continue
        x0, y0 = x * T, yy * T
        prect(dbg, x0 + 6, y0, x0 + T - 7, y0 + T - 1, cap)
        prect(dbg, x0 + 9, y0, x0 + T - 10, y0 + T - 1, shade(cap, 1.35))
        solid(x, yy)


def building(x0, y0, x1, y1, style, top_doors=(), bottom_doors=(), left_doors=(), right_doors=()):
    hwall(x0, y0, x1 - x0 + 1, style, top_doors)
    hwall(x0, y1, x1 - x0 + 1, style, bottom_doors)
    vwall(x0, y0 + 1, y1 - y0 - 1, style, left_doors)
    vwall(x1, y0 + 1, y1 - y0 - 1, style, right_doors)


def plaque(x, y, w, s, fill_c=(250, 250, 250), bgc=(20, 54, 104), size=14):
    """Placa na face da parede."""
    rect(dbg, x + 0.05, y + 0.3, w - 0.1, 0.62, bgc, outline=(240, 200, 40), width=2)
    text(dbg, s, x + w / 2, y + 0.61, size, fill_c, outline=None)


def floor_label(x, y, s, size=22, c=(246, 200, 40)):
    text(dbg, s, x, y, size, c, outline=(40, 40, 40), stroke=3)


# -------------------------------------------------------------------- objetos
def glow(d, cx, cy, r, steps=((120, 20, 10), (200, 60, 10), (240, 120, 20), (255, 190, 60), (255, 240, 170))):
    n = len(steps)
    rnd = frnd(int(cx), int(cy))
    for i, c in enumerate(steps):
        rr = r * (1 - i / (n + 0.5))
        if i:
            rr *= 1 + 0.08 * wave(i * 1.7 + (cx + cy) % 7) + rnd.uniform(-0.04, 0.04)
        ox, oy = (rnd.randint(-1, 1), rnd.randint(-1, 1)) if i >= 2 else (0, 0)
        if i >= n - 2:
            c = shade(c, 1 + 0.06 * wave(i))
        d.ellipse([cx - rr + ox, cy - rr + oy, cx + rr + ox, cy + rr + oy], fill=c)


def sparks(d, x, y, w, h, n, seed):
    rnd = random.Random(seed * 1009 + (F % LOOP) * 7919)
    for _ in range(n):
        px, py = P(x) + rnd.randrange(P(w)), P(y) + rnd.randrange(P(h))
        c = rnd.choice([(255, 230, 120), (255, 180, 60), (255, 250, 200)])
        d.rectangle([px, py, px + 1, py + 1], fill=c)


def hazard_border(x, y, w, h):
    """Faixa zebrada amarela/preta pintada no chão (não colide)."""
    x0, y0, x1, y1 = P(x), P(y), P(x + w) - 1, P(y + h) - 1
    band = 6
    for (ax, ay, bx, by) in ((x0, y0, x1, y0 + band), (x0, y1 - band, x1, y1),
                             (x0, y0, x0 + band, y1), (x1 - band, y0, x1, y1)):
        im = Image.new("RGBA", (bx - ax + 1, by - ay + 1), (240, 196, 30, 255))
        di = ImageDraw.Draw(im)
        for k in range(-im.height, im.width + im.height, 10):
            di.line([k, 0, k + im.height, im.height], fill=(30, 30, 30), width=3)
        bg.paste(im, (ax, ay))


def furnace(x, y):
    """Forno elétrico a arco (FEA) 4x4."""
    cx, cy, r = P(x + 2), P(y + 2), P(1.85)
    dbg.ellipse([cx - r - 4, cy - r + 6, cx + r + 4, cy + r + 10], fill=(30, 30, 34))       # sombra
    dbg.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 72, 80), outline=(30, 30, 34), width=3)
    dbg.ellipse([cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10], fill=(120, 50, 40))   # refratário
    glow(dbg, cx, cy, r - 18)
    for ang in (90, 210, 330):                                                              # eletrodos
        ex = cx + math.cos(math.radians(ang)) * 16
        ey = cy - math.sin(math.radians(ang)) * 16
        dbg.ellipse([ex - 9, ey - 9, ex + 9, ey + 9], fill=(60, 60, 64), outline=(20, 20, 20), width=2)
        dbg.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=(150, 150, 156))
        dbg.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=(255, 255, 220))
    rnd = frnd("arco")
    tips = [(cx + math.cos(math.radians(a)) * 16, cy - math.sin(math.radians(a)) * 16) for a in (90, 210, 330)]
    for i in range(3):
        if rnd.random() < 0.6:                                                              # arco elétrico
            (ax, ay), (bx, by) = tips[i], tips[(i + 1) % 3]
            pts = [(ax + (bx - ax) * t / 5 + rnd.randint(-4, 4), ay + (by - ay) * t / 5 + rnd.randint(-4, 4)) for t in range(6)]
            dbg.line(pts, fill=(200, 230, 255), width=2)
            dbg.line(pts, fill=(255, 255, 255), width=1)
    # braço dos eletrodos (fica acima do jogador)
    prect(dfg, cx - 6, P(y) - 10, cx + 6, cy - 4, (200, 160, 30), outline=(40, 30, 10))
    prect(dfg, cx - 14, P(y) - 14, cx + 14, P(y) - 4, (60, 60, 66), outline=(20, 20, 20))
    sparks(dbg, x - 0.3, y - 0.3, 4.6, 4.6, 40, 11)
    smoke(cx, P(y) - 14, 4)
    solid(x, y, 4, 4)


def ladle(x, y, solid_=True):
    """Panela de aço líquido 2x2 sobre trilhos."""
    cx, cy = P(x + 1), P(y + 1)
    dbg.ellipse([cx - 28, cy - 24, cx + 28, cy + 30], fill=(34, 34, 38))
    dbg.ellipse([cx - 28, cy - 28, cx + 28, cy + 26], fill=(92, 80, 74), outline=(30, 26, 24), width=3)
    glow(dbg, cx, cy - 1, 20)
    prect(dbg, cx - 31, cy - 4, cx - 26, cy + 4, (50, 50, 54))
    prect(dbg, cx + 26, cy - 4, cx + 31, cy + 4, (50, 50, 54))
    sparks(dbg, x, y - 0.2, 2, 1, 10, 5)
    if solid_:
        solid(x, y, 2, 2)


def rails(x, y, w):
    y0 = P(y)
    dbg.line([P(x), y0 + 10, P(x + w), y0 + 10], fill=(60, 60, 64), width=3)
    dbg.line([P(x), y0 + 22, P(x + w), y0 + 22], fill=(60, 60, 64), width=3)
    for k in range(P(x), P(x + w), 8):
        dbg.line([k, y0 + 7, k, y0 + 25], fill=(110, 84, 60), width=2)


def caster(x, y):
    """Lingotamento contínuo: distribuidor + 4 veios com tarugos incandescentes (7x3)."""
    rect(dbg, x, y, 1.6, 3, (80, 84, 92), outline=(30, 30, 34), width=2)          # distribuidor
    rect(dbg, x + 0.2, y + 0.3, 1.2, 2.4, (120, 50, 40))
    glow(dbg, P(x + 0.8), P(y + 1.5), 14)
    for i in range(4):
        sy = y + 0.25 + i * 0.68
        rect(dbg, x + 1.6, sy, 5.4, 0.42, (44, 44, 48))                                 # rolos
        for k in range(int(P(x + 1.6)), int(P(x + 7)), 6):
            dbg.line([k, P(sy), k, P(sy + 0.42)], fill=(90, 90, 96))
        # tarugo: do branco ao vermelho escuro
        n = 34
        for j in range(n):
            t = j / n
            c = (255, int(240 - 170 * t), int(170 - 160 * t)) if t < 0.6 else (int(255 - 90 * (t - .6) / .4), int(70 - 30 * (t - .6) / .4), 10)
            xa = P(x + 1.6) + int(j * P(5.4) / n)
            prect(dbg, xa, P(sy + 0.1), xa + P(5.4) // n + 1, P(sy + 0.32), c)
        span = P(5.4) - 4
        for m in range(4):                                     # carepa andando com o tarugo
            mx = P(x + 1.6) + 2 + ((F % 16) * (span // 4) // 16 + m * span // 4 + i * 9) % span
            prect(dbg, mx, P(sy + 0.13), mx + 2, P(sy + 0.29), (150, 40, 20))
    sparks(dbg, x + 1.4, y, 1.2, 3, 12, 7)
    solid(x, y, 7, 3)


def billets(x, y, w, h, hot=False):
    rect(dbg, x + 0.1, y + 0.15, w - 0.2, h - 0.2, (40, 40, 44))
    rows = int(h * 4)
    for r in range(rows):
        yy = P(y + 0.2) + r * 7
        for k in range(int(w)):
            c = shade((200, 70, 30), 1 + 0.1 * wave(r + k)) if hot and (r + k) % 3 else (112, 110, 112)
            prect(dbg, P(x + k) + 3, yy, P(x + k + 1) - 3, yy + 5, c, outline=shade(c, 0.7))
    solid(x, y, w, h)


def reheating_furnace(x, y):
    """Forno de reaquecimento (3x4) de tijolo refratário."""
    rect(dbg, x, y, 3, 4, (140, 64, 48), outline=(60, 26, 20), width=3)
    for r in range(8):
        yy = P(y) + 4 + r * 15
        dbg.line([P(x) + 3, yy, P(x + 3) - 3, yy], fill=(110, 48, 36))
        off = 0 if r % 2 else 12
        for k in range(P(x) + off, P(x + 3), 24):
            dbg.line([k, yy, k, yy + 15], fill=(110, 48, 36))
    rect(dbg, x + 2.4, y + 1.2, 0.6, 1.6, shade((255, 160, 40), 1 + 0.12 * wave()))
    rect(dbg, x + 2.6, y + 1.4 + 0.05 * wave(2), 0.4, 1.2, shade((255, 236, 150), 1 + 0.05 * wave(3)))
    # chaminé (acima) + fumaça subindo
    rect(dfg, x + 0.3, y - 0.6, 0.8, 1.1, (90, 90, 96), outline=(30, 30, 34), width=2)
    smoke(P(x + 0.7), P(y - 0.6))
    text(dbg, "FORNO", x + 1.2, y + 2, 13, (255, 230, 200), outline=(60, 20, 10), stroke=2)
    solid(x, y, 3, 4)


def smoke(cx, top, n=3):
    """Baforadas de fumaça que sobem e se desfazem (camada de cima)."""
    for k in range(n):
        ph = (((F % LOOP) + k * LOOP / n) % LOOP) / LOOP
        yy = top - 4 - ph * 44
        xx = cx + math.sin(ph * 5 + k) * 6
        r = 5 + ph * 9
        a = int(190 * (1 - ph))
        g = int(150 + 60 * ph)
        dfg.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(g, g, g + 4, a))


def roller_table(x, y, w, hot_from=0.0, hot_to=1.0):
    rect(dbg, x, y + 0.2, w, 0.6, (40, 40, 44))
    for k in range(P(x), P(x + w), 8):
        dbg.line([k + 2, P(y + 0.22), k + 2, P(y + 0.78)], fill=(110, 110, 118), width=3)
    a, b = P(x + w * hot_from), P(x + w * hot_to)
    prect(dbg, a, P(y + 0.4), b, P(y + 0.6), (255, 110, 30))
    prect(dbg, a, P(y + 0.45), b, P(y + 0.55), (255, 210, 110))
    for k in range(a + (F % 8) * 8, b - 10, 64):              # brilho correndo na barra
        prect(dbg, k, P(y + 0.42), k + 10, P(y + 0.58), (255, 250, 220))
    solid(x, y, w, 1)


def rolling_stand(x, y):
    """Cadeira de laminação 2x3 (atravessa a mesa de rolos)."""
    rect(dbg, x + 0.1, y, 1.8, 3, (46, 82, 128), outline=(20, 30, 46), width=3)
    rect(dbg, x + 0.35, y + 0.25, 1.3, 2.5, (70, 110, 160))
    for ry in (y + 1.2, y + 1.62):
        rect(dbg, x + 0.4, ry, 1.2, 0.22, (170, 170, 178), outline=(60, 60, 66))
        for m in range(3):                                     # cilindro girando
            mx = P(x + 0.4) + 2 + ((F % 8) * 2 + m * 12) % (P(1.2) - 5)
            prect(dbg, mx, P(ry) + 1, mx + 1, P(ry + 0.22) - 2, (110, 110, 118))
    rect(dbg, x + 0.4, y + 1.4, 1.2, 0.2, (255, 140, 40))
    rect(dbg, x + 0.7, y - 0.25, 0.6, 0.5, (240, 196, 30), outline=(60, 50, 10))       # motor
    solid(x, y, 2, 3)


def cooling_bed(x, y, w, h):
    rect(dbg, x, y, w, h, (60, 62, 68), outline=(30, 30, 34), width=2)
    for k in range(P(x) + 6, P(x + w) - 4, 10):
        dbg.line([k, P(y) + 4, k, P(y + h) - 4], fill=(40, 40, 44), width=3)
    top, bot = P(y) + 6, P(y + h) - 6
    step = (F % 16) * 9 / 16                                   # barras descendo (leito "walking beam")
    yy = top + step
    while yy < bot:
        t = (yy - top) / (bot - top)
        hot = (255, 120, 40)
        cold = (120, 118, 122)
        c = tuple(int(hot[i] + (cold[i] - hot[i]) * min(1, t * 1.4)) for i in range(3))
        dbg.line([P(x) + 4, yy, P(x + w) - 4, yy], fill=c, width=3)
        yy += 9
    solid(x, y, w, h)


def spool(x, y, hot=False):
    """Carretel de vergalhão (spooler) 2x2."""
    cx, cy = P(x + 1), P(y + 1)
    dbg.ellipse([cx - 29, cy - 27, cx + 29, cy + 31], fill=(34, 34, 38))
    dbg.ellipse([cx - 29, cy - 29, cx + 29, cy + 29], fill=(150, 60, 40) if hot else (96, 70, 58), outline=(30, 24, 20), width=2)
    for rr in range(26, 8, -4):
        c = (220, 110, 50) if hot else (124, 96, 82)
        dbg.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=c, width=2)
    if hot:                                                    # carretel girando
        for k in range(2):
            ang = math.radians((F % 8) * 22.5 + k * 180)
            dbg.line([cx + math.cos(ang) * 10, cy + math.sin(ang) * 10, cx + math.cos(ang) * 26, cy + math.sin(ang) * 26],
                     fill=(255, 200, 110), width=3)
    dbg.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(70, 74, 82), outline=(30, 30, 34), width=2)
    solid(x, y, 2, 2)


def wire_coil(x, y):
    cx, cy = P(x + 0.5), P(y + 0.5)
    dbg.ellipse([cx - 14, cy - 12, cx + 14, cy + 16], fill=(40, 40, 44))
    dbg.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(102, 92, 86), outline=(50, 44, 40), width=2)
    for rr in (11, 8):
        dbg.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(132, 120, 112), width=1)
    dbg.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(84, 86, 92))
    solid(x, y)


def rebar_bundle(x, y, w, tag=(240, 196, 30), label=None):
    """Feixe de vergalhões horizontal (w x 1) sobre calços de madeira."""
    for k in (0.4, w - 0.6):
        rect(dbg, x + k, y + 0.1, 0.25, 0.85, (140, 100, 60))
    for i in range(7):
        yy = P(y + 0.16) + i * 3 + (i % 2)
        c = (128, 76, 52) if i % 2 else (104, 62, 44)
        dbg.line([P(x) + 2, yy, P(x + w) - 3, yy], fill=c, width=3)
        for k in range(P(x) + 4, P(x + w) - 3, 4):          # nervuras
            dbg.point((k, yy - 1), fill=(150, 96, 66))
    for k in (1.2, w - 1.4):
        rect(dbg, x + k, y + 0.1, 0.12, 0.8, (50, 50, 54))  # amarração
    rect(dbg, x + w / 2 - 0.35, y + 0.25, 0.7, 0.45, tag, outline=(30, 30, 30))
    if label:
        text(dbg, label, x + w / 2, y + 0.48, 9, (20, 20, 20), outline=None, weight="Bold")
    solid(x, y, w, 1)


def mesh_stack(x, y, w, h):
    """Telas soldadas / treliças empilhadas."""
    rect(dbg, x + 0.1, y + 0.1, w - 0.2, h - 0.2, (96, 92, 90), outline=(50, 46, 44), width=2)
    for k in range(P(x) + 6, P(x + w) - 4, 6):
        dbg.line([k, P(y) + 6, k, P(y + h) - 6], fill=(140, 132, 126))
    for k in range(P(y) + 6, P(y + h) - 4, 6):
        dbg.line([P(x) + 6, k, P(x + w) - 6, k], fill=(140, 132, 126))
    solid(x, y, w, h)


def rack(x, y, h, kind):
    """Porta-palete vertical (2 x h) com produtos."""
    rect(dbg, x, y, 2, h, (40, 40, 44))
    for yy in range(y, y + h):
        rect(dbg, x + 0.08, yy + 0.08, 1.84, 0.84, (70, 70, 76))
        if kind == "telhas":
            for i in range(5):
                c = (176, 180, 188) if i % 2 else (150, 156, 166)
                rect(dbg, x + 0.15, yy + 0.15 + i * 0.13, 1.7, 0.12, c)
        elif kind == "tubos":
            for i in range(4):
                for j in range(3):
                    cx, cy = P(x + 0.35 + i * 0.43), P(yy + 0.25 + j * 0.25)
                    dbg.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(160, 164, 172), outline=(70, 72, 78))
                    dbg.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(60, 62, 68))
        elif kind == "perfis":
            for i in range(3):
                bx, by = x + 0.2 + i * 0.55, yy + 0.18
                rect(dbg, bx, by, 0.45, 0.1, (60, 100, 150))
                rect(dbg, bx + 0.17, by, 0.11, 0.62, (60, 100, 150))
                rect(dbg, bx, by + 0.55, 0.45, 0.1, (60, 100, 150))
        elif kind == "arames":
            for i in range(3):
                cx, cy = P(x + 0.38 + i * 0.62), P(yy + 0.5)
                dbg.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(170, 170, 176), outline=(90, 90, 96), width=2)
                dbg.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(70, 70, 76))
        elif kind == "vergalhao":
            for i in range(6):
                yy2 = P(yy + 0.2) + i * 4
                dbg.line([P(x) + 5, yy2, P(x + 2) - 5, yy2], fill=(128, 76, 52), width=2)
    # longarinas laranja
    for xx in (x, x + 1.86):
        rect(dbg, xx, y, 0.14, h, (232, 110, 30))
    solid(x, y, 2, h)


def forklift(x, y):
    rect(dbg, x + 0.15, y + 0.2, 0.7, 1.1, (240, 190, 20), outline=(60, 46, 6), width=2)
    rect(dbg, x + 0.25, y + 0.45, 0.5, 0.45, (40, 40, 44))
    beacon = (255, 140, 20) if F % 4 < 2 else (120, 60, 10)      # giroflex
    rect(dbg, x + 0.42, y + 0.6, 0.16, 0.16, beacon)
    rect(dbg, x + 0.25, y + 1.3, 0.12, 0.55, (70, 70, 76))
    rect(dbg, x + 0.63, y + 1.3, 0.12, 0.55, (70, 70, 76))
    for wy in (0.3, 1.0):
        rect(dbg, x + 0.05, y + wy, 0.12, 0.25, (20, 20, 20))
        rect(dbg, x + 0.83, y + wy, 0.12, 0.25, (20, 20, 20))
    solid(x, y, 1, 2)


def truck(x, y, load="vergalhao", color=(20, 70, 140), bundles=None, reverse=False, moving=False, solid_=True):
    """Carreta horizontal 5x2 com cabine à direita. bundles = nº de feixes (0..4) para carga animada."""
    rect(dbg, x + 0.05, y + 0.25, 3.9, 1.5, (60, 60, 66), outline=(20, 20, 24), width=2)
    if bundles is not None:
        for b in range(bundles):                               # feixes lado a lado na carroceria
            bx = x + 0.2 + b * 0.92
            for i in range(8):
                yy = P(y + 0.4) + i * 5
                dbg.line([P(bx), yy, P(bx + 0.82), yy], fill=(128, 76, 52) if i % 2 else (104, 62, 44), width=3)
            rect(dbg, bx + 0.36, y + 0.3, 0.1, 1.4, (240, 196, 30))
    elif load == "vergalhao":
        for i in range(8):
            yy = P(y + 0.4) + i * 5
            dbg.line([P(x) + 6, yy, P(x + 3.9) - 6, yy], fill=(128, 76, 52) if i % 2 else (104, 62, 44), width=3)
        for k in (0.8, 2.0, 3.2):
            rect(dbg, x + k, y + 0.3, 0.1, 1.4, (240, 196, 30))
    else:
        for i in range(3):
            rect(dbg, x + 0.2 + i * 1.25, y + 0.4, 1.1, 1.2, (150, 120, 80), outline=(90, 66, 40), width=2)
    rect(dbg, x + 4.0, y + 0.15, 0.95, 1.7, color, outline=(10, 20, 40), width=2)
    rect(dbg, x + 4.55, y + 0.35, 0.3, 1.3, (150, 200, 230))
    for wx in (0.4, 1.2, 3.1, 4.3):
        rect(dbg, x + wx, y + 0.08, 0.4, 0.16, (20, 20, 20))
        rect(dbg, x + wx, y + 1.76, 0.4, 0.16, (20, 20, 20))
    if reverse:                                                # luz de ré + alerta piscando
        on = F % 4 < 2
        for ly in (0.3, 1.5):
            rect(dbg, x + 0.02, y + ly, 0.12, 0.2, (255, 255, 230) if on else (120, 120, 110))
        rect(dbg, x + 4.7, y + 0.1, 0.2, 0.15, (255, 150, 20) if on else (110, 60, 10))
    if moving:                                                 # fumaça do escapamento
        for k in range(2):
            ph = ((F % 4) + k * 2) / 4
            sx, sy = P(x + 5.0) + ph * 10, P(y + 0.2) - ph * 6
            r = 2 + ph * 4
            dbg.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(150, 150, 154))
    if solid_:
        solid(x, y, 5, 2)


def forklift_h(x, y, face=1, carrying=False):
    """Empilhadeira de lado (1.2 x 0.8). face=1 garfo para a direita, -1 para a esquerda."""
    bx0 = x
    rect(dbg, bx0, y + 0.1, 1.2, 0.8, (240, 190, 20), outline=(60, 46, 6), width=2)
    rect(dbg, bx0 + (0.15 if face > 0 else 0.55), y + 0.25, 0.5, 0.5, (40, 40, 44))     # cabine
    rect(dbg, bx0 + 0.45, y + 0.42, 0.16, 0.16, (255, 140, 20) if F % 4 < 2 else (120, 60, 10))
    fx = bx0 + 1.2 if face > 0 else bx0 - 0.65
    rect(dbg, fx, y + 0.2, 0.65, 0.1, (70, 70, 76))
    rect(dbg, fx, y + 0.7, 0.65, 0.1, (70, 70, 76))
    rect(dbg, bx0 + (1.12 if face > 0 else -0.04), y + 0.08, 0.12, 0.84, (50, 50, 54))  # torre
    for wx in (0.15, 0.85):
        rect(dbg, bx0 + wx, y + 0.02, 0.22, 0.1, (20, 20, 20))
        rect(dbg, bx0 + wx, y + 0.88, 0.22, 0.1, (20, 20, 20))
    if carrying:
        for i in range(5):
            yy = P(y + 0.2) + i * 4
            dbg.line([P(fx) - 2, yy, P(fx + 0.7), yy], fill=(128, 76, 52) if i % 2 else (104, 62, 44), width=3)
        rect(dbg, fx + 0.28, y + 0.15, 0.08, 0.7, (240, 196, 30))


def car(x, y, color, down=False, solid_=True):
    """Carro vertical 1x2."""
    rect(dbg, x + 0.15, y + 0.15, 0.7, 1.7, color, outline=shade(color, 0.5), width=2)
    if down:
        rect(dbg, x + 0.25, y + 1.15, 0.5, 0.35, (150, 200, 230))
        rect(dbg, x + 0.25, y + 0.45, 0.5, 0.3, (120, 170, 200))
        rect(dbg, x + 0.25, y + 0.78, 0.5, 0.32, shade(color, 1.2))
        for lx in (0.22, 0.62):
            rect(dbg, x + lx, y + 1.78, 0.16, 0.08, (255, 250, 200))
    else:
        rect(dbg, x + 0.25, y + 0.5, 0.5, 0.35, (150, 200, 230))
        rect(dbg, x + 0.25, y + 1.25, 0.5, 0.3, (120, 170, 200))
        rect(dbg, x + 0.25, y + 0.9, 0.5, 0.32, shade(color, 1.2))
    if solid_:
        solid(x, y, 1, 2)


def tree(x, y, seed=0):
    """Tronco no chão (colide) e copa 2x2 por cima do jogador."""
    rnd = random.Random(seed)
    cx, cy = P(x + 0.5), P(y + 0.5)
    dbg.ellipse([cx - 14, cy + 4, cx + 14, cy + 14], fill=(50, 90, 40))
    prect(dbg, cx - 5, cy - 6, cx + 5, cy + 10, (110, 74, 44), outline=(70, 46, 26))
    base = rnd.choice([(46, 120, 70), (40, 110, 84), (58, 130, 60)])
    for (dx, dy, r, k) in ((0, -26, 26, 0.75), (-10, -30, 18, 1.0), (10, -28, 18, 0.95), (0, -38, 15, 1.12)):
        dfg.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r], fill=shade(base, k))
    for _ in range(10):
        px, py = cx + rnd.randrange(-20, 20), cy - 30 + rnd.randrange(-18, 14)
        dfg.rectangle([px, py, px + 2, py + 2], fill=shade(base, 1.3))
    solid(x, y)


def bush(x, y):
    cx, cy = P(x + 0.5), P(y + 0.5)
    dbg.ellipse([cx - 14, cy - 10, cx + 14, cy + 14], fill=(40, 100, 50))
    dbg.ellipse([cx - 12, cy - 12, cx + 10, cy + 8], fill=(60, 130, 64))
    dbg.point([(cx - 4, cy - 4), (cx + 4, cy - 2)], fill=(240, 220, 90))
    solid(x, y)


def plant(x, y):
    cx, cy = P(x + 0.5), P(y + 0.5)
    prect(dbg, cx - 8, cy + 2, cx + 8, cy + 13, (170, 100, 60), outline=(100, 56, 30))
    for (dx, dy) in ((-7, -4), (6, -5), (0, -10), (-3, 0), (4, 0)):
        dbg.ellipse([cx + dx - 7, cy + dy - 6, cx + dx + 7, cy + dy + 6], fill=(54, 140, 70), outline=(30, 90, 40))
    solid(x, y)


def chair(x, y, c=(40, 44, 52)):
    rect(dbg, x + 0.25, y + 0.25, 0.5, 0.5, c, outline=shade(c, 0.6))


def desk(x, y, monitor=True):
    """Mesa de trabalho 2x1 com computador e cadeira abaixo."""
    rect(dbg, x + 0.05, y + 0.1, 1.9, 0.8, (196, 160, 116), outline=(120, 90, 60), width=2)
    if monitor:
        rect(dbg, x + 0.6, y + 0.15, 0.8, 0.4, (30, 30, 36), outline=(10, 10, 10))
        rect(dbg, x + 0.66, y + 0.2, 0.68, 0.28, (60, 140, 200))
        rect(dbg, x + 0.6, y + 0.62, 0.8, 0.15, (220, 220, 224))
    rect(dbg, x + 0.15, y + 0.2, 0.3, 0.2, (250, 250, 250))
    solid(x, y, 2, 1)
    chair(x + 0.5, y + 1)


def table(x, y, w, h, c=(150, 100, 60), chairs=True, chair_c=(40, 44, 52)):
    if chairs:
        for k in range(w):
            chair(x + k, y - 0.55, chair_c)
            chair(x + k, y + h - 0.45, chair_c)
    rect(dbg, x + 0.05, y + 0.05, w - 0.1, h - 0.1, c, outline=shade(c, 0.6), width=3)
    rect(dbg, x + 0.2, y + 0.2, w - 0.4, h - 0.4, shade(c, 1.12))
    solid(x, y, w, h)


def screen(x, y, w, kind="chart"):
    """Tela/TV na face da parede (y = linha da parede)."""
    rect(dbg, x + 0.05, y + 0.2, w - 0.1, 0.75, (20, 20, 24), outline=(0, 0, 0), width=2)
    rect(dbg, x + 0.12, y + 0.27, w - 0.24, 0.6, (22, 40, 70))
    x0, y1 = P(x + 0.2), P(y + 0.82)
    if kind == "chart":
        hs = [8, 12, 10, 14, 16, 13, 17, 15]
        bw = (P(w - 0.4)) // len(hs)
        for i, hh in enumerate(hs):
            prect(dbg, x0 + i * bw + 1, y1 - hh, x0 + i * bw + bw - 2, y1, (80, 170, 240) if i % 2 else (240, 196, 30))
        pts = [(x0 + i * bw + bw // 2, y1 - hs[i] - 2) for i in range(len(hs))]
        dbg.line(pts, fill=(240, 80, 70), width=2)
        px_, py_ = pts[F % 8 % len(pts)]
        dbg.ellipse([px_ - 3, py_ - 3, px_ + 3, py_ + 3], fill=(255, 255, 255))
    else:
        text(dbg, kind, x + w / 2, y + 0.57, 11, (240, 240, 240), outline=None)


def sofa(x, y, w, c=(60, 64, 80)):
    rect(dbg, x + 0.05, y + 0.1, w - 0.1, 0.8, shade(c, 0.7), outline=shade(c, 0.4), width=2)
    for k in range(w):
        rect(dbg, x + k + 0.12, y + 0.35, 0.76, 0.5, c)
    solid(x, y, w, 1)


def bookshelf(x, y, w):
    rect(dbg, x, y + 0.05, w, 0.9, (110, 76, 46), outline=(60, 40, 20), width=2)
    rnd = random.Random(x * 31 + y)
    for row in (0.12, 0.5):
        k = P(x) + 4
        while k < P(x + w) - 6:
            bw = rnd.randrange(3, 6)
            c = rnd.choice([(180, 50, 50), (50, 90, 160), (230, 190, 60), (60, 140, 90), (220, 220, 210)])
            prect(dbg, k, P(y + row), k + bw, P(y + row + 0.33), c)
            k += bw + 1
    solid(x, y, w, 1)


def counter(x, y, w, kind="buffet"):
    rect(dbg, x, y + 0.05, w, 0.9, (120, 124, 132), outline=(60, 62, 68), width=2)
    rect(dbg, x + 0.08, y + 0.12, w - 0.16, 0.7, (200, 204, 210))
    if kind == "buffet":
        for k in range(w):
            for j, c in enumerate(((220, 170, 60), (110, 160, 70), (200, 80, 50))):
                rect(dbg, x + k + 0.1 + j * 0.28, y + 0.25, 0.24, 0.45, c, outline=(80, 80, 80))
    else:  # café
        for k in range(w):
            rect(dbg, x + k + 0.25, y + 0.15, 0.5, 0.6, (40, 40, 44), outline=(10, 10, 10))
            rect(dbg, x + k + 0.4, y + 0.55, 0.2, 0.15, (240, 240, 240))
            dbg.point((P(x + k + 0.5), P(y + 0.32)), fill=(255, 80, 60) if (F + k) % 4 < 2 else (90, 30, 20))
            for j in range(2):                                 # vapor
                ph = (((F % LOOP) + j * LOOP / 2 + k) % LOOP) / LOOP
                sx = P(x + k + 0.5) + math.sin(ph * 6 + k) * 3
                sy = P(y + 0.5) - ph * 16
                dbg.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(250, 250, 250))
    solid(x, y, w, 1)


def round_table(x, y):
    """Mesa redonda do refeitório (2x2 com 4 cadeiras)."""
    for (dx, dy) in ((0.5, -0.1), (0.5, 1.1), (-0.1, 0.5), (1.1, 0.5)):
        chair(x + dx, y + dy, (196, 74, 56))
    cx, cy = P(x + 1), P(y + 1)
    dbg.ellipse([cx - 22, cy - 20, cx + 22, cy + 24], fill=(60, 50, 40))
    dbg.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(236, 232, 224), outline=(140, 130, 120), width=2)
    dbg.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(240, 196, 30))
    solid(x, y, 2, 2)
    free(x, y)  # deixa um canto livre para não travar passagem


def bench(x, y, w):
    rect(dbg, x + 0.05, y + 0.3, w - 0.1, 0.45, (150, 100, 60), outline=(90, 60, 30), width=2)
    for k in range(w):
        dbg.line([P(x + k) + 4, P(y + 0.52), P(x + k + 1) - 4, P(y + 0.52)], fill=(120, 80, 46))
    solid(x, y, w, 1)


def helmet_rack(x, y, w):
    rect(dbg, x, y + 0.2, w, 0.6, (90, 90, 96), outline=(40, 40, 44), width=2)
    cs = [(250, 250, 250), (240, 196, 30), (40, 100, 200), (40, 160, 80), (220, 60, 50)]
    for i in range(w * 2):
        cx, cy = P(x + 0.25 + i * 0.5), P(y + 0.5)
        dbg.pieslice([cx - 7, cy - 7, cx + 7, cy + 7], 180, 360, fill=cs[i % len(cs)], outline=(30, 30, 30))
        prect(dbg, cx - 9, cy, cx + 9, cy + 2, shade(cs[i % len(cs)], 0.8))
    solid(x, y, w, 1)


def logo(d, cx, cy, s=1.0):
    """Marca estilizada: perfil de vergalhão + chapa (arte original)."""
    r = 20 * s
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(20, 54, 104), outline=(240, 196, 30), width=max(2, int(3 * s)))
    for i in (-1, 0, 1):
        x = cx + i * 9 * s
        d.line([x - 4 * s, cy + 12 * s, x + 4 * s, cy - 12 * s], fill=(255, 140, 40), width=max(2, int(4 * s)))
    d.line([cx - 14 * s, cy, cx + 14 * s, cy], fill=(230, 230, 236), width=max(1, int(2 * s)))


def monument(x, y, w):
    """Totem/letreiro de entrada com o nome da empresa."""
    rect(dbg, x - 0.1, y + 1.55, w + 0.2, 0.4, (60, 60, 64))
    rect(dbg, x, y, w, 1.7, (24, 30, 40), outline=(160, 166, 176), width=3)
    rect(dbg, x + 0.1, y + 0.1, w - 0.2, 1.5, (34, 42, 56))
    logo(dbg, P(x + 0.95), P(y + 0.85), 1.05)
    text(dbg, "AÇO CEARENSE", x + w / 2 + 0.8, y + 0.62, 26, (250, 250, 250), outline=(10, 10, 10), stroke=2)
    text(dbg, "USINA VIRTUAL  ·  GRUPO GAC", x + w / 2 + 0.8, y + 1.22, 13, (240, 196, 30), outline=None, weight="Bold")
    # holofotes
    for k in (0.3, w - 0.7):
        rect(dbg, x + k, y + 1.95, 0.4, 0.2, (240, 220, 140))
    solid(x, y, w, 2)


def safety_board(x, y):
    """Quadro 'dias sem acidentes' 2x1 (cavalete)."""
    rect(dbg, x + 0.05, y + 0.02, 1.9, 0.95, (30, 120, 60), outline=(10, 50, 20), width=2)
    text(dbg, "365", x + 1, y + 0.4, 17, (255, 255, 255), outline=(10, 40, 20), stroke=2)
    text(dbg, "DIAS SEM ACIDENTES", x + 1, y + 0.78, 7, (255, 255, 255), outline=None, weight="Bold")
    solid(x, y, 2, 1)


def crane(x, y0, y1, carry=False):
    """Ponte rolante amarela (camada de cima): viga vertical de y0 a y1 + talha."""
    for yy in range(y0, y1 + 1):
        x0, ya = P(x), P(yy)
        prect(dfg, x0 + 2, ya, x0 + T - 3, ya + T - 1, (238, 186, 24))
        prect(dfg, x0 + 2, ya, x0 + 5, ya + T - 1, (196, 150, 14))
        prect(dfg, x0 + T - 6, ya, x0 + T - 3, ya + T - 1, (196, 150, 14))
        dfg.line([x0 + 6, ya, x0 + T - 7, ya + T - 1], fill=(206, 160, 18), width=2)
        dfg.line([x0 + T - 7, ya, x0 + 6, ya + T - 1], fill=(206, 160, 18), width=2)
    # cabeceiras sobre os trilhos (listradas)
    for ye in (y0, y1):
        ya = P(ye)
        prect(dfg, P(x) - 10, ya + 4, P(x + 1) + 9, ya + 26, (30, 30, 30))
        for k in range(P(x) - 10, P(x + 1) + 9, 8):
            prect(dfg, k, ya + 6, k + 3, ya + 24, (240, 196, 30))
    # carro da talha + gancho
    ym = P((y0 + y1) / 2) + (ease(tri(32)) - 0.5) * P(7)      # talha indo e voltando
    if carry:                                                  # feixe pendurado no gancho
        for i in range(5):
            yy = ym + 16 + i * 3
            dfg.line([P(x) - 30, yy, P(x + 1) + 29, yy], fill=(128, 76, 52) if i % 2 else (104, 62, 44), width=3)
        dfg.line([P(x) + 15, ym + 6, P(x) - 18, ym + 15], fill=(30, 30, 30), width=1)
        dfg.line([P(x) + 16, ym + 6, P(x) + 49, ym + 15], fill=(30, 30, 30), width=1)
    prect(dfg, P(x) - 6, ym - 14, P(x + 1) + 5, ym + 14, (60, 60, 66), outline=(20, 20, 20))
    prect(dfg, P(x) + 10, ym - 6, P(x) + 21, ym + 6, (240, 196, 30), outline=(20, 20, 20))
    prect(dfg, P(x) + 13, ym - 12, P(x) + 18, ym - 8, (255, 60, 40) if F % 2 else (110, 20, 10))


def crane_rails(x0, x1, y):
    dfg.line([P(x0), P(y) + 2, P(x1), P(y) + 2], fill=(40, 40, 44, 255), width=4)


def dock_door(x, y, open_=False):
    """Porta de doca (na parede vertical leste)."""
    if open_:
        rect(dbg, x + 0.15, y, 0.7, 1, (34, 34, 38))
        rect(dbg, x + 0.15, y, 0.7, 0.18, (240, 196, 30))
        solid(x, y)
        return
    rect(dbg, x + 0.15, y, 0.7, 1, (240, 196, 30))
    for k in range(4):
        dbg.line([P(x + 0.15), P(y) + 4 + k * 7, P(x + 0.85), P(y) + 4 + k * 7], fill=(150, 120, 10), width=2)
    solid(x, y)


def scene():
    """Desenha o cenário inteiro no quadro F."""
    # =================================================================== CENÁRIO
    # --- base: grama
    fill(0, 0, W, H, "grass", 3)

    # --- ruas
    fill(0, 20, W, 2, "asphalt")
    fill(46, 20, 2, H - 20, "asphalt")
    for k in range(0, W * T, 48):
        if not (P(46) - 10 < k < P(48) + 10):
            prect(dbg, k, P(21) - 2, k + 24, P(21) + 1, (240, 196, 30))
    for k in range(P(22), H * T, 48):
        prect(dbg, P(47) - 2, k, P(47) + 1, k + 24, (240, 196, 30))

    # --- calçadas
    fill(2, 22, 44, 1, "paving")          # frente do escritório / refeitório
    fill(31, 22, 1, 23, "paving")         # entre escritório e refeitório
    fill(45, 22, 1, 23, "paving")         # ao lado da rua
    fill(2, 41, 29, 1, "paving")          # frente do escritório (sul)
    fill(47, 2, 1, 18, "paving")          # corredor entre galpão e CD
    fill(32, 37, 13, 8, "plaza")          # praça de entrada

    # --- pátio de carretas
    fill(60, 2, 6, 18, "asphalt")
    for yy in (3.9, 7.9, 11.9, 15.9):
        prect(dbg, P(60), P(yy), P(66) - 1, P(yy) + 2, (230, 230, 230))
    for k in range(P(2), P(20), 24):                           # zebrado do portão de cargas
        prect(dbg, P(65) + 22, k, P(66) - 1, k + 11, (240, 196, 30))

    # --- estacionamento
    fill(48, 22, 17, 24, "asphalt")
    fill(48, 22, 17, 1, "paving")
    for row_y in (24, 30):
        for k in range(49, 64):
            prect(dbg, P(k), P(row_y), P(k) + 2, P(row_y + 2), (230, 230, 230))
    rnd = random.Random(42)
    palette = [(200, 40, 40), (240, 240, 240), (40, 40, 44), (40, 90, 170), (150, 150, 156), (220, 180, 40), (60, 120, 70)]
    for row_y in (24, 30):
        for k in range(49, 63):
            if rnd.random() < 0.62:
                car(k, row_y, rnd.choice(palette))
    # portaria
    rect(dbg, 48, 39, 3, 3, (60, 60, 64))
    hwall(48, 39, 3, "office")
    rect(dbg, 48.15, 40, 2.7, 2, (226, 222, 214))
    rect(dbg, 48.3, 40.2, 1.4, 0.5, (196, 160, 116), outline=(120, 90, 60))
    rect(dbg, 48.4, 40.25, 0.5, 0.3, (60, 140, 200))
    plaque(48, 39, 3, "PORTARIA", size=12)
    solid(48, 39, 3, 3)
    # carro saindo pela portaria (desce pela rua) e cancela abrindo
    cy_ = 21.6 + 25 * seg(F, 0, 64)
    if F < 64:
        car(46.05, cy_, (40, 90, 170), down=True, solid_=False)
    lift = ease(seg(F, 24, 32)) * (1 - ease(seg(F, 46, 54)))  # 0 = abaixada, 1 = levantada
    rect(dbg, 45.6, 40.3, 0.4, 0.4, (200, 40, 40))
    ang = math.radians(90 * lift)
    bx, by = P(45.8), P(40.5)
    L = P(2.1)
    ex, ey = bx + math.cos(ang) * L, by - math.sin(ang) * L
    n = 7
    for k in range(n):
        c = (240, 240, 240) if k % 2 else (220, 40, 40)
        a0, a1 = k / n, (k + 1) / n
        dfg.line([bx + (ex - bx) * a0, by + (ey - by) * a0, bx + (ex - bx) * a1, by + (ey - by) * a1], fill=c, width=4)
    solid(45, 40)
    # caminhão de vergalhão passando na rua principal
    rx = -6 + 73 * F / NF
    truck(rx, 20, "vergalhao", (20, 54, 104), moving=True, solid_=False)

    # =================================================================== GALPÃO
    GX0, GY0, GX1, GY1 = 2, 2, 46, 19
    fill(GX0 + 1, GY0 + 1, GX1 - GX0 - 1, GY1 - GY0 - 1, "concrete")
    fill(3, 3, 14, 13, "grate")                               # aciaria
    fill(3, 16, 43, 2, "walkway")                             # passarela de pedestres
    for yy in (16, 18):
        prect(dbg, P(3), P(yy) - 2, P(46) - 1, P(yy) + 1, (240, 240, 240))
    for k in range(P(3) + 8 + (F % 8) * 8, P(46) - 12, 64):          # setas da passarela (andando)
        dbg.polygon([(k, P(17) - 6), (k + 12, P(17)), (k, P(17) + 6)], fill=(230, 240, 230))
    # divisórias de área pintadas no chão
    for xx in (17, 34):
        prect(dbg, P(xx) - 2, P(3), P(xx) + 1, P(16) - 3, (240, 196, 30))
    building(GX0, GY0, GX1, GY1, "galpao",
             bottom_doors=(8, 9, 24, 25, 40, 41), right_doors=(16, 17))
    plaque(4, 2, 8, "ACIARIA", size=15)
    plaque(20, 2, 10, "LAMINAÇÃO", size=15)
    plaque(35, 2, 10, "PÁTIO DE PRODUTOS", size=15)
    plaque(13, 19, 8, "USINA AÇO CEARENSE", size=13)
    plaque(29, 19, 8, "USE EPI · CAPACETE", size=12, bgc=(30, 110, 60))

    # --- ACIARIA
    hazard_border(3, 3, 6, 6)
    furnace(4, 4)
    rails(9, 5, 7)
    rails(9, 6, 7)
    # panela: vazamento no forno -> vai até a ponte rolante -> volta
    if F < 32 or F >= 112:
        lx = 9
    elif F < 56:
        lx = 9 + 4 * ease(seg(F, 32, 56))
    elif F < 88:
        lx = 13
    else:
        lx = 13 - 4 * ease(seg(F, 88, 112))
    if lx == 9:                                                # jato de aço do forno para a panela
        rnd_ = frnd("jato")
        pts = [(P(7.75) + k * 6, P(6) - 4 + int(4 * math.sin(k + F)) + rnd_.randint(-1, 1)) for k in range(9)]
        dbg.line(pts, fill=(255, 140, 30), width=7)
        dbg.line(pts, fill=(255, 230, 140), width=3)
        sparks(dbg, 8.6, 5.3, 1.4, 1.4, 14, 23)
    ladle(lx, 5, solid_=False)
    solid(9, 5, 5, 2)
    rect(dbg, 14.2, 4.0, 1.6, 1.1, (90, 94, 100), outline=(30, 30, 34), width=2)   # cesta de sucata
    for i in range(10):
        rr = random.Random(i)
        sx, sy = P(14.3) + rr.randrange(40), P(4.1) + rr.randrange(26)
        prect(dbg, sx, sy, sx + 6, sy + 4, rr.choice([(120, 100, 90), (90, 80, 76), (140, 120, 100)]))
    solid(14, 4, 2, 1)
    caster(4, 10)
    billets(12, 10, 4, 1, hot=True)
    billets(12, 12, 4, 1, hot=False)
    floor_label(10, 14.3, "ACIARIA · FEA", 20)

    # --- LAMINAÇÃO
    reheating_furnace(18, 4)
    roller_table(21, 6, 13, 0.0, 0.75)
    for sx in (22, 25, 28):
        rolling_stand(sx, 5)
    cooling_bed(21, 9, 9, 3)
    spool(31, 9, hot=True)
    spool(31, 12, hot=False)
    # cabine de controle (púlpito)
    rect(dbg, 18, 10, 2.6, 3, (40, 44, 52), outline=(20, 20, 24), width=3)
    rect(dbg, 18.15, 10.15, 2.3, 2.7, (130, 180, 210))
    for i in range(3):
        rect(dbg, 18.3, 10.35 + i * 0.85, 0.7, 0.45, (20, 20, 24))
        rect(dbg, 18.35, 10.4 + i * 0.85, 0.6, 0.32, (80, 220, 140) if i != 1 else (240, 120, 60))
    solid(18, 10, 3, 3)
    floor_label(25.5, 14.3, "LAMINAÇÃO · VERGALHÃO SI-50 / CARRETEL", 17)

    # --- PÁTIO DE PRODUTOS
    tags = [((240, 196, 30), "8mm"), ((40, 110, 200), "10mm"), ((220, 60, 50), "12.5"), ((40, 160, 80), "16mm")]
    for i, (yy) in enumerate((4, 5, 7, 8)):
        rebar_bundle(35, yy, 4, *tags[i % 4])
        rebar_bundle(40, yy, 5, *tags[(i + 1) % 4])
    for yy in (11, 12):
        for xx in range(35, 40):
            wire_coil(xx, yy)
    spool(40, 11)
    mesh_stack(42, 11, 3, 2)
    forklift(44, 13)
    floor_label(39.5, 14.3, "VERGALHÃO · FIO-MÁQUINA · TELAS", 16)

    # --- pontes rolantes (por cima)
    crane_rails(3, 46, 3)
    crane_rails(3, 46, 15)
    crane(13, 3, 15)
    crane(34, 3, 15, carry=True)

    # ======================================================= CENTRO DE DISTRIBUIÇÃO
    CX0, CY0, CX1, CY1 = 48, 2, 59, 19
    fill(CX0 + 1, CY0 + 1, CX1 - CX0 - 1, CY1 - CY0 - 1, "concrete")
    building(CX0, CY0, CX1, CY1, "galpao", bottom_doors=(53, 54), left_doors=(16, 17))
    plaque(49, 2, 10, "CENTRO DE DISTRIBUIÇÃO", size=12)
    for (rx, kind) in ((49, "telhas"), (52, "tubos"), (55, "perfis")):
        rack(rx, 4, 8, kind)
    rack(57, 4, 4, "arames")
    rack(57, 9, 3, "vergalhao")
    text(dbg, "TELHAS", 50, 3.55, 10, (255, 255, 255), outline=(0, 0, 0), stroke=2)
    text(dbg, "TUBOS", 53, 3.55, 10, (255, 255, 255), outline=(0, 0, 0), stroke=2)
    text(dbg, "PERFIS", 56, 3.55, 10, (255, 255, 255), outline=(0, 0, 0), stroke=2)
    # doca 1: carreta parada carregada
    dock_door(59, 5, open_=True)
    truck(60, 4, "vergalhao", (20, 70, 140))

    def truck_cycle(f):
        """Posição x da carreta no ciclo: chega de ré (0-23), doca (24-103), sai (104-127)."""
        if f < 24:
            return 66.2 - 6.2 * ease(seg(f, 0, 24)), "re"
        if f < 104:
            return 60, "doca"
        return 60 + 7 * seg(f, 104, 128) ** 2, "sai"

    # doca 2: EXPEDIÇÃO -> carreta chega vazia, é carregada e sai (defasada meio ciclo)
    g = (F + 64) % NF
    tx, st_ = truck_cycle(g)
    load = 0 if g < 34 else min(4, 1 + int((g - 34) / 16))
    dock_door(59, 9, open_=(st_ == "doca"))
    truck(tx, 8, color=(200, 40, 40), bundles=load if st_ != "re" else 0,
          reverse=(st_ == "re"), moving=(st_ != "doca"), solid_=False)

    # doca 3: RECEBIMENTO -> carreta chega cheia, empilhadeira descarrega, carreta sai
    tx, st_ = truck_cycle(F)
    trips = [28, 52, 76]                                       # início de cada viagem da empilhadeira
    taken = sum(1 for t0 in trips if F >= t0 + 10)
    dropped = sum(1 for t0 in trips if F >= t0 + 22)
    dock_door(59, 13, open_=(st_ == "doca"))
    truck(tx, 12, color=(240, 240, 240), bundles=3 - taken if F < 104 else 0,
          reverse=(st_ == "re"), moving=(st_ != "doca"), solid_=False)
    # pilha de recebimento
    rect(dbg, 50, 12.9, 1.6, 0.2, (140, 100, 60))
    for b in range(dropped):
        for i in range(4):
            yy = P(13.05) + b * 6 + i * 1.5
            dbg.line([P(50.05), yy, P(51.55), yy], fill=(128, 76, 52) if i % 2 else (104, 62, 44), width=2)
    text(dbg, "RECEBIMENTO", 50.8, 12.7, 8, (255, 255, 255), outline=(0, 0, 0), stroke=2)
    # empilhadeira: vai até a doca, pega o feixe, volta e deixa na pilha
    fx, face, carrying = 52.2, 1, False
    for t0 in trips:
        k = F - t0
        if 0 <= k < 24:
            if k < 9:
                fx, face = 52.2 + 5.6 * ease(k / 9), 1
            elif k < 12:
                fx, face, carrying = 57.8, 1, k >= 10
            elif k < 21:
                fx, face, carrying = 57.8 - 5.6 * ease((k - 12) / 9) + 0.0, -1, True
                fx += 0.65                                     # compensa o garfo ao virar
            else:
                fx, face, carrying = 52.85, -1, k < 22
    forklift_h(fx, 13.1, face, carrying)
    mesh_stack(50, 14, 2, 1)
    mesh_stack(50, 15, 2, 1)
    floor_label(54, 17.2, "EXPEDIÇÃO", 18)

    # ========================================================= ESCRITÓRIO
    OX0, OY0, OX1, OY1 = 2, 23, 30, 40
    fill(3, 24, 8, 7, "carpet_blue")       # sala de reunião
    fill(12, 24, 10, 7, "carpet_blue")     # sala S&OP
    fill(23, 24, 7, 7, "wood", 3)          # diretoria
    fill(3, 32, 17, 8, "carpet_gray")      # escritório aberto
    fill(3, 35, 5, 5, "carpet_green")      # área de foco
    fill(21, 32, 9, 8, "lobby")            # recepção
    building(OX0, OY0, OX1, OY1, "office", bottom_doors=(24, 25, 26))
    hwall(3, 31, 27, "office", doors=(6, 7, 16, 17, 26))
    vwall(11, 24, 7, "office")
    vwall(22, 24, 7, "office")
    vwall(20, 32, 8, "office", doors=(35, 36))
    hwall(3, 34, 5, "office", doors=(5, 6))           # divisória da área de foco
    plaque(4, 31, 2, "REUNIÃO", size=8)
    plaque(13, 31, 3, "SALA S&OP", size=11)
    plaque(27, 31, 3, "DIRETORIA", size=10)
    plaque(21, 40, 3, "RECEPÇÃO", size=11)
    plaque(27, 40, 3, "ESCRITÓRIO", size=10)
    plaque(3, 34, 2, "FOCO", size=10, bgc=(30, 110, 60))

    # sala de reunião
    screen(5, 23, 3, "chart")
    table(5, 26, 3, 2)
    plant(3, 24)
    plant(10, 24)
    # sala S&OP
    screen(13, 23, 4, "chart")
    screen(18, 23, 3, "S&OP")
    table(14, 26, 5, 2, c=(60, 64, 76), chair_c=(196, 74, 56))
    text(dbg, "S&OP", 16.5, 27, 18, (240, 196, 30), outline=(20, 20, 20), stroke=2)
    plant(12, 30)
    plant(21, 24)
    # diretoria
    bookshelf(23, 24, 3)
    desk(25, 26)
    sofa(23, 29, 3, (120, 40, 40))
    plant(29, 24)
    # escritório aberto
    for (dx, dy) in ((9, 32), (11, 32), (14, 32), (16, 32), (9, 35), (11, 35), (14, 35), (16, 35), (9, 38), (11, 38), (14, 38), (16, 38)):
        if dy == 38:
            rect(dbg, dx + 0.05, dy + 0.1, 1.9, 0.8, (196, 160, 116), outline=(120, 90, 60), width=2)
            rect(dbg, dx + 0.6, dy + 0.15, 0.8, 0.4, (30, 30, 36))
            rect(dbg, dx + 0.66, dy + 0.2, 0.68, 0.28, (60, 140, 200))
            solid(dx, dy, 2, 1)
        else:
            desk(dx, dy)
    plant(19, 32)
    plant(3, 32)
    text(dbg, "PCP · LOGÍSTICA · COMERCIAL", 13.5, 34.5, 10, (230, 230, 236), outline=(40, 40, 44), stroke=2)
    # área de foco
    bookshelf(3, 39, 3)
    sofa(3, 36, 2, (50, 90, 70))
    plant(7, 39)
    # recepção
    rect(dbg, 23, 33, 5, 1, (40, 54, 80), outline=(20, 26, 40), width=3)
    rect(dbg, 23.1, 33.1, 4.8, 0.4, (210, 212, 216))
    logo(dbg, P(25.5), P(33.6), 0.5)
    solid(23, 33, 5, 1)
    chair(25, 32.2, (40, 44, 52))
    logo(dbg, P(25.5), P(36.5), 1.5)                    # logo no piso
    sofa(21, 38, 2, (40, 60, 110))
    safety_board(28, 38)
    plant(21, 32)
    plant(29, 32)
    helmet_rack(21, 35, 1)

    # ========================================================= REFEITÓRIO
    RX0, RY0, RX1, RY1 = 32, 23, 44, 36
    fill(33, 24, 11, 12, "checker")
    building(RX0, RY0, RX1, RY1, "refeit", bottom_doors=(37, 38, 39))
    plaque(34, 23, 6, "REFEITÓRIO", size=13, bgc=(160, 50, 40))
    plaque(40, 36, 4, "CAFÉ COM AÇO", size=11, bgc=(160, 50, 40))
    counter(33, 24, 6, "buffet")
    counter(40, 24, 3, "cafe")
    plant(43, 24)
    for (tx, ty) in ((34, 27), (38, 27), (42, 27), (34, 31), (38, 31), (42, 31)):
        if tx + 1 < RX1:
            round_table(tx, ty)
    plant(33, 35)
    plant(43, 35)

    # ========================================================= PRAÇA / ENTRADA
    monument(34, 38, 9)
    for (bx, by) in ((32, 41), (44, 41)):
        bush(bx, by)
    bench(33, 44, 3)
    bench(41, 44, 3)
    for xx in (32, 44):
        bush(xx, 38)
    # flores ao lado do letreiro
    for xx in (33, 43):
        rect(dbg, xx + 0.1, 38.2, 0.8, 1.6, (120, 80, 50))
        for k in range(5):
            dbg.ellipse([P(xx) + 6, P(38.3) + k * 9, P(xx) + 14, P(38.3) + k * 9 + 8],
                        fill=[(230, 60, 80), (240, 220, 60), (240, 240, 240)][k % 3])
        solid(xx, 38, 1, 2)
    text(dbg, "BEM-VINDO(A)!", 38.5, 43.5, 18, (255, 255, 255), outline=(20, 54, 104), stroke=3)

    # ========================================================= ÁRVORES
    trees = [(0, 1), (0, 6), (1, 11), (0, 16), (0, 25), (1, 30), (0, 35), (1, 40), (0, 44),
             (5, 0), (11, 1), (18, 0), (24, 1), (31, 0), (39, 1), (44, 0), (52, 1), (58, 0), (64, 1),
             (4, 43), (10, 44), (16, 43), (22, 44), (28, 43)]
    for i, (tx, ty) in enumerate(trees):
        tree(tx, ty, i)
    for (bx, by) in ((3, 42), (13, 42), (19, 42), (25, 42), (8, 43), (30, 44)):
        bush(bx, by)

    # bordas do mapa: impede andar para fora pela grama do topo
    # (o próprio mapa já limita, nada a fazer)


# ===================================================================== ÁREAS
areas = []


def area(name, x, y, w, h, **props):
    areas.append((name, x, y, w, h, props))


area("Sala de Reunião", 3, 24, 8, 7, jitsiRoomName="aco-cearense-reuniao", jitsiTrigger="onaction",
     jitsiTriggerMessage="Pressione ESPAÇO para entrar na Sala de Reunião")
area("Sala S&OP", 12, 24, 10, 7, jitsiRoomName="aco-cearense-sop", jitsiTrigger="onaction",
     jitsiTriggerMessage="Pressione ESPAÇO para entrar na reunião de S&OP")
area("Diretoria", 23, 24, 7, 7, jitsiRoomName="aco-cearense-diretoria", jitsiTrigger="onaction",
     jitsiTriggerMessage="Pressione ESPAÇO para entrar na Diretoria")
area("Área de Foco", 3, 35, 5, 5, silent=True)
area("Cabine de Controle", 16, 9, 2, 5, focusable=True, zoom_margin=0.3)
area("Letreiro", 33, 40, 11, 2, focusable=True, zoom_margin=0.5)

# ====================================================== SPAWN (layer 'start')
START = [(x, y) for x in range(36, 41) for y in (41, 42)]
for (x, y) in START:
    free(x, y)

# ============================================================ MONTAGEM TILED
import numpy as np

uniq = {}                                    # hash -> imagem do tile
seqs = [[[None] * NF for _ in range(W * H)] for _ in range(2)]   # [camada][posição][quadro] = hash
gif = []
first = None


def slice_tiles(img):
    a = np.asarray(img).reshape(H, T, W, T, 4).transpose(0, 2, 1, 3, 4)
    return a


for F in range(NF):
    bg = Image.new("RGBA", (W * T, H * T), (0, 0, 0, 255))
    fg = Image.new("RGBA", (W * T, H * T), (0, 0, 0, 0))
    dbg, dfg = ImageDraw.Draw(bg), ImageDraw.Draw(fg)
    col = [[False] * W for _ in range(H)]
    scene()
    for (x, y) in START:
        free(x, y)
    if F == 0:
        first = (bg, fg, col)
    for li, img in enumerate((bg, fg)):
        arr = slice_tiles(img)
        for y in range(H):
            for x in range(W):
                t = arr[y, x]
                bts = t.tobytes()
                h = hashlib.md5(bts).hexdigest()
                if h not in uniq:
                    uniq[h] = (Image.fromarray(np.ascontiguousarray(t), "RGBA"), li == 1 and not t[:, :, 3].any())
                seqs[li][y * W + x][F] = h
    if F % 2 == 0:
        gif.append(Image.alpha_composite(bg, fg).crop((0, 0, W * T, 24 * T)).resize((W * T * 2 // 5, 24 * T * 2 // 5), Image.LANCZOS).convert("P", palette=Image.ADAPTIVE))
    print(f"quadro {F + 1}/{NF}", end="\r", flush=True)
print()
bg, fg, col = first

tiles = []          # lista de imagens 32x32
index = {}          # hash -> id local
anims = {}          # sequência de quadros -> id do tile animado
animations = {}     # id do tile animado -> [(id do quadro, duração ms), ...]


def tile_id(h):
    if h not in index:
        index[h] = len(tiles)
        tiles.append(uniq[h][0])
    return index[h]


def period(hs):
    p = 1
    while p < NF:
        if NF % p == 0 and all(hs[i] == hs[i % p] for i in range(NF)):
            return p
        p *= 2
    return NF


def place(li, pos):
    hs = seqs[li][pos]
    if len(set(hs)) == 1:
        if li == 1 and uniq[hs[0]][1]:
            return 0
        return tile_id(hs[0]) + 1
    key = tuple(hs)
    if key not in anims:
        p = period(hs)
        runs = []
        for h in hs[:p]:                       # junta quadros iguais seguidos (menos dados)
            fid = tile_id(h)
            if runs and runs[-1][0] == fid:
                runs[-1][1] += FRAME_MS
            else:
                runs.append([fid, FRAME_MS])
        anims[key] = len(tiles)
        tiles.append(uniq[hs[0]][0])           # tile base exclusivo (é ele que anima)
        animations[anims[key]] = runs
    return anims[key] + 1


floor_data = [place(0, i) for i in range(W * H)]
above_data = [place(1, i) for i in range(W * H)]

# tiles especiais (transparentes) no final
COLLIDE = len(tiles)
tiles.append(Image.new("RGBA", (T, T), (0, 0, 0, 0)))
START_T = len(tiles)
st = Image.new("RGBA", (T, T), (0, 0, 0, 0))
ImageDraw.Draw(st).point((0, 0), fill=(0, 0, 0, 1))   # quase invisível, só para diferenciar
tiles.append(st)

collide_data = [COLLIDE + 1 if col[y][x] else 0 for y in range(H) for x in range(W)]
start_data = [0] * (W * H)
for (x, y) in START:
    start_data[y * W + x] = START_T + 1

COLS = 64
rows = math.ceil(len(tiles) / COLS)
sheet = Image.new("RGBA", (COLS * T, rows * T), (0, 0, 0, 0))
for i, im in enumerate(tiles):
    sheet.paste(im, ((i % COLS) * T, (i // COLS) * T))
sheet.save(os.path.join(ROOT, "tileset.png"), optimize=True)


def tile_layer(lid, name, data, **extra):
    d = {"id": lid, "name": name, "type": "tilelayer", "x": 0, "y": 0, "width": W, "height": H,
         "opacity": 1, "visible": True, "data": data}
    d.update(extra)
    return d


objects = []
for i, (name, x, y, w, h, props) in enumerate(areas, start=1):
    objects.append({
        "id": i, "name": name, "type": "area", "class": "area", "rotation": 0, "visible": True,
        "x": x * T, "y": y * T, "width": w * T, "height": h * T,
        "properties": [{"name": k, "type": "bool" if isinstance(v, bool) else ("float" if isinstance(v, float) else "string"), "value": v}
                       for k, v in props.items()],
    })

tmap = {
    "compressionlevel": -1,
    "type": "map", "version": "1.10", "tiledversion": "1.10.2",
    "orientation": "orthogonal", "renderorder": "right-down",
    "width": W, "height": H, "tilewidth": T, "tileheight": T, "infinite": False,
    "nextlayerid": 8, "nextobjectid": len(objects) + 1,
    "properties": [
        {"name": "mapName", "type": "string", "value": "Usina Aço Cearense"},
        {"name": "mapDescription", "type": "string",
         "value": "Usina virtual: aciaria, laminação, pátio de vergalhões, centro de distribuição, escritório, sala S&OP e refeitório."},
        {"name": "mapCopyright", "type": "string", "value": "Arte original gerada por tools/gerar_mapa.py - CC BY-SA 4.0"},
    ],
    "layers": [
        tile_layer(1, "chao", floor_data),
        tile_layer(2, "colisoes", collide_data),
        tile_layer(3, "start", start_data),
        {"id": 4, "name": "areas", "type": "objectgroup", "draworder": "topdown", "x": 0, "y": 0,
         "opacity": 1, "visible": True, "objects": objects},
        {"id": 5, "name": "floorLayer", "type": "objectgroup", "draworder": "topdown", "x": 0, "y": 0,
         "opacity": 1, "visible": True, "objects": []},
        tile_layer(6, "acima", above_data),
    ],
    "tilesets": [{
        "firstgid": 1, "name": "aco_cearense", "image": "tileset.png",
        "imagewidth": COLS * T, "imageheight": rows * T,
        "tilewidth": T, "tileheight": T, "tilecount": len(tiles), "columns": COLS,
        "margin": 0, "spacing": 0,
        "properties": [{"name": "tilesetCopyright", "type": "string", "value": "Arte original - CC BY-SA 4.0"}],
        "tiles": [{"id": COLLIDE, "properties": [{"name": "collides", "type": "bool", "value": True}]}] +
                 [{"id": tid, "animation": [{"tileid": f, "duration": d} for f, d in runs]}
                  for tid, runs in sorted(animations.items())],
    }],
}
with open(os.path.join(ROOT, "map.json"), "w", encoding="utf-8") as fh:
    json.dump(tmap, fh, ensure_ascii=False, separators=(",", ":"))

# preview: chão + camada de cima (+ áreas desenhadas)
prev = Image.alpha_composite(bg, fg)
prev.convert("RGB").save(os.path.join(ROOT, "preview.png"), optimize=True)
dbgprev = Image.alpha_composite(prev, Image.new("RGBA", prev.size, (0, 0, 0, 0)))
ov = ImageDraw.Draw(dbgprev)
for y in range(H):
    for x in range(W):
        if col[y][x]:
            ov.rectangle([x * T, y * T, x * T + T - 1, y * T + T - 1], outline=(255, 0, 0, 255))
for (x, y) in START:
    ov.rectangle([x * T + 4, y * T + 4, x * T + T - 5, y * T + T - 5], outline=(0, 255, 0, 255), width=3)
if os.environ.get("PREVIEW_DEBUG_DIR"):
    dbgprev.convert("RGB").save(os.path.join(os.environ["PREVIEW_DEBUG_DIR"], "preview_colisoes.png"))
# GIF animado da prévia (mapa inteiro, reduzido, metade dos quadros)
gif[0].save(os.path.join(ROOT, "preview_animado.gif"), save_all=True, append_images=gif[1:],
            duration=FRAME_MS * 2, loop=0, optimize=True)
print(f"tiles: {len(tiles)}  animados: {len(animations)}  tileset: {COLS * T}x{rows * T}")
