#!/usr/bin/env python3
"""Pontua restaurantes coletados pelo gosom/google-maps-scraper para a venda das plaquinhas NFC.

Uso: python3 prospeccao/pontuar_leads.py dados/maps_bruto.csv [dados/leads_pontuados.csv]

Lógica: o melhor lead tem nota boa e poucas avaliações (comida boa, pouca gente sabendo),
celular para WhatsApp e não é rede. Se o arquivo de saída já existir, status e anotações
dos leads antigos são preservados.
"""
import csv
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

REDES = [
    "mcdonald", "burger king", "subway", "bob's", "bobs", "habib", "outback", "coco bambu",
    "giraffas", "china in box", "spoleto", "pizza hut", "domino", "kfc", "madero", "jeronimo",
    "cacau show", "starbucks", "applebee", "abbraccio", "camaroes", "girafas", "popeyes",
    "ragazzo", "divino fogao", "griletto", "parmeggio", "the best acai", "oakberry", "chiquinho",
]

CAMPOS_PRESERVADOS = ["status", "gancho", "mensagem", "data_contato", "observacoes"]

SAIDA_COLUNAS = [
    "pontuacao", "motivo", "status", "nome", "categoria", "endereco", "nota", "avaliacoes",
    "telefone", "whatsapp", "site", "instagram", "cardapio", "link_maps", "link_avaliacao",
    "place_id", "gancho", "mensagem", "data_contato", "observacoes",
]


def sem_acento(texto):
    texto = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in texto if not unicodedata.combining(c)).lower().strip()


def numero(valor, tipo=float):
    try:
        return tipo(str(valor).replace(",", ".").strip())
    except (TypeError, ValueError):
        return tipo(0)


def whatsapp_de(telefone):
    """Devolve 55+DDD+número se for celular brasileiro, senão vazio."""
    d = re.sub(r"\D", "", telefone or "")
    if d.startswith("55") and len(d) in (12, 13):
        d = d[2:]
    if d.startswith("0"):
        d = d[1:]
    if len(d) == 11 and d[2] == "9":
        return "55" + d
    return ""


def links_em(valor):
    """Extrai links de campos JSON do scraper (menu, order_online)."""
    if not valor or valor in ("null", "{}", "[]"):
        return []
    try:
        dado = json.loads(valor)
    except json.JSONDecodeError:
        return [valor] if valor.startswith("http") else []
    itens = dado if isinstance(dado, list) else [dado]
    return [i.get("link") for i in itens if isinstance(i, dict) and i.get("link")]


def fechado(status):
    s = sem_acento(status)
    return any(p in s for p in ("closed", "fechado", "perman", "temporar"))


def pontuar(linha, contagem_nomes):
    nota = numero(linha.get("review_rating"))
    avaliacoes = numero(linha.get("review_count"), int)
    whatsapp = whatsapp_de(linha.get("phone"))
    site = linha.get("website", "")
    nome_norm = sem_acento(linha.get("title"))
    cardapio = links_em(linha.get("menu")) + links_em(linha.get("order_online"))

    pontos, motivos = 0, []
    if nota >= 4.3 and 20 <= avaliacoes <= 200:
        pontos += 3
        motivos.append(f"nota {nota} com só {avaliacoes} avaliações")
    elif nota >= 4.3 and avaliacoes > 200:
        pontos += 1
        motivos.append("nota boa, já bem avaliado")
    elif 4.0 <= nota < 4.3:
        pontos += 1
        motivos.append(f"nota {nota}")
    elif 0 < nota < 4.0:
        pontos -= 2
        motivos.append(f"nota baixa ({nota})")
    if 5 <= avaliacoes < 20:
        pontos += 1
        motivos.append("casa nova, poucas avaliações")
    if whatsapp:
        pontos += 2
        motivos.append("celular para WhatsApp")
    elif not linha.get("phone"):
        pontos -= 3
        motivos.append("sem telefone (só visita)")
    else:
        motivos.append("telefone fixo (ligar ou visitar)")
    if "instagram.com" in site.lower():
        pontos += 1
        motivos.append("tem Instagram")
    if cardapio:
        pontos += 1
        motivos.append("cardápio ou pedido online")
    if any(r in nome_norm for r in REDES) or contagem_nomes[nome_norm] >= 3:
        pontos -= 5
        motivos.append("parece rede ou franquia")

    place_id = linha.get("place_id", "")
    return {
        "pontuacao": pontos,
        "motivo": "; ".join(motivos),
        "status": "novo",
        "nome": linha.get("title", ""),
        "categoria": linha.get("category", ""),
        "endereco": linha.get("address", ""),
        "nota": nota or "",
        "avaliacoes": avaliacoes,
        "telefone": linha.get("phone", ""),
        "whatsapp": whatsapp,
        "site": site,
        "instagram": site if "instagram.com" in site.lower() else "",
        "cardapio": cardapio[0] if cardapio else "",
        "link_maps": linha.get("link", ""),
        "link_avaliacao": f"https://search.google.com/local/writereview?placeid={place_id}" if place_id else "",
        "place_id": place_id,
        "gancho": "", "mensagem": "", "data_contato": "", "observacoes": "",
    }


def chave(lead):
    return lead.get("place_id") or sem_acento(lead.get("nome", "") + lead.get("endereco", ""))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    entrada = Path(sys.argv[1])
    saida = Path(sys.argv[2]) if len(sys.argv) > 2 else entrada.with_name("leads_pontuados.csv")

    csv.field_size_limit(10**8)
    with entrada.open(newline="", encoding="utf-8") as f:
        brutos = list(csv.DictReader(f))

    contagem_nomes = Counter(sem_acento(l.get("title")) for l in brutos)
    leads, vistos, fechados = {}, set(), 0
    for linha in brutos:
        if fechado(linha.get("status")):
            fechados += 1
            continue
        lead = pontuar(linha, contagem_nomes)
        k = chave(lead)
        if k in vistos:
            continue
        vistos.add(k)
        leads[k] = lead

    if saida.exists():
        with saida.open(newline="", encoding="utf-8") as f:
            for antigo in csv.DictReader(f):
                k = chave(antigo)
                if k in leads:
                    for campo in CAMPOS_PRESERVADOS:
                        if antigo.get(campo):
                            leads[k][campo] = antigo[campo]
                else:
                    leads[k] = {c: antigo.get(c, "") for c in SAIDA_COLUNAS}

    ordenados = sorted(leads.values(), key=lambda l: numero(l["pontuacao"]), reverse=True)
    saida.parent.mkdir(parents=True, exist_ok=True)
    with saida.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SAIDA_COLUNAS)
        w.writeheader()
        w.writerows(ordenados)

    bons = [l for l in ordenados if numero(l["pontuacao"]) >= 4 and l["status"] == "novo"]
    print(f"Lidos: {len(brutos)} | fechados: {fechados} | únicos: {len(ordenados)} | "
          f"pontuação ≥ 4 ainda novos: {len(bons)}")
    print(f"Salvo em {saida}\n")
    for l in ordenados[:10]:
        print(f"{l['pontuacao']:>3}  {l['nome'][:40]:<40}  {l['motivo']}")


if __name__ == "__main__":
    main()
