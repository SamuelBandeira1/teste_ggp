# Pesquisa de mercado: orquestração, tokens, Office/BI e escrita

Pesquisa feita em 21/10/2026 para comparar o método do Samuel com o que o mercado usa no Claude Code. As contagens de estrelas e os percentuais de economia vêm de blogs e READMEs e variam entre fontes: tratar como ordem de grandeza, não como medida.

## 1. Frameworks de orquestração

| Framework | O que é | Ponto forte | Ponto fraco para o nosso uso | Decisão |
|---|---|---|---|---|
| **Claude Code nativo** (subagentes, skills, plan mode, hooks) | Subagente em `.md` com ferramentas e modelo próprios; skill carrega sob demanda | Já resolve orquestrador + especialistas com custo controlado | Exige escrever o próprio método | **Base do pacote** |
| **BMAD-METHOD** | Processo tipo SOP com personas (analista, PM, arquiteto, dev, QA) e documentos entre fases | Planejamento forte, portões claros | Feito para software com escopo travado; mudança no meio força replanejar; o "Party Mode" é um modelo só fazendo várias vozes | Já adaptado no A.R.E.S. (portões, passagem). Não instalar inteiro |
| **agency-agents** (msitarzewski) | Coleção de 100+ agentes especialistas em `.md` copiados para `~/.claude/agents` | Formato de especialista claro (missão, regras, entrega) | Medimos ~110 tokens fixos por agente instalado: 144 agentes ≈ 15 mil tokens em toda sessão | Formato adotado nos nossos 11 subagentes; não instalar a coleção |
| **Superpowers** (obra) | Skills de método para programação: brainstorm → plano → execução, TDD, depuração sistemática | O mais adotado; ativação automática; leve | Focado em código, não em análise e S&OP | **Instalado** para tarefas de código; análise segue o método Samuel (ver [REPOSITORIOS-RECOMENDADOS.md](REPOSITORIOS-RECOMENDADOS.md)) |
| **Everything Claude Code (ECC)** | Harness amplo: agentes, skills, hooks, regras para muitas linguagens | Cobertura grande pronta | Pesado; muito do que vem não se aplica | A `escrita-direta-pt-br` já adaptou o brand-voice dele. Não instalar |
| **claude-flow / Ruflo** | Plataforma de enxame com agente "rainha" e consenso | Paralelismo grande | Complexidade de infraestrutura e consumo alto | Não usar |
| oh-my-claudecode, Maestro, Gas Town | Times de agentes, especialistas multi-CLI, persistência em git | Nichos específicos | Sem ganho claro sobre o nativo para o nosso caso | Não usar |

**Conclusão.** O A.R.E.S. já era um BMAD/agency-agents adaptado ao trabalho do Samuel. O que faltava era rodar isso com subagentes reais (independência do Conselho, leitura pesada fora do contexto principal, modelo por tarefa). Frameworks pesados somam tokens fixos e cerimônia sem melhorar a entrega de análise.

**O que o método do Samuel tem e o mercado não tem**, e por isso foi mantido como está:
- separação método x dado com protocolo anti-contaminação de premissa entre ciclos;
- regra da "curva torta" (sem redondo, sem meses idênticos, sem salto > 25% sem explicação);
- registro do racional quando a gestão contraria a lógica matemática;
- fechamento com impacto de negócio e "o que preciso que você me traga", organizado por pessoa.

## 2. Economia de tokens

Fonte principal: documentação oficial de custos do Claude Code. Detalhe prático em [ECONOMIA-DE-TOKENS.md](ECONOMIA-DE-TOKENS.md).

| Técnica | Efeito | No pacote |
|---|---|---|
| Subagente com `model: haiku` para busca e conferência | Tarefa repetitiva em modelo barato; leitura pesada fica fora do contexto principal | `levantamento`, `auditor-numeros` |
| Instrução específica fora do CLAUDE.md, em skill | Skill só carrega quando usada; CLAUDE.md carrega sempre (meta: < 200 linhas) | CLAUDE.md global com ~40 linhas; resto em skills |
| `/clear` entre assuntos, `/compact` com foco | Contexto velho é reenviado a cada mensagem | Regra no CLAUDE.md + instrução de compactação |
| Hook que filtra saída antes do Claude ler | Log de milhares de linhas vira dezenas | Documentado; não ligado por padrão |
| Script em vez de raciocínio | Conta, filtro e conferência por código | `auditar_numeros.py`, `resumir_tmdl.py`, scripts de vendas |
| Agent teams (experimental) | ~7x mais tokens que sessão normal em plan mode | Não ligado |
| `/usage` com atribuição por skill, subagente e MCP + recomendações (`f` aplica) | Mostra onde o consumo está | Usar semanalmente |

Ferramentas de terceiros:
- **ccusage**: mede consumo a partir dos logs locais. Útil para medir antes de otimizar.
- **RTK (Rust Token Killer)**, **context-mode**, **Headroom**: filtram ou comprimem saída de ferramenta. Benchmark independente mostrou ganho pequeno quando a saída já é curta; servem para quem roda muito teste/log.
- **Caveman**: comprime a prosa do Claude. Conflita com a qualidade de texto que o Samuel exige; não usar em entrega.

## 3. Office e Power BI

