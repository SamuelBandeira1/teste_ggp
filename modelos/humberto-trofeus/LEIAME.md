# Troféus do Humberto: versão 7 (13/11/2026)

Ícone impresso **deitado**, encaixado numa **base padrão** (a mesma para os 9). Preto e branco no AMS.
Prévias: `preview.png` (montados) e `preview-pecas.png` (ícone deitado com o pino; base com o encaixe).

## O que mudou desde a versão 1 (feedback da reunião de 13/11)
- Duas cores: o **fundo e a borda brancos** seguram as partes soltas (troféus 1, 2, 3, 4, 5 e 8). Os detalhes brancos ficam embutidos.
- **Camaleão (7):** todo preto, só o olho branco. **Capacete (6) e leitura (9):** pretos, sem fundo.
- **"2026" em branco** embutido na frente da base.
- **Base separada com encaixe padronizado** (ideia do Humberto): imprime as 9 bases iguais e os ícones deitados.

## Medidas
- Montado: 120 mm de altura. Base 25 mm (62 mm de diâmetro embaixo, 56 mm em cima). Pé do ícone 50 × 14 × 5 mm. Ícone 90 mm.
- Ícone: 14 mm de espessura. Frente com borda arredondada, costas retas (é o lado que vai na mesa).
- **Encaixe:** pino de 20 × 8 × 8 mm embaixo do pé; furo na base com 0,2 mm de folga de cada lado. Se ficar justo demais, lixar o pino; se ficar folgado, uma gota de cola.
- Embaixo da base: rebaixo de 26,5 × 1 mm para tag NFC adesiva de 25 mm (opcional).

## Como imprimir
- **Arquivos `.3mf`:** abrir no Bambu Studio. Se perguntar "carregar como objeto único com várias partes?", responder **Sim**. Depois atribuir as cores: parte `preto` → filamento preto, parte `branco` → branco.
- **Ícones:** já vêm deitados, costas na mesa. PLA, camada 0,2 mm, 3 paredes, 15% de preenchimento, **sem suporte**. Dá para pôr 2 ou 3 ícones por mesa.
- **Base:** em pé, como vem no arquivo. As 9 cabem numa mesa só (são iguais: copiar 9 vezes).
- **Testar primeiro:** 1 base + o ícone 5 (café). Conferir o encaixe antes de rodar o resto.
- **Filamento estimado:** ~570 g de preto e ~130 g de branco para os 9 com as bases (estimativa pela geometria; o número certo vem do fatiador). A troca de cor no AMS gasta mais um pouco de purga.

## Versão 7 (ferramentas profissionais)
- Contornos tirados da referência com o **VTracer** (vetorização em curvas), centrados no centro da base medido na referência.
- Volume feito no **Blender** (rodando na nuvem): extrusão exata, chanfro arredondado de 1,8 mm na frente, costas retas para a mesa.
- Peça assenta **direto na base** (sem pé). Pino de 30 × 8 × 8 mm escondido no encaixe; base cilíndrica de 66 mm com borda arredondada, "2026" em branco e rebaixo para NFC.
- O pino é uma casca separada dentro do mesmo objeto: o fatiador une as duas. Se o Bambu Studio avisar de "malha com erros", aceitar o reparo automático.
- Leitor (9) segue o desenho vetorial da v6.
- Scripts em `v7-pipeline/` (camadas.py → build7.py → render7.py).

## Versão 5 (acabamento)
- Contornos convertidos em curvas suaves (antes eram tirados dos pixels, com cantos tortos) e malha mais fina (0,25 mm).
- Escudo com contorno simétrico; riscos de brilho da referência removidos.
- **Leitor (9) redesenhado do zero em vetor**, simétrico: cabeça redonda, franja com três pontas em curva, rosto branco com olhos fechados espiando por cima do livro, livro aberto com lombada, borda das folhas e linhas de texto, relógio com ponteiros arredondados.
- Partes pretas cercadas de branco (ponteiros do relógio, olhos) ficam presas no branco, sem pontes extras.
- Sem furinho entre o ícone e o pé.

## Versão 4
- Refeito a partir da imagem de referência em alta resolução (contornos mais limpos).
- **Camaleão vazado** como na foto (só o olho branco).
- **Livro (9):** linhas brancas desenhadas à mão para a borda das páginas, a lombada, as linhas do texto e a franja do cabelo (na referência isso só aparece por sombra).

## Pontos fracos (ver com o Humberto)
- O 3 (anime) e o 6 (capacete) têm detalhes pequenos.

## Arquivos
- `trofeu-N-*.3mf`: ícones (deitados). `base-padrao-2026.3mf`: base.
- `gerar_v5.py` (usa `gerar_v3_encaixe.py` e `gerar_v2_cores.py`): gera tudo de novo. Medidas no topo dos arquivos. Precisa da imagem de referência em alta, em tons de cinza, como `ref_hd.png` ao lado do script.
