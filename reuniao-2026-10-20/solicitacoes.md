# Reunião 20/10/2026 (08:55): ajustes na apresentação de Planejamento Integrado

**Fontes cruzadas**
1. Transcrição automática enviada (Teams/Office, "Interlocutor 1..4").
2. Retranscrição local do áudio com **Whisper large-v3** (int8, via sherpa-onnx) + separação de falantes (pyannote + ERes2Net). Arquivo: `transcricao_whisper_large_v3.txt`.

**Glossário (o que as transcrições escreveram errado)**

| Escrito como | Provavelmente é |
|---|---|
| SNOPI, Sinopi, S não pi, Senopi | **S&OP** (Sales & Operations Planning) |
| SNOI, SNUI, essa no i, Senoí, assino I | **S&OE** (Sales & Operations Execution): plano semanal |
| IBP, BBP, IPP | **SAP IBP** |
| SAP na o ano passado / Sapnod / sapinal | evento **SAP NOW 2025** |
| programa do "and" / Intuend | programa **End-to-End** |
| atif / ativo | **OTIF** |
| response supply / Responsify | **IBP Response & Supply** |
| ECP (Whisper) | **PCP** (a transcrição enviada acertou) |

**Prazo:** o gestor (Interlocutor 3) sai ao meio-dia para pegar voo no início da tarde. O roteiro precisa chegar antes disso. Amanhã ele encaixa um horário para ajustes.

---

## 1. Direção geral
- O material está bom, mas **focado demais em ganhos operacionais**. Ele quer uma **visão mais executiva, de negócio**.
- Ele vai **reaproveitar parte do material que apresentou no SAP NOW 2025** e vai **enviar esse material** para a equipe.
- Por enquanto **não é para tirar nada**. Ele está só apontando o que falta e depois faz a seleção final, se ficar grande demais.

## 2. Jornada / trajetória (slide do roadmap do S&OP, slide 6)
- [ ] Transformar o "roadmap do S&OP" na **jornada da empresa em busca da melhoria dos processos de gestão de atendimento ao cliente**, incluindo:
  - criação do **planejamento integrado (2019–2020)**;
  - **programa End-to-End (2022)**, com a entrada da parte de **Customer** *(trecho incerto: "criação do Customer, visão do OTIF e do IBP")*;
  - **SAP IBP**, **S&OP** e **S&OE**.
- [ ] Encaixar a linha do tempo no **modelo visual do material do SAP NOW** (ou em outro modelo visual equivalente).
- [ ] Encaixar melhor o **IBP em 2020**.
- [ ] Incluir a implantação do **S&OE**. ⚠️ **Data:** o gestor falou "2026", mas a equipe corrigiu: **"foi ano passado… de julho de 2025 pra cá"**. Usar **jul/2025** (confirmar com ele).
- [ ] No **slide 6**, adicionar **"Futuro"** em **pontilhado**, com **3 caixinhas separadas**: **PPDS**, **Response & Supply** e **ATP**.
- [ ] Deixar explícito em algum lugar: *"implantamos o IBP para suportar o processo de planejamento de demanda / S&OP e permitir implantar o S&OE"*.

## 3. Dados institucionais (slides 3, 4 e 5)
- [ ] **Remover o slide 4** e **juntar os slides 3 e 5**.
- [ ] Sintetizar como ele fez no SAP NOW: **mapa das empresas** com os **dados do grupo ao lado** (faturamento, volume, base de clientes, fornecedores, empregos diretos e indiretos). Ele indicou que parte disso pode sair para ganhar espaço.
- [ ] Adicionar uma **"bolinha" com o número de SKUs tratados no planejamento**. No material dele: **~4.800 SKUs** (principais matérias-primas + produtos acabados, base puxada e sem duplicatas). Refazer a contagem. Se der o mesmo número, só repetir.
- [ ] O material dele está **desatualizado**: **manter os números da versão atual**, que vieram direto da Comunicação.

## 4. Slides 7, 8 e 9 (manter)
- [ ] **Slide 7, "Fatores para seleção do IBP"**: manter. **Ajustar o layout**: o texto dentro das bolinhas está pequeno demais, quase não dá para ler.
- [ ] **Slide 8, módulos implementados**: manter.
- [ ] **Slide 9** (contexto/texto): manter.
- [ ] **Exemplos visuais de uso da ferramenta**: conferir os do SAP NOW. O Interlocutor 2 disse que já colocou exemplos mais recentes.

