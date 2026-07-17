"""Render study-local reusable template controls."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


INCLUDE_PATTERN = re.compile(r"{{>\s*([a-zA-Z0-9_./-]+)\s*}}")
VARIABLE_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")


def render_template(
    template_path: Path,
    variables: dict[str, Any],
    partial_root: Path,
    include_stack: tuple[Path, ...] = (),
) -> str:
    """Render a template file with recursive partial includes."""
    path = template_path.resolve()
    if path in include_stack:
        chain = " -> ".join(str(item) for item in (*include_stack, path))
        raise ValueError(f"Circular template include: {chain}")

    text = path.read_text()

    def include(match: re.Match[str]) -> str:
        name = match.group(1)
        partial_path = partial_root / f"{name}.md"
        if not partial_path.is_file():
            raise FileNotFoundError(f"Template partial not found: {partial_path}")
        return render_template(partial_path, variables, partial_root, (*include_stack, path))

    text = INCLUDE_PATTERN.sub(include, text)

    def substitute(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in variables:
            raise KeyError(f"Missing template variable: {name}")
        value = variables[name]
        if isinstance(value, list):
            return "\n".join(str(item) for item in value)
        if isinstance(value, dict):
            return json.dumps(value, indent=2, sort_keys=True)
        return str(value)

    return VARIABLE_PATTERN.sub(substitute, text).rstrip() + "\n"


def main() -> None:
    """Render one matched reusable-template control."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", type=Path)
    parser.add_argument("variables", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--partial-root",
        type=Path,
        default=Path(__file__).resolve().parent / "partials",
    )
    args = parser.parse_args()

    variables = json.loads(args.variables.read_text())
    rendered = render_template(args.template, variables, args.partial_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)


if __name__ == "__main__":
    main()
