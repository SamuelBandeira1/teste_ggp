# Instruções para o Claude da conta de trabalho do Samuel

> **Para o Samuel:** abra o Claude Code no computador do trabalho, já logado na conta de trabalho, e cole este documento inteiro como primeira mensagem. Ele vai checar a máquina, perguntar o que precisar e instalar tudo.

---

Olá, Claude. Sou o Samuel. Este documento explica o que preciso que você faça nesta máquina. Leia tudo antes de executar qualquer coisa.

## 1. Contexto

Trabalho no Planejamento Integrado (S&OP/S&OE) do Grupo Aço Cearense. Uso Python, Excel, PowerPoint e Power BI todo dia. Na minha conta pessoal do Claude eu montei um método de trabalho: skills, subagentes, regras de qualidade e de economia de tokens. Ele foi empacotado num repositório chamado **samuel-stack**, e agora quero o mesmo funcionando aqui, na conta de trabalho.

O pacote está em:
- Repositório: `https://github.com/SamuelBandeira1/teste_ggp` (público)
- Branch: `claude/gracious-ptolemy-bmbc95` (o branch `main` está vazio, não use)

Ele contém:

| Parte | O que é |
|---|---|
| `plugins/metodo-samuel` | Skills `fluxo-antes-de-executar`, `orquestrador`, `conselho-critico`, `checagem-de-entrega`, `escrita-direta-pt-br`, `fechamento-de-sessao` e 9 subagentes (levantamento, pesquisador-web, analista-dados, revisor-texto, auditor-numeros e os 4 do Conselho) |
| `plugins/sop-comercial` | Skills `planejamento-sop-aco-cearense`, `radar-excecoes-vendas`, `analise-desvios-vendas`, com scripts Python |
| `plugins/office-bi` | Skills `entregas-office` e `power-bi-pbip`, e os subagentes `construtor-office` e `especialista-power-bi` |
| `plugins/pessoal` | Projetos pessoais. **Não instalar** nesta conta |
| `config/CLAUDE.md` | Minhas instruções globais (roteamento de pedidos e regras) |
| `config/templates/` | Modelos de CLAUDE.md para projetos e um `.gitignore` para projetos de dados |
| `scripts/instalar.ps1` e `instalar.sh` | Instaladores |
| `scripts/empacotar_claude_ai.py` | Gera os .zip das skills para subir no claude.ai web |
| `docs/` | Inventário, pesquisa de mercado, repositórios recomendados, economia de tokens, migração do claude.ai |
| `requirements.txt` | Bibliotecas Python dos scripts |

O instalador também instala estes repositórios de terceiros, checados um a um (detalhes em `docs/REPOSITORIOS-RECOMENDADOS.md`):
- `anthropics/skills` (document-skills: xlsx, pptx, docx, pdf)
- `anthropics/knowledge-work-plugins`: `data`, `finance`, `operations`, `productivity`
- `obra/superpowers`: método para tarefas de código
- `forrestchang/andrej-karpathy-skills`: regras de código enxuto
- `morluto/rea` (REA, Reverse Engineer Anything): engenharia reversa de site, app e executável

## 2. Regras que valem durante todo o trabalho

1. **Pergunte antes de instalar programa no sistema** (Git, Node, Python, LibreOffice) e antes de criar repositório no GitHub. Mostre o comando que vai rodar.
2. **Dado da empresa nunca vai para o GitHub pessoal.** O samuel-stack só tem método, sem número de ciclo, base de vendas ou senha, e pode ficar num repositório privado meu. Projeto com dado da Aço Cearense fica no GitHub/Azure DevOps da empresa (se a TI liberar) ou só nesta máquina.
3. **Antes de qualquer push**, liste os arquivos que vão subir e confirme que não há `.xlsx`, `.xlsm`, `.csv`, `.pbix`, `.parquet`, `.env`, `secrets.toml` ou credenciais.
4. **REA é ferramenta de engenharia reversa.** Pergunte se a TI autorizou antes de instalar. Se eu disser que não ou não souber, instale com `-SemRea`.
5. **Não mexa no plugin `pessoal`.**
6. Se um passo falhar, não improvise uma alternativa arriscada. Diga o erro, a causa provável e a opção mais segura.

## 3. Passo a passo

### Passo 1 — Checar a máquina

Rode e me mostre um resumo do que tem e do que falta:
- Sistema operacional (provavelmente Windows)
- `claude --version`
- `git --version`
- `gh --version` e `gh auth status` (GitHub CLI)
- `node --version`: o REA precisa de 22.19+, 24.11+ ou 26+
- `python --version` (ou `python3`): precisa de 3.10+
- `soffice --version` (LibreOffice: recalcula fórmulas e renderiza slides para conferência; opcional, mas recomendado)

Se faltar algo no Windows, proponha a instalação pelo `winget` e espere meu ok:
```
winget install --id Git.Git -e
winget install --id GitHub.cli -e
winget install --id OpenJS.NodeJS.LTS -e
winget install --id Python.Python.3.12 -e
winget install --id TheDocumentFoundation.LibreOffice -e
```
Se o `winget` for bloqueado pela TI, me diga o que falta para eu pedir à TI.

