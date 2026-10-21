---
name: fechamento-de-sessao
description: "Use ao fim de um trabalho longo ou aprovado, quando o Samuel disser \"fecha a sessão\", \"registra isso\", \"salva o checkpoint\", \"onde paramos\", ou quando ele voltar a um trabalho antigo e pedir para retomar. Registra decisões com racional, premissas com origem, pendências por pessoa e armadilhas aprendidas num CHECKPOINT do projeto, para a próxima sessão começar sem retrabalho e sem carregar número velho como premissa."
---

# Fechamento de sessão

Objetivo: a próxima sessão começa do ponto certo, em poucos tokens, sem reler tudo e sem herdar número de rodada anterior como se fosse premissa.

## Quando rodar
- Fim de trabalho longo ou aprovado (oferecido em uma linha pela `fluxo-antes-de-executar` ou pelo `orquestrador`).
- Antes de `/clear` ou de pausa longa num trabalho que vai continuar.
- Na volta: "onde paramos?" → ler o CHECKPOINT e resumir em até 8 linhas antes de qualquer outra coisa.

## Onde gravar
1. Se o projeto já tem `CHECKPOINT.md` (raiz ou pasta `Contexto/`), atualizar esse.
2. Se não tem, criar `CHECKPOINT.md` na raiz do projeto.
3. Sem pasta de projeto (conversa solta), entregar o bloco na resposta para o Samuel colar onde guarda.

Nunca gravar senha, token, dado pessoal de cliente ou número sensível de ciclo dentro de skill ou de CLAUDE.md. Número de ciclo fica no arquivo do ciclo.

## Formato (acrescentar no topo; manter o histórico abaixo)
```
## <AAAA-MM-DD> — <trabalho>
Estado: <concluído | em andamento: etapa X de Y | bloqueado por ...>
Entregas: <caminho do arquivo — o que é>

Decisões (com racional)
- <data> | <quem decidiu> | <o que> | <lógica contrariada, se houver> | <motivo prático>

Premissas desta rodada (morrem no fim do ciclo)
- <premissa> — origem: <arquivo/aba/pessoa/data> — status: travada | aberta

Pendências — o que preciso que você me traga
- <pessoa ou área>: <pergunta ou dado>

Próximo passo: <uma ação concreta>
Armadilhas aprendidas: - <o que deu errado> → <regra para não repetir>
```

## Regras
- Curto: o bloco do dia cabe em uma tela. Detalhe fica nos arquivos de entrega; o checkpoint aponta para eles.
- Decisão fora da lógica pura sempre leva o racional. É o que evita "por que fizemos isso mesmo?" no ciclo seguinte.
- Armadilha que se repetiu duas vezes vira proposta de ajuste na skill do processo (mostrar o trecho novo para o Samuel aprovar; não editar skill sozinho).
- Tarefa recorrente sem skill que cubra: sugerir em uma linha criar uma skill nova com `skill-creator`.
- Ao retomar, tratar número do checkpoint como referência histórica e perguntar "isso ainda vale nesta rodada?" antes de usar como premissa.
