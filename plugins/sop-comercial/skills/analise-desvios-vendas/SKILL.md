---
name: analise-desvios-vendas
description: "Use este skill SEMPRE que o usuário quiser analisar desvios de vendas, comparar realizado vs. previsão, entender por que uma linha de produto ou região está abaixo/acima do planejado, gerar relatório de performance comercial, identificar causas de variação entre vendas e forecast, ou quando o usuário fizer upload de arquivos de vendas e/ou previsão pedindo qualquer análise de performance. Triggers: 'analise os desvios', 'compare realizado vs previsão', 'por que a linha X caiu', 'relatório de performance', 'quais produtos estão desviando', 'análise mensal de vendas', 'quem está comprando', 'concentração de clientes', 'análise de mix', 'evolução de vendas'."
---

# Agente de Análise de Desvios de Vendas

## Objetivo

Analisar bases de dados de vendas e previsão para identificar causas reais dos desvios de desempenho, com foco em gerar insights profundos, sinais ocultos e recomendações táticas para o time comercial.

---

## PASSO 0 — Onboarding Obrigatório (SEMPRE fazer antes de começar)

Antes de qualquer análise, fazer duas perguntas ao usuário:

**Pergunta 1 — Foco da análise:**
> "Qual nível de detalhe você quer no foco principal do relatório? (Você pode escolher mais de um)"
> 1. Visão geral macro (diagnóstico executivo + todas as dimensões)
> 2. Linha de produto / Mix (Grupo × Espessura)
> 3. Região / Estado / Gerência
> 4. Clientes (concentração, novos, em risco, crescimento)
> 5. Segmento de mercado (Construção Civil, Distribuição, Indústria...)
> 6. Análise completa (todas as dimensões acima)

**Pergunta 2 — Período de referência:**
> "Qual mês quero analisar como 'mês atual'? (Ex: Mai/2026 — deixe em branco para usar o último mês com dados)"

Aguardar as respostas antes de prosseguir. O foco escolhido determina quais seções aprofundar.

---

## Estrutura das Bases de Dados

