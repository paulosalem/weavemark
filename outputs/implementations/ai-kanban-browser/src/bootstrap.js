import { APP_VERSION, BOOTSTRAP_FILES } from "./constants.js";

const TEMPLATE_PATHS = Object.freeze({
  "AGENTS.md": "../templates/root/AGENTS.md",
  "CLAUDE.md": "../templates/root/CLAUDE.md",
  ".agents/skills/ai-kanban/SKILL.md": "../templates/skill/SKILL.md",
  ".agents/skills/ai-kanban/ai_kanban.py": "../templates/skill/ai_kanban.py",
  ".agents/skills/ai-kanban/ai-kanban.sh": "../templates/skill/ai-kanban.sh",
  ".agents/skills/ai-kanban/ai-kanban.ps1": "../templates/skill/ai-kanban.ps1",
});

let cache = null;

export async function loadBootstrapFiles() {
  if (cache) return { ...cache };
  const entries = await Promise.all(
    Object.entries(TEMPLATE_PATHS).map(async ([workspacePath, templatePath]) => {
      const response = await fetch(new URL(templatePath, import.meta.url));
      if (!response.ok) throw new Error(`Bootstrap template is unavailable: ${workspacePath}`);
      const content = (await response.text())
        .replaceAll("{{APP_VERSION}}", APP_VERSION)
        .replaceAll("{{WORKSPACE_FOLDER}}", "the selected Board Workspace folder");
      return [workspacePath, content];
    }),
  );
  cache = Object.fromEntries(entries);
  if (Object.keys(cache).some((path) => !BOOTSTRAP_FILES.includes(path))) {
    throw new Error("The bootstrap template map contains an unrecognized path.");
  }
  return { ...cache };
}
