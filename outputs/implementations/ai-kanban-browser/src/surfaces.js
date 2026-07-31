import { escapeHtml, renderMarkdown, safeUrl } from "./markdown.js";

export function renderSurface(output, { compact = false } = {}) {
  const article = document.createElement("article");
  article.className = `surface surface-${output.type}${compact ? " surface-compact" : ""}`;
  article.dataset.status = output.status;
  article.innerHTML = `
    <header>
      <span class="surface-type">${icon(output.type)} ${escapeHtml(output.type)}</span>
      <span class="status-label">${escapeHtml(output.status)}</span>
    </header>
    <h4>${escapeHtml(output.title)}</h4>
    <div class="surface-content"></div>
    <footer>
      <span>${escapeHtml(output.owner || "workspace")}</span>
      <span>${escapeHtml(formatDate(output.updatedAt || output.createdAt))}</span>
    </footer>
  `;
  const body = article.querySelector(".surface-content");
  renderContent(body, output, compact);
  if (!compact) appendActions(article, output);
  return article;
}

function renderContent(body, output, compact) {
  const content = String(output.content ?? output.payload ?? "");
  if (output.type === "text") {
    body.className += " markdown";
    body.innerHTML = renderMarkdown(compact ? excerpt(content, 220) : content);
    return;
  }
  if (output.type === "status") {
    body.innerHTML = `<p class="status-surface">${escapeHtml(content)}</p>`;
    return;
  }
  if (output.type === "link") {
    const href = safeUrl(content);
    body.innerHTML = href
      ? `<a href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">${escapeHtml(output.label || content)}</a>`
      : `<p class="unsafe-content">Link unavailable: ${escapeHtml(content)}</p>`;
    return;
  }
  if (output.type === "table") {
    renderTable(body, content, compact);
    return;
  }
  if (output.type === "image") {
    const href = safeImageUrl(content);
    body.innerHTML = href
      ? `<button class="image-preview" type="button" aria-label="Zoom ${escapeHtml(output.title)}"><img src="${escapeHtml(href)}" alt="${escapeHtml(output.altText || output.title)}"></button>`
      : `<p class="unsafe-content">Image reference is unavailable.</p>`;
    body.querySelector("button")?.addEventListener("click", () => {
      body.classList.toggle("is-zoomed");
    });
    return;
  }
  if (output.type === "diff") {
    body.innerHTML = `<pre class="diff-view">${content.split("\n").slice(0, compact ? 8 : 300).map((line) => {
      const kind = line.startsWith("+") ? "add" : line.startsWith("-") ? "remove" : "context";
      return `<span data-kind="${kind}">${escapeHtml(line)}</span>`;
    }).join("\n")}</pre>`;
    return;
  }
  if (output.type === "file") {
    const metadata = parseObject(content);
    body.innerHTML = `
      <dl class="file-metadata">
        <div><dt>Path</dt><dd>${escapeHtml(metadata?.path || content)}</dd></div>
        <div><dt>Media type</dt><dd>${escapeHtml(metadata?.mediaType || "Unknown")}</dd></div>
        <div><dt>Size</dt><dd>${escapeHtml(metadata?.size || "Unknown")}</dd></div>
      </dl>`;
    return;
  }
  body.innerHTML = `<pre><code>${escapeHtml(compact ? excerpt(content, 260) : content)}</code></pre>`;
}

