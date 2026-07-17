"""Project and user configuration for WeaveMark.

Resolution order (later overrides earlier):
  1. Built-in defaults
  2. Global user config:  ~/.weavemark/config.json
  3. Project config:      .weavemark.config.json (searched cwd → parents)
  4. CLI flags (--library-dir, --model, etc.)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from weavemark.defaults import DEFAULT_MODEL

GLOBAL_DIR = Path.home() / ".weavemark"
GLOBAL_CONFIG = GLOBAL_DIR / "config.json"
PROJECT_CONFIG_NAME = ".weavemark.config.json"


@dataclass
class WeaveMarkEnvConfig:
    """Resolved configuration for WeaveMark."""

    library_dirs: list[Path] = field(default_factory=list)
    default_model: str = DEFAULT_MODEL

    # Provenance tracking (which files contributed)
    _global_path: Path | None = field(default=None, repr=False)
    _project_path: Path | None = field(default=None, repr=False)

    def effective_library_dirs(self, cwd: Path | None = None) -> list[Path]:
        """Return project, user, and configured promplet-library directories."""
        dirs = list(self.library_dirs)
        if cwd is None:
            cwd = Path.cwd()
        default_promplets = cwd / "promplets"
        user_promplets = GLOBAL_DIR / "promplets"
        if user_promplets.is_dir() and user_promplets not in dirs:
            dirs.insert(0, user_promplets)
        if default_promplets.is_dir() and default_promplets not in dirs:
            dirs.insert(0, default_promplets)
        return dirs


def _find_project_config(start: Path | None = None) -> Path | None:
    """Walk from *start* up to the filesystem root looking for project config."""
    current = (start or Path.cwd()).resolve()
    for _ in range(50):  # safety limit
        candidate = current / PROJECT_CONFIG_NAME
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _load_json(path: Path) -> dict[str, Any]:
    """Load a JSON file, returning {} on any error."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _apply_dict(
    config: WeaveMarkEnvConfig, data: dict[str, Any], base_dir: Path
) -> None:
    """Merge a raw JSON dict into a config object."""
    if "library_dirs" in data:
        raw = data["library_dirs"]
        if isinstance(raw, list):
            for d in raw:
                p = Path(d).expanduser()
                if not p.is_absolute():
                    p = (base_dir / p).resolve()
                if p not in config.library_dirs:
                    config.library_dirs.append(p)
    if "default_model" in data:
        config.default_model = str(data["default_model"])


def load_config(
    project_dir: Path | None = None,
    extra_library_dirs: list[Path] | None = None,
) -> WeaveMarkEnvConfig:
    """Load and merge the two-tier configuration.

    Parameters
    ----------
    project_dir : Path, optional
        Starting directory for project config search (defaults to cwd).
    extra_library_dirs : list of Path, optional
        Additional --library-dir values from CLI flags.
    """
    config = WeaveMarkEnvConfig()

    # 1. Global
    if GLOBAL_CONFIG.is_file():
        data = _load_json(GLOBAL_CONFIG)
        _apply_dict(config, data, GLOBAL_DIR)
        config._global_path = GLOBAL_CONFIG

    # 2. Project (overrides global)
    proj = _find_project_config(project_dir)
    if proj:
        data = _load_json(proj)
        _apply_dict(config, data, proj.parent)
        config._project_path = proj

    # 3. CLI extras
    if extra_library_dirs:
        for d in extra_library_dirs:
            p = d.expanduser().resolve()
            if p not in config.library_dirs:
                config.library_dirs.append(p)

    return config


def print_env(config: WeaveMarkEnvConfig, cwd: Path | None = None) -> str:
    """Return a formatted string describing the resolved environment."""
    if cwd is None:
        cwd = Path.cwd()
    lines = []
    lines.append("WeaveMark Environment")
    lines.append("=" * 50)
    lines.append("")
    lines.append(f"  Global config:   {config._global_path or '(not found)'}")
    lines.append(f"  Project config:  {config._project_path or '(not found)'}")
    lines.append(f"  Default model:   {config.default_model}")
    lines.append(f"  Cache dir:       {GLOBAL_DIR}")
    lines.append("")
    lines.append("  Promplet library directories:")
    for d in config.effective_library_dirs(cwd):
        exists = "✓" if d.is_dir() else "✗"
        lines.append(f"    {exists} {d}")
    if not config.effective_library_dirs(cwd):
        lines.append("    (none)")
    lines.append("")
    return "\n".join(lines)