### Tabela Vendas (Micro — nível mais granular)
| Coluna | Descrição |
|---|---|
| `descricao_linha` | Linha de produto (ex: Tubo, CA-50, Tela) |
| `descricao_grupo` | Grupo/SKU dentro da linha |
| `descricao_espessura` | Espessura do produto |
| `descricao_parceiro_master` | Cliente — **exclusivo desta tabela** |
| `descricao_segmento_mercado` | Segmento do cliente — **exclusivo desta tabela** |
| `descricao_fornecedor` | Fornecedor — **exclusivo desta tabela** |
| `descricao_gerencia_2` | Gerência comercial responsável |
| `descricao_empresa_3` | Empresa (ex: AC's, SIN) |
| `descricao_estado` | Estado (UF) |
| `numero_ano_mes` | Período YYYYMM |
| `Venda Vol` | Volume vendido em toneladas |

### Tabela Previsão (Macro — sem cliente/fornecedor)
| Coluna | Descrição |
|---|---|
| `descricao_linha` | Linha de produto |
| `descricao_grupo` | Grupo/SKU |
| `descricao_espessura` | Espessura |
| `descricao_gerencia_2` | Gerência comercial |
| `descricao_empresa_3` | Empresa |
| `descricao_estado` | Estado (UF) |
| `numero_ano_mes` | Período YYYYMM |
| `Previsão Vol` | Volume previsto em toneladas |

---

## Regra Crítica de Granularidade

### Regra 1 — Agregação Bottom-Up para Comparação
**Chave de join obrigatória:**
```
numero_ano_mes + descricao_empresa_3 + descricao_linha +
descricao_grupo + descricao_espessura + descricao_estado + descricao_gerencia_2
```
Nunca cruzar `descricao_parceiro_master` / `descricao_segmento_mercado` / `descricao_fornecedor` com a previsão.

### Regra 2 — Drill-Down para Causa Raiz
1. Identificar ONDE está o desvio no nível macro (join com previsão)
2. Abrir detalhes de vendas para explicar o PORQUÊ (cliente, segmento, fornecedor)

---

## PASSO 1 — Executar Script de Análise

```bash
# <caminho_do_skill> = pasta desta skill. No Claude Code via plugin: ${CLAUDE_PLUGIN_ROOT}/skills/analise-desvios-vendas
python <caminho_do_skill>/scripts/analisar_desvios.py \
  --vendas "<caminho_vendas>" \
  --previsao "<caminho_previsao>" \
  --output "<output>/analise_resultado.json"
```

Ler o JSON completo antes de escrever qualquer insight. Se o script falhar, fazer os cálculos com pandas seguindo as regras de granularidade.

---

## PASSO 2 — Construir o Relatório Word

Carregar a skill `docx` pelo nome (no Claude Code vem do plugin `document-skills@anthropic-agent-skills`; no claude.ai já é embutida) e seguir também `entregas-office`.

### Estrutura Completa do Relatório

O relatório deve ter exatamente estas seções, com profundidade ajustada ao foco escolhido pelo usuário:

---

### Seção 1 — Indicadores-chave (sempre incluir)

Tabela de KPIs no topo do relatório:

| Indicador | Leitura |
|---|---|
| Plano do mês | X t |
| Realizado | X t |
| Atingimento | X% |
| Clientes ativos no mês | N |
| Top 1 / Top 5 / Top 10 | X% / Y% / Z% |
| Clientes novos no mês | N clientes / X t |
| HHI de concentração | 0,0XX (baixo/moderado/alto) |
| Desvio acumulado (meses realizados) | X t (Y%) |

**HHI:** índice de concentração de mercado. Abaixo de 0,10 = pulverizado; 0,10–0,18 = moderado; acima de 0,18 = concentrado.

---

### Seção 2 — Diagnóstico Executivo (sempre incluir)

- Tabela mensal: Previsto | Realizado | Desvio Abs | Desvio % | Clientes ativos
- Gráfico de barras (descrever os dados para o docx): volume por mês vs. linha de plano mensal
- Veredito em 3-5 bullets: quais foram os principais motivadores macro? Qual o "sinal escondido" do mês?

**O "sinal escondido" é o padrão não óbvio:** ex. 44% do volume veio de clientes sem histórico; uma única linha representa 70% do desvio; desvio geográfico concentrado em 2 estados, etc. Sempre buscar e nomear esse sinal.

---

### Seção 3 — Concentração e Pulverização (sempre incluir)

- Breakdown: Top 1 / Top 5 / Top 10 / Top 20 / Top 50 clientes = X% do volume
- HHI calculado
- Tabela Top 20 clientes: Nome | Segmento | Status (Novo/Recorrente/Reativado) | Volume (t) | Share %
- Interpretação: o mercado está pulverizado ou concentrado? Qual é o risco de dependência?

---

### Seção 4 — Mix de Produto: Grupo × Espessura (incluir se foco = Linha/Produto ou Geral)

- Ranking das combinações Grupo×Espessura por volume: Grupo | Espessura | Volume (t) | Share % | N° Clientes
- Identificar combinações dominantes e anomalias (ex: uma espessura com pouquíssimos clientes e alto volume = risco de concentração)
- O que os Top 15 clientes compraram em detalhe (top 3 combinações por cliente)

---

### Seção 5 — Segmentos de Mercado (incluir se foco = Segmento ou Geral)

- Tabela: Segmento | Volume (t) | Share % | N° Clientes
- Evolução do mix de segmentos entre meses (qual segmento cresceu/caiu?)
- Identificar se há migração de segmento (ex: Distribuição cedendo espaço para Construção Civil)

---

### Seção 6 — Raio-X Geográfico (incluir se foco = Região ou Geral)

- Tabela: Estado | Realizado | Previsto | Desvio Abs | Desvio % | Clientes ativos
- Top 5 estados com maior desvio positivo e negativo
- Análise por gerência: Comercial I | Comercial II | Comercial Inox
- Identificar concentração geográfica: desvio de UF inteira concentrado em 1-2 clientes?

---

### Seção 7 — Comportamento de Clientes (incluir se foco = Clientes ou Geral)

**7a. Top 10 clientes do mês:**
Tabela: Cliente | Segmento | Status | Volume (t) | Share % | Vs. mês anterior | Vs. média histórica

**7b. Clientes novos (sem histórico nos meses anteriores):**
- Quantos são e quanto representam do volume total
- Top 15 novos: Nome | Segmento | Volume (t) | Share %
- São obra pontual, reativação ou novo canal?

**7c. Crescimento dos recorrentes:**
Tabela: Cliente | Volume mês atual | Média histórica | Incremento (t) | Crescimento %
Ordenar por incremento absoluto (não por %).

**7d. Clientes em risco de churn:**
Compraram no mês anterior e zeraram: Nome | Volume anterior | Dias sem compra

**Status dos clientes:**
- **Novo**: sem nenhuma compra nos meses anteriores do arquivo
- **Reativado**: comprou há 2+ meses, ficou ausente pelo menos 1 mês, voltou
- **Recorrente**: comprou em pelo menos um mês anterior consecutivo

---

### Seção 8 — Projeção e Plano de Ação (sempre incluir)

- Run-rate do mês atual e projeção de fechamento
- Gap vs. meta
- **Tabela de recomendações priorizadas:**

| # | Ação | Alvo (cliente/região/produto) | Volume potencial (t) | Prioridade |
|---|---|---|---|---|
| 1 | [ação específica e acionável] | [nome do alvo] | [estimativa] | Alta |

As recomendações devem ser específicas e nomear clientes, linhas ou regiões reais dos dados.

---

### Seção 9 — Alertas e Anomalias (sempre incluir)

- Combinações de vendas sem previsão correspondente
- Previsões sem nenhuma realização
- Clientes com desvio extremo (>+200% vs. histórico)
- Dados faltantes ou inconsistentes

---

### Apêndice Metodológico (sempre incluir)

Definir claramente:
- Critério de classificação (Novo / Recorrente / Reativado)
- Como foi calculado o HHI
- Período de histórico usado para comparação
- Qualquer ajuste ou ressalva sobre os dados

---

## Diretrizes de Narrativa

O relatório deve ter **voz analítica**, não apenas listar tabelas. Para cada seção:
- Abrir com 1-2 frases de interpretação antes de apresentar dados
- Nomear o achado principal ("O sinal mais importante aqui é...")
- Fechar com implicação prática ("Isso sugere que...")

**Formatos:**
- Volumes: X.XXX,X t (ponto para milhar, vírgula para decimal)
- Percentuais: +X,X% ou -X,X% (sempre com sinal)
- Ordenar por magnitude absoluta, não percentual
- Evitar afirmações vagas — todo insight deve citar o número que o sustenta

## Solicitação de Arquivos

Se os arquivos não foram fornecidos, solicitar:
1. `tabela_vendas.xlsx` — base de vendas realizadas
2. `tabela_previsao.xlsx` — base de previsão/forecast

Se apenas vendas forem fornecidas: realizar análise de demanda histórica + concentração + mix + comportamento de clientes, e avisar que o comparativo vs. previsão não é possível.
