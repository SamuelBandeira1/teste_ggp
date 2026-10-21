# Economia de tokens

## Quanto o pacote custa por sessão

Medido com `claude plugin details` (estimativa do próprio Claude Code). "Fixo" é o que entra em toda sessão (nome e descrição das skills e subagentes); o conteúdo completo só entra quando a skill é usada.

| Plugin | Fixo por sessão | Ao usar (exemplos) |
|---|---|---|
| metodo-samuel | ~1.970 | orquestrador ~2,7 mil · escrita ~2,1 mil · conselho ~1,7 mil |
| sop-comercial | ~730 | — |
| office-bi | ~590 | — |
| document-skills (Anthropic) | ~1.030 | — |
| data | ~1.130 | — |
| operations | ~870 | — |
| finance | ~750 | — |
| productivity | ~350 | — |
| **Total** | **~7.400** | |

Plugin que não for usado em 2 semanas: desligar com `claude plugin disable <nome>@<marketplace>`.

## Regras que já estão no pacote

1. **Modelo por tarefa** (frontmatter `model:` dos subagentes): haiku para `levantamento` e `auditor-numeros`; sonnet para análise, construção, texto e Conselho. A conversa principal fica com o modelo que você escolher.
2. **Leitura pesada fora do contexto principal**: base grande, log e muitos arquivos vão para subagente, que devolve resumo de até 15 linhas e caminho de arquivo.
3. **Script em vez de raciocínio**: `auditar_numeros.py`, `resumir_tmdl.py`, scripts de radar e desvios.
4. **CLAUDE.md enxuto** (~40 linhas) com instrução de compactação; o detalhe mora nas skills.
5. **Sem cascata**: subagente não chama subagente.

## Hábitos

- Um assunto por sessão. `/clear` ao trocar de assunto (custa zero); `/rename` antes para achar depois com `/resume`.
- `/compact <o que preservar>` antes de pausa longa num trabalho que continua. Compactar contexto grande também gasta.
- Pedido específico ("ajusta a medida X no arquivo Y") gasta menos que pedido vago ("melhora o modelo").
- Plan mode (Shift+Tab) em tarefa grande: errar a direção custa mais que planejar.
- Esc para parar quando o Claude for para o lado errado; `/rewind` para voltar.
- Não trocar de modelo no meio da conversa sem motivo: invalida o cache.

## Medir

- `/usage`: consumo da sessão, uso do plano, atribuição por skill/subagente/MCP e recomendações (`f` aplica as que der).
- `/context`: o que está ocupando a janela agora.
- `/insights`: relatório de como você usa o Claude Code e onde trava.
- `npx ccusage@latest`: histórico de consumo por dia e por modelo, a partir dos logs locais.

## Configurações opcionais (`~/.claude/settings.json`)

Rodar todos os subagentes num modelo só (útil se a cota apertar):
```json
{ "env": { "CLAUDE_CODE_SUBAGENT_MODEL": "haiku", "CLAUDE_CODE_SUBAGENT_MODEL_FORCE": "1" } }
```
Sem o `_FORCE`, vale só para subagente que não declara modelo.

Hook que corta saída de teste longa (exemplo da documentação oficial): ver "Offload processing to hooks" em https://code.claude.com/docs/en/costs. Só vale a pena se você roda suíte de teste grande com frequência.

## O que não fazer

- Instalar coleção inteira de agentes (100+): cada agente custa ~110 tokens fixos.
- Ligar agent teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`) para trabalho que um orquestrador com 3 subagentes resolve: o time custa várias vezes mais.
- Usar compressor de prosa (Caveman e similares) em texto que vai para outra pessoa.
