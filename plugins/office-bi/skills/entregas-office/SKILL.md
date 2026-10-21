---
name: entregas-office
description: "Use SEMPRE que a entrega for planilha Excel (.xlsx), apresentação PowerPoint (.pptx) ou documento Word (.docx), criada do zero ou editada, mesmo que o Samuel não peça padrão. Complementa as skills técnicas xlsx, pptx e docx com o padrão de entrega dele: aba de premissas com origem, fórmulas vivas, títulos descritivos, um ponto por slide, recálculo e conferência visual antes de entregar."
---

# Entregas Office no padrão do Samuel

As skills `xlsx`, `pptx` e `docx` (plugin document-skills da Anthropic) cuidam da técnica do arquivo. Esta skill define **como a entrega tem que sair** para não voltar. Ler a skill técnica do formato primeiro, depois aplicar o padrão abaixo.

## Ferramentas (Claude Code)
| Para | Usar |
|---|---|
| Ler e transformar dados | `pandas` (`read_excel`, `pivot_table`), nunca copiar tabela grande para a conversa |
| Criar/editar xlsx com fórmula e formatação | `openpyxl` (preserva o arquivo existente); `xlsxwriter` só para arquivo novo com gráfico nativo |
| Recalcular fórmulas e checar erro | `soffice --headless --convert-to xlsx --outdir recalc <arquivo>` e depois ler com `data_only=True` |
| Criar/editar pptx | `python-pptx`; partir do modelo (.potx/.pptx) da empresa quando existir |
| Conferir slide visualmente | `soffice --headless --convert-to pdf` e depois `pdftoppm -png -r 60` para olhar cada página |
| Word | `python-docx` (ou docx-js, conforme a skill docx) |
| Auditar números | `auditar_numeros.py` da skill `checagem-de-entrega` |

No Microsoft 365: o add-in Claude for Excel/PowerPoint trabalha no arquivo aberto; o conector Microsoft 365 lê arquivos no OneDrive/SharePoint (escrita depende do admin liberar). No Claude Code, o caminho é arquivo local ou sincronizado pelo OneDrive.

## Excel
- **Abas fixas**: `Resumo` (o que o leitor olha), abas de cálculo, `Premissas` (cada premissa com valor, origem, data, dono, status travada/aberta), `Base` (dado bruto, intocado), `Log` quando houver decisão fora da lógica pura.
- **Fórmula viva** para total, subtotal, percentual e derivado. Valor colado só na `Base` e em premissa digitada (célula de entrada com fundo diferente).
- Unidade no cabeçalho (`Volume (t)`, `Receita (R$ mil)`), período explícito, formato de número consistente, sem casa decimal inútil.
- Nada de mês com valor idêntico ao vizinho, número redondo sem justificativa ou salto acima de 25% sem nota (regra da equipe de S&OP).
- Antes de entregar: recalcular com LibreOffice, procurar `#REF!`, `#DIV/0!`, `#N/A`, `#VALUE!` e rodar `auditar_numeros.py`.
- Editando arquivo de outra pessoa: manter formatação, nomes de aba e fórmulas existentes; mudar só o pedido e listar o que mudou.

## PowerPoint
- **Título descritivo**: diz do que o slide trata ("Cobertura de capacidade por linha — 2027"). Nunca poético.
- **Um ponto por slide.** Se precisa de dois títulos, são dois slides.
- Número sempre com unidade e período; fonte e data no rodapé do slide.
- Identidade visual forte e elementos grandes: gráfico ocupa o slide, tabela com no máximo 7 linhas visíveis (o resto vai para anexo).
- Gráfico: barra para comparação, linha para série no tempo; destacar só a série que importa, o resto em cinza.
- Sequência padrão de análise: o que foi examinado → o que significa (impacto em número) → oportunidade → o que preciso que vocês tragam (por área ou pessoa).
- Antes de entregar: renderizar cada slide em imagem e olhar texto cortado, sobreposição, contraste, marcador interno esquecido.

## Word
- Títulos descritivos, narrativa sequencial com comparação entre as partes (não comprimir em bullet).
- Tabelas com fonte e data. Resumo executivo no início em até 6 linhas.
- Formato de análise S&OP quando aplicável: Resumo Executivo → Premissas → Dados → Distribuição → Justificativa Técnica → Riscos → Recomendações → Próximos Passos.

## Antes de entregar qualquer arquivo
1. `checagem-de-entrega` (números) e `escrita-direta-pt-br` (texto).
2. Abrir o arquivo final (recalculado/renderizado) e conferir, não confiar no script que gerou.
3. Dizer o caminho do arquivo, o que contém e as ressalvas em até 3 linhas.
