# Pendências do Samuel

Anotado em 10/11/2026. Quando o Samuel pedir "verifica as pendências", começar por aqui.

## Situação em 13/11
- **A impressora deu defeito em 12/11.** O Samuel passou a noite tentando e não conseguiu imprimir nada. Antes de qualquer pedido, consertar a máquina.
- **Os brindes de 19/11 estão em risco**, porque o prazo de impressão era 17/11. Se a máquina não voltar até 15/11, reduzir o brinde (menos peças ou uma peça mais rápida).
- A tia Karina está atrasada (era para 10/11).

## 0. Resumo (atualizado em 12/11)
| Cliente | Pedido | Status |
|---|---|---|
| Humberto | Placa de mesa SOE/SNOI/SNOP, besouro, moldura, cantoneiras, **9 troféus** | **Confirmou que quer o orçamento de tudo.** Fazer o orçamento único (itens 1, 1b, 1c, 1g) |
| Patrícia | 5 pias de água benta personalizadas | Falar com ela: modelos e nomes dos casais (item 1f) |
| João Vasconcelos | "Dummy" + peças de aquário | Pegar a imagem no WhatsApp e entender o pedido (item 1e) |
| Tia Karina | Peças geométricas azul e amarelo | Terminar e precificar com 2 rolos (item 1d) |
| Confraternização 19/11 | 30 brindes | Decidir o modelo e imprimir até 17/11 (item 2) |

## 1. Placa de mesa do Humberto (setor SOE)
- **Pedido:** o Humberto quer uma placa de mesa do setor. Ele já tem uma escrita "SOP" e quer algo na mesma linha com as siglas SNOI e SNOP.
- **Objetivo nosso:** entregar algo mais bonito que a placa atual e divulgar a nossa marca. É vitrine, então vale caprichar.
- **Referência que o Samuel gostou:** as placas de mesa de médico, com o nome em cima, o símbolo no meio e o curso embaixo.
- **Proposta de layout:**
  - em cima, as siglas em destaque (ex.: S&OP · S&OI);
  - no centro, um símbolo de planejamento integrado (ex.: setas em ciclo fechado ou engrenagem com gráfico);
  - embaixo, "Planejamento Integrado";
  - na base ou atrás, a nossa marca pequena, com tag NFC que abre o nosso Instagram ("encoste o celular").
- **Confirmar com o Humberto antes de modelar:**
  1. Grafia exata das siglas: SNOI/SNOP ou S&OI/S&OP? E onde entra o SOE (S&OE)?
  2. Se leva o nome dele ou só o setor.
  3. Cores: as da empresa ou as nossas, conforme o filamento em estoque.
  4. Tamanho da mesa ou da placa atual. Pedir uma foto.
- **Próximo passo:** o Claude faz 2 ou 3 opções de layout em imagem para o Samuel mostrar ao Humberto.

## 1b. Humberto: besouro e moldura (pedido separado da placa)
- **Pedido:** além da placa, o Humberto quer um **besouro** e uma **moldura**. As referências ele mandou no WhatsApp; o Samuel vai enviar as fotos.
- **O Samuel quer fazer o fundo.** Confirmar se é o fundo da moldura (a parte de trás ou o painel atrás da foto) ou um fundo/base para o besouro.
- **Faltam:** as fotos de referência, as medidas, as cores, e se o besouro é decorativo ou se leva NFC.
- **Próximo passo:** com as fotos, o Claude descreve as peças (formato, medidas, cores, tempo e custo estimados no fatiador) e monta um orçamento junto com a placa.

## 1c. Humberto: cantoneiras para colar moldura (pedido separado)
- **Pedido:** peças de canto em L que seguram a moldura no esquadro (90°) enquanto a cola seca, uma em cada canto. São 4 por moldura.
- **Referência:** desenho dele mostrando uma moldura retangular com as 4 cantoneiras em L encaixadas por fora dos cantos. A foto está em `dados/referencias/humberto-cantoneira-moldura.jpg` (fora do git, porque aparece documento do trabalho ao fundo).
- **Modelo:** ele diz que existe pronto no MakerWorld (Bambu Lab). Buscar por "picture frame corner clamp" ou "frame gluing corner" e escolher o que bate com o desenho.
- **Falta:** ele vai passar as medidas: largura e altura do perfil da moldura e a espessura. Não modelar nem imprimir antes disso.
- **Dica de impressão:** PETG ou PLA com 4 paredes, para não abrir quando apertar. Incluir um rebaixo no canto interno para a cola que escorrer não grudar na peça.

## 1g. Humberto: 9 troféus temáticos (pedido de 11/11 no WhatsApp)
- **Pedido:** "um troféu de cada" seguindo a referência que ele mandou. São 9 ícones pretos, cada um sobre uma base redonda:
  1. Engrenagem com `</>` e chave inglesa (desenvolvimento/TI)
  2. Escudo com aperto de mão
  3. Capelo de formatura com personagem de anime segurando livro
  4. Sol sorrindo com calculadora e gráfico de barras subindo
  5. Xícara de café com óculos
  6. Capacete de corrida com bandeira quadriculada
  7. Camaleão no galho
  8. Haltere com folha, óculos redondos e raio
  9. Pessoa lendo livro com relógio atrás
