# Repositórios que circulam como "obrigatórios" no Claude Code: quais instalar

Pesquisa de 21/10/2026. Juntei os repositórios que mais aparecem nos vídeos e posts de TikTok, Instagram, Threads, X e YouTube ("os 5 repositórios que você tem que ter", "os 2 principais") e conferi cada um no GitHub. Os vídeos quase nunca mostram dado de uso; por isso o critério foi:

1. **Popularidade real**: estrelas no GitHub (ranking diário de 21/10/2026) e, quando existe, número de instalações.
2. **Promessa x evidência**: o que o vídeo diz que muda e o que o próprio repositório (ou teste independente) mostra.
3. **Custo**: tokens fixos por sessão, medidos instalando cada um numa pasta de usuário limpa com `claude plugin details`.
4. **Encaixe no seu trabalho**: S&OP, dados, Excel/PowerPoint/Power BI, apps Python e páginas web, numa máquina corporativa.

## Resultado

### Instalar (o instalador já faz)

| Repositório | Estrelas | O que muda de verdade | Custo fixo | Por que entra |
|---|---|---|---|---|
| **anthropics/skills** (document-skills) | 183 mil | Excel, PowerPoint, Word e PDF no mesmo padrão que o claude.ai usa | ~1.030 tok | Base de toda entrega Office |
| **obra/superpowers** | 303 mil (o mais estrelado; ~1 milhão de instalações) | Em tarefa de código: brainstorming → plano → execução com subagentes, TDD, depuração sistemática, verificação antes de dizer que terminou | ~850 tok + 1 hook de início de sessão | É o único da lista com adoção medida em instalações e aceito no marketplace oficial da Anthropic. Vale para os apps Python (SOE, copiloto, atas) |
| **forrestchang/andrej-karpathy-skills** | 222 mil | Quatro regras: pensar antes de codar, o mínimo de código que resolve, mexer só no necessário, definir critério de sucesso e verificar | ~105 tok | Custo quase zero e as regras são as mesmas do seu método (perguntar o ambíguo, não inventar escopo, verificar) |
| **morluto/rea** (Reverse Engineer Anything) — o "do Morlock" | 354 mil | Dá ao Claude ferramentas para analisar site, app Electron/JavaScript, APK e binário, a partir do que o app mostra até o código de máquina | ~70 tok (skill de 23 KB carrega só quando usada; ferramentas MCP ficam adiadas) | Você pediu. Instala limpo (`npx rea-agents setup --client claude_code`), com backup da configuração |

Com o pacote do Samuel e os plugins da Anthropic, o total fixo fica em torno de **8,5 mil tokens por sessão**.

**O que esperar do REA, sem exagero.** Ele explica e reconstrói comportamento a partir do que está no app; não devolve o código-fonte original nem clona sistema sozinho. Código que roda no servidor não aparece. Para site e app JavaScript não precisa de nada extra; para executável nativo precisa do Ghidra (gratuito) ou IDA/Hopper. No Windows o suporte a Ghidra é experimental. O próprio projeto limita o uso a pesquisa, interoperabilidade e software que você tem direito de analisar: no trabalho, só em sistema próprio ou com autorização da TI.

### Instalar se for usar (opcional no instalador)

| Repositório | Estrelas | Quando vale | Custo fixo | Como |
|---|---|---|---|---|
| **nextlevelbuilder/ui-ux-pro-max-skill** | 138 mil | Landing page, página de cliente, dashboard web. Catálogo de estilos, paletas, fontes e regras de UX | ~1.070 tok | `--com-design` no instalador |
| **mvanhorn/last30days-skill** | 65 mil | Pesquisa do que se falou nos últimos 30 dias em Reddit, X, YouTube, Hacker News, ranqueado por engajamento | ~105 tok | `--com-pesquisa` no instalador |
| **upstash/context7** | — | Documentação atualizada de bibliotecas (pandas, Streamlit, python-pptx) quando estiver programando | MCP adiado | `npx ctx7 setup --claude` (pede login OAuth) |
| **mattpocock/skills** | 299 mil | Alternativa ao Superpowers, com bons métodos de entrevista (`grill-me`) e passagem de contexto (`handoff`) | ~1.650 tok | Não junto com o Superpowers: os dois fazem a mesma coisa |

### Não instalar

