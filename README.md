# samuel-stack

Pacote para levar o método de trabalho da conta pessoal do Claude para a conta de trabalho: skills, subagentes, orquestração, regras de economia de tokens, padrão de Office e Power BI. Instala no Claude Code com um comando e gera os .zip para subir no claude.ai.

Testado em 21/10/2026 com Claude Code 2.1.306 no Linux: `claude plugin validate` passou no marketplace e nos 4 plugins, e o `instalar.sh` rodou do zero numa pasta de usuário vazia (8 plugins ativos, CLAUDE.md importado). O `instalar.ps1` (Windows) segue os mesmos passos, mas não foi executado aqui por falta de PowerShell no ambiente de teste.

## O que vem no pacote

| Plugin | Conteúdo | Custo fixo por sessão |
|---|---|---|
| `metodo-samuel` | Skills `fluxo-antes-de-executar`, `orquestrador`, `conselho-critico`, `checagem-de-entrega` (com script de auditoria de números), `escrita-direta-pt-br` (com varredura de padrões de IA), `fechamento-de-sessao`. Subagentes: `levantamento`, `pesquisador-web`, `analista-dados`, `revisor-texto`, `auditor-numeros` e os 4 do Conselho | ~2,0 mil tokens |
| `sop-comercial` | `planejamento-sop-aco-cearense`, `radar-excecoes-vendas`, `analise-desvios-vendas` (com os scripts Python) | ~0,7 mil |
| `office-bi` | `entregas-office` (padrão de Excel, PowerPoint, Word), `power-bi-pbip` (PBIP/TMDL/DAX com script que resume o modelo). Subagentes `construtor-office` e `especialista-power-bi` | ~0,6 mil |
| `pessoal` | `equipe-nfc-3d`, `registro-shaping`. Vem **desligado** | — |

O instalador também adiciona os repositórios que passaram na checagem de [docs/REPOSITORIOS-RECOMENDADOS.md](docs/REPOSITORIOS-RECOMENDADOS.md):

| Repositório | Para quê |
|---|---|
| `anthropics/skills` (document-skills) | Excel, PowerPoint, Word, PDF |
| `anthropics/knowledge-work-plugins` (`data`, `finance`, `operations`, `productivity`) | Os mesmos plugins de trabalho da conta pessoal |
| `obra/superpowers` | Método para tarefas de código: plano, TDD, depuração, verificação |
| `forrestchang/andrej-karpathy-skills` | Quatro regras de código enxuto e verificado |
| `morluto/rea` (REA, o "do Morlock") | Engenharia reversa de site, app e executável. Precisa de Node 22.19+ |

Opcionais: `--com-design` (UI UX Pro Max) e `--com-pesquisa` (last30days). Com o padrão ligado, o custo fixo fica em torno de 8,5 mil tokens por sessão; o conteúdo completo de cada skill só entra quando ela é usada.

## Instalar no Claude Code (conta de trabalho)

1. Copiar este repositório para o GitHub do trabalho (de preferência **privado**, ver "Cuidados" abaixo) e clonar na máquina:
   ```
   git clone <url-do-repo-no-trabalho> samuel-stack
   cd samuel-stack
   ```
2. Entrar no Claude Code com a conta de trabalho (`claude` e depois `/login`).
3. Rodar o instalador:
   - Windows: `powershell -ExecutionPolicy Bypass -File .\scripts\instalar.ps1`
   - Linux, macOS, WSL: `./scripts/instalar.sh`
   - Opções: `--com-pessoal` / `-ComPessoal` liga o plugin pessoal; `--sem-extras` / `-SemExtras` pula os plugins de terceiros; `--sem-rea` / `-SemRea` pula o REA; `--com-design` / `-ComDesign` e `--com-pesquisa` / `-ComPesquisa` somam os opcionais; `--repo dono/repo` / `-Repo dono/repo` instala direto do GitHub em vez da pasta local.
4. Abrir o Claude Code e conferir com `/plugin` e `/context`.

O instalador:
- registra o marketplace `samuel-stack` e instala os plugins;
- adiciona os marketplaces `anthropics/skills` e `anthropics/knowledge-work-plugins`;
- acrescenta em `~/.claude/CLAUDE.md` uma linha `@<pasta>/config/CLAUDE.md` (faz backup do arquivo antigo). Como a linha aponta para a pasta clonada, um `git pull` atualiza as instruções;
- instala as bibliotecas Python dos scripts (pandas, numpy, openpyxl, xlsxwriter, python-pptx, python-docx).

