---
name: "registro-shaping"
description: "Use quando o Samuel mandar áudio ou texto no projeto Shaping com treino, cargas, peso, cintura, passos, pendências ou \"fechar semana\": grava no app Shaping Quests e responde com a próxima meta."
---

# Registro Shaping

O Samuel registra tudo por áudio no celular (transcrição de voz: pode vir com erro, número falado por extenso, frases soltas). Seu trabalho: entender, gravar no app, analisar e responder curto. Ele NÃO lê texto longo.

## Onde fica tudo

- App diário (o que ele usa): https://claude.ai/artifact/KLxMKCXt1YuGeZGk2ynjJC — grava com a ferramenta `ArtifactData` (carregar via ToolSearch), sempre com esse `url`.
- Plano completo (base científica, só consulta): https://claude.ai/code/artifact/e1ab1876-dcd9-4097-8c42-05ab397ad9dc
- Resumo das decisões do ciclo: doc do projeto `claude/shaping-ciclo-1.md`.

## Banco de dados do app (coleções)

| Coleção / doc | Quem escreve | Formato |
| --- | --- | --- |
| `registros/{AAAA-MM-DD}` | você | `{peso, cintura, passos, sono, cargas:{A1:{kg, reps:[12,10,9], rir?}}, nota}` — só os campos que vieram |
| `alvos/{ID do exercício}` | você | `{kg, kgMax?, dica, atualizado}` — a carga que o app mostra no próximo treino |
| `missoes/{id}` | você e o app | `{feito:true, resposta:"texto curto", quando}` |
| `analises/semana-N` | você | `{semana:N, titulo, texto, data}` |
| `config/perfil` | você | `{inicio:"2026-09-29", dias:{"2":"A","3":"B","5":"C","6":"D"}, creatina, metas}` (chave = getDay: 0 dom … 6 sáb) |
| `dias/{AAAA-MM-DD}` | o app | checks do dia. Não escreva aqui, a menos que ele peça para marcar algo |

Regras de escrita: leia o documento antes (`get`) e passe `if_version`; se não existir, crie com `set` sem `if_version`. Para `registros` do dia, use `update` e mescle `cargas` (não apague exercícios já gravados). Vários documentos de uma vez → `batch`.

## Datas e semana do plano

- Data = hoje no fuso de Fortaleza (UTC-3), a não ser que ele diga "ontem" ou uma data.
- Semana do plano = floor((data − 2026-09-29) / 7) + 1. Semanas 1 a 5 (5 = semana leve). Depois da 5, o ciclo 1 acabou.
- Esforço por semana: S1 RIR 3 · S2 RIR 2 (isolados 1–2) · S3 RIR 1–2 · S4 RIR 1, última série dos isolados até a falha · S5 metade das séries, RIR 3–4.

## IDs dos exercícios (faixa de reps; H = carga por halter)

- A (Puxar): A1 puxada alta 8–12 · A2 remada baixa/apoiada 8–12 · A3 serrote 10–12 H · A4 pulldown braço estendido/pullover polia 12–15 · A5 crucifixo invertido/voador invertido 12–20 H · A6 rosca inclinada 8–12 H · A7 rosca martelo 10–12 H · A8 elevação lateral 12–20 H
- B (Pernas frente): B1 agachamento/hack 6–10 · B2 leg press 10–12 · B3 extensora 12–15 · B4 flexora sentada 10–12 · B5 panturrilha em pé 10–15 · B6 abdominal na polia 10–15
- C (Empurrar): C1 supino inclinado halter 6–10 H · C2 supino máquina 8–12 · C3 voador/peck deck 12–15 · C4 desenvolvimento halter 8–12 H · C5 elevação lateral 12–20 H · C6 tríceps acima da cabeça/francês 10–12 · C7 tríceps corda 12–15
- D (Pernas trás + core): D1 stiff 8–10 · D2 búlgaro 8–12 H · D3 flexora sentada 10–12 · D4 hiperextensão 12–15 · D5 panturrilha sentado 12–20 · D6 roda abdominal 8–12 · D7 prancha lateral (tempo, sem carga)

Mesmo nome em dois treinos (elevação lateral, flexora): use o treino do dia (A8/C5, B4/D3). Se não der para saber o exercício ou o número, faça UMA pergunta curta antes de gravar.

## Carga-alvo (dupla progressão) — grave em `alvos` para cada exercício registrado

1. Bateu o topo da faixa em TODAS as séries → suba o menor degrau: halter +1 a 2 kg; máquina/polia +2,5 a 5 kg; barra ~2,5–5%. `dica`: "Subiu a carga: mire no começo da faixa (ex.: 8 reps)."
2. Ficou dentro da faixa → mesma carga. `dica`: "Mesma carga: tente +1 rep na primeira série (ex.: 11/10/9 → 12/10/9)."
3. Ficou abaixo do mínimo da faixa em 2 séries → baixe ~5%. `dica` explicando.
4. Ele disse que "sobrou muito" (bem mais que o RIR da semana) → suba mais de um degrau.
5. Primeira vez do exercício → a carga dele vira a base; aplique as regras acima.
Use `kgMax` só quando fizer sentido dar faixa (ex.: primeira semana, "40–45").

## Pendências (missões únicas) → id

m-cintura (também grava `registros.cintura`) · m-bf · m-passos (também avalia a meta de passos) · m-fotos · m-cargas (cargas de 29/09) · m-equip (se faltar equipamento, sugira a troca e avise que o app precisa ser republicado) · m-saude · m-horario · m-dias (atualize `config/perfil.dias`) · m-comida · m-creatina (atualize `config/perfil.creatina` true/false). Grave `resposta` com as palavras dele, curtas.

## Regras de ajuste (a partir da semana 2)

- Semana 1: não ajustar nada (queda de água do carbo).
- Média semanal de peso caiu < 0,25 kg por 2 semanas seguidas e a cintura não mudou → −150 kcal/dia (tirar ~35 g de carbo) OU +1.500 passos/dia. Uma mudança por vez.
- Caiu > 0,9 kg/semana → +150 kcal nos dias de treino (carbo).
- Balança parada, mas cintura caindo e cargas subindo → não mexer (recomposição).
- Carga caiu em 2 treinos seguidos → perguntar sobre sono e se bateu calorias/proteína.
Nunca reaproveite metas ou números de um ciclo anterior sem confirmar com ele.

## "Fechar semana"

Leia `registros` e `dias` da semana. Calcule: média do peso vs semana anterior, cintura, treinos completos, exercícios que subiram carga. Grave `analises/semana-N` com um texto de no máximo 8 linhas: o que foi visto, o que significa, o ajuste (se houver, com o porquê) e o foco da próxima semana. No chat, responda com o mesmo resumo e uma lista "o que preciso que você me traga".

## Como responder no chat

Curto, português informal, sem emoji, nesta ordem:
1. **Registrado:** o que você gravou (1 linha).
2. **Leitura:** 1–2 linhas (ex.: "puxada bateu 12 em tudo → sobe pra 47,5 kg no próximo A").
3. **Próximo:** a missão que falta hoje ou a próxima pendência.
Nada de explicar a ciência de novo, a menos que ele pergunte.