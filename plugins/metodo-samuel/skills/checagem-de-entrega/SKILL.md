---
name: "checagem-de-entrega"
description: "Use SEMPRE antes de apresentar como final qualquer análise, plano, planilha, relatório, deck, dashboard, e-mail ou documento com números, premissas ou conclusões, mesmo que o Samuel não peça revisão. Roda checagem própria (soma, contradição, origem, ordem de grandeza, números redondos, tom, fonte externa) e fecha a análise com impacto de negócio e \"o que preciso que você me traga\"."
---

# Checagem de entrega

Entrega com número errado, redondo demais ou contraditório passa a impressão de trabalho malfeito na equipe do Samuel. Rodar a checagem abaixo antes de apresentar algo como final. Corrigir o que falhar e rodar de novo. Na resposta, reportar só o que importa, sem listar cada item verificado.

## Checagem

1. **Soma bate.** Totais iguais à soma das partes, percentuais fecham. Quando houver tabela ou planilha, recalcular por código em vez de conferir de cabeça. Atalho para planilha ou CSV: `python <pasta desta skill>/scripts/auditar_numeros.py <arquivo>` aponta soma que não fecha, número redondo, valores repetidos em sequência e saltos acima de 25% (no Claude Code via plugin, a pasta é `${CLAUDE_PLUGIN_ROOT}/skills/checagem-de-entrega`).
2. **Período e escala.** Horizonte certo, meses completos, sem período faltando ou duplicado. Unidade consistente (t x mil t, R$ x R$ mil).
3. **Ordem de grandeza.** Comparar com o histórico ou uma referência. Variação que foge do padrão histórico precisa de explicação escrita.
4. **Nada contraditório.** O texto diz o que a tabela mostra. A mesma métrica tem o mesmo valor em todos os lugares do material.
5. **Origem rastreável.** Todo número tem fonte (arquivo, aba, data, pessoa) ou está marcado como premissa. Nenhum valor de rodada anterior usado como premissa sem confirmação nesta rodada.
6. **Cara de bem planejado.** Sem números redondos sem justificativa, sem meses ou períodos com valores idênticos, sem saltos abruptos sem explicação. A curva deve sair "torta" por construção, com a lógica que a gerou. Se algo redondo for intencional, dizer o porquê.
7. **Divergência entre fontes.** Apresentar como pergunta aberta sobre o critério ("qual foi o corte?"), nunca como erro ou lacuna de quem montou.
8. **Número que contraria decisão já tomada.** Registrar que a decisão pode ter razão comercial ou contratual fora da margem e sugerir checagem, sem invalidar a decisão.
9. **Tom, se o material vai para outras áreas.** Consultivo, não afirmativo.

## Checagem extra quando há fonte externa

Vale para mercado, concorrente, preço de aço, câmbio, notícia, relatório setorial ou qualquer dado que não veio de arquivo interno.

10. **Fato, inferência e recomendação separados.** O leitor tem que saber o que é dado, o que é leitura do dado e o que é sugestão.
11. **Toda afirmação importante tem fonte**, com data. Dado antigo é sinalizado como antigo.
12. **Estimativa rotulada como estimativa**, com a lógica de cálculo.
13. **Evidência contrária.** Antes de concluir, procurar o que contradiz a conclusão e citar se existir.

## Resultado

Classificar internamente como PRONTO, COM RESSALVAS ou NÃO PRONTO.

- NÃO PRONTO: corrigir e rodar a checagem de novo antes de mostrar.
- COM RESSALVAS: listar as ressalvas na entrega, em 1 a 3 linhas.
- PRONTO: entregar sem comentar a checagem.

## Fechamento de toda análise

Toda análise termina com esta estrutura, mesmo em conversa e não só em documento formal:

1. **O que foi examinado e por quê.**
2. **O que significa**, em impacto de negócio (em número, quando possível).
3. **Qual a oportunidade.**
4. **O que preciso que você me traga.** Os questionamentos e dados pendentes, organizados de forma direcionada (por pessoa, área ou fonte), para o Samuel saber exatamente o que buscar e devolver antes de seguir.

Proporcional ao tamanho: em resposta curta ou pergunta pontual, o fechamento vira 1 a 3 linhas (o que significa e, se houver pendência, o que preciso que você me traga). Estrutura completa só em análise de verdade.

Se houve decisão fora da lógica pura, registrar o racional junto.

Títulos de seção sempre descritivos ("Cobertura de capacidade por linha"), nunca poéticos.