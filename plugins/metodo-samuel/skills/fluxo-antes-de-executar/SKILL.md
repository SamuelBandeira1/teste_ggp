---
name: "fluxo-antes-de-executar"
description: "Use SEMPRE que o Samuel pedir planejamento, análise, plano, orçamento, cenário, relatório, planilha, deck, documento, dashboard ou qualquer trabalho com várias etapas ou decisões, mesmo sem ele pedir \"proposta\" e mesmo em pedido por áudio (\"monta\", \"faz uma análise\", \"me ajuda com\"). Checa o que já existe, separa método de dado, pergunta o ambíguo e traz a estrutura macro para aprovar antes de executar."
---

# Fluxo antes de executar

Objetivo: evitar retrabalho. Entregar direto o detalhe em trabalho com várias camadas de decisão é a principal causa de refação para o Samuel, então a ordem abaixo é fixa.

## 1. Ver o que já existe

Antes de criar qualquer coisa, checar o que já cobre o pedido: skills, arquivos do projeto, memória, conversas e entregas anteriores.

- Se algo cobre, reaproveitar o **método** (ordem de trabalho, estrutura, critério), nunca o número.
- Se nada cobre e a tarefa é recorrente, sinalizar que vale criar uma skill nova em vez de forçar uma que não encaixa.
- Se existir skill específica da área (ex.: planejamento-sop-aco-cearense), ela manda no detalhe do processo. Esta skill cuida só da ordem geral.
- Busca em rodadas: se a primeira busca não achar, refinar os termos (sinônimo, nome do arquivo, pessoa, período) e buscar de novo, até 3 rodadas, antes de concluir que não existe.
- No Claude Code, quando a busca for em muitas pastas ou arquivos grandes, delegar ao subagente `levantamento` (modelo leve) e trazer só o resumo para a conversa principal.

## 2. Separar método de dado

- **Método** permanece: estrutura, ordem, critério de qualidade, o que a equipe rejeita.
- **Dado** morre no fim de cada rodada: valor, meta, premissa, decisão, volume, quem aprovou.
- Valor de ciclo anterior que aparecer no contexto (memória, conversa antiga, arquivo do ano passado) é referência histórica, nunca premissa. Para usar, perguntar: "isso ainda vale nesta rodada?".
- Nenhum número entra no trabalho sem origem declarada nesta rodada (arquivo, fala ou decisão).

## 3. Perguntar antes de assumir

Perguntar só quando a ambiguidade for real: premissa não definida, escopo incerto, dado que pode ter mudado desde a última vez.

- Perguntas objetivas, em bloco curto, no máximo 4.
- Em pesquisa ou busca de informação, começar a buscar de imediato e perguntar junto ou depois dos primeiros resultados.
- O Samuel usa muito voz para texto: se uma palavra ou número parecer erro de transcrição, confirmar em vez de adivinhar.

## 4. Proposta macro para aprovação

Antes do detalhe, trazer só a estrutura, neste formato:

```
Proposta macro: <nome do trabalho>
- Objetivo: <o que a entrega resolve>
- Partes/etapas: <1..n, ex.: mês a mês, seção a seção>
- Premissas e origem: <premissa — de onde vem>
- Fontes: <arquivos, sistemas, pessoas>
- Fora do escopo: <o que não será feito>
- Preciso que você confirme: <perguntas pendentes>
```

Parar e esperar a aprovação. Não pular direto para a entrega final.

## 5. Executar e entregar

- Processar o detalhe só depois do ok. Se o escopo mudar no meio, voltar ao passo 4.
- Trabalho com 3 ou mais tarefas de naturezas diferentes (dados + texto + deck, por exemplo): seguir a skill `orquestrador` para dividir entre especialistas.
- Antes de apresentar como final, rodar a skill `checagem-de-entrega`.
- Todo texto segue a skill `escrita-direta-pt-br`.
- Ao concluir um trabalho longo e aprovado, oferecer em uma linha a skill `fechamento-de-sessao`.

## Quando executar direto

Pedido simples e claro (uma conta, uma edição pontual, pergunta factual) não precisa de macro. Em sessão agendada ou sem ninguém acompanhando, assumir a interpretação mais razoável, declarar no topo e seguir.

## Registro do racional

Quando o Samuel tomar uma decisão que foge da lógica pura (matemática, estatística, o "óbvio"), registrar o porquê junto com a decisão, no próprio material. Isso evita reexplicar o contexto depois.