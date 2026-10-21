#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Radar de Excecoes de Vendas — motor de deteccao estatistica.

Varre a base de vendas em varios niveis (linha, grupo, SKU, empresa, estado,
gerencia, segmento, cliente), constroi um baseline historico ROBUSTO por serie
(mediana + MAD) e devolve as excecoes priorizadas por severidade estatistica
X materialidade, com drill-down de causa e a pergunta a fazer ao comercial.

Uso:
    python radar_excecoes.py \
        --vendas tabela_vendas.xlsx \
        --previsao tabela_previsao.xlsx \
        --output radar_resultado.json \
        [--mes 202605] [--janela 12] [--csv excecoes.csv]

Saida: JSON estruturado. NUNCA escreva insight sem ler o JSON inteiro.
"""

import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ─── Colunas ─────────────────────────────────────────────────────────────────

COL_MES      = "numero_ano_mes"
COL_VENDA    = "Venda Vol"
COL_PREV     = "Previsao Vol"
COL_EMPRESA  = "descricao_empresa_3"
COL_LINHA    = "descricao_linha"
COL_GRUPO    = "descricao_grupo"
COL_ESPESS   = "descricao_espessura"
COL_ESTADO   = "descricao_estado"
COL_GERENCIA = "descricao_gerencia_2"
COL_CLIENTE  = "descricao_parceiro_master"
COL_SEGMENTO = "descricao_segmento_mercado"
COL_FORNEC   = "descricao_fornecedor"

# Dimensoes que existem SO na base de vendas (nunca cruzar com previsao)
DIMS_SO_VENDAS = {COL_CLIENTE, COL_SEGMENTO, COL_FORNEC}

# ─── Niveis de varredura ─────────────────────────────────────────────────────
# 'pai' aponta para o nivel imediatamente superior, usado para deduplicar
# excecoes redundantes (SKU que sozinho explica o desvio da linha inteira).

NIVEIS = [
    {"id": "empresa",        "rotulo": "Empresa",              "dims": [COL_EMPRESA],                        "pai": None},
    {"id": "linha",          "rotulo": "Linha",                "dims": [COL_LINHA],                          "pai": None},
    {"id": "grupo",          "rotulo": "Grupo",                "dims": [COL_LINHA, COL_GRUPO],               "pai": "linha"},
    {"id": "sku",            "rotulo": "SKU (Grupo x Espessura)", "dims": [COL_LINHA, COL_GRUPO, COL_ESPESS], "pai": "grupo"},
    {"id": "estado",         "rotulo": "Estado",               "dims": [COL_ESTADO],                         "pai": None},
    {"id": "gerencia",       "rotulo": "Gerencia",             "dims": [COL_GERENCIA],                       "pai": None},
    {"id": "empresa_linha",  "rotulo": "Empresa x Linha",      "dims": [COL_EMPRESA, COL_LINHA],             "pai": "empresa"},
    {"id": "estado_linha",   "rotulo": "Estado x Linha",       "dims": [COL_ESTADO, COL_LINHA],              "pai": "estado"},
    {"id": "gerencia_linha", "rotulo": "Gerencia x Linha",     "dims": [COL_GERENCIA, COL_LINHA],            "pai": "gerencia"},
    {"id": "segmento",       "rotulo": "Segmento de mercado",  "dims": [COL_SEGMENTO],                       "pai": None},
    {"id": "cliente",        "rotulo": "Cliente",              "dims": [COL_CLIENTE],                        "pai": None},
    {"id": "cliente_linha",  "rotulo": "Cliente x Linha",      "dims": [COL_CLIENTE, COL_LINHA],             "pai": "cliente"},
]

# Camada narrativa — organiza o deck: primeiro o macro, depois produto, depois cliente.
CAMADA = {
    "empresa": "macro", "linha": "macro", "estado": "macro", "gerencia": "macro",
    "segmento": "macro", "empresa_linha": "macro", "estado_linha": "macro",
    "gerencia_linha": "macro",
    "grupo": "produto", "sku": "produto",
    "cliente": "cliente", "cliente_linha": "cliente",
}

# Nivel filho usado para explicar a causa de cada excecao
FILHO_PARA_CAUSA = {
    "empresa":        "empresa_linha",
    "linha":          "grupo",
    "grupo":          "sku",
    "estado":         "estado_linha",
    "gerencia":       "gerencia_linha",
    "empresa_linha":  None,
    "estado_linha":   None,
    "gerencia_linha": None,
    "sku":            None,
    "segmento":       None,
    "cliente":        "cliente_linha",
    "cliente_linha":  None,
}

MESES_PT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
            "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

FATOR_MAD = 1.4826  # escala o MAD para equivaler a 1 sigma numa normal


# ─── Helpers ─────────────────────────────────────────────────────────────────

def log(msg):
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def fmt_mes(yyyymm):
    try:
        a, m = int(yyyymm) // 100, int(yyyymm) % 100
        return f"{MESES_PT[m - 1]}/{a}"
    except Exception:
        return str(yyyymm)


def fmt_num(v, dec=1):
    """Formato BR: 3.058,4"""
    try:
        s = f"{float(v):,.{dec}f}"
    except (TypeError, ValueError):
        return "n/d"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def rd(v, n=2):
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    if np.isnan(f) or np.isinf(f):
        return None
    return round(f, n)


def load_file(path, label, obrigatorio=True):
    p = Path(path)
    if not p.exists():
        if obrigatorio:
            sys.stderr.write(f"[ERRO] Arquivo nao encontrado: {path}\n")
            sys.exit(1)
        return None
    ext = p.suffix.lower()
    if ext in (".xlsx", ".xlsm", ".xls"):
        df = pd.read_excel(path)
    elif ext in (".csv", ".txt"):
        df = pd.read_csv(path, sep=None, engine="python")
    else:
        sys.stderr.write(f"[ERRO] Formato nao suportado: {ext}\n")
        sys.exit(1)
    # Normaliza acento da coluna de previsao (varia por SO/exportador)
    df.columns = [str(c).replace("Previsão Vol", "Previsao Vol").strip() for c in df.columns]
    if COL_MES in df.columns:
        df[COL_MES] = pd.to_numeric(df[COL_MES], errors="coerce").astype("Int64")
        df = df[df[COL_MES].notna()].copy()
        df[COL_MES] = df[COL_MES].astype(int)
    log(f"[OK] {label}: {len(df):,} linhas de '{p.name}'")
    return df


def checar_colunas(df, obrigatorias, label):
    faltando = [c for c in obrigatorias if c not in df.columns]
    if faltando:
        sys.stderr.write(
            f"[ERRO] Colunas ausentes em {label}: {faltando}\n"
            f"       Colunas encontradas: {list(df.columns)}\n"
        )
        sys.exit(1)


def chave_str(valores):
    return " | ".join(str(v) for v in valores)


# ─── Baseline robusto ────────────────────────────────────────────────────────

def estatisticas_baseline(hist, cfg):
    """hist: np.array com o volume de cada mes da janela historica (zeros incluidos)."""
    mediana = float(np.median(hist)) if len(hist) else 0.0
    mad = float(np.median(np.abs(hist - mediana))) if len(hist) else 0.0
    sigma_rob = mad * FATOR_MAD

    media = float(np.mean(hist)) if len(hist) else 0.0
    desvpad = float(np.std(hist, ddof=1)) if len(hist) > 1 else 0.0

    # Piso de dispersao: impede z-score explosivo em serie quase constante,
    # onde MAD=0 faria qualquer oscilacao virar alerta.
    piso = max(cfg["piso_rel"] * abs(mediana), cfg["piso_abs"])
    sigma_efetivo = max(sigma_rob, piso)
    if sigma_rob == 0 and desvpad > 0:
        sigma_efetivo = max(desvpad, piso)

    return {
        "mediana": mediana,
        "mad": mad,
        "sigma_robusto": sigma_rob,
        "sigma_efetivo": sigma_efetivo,
        "media": media,
        "desvpad": desvpad,
        "minimo": float(np.min(hist)) if len(hist) else 0.0,
        "maximo": float(np.max(hist)) if len(hist) else 0.0,
        "p25": float(np.percentile(hist, 25)) if len(hist) else 0.0,
        "p75": float(np.percentile(hist, 75)) if len(hist) else 0.0,
        "meses_ativos": int(np.sum(hist > 0)),
        "meses_janela": int(len(hist)),
    }


def contar_trailing(serie_valores, referencia, tol, direcao):
    """Quantos meses consecutivos, terminando no mes atual, ficaram fora da faixa."""
    n = 0
    for v in reversed(serie_valores):
        if direcao == "abaixo" and v < referencia * (1 - tol):
            n += 1
        elif direcao == "acima" and v > referencia * (1 + tol):
            n += 1
        else:
            break
    return n


# ─── Classificacao ───────────────────────────────────────────────────────────

def classificar(z, desvio_abs, share_total, base, cfg, atual, trailing_abaixo,
                trailing_acima, primeira_venda):
    """Devolve (tipo_primario, sinais, severidade)."""
    sinais = []
    mediana = base["mediana"]
    ativos = base["meses_ativos"]

    material = abs(desvio_abs) >= cfg["limiar_material"]
    muito_material = abs(desvio_abs) >= cfg["limiar_material"] * 3

    # Sinais estruturais (independem do z)
    if primeira_venda and atual > 0:
        sinais.append("estreia")
    if ativos >= cfg["min_meses_ativos"] and mediana > 0 and atual == 0:
        sinais.append("ruptura")
    if trailing_abaixo >= cfg["meses_tendencia"]:
        sinais.append("queda_sustentada")
    if trailing_acima >= cfg["meses_tendencia"]:
        sinais.append("crescimento_sustentado")

    # Sinais estatisticos
    if z is not None:
        if z <= -cfg["z_atencao"]:
            sinais.append("queda_atipica")
        elif z >= cfg["z_atencao"]:
            sinais.append("pico_atipico")

    if not sinais:
        return None, [], "normal"

    # Tipo primario: do mais especifico/explicativo ao mais generico
    ordem = ["ruptura", "estreia", "queda_sustentada", "queda_atipica",
             "pico_atipico", "crescimento_sustentado"]
    tipo = next((t for t in ordem if t in sinais), sinais[0])

    # Severidade = significancia estatistica X materialidade
    az = abs(z) if z is not None else 0.0
    sev = "observar"

    if "ruptura" in sinais and material:
        sev = "critico"
    elif az >= cfg["z_critico"] and material:
        sev = "critico"
    elif az >= cfg["z_atencao"] and muito_material:
        sev = "critico"
    elif az >= cfg["z_atencao"] and material:
        sev = "atencao"
    elif ("queda_sustentada" in sinais or "crescimento_sustentado" in sinais) and material:
        sev = "atencao"
    elif "estreia" in sinais:
        # Serie nova nao tem baseline, entao a gravidade vem so da materialidade
        sev = "critico" if abs(desvio_abs) >= cfg["limiar_material"] * 5 else (
            "atencao" if muito_material else "observar")

    # Trava de ruido: serie com historico curto nao vira critico sozinha...
    # ...a menos que o volume envolvido seja grande demais para ignorar.
    if base["meses_ativos"] < cfg["min_meses_ativos"] and sev == "critico":
        sinais.append("historico_curto")
        if abs(desvio_abs) < cfg["limiar_material"] * 5:
            sev = "atencao"

    # Trava de relevancia: peso irrisorio nunca e critico. Numa ruptura o peso
    # atual e zero por definicao, entao vale tambem o peso historico da serie.
    if sev == "critico" and share_total is not None:
        share_hist = (mediana / cfg["volume_mes"] * 100) if cfg.get("volume_mes") else None
        peso = max(share_total, share_hist or 0.0)
        if peso < cfg["share_min_critico"]:
            sev = "atencao"

    return tipo, sinais, sev


def score_prioridade(z, desvio_abs):
    az = min(abs(z), 10.0) if z is not None else 1.0
    return round(az * (abs(desvio_abs) ** 0.5), 2)


# ─── Perguntas para o comercial ──────────────────────────────────────────────

TEMPLATES_PERGUNTA = {
    "ruptura": (
        "{alvo} zerou em {mes} depois de {ativos} meses vendendo (mediana {mediana} t). "
        "E perda de cliente, ruptura de estoque, decisao de preco ou o pedido escorregou para o mes seguinte?"
    ),
    "queda_sustentada": (
        "{alvo} esta abaixo da mediana historica ha {trailing} meses seguidos "
        "({atual} t em {mes} vs. mediana {mediana} t, {desvio_pct}). "
        "Isso e movimento de mercado, perda para concorrente ou decisao nossa de mix/preco?"
    ),
    "queda_atipica": (
        "{alvo} caiu para {atual} t em {mes} contra mediana de {mediana} t ({desvio_pct}, z={z}). "
        "O que mudou neste mes? Ha cliente especifico por tras ou e queda difusa?"
    ),
    "pico_atipico": (
        "{alvo} saltou para {atual} t em {mes} contra mediana de {mediana} t ({desvio_pct}, z={z}). "
        "E demanda recorrente, obra pontual ou antecipacao de pedido? Da para sustentar no proximo mes?"
    ),
    "crescimento_sustentado": (
        "{alvo} esta acima da mediana ha {trailing} meses seguidos ({atual} t em {mes}). "
        "Esse novo patamar ja esta refletido na previsao? Precisamos rever capacidade ou estoque?"
    ),
    "estreia": (
        "{alvo} aparece pela primeira vez em {mes} com {atual} t. "
        "E cliente/produto novo de verdade, mudanca de cadastro ou reclassificacao na base?"
    ),
    "desvio_previsao": (
        "{alvo} fechou {atual} t contra previsao de {previsto} t ({ating_pct} de atingimento). "
        "A previsao estava errada ou a execucao ficou aquem? Quem revisa e quando?"
    ),
    "previsao_nao_realizada": (
        "{alvo} tinha {previsto} t previstos em {mes} e nao realizou nada. "
        "A previsao entrou por engano, o pedido nao veio ou foi faturado em outra chave?"
    ),
    "venda_sem_previsao": (
        "{alvo} vendeu {atual} t em {mes} sem nenhuma previsao. "
        "E demanda nao mapeada ou falha no processo de forecast?"
    ),
}


def montar_pergunta(exc, mes_label):
    tipo = exc["tipo"]
    tpl = TEMPLATES_PERGUNTA.get(tipo)
    if not tpl:
        return None
    dp = exc.get("desvio_pct")
    return tpl.format(
        alvo=f"{exc['nivel_rotulo']} '{exc['chave']}'",
        mes=mes_label,
        atual=fmt_num(exc["valor_atual"]),
        mediana=fmt_num(exc["mediana"]),
        previsto=fmt_num(exc.get("previsto") or 0),
        ating_pct=f"{exc.get('atingimento_pct')}%" if exc.get("atingimento_pct") is not None else "n/d",
        desvio_pct=f"{dp:+.1f}%".replace(".", ",") if dp is not None else "n/d",
        z=f"{exc['z_robusto']:.1f}".replace(".", ",") if exc.get("z_robusto") is not None else "n/d",
        trailing=exc.get("meses_fora_faixa") or 0,
        ativos=exc.get("meses_ativos") or 0,
    )


# ─── Motor principal ─────────────────────────────────────────────────────────

def series_por_nivel(df, dims, col_valor, meses):
    """Matriz serie x mes, com zeros preenchidos nos meses sem movimento."""
    d = df.copy()
    for c in dims:
        d[c] = d[c].fillna("(nao informado)").astype(str)
    piv = (d.groupby(dims + [COL_MES], dropna=False)[col_valor]
             .sum()
             .unstack(COL_MES)
             .reindex(columns=meses, fill_value=0.0)
             .fillna(0.0))
    return piv


def analisar_nivel(nivel, df_v, df_p, meses_hist, mes_atual, cfg, total_mes):
    dims = nivel["dims"]
    if any(c not in df_v.columns for c in dims):
        return [], {"nivel": nivel["id"], "status": "colunas_ausentes"}

    meses_serie = meses_hist + [mes_atual]
    piv = series_por_nivel(df_v, dims, COL_VENDA, meses_serie)

    # Previsao no mes atual (so para niveis sem dimensao exclusiva de vendas)
    prev_map = {}
    usa_prev = df_p is not None and not any(c in DIMS_SO_VENDAS for c in dims)
    if usa_prev and all(c in df_p.columns for c in dims):
        dp = df_p[df_p[COL_MES] == mes_atual].copy()
        for c in dims:
            dp[c] = dp[c].fillna("(nao informado)").astype(str)
        if len(dp):
            g = dp.groupby(dims, dropna=False)[COL_PREV].sum()
            prev_map = {(k if isinstance(k, tuple) else (k,)): float(v) for k, v in g.items()}

    # Primeira venda de cada serie em toda a base (nao so na janela)
    primeiro_mes = {}
    dv = df_v.copy()
    for c in dims:
        dv[c] = dv[c].fillna("(nao informado)").astype(str)
    g_first = dv[dv[COL_VENDA] > 0].groupby(dims, dropna=False)[COL_MES].min()
    for k, v in g_first.items():
        primeiro_mes[k if isinstance(k, tuple) else (k,)] = int(v)

    excecoes = []
    n_series = 0

    for idx, row in piv.iterrows():
        chave_tupla = idx if isinstance(idx, tuple) else (idx,)
        valores = row.values.astype(float)
        hist = valores[:-1]
        atual = float(valores[-1])
        n_series += 1

        base = estatisticas_baseline(hist, cfg)
        previsto = prev_map.get(chave_tupla)

        # Descarta poeira: serie sem relevancia nem no historico nem agora
        if base["maximo"] < cfg["volume_minimo"] and atual < cfg["volume_minimo"] \
           and (previsto or 0) < cfg["volume_minimo"]:
            continue

        desvio_abs = atual - base["mediana"]
        desvio_pct = ((atual - base["mediana"]) / base["mediana"] * 100
                      if base["mediana"] > 0 else None)
        z = (desvio_abs / base["sigma_efetivo"]) if base["sigma_efetivo"] > 0 else None
        # Sem nenhum mes ativo no historico nao existe baseline: z seria um numero
        # gigante e sem significado. A serie e tratada como estreia, nao como pico.
        if base["meses_ativos"] == 0:
            z = None
        elif z is not None:
            z = float(np.clip(z, -50.0, 50.0))
        share = (atual / total_mes * 100) if total_mes else None

        trailing_abaixo = contar_trailing(list(valores), base["mediana"], cfg["tol_tendencia"], "abaixo") \
            if base["mediana"] > 0 else 0
        trailing_acima = contar_trailing(list(valores), base["mediana"], cfg["tol_tendencia"], "acima") \
            if base["mediana"] > 0 else 0
        primeira_venda = primeiro_mes.get(chave_tupla) == mes_atual

        tipo, sinais, sev = classificar(
            z, desvio_abs, share, base, cfg, atual,
            trailing_abaixo, trailing_acima, primeira_venda
        )

        # Camada previsao (pode criar excecao mesmo sem anomalia historica)
        prev_bloco = None
        if previsto is not None or (usa_prev and atual > 0 and prev_map):
            pv = previsto or 0.0
            desvio_prev = atual - pv
            ating = (atual / pv * 100) if pv > 0 else None
            prev_bloco = {
                "previsto": rd(pv, 1),
                "desvio_prev_abs": rd(desvio_prev, 1),
                "atingimento_pct": rd(ating, 1),
            }
            material_prev = abs(desvio_prev) >= cfg["limiar_material"]
            if pv > 0 and atual == 0 and material_prev:
                sinais.append("previsao_nao_realizada")
                tipo = tipo or "previsao_nao_realizada"
                sev = "critico" if sev in ("normal", "observar") else sev
            elif pv == 0 and atual > 0 and material_prev:
                sinais.append("venda_sem_previsao")
                tipo = tipo or "venda_sem_previsao"
                sev = "atencao" if sev in ("normal", "observar") else sev
            elif ating is not None and abs(ating - 100) >= cfg["tol_previsao_pct"] and material_prev:
                sinais.append("desvio_previsao")
                if tipo is None:
                    tipo = "desvio_previsao"
                if sev in ("normal", "observar"):
                    sev = "critico" if (abs(ating - 100) >= cfg["tol_previsao_pct"] * 2
                                        and abs(desvio_prev) >= cfg["limiar_material"] * 3) else "atencao"

        if tipo is None or sev == "normal":
            continue

        exc = {
            "nivel": nivel["id"],
            "nivel_rotulo": nivel["rotulo"],
            "camada": CAMADA.get(nivel["id"], "macro"),
            "dims": dims,
            "chave_valores": list(chave_tupla),
            "chave": chave_str(chave_tupla),
            "tipo": tipo,
            "sinais": sorted(set(sinais)),
            "severidade": sev,
            "valor_atual": rd(atual, 1),
            "mediana": rd(base["mediana"], 1),
            "media": rd(base["media"], 1),
            "mad": rd(base["mad"], 2),
            "sigma_robusto": rd(base["sigma_robusto"], 2),
            "desvpad": rd(base["desvpad"], 2),
            "p25": rd(base["p25"], 1),
            "p75": rd(base["p75"], 1),
            "minimo_hist": rd(base["minimo"], 1),
            "maximo_hist": rd(base["maximo"], 1),
            "z_robusto": rd(z, 2),
            "desvio_abs": rd(desvio_abs, 1),
            "desvio_pct": rd(desvio_pct, 1),
            "share_mes_pct": rd(share, 2),
            "meses_ativos": base["meses_ativos"],
            "meses_janela": base["meses_janela"],
            "meses_fora_faixa": max(trailing_abaixo, trailing_acima),
            "direcao": "queda" if desvio_abs < 0 else "alta",
            "serie": [rd(v, 1) for v in valores],
            "score": score_prioridade(z, desvio_abs),
        }
        if prev_bloco:
            exc.update(prev_bloco)
        excecoes.append(exc)

    return excecoes, {"nivel": nivel["id"], "series_avaliadas": n_series,
                      "excecoes": len(excecoes), "status": "ok"}


# ─── Causa raiz ──────────────────────────────────────────────────────────────

def explicar_causa(exc, df_v, meses_hist, mes_atual, cfg, todas_por_nivel, top_n=3):
    """Top contribuintes do desvio: no nivel filho e por cliente."""
    causas = {}
    nivel_filho = FILHO_PARA_CAUSA.get(exc["nivel"])
    dims_pai = exc["dims"]
    filtro = pd.Series(True, index=df_v.index)
    for c, v in zip(dims_pai, exc["chave_valores"]):
        filtro &= (df_v[c].fillna("(nao informado)").astype(str) == str(v))
    sub = df_v[filtro]
    if sub.empty:
        return causas

    def top_contribuintes(dims_filho):
        dims_extra = [d for d in dims_filho if d not in dims_pai]
        if not dims_extra:
            return []
        piv = series_por_nivel(sub, dims_extra, COL_VENDA, meses_hist + [mes_atual])
        saida = []
        for idx, row in piv.iterrows():
            vals = row.values.astype(float)
            med = float(np.median(vals[:-1]))
            atual = float(vals[-1])
            delta = atual - med
            if abs(delta) < cfg["volume_minimo"] * 0.5:
                continue
            saida.append({
                "chave": chave_str(idx if isinstance(idx, tuple) else (idx,)),
                "atual": rd(atual, 1),
                "mediana": rd(med, 1),
                "delta": rd(delta, 1),
                "part_do_desvio_pct": rd(delta / exc["desvio_abs"] * 100, 1)
                if exc["desvio_abs"] else None,
            })
        # mesma direcao do desvio do pai primeiro, ordenado por magnitude
        saida.sort(key=lambda x: -abs(x["delta"] or 0))
        return saida[:top_n]

    if nivel_filho:
        dims_filho = next(n["dims"] for n in NIVEIS if n["id"] == nivel_filho)
        c = top_contribuintes(dims_filho)
        if c:
            causas["por_" + nivel_filho] = c

    # Cliente sempre explica, quando a dimensao existe e nao e o proprio nivel
    if COL_CLIENTE in df_v.columns and COL_CLIENTE not in dims_pai:
        c = top_contribuintes(dims_pai + [COL_CLIENTE])
        if c:
            causas["por_cliente"] = c

    if COL_SEGMENTO in df_v.columns and COL_SEGMENTO not in dims_pai and exc["nivel"] != "cliente":
        c = top_contribuintes(dims_pai + [COL_SEGMENTO])
        if c:
            causas["por_segmento"] = c[:2]

    return causas


def marcar_redundantes(excecoes, cfg):
    """
    Quando UM filho sozinho explica quase todo o desvio do pai, a manchete util
    e o filho (especifico e acionavel) — o pai vira eco. Ex.: 'Estado SP caiu'
    quando 100% da queda de SP e a linha CA-50: a manchete e 'SP | CA-50'.
    """
    por_nivel_chave = {}
    for e in excecoes:
        por_nivel_chave.setdefault(e["nivel"], {})[e["chave"]] = e

    for e in excecoes:
        pai_id = next((n["pai"] for n in NIVEIS if n["id"] == e["nivel"]), None)
        if not pai_id:
            continue
        dims_pai = next(n["dims"] for n in NIVEIS if n["id"] == pai_id)
        chave_pai = chave_str([v for c, v in zip(e["dims"], e["chave_valores"]) if c in dims_pai])
        pai = por_nivel_chave.get(pai_id, {}).get(chave_pai)
        if not pai or pai.get("redundante_com"):
            continue
        if pai["direcao"] != e["direcao"] or not pai.get("desvio_abs"):
            continue
        cobertura = abs(e["desvio_abs"] / pai["desvio_abs"])
        if cobertura >= cfg["cobertura_redundante"]:
            pai["redundante_com"] = {
                "nivel": e["nivel"], "chave": e["chave"],
                "cobertura_pct": rd(cobertura * 100, 1),
                "motivo": "desvio explicado quase inteiramente por este filho",
            }
    return excecoes


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Radar de Excecoes de Vendas")
    ap.add_argument("--vendas", required=True)
    ap.add_argument("--previsao", default=None)
    ap.add_argument("--output", required=True)
    ap.add_argument("--csv", default=None, help="CSV opcional com todas as excecoes")
    ap.add_argument("--mes", type=int, default=None, help="YYYYMM do mes a analisar")
    ap.add_argument("--janela", type=int, default=12, help="meses de historico (default 12)")
    ap.add_argument("--z-critico", type=float, default=3.0)
    ap.add_argument("--z-atencao", type=float, default=2.0)
    ap.add_argument("--min-meses-ativos", type=int, default=4)
    ap.add_argument("--volume-minimo", type=float, default=1.0,
                    help="volume (t) abaixo do qual a serie e ignorada")
    ap.add_argument("--material-pct", type=float, default=0.5,
                    help="%% do volume do mes que torna um desvio material")
    ap.add_argument("--tol-previsao", type=float, default=20.0,
                    help="%% de desvio vs. previsao que vira alerta")
    ap.add_argument("--top-excecoes", type=int, default=120)
    args = ap.parse_args()

    cfg = {
        "z_critico": args.z_critico,
        "z_atencao": args.z_atencao,
        "min_meses_ativos": args.min_meses_ativos,
        "volume_minimo": args.volume_minimo,
        "piso_rel": 0.10,
        "piso_abs": max(args.volume_minimo * 0.5, 0.1),
        "meses_tendencia": 3,
        "tol_tendencia": 0.15,
        "tol_previsao_pct": args.tol_previsao,
        "share_min_critico": 0.05,
        "cobertura_redundante": 0.70,
    }

    df_v = load_file(args.vendas, "Vendas")
    checar_colunas(df_v, [COL_MES, COL_VENDA, COL_LINHA], "Vendas")
    df_v[COL_VENDA] = pd.to_numeric(df_v[COL_VENDA], errors="coerce").fillna(0.0)

    df_p = None
    if args.previsao:
        df_p = load_file(args.previsao, "Previsao", obrigatorio=False)
        if df_p is not None:
            if COL_PREV not in df_p.columns:
                log(f"[AVISO] Coluna '{COL_PREV}' ausente na previsao — camada de forecast desligada.")
                df_p = None
            else:
                df_p[COL_PREV] = pd.to_numeric(df_p[COL_PREV], errors="coerce").fillna(0.0)

    meses = sorted(int(m) for m in df_v[COL_MES].unique())
    if not meses:
        sys.stderr.write("[ERRO] Nenhum periodo valido em numero_ano_mes.\n")
        sys.exit(1)

    mes_atual = args.mes if args.mes in meses else meses[-1]
    if args.mes and args.mes not in meses:
        log(f"[AVISO] Mes {args.mes} nao existe na base. Usando {mes_atual}.")

    anteriores = [m for m in meses if m < mes_atual]
    meses_hist = anteriores[-args.janela:]
    if len(meses_hist) < 3:
        log(f"[AVISO] Apenas {len(meses_hist)} meses de historico. "
            f"Os z-scores ficam frageis — trate os alertas como indicativos.")

    total_mes = float(df_v[df_v[COL_MES] == mes_atual][COL_VENDA].sum())
    cfg["limiar_material"] = max(total_mes * args.material_pct / 100.0, args.volume_minimo)
    cfg["volume_mes"] = total_mes

    log(f"[..] Mes de analise: {fmt_mes(mes_atual)} | historico: "
        f"{fmt_mes(meses_hist[0]) if meses_hist else '-'} a "
        f"{fmt_mes(meses_hist[-1]) if meses_hist else '-'} ({len(meses_hist)} meses)")
    log(f"[..] Volume do mes: {total_mes:,.1f} t | limiar de materialidade: "
        f"{cfg['limiar_material']:,.1f} t")

    todas = []
    diagnostico_niveis = []
    for nivel in NIVEIS:
        exc, diag = analisar_nivel(nivel, df_v, df_p, meses_hist, mes_atual, cfg, total_mes)
        todas.extend(exc)
        diagnostico_niveis.append(diag)
        log(f"[..] {nivel['rotulo']}: {diag.get('series_avaliadas', 0)} series -> "
            f"{diag.get('excecoes', 0)} excecoes")

    todas = marcar_redundantes(todas, cfg)
    ordem_sev = {"critico": 0, "atencao": 1, "observar": 2}
    todas.sort(key=lambda e: (ordem_sev.get(e["severidade"], 9), -e["score"]))

    # Causa raiz apenas para as que vao ao deck (custo computacional)
    manchetes = [e for e in todas if not e.get("redundante_com")]
    for e in manchetes[:30]:
        e["causas"] = explicar_causa(e, df_v, meses_hist, mes_atual, cfg, todas)

    mes_label = fmt_mes(mes_atual)
    for e in todas:
        e["pergunta_comercial"] = montar_pergunta(e, mes_label)

    todas = todas[:args.top_excecoes]

    def conta(sev, apenas_manchete=True):
        return len([e for e in todas if e["severidade"] == sev
                    and (not apenas_manchete or not e.get("redundante_com"))])

    hist_total = [float(df_v[df_v[COL_MES] == m][COL_VENDA].sum()) for m in meses_hist]
    base_total = estatisticas_baseline(np.array(hist_total), cfg) if hist_total else None

    resultado = {
        "meta": {
            "mes_analisado": mes_atual,
            "mes_analisado_label": mes_label,
            "meses_historico": meses_hist,
            "meses_historico_label": [fmt_mes(m) for m in meses_hist],
            "janela": len(meses_hist),
            "tem_previsao": df_p is not None,
            "parametros": {k: v for k, v in cfg.items()},
            "linhas_vendas": int(len(df_v)),
        },
        "panorama": {
            "volume_mes": rd(total_mes, 1),
            "mediana_historica": rd(base_total["mediana"], 1) if base_total else None,
            "media_historica": rd(base_total["media"], 1) if base_total else None,
            "desvio_vs_mediana_abs": rd(total_mes - base_total["mediana"], 1) if base_total else None,
            "desvio_vs_mediana_pct": rd((total_mes - base_total["mediana"]) / base_total["mediana"] * 100, 1)
            if base_total and base_total["mediana"] else None,
            "z_robusto_total": rd((total_mes - base_total["mediana"]) / base_total["sigma_efetivo"], 2)
            if base_total and base_total["sigma_efetivo"] else None,
            "serie_total": [rd(v, 1) for v in hist_total] + [rd(total_mes, 1)],
            "previsto_mes": rd(float(df_p[df_p[COL_MES] == mes_atual][COL_PREV].sum()), 1)
            if df_p is not None else None,
        },
        "contagem": {
            "criticos": conta("critico"),
            "atencao": conta("atencao"),
            "observar": conta("observar"),
            "total_excecoes": len(todas),
            "redundantes_suprimidas": len([e for e in todas if e.get("redundante_com")]),
        },
        "diagnostico_niveis": diagnostico_niveis,
        "manchetes_por_camada": {
            cam: [e["chave"] + f"  [{e['nivel']}/{e['severidade']}/{e['tipo']}]"
                  for e in todas
                  if e["camada"] == cam and not e.get("redundante_com")][:12]
            for cam in ("macro", "produto", "cliente")
        },
        "excecoes": todas,
        "qualidade_dados": {
            "meses_na_base": [fmt_mes(m) for m in meses],
            "colunas_vendas": list(df_v.columns),
            "colunas_previsao": list(df_p.columns) if df_p is not None else None,
            "nulos_por_coluna": {c: int(df_v[c].isna().sum())
                                 for c in df_v.columns if df_v[c].isna().any()},
        },
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    def _json_safe(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.bool_,)):
            return bool(o)
        return str(o)

    out.write_text(json.dumps(resultado, ensure_ascii=False, indent=2, default=_json_safe),
                   encoding="utf-8")
    log(f"[OK] JSON gravado em {out}")

    if args.csv:
        cols = ["severidade", "tipo", "nivel_rotulo", "chave", "valor_atual", "mediana",
                "desvio_abs", "desvio_pct", "z_robusto", "meses_ativos", "share_mes_pct",
                "previsto", "atingimento_pct", "score"]
        dfe = pd.DataFrame(todas)
        for c in cols:
            if c not in dfe.columns:
                dfe[c] = None
        dfe[cols].to_csv(args.csv, index=False, sep=";", decimal=",", encoding="utf-8-sig")
        log(f"[OK] CSV gravado em {args.csv}")

    c = resultado["contagem"]
    log(f"\n[RESUMO] {c['criticos']} criticos | {c['atencao']} atencao | "
        f"{c['observar']} observar | {c['redundantes_suprimidas']} redundantes")


if __name__ == "__main__":
    main()