function renderTable(body, content, compact) {
  const parsed = parseObject(content);
  const rows = Array.isArray(parsed) ? parsed : parsed?.rows;
  if (!Array.isArray(rows) || !rows.length || rows.some((row) => !row || typeof row !== "object")) {
    body.innerHTML = `<p class="unsafe-content">Table data must be a JSON array of objects.</p>`;
    return;
  }
  const columns = Object.keys(rows[0]).slice(0, 12);
  let visible = rows.slice(0, compact ? 3 : 200);
  const wrap = document.createElement("div");
  wrap.className = "table-wrap";
  wrap.innerHTML = `
    ${compact ? "" : '<label class="table-filter">Filter table <input type="search"></label>'}
    <table>
      <thead><tr>${columns.map((column) => `<th><button type="button" data-column="${escapeHtml(column)}">${escapeHtml(column)}</button></th>`).join("")}</tr></thead>
      <tbody></tbody>
    </table>`;
  const tbody = wrap.querySelector("tbody");
  const draw = () => {
    tbody.innerHTML = visible.map((row) => `<tr>${columns.map(
      (column) => `<td>${escapeHtml(row[column])}</td>`,
    ).join("")}</tr>`).join("");
  };
  draw();
  wrap.querySelectorAll("[data-column]").forEach((button) => {
    button.addEventListener("click", () => {
      const key = button.dataset.column;
      visible.sort((left, right) => String(left[key] ?? "").localeCompare(String(right[key] ?? "")));
      draw();
    });
  });
  wrap.querySelector("input")?.addEventListener("input", (event) => {
    const query = event.target.value.toLowerCase();
    visible = rows.filter((row) => columns.some(
      (column) => String(row[column] ?? "").toLowerCase().includes(query),
    )).slice(0, 200);
    draw();
  });
  body.append(wrap);
}

function appendActions(article, output) {
  const actions = document.createElement("div");
  actions.className = "surface-actions";
  const copy = document.createElement("button");
  copy.className = "text-action";
  copy.type = "button";
  copy.textContent = "Copy";
  copy.addEventListener("click", () => navigator.clipboard.writeText(String(output.content || "")));
  actions.append(copy);
  if (["program", "table", "diff", "file", "image"].includes(output.type)) {
    const download = document.createElement("button");
    download.className = "text-action";
    download.type = "button";
    download.textContent = "Download";
    download.addEventListener("click", async () => {
      try {
        await downloadOutput(output);
      } catch (error) {
        download.title = error.message;
        download.textContent = "Download failed";
      }
    });
    actions.append(download);
  }
  if (output.type === "program") {
    const open = document.createElement("button");
    open.className = "text-action";
    open.type = "button";
    open.textContent = "Open as text";
    open.addEventListener("click", () => {
      const url = URL.createObjectURL(new Blob([String(output.content || "")], {
        type: "text/plain;charset=utf-8",
      }));
      window.open(url, "_blank", "noopener,noreferrer");
      setTimeout(() => URL.revokeObjectURL(url), 5_000);
    });
    actions.append(open);
  }
  article.append(actions);
}

async function downloadOutput(output) {
  if (output.type === "image") {
    const href = safeImageUrl(String(output.content || ""));
    if (!href) throw new Error("Image URL is not safe to download.");
    const response = await fetch(href);
    if (!response.ok) throw new Error(`Image download returned HTTP ${response.status}.`);
    const blob = await response.blob();
    if (!blob.type.startsWith("image/")) {
      throw new Error("Downloaded content is not an image.");
    }
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${slug(output.title)}.${imageExtension(blob.type)}`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(link.href), 0);
    return;
  }
  const type = output.type === "table" ? "application/json" : "text/plain";
  const extension = output.type === "table" ? "json" : output.type === "program" ? "txt" : "txt";
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([String(output.content || "")], { type }));
  link.download = `${slug(output.title)}.${extension}`;
  link.click();
  setTimeout(() => URL.revokeObjectURL(link.href), 0);
}

function imageExtension(mediaType) {
  return ({
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/svg+xml": "svg",
    "image/avif": "avif",
  })[mediaType.toLowerCase()] || "img";
}

function safeImageUrl(value) {
  try {
    const url = new URL(value, location.href);
    return ["https:", "http:", "data:", "blob:"].includes(url.protocol) ? url.href : null;
  } catch {
    return null;
  }
}

function parseObject(value) {
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

function icon(type) {
  return ({
    text: "¶",
    status: "●",
    link: "↗",
    program: "⌘",
    table: "▦",
    diff: "±",
    image: "▧",
    file: "◫",
  })[type] || "•";
}

function excerpt(value, length) {
  const normalized = String(value || "").replace(/\s+/g, " ").trim();
  return normalized.length > length ? `${normalized.slice(0, length - 1)}…` : normalized;
}

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

function slug(value) {
  return String(value || "output").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}