| Item | Situação | Uso |
|---|---|---|
| Skills `xlsx`, `pptx`, `docx`, `pdf` da Anthropic (`document-skills`) | As mesmas que o claude.ai usa em produção | Instaladas pelo pacote; `entregas-office` adiciona o padrão do Samuel |
| Claude para Excel, PowerPoint e Word (add-in) | Disponível nos planos pagos; trabalha no arquivo aberto | Ajustes pontuais dentro do Office |
| Conector Microsoft 365 | Lê Outlook, OneDrive, SharePoint, Teams; escrita depende do admin | Ligar no claude.ai do trabalho |
| **Power BI Modeling MCP** (Microsoft, preview) | Opera modelo no Desktop, no Fabric ou em PBIP/TMDL; roda DAX; não mexe em página de relatório; tem `--readonly` | Documentado na skill `power-bi-pbip`, somente leitura primeiro |
| MCPs da comunidade (horizun-pbi-mcp, sulaiman013/powerbi-mcp) | Cobrem também relatório (PBIR); sem vínculo com a Microsoft | Avaliar com a TI antes |

A própria Microsoft alerta que LLM erra DAX de lógica complexa: por isso a skill obriga teste de toda medida contra número conhecido.

## 4. Texto sem cara de IA

- **humanizer** (blader) e forks: skill baseada no guia "Signs of AI writing" da Wikipedia, com varredura de padrões e segunda passada de auditoria. Em inglês.
- **stop-slop**: lista de padrões proibidos e nota de 1 a 10.
- Decisão: em vez de instalar skill em inglês, a `escrita-direta-pt-br` ganhou uma tabela de padrões de IA **em português** (abertura que anuncia, trio de adjetivos, contraste fabricado, gerúndio em cascata, vago no lugar do número etc.) e o subagente `revisor-texto`.
- O que mais melhora o texto daqui para frente é preencher o **perfil de voz** com 5 a 20 textos de trabalho escritos pelo Samuel (passo descrito na skill).

## 5. Próximos passos sugeridos

1. Preencher o perfil de voz da `escrita-direta-pt-br` com e-mails e mensagens de Teams reais.
2. Trazer os documentos do A.R.E.S. v3 do Projeto no claude.ai para `docs/ares-v3/`.
3. Criar casos de teste das skills principais (`claude plugin eval` ou a skill `skill-creator`) para medir se elas disparam no pedido certo.
4. Testar o MCP de Power BI em somente leitura num modelo real e ajustar a skill.
5. Depois de 2 semanas de uso, rodar `/usage` e `/insights` e cortar o que não é usado (plugins da Anthropic que não dispararam).

## Fontes

- Documentação Claude Code — custos: https://code.claude.com/docs/en/costs
- Documentação Claude Code — marketplaces: https://code.claude.com/docs/en/plugin-marketplaces
- Documentação Claude Code — manifesto de plugin: https://code.claude.com/docs/en/plugins/manifest-reference
- Documentação Claude Code — subagentes: https://code.claude.com/docs/en/sub-agents
- anthropics/skills: https://github.com/anthropics/skills
- anthropics/knowledge-work-plugins: https://github.com/anthropics/knowledge-work-plugins
- Microsoft Power BI Modeling MCP: https://github.com/microsoft/powerbi-modeling-mcp
- Análise do MCP de Power BI: https://medium.com/@michael.hannecke/microsofts-power-bi-modeling-mcp-server-what-it-actually-means-for-your-bi-workflow-b7afe99eef80
- horizun-pbi-mcp: https://pypi.org/project/horizun-pbi-mcp/
- Comparação BMAD, Claude Flow, Gas Town: https://re-cinq.com/blog/multi-agent-orchestration-bmad-claude-flow-gastown
- Comparação de plugins de fluxo: https://chenguangliang.com/en/posts/claude-code-workflow-plugins-comparison/
- Ferramentas de orquestração 2026: https://agentconn.com/blog/best-ai-agent-orchestration-tools-2026/
- Cinco frameworks comparados: https://www.everydev.ai/p/blog-five-claude-code-frameworks-compared-when-to-use-each-when-to-use-none
- BMAD — instalação: https://docs.bmad-method.org/how-to/install-bmad
- agency-agents — instalação: https://www.mintlify.com/msitarzewski/agency-agents/installation
- Superpowers — instalação: https://www.mintlify.com/obra/superpowers/installation/claude-code
- Pilha de economia de tokens (RTK, Caveman, context-mode, Headroom): https://github.com/sgaabdu4/claude-code-tips
- Ferramentas de tokens testadas: https://computingforgeeks.com/reduce-claude-code-token-usage-tools/
- Subagentes com Haiku: https://www.mindstudio.ai/blog/manage-token-costs-claude-code-dynamic-workflows
- Humanizer: https://www.blog.brightcoding.dev/2026/06/07/humanizer-the-essential-tool-to-strip-ai-patterns-from-text
- Skills de escrita: https://www.analyticsvidhya.com/blog/2026/08/top-5-claude-writing-skills/
- Claude no Microsoft 365: https://support.claude.com/en/articles/13892150-work-across-microsoft-365-apps
- Claude para Microsoft 365 (visão geral): https://www.usecarly.com/blog/claude-for-microsoft-365/
- Skills no claude.ai (upload, compartilhamento): https://support.claude.com/en/articles/12512180-using-skills-in-claude
