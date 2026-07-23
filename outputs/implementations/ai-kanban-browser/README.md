# AI Kanban browser demo

A static, backend-free Kanban workspace whose canonical state is a
user-selected `.aikanban.sqlite` file.

## Run

```bash
python -m http.server 4173
```

Open `http://localhost:4173/outputs/implementations/ai-kanban-browser/` when
serving from the repository root, or run the command inside this folder and open
`http://localhost:4173/`.

## Test

```bash
npm test
```

Browser testing is performed with Playwright against a static HTTP server.

## Persistence

- Chromium desktop: Open/Create connects directly to a user-selected SQLite file
  through the File System Access API.
- Other browsers: import a SQLite file and explicitly download updates.
- IndexedDB stores only a recent `FileSystemFileHandle`; the selected SQLite file
  remains authoritative.
- `sql.js` 1.14.1 is vendored under `vendor/` and runs in a Web Worker.

## Limitations

- The complete SQLite database is serialized and rewritten on save.
- Only one tab may own a writable workspace.
- AI integration is provider-neutral copy/import. No provider credential is
  required, uploaded, or persisted.