- **Medidas:** 12 cm de altura total e base de 2,5 cm. Na imagem de referência, os 2,5 cm são a altura da base redonda.
- **Resposta do Samuel na hora:** "É possível, vou ver aqui a possibilidade". Ele está esperando o orçamento.
- **Referência:** `dados/referencias/humberto-trofeus.jpg` (fora do git, porque o print mostra uma reunião do trabalho).
- **Confirmar com ele:**
  1. Se é 1 de cada (9 no total).
  2. Se leva nome ou título na base (ex.: nome da pessoa ou "Melhor do ano").
  3. Se é tudo preto como na imagem ou se a base tem outra cor.
  4. O prazo (é para a confraternização de 19/11?).
- **Produção:** é uma cor só, o que facilita. O ícone é chapado (formato de silhueta, extrudado), então dá para modelar a partir da imagem: vetorizar cada silhueta, extrudar uns 8 a 10 mm e encaixar na base. Para não quebrar, as partes finas (óculos, chave, raio, bandeira) precisam de pelo menos 2 mm de espessura. Procurar também modelos prontos parecidos no MakerWorld.
- **O item 8 lembra Harry Potter** (óculos redondos + raio). Para presente particular não tem problema; não usar isso em produto para vender.

## 1d. Tia Karina (tia da Amanda): peças geométricas — terminar hoje (10/11)
- **Pedido:** as peças geométricas dela. O projeto já existe em um dos projetos do Claude ou do Claude Code; procurar lá antes de começar do zero.
- **Cores:** só azul e amarelo. Não temos essas cores, então é preciso comprar 2 rolos de filamento só para esse pedido.
- **Preço:** tem que cobrir os 2 rolos inteiros, e não só os gramas usados, mais o custo normal (tag, energia, perda) e a margem. Ela pode pagar.
- **A fazer quando o Samuel pedir:** achar o projeto, terminar, calcular o preço com os 2 rolos embutidos e, se ele quiser, imprimir uma peça de teste.
- Só anotado. Não executar nada sem o Samuel pedir.

## 1e. João Vasconcelos: "dummy" e peças de aquário
- **Pedido 1:** um "dummy". A imagem de referência está no WhatsApp. Confirmar o que é exatamente (boneco, peça de teste, manequim?) quando abrir a imagem.
- **Pedido 2:** peças de aquário (separado do dummy).
- **Atenção no aquário:** se a peça fica dentro da água, usar PETG (PLA amolece e degrada com o tempo) e evitar cores ou aditivos duvidosos. Perguntar se há peixe, para não soltar nada tóxico.
- **Falta:** as imagens (no WhatsApp), as medidas e a quantidade.
- **Próximo passo:** quando o /backlog-whatsapp rodar, salvar as imagens em `dados/referencias/` e montar o orçamento.

## 1f. Patrícia (cliente da pia de água benta): 5 unidades
- **Pedido:** 5 pias de água benta personalizadas com os nomes dos casais.
- **Falar com ela antes de qualquer coisa:**
  1. Quais modelos ela quer (o mesmo da anterior ou outros?).
  2. Os nomes de cada casal, com a grafia exata.
  3. As cores.
  4. O prazo (é para alguma data, casamento ou batizado?).
- **Preço:** usar o valor da peça anterior como base e oferecer preço por quantidade para as 5.
- **Próximo passo:** o Claude prepara a mensagem para o Samuel mandar para ela com essas perguntas.

## 2. Brindes para a confraternização de 19/11 (quinta-feira)
- **Quantidade:** 30 brindes pequenos com a nossa marca.
- **Prazo:** tudo impresso até 17/11, para sobrar margem para falha de impressão. Só temos uma impressora.
- **Opções, da mais recomendada para a menos:**
  1. **Chaveiro com a logo e tag NFC que abre o nosso Instagram.** É brinde e demonstração do produto ao mesmo tempo: a pessoa encosta o celular e conhece a gente. Pequeno, rápido de imprimir, várias peças por mesa. Se o custo da tag pesar, colocar NFC em parte deles e QR no resto.
  2. **Suporte de celular de mesa** com a logo. É útil e fica na mesa à vista de todos, mas gasta mais filamento e mais tempo de máquina.
  3. **Marcador de página ou ímã de geladeira** com a logo. É o mais barato e o mais rápido, mas é o que menos marca.
- **Antes de decidir:** fatiar o chaveiro e o suporte, anotar gramas e tempo por peça, e calcular custo e horas de máquina para 30 unidades com a fórmula do `BRIEFING.md` ("Custo e preço").
- **Junto com o brinde:** um cartãozinho ou etiqueta com @ do Instagram e WhatsApp, e a frase "a gente faz placas com NFC para o seu negócio".

## 2b. Ideia: anunciar no Mercado Livre, Shopee e Elo7
- Começar com 3 a 5 anúncios de produto personalizado: placa de mesa por profissão, placa NFC para pequeno negócio, kit de chaveiros com nome ou logo.
- Antes de definir o preço, conferir a tarifa e o custo fixo no simulador do Mercado Livre (Clássico em torno de 10% a 14%).
- Abrir o MEI se as vendas engrenarem.

## 3. Em aberto do plano da semana (`BRIEFING.md`)
- Leads do Google Maps e backlog do WhatsApp: rodar no Claude Code local. O PC caiu e precisa reconectar.
- Preço (Fase 0.3): falta o Samuel mandar os gramas e o tempo do fatiador, o preço do kg de filamento, o preço da tag, o modelo da impressora, o kWh da Enel e as cores em estoque.
