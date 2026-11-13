# Vetores 2D e arquivos de impressão dos 9 troféus (método A)

Cada ícone é redesenhado por peças fechadas, com âncoras medidas em px na referência
(`../referencia/trofeus-referencia-hd.png`). Nenhum pixel vira geometria, então sombra e brilho não entram.

## Arquivos
- `trofeu-N-vetor.svg`: vetor em mm, camadas `BRANCO`, `PRETO` e `RELEVO` (oculta). x = 0 é o eixo da base; a borda de baixo é a linha de apoio.
- `trofeu-N-conferencia.png` e `trofeu-N-zoom-{topo,meio,base}.png`: referência | vetor | contorno do vetor sobre a referência, na mesma escala.
- `todos-os-9-vetores.png`: os 9 lado a lado.
- `3mf/trofeu-N-*.3mf`: peça para imprimir (partes `preto` e `branco`).
- `iconeN.py`: as peças de cada ícone. `vetor_lib.py`: curvas, booleanas, mínimos, ajuste Bézier, verificação. `gerar_3mf.py`: extrusão e pino.

## Como refazer
    python3 icone3.py        # gera SVG, PNGs e roda a verificação do troféu 3
    python3 gerar_3mf.py     # gera os 9 .3mf e mede o encaixe (ou: python3 gerar_3mf.py 3)

## Verificação automática (todo ícone precisa passar)
Preto com no mínimo 2 mm, branco com no mínimo 1,2 mm, contorno externo em peça única, sem pontinhos soltos, PRETO + BRANCO = contorno.

## Impressão (igual ao troféu 2 da v9 e ao `../v9/PADRAO-ENCAIXE.md`)
- Ícone com 95 mm de altura, deitado, costas na mesa. Preto com 14 mm de espessura; branco com 13 mm (1 mm rebaixado na frente).
- Pino de 30 x 8 x 8 mm em todos: x de -15 a +15 mm (centrado no eixo da base), rente às costas, 8 mm abaixo da linha de apoio. Serve na `base-padrao-2026.3mf`.
- No Bambu Studio: "carregar como objeto único com várias partes?" Sim. Parte `preto` no filamento preto, `branco` no branco.
- Sem chanfro/borda arredondada na frente: os .3mf são prismas retos, como o troféu 2 da v9.

## Decisões de desenho
- 1: filete branco de 1,4 mm em volta do monitor e da chave onde passam na frente de outra peça; pé único e reto sobre a base.
- 2: mangas lisas; polegar da mão de cima redesenhado mais fino (5 a 7 mm) e em linha contínua com o dorso; rodapé de 30 mm sob a ponta do escudo.
- 3: linhas de 1,4 mm no chapéu, cordão, nó da borla e faixa × corpo; halo de 2,8 mm; lado direito do halo em linha reta até a base.
- 4: filete só em volta da calculadora; seta fundida ao aro do sol; vãos entre as barras em branco; rodapé sob as barras.
- 5: óculos redesenhados (topo reto, lentes em meia elipse); pontas do vapor entram na borda da xícara.
- 6: bandeira 6 px mais alta que na referência para a borda não encostar no capacete; casas brancas com cantos redondos; filete branco entre capacete e bandeira.
- 7: todo preto, só o olho branco; cauda em espiral logarítmica regular; espiral e vãos entre patas e galho vazados.
- 8: placa branca retangular de cantos redondos (95 x 95 mm, centrada no eixo da base) com todos os elementos dentro.
- 9: franja em zigue-zague com linha de 1,4 mm; duas linhas de 1,4 mm na lombada; mostrador do relógio branco segurando os ponteiros.

## Acabamento das curvas
Arestas retas saem como retas exatas no SVG; cantos e curvas viram poucas Béziers com tangente herdada da reta vizinha.
Sobras de linha mais finas que 1,34 mm e pontinhos brancos menores que 4 mm² são eliminados automaticamente.
