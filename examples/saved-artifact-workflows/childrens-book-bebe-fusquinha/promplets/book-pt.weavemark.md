@promplet version: 0.7

@note
  MAIN STORY FILE — "O Bebê Fusquinha e a Biblioteca Perdida das Perguntas", a
  15-page Portuguese picture book, expressed FULLY in WeaveMark (authoring, an
  illustrated COVER, per-page rendering, and packaging into a print-ready book),
  with no external script.

  This is the concrete story: its page-by-page SCRIPT lives in the companion vars
  (`pages` — one entry per page, each with a `.scene` and a `.text`), and it
  REFINES the local named character-universe module — so the
  cast, palette, and continuity come from the bible, and only this adventure's
  beats live here.

  Stage `author` @refines the illustrated-story-core (picture-book format, pinned),
  the local Bebê Fusquinha universe module, and a local path-based story fragment,
  then emits the
  STRICT JSON book (title + 15 pages, each with a self-contained illustration prompt
  and its narration). The narration text of every page is FIXED — it must be lettered
  verbatim, in Portuguese, into each illustration (text_in_image on).

  Stage `cover` renders ONE illustrated book cover (not part of the script) and
  persists it to `cover.png`. Stage `page` is REPEATED once per page
  (repeat: page, count: @{page_count}), rendering each page's full illustration to
  `pages/page-@{index}.png`. The two `@package` steps then assemble a print-ready
  HTML book (opening with the illustrated cover) and a PDF converted from it.

  Companion vars (`../pt/inputs/vars.json` from this example family) set language,
  page_count,
  audience, tone, art_style, premise, lessons, the image controls, title, and
  cover_image — AND the page-by-page `pages` beat sheet: a JSON object keyed by page
  number ("1".."@{page_count}"), each with a `.scene` (what the illustration shows)
  and a `.text` (the fixed narration to letter onto that page). The author stage
  reads them via dotted paths (@{pages.1.scene}, @{pages.1.text}, …). The reusable
  universe lives beside this entrypoint as the local module
  `examples.baby_bug.universe`.

@execute chain
  repeat: page
  count: @{page_count}

@prompt author
  @refine module:weavemark.domains.creative.illustrated_story_core
    with story_format: "picture-book"

  ## Universo dos personagens — fonte canônica

  Use a bíblia a seguir como a fonte canônica do elenco, do mundo, do estilo visual
  e das regras de produção desta história. Reafirme por extenso a âncora visual de
  cada personagem em TODA ilustração em que ele aparecer; não reescreva
  personalidades, não altere cores ou proporções e não introduza vilões.

  @refine module:examples.baby_bug.universe mingle: false

  @refine ./library-of-questions-pt.weavemark.md mingle: false

@prompt cover
  @output type: image
    file: cover.png
    size: @{image_size}
    quality: @{image_quality}
    model: @{image_model}
  Você é o ilustrador da CAPA deste livro infantil. Renderize UMA capa ilustrada,
  encantadora e perfeitamente on-model, no estilo visual do universo canônico abaixo.

  @refine module:examples.baby_bug.universe mingle: false

  A capa deve:
  - reunir os três amigos — Bebê Fusquinha, Barco Baleião e Garfudo — reafirmando por
    extenso a âncora visual de cada um exatamente como descrita acima;
  - evocar a Biblioteca das Perguntas ao fundo — torres entre árvores enormes, luz
    dourada e livros luminosos flutuando — sem revelar o final da história;
  - manter a paleta do universo (azul-claro, azul profundo, turquesa, verde-esmeralda,
    dourado, amarelo quente, creme) e uma iluminação cinematográfica acolhedora;
  - letrar o TÍTULO do livro DENTRO da arte, grande e legível, em português, com
    ortografia e acentuação corretas, bem afastado dos rostos, exatamente assim:
    "@{title}".

  Produza SOMENTE a imagem da capa, sem comentários.

@prompt page
  @output type: image
    file: pages/page-@{index}.png
    size: @{image_size}
    quality: @{image_quality}
    model: @{image_model}
  Você é o ilustrador do livro infantil abaixo. Renderize a página @{index} de
  @{count} como UMA ilustração finalizada.

  Siga EXATAMENTE o prompt `illustration` daquela página — seu estilo de arte e a
  âncora visual reafirmada de cada personagem — para que a página fique perfeitamente
  on-model com o resto do livro. Como o prompt pede que a narração seja letrada na
  imagem, escreva aquelas palavras exatas, grandes e legíveis, em português e longe
  dos rostos. Produza SOMENTE a imagem, sem comentários.

  O livro completo autoral (JSON), para contexto e consistência entre páginas:
  @{author}

@package instructions: module:weavemark.domains.creative.picture_book_html file: book.html
@package from: book.html file: book.pdf
