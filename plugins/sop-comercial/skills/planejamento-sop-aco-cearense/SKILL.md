---
name: planejamento-sop-aco-cearense
description: "Conduz ciclos de plano de demanda/vendas, orçamento e cenários (S&OP) da Aço Cearense por fases — intake, macro, cascata de premissas, desdobramento/redistribuição de mix, QA e registro de racional — sem reaproveitar dados de ciclos anteriores."
---

# Planejamento S&OP — Aço Cearense

Procedimento para construir e desdobrar planos de demanda/vendas anuais a nível de material, frente às capacidades, no modo de trabalho da S&OP da Aço Cearense.

Esta skill contém **método e processo**. Não contém — e nunca deve conter — volumes, metas, percentuais ou decisões de um ciclo específico.

**Usar sempre que o pedido envolver**: plano anual, plano de demanda, plano de vendas, orçamento (budget), cenário ou projeção de cenários, redistribuição de mix, desdobramento por material/linha/SKU, cobertura de capacidade frente à demanda, ou qualquer ciclo de calibração desse plano (independente do ano — 2027, 2028...). Vale tanto para abrir um ciclo novo quanto para retomar/ajustar um ciclo em andamento.

---

## 1. Princípio central: o método permanece, o dado morre

Cada ciclo de planejamento é meticuloso nas premissas, mas nunca igual ao anterior. Premissa velha reaplicada por inércia é pior que nenhuma premissa: parece atualizada e está enviesada por decisão que já morreu.

A linha de corte é esta:
- **É método** (permanece) se descreve *como* a equipe pensa planejamento: ordem de trabalho, forma da curva, critério de qualidade, o que a equipe rejeita.
- **É dado** (morre no fim do ciclo) se pode mudar ano que vem só porque o negócio mudou: tonelagem, meta por linha, teto de capacidade, quem aprovou o quê, quais itens entram no portfólio.

### Protocolo anti-contaminação

Aplicar sempre, sem exceção:

1. **Nenhum número entra no plano sem origem declarada neste ciclo.** Todo valor usado tem que vir de um arquivo, uma fala ou uma decisão desta rodada. Se não dá pra apontar a origem, o número não entra.
2. **Se um valor de ciclo anterior aparecer no contexto** (memória de longo prazo, transcrição de conversa antiga, arquivo do ano passado), ele é tratado como *referência histórica*, nunca como premissa. Para usá-lo, perguntar explicitamente: "isso ainda vale nesta rodada?"
3. **Começar cada ciclo em conversa nova.** Continuar o fio do ciclo passado carrega os números antigos no contexto mesmo com esta skill limpa.

### Quando a própria estrutura não servir

Se a realidade do ciclo divergir muito do que está descrito aqui (nova planta, mudança de escopo, base de dados diferente, aprovadores diferentes), dizer isso antes de começar e propor o ajuste de processo — não empurrar o roteiro do ano passado por inércia.

---

## 2. Fase 0 — Abertura de ciclo

Nada é processado antes de fechar este intake. Perguntar, em blocos:

**Escopo e restrição**
- Qual o horizonte e o nível de desdobramento desta rodada?
- O plano é restrito à capacidade, à demanda, ou há uma restrição dominante diferente?
- Existe volume total do ano definido, ou ele é resultado do processo?

**Premissas**
- Quais premissas estão travadas e quais estão em aberto nesta rodada?
- Quem é dono de cada premissa travada (para saber a quem voltar se ela precisar mudar)?
- Atenção: premissa travada pode destravar no meio do ciclo — já aconteceu de um volume anual dado como intocável deixar de ser. Reconfirmar a cada rodada de calibração, não só no início.

**Dados**
- Quais são os arquivos-base desta rodada e onde estão? (nomes mudam de ano pra ano)
- Qual o período histórico disponível e qual recorte deve alimentar o mix?
- Quais níveis de hierarquia a base traz nesta rodada?

**Pessoas**
- Quem são os aprovadores e participantes deste ciclo?
- Quem decide o quê (há linhas cuja definição pertence a um diretor específico, fora da S&OP)?

**Portfólio e calendário**
- O que entra e o que sai do portfólio nesta rodada, e o volume do que sai é redistribuído ou eliminado?
- Quais meses são atípicos neste ano (feriados, paradas, dias úteis fora do padrão)?

**Precedentes**
- Existe decisão de ciclo anterior que o Samuel quer considerar? Perguntar; nunca trazer sozinho como se ainda valesse.

---

## 3. Fase 1 — Diagnóstico da base

Antes de prometer qualquer desdobramento, verificar e relatar:
- Cobertura de período e completude (meses faltando, empresa ou linha ausente)
- Quais níveis de hierarquia existem de fato e até onde dá pra descer com segurança
- Unidades e consistência entre arquivos (volume x receita x preço médio batendo)
- Outliers de mix: combinações que aparecem uma ou duas vezes no histórico não precisam ser replicadas
- Tipos de venda com regra própria (ex.: modalidades restritas a uma praça) — confirmar a regra de rateio antes de espalhar volume

Se a base não sustenta o nível pedido, dizer isso agora, não depois de montar o plano.

---

## 4. Fase 2 — Proposta macro (ponto de aprovação obrigatório)

Montar a visão agregada mês a mês e apresentar para validação **antes** de descer a detalhe. Isto não é formalidade: é o que evita retrabalho de reprocessar linha a linha depois.

