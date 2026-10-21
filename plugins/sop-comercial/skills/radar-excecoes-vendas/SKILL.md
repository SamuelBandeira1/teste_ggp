---
name: radar-excecoes-vendas
description: "Use este skill SEMPRE que o usuário quiser detectar o que fugiu do padrão histórico na base de vendas — anomalias, exceções de processo, comportamento fora da curva — e gerar o material para questionar o time comercial. Diferente de uma análise de desvio vs. previsão: aqui o benchmark é o próprio histórico (mediana e MAD por série). Triggers: 'o que saiu do eixo', 'o que está destoando', 'radar de exceções', 'detectar anomalia de vendas', 'o que fugiu do padrão', 'quais SKUs estão fora da curva', 'me monta o slide pra cobrar o comercial', 'algo crítico nas vendas', 'exceções do mês', 'quais clientes pararam de comprar', 'ruptura de venda', 'análise estatística de vendas', 'z-score de vendas', 'baseline histórico de venda'."
---

# Radar de Exceções de Vendas

## O que este skill faz

Varre a base de vendas em **12 níveis** (empresa, linha, grupo, SKU, estado, gerência, segmento, cliente e cruzamentos), constrói um **baseline histórico robusto** para cada série e devolve o que está fora do padrão — classificado por gravidade, com a **causa raiz** e a **pergunta a fazer ao comercial**.

Entregáveis padrão: **PPTX de reunião** + **Word executivo**.

> **Quando NÃO usar:** se o pedido for comparar realizado vs. previsão, analisar mix, concentração de clientes ou montar o relatório mensal de performance, use o skill `analise-desvios-vendas`. Este aqui é o radar de anomalias contra o histórico. Os dois se complementam e podem rodar na mesma sessão.

---

## PASSO 0 — Onboarding (sempre antes de rodar)

Fazer estas perguntas com a ferramenta de pergunta ao usuário (não em texto solto):

1. **Mês a analisar** — "Qual mês é o 'atual'? (deixe em branco para o último mês com dados)"
2. **Janela de histórico** — 12 meses (padrão) / 6 / 24 / toda a base
3. **Sensibilidade** — Equilibrada (z≥3 crítico, z≥2 atenção — padrão) / Conservadora (só o gritante: z≥4 e ≥1% do volume) / Sensível (z≥2,5 crítico, pega mais coisa)
4. **Foco do deck** — Tudo / Só macro (linha, região, gerência) / Só produto (grupo, SKU) / Só cliente

Se os arquivos não vieram, pedir:
- `tabela_vendas.xlsx` (obrigatório)
- `tabela_previsao.xlsx` (opcional — liga a camada de aderência ao forecast)

Se o usuário estiver ausente (rodada agendada), assumir: último mês, janela 12, sensibilidade equilibrada, foco tudo — e **declarar essa suposição no topo do entregável**.

---

## Estrutura esperada da base

### Vendas (granular)
`descricao_linha`, `descricao_grupo`, `descricao_espessura`, `descricao_parceiro_master`, `descricao_segmento_mercado`, `descricao_fornecedor`, `descricao_gerencia_2`, `descricao_empresa_3`, `descricao_estado`, `numero_ano_mes` (YYYYMM), `Venda Vol` (toneladas)

### Previsão (macro — sem cliente/segmento/fornecedor)
Mesmas colunas menos as três exclusivas de vendas, com `Previsao Vol`.

**Regra dura:** nunca cruzar `descricao_parceiro_master`, `descricao_segmento_mercado` ou `descricao_fornecedor` com a previsão. O script já respeita isso — desliga a camada de forecast nos níveis de cliente/segmento.

Se as colunas vierem com outros nomes, **renomear no arquivo antes de rodar** (não editar o script). Se faltar coluna, o script avisa e lista as que encontrou.

---

## PASSO 1 — Rodar o motor

```bash
# <skill_dir> = pasta desta skill. No Claude Code via plugin: ${CLAUDE_PLUGIN_ROOT}/skills/radar-excecoes-vendas
python <skill_dir>/scripts/radar_excecoes.py \
  --vendas "<caminho_vendas>" \
  --previsao "<caminho_previsao>" \
  --output radar_resultado.json \
  --csv radar_excecoes.csv \
  --mes 202606 --janela 12
```

Parâmetros de sensibilidade (ajustar conforme a resposta do PASSO 0):

