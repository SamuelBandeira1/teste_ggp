#!/usr/bin/env bash
# Instala o samuel-stack no Claude Code desta máquina (Linux, macOS, WSL, Git Bash).
#
# Uso:
#   ./scripts/instalar.sh                 # instala a partir desta pasta (clone local)
#   ./scripts/instalar.sh --repo dono/repo   # instala a partir do GitHub (repo privado precisa de git autenticado)
#   ./scripts/instalar.sh --com-pessoal   # inclui o plugin "pessoal" (NFC 3D, Shaping)
#   ./scripts/instalar.sh --sem-extras    # não instala os plugins de terceiros (Anthropic, Superpowers, Karpathy)
#   ./scripts/instalar.sh --sem-rea       # não instala o REA (engenharia reversa)
#   ./scripts/instalar.sh --com-design    # + UI UX Pro Max (landing page, dashboard web)
#   ./scripts/instalar.sh --com-pesquisa  # + last30days (pesquisa em Reddit, X, YouTube dos últimos 30 dias)
#
# Pode rodar de novo quando quiser: o que já está instalado é mantido.
set -u

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
ORIGEM="$RAIZ"
COM_PESSOAL=0
EXTRAS=1
REA=1
DESIGN=0
PESQUISA=0
while [ $# -gt 0 ]; do
  case "$1" in
    --repo) ORIGEM="$2"; shift 2 ;;
    --com-pessoal) COM_PESSOAL=1; shift ;;
    --sem-extras) EXTRAS=0; shift ;;
    --sem-rea) REA=0; shift ;;
    --com-design) DESIGN=1; shift ;;
    --com-pesquisa) PESQUISA=1; shift ;;
    *) echo "Opção desconhecida: $1"; exit 2 ;;
  esac
done

if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code não encontrado. Instale antes: https://code.claude.com/docs/en/setup"
  exit 1
fi

FALHAS=()
passo() { echo; echo "==> $*"; }
tenta() { "$@" || FALHAS+=("$*"); }

passo "Marketplace samuel-stack ($ORIGEM)"
tenta claude plugin marketplace add "$ORIGEM"
for p in metodo-samuel sop-comercial office-bi; do
  tenta claude plugin install "$p@samuel-stack"
done
[ "$COM_PESSOAL" = 1 ] && tenta claude plugin install "pessoal@samuel-stack"

if [ "$EXTRAS" = 1 ]; then
  passo "Skills de documento da Anthropic (xlsx, pptx, docx, pdf)"
  tenta claude plugin marketplace add anthropics/skills
  tenta claude plugin install "document-skills@anthropic-agent-skills"

  passo "Plugins de trabalho da Anthropic (dados, finanças, operações, produtividade)"
  tenta claude plugin marketplace add anthropics/knowledge-work-plugins
  for p in data finance operations productivity; do
    tenta claude plugin install "$p@knowledge-work-plugins"
  done

  passo "Método para tarefas de código: Superpowers e regras do Karpathy"
  tenta claude plugin marketplace add anthropics/claude-plugins-official
  tenta claude plugin install "superpowers@claude-plugins-official"
  tenta claude plugin marketplace add forrestchang/andrej-karpathy-skills
  tenta claude plugin install "andrej-karpathy-skills@karpathy-skills"
fi

if [ "$DESIGN" = 1 ]; then
  passo "UI UX Pro Max (design de páginas e dashboards web)"
  tenta claude plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
  tenta claude plugin install "ui-ux-pro-max@ui-ux-pro-max-skill"
fi

if [ "$PESQUISA" = 1 ]; then
  passo "last30days (pesquisa dos últimos 30 dias em Reddit, X, YouTube, HN)"
  tenta claude plugin marketplace add mvanhorn/last30days-skill
  tenta claude plugin install "last30days@last30days-skill"
fi

if [ "$REA" = 1 ]; then
  passo "REA — Reverse Engineer Anything (morluto/rea)"
  if command -v node >/dev/null 2>&1 && node -e 'const [a,b]=process.versions.node.split(".").map(Number);process.exit((a===22&&b>=19)||(a===24&&b>=11)||a>=26?0:1)'; then
    # Registra o MCP no ~/.claude.json (com backup) e instala a skill reverse-engineer-anything.
    # Ghidra/IDA/Hopper só são necessários para executável nativo; site e app JavaScript funcionam sem.
    tenta npx -y rea-agents@latest setup --client claude_code --yes
  else
    FALHAS+=("REA precisa de Node.js 22.19+, 24.11+ ou 26+ (https://nodejs.org). Depois: npx -y rea-agents@latest setup --client claude_code")
  fi
fi

passo "Instruções globais (~/.claude/CLAUDE.md)"
mkdir -p "$HOME/.claude"
GLOBAL="$HOME/.claude/CLAUDE.md"
IMPORT="@$RAIZ/config/CLAUDE.md"
if [ -f "$GLOBAL" ] && grep -qF "$IMPORT" "$GLOBAL"; then
  echo "Já importado em $GLOBAL"
else
  [ -f "$GLOBAL" ] && cp "$GLOBAL" "$GLOBAL.bak.$(date +%Y%m%d%H%M%S)" && echo "Backup do CLAUDE.md anterior criado."
  printf '\n# samuel-stack (atualiza com git pull na pasta do repositório)\n%s\n' "$IMPORT" >> "$GLOBAL"
  echo "Linha de importação adicionada em $GLOBAL"
fi

passo "Bibliotecas Python usadas pelos scripts"
if command -v python3 >/dev/null 2>&1; then
  python3 -m pip install --user --quiet pandas numpy openpyxl xlsxwriter python-pptx python-docx \
    || FALHAS+=("pip install (rode manualmente: python3 -m pip install pandas numpy openpyxl xlsxwriter python-pptx python-docx)")
else
  FALHAS+=("python3 não encontrado: instale Python 3.10+ para os scripts de auditoria, radar e desvios")
fi
command -v soffice >/dev/null 2>&1 || echo "Aviso: LibreOffice (soffice) não encontrado. Ele recalcula fórmulas e renderiza slides para conferência."

passo "Resultado"
claude plugin list 2>/dev/null | grep -E "^\s*>|Status" || true
if [ ${#FALHAS[@]} -gt 0 ]; then
  echo; echo "Passos que falharam (rode de novo ou faça manualmente):"
  printf ' - %s\n' "${FALHAS[@]}"
  exit 1
fi
echo; echo "Pronto. Abra o Claude Code e rode /plugin para conferir. Para medir consumo: /usage (ou npx ccusage@latest)."
