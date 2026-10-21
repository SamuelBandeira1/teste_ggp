---
name: "conselho-critico"
description: "Use antes de entregar criação, proposta, site, orçamento ou plano, e quando o Samuel perguntar \"isso está bom mesmo?\", \"critica isso\", \"avalia esse projeto\" ou \"testa essa ideia\"."
---

# Conselho Crítico

Adaptado do A.R.E.S. v3 do Samuel, a partir do bmad-review e do Reality Checker (BMAD-METHOD, MIT, BMad Code, LLC; agency-agents, MIT, AgentLand Contributors).

O Conselho parte do "não pronto" e precisa ser convencido pela evidência. Nota perfeita vinda de quem fez o trabalho é sinal de alerta, não de qualidade.

## Modos
| Modo | Conselheiros | Mínimo de achados brutos |
|---|---|---|
| Micro | Cético | 3 |
| Padrão | 2, pela tabela abaixo | 6 |
| Completo | os 4 | 10, com pelo menos um terço sobre o que falta |
| Testar ideia | Advogado do Diabo + Visão de Fora | 6, focados no ponto mais fraco da ideia |
Achado sem evidência não conta para o mínimo. Se chegar a zero, procurar de novo antes de aceitar.

Escolha no modo padrão: proposta e orçamento → Cético + Advogado; site, página ou visual → Lente do Cliente + Cético; plano ou ideia nova → Advogado + Visão de Fora; mensagem → Lente do Cliente + Advogado.

## Conselheiros
**Cético — "cadê a prova?"** Recalcula 3 números (preço, margem, quantidade, medida). Rastreia 3 afirmações até a origem. Para tudo que diz "funciona", pergunta: "se isto estivesse errado, alguma conferência pegaria?" e diz até onde procurou. Em site: abriu no navegador? testou no celular? clicou nos botões? Tem veto único sobre número e preço.

**Advogado do Diabo — "por que isso vai dar errado?"** Pre-mortem: supõe que o cliente recusou ou que a entrega deu problema daqui a 1 mês e lista as causas mais prováveis. Escreve a melhor versão do argumento contrário. Pergunta o efeito de segunda ordem (prazo do Ricardo, custo escondido, promessa que não se cumpre).

**Visão de Fora — "por que estamos fazendo assim?"** Volta ao objetivo do cliente em uma frase e checa se a entrega é o caminho mais curto até ele. Compara com 3 referências de mercado. Propõe 2 alternativas radicais (uma 10x mais simples) e o teste barato que provaria cada uma.

**Lente do Cliente — "quem recebe entende e age?"** Lê só a primeira tela por 30 segundos, como o cliente final com pressa no celular. Diz o que ficou entendido x o que precisava. Lista as 3 perguntas que esse leitor faria e se a entrega já responde. Confere se o próximo passo (chamar no WhatsApp, pedir orçamento, agendar) é óbvio. Marcador interno visível ("[confirmar]", "[[CAMPO]]") ou visual sem nada próprio do negócio são achados, mesmo que o resto funcione.

## Como rodar
1. Escrever o critério de sucesso do pedido em uma linha.
2. Cada conselheiro escreve a crítica **inteira antes de ler a do próximo**.
   - **No Claude Code:** rodar cada conselheiro como subagente separado, em paralelo, numa única mensagem (`conselho-cetico`, `conselho-advogado`, `conselho-visao-de-fora`, `conselho-lente-do-cliente`). Passar a cada um só o critério de sucesso, o caminho dos arquivos da entrega e o modo; nunca a crítica dos outros. Isso dá independência real e mantém a leitura dos arquivos fora do contexto principal.
   - **No Claude web (sem subagentes):** esta ordem sequencial é o substituto da independência real.
3. Rodada bruta: todos os achados, no formato abaixo, incluindo o que falta (omissão), não só o que está errado.
4. Convergência: achado apontado por dois conselheiros é sinal mais forte, não repetição. Marcar.
5. Priorizar e reportar os 7 mais severos na tabela; o resto vai num anexo de uma linha cada.
6. Veredito.

Formato de cada achado:
`Onde | Problema em uma linha | Evidência | Consequência se sair assim | Correção concreta | Esforço (baixo, médio, alto) | Bloqueante? (sim/não)`

## Veredito
- **NÃO PRONTO:** existe achado bloqueante. Volta para a equipe com o retorno padrão (tentativa N de 3, corrigir só o apontado).
- **COM RESSALVAS:** sem bloqueante, mas com ressalvas que o Samuel precisa saber; listar em 1 a 3 linhas na entrega.
- **PRONTO:** entregar sem comentar a crítica.

Fechar dizendo até onde o Conselho procurou e o que ficou sem verificar.