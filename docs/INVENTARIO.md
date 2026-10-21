# Inventário da conta pessoal

Levantamento feito em 21/10/2026 na conta pessoal (claude.ai + Claude Code), nos 13 repositórios do GitHub `SamuelBandeira1` e nas skills e plugins sincronizados.

## Skills autorais (9)

| Skill | Destino no pacote | O que mudou |
|---|---|---|
| `fluxo-antes-de-executar` | `metodo-samuel` | + delegação da busca ao subagente `levantamento`; + gatilho para o `orquestrador` |
| `checagem-de-entrega` | `metodo-samuel` | + script `auditar_numeros.py` (soma, redondo, repetido, salto > 25%, fórmula sem valor) |
| `escrita-direta-pt-br` | `metodo-samuel` | + tabela de padrões de IA em português; perfil de voz passa a usar textos de trabalho |
| `conselho-critico` | `metodo-samuel` | + execução com 4 subagentes independentes em paralelo no Claude Code (no web segue sequencial) |
| `planejamento-sop-aco-cearense` | `sop-comercial` | sem mudança |
| `radar-excecoes-vendas` | `sop-comercial` | indicação de onde fica a pasta do script no Claude Code |
| `analise-desvios-vendas` | `sop-comercial` | removido caminho fixo `C:\Users\samue\...\skills\docx` da conta pessoal; agora carrega a skill `docx` pelo nome |
| `equipe-nfc-3d` | `pessoal` (desligado) | sem mudança |
| `registro-shaping` | `pessoal` (desligado) | sem mudança. Depende de artefatos da conta pessoal; não funciona na conta de trabalho |

## Criado neste pacote

| Item | Por quê |
|---|---|
| Skill `orquestrador` | A orquestração do A.R.E.S. só existia para o negócio NFC + 3D. Esta é a versão para S&OP, dados, BI e Office, com subagentes reais e modelo por tarefa |
| Skill `fechamento-de-sessao` | Era citada pela `fluxo-antes-de-executar`, mas não existia na conta |
| Skill `entregas-office` | Padrão de Excel/PowerPoint/Word estava espalhado em várias skills; agora é um só, por cima das skills técnicas da Anthropic |
| Skill `power-bi-pbip` + `resumir_tmdl.py` | Não havia nada de Power BI na conta |
| 11 subagentes | Especialistas e conselheiros com ferramentas e modelo limitados |
| `config/CLAUDE.md` | Instrução global com roteamento por tipo de pedido |
| `config/templates/` | Padrão dos repositórios `copiloto-vendas` (CLAUDE.md de projeto de ML) e `soe-inteligencia-comercial` (agente mentor), generalizados |

## Plugins e skills de terceiros que estavam ativos

- **Da Anthropic, embutidos no claude.ai** (docx, xlsx, pptx, pdf, deep-research, skill-creator, mcp-builder, theme-factory, canvas-design, web-artifacts-builder, internal-comms, doc-coauthoring, algorithmic-art, learn, morning, import-memory, navegador, computer-use, docs, google-workspace): já vêm em qualquer plano pago do claude.ai. No Claude Code, o instalador adiciona `document-skills`; `skill-creator` e as demais vêm no plugin `example-skills@anthropic-agent-skills`, se quiser.
- **knowledge-work-plugins da Anthropic** (operations, design, product-management, sales, legal, finance, marketing, data, enterprise-search, customer-support, productivity, bio-research, product-tracking-skills, growthbook, pdf-viewer, cowork-plugin-management): o instalador liga só `data`, `finance`, `operations` e `productivity`, os ligados ao trabalho de S&OP. Os outros ficam disponíveis no mesmo marketplace (`claude plugin install <nome>@knowledge-work-plugins`). Cada um soma de 300 a 1.100 tokens fixos por sessão.
- **rytiva** (treino, plugin de terceiro com MCP próprio): pessoal, não incluído.

## Repositórios do GitHub (13)

| Repositório | Visibilidade | Uso no pacote |
|---|---|---|
| `soe-inteligencia-comercial` | público | Persona e regras do agente mentor (`Contexto/`) → `config/templates/CLAUDE-mentor-aprendizado.md`. Specs `.kiro/` são do projeto; o `AGENTS.md` aponta para `.agents/personas/maestro.md`, que **não está no repositório** |
| `copiloto-vendas` | privado | `claude.md` (orquestrador + agentes de dados/scoring/explicação, princípios de ML) → `config/templates/CLAUDE-projeto-dados.md` |
| `lstm-forecast-demanda` | privado | Projeto de estudo; padrão de mentor já coberto pelo template |
| `modelo-propensao` | privado | Repositório vazio |
| `gerador-atas-streamlit`, `divisor-atas-streamlit` | público | Apps de produto; não são método. Continuam no GitHub |
| `projeto_leads_barbearia` | público | Método comercial do negócio pessoal; não incluído |
| `comaf-portas`, `landing-liana`, `landing_page_garage_club`, `resolve-prod`, `samuelpessoal` | público/privado | Sites de clientes e pessoal; não incluídos |
| `teste_ggp` | público | Este pacote |

Nenhum repositório contém os "repositórios de engenharia reversa" citados. Se eles estão em outra conta do GitHub, numa organização ou só no computador, precisam ser trazidos para cá para entrar no pacote.

## O que não dá para puxar daqui (fazer à mão)

| Item | Onde está | Como levar |
|---|---|---|
| **A.R.E.S. v3** (documentos-base citados pelas skills `conselho-critico` e `equipe-nfc-3d`) | Conhecimento de algum Projeto no claude.ai | Abrir o Projeto, baixar os arquivos e colocar em `docs/ares-v3/` neste repositório. As regras principais já estão nas skills |
| Biblioteca de domínio e "Armadilhas aprendidas" do Projeto NFC | Conhecimento do Projeto no claude.ai | Mesmo caminho, se quiser na conta de trabalho |
| Memória do Claude (o que ele lembra de você) | Configurações > Memória, na conta pessoal | Exportar o resumo e usar a skill `import-memory` na conta de trabalho; tirar o que for pessoal |
| Instruções de Projetos e preferências do perfil | claude.ai | Usar `claude-ai/PREFERENCIAS-PERFIL.md` como base |
| Conectores (Gmail, Drive, Calendar, Figma, Vercel, Higgsfield) | Conectores da conta pessoal | Na conta de trabalho, conectar Microsoft 365 e o que a TI liberar |
| Artefatos publicados (app Shaping Quests etc.) | claude.ai | Ficam na conta pessoal |
