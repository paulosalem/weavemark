"""Run a spec's ``@package`` steps after execution — fully in-language packaging.

After a pipeline executes, its produced artifacts (named via ``@output file:``)
are persisted to disk, and each ``@package`` step turns them into a deliverable:

- **Render** (``template:``): compile and execute a *packaging template promplet*
  with the pipeline's outputs and artifact file lists in scope. The template is
  ordinary WeaveMark; assembling "one section per artifact" is done by a
  **semantic transformation** (the model fills the skeleton), so no template
  iteration primitive is required. The produced text is written to ``file:``.
- **Convert** (``from:``): deterministically convert an already-produced
  deliverable to another format (e.g. HTML -> PDF).

Packaging context exposed to a template:
- every input variable, unchanged;
- ``@{<stage>}`` — a completed stage's text output (e.g. an author stage's JSON);
- ``@{<stage>_files}`` — the ordered relative paths of that stage's persisted
  artifacts (e.g. ``@{page_files}``).
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..engines.base import ExecutionResult
from ..logging_policy import LoggingSettings
from ..protection import ProtectionContext
from .convert import ConversionError, convert_file
from .persist import persist_execution_artifacts

_FENCE_RE = re.compile(r"^\s*```[\w-]*\s*\n|\n?```\s*$")


@dataclass(frozen=True)
class PackageResult:
    """Outcome of a single ``@package`` step."""

    file: Path
    kind: str
    ok: bool
    note: str = ""


def _strip_fences(text: str) -> str:
    """Remove a single wrapping Markdown code fence, if the model added one."""

    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = _FENCE_RE.sub("", stripped)
        stripped = re.sub(r"\n?```\s*$", "", stripped)
    return stripped.strip()


def build_package_context(
    variables: dict[str, Any],
    execution: ExecutionResult,
    stage_files: dict[str, list[str]],
) -> dict[str, Any]:
    """Assemble the variable context a packaging template is compiled against."""

    context: dict[str, Any] = dict(variables)
    stage_outputs: dict[str, list[str]] = {}
    for step in execution.steps:
        stage = step.metadata.get("stage") or step.name
        stage_outputs.setdefault(str(stage), []).append(str(step.response))
    for stage, outputs in stage_outputs.items():
        context[stage] = "\n".join(outputs)
    for stage, files in stage_files.items():
        context[f"{stage}_files"] = list(files)
    return context


async def _render_package(
    package: dict[str, str],
    context: dict[str, Any],
    base_dir: Path,
    root: Path,
    model: str,
    client: Any | None = None,
    protection: ProtectionContext | None = None,
    logging_settings: LoggingSettings | None = None,
) -> PackageResult:
    from weavemark.api import CompileOptions, compile_file
    from weavemark.engines.single_call import SingleCallEngine
    from weavemark.logging_setup import new_client
    from weavemark.promplet_library import (
        PrompletLibraryLookupError,
        resolve_module_source,
    )

    target = root / package["file"]
    template_reference = package["template"]
    if template_reference.startswith("module:"):
        try:
            template_path = resolve_module_source(
                template_reference.removeprefix("module:"),
                cwd=base_dir,
            ).path
        except PrompletLibraryLookupError as exc:
            return PackageResult(target, "render", False, str(exc))
    else:
        template_path = (base_dir / template_reference).resolve()
    if protection is not None:
        template_path = protection.authorize_read(
            template_path,
            reason=f"Reading @package template {template_reference!r}",
        )
    if not template_path.is_file():
        return PackageResult(
            target, "render", False, f"template not found: {template_reference}"
        )
    compiled = await compile_file(
        template_path,
        context,
        options=CompileOptions(model=model),
        protection_context=protection,
    )
    if compiled.errors:
        return PackageResult(
            target, "render", False, f"template compile failed: {compiled.errors}"
        )
    engine_client = (
        client
        if client is not None
        else new_client(
            model=model,
            protection=protection,
            logging_settings=logging_settings,
        )
    )
    execution = await SingleCallEngine(client=engine_client).execute(compiled)
    if protection is not None:
        target = protection.authorize_write(
            target,
            reason="Writing a rendered @package deliverable",
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_strip_fences(execution.output), encoding="utf-8")
    return PackageResult(target, "render", True)


async def _convert_package(
    package: dict[str, str],
    root: Path,
    protection: ProtectionContext | None = None,
    logging_settings: LoggingSettings | None = None,
) -> PackageResult:
    target = root / package["file"]
    source = root / package["from"]
    if protection is not None:
        source = protection.authorize_read(
            source,
            reason="Reading the source of an @package conversion",
        )
        target = protection.authorize_write(
            target,
            reason="Writing a converted @package deliverable",
        )
    if not source.is_file():
        return PackageResult(
            target, "convert", False, f"source not found: {package['from']}"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        ok = await asyncio.to_thread(convert_file, source, target)
    except ConversionError as exc:
        return PackageResult(target, "convert", False, str(exc))
    if not ok:
        return PackageResult(
            target,
            "convert",
            False,
            "conversion backend unavailable (e.g. Playwright/Chromium not "
            "installed); the source deliverable was still produced",
        )
    return PackageResult(target, "convert", True)


async def run_packages(
    packages: list[dict[str, str]],
    variables: dict[str, Any],
    execution: ExecutionResult,
    *,
    base_dir: Path,
    root: Path,
    model: str,
    client: Any | None = None,
    stage_files: dict[str, list[str]] | None = None,
    protection: ProtectionContext | None = None,
    logging_settings: LoggingSettings | None = None,
) -> list[PackageResult]:
    """Persist artifacts (unless already persisted), then run each ``@package`` step.

    When *stage_files* is provided, the artifacts were already written to *root*
    (e.g. streamed during execution), so this skips re-persisting them and reuses
    that stage → file mapping to build the packaging-template context.
    """

    root = Path(root)
    if stage_files is None:
        stage_files = persist_execution_artifacts(execution, root, protection)
    context = build_package_context(variables, execution, stage_files)

    results: list[PackageResult] = []
    for package in packages:
        if "template" in package:
            results.append(
                await _render_package(
                    package,
                    context,
                    base_dir,
                    root,
                    model,
                    client,
                    protection,
                    logging_settings,
                )
            )
        elif "from" in package:
            results.append(await _convert_package(package, root, protection))
    return results


__all__ = ["PackageResult", "build_package_context", "run_packages"]