| Repositório | O que o vídeo promete | O que a checagem mostrou |
|---|---|---|
| **thedotmack/claude-mem** | Memória entre sessões | O Claude Code já tem memória automática nativa. O claude-mem adiciona 6 hooks, um serviço local com banco vetorial e, por padrão, pede login num serviço externo para resumir as observações: risco para dado da empresa |
| **JuliusBrussee/caveman** | Corta 65% a 75% dos tokens | No teste do próprio repositório, a instrução simples "responda de forma concisa" deu 4.334 tokens contra 4.119 do caveman. A JetBrains mediu 8,5% a menos. Ele liga sozinho também nos subagentes e muda o jeito de escrever, o que bate de frente com a escrita da entrega |
| **gsd-build/get-shit-done** (GSD) | Sistema de desenvolvimento por especificação | Repositório arquivado (mudou para open-gsd/gsd-core) e faz o mesmo papel do Superpowers |
| **affaan-m/everything-claude-code** (ECC) | Setup completo de vencedor de hackathon | Pesado: dezenas de agentes, hooks e regras para várias linguagens; quase nada se aplica a S&OP |
| **Panniantong/Agent-Reach** | Claude pesquisando Reddit, YouTube, X | Vários canais usam cookie de conta logada; o próprio README avisa risco de banimento de conta. Para pesquisa, o last30days faz o mesmo sem cookie |
| **free-claude-code**, 9Router e outros "Claude de graça" | Usar o Claude Code com outros modelos | Passa código e chave por terceiros. Proibido em máquina corporativa |
| Repositórios com o "código vazado do Claude Code" (claw-code e espelhos) | Ver como o Claude Code funciona por dentro | Problema legal e já usados para espalhar malware que rouba credencial (Trend Micro) |
| hesreallyhim/awesome-claude-code, ComposioHQ/awesome-claude-skills | "Todas as skills" | São listas de links, não ferramenta. Bom para consultar, não para instalar |
| headroom, codebase-memory-mcp, graphify | 60% a 99% menos tokens | Números só do próprio autor; benchmark independente achou ganho pequeno quando a saída já é curta. Servem para base de código muito grande |

## Ordem de prioridade entre os métodos

O Superpowers e o seu método se sobrepõem em "planejar antes de executar". A regra no `config/CLAUDE.md`:
- **Tarefa de código** (app, script, automação, página): manda o Superpowers (brainstorming, plano, TDD, depuração), com as regras do Karpathy.
- **Análise, plano S&OP, planilha, deck, Power BI, texto**: manda o método Samuel (`fluxo-antes-de-executar`, `orquestrador`, `checagem-de-entrega`).
- **Engenharia reversa** de site, app ou executável: REA, só em sistema próprio ou autorizado.

## Fontes

- Ranking diário de estrelas (21/10/2026): https://github.com/thejesh23/ai-plugin-rankings
- REA: https://github.com/morluto/rea · checagem do que é verdade: https://pasqualepillitteri.it/en/news/23845/rea-reverse-engineer-anything-github-true-false · guia em português: https://horadecodar.com.br/rea-reverse-engineer-anything/ · vídeo: https://www.youtube.com/watch?v=YJI_94GK-Bw
- Superpowers: https://github.com/obra/superpowers
- Karpathy skills: https://github.com/multica-ai/andrej-karpathy-skills
- Matt Pocock skills: https://github.com/mattpocock/skills
- claude-mem: https://github.com/thedotmack/claude-mem · memória nativa do Claude Code: https://code.claude.com/docs/en/memory
- Caveman (benchmarks no README): https://github.com/JuliusBrussee/caveman
- GSD (arquivado): https://github.com/gsd-build/get-shit-done
- UI UX Pro Max: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- last30days: https://github.com/mvanhorn/last30days-skill
- Context7: https://github.com/upstash/context7
- Agent-Reach: https://github.com/Panniantong/Agent-Reach
- Listas virais: post de Hasan Toor no X (https://x.com/hasantoxr/status/2035312729427480840), Threads @olucaslopesc (https://www.threads.com/@olucaslopesc/post/DWM-wdnmANb), TikTok @sabrina_ramonov (https://www.tiktok.com/@sabrina_ramonov/video/7617663469134892302), TikTok @chase_ai_ (https://www.tiktok.com/@chase_ai_/video/7625388860536605966), guia "5 Best GitHub Repos for Claude Code" (https://buildwire.ai/blog/the-5-best-github-repos-for-claude-code/)
- Alerta de malware em repositórios falsos do Claude Code: https://www.trendmicro.com/en_us/research/26/d/weaponizing-trust-claude-code-lures-and-github-release-payloads.html
