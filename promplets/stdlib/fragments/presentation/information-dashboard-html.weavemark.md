@promplet version: 0.7

@module weavemark.std.presentation.information_dashboard_html

@note
  Reusable semantic packaging instructions for turning a completed Markdown
  report into a polished, standalone HTML information dashboard. Invoke with
  `@package instructions: module:weavemark.std.presentation.information_dashboard_html`.
  The packaging runtime supplies the engine's canonical report as @{output}.

@output enforce: strict
  Return exactly one complete HTML5 document. Its first non-whitespace text MUST
  be `<!doctype html>` and its final non-whitespace text MUST be `</html>`.
  Include no Markdown fence, explanation, preamble, or trailing commentary.

Transform the completed Markdown report below into an exceptional standalone
HTML information dashboard. Preserve its meaning, evidence, qualifications,
source URLs, and uncertainty. Do not add facts, metrics, dates, quotations,
citations, or links that are absent from the report.

<source-report>
@{output}
</source-report>

Design direction:
- Aim for the calm authority of a premium research publication combined with
  the scanability of a modern analytical dashboard.
- Use a restrained mineral palette: near-black navy, warm paper, slate, a
  precise emerald accent, and sparing copper for attention. Maintain WCAG AA
  text contrast.
- Establish a strong editorial hierarchy: compact eyebrow, decisive title,
  concise deck, then a responsive overview grid. Use card-like sections where
  they improve scanning, not as decoration around every paragraph.
- Surface only report-supported key figures in a compact metric strip. Pair
  every figure with its unit, period, and qualifier when available. Never infer
  a missing unit or timeframe.
- Make evidence, uncertainty, tensions, risks, and next-investigation items
  visually distinct. Use honest labels such as "Reported", "Search evidence",
  "Uncertain", and "Next check" only when the source supports them.
- Render comparison-heavy material as readable tables on wide screens and
  stacked labeled rows on narrow screens. Keep long URLs from breaking layouts.
- Preserve valid source URLs as clearly named links. Add
  `target="_blank" rel="noopener noreferrer"` to external links. Never invent
  link destinations.

Document requirements:
- Emit semantic HTML5 with `header`, `main`, `section`, `article`, `table`,
  `aside`, and `footer` where appropriate. Include a skip link and logical
  heading order.
- Include all CSS in one `<style>` element. Use no scripts, frameworks,
  external fonts, external stylesheets, images, SVG, canvas, or network-loaded
  assets. Use a system-font stack with tabular numerals for quantitative data.
- Include `<meta charset="utf-8">`, a responsive viewport meta tag, a concise
  title, and a restrictive Content Security Policy that blocks scripts,
  objects, frames, connections, forms, and base-URI changes while allowing only
  the document's inline styles.
- Use CSS Grid and Flexbox for a fluid layout with a generous maximum reading
  width. At approximately 900px and 640px, collapse multi-column regions
  gracefully without hiding content or requiring horizontal page scrolling.
- Treat zero page-level horizontal overflow at a 320px viewport as a hard
  requirement. Set `min-width: 0` on grid/flex children, use
  `minmax(0, 1fr)` for shrinkable tracks, and apply `overflow-wrap: anywhere`
  to URLs, raw values, and other unbroken strings. If tables become stacked
  labeled rows, their value track must also be `minmax(0, 1fr)`.
- Use subtle borders, tonal surfaces, careful spacing, and restrained shadows.
  Avoid gradients, glassmorphism, excessive pills, oversized hero typography,
  novelty icons, fake charts, decorative gauges, and animation.
- Provide highly legible hover and keyboard-focus states. Respect
  `prefers-reduced-motion`. Do not communicate status through color alone.
- Add print styles that remove shadows, preserve source URLs, avoid splitting
  cards and table rows when practical, and produce clean A4/Letter output.
- End with a compact methodology/source note and retain any educational or
  financial disclaimer from the report. If none exists, do not invent one.

Content rules:
- Adapt the section layout to the supplied report rather than forcing empty
  dashboard modules.
- Convert Markdown structure faithfully. Keep substantive caveats near the
  claims they qualify.
- Do not expose these transformation instructions or the `<source-report>`
  wrapper in the document.

Output only the complete HTML document.
