#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente de Analise de Desvios de Vendas — script de calculos
Gera JSON estruturado com todas as metricas prontas para o relatorio.

Uso:
    python analisar_desvios.py \
        --vendas tabela_vendas.xlsx \
        --previsao tabela_previsao.xlsx \
        --output analise_resultado.json
"""

import argparse
import json
import sys
import warnings
from pathlib import Path

import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")

# ─── Constantes ──────────────────────────────────────────────────────────────

CHAVE_JOIN = [
    "numero_ano_mes",
    "descricao_empresa_3",
    "descricao_linha",
    "descricao_grupo",
    "descricao_espessura",
    "descricao_estado",
    "descricao_gerencia_2",
]

COL_VENDA = "Venda Vol"
COL_PREV  = "Previsao Vol"

# ─── Helpers ─────────────────────────────────────────────────────────────────

def fmt_mes(yyyymm):
    meses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    ano = int(yyyymm) // 100
    mes = int(yyyymm) % 100
    return f"{meses[mes-1]}/{ano}"

def pct(realizado, previsto):
    if not previsto or previsto == 0:
        return None
    return round((realizado - previsto) / previsto * 100, 1)

def ating(realizado, previsto):
    if not previsto or previsto == 0:
        return None
    return round(realizado / previsto * 100, 1)

def r1(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    return round(float(v), 1)

def r2(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    return round(float(v), 2)

def log(msg):
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()

# ─── Carregamento ─────────────────────────────────────────────────────────────

def load_file(path, label):
    p = Path(path)
    if not p.exists():
        sys.stderr.write(f"[ERRO] Arquivo nao encontrado: {path}\n")
        sys.exit(1)
    ext = p.suffix.lower()
    if ext in (".xlsx", ".xls"):
        df = pd.read_excel(path, dtype={"numero_ano_mes": int})
    elif ext == ".csv":
        df = pd.read_csv(path, dtype={"numero_ano_mes": int})
    else:
        sys.stderr.write(f"[ERRO] Formato nao suportado: {ext}\n")
        sys.exit(1)
    # Normalizar nome da coluna de previsao (acento pode variar por SO)
    df.columns = [c.replace("Previsão Vol", "Previsao Vol") for c in df.columns]
    log(f"[OK] {label}: {len(df):,} linhas de '{p.name}'")
    return df

# ─── Join macro ───────────────────────────────────────────────────────────────

def build_macro_join(df_v, df_p):
    vagg = df_v.groupby(CHAVE_JOIN, dropna=False)[COL_VENDA].sum().reset_index()
    pagg = df_p.groupby(CHAVE_JOIN, dropna=False)[COL_PREV].sum().reset_index()
    m = pd.merge(vagg, pagg, on=CHAVE_JOIN, how="outer")
    m[COL_VENDA] = m[COL_VENDA].fillna(0)
    m[COL_PREV]  = m[COL_PREV].fillna(0)
    m["desvio_abs"] = m[COL_VENDA] - m[COL_PREV]
    m["desvio_pct"] = m.apply(lambda r: pct(r[COL_VENDA], r[COL_PREV]), axis=1)
    return m

# ─── Classificacao de clientes ────────────────────────────────────────────────

def classificar_clientes(df_v, mes_atual):
    """
    Novo: sem nenhuma compra em meses anteriores ao mes_atual.
    Reativado: comprou em algum mes anterior, mas nao no mes imediatamente anterior.
    Recorrente: comprou no mes imediatamente anterior.
    """
    meses = sorted(df_v["numero_ano_mes"].unique())
    idx_atual = list(meses).index(mes_atual) if mes_atual in meses else len(meses) - 1
    mes_ant = meses[idx_atual - 1] if idx_atual > 0 else None
    meses_anteriores = [m for m in meses if m < mes_atual]

    clientes_atual = set(df_v[df_v["numero_ano_mes"] == mes_atual]["descricao_parceiro_master"].dropna())
    clientes_ant   = set(df_v[df_v["numero_ano_mes"] == mes_ant]["descricao_parceiro_master"].dropna()) if mes_ant else set()
    clientes_hist  = set(df_v[df_v["numero_ano_mes"].isin(meses_anteriores)]["descricao_parceiro_master"].dropna())

    status = {}
    for c in clientes_atual:
        if c not in clientes_hist:
            status[c] = "Novo"
        elif c not in clientes_ant:
            status[c] = "Reativado"
        else:
            status[c] = "Recorrente"
    return status, clientes_ant

# ─── HHI e concentracao ───────────────────────────────────────────────────────

def calcular_hhi(volumes):
    """HHI = soma dos quadrados dos shares. Retorna valor de 0 a 1."""
    total = sum(volumes)
    if total == 0:
        return None
    shares = [v / total for v in volumes]
    return round(sum(s**2 for s in shares), 4)

def interpretar_hhi(hhi):
    if hhi is None:
        return "N/A"
    if hhi < 0.10:
        return "Pulverizado"
    if hhi < 0.18:
        return "Moderado"
    return "Concentrado"

def curva_concentracao(df_mes, col_vol, col_cliente, tops=(1, 5, 10, 20, 50, 100)):
    """Retorna share acumulado dos top-N clientes."""
    vol_por_cliente = df_mes.groupby(col_cliente)[col_vol].sum().sort_values(ascending=False)
    total = vol_por_cliente.sum()
    resultado = {}
    for n in tops:
        top_n_vol = vol_por_cliente.head(n).sum()
        resultado[f"top{n}_pct"] = r1(top_n_vol / total * 100) if total > 0 else None
    resultado["total_clientes"] = len(vol_por_cliente)
    return resultado

# ─── Secao 1: Indicadores-chave ──────────────────────────────────────────────

def secao_indicadores(df_v, merged, mes_atual, status_clientes):
    df_mes = df_v[df_v["numero_ano_mes"] == mes_atual]
    total_real = df_mes[COL_VENDA].sum()
    prev_mes   = merged[merged["numero_ano_mes"] == mes_atual][COL_PREV].sum()

    vols_cliente = df_mes.groupby("descricao_parceiro_master")[COL_VENDA].sum()
    hhi = calcular_hhi(vols_cliente.tolist())
    conc = curva_concentracao(df_mes, COL_VENDA, "descricao_parceiro_master")

    novos    = [c for c, s in status_clientes.items() if s == "Novo"]
    vol_novos = df_mes[df_mes["descricao_parceiro_master"].isin(novos)][COL_VENDA].sum()

    # Acumulado apenas meses com vendas (exclui futuros)
    meses_com_venda = sorted(df_v["numero_ano_mes"].unique())
    m_real = merged[merged["numero_ano_mes"].isin(meses_com_venda)][COL_VENDA].sum()
    m_prev = merged[merged["numero_ano_mes"].isin(meses_com_venda)][COL_PREV].sum()

    return {
        "mes_atual": fmt_mes(mes_atual),
        "realizado_mes_ton": r1(total_real),
        "previsto_mes_ton":  r1(prev_mes),
        "atingimento_pct":   ating(total_real, prev_mes),
        "clientes_ativos":   len(vols_cliente),
        "concentracao": conc,
        "hhi": hhi,
        "hhi_interpretacao": interpretar_hhi(hhi),
        "clientes_novos_qtd": len(novos),
        "clientes_novos_vol_ton": r1(vol_novos),
        "clientes_novos_share_pct": r1(vol_novos / total_real * 100) if total_real > 0 else None,
        "acumulado_meses_realizados": {
            "realizado_ton": r1(m_real),
            "previsto_ton":  r1(m_prev),
            "desvio_abs_ton": r1(m_real - m_prev),
            "desvio_pct":    pct(m_real, m_prev),
            "n_meses": len(meses_com_venda),
        },
    }

# ─── Secao 2: Diagnostico executivo ──────────────────────────────────────────

def secao_diagnostico(df_v, merged):
    meses = sorted(merged["numero_ano_mes"].unique())
    resumo = []
    for m in meses:
        sub_m  = merged[merged["numero_ano_mes"] == m]
        sub_v  = df_v[df_v["numero_ano_mes"] == m]
        real   = sub_m[COL_VENDA].sum()
        prev   = sub_m[COL_PREV].sum()
        n_cli  = sub_v["descricao_parceiro_master"].nunique()
        resumo.append({
            "periodo":       fmt_mes(m),
            "yyyymm":        int(m),
            "realizado_ton": r1(real),
            "previsto_ton":  r1(prev),
            "desvio_abs_ton": r1(real - prev),
            "desvio_pct":    pct(real, prev),
            "atingimento_pct": ating(real, prev),
            "clientes_ativos": int(n_cli),
            "tem_vendas":    real > 0,
        })
    return {"resumo_mensal": resumo}

# ─── Secao 3: Concentracao e clientes ────────────────────────────────────────

def secao_concentracao(df_v, mes_atual, status_clientes):
    df_mes = df_v[df_v["numero_ano_mes"] == mes_atual]
    total  = df_mes[COL_VENDA].sum()

    vol_cli = (
        df_mes.groupby("descricao_parceiro_master", dropna=False)[COL_VENDA]
        .sum()
        .reset_index()
        .sort_values(COL_VENDA, ascending=False)
    )

    # Top 20 com segmento e status
    seg_map = (
        df_mes.groupby("descricao_parceiro_master")["descricao_segmento_mercado"]
        .agg(lambda x: x.value_counts().index[0] if len(x) > 0 else "N/A")
        .to_dict()
    )

    top20 = []
    for _, row in vol_cli.head(20).iterrows():
        c = row["descricao_parceiro_master"]
        top20.append({
            "cliente":    str(c),
            "segmento":   seg_map.get(c, "N/A"),
            "status":     status_clientes.get(c, "N/A"),
            "volume_ton": r1(row[COL_VENDA]),
            "share_pct":  r1(row[COL_VENDA] / total * 100) if total > 0 else None,
        })

    hhi = calcular_hhi(vol_cli[COL_VENDA].tolist())
    conc = curva_concentracao(df_mes, COL_VENDA, "descricao_parceiro_master")

    return {
        "top20_clientes": top20,
        "concentracao_cumulativa": conc,
        "hhi": hhi,
        "hhi_interpretacao": interpretar_hhi(hhi),
    }

# ─── Secao 4: Mix Grupo × Espessura ──────────────────────────────────────────

def secao_mix_produto(df_v, mes_atual):
    df_mes = df_v[df_v["numero_ano_mes"] == mes_atual]
    total  = df_mes[COL_VENDA].sum()

    # Ranking Grupo × Espessura
    grp = (
        df_mes.groupby(["descricao_grupo", "descricao_espessura"], dropna=False)
        .agg(volume_ton=(COL_VENDA, "sum"), n_clientes=("descricao_parceiro_master", "nunique"))
        .reset_index()
        .sort_values("volume_ton", ascending=False)
    )
    grp["share_pct"] = (grp["volume_ton"] / total * 100).round(1)
    grp["volume_ton"] = grp["volume_ton"].round(1)
    ranking = grp.head(20).to_dict(orient="records")

    # Por linha
    por_linha = (
        df_mes.groupby("descricao_linha", dropna=False)
        .agg(volume_ton=(COL_VENDA, "sum"), n_clientes=("descricao_parceiro_master", "nunique"))
        .reset_index()
        .sort_values("volume_ton", ascending=False)
    )
    por_linha["share_pct"] = (por_linha["volume_ton"] / total * 100).round(1)
    por_linha["volume_ton"] = por_linha["volume_ton"].round(1)

    # Top 15 clientes: o que compraram (top 3 combinacoes por cliente)
    top15_cli = (
        df_mes.groupby("descricao_parceiro_master")[COL_VENDA]
        .sum().sort_values(ascending=False).head(15).index.tolist()
    )
    compras_top15 = []
    for c in top15_cli:
        sub_c = df_mes[df_mes["descricao_parceiro_master"] == c]
        combos = (
            sub_c.groupby(["descricao_grupo", "descricao_espessura"])[COL_VENDA]
            .sum().sort_values(ascending=False).head(3).reset_index()
        )
        compras_top15.append({
            "cliente": str(c),
            "compras_principais": [
                {
                    "grupo_espessura": f"{row['descricao_grupo']} {row['descricao_espessura']}mm",
                    "volume_ton": r1(row[COL_VENDA]),
                }
                for _, row in combos.iterrows()
            ],
        })

    return {
        "ranking_grupo_espessura": ranking,
        "por_linha": por_linha.to_dict(orient="records"),
        "compras_top15_clientes": compras_top15,
    }

# ─── Secao 5: Segmentos ───────────────────────────────────────────────────────

def secao_segmentos(df_v, mes_atual):
    df_mes  = df_v[df_v["numero_ano_mes"] == mes_atual]
    total   = df_mes[COL_VENDA].sum()
    meses   = sorted(df_v["numero_ano_mes"].unique())

    seg_mes = (
        df_mes.groupby("descricao_segmento_mercado", dropna=False)
        .agg(volume_ton=(COL_VENDA, "sum"), n_clientes=("descricao_parceiro_master", "nunique"))
        .reset_index()
        .sort_values("volume_ton", ascending=False)
    )
    seg_mes["share_pct"] = (seg_mes["volume_ton"] / total * 100).round(1)
    seg_mes["volume_ton"] = seg_mes["volume_ton"].round(1)

    # Evolucao por segmento nos meses disponíveis
    evolucao = []
    for m in meses:
        sub = df_v[df_v["numero_ano_mes"] == m]
        t   = sub[COL_VENDA].sum()
        for seg, g in sub.groupby("descricao_segmento_mercado", dropna=False):
            v = g[COL_VENDA].sum()
            evolucao.append({
                "periodo": fmt_mes(m),
                "yyyymm":  int(m),
                "segmento": str(seg),
                "volume_ton": r1(v),
                "share_pct": r1(v / t * 100) if t > 0 else None,
            })

    return {
        "segmentos_mes_atual": seg_mes.to_dict(orient="records"),
        "evolucao_mensal": evolucao,
    }

# ─── Secao 6: Geografico ──────────────────────────────────────────────────────

def secao_geografico(df_v, merged, mes_atual):
    def resumo(df_m, df_merged_m, col):
        grp_v = df_m.groupby(col, dropna=False).agg(
            realizado_ton=(COL_VENDA, "sum"),
            n_clientes=("descricao_parceiro_master", "nunique"),
        ).reset_index()
        grp_p = df_merged_m.groupby(col, dropna=False)[COL_PREV].sum().reset_index()
        grp_p.columns = [col, "previsto_ton"]
        r = pd.merge(grp_v, grp_p, on=col, how="outer").fillna(0)
        r["desvio_abs_ton"] = (r["realizado_ton"] - r["previsto_ton"]).round(1)
        r["desvio_pct"]     = r.apply(lambda x: pct(x["realizado_ton"], x["previsto_ton"]), axis=1)
        r["realizado_ton"]  = r["realizado_ton"].round(1)
        r["previsto_ton"]   = r["previsto_ton"].round(1)
        return r.sort_values("desvio_abs_ton").to_dict(orient="records")

    df_mes      = df_v[df_v["numero_ano_mes"] == mes_atual]
    merged_mes  = merged[merged["numero_ano_mes"] == mes_atual]
    merged_todos = merged[merged["numero_ano_mes"].isin(df_v["numero_ano_mes"].unique())]
    df_todos    = df_v[df_v["numero_ano_mes"].isin(df_v["numero_ano_mes"].unique())]

    por_estado_mes   = resumo(df_mes,    merged_mes,    "descricao_estado")
    por_gerencia_mes = resumo(df_mes,    merged_mes,    "descricao_gerencia_2")
    por_estado_acum  = resumo(df_todos,  merged_todos,  "descricao_estado")

    return {
        "por_estado_mes_atual": por_estado_mes,
        "por_gerencia_mes_atual": por_gerencia_mes,
        "por_estado_acumulado": por_estado_acum,
        "top5_piores_estados": por_estado_mes[:5],
        "top5_melhores_estados": por_estado_mes[-5:][::-1],
    }

# ─── Secao 7: Comportamento de clientes ──────────────────────────────────────

def secao_clientes(df_v, mes_atual, status_clientes, clientes_mes_anterior):
    df_mes  = df_v[df_v["numero_ano_mes"] == mes_atual]
    total   = df_mes[COL_VENDA].sum()
    meses   = sorted(df_v["numero_ano_mes"].unique())

    # Mapa de segmento dominante por cliente
    seg_map = (
        df_mes.groupby("descricao_parceiro_master")["descricao_segmento_mercado"]
        .agg(lambda x: x.value_counts().index[0] if len(x) > 0 else "N/A")
        .to_dict()
    )

    # Media historica por cliente (todos os meses anteriores ao atual)
    df_hist = df_v[df_v["numero_ano_mes"] < mes_atual]
    n_meses_hist = df_hist["numero_ano_mes"].nunique()
    media_hist = (
        df_hist.groupby("descricao_parceiro_master")[COL_VENDA]
        .sum()
        .div(n_meses_hist if n_meses_hist > 0 else 1)
        .reset_index()
    )
    media_hist.columns = ["descricao_parceiro_master", "media_mensal_ton"]

    # Top 10 clientes do mes com dados comparativos
    vol_cli = (
        df_mes.groupby("descricao_parceiro_master")[COL_VENDA]
        .sum().reset_index().sort_values(COL_VENDA, ascending=False)
    )
    top10_raw = vol_cli.head(10)
    top10 = []
    for _, row in top10_raw.iterrows():
        c = row["descricao_parceiro_master"]
        v_atual = row[COL_VENDA]
        media_row = media_hist[media_hist["descricao_parceiro_master"] == c]["media_mensal_ton"]
        media_v   = float(media_row.values[0]) if len(media_row) > 0 else None
        # volume mes anterior
        df_ant_c = df_v[(df_v["numero_ano_mes"].isin([m for m in meses if m < mes_atual][-1:])) &
                        (df_v["descricao_parceiro_master"] == c)]
        v_ant = df_ant_c[COL_VENDA].sum() if len(df_ant_c) > 0 else 0
        top10.append({
            "cliente": str(c),
            "segmento": seg_map.get(c, "N/A"),
            "status": status_clientes.get(c, "N/A"),
            "volume_ton": r1(v_atual),
            "share_pct": r1(v_atual / total * 100) if total > 0 else None,
            "vs_mes_anterior_ton": r1(v_atual - v_ant),
            "vs_mes_anterior_pct": pct(v_atual, v_ant) if v_ant > 0 else None,
            "vs_media_historica_ton": r1(v_atual - media_v) if media_v is not None else None,
            "vs_media_historica_pct": pct(v_atual, media_v) if media_v and media_v > 0 else None,
        })

    # Clientes novos — top 15
    novos = [c for c, s in status_clientes.items() if s == "Novo"]
    novos_df = vol_cli[vol_cli["descricao_parceiro_master"].isin(novos)].head(15)
    top_novos = []
    for _, row in novos_df.iterrows():
        c = row["descricao_parceiro_master"]
        top_novos.append({
            "cliente": str(c),
            "segmento": seg_map.get(c, "N/A"),
            "volume_ton": r1(row[COL_VENDA]),
            "share_pct": r1(row[COL_VENDA] / total * 100) if total > 0 else None,
        })

    vol_novos    = df_mes[df_mes["descricao_parceiro_master"].isin(novos)][COL_VENDA].sum()
    vol_reat     = df_mes[df_mes["descricao_parceiro_master"].isin(
        [c for c, s in status_clientes.items() if s == "Reativado"])][COL_VENDA].sum()
    vol_recorr   = df_mes[df_mes["descricao_parceiro_master"].isin(
        [c for c, s in status_clientes.items() if s == "Recorrente"])][COL_VENDA].sum()

    # Crescimento de recorrentes vs media historica
    recorrentes = [c for c, s in status_clientes.items() if s == "Recorrente"]
    recorr_vol  = vol_cli[vol_cli["descricao_parceiro_master"].isin(recorrentes)].copy()
    recorr_vol  = recorr_vol.merge(media_hist, on="descricao_parceiro_master", how="left")
    recorr_vol["incremento_ton"] = recorr_vol[COL_VENDA] - recorr_vol["media_mensal_ton"].fillna(0)
    recorr_vol["cresc_pct"] = recorr_vol.apply(
        lambda r: pct(r[COL_VENDA], r["media_mensal_ton"]) if r["media_mensal_ton"] and r["media_mensal_ton"] > 0 else None,
        axis=1
    )
    crescimento_recorr = (
        recorr_vol[recorr_vol["incremento_ton"] > 0]
        .sort_values("incremento_ton", ascending=False)
        .head(15)
    )
    top_crescimento = []
    for _, row in crescimento_recorr.iterrows():
        c = row["descricao_parceiro_master"]
        top_crescimento.append({
            "cliente": str(c),
            "volume_atual_ton": r1(row[COL_VENDA]),
            "media_historica_ton": r1(row["media_mensal_ton"]),
            "incremento_ton": r1(row["incremento_ton"]),
            "crescimento_pct": r1(row["cresc_pct"]) if row["cresc_pct"] is not None else None,
        })

    # Clientes em risco (compraram no mes anterior, zeraram agora)
    em_risco = []
    mes_ant_meses = [m for m in meses if m < mes_atual]
    if mes_ant_meses:
        mes_ant = mes_ant_meses[-1]
        compraram_antes = set(df_v[df_v["numero_ano_mes"] == mes_ant]["descricao_parceiro_master"].dropna())
        clientes_atuais = set(df_mes["descricao_parceiro_master"].dropna())
        churn_candidatos = compraram_antes - clientes_atuais
        for c in list(churn_candidatos):
            v_ant = df_v[(df_v["numero_ano_mes"] == mes_ant) &
                         (df_v["descricao_parceiro_master"] == c)][COL_VENDA].sum()
            em_risco.append({
                "cliente": str(c),
                "volume_mes_anterior_ton": r1(v_ant),
                "segmento": str(df_v[df_v["descricao_parceiro_master"] == c]["descricao_segmento_mercado"].mode().values[0])
                             if len(df_v[df_v["descricao_parceiro_master"] == c]) > 0 else "N/A",
            })
        em_risco.sort(key=lambda x: x["volume_mes_anterior_ton"] or 0, reverse=True)

    return {
        "top10_clientes": top10,
        "resumo_status": {
            "novos_qtd": len(novos),
            "novos_vol_ton": r1(vol_novos),
            "novos_share_pct": r1(vol_novos / total * 100) if total > 0 else None,
            "reativados_qtd": len([c for c, s in status_clientes.items() if s == "Reativado"]),
            "reativados_vol_ton": r1(vol_reat),
            "recorrentes_qtd": len(recorrentes),
            "recorrentes_vol_ton": r1(vol_recorr),
            "recorrentes_share_pct": r1(vol_recorr / total * 100) if total > 0 else None,
        },
        "top15_novos": top_novos,
        "top15_crescimento_recorrentes": top_crescimento,
        "clientes_em_risco_churn": em_risco[:20],
    }

# ─── Secao 8: Projecao ───────────────────────────────────────────────────────

def secao_projecao(df_v, merged, mes_atual):
    df_mes   = df_v[df_v["numero_ano_mes"] == mes_atual]
    real_mes = df_mes[COL_VENDA].sum()
    prev_mes = merged[merged["numero_ano_mes"] == mes_atual][COL_PREV].sum()

    df_hist  = df_v[df_v["numero_ano_mes"] < mes_atual]
    n_meses  = df_hist["numero_ano_mes"].nunique()
    media_h  = df_hist.groupby("numero_ano_mes")[COL_VENDA].sum().mean() if n_meses > 0 else None

    return {
        "mes_atual": fmt_mes(mes_atual),
        "realizado_ton": r1(real_mes),
        "previsto_ton":  r1(prev_mes),
        "gap_ton":       r1(prev_mes - real_mes),
        "atingimento_pct": ating(real_mes, prev_mes),
        "media_historica_mensal_ton": r1(media_h),
        "nota": "Para projecao intraday, fornecer data de corte dos dados de vendas.",
    }

# ─── Secao 9: Anomalias ──────────────────────────────────────────────────────

def secao_anomalias(df_v, df_p, merged):
    alertas = []
    meses_v = set(df_v["numero_ano_mes"].unique())

    # Vendas sem previsao correspondente
    vagg = df_v.groupby(CHAVE_JOIN)[COL_VENDA].sum().reset_index()
    sem_prev = pd.merge(vagg, df_p[CHAVE_JOIN + [COL_PREV]], on=CHAVE_JOIN, how="left")
    sem_prev = sem_prev[sem_prev[COL_PREV].isna()]
    if len(sem_prev) > 0:
        alertas.append({
            "tipo": "vendas_sem_previsao",
            "descricao": f"{len(sem_prev)} combinacoes de vendas sem previsao correspondente",
            "volume_ton": r1(sem_prev[COL_VENDA].sum()),
        })

    # Previsoes sem nenhuma venda (nos meses ja realizados)
    pagg = df_p.groupby(CHAVE_JOIN)[COL_PREV].sum().reset_index()
    sem_venda = pd.merge(pagg, df_v.groupby(CHAVE_JOIN)[COL_VENDA].sum().reset_index(),
                         on=CHAVE_JOIN, how="left")
    sem_venda = sem_venda[sem_venda["numero_ano_mes"].isin(meses_v)]
    sem_venda = sem_venda[sem_venda[COL_VENDA].isna() | (sem_venda[COL_VENDA] == 0)]
    if len(sem_venda) > 0:
        alertas.append({
            "tipo": "previsao_sem_realizacao",
            "descricao": f"{len(sem_venda)} combinacoes previstas sem venda realizada",
            "volume_ton": r1(sem_venda[COL_PREV].sum()),
        })

    # Outliers de desvio entre combinacoes com historico
    out = merged[
        (merged[COL_PREV] > 1) & (merged[COL_VENDA] > 0) &
        ((merged["desvio_pct"] > 100) | (merged["desvio_pct"] < -50))
    ].copy()
    if len(out) > 0:
        out["desvio_abs_ton"] = (out[COL_VENDA] - out[COL_PREV]).round(1)
        alertas.append({
            "tipo": "outliers_desvio_extremo",
            "descricao": f"{len(out)} combinacoes com desvio extremo (>+100% ou <-50%)",
            "exemplos": out.sort_values("desvio_abs_ton").head(5)[
                CHAVE_JOIN + [COL_VENDA, COL_PREV, "desvio_pct"]
            ].to_dict(orient="records"),
        })

    return {"alertas": alertas, "total_alertas": len(alertas)}

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vendas",   required=True)
    parser.add_argument("--previsao", required=True)
    parser.add_argument("--output",   required=True)
    parser.add_argument("--mes",      type=int, default=None)
    args = parser.parse_args()

    df_v = load_file(args.vendas,   "Vendas")
    df_p = load_file(args.previsao, "Previsao")

    # Validar colunas minimas
    for col in CHAVE_JOIN + [COL_VENDA]:
        if col not in df_v.columns:
            sys.stderr.write(f"[ERRO] Coluna ausente em vendas: '{col}'\n"); sys.exit(1)
    for col in CHAVE_JOIN + [COL_PREV]:
        if col not in df_p.columns:
            sys.stderr.write(f"[ERRO] Coluna ausente em previsao: '{col}'\nColunas: {list(df_p.columns)}\n"); sys.exit(1)

    mes_atual = args.mes if args.mes else int(df_v["numero_ano_mes"].max())
    log(f"[INFO] Mes de analise: {fmt_mes(mes_atual)} ({mes_atual})")

    merged = build_macro_join(df_v, df_p)
    log(f"[INFO] Join macro: {len(merged):,} combinacoes")

    status_clientes, clientes_mes_ant = classificar_clientes(df_v, mes_atual)
    log(f"[INFO] Clientes classificados: {len(status_clientes):,}")

    log("[INFO] Calculando secoes...")
    resultado = {
        "meta": {
            "mes_analise": fmt_mes(mes_atual),
            "yyyymm_analise": mes_atual,
            "total_linhas_vendas": len(df_v),
            "total_linhas_previsao": len(df_p),
            "meses_vendas": [fmt_mes(m) for m in sorted(df_v["numero_ano_mes"].unique())],
            "meses_previsao": [fmt_mes(m) for m in sorted(df_p["numero_ano_mes"].unique())],
        },
        "sec1_indicadores_chave":  secao_indicadores(df_v, merged, mes_atual, status_clientes),
        "sec2_diagnostico":        secao_diagnostico(df_v, merged),
        "sec3_concentracao":       secao_concentracao(df_v, mes_atual, status_clientes),
        "sec4_mix_produto":        secao_mix_produto(df_v, mes_atual),
        "sec5_segmentos":          secao_segmentos(df_v, mes_atual),
        "sec6_geografico":         secao_geografico(df_v, merged, mes_atual),
        "sec7_clientes":           secao_clientes(df_v, mes_atual, status_clientes, clientes_mes_ant),
        "sec8_projecao":           secao_projecao(df_v, merged, mes_atual),
        "sec9_anomalias":          secao_anomalias(df_v, df_p, merged),
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2, default=str)

    n_al = resultado["sec9_anomalias"]["total_alertas"]
    log(f"[OK] Resultado salvo em: {out}")
    log(f"[OK] Concluido. Alertas: {n_al}")

if __name__ == "__main__":
    main()
