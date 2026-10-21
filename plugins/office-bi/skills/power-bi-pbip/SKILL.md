---
name: power-bi-pbip
description: "Use para qualquer trabalho de Power BI: criar ou corrigir medida DAX, revisar ou documentar modelo semântico, editar projeto PBIP (arquivos TMDL e PBIR), migrar lógica de Excel para Power BI, montar dicionário de medidas, ou usar o MCP de modelagem da Microsoft. Inclui fluxo seguro (backup, somente leitura primeiro, teste de DAX contra número conhecido) e script que resume o modelo em poucos tokens."
---

# Power BI com Claude Code (PBIP, TMDL, DAX)

O Claude Code não abre o arquivo `.pbix` (binário). Ele trabalha bem com o formato **PBIP**, que é texto: modelo em TMDL e relatório em PBIR (JSON). Por isso o primeiro passo é sempre ter o projeto em PBIP.

## 1. Preparar o projeto
- No Power BI Desktop: Arquivo > Salvar como > **Projeto do Power BI (.pbip)**. Em Opções > Recursos de visualização, ligar **armazenamento de modelo semântico no formato TMDL** e **formato de relatório PBIR** se ainda forem opcionais na versão instalada.
- Estrutura: `Nome.SemanticModel/definition/` (tabelas em `tables/*.tmdl`, `relationships.tmdl`, `model.tmdl`) e `Nome.Report/definition/` (páginas e visuais em JSON).
- Colocar a pasta sob git (ou copiar a pasta inteira) **antes** de qualquer edição. Backup é obrigatório.
- Fechar o Desktop antes de editar os arquivos; reabrir para validar.

## 2. Entender o modelo gastando pouco
Não ler todos os TMDL na conversa. Rodar:
```
python <pasta desta skill>/scripts/resumir_tmdl.py <pasta .SemanticModel> > modelo_resumo.md
```
(no Claude Code via plugin: `${CLAUDE_PLUGIN_ROOT}/skills/power-bi-pbip/scripts/resumir_tmdl.py`). Gera tabelas, colunas, medidas com expressão, pasta e formato, e relacionamentos. Trabalhar a partir do resumo e abrir só o TMDL que vai mudar.

## 3. Duas formas de alterar
| Caminho | Quando | Cuidado |
|---|---|---|
| Editar TMDL/PBIR direto | medida nova, ajuste de expressão, formato, pasta, descrição, renomear em lote | manter a indentação com tab; reabrir no Desktop para validar |
| MCP de modelagem da Microsoft (`@microsoft/powerbi-modeling-mcp`) | operar no modelo aberto no Desktop ou no Fabric, rodar DAX de teste, checar boas práticas | está em preview; começar com `--readonly`; escrita só com ok do Samuel |

Configuração do MCP (Windows, Node instalado), no `.mcp.json` do projeto ou com `claude mcp add`:
```json
{ "mcpServers": { "powerbi-modeling": { "type": "stdio", "command": "npx",
  "args": ["-y", "@microsoft/powerbi-modeling-mcp@latest", "--start", "--readonly"] } } }
```
Tirar `--readonly` só para uma sessão de escrita aprovada. O servidor pede aceite da EULA na primeira vez. Ele altera só modelo (tabela, coluna, medida, relacionamento), não página de relatório.

Complementos úteis no Windows: DAX Studio (rodar e medir consulta), Tabular Editor (Best Practice Analyzer, edição em lote).

## 4. Padrão de DAX
- Nome de medida em português claro, com unidade quando couber: `Volume Vendido (t)`, `Aderência Forecast %`. Pasta de exibição por tema. Descrição em toda medida de negócio.
- `VAR ... RETURN` para expressão com mais de um passo; `DIVIDE` em toda divisão; nada de coluna calculada quando medida resolve.
- Modelo estrela: fatos ligados a dimensões, tabela calendário marcada como tabela de datas, relacionamento de mão única por padrão (bidirecional só com motivo escrito).
- Medida base primeiro (`Volume Vendido (t) = SUM(fVendas[Venda Vol])`), derivadas reaproveitam a base.
- Time intelligence (acumulado, mesmo período ano anterior, média móvel) e regra de rateio: escrever o caso de teste antes da medida.

## 5. Testar antes de dizer que está pronto
DAX gerado por IA costuma parecer certo e errar em lógica de negócio. Toda medida nova ou alterada passa por:
1. Consulta de teste (DAX Query View no Desktop, DAX Studio ou MCP):
   ```
   EVALUATE SUMMARIZECOLUMNS(dCalendario[AnoMes], "Teste", [Volume Vendido (t)])
   ```
2. Comparar com número conhecido: total da base em Excel/pandas para o mesmo filtro. Diferença precisa de explicação.
3. Testar um recorte pequeno (um mês, uma linha, um cliente) conferível na mão.
4. Registrar no PR/commit ou no CHECKPOINT: medida, fórmula, teste e resultado.

## 6. Entregar
- Lista do que mudou (arquivo e objeto), medidas com fórmula e resultado do teste.
- O que o Samuel precisa conferir abrindo o Desktop (visual quebrado, medida com erro, atualização).
- Dicionário de medidas atualizado (`modelo_resumo.md`) quando o modelo for compartilhado.
