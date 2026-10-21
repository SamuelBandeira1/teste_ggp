"""Resume um modelo semântico Power BI em formato TMDL num Markdown curto.

Lê a pasta <Nome>.SemanticModel (ou a subpasta definition/) e lista tabelas,
colunas, medidas (expressão, pasta, formato, descrição) e relacionamentos.
Serve para o Claude entender o modelo sem ler todos os .tmdl.

Uso:
  python resumir_tmdl.py <pasta .SemanticModel> [--sem-expressao]
"""
import argparse
import pathlib
import re
import sys

OBJ = re.compile(r"^(\t*)(table|column|measure|relationship|calculationGroup|calculationItem)\s+(.+?)\s*(=\s*(.*))?$")
PROP = re.compile(r"^(\t*)(\w+)\s*(?::\s*(.*))?$")  # "isHidden" sozinho = true


def nome_limpo(n):
    n = n.strip()
    return n[1:-1].replace("''", "'") if n.startswith("'") and n.endswith("'") else n


def nivel(linha):
    return len(linha) - len(linha.lstrip("\t"))


def ler_arquivo(caminho, modelo):
    linhas = caminho.read_text(encoding="utf-8-sig").splitlines()
    tabela = None
    atual = None  # dict do objeto corrente (coluna/medida/relacionamento)
    descricao = []
    i = 0
    while i < len(linhas):
        ln = linhas[i]
        if ln.strip().startswith("///"):
            descricao.append(ln.strip()[3:].strip())
            i += 1
            continue
        m = OBJ.match(ln)
        if m:
            ind, tipo, nome, _, expr = m.groups()
            obj = {"tipo": tipo, "nome": nome_limpo(nome), "descricao": " ".join(descricao), "props": {}}
            descricao = []
            if tipo == "table":
                tabela = {"nome": obj["nome"], "colunas": [], "medidas": [], "descricao": obj["descricao"]}
                modelo["tabelas"].append(tabela)
                atual = None
            elif tipo == "relationship":
                atual = obj
                modelo["relacionamentos"].append(obj)
            else:
                partes = [expr.strip()] if expr and expr.strip() else []
                # expressão em várias linhas: linhas mais indentadas que as propriedades
                j = i + 1
                while j < len(linhas) and (not linhas[j].strip() or nivel(linhas[j]) > len(ind) + 1):
                    if linhas[j].strip():
                        partes.append(linhas[j].strip())
                    j += 1
                if partes and partes[0] == "```":
                    partes = [p for p in partes if p != "```"]
                obj["expressao"] = " ".join(partes)
                i = j - 1
                atual = obj
                if tabela is not None:
                    tabela["medidas" if tipo == "measure" else "colunas"].append(obj)
            i += 1
            continue
        p = PROP.match(ln)
        if p and atual is not None and nivel(ln) >= 1:
            atual["props"][p.group(2)] = (p.group(3) or "true").strip()
        i += 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pasta")
    ap.add_argument("--sem-expressao", action="store_true", help="não imprime a expressão DAX das medidas")
    a = ap.parse_args()

    raiz = pathlib.Path(a.pasta).resolve()
    arquivos = sorted(raiz.rglob("*.tmdl"))
    if not arquivos:
        sys.exit(f"Nenhum .tmdl encontrado em {raiz}. O projeto está salvo como PBIP com formato TMDL?")
    modelo = {"tabelas": [], "relacionamentos": []}
    for arq in arquivos:
        ler_arquivo(arq, modelo)

    tabelas = [t for t in modelo["tabelas"] if not t["nome"].startswith(("LocalDateTable_", "DateTableTemplate_"))]
    n_med = sum(len(t["medidas"]) for t in tabelas)
    print(f"# Resumo do modelo — {raiz.name}\n")
    print(f"{len(tabelas)} tabelas, {n_med} medidas, {len(modelo['relacionamentos'])} relacionamentos\n")

    print("## Tabelas e colunas\n")
    for t in tabelas:
        cols = [f"{c['nome']} ({c['props'].get('dataType', '?')})" for c in t["colunas"] if c["props"].get("isHidden") != "true"]
        ocultas = sum(1 for c in t["colunas"] if c["props"].get("isHidden") == "true")
        extra = f" + {ocultas} ocultas" if ocultas else ""
        print(f"- **{t['nome']}**: {', '.join(cols) or '—'}{extra}")

    print("\n## Medidas\n")
    for t in tabelas:
        for m in t["medidas"]:
            pasta = m["props"].get("displayFolder", "")
            fmt = m["props"].get("formatString", "")
            meta = " | ".join(x for x in [f"pasta: {pasta}" if pasta else "", f"formato: {fmt}" if fmt else ""] if x)
            print(f"- **[{m['nome']}]** ({t['nome']}){' — ' + meta if meta else ''}")
            if m["descricao"]:
                print(f"  - descrição: {m['descricao']}")
            else:
                print("  - descrição: (sem descrição)")
            if not a.sem_expressao and m.get("expressao"):
                print(f"  - `{m['expressao']}`")

    print("\n## Relacionamentos\n")
    for r in modelo["relacionamentos"]:
        p = r["props"]
        direcao = p.get("crossFilteringBehavior", "oneDirection")
        ativo = "" if p.get("isActive", "true") == "true" else " (inativo)"
        print(f"- {p.get('fromColumn', '?')} → {p.get('toColumn', '?')} [{direcao}]{ativo}")

    sem_desc = [m["nome"] for t in tabelas for m in t["medidas"] if not m["descricao"]]
    bidir = [r for r in modelo["relacionamentos"] if r["props"].get("crossFilteringBehavior") == "bothDirections"]
    print("\n## Pontos de atenção\n")
    print(f"- Medidas sem descrição: {len(sem_desc)} de {n_med}")
    print(f"- Relacionamentos bidirecionais: {len(bidir)}")


if __name__ == "__main__":
    main()
