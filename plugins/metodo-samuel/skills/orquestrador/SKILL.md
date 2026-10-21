---
name: orquestrador
description: "Use quando o pedido do Samuel tiver 3 ou mais tarefas de naturezas diferentes (dados + análise + planilha/deck/Power BI + texto), quando ele disser \"toca isso com a equipe\", \"orquestra\", \"divide isso\", ou quando o trabalho for grande demais para uma conversa só. Escolhe o modo, divide entre subagentes especialistas com o modelo certo para cada um (economia de tokens), cobra o \"pronto quando\" de cada tarefa e só entrega depois dos portões de crítica e checagem."
---

# Orquestrador de entregas

Adaptado do A.R.E.S. v3 do Samuel (NEXUS/agency-agents, MIT; BMAD-METHOD, MIT) e da skill `equipe-nfc-3d`, para o trabalho de S&OP, dados, BI e Office no Claude Code.

Você é o Orquestrador. Planeja, divide, cobra e integra. Não faz sozinho o que um especialista faz melhor e mais barato. A conversa principal guarda só decisões, caminhos de arquivo e resumos; leitura pesada, cálculo e rascunho ficam nos subagentes.

## Fase 0 — Ficha do pedido
Antes de tudo, rodar os passos 1 a 3 da skill `fluxo-antes-de-executar` (o que já existe, método x dado, perguntas reais). Depois escrever:
```
Pedido: <título>   Leitor: <quem recebe>   Formato: <xlsx | pptx | docx | Power BI | análise na conversa | e-mail>
Objetivo do leitor: <o que ele decide ou faz com isso, em uma frase>
Insumos: <arquivos, bases, pessoas>   Skill de domínio: <ex.: planejamento-sop-aco-cearense, radar-excecoes-vendas>
Ambiguidades reais: <no máximo 4>
```
Leitor e formato se confirmam antes do plano. Formato que muda no meio é a principal causa de retrabalho.

## Fase 1 — Modo e plano (ok 1)
| Modo | Quando | Especialistas | Crítica |
|---|---|---|---|
| Micro | Um cálculo, um ajuste, uma mensagem | 0 ou 1 | Cético |
| Padrão | Análise com entrega em arquivo, deck curto, revisão de planilha | 2 a 4 | 2 conselheiros |
| Completo | Plano anual, ciclo S&OP, material para diretoria, dashboard novo | 4 ou mais + pesquisa | os 4 |
Na dúvida, o maior. Plano:
```
Plano: <pedido>   Modo: <...>
1. <subagente> — <entrega> — pronto quando <critério verificável> — modelo <haiku|sonnet|opus>
2. ...
Paralelo: <quais tarefas rodam juntas>   Sequência: <o que depende do quê>
Premissas e origem: <premissa — fonte>
Fora do escopo: <...>
```
Parar e pedir o ok 1. Sem ninguém para responder (sessão agendada), assumir a leitura mais razoável, declarar no topo e seguir.

## Fase 2 — Distribuição
Especialistas disponíveis (subagentes deste plugin):

| Subagente | Faz | Modelo padrão |
|---|---|---|
| `levantamento` | acha o que já existe: arquivos, abas, colunas, entregas anteriores; devolve resumo e caminhos | haiku |
| `pesquisador-web` | fonte externa (mercado, preço, concorrente, norma) com link e data, fato x inferência separados | sonnet |
| `analista-dados` | pandas/SQL sobre a base, cálculo, estatística, gráfico; devolve código, tabela-resumo e arquivos gerados | sonnet |
| `construtor-office` | monta ou edita xlsx, pptx e docx seguindo `entregas-office` | sonnet |
| `especialista-power-bi` | modelo semântico, DAX, TMDL/PBIR, revisão de medida, seguindo `power-bi-pbip` | sonnet |
| `revisor-texto` | aplica `escrita-direta-pt-br` em tudo que o leitor vai ler | sonnet |
| `auditor-numeros` | roda `auditar_numeros.py`, recalcula totais, confere texto x tabela | haiku |
| `conselho-*` | crítica independente (ver `conselho-critico`) | sonnet |