| Flag | Padrão | Para que serve |
|---|---|---|
| `--z-critico` | 3.0 | z robusto que torna a exceção crítica |
| `--z-atencao` | 2.0 | z robusto que gera alerta |
| `--material-pct` | 0.5 | % do volume do mês que torna um desvio "material" |
| `--volume-minimo` | 1.0 | volume (t) abaixo do qual a série é ignorada |
| `--min-meses-ativos` | 4 | histórico mínimo para a série virar crítica |
| `--tol-previsao` | 20.0 | % de desvio vs. previsão que vira alerta |
| `--top-excecoes` | 120 | teto de exceções no JSON |

Perfis: **conservadora** → `--z-critico 4 --z-atencao 3 --material-pct 1.0`. **Sensível** → `--z-critico 2.5 --z-atencao 1.8 --material-pct 0.3`.

**Ler o JSON inteiro antes de escrever qualquer frase.** Se o script falhar, refazer os cálculos com pandas seguindo `references/metodologia.md` — não inventar números.

---

## PASSO 2 — Ler e triar o JSON

Campos que importam em cada exceção:

- `severidade`: `critico` | `atencao` | `observar`
- `camada`: `macro` | `produto` | `cliente` — define a seção do deck
- `tipo`: `ruptura`, `estreia`, `queda_sustentada`, `queda_atipica`, `pico_atipico`, `crescimento_sustentado`, `desvio_previsao`, `previsao_nao_realizada`, `venda_sem_previsao`
- `redundante_com`: **se presente, NÃO vira slide próprio.** Significa que essa linha é eco de um filho mais específico que já explica o desvio. Citar como contexto, no máximo.
- `causas`: top contribuintes por nível filho, por cliente e por segmento, com `part_do_desvio_pct`
- `pergunta_comercial`: rascunho da pergunta — **refinar com o contexto real, não copiar cru**
- `serie`: os 13 valores (histórico + mês atual) para o gráfico
- `z_robusto`, `mediana`, `p25`/`p75`, `desvio_abs`, `desvio_pct`, `meses_ativos`

**Regras de triagem para o deck:**

1. Descartar tudo com `redundante_com`.
2. Ordenar por `score` dentro de cada severidade (o script já entrega assim).
3. Selecionar **no máximo 8 exceções críticas** para slide dedicado, respeitando a proporção: até 4 de `macro`, até 2 de `produto`, até 2 de `cliente`. Se o usuário escolheu um foco, usar só aquela camada.
4. O resto vai em tabela consolidada.
5. Se `contagem.criticos` for 0, **dizer isso claramente** — mês dentro do padrão é uma conclusão legítima e valiosa. Não inflar `atencao` para preencher slide.

**Checagem obrigatória antes de escrever:** dois níveis diferentes podem descrever o mesmo fato (ex.: se cada linha de produto tem uma gerência fixa, "Linha CA-50" e "Comercial Inox" são a mesma série). O script não pega isso porque são dimensões irmãs, não pai/filho. Comparar `valor_atual` e `desvio_abs` entre as manchetes: **se dois níveis têm números idênticos, mantenha só um** e mencione que a dimensão é redundante na base.

---

## PASSO 3 — Montar o PPTX

Ler o SKILL.md do skill **pptx** antes de construir. Usar os dados de `serie` para os gráficos.

### Estrutura do deck

**Slide 1 — Capa**
`Radar de Exceções de Vendas` · mês analisado · janela de histórico · data de geração.

**Slide 2 — Como ler este material**
Três frases, sem jargão: (a) o benchmark é a mediana dos últimos N meses de cada série, não a média — mês atípico não distorce; (b) "z" mede quantos desvios típicos o mês fugiu do normal daquela série; (c) só vira crítico o que é estatisticamente fora do padrão **e** grande o bastante para mexer no resultado.

**Slide 3 — Painel do mês**
- Volume realizado vs. mediana histórica vs. previsto (3 números grandes)
- Gráfico de linha da série total (13 meses) com faixa da mediana
- Semáforo: N críticos · N atenção · N observar
- Uma frase de veredito: o mês está dentro do padrão ou não, e onde está a maior parte do desvio

**Slide 4 — Mapa das exceções críticas**
Tabela: Severidade | Nível | Chave | Realizado | Mediana | Desvio | z | Tipo. Ordenada por score.

**Slides 5 a 12 — Um por exceção crítica** *(o coração do deck)*

Cada slide tem exatamente estes quatro blocos:

