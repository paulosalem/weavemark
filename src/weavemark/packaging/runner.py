"""Run a spec's ``@package`` steps after execution — fully in-language packaging.

After a pipeline executes, its produced artifacts (named via ``@output file:``)
are persisted to disk, and each ``@package`` step turns them into a deliverable:

- **Apply** (``instructions:`` and/or body): compile reusable and local WeaveMark
  instructions with the pipeline output context, then execute one semantic
  transformation and write the result to ``file:``.
- **Convert** (``from:``): deterministically convert an already-produced
  deliverable to another format (e.g. HTML -> PDF).

Packaging context exposed to instructions:
- every input variable, unchanged;
- ``@{output}`` — the execution engine's canonical primary output;
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
from ..promplet_application import PrompletApplicationResult, apply_promplet
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
    application: PrompletApplicationResult | None = None


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
    """Assemble the variable context package instructions are compiled against."""

    context: dict[str, Any] = dict(variables)
    stage_outputs: dict[str, list[str]] = {}
    for step in execution.steps:
        stage = step.metadata.get("stage") or step.name
        stage_outputs.setdefault(str(stage), []).append(str(step.response))
    for stage, outputs in stage_outputs.items():
        context[stage] = "\n".join(outputs)
    for stage, files in stage_files.items():
        context[f"{stage}_files"] = list(files)
    context["output"] = str(execution.output)
    return context


async def _apply_package(
    package: dict[str, str],
    context: dict[str, Any],
    base_dir: Path,
    root: Path,
    model: str,
    client: Any | None = None,
    protection: ProtectionContext | None = None,
    logging_settings: LoggingSettings | None = None,
) -> PackageResult:
    target = root / package["file"]
    application = await apply_promplet(
        context=context,
        base_dir=base_dir,
        model=model,
        instructions=package.get("instructions"),
        body=package.get("body"),
        client=client,
        protection=protection,
        logging_settings=logging_settings,
    )
    if not application.ok:
        return PackageResult(
            target,
            "apply",
            False,
            "; ".join(application.errors),
            application,
        )
    if protection is not None:
        target = protection.authorize_write(
            target,
            reason="Writing a rendered @package deliverable",
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_strip_fences(application.output), encoding="utf-8")
    return PackageResult(target, "apply", True, application=application)


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
    that stage → file mapping to build the package-instruction context.
    """

    root = Path(root)
    if stage_files is None:
        stage_files = persist_execution_artifacts(execution, root, protection)
    context = build_package_context(variables, execution, stage_files)

    results: list[PackageResult] = []
    for package in packages:
        if "instructions" in package or "body" in package:
            results.append(
                await _apply_package(
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
