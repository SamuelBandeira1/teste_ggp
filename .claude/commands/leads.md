---
description: Coleta restaurantes no Google Maps, pontua, escreve as mensagens e gera a fila de envio
---

Siga as regras do `CLAUDE.md`. Nada é enviado: o resultado é uma fila para o Samuel revisar e clicar.
$ARGUMENTS pode trazer um arquivo de buscas diferente ou um limite de leads (padrão: 60).

1. Cidade confirmada: Fortaleza/CE. Use `prospeccao/buscas.txt` como está, a menos que o Samuel peça outros bairros.
2. Rode o scraper (Docker), salvando em `dados/`:
   ```bash
   mkdir -p dados
   docker run --rm \
     -v gmaps-playwright-cache:/opt \
     -v "$PWD/prospeccao/buscas.txt:/queries.txt:ro" \
     -v "$PWD/dados:/out" \
     gosom/google-maps-scraper \
     -input /queries.txt -results /out/maps_bruto.csv \
     -depth 3 -lang pt -exit-on-inactivity 3m
   ```
   Antes da coleta completa, teste com 1 linha de busca e `-depth 1` para validar. No Windows sem WSL, troque `$PWD` pelo caminho absoluto.
   Se houver resultados anteriores, use `-resume` com o mesmo arquivo para não duplicar.
3. `python3 prospeccao/pontuar_leads.py dados/maps_bruto.csv` → `dados/leads_pontuados.csv`. Se já existir, o script preserva status e anotações dos leads antigos.
4. Para os N melhores com status `novo`: abra o site ou Instagram e leia 3 avaliações recentes no link do Maps. Preencha `gancho` com 1 detalhe citável e verdadeiro (prato elogiado, reclamação de demora para ver o cardápio, casa nova). Se o número já aparece em conversas antigas no WhatsApp, marque em `observacoes` para não abordar de novo.
5. Escreva a mensagem de cada um a partir dos modelos do `BRIEFING.md` (A para quem tem nota boa e poucas avaliações, B para quem tem cardápio online). Use nota e nº de avaliações reais. Sem preço enquanto o preço estiver A DEFINIR no `CLAUDE.md`.
6. Gere `dados/fila.html`: uma página simples, legível no celular, um cartão por lead com nome, bairro, nota, avaliações, gancho, mensagem, botão "Abrir no WhatsApp" (`https://wa.me/<numero>?text=<mensagem codificada>`), link do Maps e botão para copiar o link de avaliação. Ordem: maior pontuação primeiro. Teste no navegador que os botões abrem o link certo.
7. Termine com: quantos lugares coletados, quantos passaram no filtro, os 10 melhores com o motivo, e 5 mensagens para o Samuel aprovar.
