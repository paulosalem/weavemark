"""Shared guided-input collection for Python example runners."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ellements.cli import CliPrinter

from weavemark.cli_inputs import prompt_for_missing_inputs


def collect_guided_variables(
    spec_path: Path,
    variables: dict[str, Any],
) -> dict[str, Any] | None:
    """Collect missing promplet variables through WeaveMark's native CLI prompts."""

    printer = CliPrinter("WeaveMark example", icon="WM", verbose=False)
    spec_text = spec_path.read_text(encoding="utf-8")
    return prompt_for_missing_inputs(
        printer,
        spec_text,
        variables,
        spec_path.parent,
    )
