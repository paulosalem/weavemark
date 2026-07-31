import { createReadStream, statSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import {
  decodeRequestPath,
  resolveContainedPath,
} from "./serve-static-paths.mjs";

const root = resolve(fileURLToPath(new URL("..", import.meta.url)));
const port = Number(process.env.PORT || process.argv[2] || 4173);
const mediaTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
  ".svg": "image/svg+xml",
  ".wasm": "application/wasm",
};

const server = createServer((request, response) => {
  let pathname;
  try {
    pathname = decodeRequestPath(request.url);
  } catch {
    response.writeHead(400, { "Content-Type": "text/plain; charset=utf-8" })
      .end("Bad request");
    return;
  }
  let candidate;
  try {
    candidate = resolveContainedPath(root, pathname);
  } catch {
    response.writeHead(403).end("Forbidden");
    return;
  }
  let file = candidate;
  try {
    if (statSync(file).isDirectory()) file = join(file, "index.html");
    const stat = statSync(file);
    response.writeHead(200, {
      "Content-Type": mediaTypes[extname(file)] || "application/octet-stream",
      "Content-Length": stat.size,
      "Cache-Control": "no-store",
      "Cross-Origin-Resource-Policy": "same-origin",
      "X-Content-Type-Options": "nosniff",
    });
    createReadStream(file).pipe(response);
  } catch {
    response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" }).end("Not found");
  }
});

server.listen(port, "127.0.0.1", () => {
  process.stderr.write(`AI Kanban static server: http://127.0.0.1:${port}/\n`);
});
