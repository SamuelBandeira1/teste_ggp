# Levar o método para o claude.ai da conta de trabalho

O claude.ai (web, desktop, celular) não lê `~/.claude` nem roda subagentes. Ele usa skills enviadas como .zip, preferências do perfil, instruções de Projeto e conectores. As skills deste pacote já têm o caminho alternativo para o web (o Conselho roda em sequência em vez de em paralelo).

## 1. Skills

1. Na pasta do repositório: `python scripts/empacotar_claude_ai.py` (com `--com-pessoal` se quiser as pessoais).
2. No claude.ai da conta de trabalho: **Personalizar > Skills > "+" > Criar skill > Fazer upload de skill**, um zip de `dist/claude-ai/skills/<plugin>/` por vez.
3. Ordem sugerida: `fluxo-antes-de-executar`, `checagem-de-entrega`, `escrita-direta-pt-br`, `conselho-critico`, `orquestrador`, `fechamento-de-sessao`, `entregas-office`, `power-bi-pbip`, `planejamento-sop-aco-cearense`, `radar-excecoes-vendas`, `analise-desvios-vendas`.
4. Precisa de **Execução de código e criação de arquivos** ligada (os scripts Python rodam no ambiente do claude.ai).
5. Plano Team/Enterprise: o dono da organização pode distribuir o plugin inteiro para a equipe (`dist/claude-ai/plugins/<plugin>.zip`) em Configurações da organização > Skills/Plugins. Skill enviada por você fica só na sua conta até ser compartilhada.

As skills `xlsx`, `pptx`, `docx`, `pdf`, `deep-research` e `skill-creator` já vêm no claude.ai: não precisa subir.

## 2. Preferências do perfil

Configurações > Perfil > "Que preferências pessoais o Claude deve considerar": colar o texto de [../claude-ai/PREFERENCIAS-PERFIL.md](../claude-ai/PREFERENCIAS-PERFIL.md).

## 3. Projetos

Para cada frente recorrente (ciclo S&OP, radar mensal, estudos), criar um Projeto com:
- instrução do Projeto: 3 a 5 linhas dizendo a frente, o leitor e a skill que manda (ex.: "Ciclo de orçamento 2027. Seguir `planejamento-sop-aco-cearense`. Leitor: diretoria comercial.");
- conhecimento: só método e referência (manual, glossário, CHECKPOINT). **Não** colocar base com números de ciclo anterior: é a contaminação de premissa que a skill de S&OP proíbe.

## 4. Conectores

- **Microsoft 365**: Configurações > Conectores. Dá acesso a Outlook, OneDrive, SharePoint e Teams. A escrita em arquivos precisa ser liberada pelo admin.
- **Add-in Claude para Excel/PowerPoint/Word**: instalar pelo Microsoft AppSource (ou pedir à TI). Trabalha no arquivo aberto.
- Power BI: não há conector nativo no claude.ai; o caminho é o Claude Code com a skill `power-bi-pbip`.

## 5. Memória

Na conta pessoal: Configurações > Memória, copiar o que for de trabalho. Na conta de trabalho, pedir "importa essa memória" (skill `import-memory`) e colar. Tirar o que for pessoal (treino, negócio NFC, família).