Para atualizar depois: `git pull` na pasta. Instalado a partir da pasta local, o Claude Code lê os plugins direto dela, então a mudança vale na próxima sessão. Instalado com `--repo` (GitHub), aumentar o `version` no `plugin.json` de cada plugin alterado e rodar `claude plugin marketplace update samuel-stack` seguido de `claude plugin update <plugin>@samuel-stack`.

Instalação manual, sem script:
```
claude plugin marketplace add <pasta-ou-dono/repo>
claude plugin install metodo-samuel@samuel-stack
claude plugin install sop-comercial@samuel-stack
claude plugin install office-bi@samuel-stack
claude plugin marketplace add anthropics/skills
claude plugin install document-skills@anthropic-agent-skills
```

## Levar para o claude.ai (web e desktop)

O claude.ai não usa subagentes nem a pasta `~/.claude`, então o caminho é outro. Passo a passo em [docs/CLAUDE-AI.md](docs/CLAUDE-AI.md). Resumo:
1. `python scripts/empacotar_claude_ai.py` gera um .zip por skill em `dist/claude-ai/skills/`.
2. No claude.ai da conta de trabalho: Personalizar > Skills > "+" > Fazer upload de skill, um zip por vez.
3. Colar as preferências de [claude-ai/PREFERENCIAS-PERFIL.md](claude-ai/PREFERENCIAS-PERFIL.md) em Configurações > Perfil.
4. Conectar Microsoft 365 nos conectores (o admin libera a escrita).

## Como o fluxo funciona depois de instalado

1. Pedido com várias etapas → `fluxo-antes-de-executar` checa o que já existe (subagente `levantamento`, modelo leve), separa método de dado, faz até 4 perguntas e traz a proposta macro.
2. Três ou mais tarefas diferentes → `orquestrador` divide entre subagentes, cada um com o modelo adequado (haiku para busca e conferência, sonnet para análise e construção), com bloco de passagem e "pronto quando".
3. Números → `auditor-numeros` roda `auditar_numeros.py` (total que não fecha, número redondo, valores repetidos, salto acima de 25%).
4. Crítica → os 4 conselheiros rodam em paralelo, cada um no seu contexto, sem ler a crítica dos outros.
5. Entrega → `checagem-de-entrega` + `escrita-direta-pt-br`, fechando com impacto de negócio e "o que preciso que você me traga".
6. Fim → `fechamento-de-sessao` grava decisões, premissas e pendências no `CHECKPOINT.md`.

## Estrutura

```
.claude-plugin/marketplace.json   catálogo dos plugins
plugins/<plugin>/                 skills/, agents/, .claude-plugin/plugin.json
config/CLAUDE.md                  instruções globais (importadas no ~/.claude/CLAUDE.md)
config/templates/                 CLAUDE.md de projeto de dados e de projeto de estudo
claude-ai/                        textos para colar no claude.ai
scripts/                          instaladores e empacotador
docs/                             inventário, pesquisa de mercado, tokens, claude.ai
```

## Cuidados

- **Este repositório (`teste_ggp`) é público.** O conteúdo não tem senha, token nem número de ciclo, mas descreve o método de S&OP da Aço Cearense, nomes de colunas das bases e os projetos pessoais. Recomendo copiar para um repositório **privado** no GitHub do trabalho e tornar este privado ou apagar o branch depois.
- Antes de rodar na máquina do trabalho, confirmar a política de TI: o instalador baixa plugins do GitHub (Anthropic, Superpowers, Karpathy) e o REA pelo npm. O REA é ferramenta de engenharia reversa; usar só em sistema próprio ou com autorização.
- O MCP de Power BI da Microsoft está em preview: começar com `--readonly` e fazer backup do projeto (ver skill `power-bi-pbip`).

## Documentação

- [docs/REPOSITORIOS-RECOMENDADOS.md](docs/REPOSITORIOS-RECOMENDADOS.md): os repositórios "obrigatórios" das redes sociais, checados um a um (instalar, opcional, não instalar)
- [docs/INVENTARIO.md](docs/INVENTARIO.md): o que foi puxado da conta pessoal, o que mudou e o que ficou de fora
- [docs/PESQUISA-MERCADO.md](docs/PESQUISA-MERCADO.md): comparação com BMAD, Superpowers, agency-agents, claude-flow e outros, e o que foi incorporado
- [docs/ECONOMIA-DE-TOKENS.md](docs/ECONOMIA-DE-TOKENS.md): regras, configurações e ferramentas para medir e reduzir consumo
- [docs/CLAUDE-AI.md](docs/CLAUDE-AI.md): migração da parte web (skills, perfil, projetos, conectores)
