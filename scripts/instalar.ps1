# Instala o samuel-stack no Claude Code desta máquina (Windows / PowerShell).
#
# Uso (na pasta do repositório clonado):
#   powershell -ExecutionPolicy Bypass -File .\scripts\instalar.ps1
#   powershell -ExecutionPolicy Bypass -File .\scripts\instalar.ps1 -Repo dono/repo
#   powershell -ExecutionPolicy Bypass -File .\scripts\instalar.ps1 -ComPessoal
#   powershell -ExecutionPolicy Bypass -File .\scripts\instalar.ps1 -SemExtras    # sem plugins de terceiros
#   powershell -ExecutionPolicy Bypass -File .\scripts\instalar.ps1 -SemRea       # sem o REA
#   powershell -ExecutionPolicy Bypass -File .\scripts\instalar.ps1 -ComDesign    # + UI UX Pro Max
#   powershell -ExecutionPolicy Bypass -File .\scripts\instalar.ps1 -ComPesquisa  # + last30days
#
# Pode rodar de novo quando quiser: o que já está instalado é mantido.
param(
  [string]$Repo = "",
  [switch]$ComPessoal,
  [switch]$SemExtras,
  [switch]$SemRea,
  [switch]$ComDesign,
  [switch]$ComPesquisa
)

$Raiz = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Origem = if ($Repo) { $Repo } else { $Raiz }
$Falhas = New-Object System.Collections.Generic.List[string]

function Passo($t) { Write-Host ""; Write-Host "==> $t" -ForegroundColor Cyan }
function Tenta([string[]]$cmdArgs) {
  & claude @cmdArgs
  if ($LASTEXITCODE -ne 0) { $Falhas.Add("claude " + ($cmdArgs -join " ")) }
}

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
  Write-Host "Claude Code não encontrado. Instale antes: https://code.claude.com/docs/en/setup" -ForegroundColor Red
  exit 1
}

Passo "Marketplace samuel-stack ($Origem)"
Tenta @("plugin", "marketplace", "add", $Origem)
foreach ($p in @("metodo-samuel", "sop-comercial", "office-bi")) { Tenta @("plugin", "install", "$p@samuel-stack") }
if ($ComPessoal) { Tenta @("plugin", "install", "pessoal@samuel-stack") }

if (-not $SemExtras) {
  Passo "Skills de documento da Anthropic (xlsx, pptx, docx, pdf)"
  Tenta @("plugin", "marketplace", "add", "anthropics/skills")
  Tenta @("plugin", "install", "document-skills@anthropic-agent-skills")

  Passo "Plugins de trabalho da Anthropic (dados, finanças, operações, produtividade)"
  Tenta @("plugin", "marketplace", "add", "anthropics/knowledge-work-plugins")
  foreach ($p in @("data", "finance", "operations", "productivity")) { Tenta @("plugin", "install", "$p@knowledge-work-plugins") }

  Passo "Método para tarefas de código: Superpowers e regras do Karpathy"
  Tenta @("plugin", "marketplace", "add", "anthropics/claude-plugins-official")
  Tenta @("plugin", "install", "superpowers@claude-plugins-official")
  Tenta @("plugin", "marketplace", "add", "forrestchang/andrej-karpathy-skills")
  Tenta @("plugin", "install", "andrej-karpathy-skills@karpathy-skills")
}

if ($ComDesign) {
  Passo "UI UX Pro Max (design de páginas e dashboards web)"
  Tenta @("plugin", "marketplace", "add", "nextlevelbuilder/ui-ux-pro-max-skill")
  Tenta @("plugin", "install", "ui-ux-pro-max@ui-ux-pro-max-skill")
}

if ($ComPesquisa) {
  Passo "last30days (pesquisa dos últimos 30 dias em Reddit, X, YouTube, HN)"
  Tenta @("plugin", "marketplace", "add", "mvanhorn/last30days-skill")
  Tenta @("plugin", "install", "last30days@last30days-skill")
}

if (-not $SemRea) {
  Passo "REA — Reverse Engineer Anything (morluto/rea)"
  $nodeOk = $false
  if (Get-Command node -ErrorAction SilentlyContinue) {
    $v = (& node -p "process.versions.node").Split(".") | ForEach-Object { [int]$_ }
    $nodeOk = ($v[0] -eq 22 -and $v[1] -ge 19) -or ($v[0] -eq 24 -and $v[1] -ge 11) -or ($v[0] -ge 26)
  }
  if ($nodeOk) {
    # Registra o MCP no ~/.claude.json (com backup) e instala a skill reverse-engineer-anything.
    & npx -y rea-agents@latest setup --client claude_code --yes
    if ($LASTEXITCODE -ne 0) { $Falhas.Add("npx -y rea-agents@latest setup --client claude_code") }
  } else {
    $Falhas.Add("REA precisa de Node.js 22.19+, 24.11+ ou 26+ (https://nodejs.org). Depois: npx -y rea-agents@latest setup --client claude_code")
  }
}

Passo "Instruções globais (~/.claude/CLAUDE.md)"
$DirClaude = Join-Path $HOME ".claude"
New-Item -ItemType Directory -Force -Path $DirClaude | Out-Null
$Global = Join-Path $DirClaude "CLAUDE.md"
$Import = "@" + ((Join-Path $Raiz "config\CLAUDE.md") -replace "\\", "/")
if ((Test-Path $Global) -and (Select-String -Path $Global -SimpleMatch $Import -Quiet)) {
  Write-Host "Já importado em $Global"
} else {
  if (Test-Path $Global) {
    Copy-Item $Global "$Global.bak.$(Get-Date -Format yyyyMMddHHmmss)"
    Write-Host "Backup do CLAUDE.md anterior criado."
  }
  Add-Content -Path $Global -Encoding UTF8 -Value "`n# samuel-stack (atualiza com git pull na pasta do repositório)`n$Import"
  Write-Host "Linha de importação adicionada em $Global"
}

Passo "Bibliotecas Python usadas pelos scripts"
$py = Get-Command python -ErrorAction SilentlyContinue
if ($py) {
  & python -m pip install --user --quiet -r (Join-Path $Raiz "requirements.txt")
  if ($LASTEXITCODE -ne 0) { $Falhas.Add("python -m pip install -r requirements.txt") }
} else {
  $Falhas.Add("Python não encontrado: instale Python 3.10+ para os scripts de auditoria, radar e desvios")
}
if (-not (Get-Command soffice -ErrorAction SilentlyContinue)) {
  Write-Host "Aviso: LibreOffice (soffice) não está no PATH. Ele recalcula fórmulas e renderiza slides para conferência." -ForegroundColor Yellow
}

Passo "Resultado"
& claude plugin list
if ($Falhas.Count -gt 0) {
  Write-Host ""; Write-Host "Passos que falharam (rode de novo ou faça manualmente):" -ForegroundColor Yellow
  $Falhas | ForEach-Object { Write-Host " - $_" }
  exit 1
}
Write-Host ""; Write-Host "Pronto. Abra o Claude Code e rode /plugin para conferir. Para medir consumo: /usage (ou npx ccusage@latest)."