1. **Título = a exceção em uma frase de negócio.** "CA-50 em SP caiu 55% e já são 3 meses seguidos abaixo do padrão." Nunca "Análise da linha CA-50".
2. **Gráfico:** barras dos 13 meses, mês atual destacado, linha horizontal na mediana e faixa sombreada p25–p75. É isso que faz a anomalia ser óbvia sem explicação.
3. **Caixa de números:** Realizado | Mediana histórica | Faixa normal (p25–p75) | Desvio (t e %) | z robusto | Meses fora da faixa | Previsto e atingimento, quando houver.
4. **Causa e pergunta:** 2–3 bullets com os contribuintes de `causas` ("Cliente X responde por 84% do desvio"), e a **pergunta em destaque visual** — caixa colorida, fonte maior. A pergunta é o produto do slide.

**Slide 13 — Atenção (consolidado)**
Tabela com as de severidade `atencao`, agrupadas por camada. Sem slide individual.

**Slide 14 — Aderência à previsão** *(só se houver base de previsão)*
Onde a previsão errou o alvo: `desvio_previsao`, `previsao_nao_realizada`, `venda_sem_previsao`. A pergunta aqui é sempre sobre o **processo** de forecast, não sobre a venda.

**Slide 15 — Pauta da reunião**
Todas as perguntas numeradas, com colunas **Responsável** e **Prazo** em branco para preencher na reunião. Este é o slide que o Samuel projeta na tela.

**Slide 16 — Apêndice metodológico**
Janela usada, parâmetros de sensibilidade, o que é mediana/MAD/z, critérios de severidade, séries excluídas por histórico insuficiente.

---

## PASSO 4 — Montar o Word executivo

Ler o SKILL.md do skill **docx** antes de construir. Mesmo conteúdo, voz narrativa:

1. **Sumário executivo** — 5 bullets: o mês fechou onde, quantas exceções, qual a mais grave, qual o padrão por trás delas, o que precisa de decisão.
2. **Panorama do mês** — total realizado vs. mediana vs. previsão, com a série.
3. **Exceções críticas** — uma subseção por exceção: o que aconteceu, os números, a causa apurada, a pergunta aberta.
4. **Exceções em atenção** — tabela.
5. **Aderência à previsão**.
6. **Padrões transversais** — o que várias exceções têm em comum (mesma região? mesmo cliente? mesma linha?). Esta seção é a que o PPTX não consegue dar; é o maior valor do Word. Se três SKUs diferentes caíram e todos são do mesmo fornecedor, **isso** é o achado.
7. **Pauta de perguntas** — numeradas, prontas para a reunião.
8. **Apêndice metodológico**.

---

## Diretrizes de escrita

- **Todo insight cita o número que o sustenta.** "Caiu bastante" não existe; "caiu 857 t, 55% abaixo da mediana" existe.
- **Nomear sempre.** Cliente real, UF real, SKU real. Nunca "alguns clientes".
- **Não afirmar causa.** O radar mostra *o que* fugiu e *quem* contribuiu. O *porquê* é o que se pergunta ao comercial. Escrever "o desvio se concentra em X" — não "o desvio ocorreu porque X".
- **Perguntas abertas e verificáveis.** "Isso é perda de cliente, decisão de preço ou pedido que escorregou?" força uma resposta específica; "o que houve?" não.
- **Formatos:** volumes `X.XXX,X t` · percentuais sempre com sinal `+X,X%` / `-X,X%` · z com uma decimal.
- **Ordenar por magnitude absoluta**, nunca por percentual — um SKU de 2 t que dobrou não é notícia.

---

## Rodada recorrente

Se o usuário quiser isso todo mês, oferecer uma tarefa agendada (ferramentas de scheduled task, nunca cron local): dia útil combinado, prompt autossuficiente indicando onde estão os arquivos, mês = último com dados, e entrega do PPTX + Word. Lembrar que a sessão agendada roda sem ninguém assistindo — ela deve assumir os padrões e declarar as suposições.

---

## Limitações a declarar no apêndice

- Base só tem volume (t). Sem faturamento, o radar não enxerga queda de preço com volume estável.
- Séries com menos de 4 meses ativos não viram crítico por si só — o baseline não sustenta.
- Sazonalidade não é modelada. Se o negócio tem estação forte, comparar com a janela inteira gera alarme falso previsível; nesse caso rodar com `--janela 24` e ler os picos do mesmo mês do ano anterior antes de concluir.
- O radar aponta o que é estatisticamente incomum. Incomum não é sinônimo de ruim — a leitura de negócio é do analista.