### Passo 2 — Baixar o pacote

Na pasta do usuário:
```
cd $HOME
git clone -b claude/gracious-ptolemy-bmbc95 https://github.com/SamuelBandeira1/teste_ggp.git samuel-stack
cd samuel-stack
```
Confira que existem `.claude-plugin/marketplace.json`, `plugins/`, `config/CLAUDE.md` e `scripts/instalar.ps1`. Leia o `README.md` para ter o mapa do pacote.

### Passo 3 — Criar o meu repositório privado (pergunte antes)

Pergunte em qual conta do GitHub quero guardar o samuel-stack (minha pessoal ou a da empresa). Com a resposta:

1. Se o `gh` não estiver logado: `gh auth login` (eu faço o login no navegador; nunca me peça senha ou token no chat).
2. Troque a origem antiga e crie o repositório privado:
   ```
   git remote rename origin origem-pacote
   git checkout -b main
   gh repo create samuel-stack --private --source . --remote origin
   ```
3. Antes do push, mostre `git ls-files` filtrado por extensões de dados e segredos (regra 3 da seção 2). Só depois:
   ```
   git push -u origin main
   ```
4. Me mostre a URL do repositório criado.

Se eu disser para pular este passo, siga usando a pasta local; a instalação funciona igual.

### Passo 4 — Instalar

Na pasta `samuel-stack`, no PowerShell:
```
powershell -ExecutionPolicy Bypass -File .\scripts\instalar.ps1
```
Opções:
- `-SemRea`: não instala o REA (use se a TI não autorizou)
- `-ComDesign`: soma o UI UX Pro Max (páginas e dashboards web)
- `-ComPesquisa`: soma o last30days (pesquisa recente em Reddit, X, YouTube)
- `-SemExtras`: instala só os plugins do Samuel, sem os de terceiros

Linux, macOS ou Git Bash: `./scripts/instalar.sh` com as mesmas opções em minúsculo (`--sem-rea`, `--com-design`, `--com-pesquisa`, `--sem-extras`).

O instalador:
1. registra o marketplace `samuel-stack` (pasta local) e instala `metodo-samuel`, `sop-comercial` e `office-bi`;
2. instala os plugins de terceiros da seção 1;
3. roda `npx -y rea-agents@latest setup --client claude_code --yes`, que registra o MCP do REA em `~/.claude.json` (com backup) e instala a skill `reverse-engineer-anything`;
4. acrescenta em `~/.claude/CLAUDE.md` a linha `@<pasta>/config/CLAUDE.md`, fazendo backup do arquivo anterior;
5. instala as bibliotecas do `requirements.txt`.

**Atenção:** o `instalar.ps1` não foi executado num Windows de verdade, só a versão `.sh` foi testada. Se der erro, rode os comandos à mão:
```
claude plugin marketplace add <caminho-da-pasta-samuel-stack>
claude plugin install metodo-samuel@samuel-stack
claude plugin install sop-comercial@samuel-stack
claude plugin install office-bi@samuel-stack
claude plugin marketplace add anthropics/skills
claude plugin install document-skills@anthropic-agent-skills
claude plugin marketplace add anthropics/knowledge-work-plugins
claude plugin install data@knowledge-work-plugins
claude plugin install finance@knowledge-work-plugins
claude plugin install operations@knowledge-work-plugins
claude plugin install productivity@knowledge-work-plugins
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin install superpowers@claude-plugins-official
claude plugin marketplace add forrestchang/andrej-karpathy-skills
claude plugin install andrej-karpathy-skills@karpathy-skills
npx -y rea-agents@latest setup --client claude_code --yes
python -m pip install --user -r requirements.txt
```
E adicione ao final de `~/.claude/CLAUDE.md` (crie o arquivo se não existir, com backup se existir) a linha abaixo, com o caminho absoluto da pasta e barras `/`:
```
@C:/Users/<usuario>/samuel-stack/config/CLAUDE.md
```

### Passo 5 — Verificar

1. `claude plugin list`: estes plugins devem aparecer habilitados: `metodo-samuel`, `sop-comercial`, `office-bi`, `document-skills`, `data`, `finance`, `operations`, `productivity`, `superpowers`, `andrej-karpathy-skills` (mais `ui-ux-pro-max` e `last30days` se usei as opções). `pessoal` não deve estar.
2. `claude plugin details metodo-samuel`: deve listar 6 skills e 9 agentes.
3. Abra `~/.claude/CLAUDE.md` e confirme a linha de importação. Depois de reiniciar o Claude Code, rode `/memory` e confirme que `config/CLAUDE.md` aparece carregado. Se o import não carregar, copie o conteúdo de `config/CLAUDE.md` direto para `~/.claude/CLAUDE.md`.
4. REA (se instalado): `npx -y rea-agents@latest doctor` e confirme que a pasta `~/.claude/skills/reverse-engineer-anything` existe. Ghidra só é necessário para executável nativo; site e app JavaScript funcionam sem.
5. Scripts:
   ```
   python plugins/metodo-samuel/skills/checagem-de-entrega/scripts/auditar_numeros.py --help
   python plugins/office-bi/skills/power-bi-pbip/scripts/resumir_tmdl.py --help
   ```
