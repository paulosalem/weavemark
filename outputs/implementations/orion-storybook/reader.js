const pages = [
  {
    alt: "Orion, a small purple dragon, watches other young dragons make fire in a sunny green valley.",
    caption: "Every young dragon was learning to make fire — every dragon but Orion.",
  },
  {
    alt: "Orion squeezes his eyes shut and blows, producing only a chilly grey puff and a hiccup.",
    caption: "He puffed with all his might. Out came smoke — and a hiccup.",
  },
  {
    alt: "Orion sneezes harmless sparkles and looks discouraged when no flame appears.",
    caption: "A sprinkle of sparkles, but no fire at all.",
  },
  {
    alt: "Mama Dragon kneels beside Orion and gently asks what he thinks fire needs.",
    caption: "Do not force it, Mama says. Be a fire detective.",
  },
  {
    alt: "Orion and Mama watch a breeze make a campfire grow taller and brighter.",
    caption: "Air! Fire loves a big breath.",
  },
  {
    alt: "Mama flicks a bright spark while Orion wonders where his own spark might be.",
    caption: "Fire needs a spark to begin — but where is Orion's?",
  },
  {
    alt: "Orion tries a large belly breath and makes a warmer puff of smoke, grinning at the progress.",
    caption: "Warmer this time. Still no flame — but closer.",
  },
  {
    alt: "Orion cups his paws around Pip, a tiny shivering orange bird, during a cold gust.",
    caption: "Orion forgets about showing off and tries to warm his friend.",
  },
  {
    alt: "A gentle golden flame appears as Orion breathes warmly toward Pip, lighting their delighted faces.",
    caption: "His heart glows with kindness — and whoosh, a small golden flame.",
  },
  {
    alt: "Pip nestles by Orion's little flame while Orion smiles with quiet understanding.",
    caption: "His spark was the warm, curious feeling glowing inside him.",
  },
  {
    alt: "Orion practices across the meadow, progressing from wobbly sparks to a steady flame.",
    caption: "A wobble here, a whoosh there — every flame grows braver.",
  },
  {
    alt: "Orion helps a smaller worried dragon become a fire detective while Mama and Pip watch.",
    caption: "Do not force it. Let us be fire detectives — together.",
  },
];

const cover = document.querySelector("#cover");
const pageView = document.querySelector("#pageView");
const image = document.querySelector("#pageImage");
const caption = document.querySelector("#pageCaption");
const status = document.querySelector("#pageStatus");
const previous = document.querySelector("#previousButton");
const next = document.querySelector("#nextButton");
const start = document.querySelector("#startButton");

let current = 0;

function render() {
  const onCover = current === 0;
  cover.hidden = !onCover;
  pageView.hidden = onCover;
  previous.disabled = onCover;

  if (onCover) {
    status.textContent = "Cover · 12 illustrated pages";
    next.textContent = "Start";
    location.hash = "cover";
    window.scrollTo({ top: 0, behavior: "auto" });
    return;
  }

  const page = pages[current - 1];
  image.src = `./pages/page-${current}.jpg`;
  image.alt = page.alt;
  caption.textContent = page.caption;
  status.textContent = `Page ${current} of ${pages.length}`;
  next.textContent = current === pages.length ? "Back to cover" : "Next";
  location.hash = `page-${current}`;
  window.scrollTo({ top: 0, behavior: "auto" });
}

function advance() {
  current = current === pages.length ? 0 : current + 1;
  render();
}

function retreat() {
  current = Math.max(0, current - 1);
  render();
}

function readHash() {
  const match = location.hash.match(/^#page-(\d+)$/);
  if (match) current = Math.min(pages.length, Math.max(1, Number(match[1])));
  else current = 0;
  render();
}

start.addEventListener("click", advance);
next.addEventListener("click", advance);
previous.addEventListener("click", retreat);
window.addEventListener("hashchange", readHash);
window.addEventListener("keydown", (event) => {
  if (event.key === "ArrowRight" || event.key === "PageDown") advance();
  if (event.key === "ArrowLeft" || event.key === "PageUp") retreat();
  if (event.key === "Escape") {
    current = 0;
    render();
  }
});

readHash();
