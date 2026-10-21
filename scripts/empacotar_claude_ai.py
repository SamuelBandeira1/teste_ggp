"""Gera os .zip para subir as skills no claude.ai (web e desktop) da conta de trabalho.

Saída em dist/claude-ai/:
  skills/<plugin>/<skill>.zip  -> upload individual: Personalizar > Skills > "+" > Fazer upload de skill
  plugins/<plugin>.zip         -> para o admin da organização distribuir o plugin inteiro

Uso:  python scripts/empacotar_claude_ai.py [--com-pessoal]
"""
import argparse
import pathlib
import shutil
import zipfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
IGNORAR = {"__pycache__", ".DS_Store"}


def zipar(origem, destino, prefixo):
    destino.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for arq in sorted(origem.rglob("*")):
            if arq.is_file() and not (IGNORAR & set(arq.parts)):
                z.write(arq, pathlib.Path(prefixo) / arq.relative_to(origem))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--com-pessoal", action="store_true", help="inclui o plugin pessoal")
    a = ap.parse_args()

    saida = RAIZ / "dist" / "claude-ai"
    shutil.rmtree(saida, ignore_errors=True)
    total = 0
    for plugin in sorted((RAIZ / "plugins").iterdir()):
        if not plugin.is_dir() or (plugin.name == "pessoal" and not a.com_pessoal):
            continue
        for skill in sorted((plugin / "skills").iterdir()):
            if (skill / "SKILL.md").exists():
                zipar(skill, saida / "skills" / plugin.name / f"{skill.name}.zip", skill.name)
                total += 1
        zipar(plugin, saida / "plugins" / f"{plugin.name}.zip", plugin.name)
    print(f"{total} skills empacotadas em {saida}")
    for z in sorted(saida.rglob("*.zip")):
        print(f"  {z.relative_to(RAIZ)}  ({z.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
