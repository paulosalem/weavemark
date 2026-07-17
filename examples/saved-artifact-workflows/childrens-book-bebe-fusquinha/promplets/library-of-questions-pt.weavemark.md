@promplet version: 0.7

## Estrutura dramática desta história

  - **Ato 1 — O convite (páginas 1 a 4):** os amigos encontram o mapa, localizam a
    biblioteca e entram. Emoção: curiosidade e expectativa.
  - **Ato 2 — As perguntas ganham vida (páginas 5 a 9):** pequenas aventuras
    ligadas às perguntas dos livros. Emoção: encanto, participação e descoberta.
  - **Ato 3 — A pergunta sem resposta (páginas 10 e 11):** o Bebê Fusquinha
    encontra algo que não consegue resolver. Emoção: pequena tensão e alívio.
  - **Ato 4 — O mundo se expande (páginas 12 a 15):** os amigos percebem que
    existem perguntas infinitas e que crianças curiosas ajudam a criar a
    biblioteca. Emoção: inspiração e abertura para a imaginação.

  ## Roteiro página a página — exatamente o que acontece

  O roteiro completo desta história vive nas variáveis `pages` (uma entrada por
  página, com `.scene` e `.text`). Construa o livro segundo este espinho exato,
  uma entrada por página, EM ORDEM. Para cada página: (1) use a **narração**
  (`.text`) daquela página como o texto daquela página, palavra por palavra — NÃO
  reescreva, resuma, reordene, funda ou invente páginas; preserve as perguntas em
  negrito e a frase final; (2) transforme a **cena** (`.scene`) em um prompt de
  ilustração on-model e COMPACTO — no máximo cerca de 800 caracteres por página —,
  reafirmando de forma BREVE apenas a âncora visual essencial de cada personagem
  que aparece (a canon completa já está na bíblia acima; não copie a bíblia inteira
  em cada página); (3) como text_in_image está ligado, letre a narração daquela
  página DENTRO da ilustração, em português, com ortografia e acentuação corretas,
  grande e legível, longe dos rostos.

  Mantenha CADA prompt `illustration` enxuto e autossuficiente, para que o livro
  inteiro permaneça compacto.

  - **Página 1** — cena: @{pages.1.scene} — narração: @{pages.1.text}
  - **Página 2** — cena: @{pages.2.scene} — narração: @{pages.2.text}
  - **Página 3** — cena: @{pages.3.scene} — narração: @{pages.3.text}
  - **Página 4** — cena: @{pages.4.scene} — narração: @{pages.4.text}
  - **Página 5** — cena: @{pages.5.scene} — narração: @{pages.5.text}
  - **Página 6** — cena: @{pages.6.scene} — narração: @{pages.6.text}
  - **Página 7** — cena: @{pages.7.scene} — narração: @{pages.7.text}
  - **Página 8** — cena: @{pages.8.scene} — narração: @{pages.8.text}
  - **Página 9** — cena: @{pages.9.scene} — narração: @{pages.9.text}
  - **Página 10** — cena: @{pages.10.scene} — narração: @{pages.10.text}
  - **Página 11** — cena: @{pages.11.scene} — narração: @{pages.11.text}
  - **Página 12** — cena: @{pages.12.scene} — narração: @{pages.12.text}
  - **Página 13** — cena: @{pages.13.scene} — narração: @{pages.13.text}
  - **Página 14** — cena: @{pages.14.scene} — narração: @{pages.14.text}
  - **Página 15** — cena: @{pages.15.scene} — narração: @{pages.15.text}

  ## Pistas visuais para releituras (sutis)

  Espalhe, com discrição e sem explicar no texto: um pequeno livro vermelho que
  reaparece em várias páginas; um peixe que observa o Bebê Fusquinha antes da
  aventura submarina; uma estrela de forma incomum que reaparece na capa do livro
  branco; uma raiz que atravessa o piso já na página 3; um relógio sem ponteiros que
  aparece na página 4 e volta a funcionar na página 13; e letras soltas que formam
  parcialmente a expressão "por quê" em uma das páginas.