6. Peça para eu reiniciar o Claude Code e rodar `/context`, para ver o consumo fixo. O esperado é algo em torno de 8,5 mil tokens das skills e plugins.

### Passo 6 — Teste de funcionamento

Depois de reiniciar, me sugira estes três pedidos de teste e confira se o comportamento bate:

| Pedido de teste | O que tem que acontecer |
|---|---|
| "Monta um plano de demanda de 2027 por linha" | Usa `fluxo-antes-de-executar` e `planejamento-sop-aco-cearense`: pergunta escopo, premissas e arquivos e traz a proposta macro **antes** de qualquer número. Não inventa volume |
| "Audita esta planilha" (com um .xlsx qualquer meu) | Usa `checagem-de-entrega` / `auditor-numeros` e roda `auditar_numeros.py` |
| "Cria um script Python que lê um CSV e soma por mês" | Usa o método do Superpowers (plano, teste, verificação) com as regras do Karpathy |

Se alguma skill não disparar, verifique se o plugin está habilitado e me diga qual falhou.

### Passo 7 — Parte web (claude.ai) — me orientar, não fazer sozinho

O claude.ai web não lê esta máquina. Rode:
```
python scripts/empacotar_claude_ai.py
```
Depois me passe o roteiro (está em `docs/CLAUDE-AI.md`):
1. Em claude.ai > Personalizar > Skills > "+" > Fazer upload de skill, subir um zip por vez de `dist/claude-ai/skills/`, na ordem: fluxo-antes-de-executar, checagem-de-entrega, escrita-direta-pt-br, conselho-critico, orquestrador, fechamento-de-sessao, entregas-office, power-bi-pbip, planejamento-sop-aco-cearense, radar-excecoes-vendas, analise-desvios-vendas.
2. Colar o texto de `claude-ai/PREFERENCIAS-PERFIL.md` em Configurações > Perfil.
3. Conectar o Microsoft 365 em Configurações > Conectores (a escrita em arquivos depende do admin).
4. Ligar "Execução de código e criação de arquivos".

## 4. Como trabalhar comigo depois de instalado

Isto já está no `config/CLAUDE.md`. Resumo:
- Pedido com várias etapas → `fluxo-antes-de-executar`: ver o que existe, separar método de dado, até 4 perguntas, proposta macro antes do detalhe.
- 3 ou mais tarefas diferentes → `orquestrador`, com subagentes no modelo certo (haiku para busca e conferência, sonnet para análise e texto).
- Antes de entregar → `checagem-de-entrega`; criação grande → `conselho-critico`; todo texto → `escrita-direta-pt-br`.
- Código → Superpowers + Karpathy. Análise, planilha, deck, Power BI → o meu método.
- Nenhum número sem origem nesta rodada. Fechar análise com: o que foi examinado, o que significa, oportunidade, o que preciso que você me traga.

Rotina de Git (casa e trabalho):
- **Começo do dia**: `git pull` na pasta `samuel-stack` (atualiza skills e instruções).
- **Fim do dia, se mudou algo**: confira os arquivos (regra 3 da seção 2), depois commit e `git push`.
- Mudou skill e instalou com `--repo` em vez da pasta local: aumente o `version` em `plugins/<plugin>/.claude-plugin/plugin.json` e rode `claude plugin marketplace update samuel-stack`.
- Projeto novo de dados: copie `config/templates/gitignore-projeto-dados` como `.gitignore` e `config/templates/CLAUDE-projeto-dados.md` como `CLAUDE.md`, e crie um `requirements.txt`.

## 5. Pendências que ficam comigo (me lembre no fim)

1. Confirmar com a TI: uso de GitHub pessoal para o método, REA, MCP de Power BI e winget.
2. Mandar de 5 a 20 textos meus de trabalho (e-mail, Teams) para preencher o perfil de voz da `escrita-direta-pt-br`.
3. Trazer os documentos do A.R.E.S. v3 do Projeto da conta pessoal para `docs/ares-v3/`.
4. Importar a memória de trabalho da conta pessoal (skill `import-memory` no claude.ai).
5. Depois de 2 semanas de uso: `/usage` e `/insights` para cortar plugin que não foi usado.

## 6. O que me entregar no final

Um relatório curto, neste formato:
```
Instalação samuel-stack — <data>
Máquina: <SO, versões de claude, git, gh, node, python, LibreOffice>
Repositório: <URL do repositório privado ou "pasta local">
Plugins habilitados: <lista>
REA: <instalado / não instalado e por quê>
CLAUDE.md global: <importado / copiado>
Testes: <resultado dos 3 pedidos de teste>
Falhou ou ficou pendente: <item — motivo — o que fazer>
O que preciso que você me traga: <por pessoa ou área: TI, eu>
```