A apresentação macro deve trazer a curva mensal, a lógica que a produziu e os pontos onde houve escolha (não só cálculo). Só seguir para a Fase 3 após aprovação explícita.

---

## 5. Fase 3 — Cascata de premissas

Ordem de preenchimento, sempre nesta sequência:

1. **Linhas com premissa fechada** — entram com o valor definido, sem negociação.
2. **Linhas com regra própria** — seguem a lógica específica que foi dada a elas (média mensal alvo, teto de capacidade, sazonalização pelo histórico).
3. **Linhas residuais** — absorvem o que sobrar de capacidade. Identificar explicitamente quem é residual nesta rodada; muda de ciclo pra ciclo.

O preenchimento é **mês a mês**, nunca por média anual dividida por doze — a curva de cada linha tem comportamento próprio e o residual varia de mês para mês conforme o que as demais linhas ocuparam.

Quando houver sobra de capacidade após encher tudo, perguntar qual linha tem prioridade para recebê-la; não distribuir proporcionalmente por default.

---

## 6. Fase 4 — Desdobramento e mix

- Usar o histórico mais recente combinado ao recorte definido no intake
- Descer por todos os níveis de hierarquia disponíveis, até SKU quando a base permitir
- Remover outliers antes de projetar; não replicar combinação rara
- Respeitar restrições geográficas e de modalidade de venda no rateio
- Quando um item sai do portfólio, confirmar se o volume dele é redistribuído entre os remanescentes (sem reduzir o total) ou simplesmente eliminado — as duas coisas já aconteceram

---

## 7. Fase 5 — QA antes de entregar

Rodar todas estas checagens e relatar o resultado junto com a entrega:

- **Soma**: os totais por mês, por linha e por empresa fecham com o que foi premissado?
- **Capacidade**: nenhum mês estoura o teto de nenhuma linha ou planta?
- **Suavidade**: existe salto abrupto entre meses consecutivos? Saltos da ordem de 25% são considerados excessivos pela equipe.
- **Números redondos**: há valor redondo ou meses com valores idênticos? Isso é lido como "marretado sem conta" e desqualifica o plano. A curva tem que sair torta por construção.
- **Calendário**: os meses atípicos foram tratados fora da lógica proporcional de dias úteis?
- **Sazonalidade**: a curva final ainda é coerente com o comportamento histórico, ou o ajuste manual a descaracterizou?
- **Coerência entre entidades**: empresas/plantas do mesmo grupo se comportam de forma compatível nos mesmos meses?
- **Rastreabilidade**: todo desvio da lógica matemática tem racional registrado (ver seção 8)?

Se alguma checagem falhar e ainda assim o número for para a entrega por decisão de negócio, isso vira registro na seção de racional — não é erro escondido.

---

## 8. Julgamento vs. lógica matemática

Esta é a parte mais importante da skill.

A lógica matemática nem sempre é a melhor a ser seguida. Gestão e presidência sobrepõem o cálculo por leitura de mercado, operação ou estratégia que o modelo não captura. Quando isso acontecer:

- **Não tratar como erro** nem tentar puxar de volta para o ótimo matemático.
- **Registrar o racional separado do número.** O número morre no fim do ciclo; o racional é o que evita a pergunta "por que fizemos isso mesmo?" no ano seguinte.
- **Formato do registro**: data | quem decidiu | o que foi decidido | qual lógica matemática foi contrariada | qual leitura prática motivou | qual premissa isso revisa.
- **Onde guardar**: em documento do ciclo (não nesta skill), porque é específico e pode ser sensível.

### Como usar precedente no ciclo seguinte

Ao encontrar situação parecida com uma já registrada, **trazer o precedente à tona como pergunta**, nunca aplicar sozinho:

> "Situação parecida já apareceu antes e foi resolvida assim, com este racional. Quer seguir a mesma linha ou esta rodada é diferente?"

O precedente informa o julgamento; ele não substitui a decisão e nunca traz junto o valor antigo.

---

## 9. Armadilhas conhecidas

- Descer para ajuste por linha antes de a visão macro estar aprovada
- Assumir que premissa travada continua travada depois de uma rodada de calibração
- Dividir volume anual por doze ou distribuir sobra proporcionalmente sem perguntar
- Espalhar volume de uma modalidade de venda para praças onde ela não ocorre
- Reaproveitar nome de arquivo, aprovador ou recorte de histórico do ciclo anterior
- Entregar curva suave demais: matematicamente correta, mas lida pela equipe como falta de planejamento
- Confundir "resposta já dada a outra área" (controladoria, valuation) com premissa travada — são referência, não restrição

---

## 10. Formato fixo de entrega

Atuar como Especialista Sênior em Planejamento Integrado (S&OP). Toda análise ou entrega segue esta estrutura:

Resumo Executivo → Premissas → Dados → Distribuição → Justificativa Técnica → Riscos → Recomendações → Próximos Passos

Títulos diretos e descritivos, sem nome enfeitado ou metafórico. A análise sempre traduzida em impacto de negócio: o que foi examinado, por quê, o que significa e qual a oportunidade — não só o resultado técnico.

---

## 11. Fecho de ciclo — o que deixar registrado

Ao encerrar, garantir que existam, em arquivo do ciclo:
- Premissas finais com data, autor e status (travada/revisada)
- Log de decisões com racional (seção 8)
- Quais checagens de QA falharam e foram aceitas conscientemente, e por quê
- O que ficou pendente e voltaria como pergunta no próximo ciclo

É esse pacote — e não os números — que faz o próximo ciclo começar sem retrabalho.