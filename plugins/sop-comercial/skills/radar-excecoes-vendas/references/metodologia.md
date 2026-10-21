# Metodologia do Radar de Exceções

Documento de referência. Ler quando precisar refazer cálculos à mão, explicar o método ao time comercial ou justificar por que algo foi (ou não foi) classificado como exceção.

---

## 1. Por que mediana e MAD, e não média e desvio padrão

Base de vendas tem outliers naturais: uma obra grande, um mês de antecipação de pedido, um cliente que sumiu por 30 dias. A média e o desvio padrão **absorvem** esses eventos e passam a considerá-los normais.

Exemplo real de série (t): `100, 105, 98, 102, 480, 99, 101, 103`

| Estatística | Valor | Leitura |
|---|---|---|
| Média | 148,5 | inflada pelo mês de 480 |
| Desvio padrão | 132,7 | enorme, quase nada vira anomalia |
| **Mediana** | **102,5** | o patamar real do negócio |
| **MAD × 1,4826** | **~4,4** | a variação típica de verdade |

Com média/desvio padrão, um mês de 60 t (queda de 41% no patamar real) dá z = −0,67 — invisível. Com mediana/MAD dá z = −9,7 — alarme imediato. É por isso que o padrão do radar é robusto.

---

## 2. Construção do baseline

Para cada série (uma combinação de chave num nível, ex.: `SP | CA-50`):

1. Monta o vetor de volume dos N meses da janela **anteriores** ao mês analisado. Mês sem movimento entra como **zero** — ausência de venda é informação, não dado faltante.
2. `mediana = median(hist)`
3. `MAD = median(|hist − mediana|)`
4. `sigma_robusto = MAD × 1,4826` — o fator converte o MAD para a escala de um desvio padrão numa distribuição normal, para que o z tenha a leitura habitual.
5. **Piso de dispersão:** `sigma_efetivo = max(sigma_robusto, 10% da mediana, 0,5 t)`

O piso existe por um motivo prático: numa série quase constante o MAD tende a zero, e sem piso qualquer oscilação de 3% viraria z = 12. O piso diz "variação de até 10% do patamar é ruído, não notícia".

Se o MAD é zero mas o desvio padrão não é, o desvio padrão entra no lugar.

---

## 3. Z-score robusto

```
z = (valor_do_mês − mediana) / sigma_efetivo
```

Leitura para o time comercial:

| z | Significado |
|---|---|
| entre −2 e +2 | dentro da variação normal daquela série |
| ±2 a ±3 | atípico — merece explicação |
| acima de ±3 | fora do padrão — é exceção de processo |
| acima de ±5 | quebra de padrão, quase sempre tem evento concreto por trás |

O z é truncado em ±50 para não poluir slide. Série sem nenhum mês ativo no histórico não tem z: é **estreia**, e a gravidade vem só do volume envolvido.

---

## 4. Tipos de exceção

| Tipo | Como é detectado |
|---|---|
| `ruptura` | série ativa em ≥4 meses, mediana > 0, mês atual = 0 |
| `estreia` | primeira venda da série em toda a base é o mês atual |
| `queda_sustentada` | ≥3 meses consecutivos, terminando no atual, abaixo de 85% da mediana |
| `crescimento_sustentado` | ≥3 meses consecutivos acima de 115% da mediana |
| `queda_atipica` | z ≤ −2 |
| `pico_atipico` | z ≥ +2 |
| `desvio_previsao` | atingimento vs. forecast foge ±20% e o desvio é material |
| `previsao_nao_realizada` | havia previsão material e a realização foi zero |
| `venda_sem_previsao` | venda material sem nenhuma previsão na chave |

Uma série pode disparar vários sinais ao mesmo tempo — todos ficam em `sinais`. O `tipo` primário é o mais específico (ruptura e estreia vêm antes de queda/pico, porque explicam mais).

---

## 5. Severidade = significância × materialidade

Estatística sozinha não basta: um SKU de 3 t que triplicou tem z alto e importância zero.

**Materialidade:** `limiar = max(0,5% do volume total do mês, volume_minimo)`. "Muito material" = 3× o limiar.

| Condição | Severidade |
|---|---|
| ruptura + material | **crítico** |
| \|z\| ≥ 3 + material | **crítico** |
| \|z\| ≥ 2 + muito material | **crítico** |
| \|z\| ≥ 2 + material | atenção |
| tendência sustentada + material | atenção |
| estreia com desvio ≥ 5× limiar | crítico |
| resto dos sinais | observar |

**Duas travas anti-ruído:**

- Série com menos de 4 meses ativos não vira crítica — o baseline não sustenta a afirmação. Exceção: volume ≥ 5× o limiar, aí o tamanho fala mais alto que a estatística.
- Série com peso irrisório no mês (< 0,05% do total) não vira crítica. Numa ruptura o peso atual é zero por definição, então vale o **peso histórico** (mediana ÷ volume do mês).

**Score de priorização:** `min(|z|, 10) × √|desvio_abs|`. Equilibra "quão anormal" com "quão grande" — sem isso o ranking vira uma lista de SKUs minúsculos com z estratosférico.

---

## 6. Deduplicação hierárquica

Cada nível tem um pai (`sku → grupo → linha`, `estado_linha → estado`, `cliente_linha → cliente`, etc.).

Quando **um filho sozinho explica ≥70% do desvio do pai**, na mesma direção, o **pai** é marcado como `redundante_com` apontando o filho.

A lógica: se a queda inteira do estado de SP é a linha CA-50, a manchete útil é "CA-50 em SP", não "SP". O pai vira eco. Isso evita que o mesmo fato ocupe 4 slides com nomes diferentes.

**Limite conhecido:** só funciona na relação pai/filho. Dimensões irmãs que espelham uma à outra na base (ex.: cada linha pertence a uma única gerência) geram duplicata que o script não pega — a checagem é manual, comparando `valor_atual` e `desvio_abs` entre as manchetes.

---

## 7. Causa raiz

Para cada exceção que vira manchete, o script abre três recortes e ranqueia por `delta = atual − mediana_do_filho`:

- **por nível filho** (ex.: uma exceção de linha abre em grupos)
- **por cliente** (sempre, quando a dimensão existe e não é o próprio nível)
- **por segmento** (top 2)

`part_do_desvio_pct` diz quanto daquele contribuinte explica o desvio do pai. Pode passar de 100% quando há movimentos em direções opostas se cancelando — isso é informação, não erro: significa que o número agregado esconde dois movimentos.

---

## 8. Camada de previsão

Só roda em níveis **sem** `descricao_parceiro_master`, `descricao_segmento_mercado` ou `descricao_fornecedor` — essas colunas não existem na base de previsão e cruzá-las produziria números falsos.

A chave de agregação é a interseção de dimensões entre as duas bases.

---

## 9. O que o método NÃO faz

- **Sazonalidade:** não há decomposição sazonal. Com janela de 12 meses a mediana já mistura estações. Negócio sazonal deve rodar `--janela 24` e conferir o mesmo mês do ano anterior antes de concluir.
- **Preço:** sem coluna de faturamento, queda de preço com volume estável é invisível. Se a base ganhar `Faturamento R$`, dá para derivar R$/t e rodar o mesmo motor sobre essa métrica.
- **Causalidade:** o radar mostra o quê e o quem. O porquê vem da reunião.
- **Correlação entre séries:** cada série é avaliada isoladamente. Padrões transversais (três SKUs do mesmo fornecedor caindo juntos) são achados do analista lendo o conjunto, não do script.
