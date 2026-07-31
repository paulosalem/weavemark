const SAFE_LINK = /^(https?:|mailto:)/i;

export function renderMarkdown(source) {
  const escaped = escapeHtml(String(source || "")).replace(/\r\n?/g, "\n");
  const blocks = escaped.split(/\n{2,}/).map((block) => {
    if (/^#{1,3}\s/.test(block)) {
      const [, marks, text] = block.match(/^(#{1,3})\s+([\s\S]*)$/);
      const level = Math.min(4, marks.length + 2);
      return `<h${level}>${inline(text)}</h${level}>`;
    }
    if (block.split("\n").every((line) => /^[-*]\s+/.test(line))) {
      return `<ul>${block.split("\n").map((line) => `<li>${inline(line.slice(2))}</li>`).join("")}</ul>`;
    }
    if (/^```/.test(block) && /```$/.test(block)) {
      return `<pre><code>${block.replace(/^```[^\n]*\n?/, "").replace(/\n?```$/, "")}</code></pre>`;
    }
    return `<p>${inline(block).replace(/\n/g, "<br>")}</p>`;
  });
  return blocks.join("");
}

export function safeUrl(value) {
  try {
    const url = new URL(value, location.href);
    return SAFE_LINK.test(url.protocol) ? url.href : null;
  } catch {
    return null;
  }
}

export function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[character]);
}

function inline(value) {
  return value
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_match, label, target) => {
      const decoded = target.replaceAll("&amp;", "&");
      return SAFE_LINK.test(decoded)
        ? `<a href="${target}" target="_blank" rel="noopener noreferrer">${label}</a>`
        : `${label} (${target})`;
    });
}