## 5. Novo visual: áreas envolvidas no processo
- [ ] Criar um visual (**não um organograma**, para não passar ideia de hierarquia) com as **áreas envolvidas hoje no planejamento integrado**: **PCP, Logística, Comex, Comercial** (e outras, se houver).
- Objetivo: mostrar a **estrutura atual do processo**. Ele vai explicar que hoje o modelo é **um pouco descentralizado**.

## 6. S&OE: exemplos visuais (faltando)
- [ ] Incluir **telas de exemplo do S&OE**: os **planos semanais** e as visões semanais com o **sinal de exclamação** que indica onde **possivelmente vai haver gargalo**.
- Mensagem: com o S&OE existe um **plano de operações semanal** que gera **alertas**, e a equipe consegue **se antecipar** e discutir cenários (ajuste na venda ou ajuste na operação). Isso traz visões que antes não existiam.

## 7. S&OP: transformar ganho operacional em ganho de negócio
- [ ] Hoje os benefícios aparecem como **ganho de processo** (redução de tempo, ex.: **planejamento de demanda de 9 para 5 dias**, ferramentas, automações). Ele **não quer** passar a ideia de *"investimos 4 milhões só para reduzir de 9 para 5 dias"*.
- [ ] Mostrar o **ganho para o negócio e para o Comercial**: plano de vendas e operações mais assertivo e aumento do nível de serviço ao cliente.
- [ ] Incluir **gráfico da evolução do OTIF** e **gráfico da evolução da assertividade (acurácia) da previsão**.
  - ⚠️ Ponto do Interlocutor 1: **checar o dado e a série histórica** para sustentar a narrativa. Houve uma **queda de OTIF que não teve relação com o processo**.
  - Narrativa combinada: a melhoria nos indicadores **não é exclusiva** do IBP ou do processo. Falar sempre em **contribuição**, junto com outras iniciativas da empresa.
- [ ] Traduzir em benefício as **ferramentas estatísticas (8 modelos, 5 mil combinações)**. Explicação dada: antes a estatística e o ajuste de outliers eram feitos no **nível macro/linha**, reproduzindo o erro embutido. Agora a correção e a estatística são feitas **no menor nível** e depois **agregadas**.
- [ ] Destacar (pedido do Interlocutor 1): o **módulo de demanda teve pouquíssimo atrito** na implantação, porque **o processo já existia e rodava bem** (colaboração, reuniões, estatística, ainda que em Excel e em pedaços). A ferramenta trouxe um upgrade sem precisar reinventar nada. Isso foi uma **alavanca de sucesso** e evita a leitura de que "era tudo mato e a ferramenta salvou tudo".
- Ainda pendente: o gestor quer que a equipe **explique o slide de resumo de benefícios em dias** (ele marcou como "vou ver com vocês").

## 8. Entregável imediato: roteiro
- [ ] **Roteiro escrito ou falado (áudio), slide por slide**, como se a equipe estivesse apresentando ponto a ponto. Ele vai ler ou ouvir no avião.
- Quem monta: Interlocutor 2 com ajuda de outro colega (nome incerto: "maneiro/Lopes" na transcrição enviada, "Lobby" no Whisper). Enquanto isso, outra pessoa faz os ajustes nos slides (Whisper: "o André vai fazer os ajustes").
- O gestor está enviando dados que já estão prontos para a equipe puxar.

---

## Divergências entre as transcrições (conferir)
| Ponto | Transcrição enviada | Whisper large-v3 | Leitura sugerida |
|---|---|---|---|
| Ano de início do S&OE | "inclui 2026" | "em 2026, não foi? Foi… de 2025 pra cá" | **jul/2025** |
| Slide 9 | "Coloca esse slide com texto" | "Coloca esse slide, o contexto" | Slide de contexto, manter |
| Futuro (slide 6) | "ppds response supply o ATP" | "PPDS, Responsify, o ATP" | PPDS / Response & Supply / ATP |
| Áreas | "PCP, logística, Comex, comercial" | "ECP, logística, COMEX comercial" | **PCP** |
| Quem estará na apresentação | "o orgulho vai estar lá" | "a Ruda vai estar lá" | uma pessoa específica (nome incerto) |
| Nomes citados | "Cintia", "Uai", "Sérgio", "maneiro/Lopes" | "Beto", "Lobby", "André" | Nomes não confiáveis em nenhuma das duas |
| 05:54 | "fatores para seleção de BP" | "fatores para seleção do IBP" | **IBP** |

Trechos ininteligíveis nas duas versões: 02:00–02:25 e 09:00–09:50 (conversa paralela sobre outra empresa com "2 mil e tantas key figures", que não parece ser solicitação).