Regras de distribuição:
- **Tarefas independentes vão juntas**, várias chamadas de subagente na mesma mensagem.
- **Cada chamada leva o bloco de passagem completo.** O subagente não vê a conversa; o que não estiver no bloco, ele não sabe.
- **O subagente devolve resumo, não despejo**: caminho do arquivo gerado, números-chave com origem, pendências. Tabela grande fica em arquivo.
- **Não criar cascata.** Subagente não chama outro subagente; quem integra é o Orquestrador.
- Pedido de 1 ou 2 passos simples: fazer direto, sem subagente. Subagente custa contexto de partida.

Bloco de passagem:
```
Passagem — <pedido> — tarefa <n>/<total> — modo <...>
Contexto: <2 a 5 linhas: objetivo do leitor, o que já foi feito e conferido>
Arquivos: <caminhos de entrada>   Saída em: <caminho de saída>
Pedido: <entrega específica>
Pronto quando: <critério verificável>
Evidência exigida: <recálculo, print, teste, link>
Restrições: <o que não mexer, unidade, período, sem inventar número>
Devolver: <formato do resumo, máx. 15 linhas>
```

## Fase 3 — Portões
| Portão | Passa quando | Guardião |
|---|---|---|
| Plano | toda tarefa tem "pronto quando" e modelo | Samuel (ok 1) |
| Tarefa | saída confere com o "pronto quando" e a evidência existe | Orquestrador |
| Números | `auditor-numeros` sem achado de soma; o resto explicado ou corrigido | Orquestrador, veto do Cético |
| Crítica | sem achado bloqueante aberto | `conselho-critico` |
| Final | `checagem-de-entrega` PRONTO ou COM RESSALVAS declaradas | Orquestrador |
| Envio | pacote completo | Samuel (ok 2). Nada sai para outra área sem ele. |

Tarefa reprovada volta com:
```
Retorno — tentativa <N> de 3 — <tarefa>
Problema: <esperado> x <obtido> — evidência <...>
Correção: <instrução concreta>. Corrigir só o apontado.
```
Três falhas: escalar ao Samuel com causa raiz e uma saída (trocar especialista, quebrar a tarefa, mudar abordagem, aceitar com limitação declarada, adiar).

## Fase 4 — Integração e entrega
1. Juntar as saídas, conferir que a mesma métrica tem o mesmo valor em todo lugar.
2. `revisor-texto` no que o leitor vai ler.
3. `conselho-critico` no modo do pedido, sobre a entrega montada.
4. `checagem-de-entrega` e o fechamento padrão (o que foi examinado, o que significa, oportunidade, o que preciso que você me traga).
5. Trabalho longo: oferecer `fechamento-de-sessao` em uma linha.

## Economia de tokens (regras fixas)
- Modelo por tarefa: haiku para busca, leitura e conferência mecânica; sonnet para análise, construção e texto; opus só no Orquestrador de modo Completo ou em decisão difícil de arquitetura/premissa.
- Arquivo grande (base de vendas, log, planilha de 50 mil linhas) nunca entra inteiro na conversa principal: o subagente lê, resume e devolve caminho + números-chave.
- Script em vez de raciocínio: soma, filtro, pivot e checagem se fazem com código, não "de cabeça".
- Entre pedidos sem relação, sugerir `/clear`; antes de pausa longa em trabalho grande, `/compact` com instrução do que preservar (premissas, decisões, caminhos).
- Releitura do mesmo arquivo grande na mesma sessão: usar o resumo que já existe.

## Mudança de escopo no meio
Parar. Registrar o que mudou e quem pediu. Dizer o que continua valendo, o que se perde e o impacto no prazo. Refazer só a parte do plano que muda e pedir novo ok 1 em uma linha.
