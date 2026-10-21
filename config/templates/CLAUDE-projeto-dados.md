# <Nome do projeto> — instruções para o Claude

Copie este arquivo para a raiz de um projeto de dados/ML como `CLAUDE.md` e preencha os campos `< >`. Vem do padrão usado no copiloto-vendas e no SOE Inteligência Comercial.

## Contexto
<Duas a quatro linhas: o que o projeto entrega, para quem, de onde vêm os dados.>

Os modelos e scripts versionados são a **fonte única da verdade numérica**. O Claude orquestra, escreve código e formata saída; não inventa número.

## Estrutura
- `src/data/` ingestão e limpeza · `src/features/` features · `src/models/` modelos e backtest · `src/scoring/` aplicação diária · `tests/`
- Bases em `<pasta>`; nunca versionar dado sensível nem `.env`.
- Progresso em `CHECKPOINT.md` (skill `fechamento-de-sessao`).

## Princípios (não negociáveis)
1. **Sem número inventado.** Probabilidade, volume, data prevista e métrica vêm de função/modelo rodado. Se não existe, escrever o código primeiro.
2. **Estatística correta.** Classificação: backtest temporal com janela rolante, AUC + lift + precision@k, calibração (Brier, Platt/isotônica no código). Forecast: WAPE, MAPE, Bias segmentados por produto/cliente/UF.
3. **Guardrails no código.** Clamp de volume por quantil histórico (p95/p99), probabilidade entre 0 e 1 (evitar > 0,99 sem motivo), regra de fallback para cliente novo ou série curta.
4. **Explicabilidade.** Toda lista priorizada traz o "motivo" em linguagem de negócio.
5. **Escopo fechado.** Mudança de arquitetura, nova integração ou nova tecnologia: propor plano e esperar ok.

## Como trabalhar
- Tarefa não trivial: plano numerado → ok → implementação → teste.
- Funções pequenas e reutilizáveis; mudanças correlatas num único patch.
- Rodar só os testes do módulo afetado (`pytest tests/test_<modulo>.py -q`), não a suíte inteira.
- Ler só os arquivos citados; não varrer o repositório sem necessidade.

## Papéis de subagente (quando a tarefa for ampla)
- `levantamento` (haiku): estrutura de bases e arquivos.
- `analista-dados` (sonnet): features, modelo, métricas, backtest.
- `auditor-numeros` (haiku): confere saída numérica antes de entregar.
- Explicação/UX fica na conversa principal: tabela Markdown padrão + motivo curto.

## Pronto quando
Roda sem erro · teste das funções novas passa · nenhum número hard-coded no lugar de modelo · guardrails aplicados · formato de saída igual ao combinado · mudança localizada.
