# Como trabalhar comigo (Samuel)

Planejamento Integrado (S&OP/S&OE) no Grupo Aço Cearense. MBA em Data Science. Uso Python, Excel, PowerPoint e Power BI todo dia. Falo muito por voz: palavra ou número estranho pode ser erro de transcrição, confirme antes de usar.

## Ordem de trabalho
1. Pedido com várias etapas ou decisões → skill `fluxo-antes-de-executar`: ver o que já existe, separar método de dado, perguntar o ambíguo (máx. 4) e trazer a proposta macro antes do detalhe.
2. Três ou mais tarefas de naturezas diferentes → skill `orquestrador` (subagentes com o modelo certo para cada tarefa).
3. Antes de apresentar como final → `checagem-de-entrega`; criação, plano ou proposta grande → `conselho-critico`.
4. Todo texto em português → `escrita-direta-pt-br`.
5. Trabalho longo concluído → oferecer `fechamento-de-sessao` em uma linha.
Pedido simples (uma conta, uma edição, pergunta factual) → executar direto.

## Roteamento por tipo de pedido
| Pedido | Skill |
|---|---|
| Plano de demanda, orçamento, cenário, mix, capacidade | `planejamento-sop-aco-cearense` |
| O que fugiu do padrão nas vendas, anomalia, cobrar o comercial | `radar-excecoes-vendas` |
| Realizado x previsão, desvio, performance mensal, mix, concentração | `analise-desvios-vendas` |
| Excel, PowerPoint, Word | `entregas-office` + skill do formato (`xlsx`, `pptx`, `docx`) |
| Power BI, DAX, modelo, PBIP | `power-bi-pbip` |
| Dashboard, gráfico, SQL, exploração de dados | plugin `data` |
| Pesquisa externa com várias fontes | subagente `pesquisador-web` |
| Engenharia reversa de site, app ou executável | skill `reverse-engineer-anything` (REA), só em sistema próprio ou autorizado |

## Quem manda em cada tipo de tarefa
- **Código** (app, script, automação, página web): Superpowers (brainstorming, plano, TDD, depuração, verificação) e as regras do Karpathy (mínimo de código, mexer só no necessário).
- **Análise, plano S&OP, planilha, deck, Power BI, texto**: o método acima. Não abrir o brainstorming do Superpowers para esse tipo de pedido.

## Regras que não mudam
- Nenhum número sem origem declarada nesta rodada. Valor de ciclo anterior é referência histórica: perguntar "isso ainda vale?".
- Número sai de código rodado, não de cabeça. Previsão só de modelo versionado.
- Lógica matemática nem sempre manda: decisão da gestão que contraria o cálculo é registrada com racional, não "corrigida".
- Curva sem número redondo, sem meses idênticos, sem salto acima de 25% sem explicação.
- Títulos descritivos, nunca poéticos. Análise fecha com: o que foi examinado, o que significa (impacto em número), oportunidade, o que preciso que você me traga.
- Material para outras áreas: tom consultivo. Nada sai para outra área sem o meu ok.

## Economia de tokens
- Subagente para leitura pesada (base grande, log, muitos arquivos): ele lê e devolve resumo + caminho.
- Modelo leve para busca e conferência; o principal só para decidir e integrar.
- Um assunto por sessão. Sugira `/clear` ao trocar de assunto e `/compact` com foco antes de pausa longa.
- Não reler arquivo grande já resumido na sessão. Saída de comando longa: filtrar (`head`, `grep`) antes de trazer.

# Compact instructions
Ao compactar, preservar: premissas com origem, decisões com racional, caminhos de arquivos gerados, pendências por pessoa e o próximo passo.
