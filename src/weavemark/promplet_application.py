"""Compile and execute reusable promplet instructions over explicit context."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .api import CompileOptions, compile_file, compile_text
from .compilation.result import CompositionResult
from .engines.base import ExecutionResult, RuntimeConfig
from .engines.single_call import SingleCallEngine
from .logging_policy import LoggingSettings
from .logging_setup import new_client
from .promplet_library import PrompletLibraryLookupError, resolve_module_source
from .protection import ProtectionContext

_LOCAL_PRECEDENCE = (
    "The local instructions below supplement the reusable instructions above. "
    "If they conflict, follow the local instructions."
)


@dataclass(frozen=True)
class PrompletApplicationResult:
    """Result of one compiled promplet application."""

    compiled: CompositionResult | None
    execution: ExecutionResult | None
    errors: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        """Return whether compilation and execution completed."""

        return self.compiled is not None and self.execution is not None and not self.errors

    @property
    def output(self) -> str:
        """Return the application output, or an empty string on failure."""

        return "" if self.execution is None else str(self.execution.output)


def _resolve_instructions_path(reference: str, base_dir: Path) -> Path:
    if reference.startswith("module:"):
        resolved = resolve_module_source(
            reference.removeprefix("module:"),
            cwd=base_dir,
        )
        return Path(resolved.path)
    return (base_dir / reference).resolve()


def _component_prompt(result: CompositionResult) -> str:
    return str(result.prompts.get("default", result.composed_prompt)).strip()


def _combine_components(
    reusable: CompositionResult | None,
    local: CompositionResult | None,
    protection: ProtectionContext | None,
) -> CompositionResult:
    components = [item for item in (reusable, local) if item is not None]
    if len(components) == 1:
        return components[0]

    assert reusable is not None and local is not None
    prompt = "\n\n".join(
        (
            _component_prompt(reusable),
            _LOCAL_PRECEDENCE,
            _component_prompt(local),
        )
    )
    output_contract = local.prompt_outputs.get("default")
    if output_contract is None:
        output_contract = reusable.prompt_outputs.get("default")
    return CompositionResult(
        composed_prompt=prompt,
        prompts={"default": prompt},
        prompt_outputs=(
            {"default": output_contract} if output_contract is not None else {}
        ),
        compile={**reusable.compile, **local.compile},
        warnings=[*reusable.warnings, *local.warnings],
        protection=protection,
    )


async def apply_promplet(
    *,
    context: dict[str, Any],
    base_dir: Path,
    model: str,
    instructions: str | None = None,
    body: str | None = None,
    client: Any | None = None,
    protection: ProtectionContext | None = None,
    logging_settings: LoggingSettings | None = None,
) -> PrompletApplicationResult:
    """Compile reusable and/or inline instructions, then execute one semantic call."""

    reusable: CompositionResult | None = None
    local: CompositionResult | None = None
    compile_options = CompileOptions(model=model)

    if instructions:
        try:
            instructions_path = _resolve_instructions_path(instructions, base_dir)
        except PrompletLibraryLookupError as exc:
            return PrompletApplicationResult(None, None, (str(exc),))
        if protection is not None:
            instructions_path = protection.authorize_read(
                instructions_path,
                reason=f"Reading @package instructions {instructions!r}",
            )
        if not instructions_path.is_file():
            return PrompletApplicationResult(
                None,
                None,
                (f"instructions not found: {instructions}",),
            )
        reusable = await compile_file(
            instructions_path,
            context,
            options=compile_options,
            protection_context=protection,
        )
        if reusable.errors:
            return PrompletApplicationResult(
                reusable,
                None,
                tuple(f"instructions compile failed: {error}" for error in reusable.errors),
            )

    if body and body.strip():
        local = await compile_text(
            body,
            context,
            base_dir=base_dir,
            options=compile_options,
            protection_context=protection,
        )
        if local.errors:
            return PrompletApplicationResult(
                local,
                None,
                tuple(f"inline instructions compile failed: {error}" for error in local.errors),
            )

    if reusable is None and local is None:
        return PrompletApplicationResult(
            None,
            None,
            ("promplet application requires instructions or a non-empty body",),
        )

    compiled = _combine_components(reusable, local, protection)
    engine_client = client or new_client(
        model=model,
        protection=protection,
        logging_settings=logging_settings,
    )
    execution = await SingleCallEngine(client=engine_client).execute(
        compiled,
        RuntimeConfig(
            model=model,
            execution_variables=dict(context),
            protection=protection,
        ),
    )
    return PrompletApplicationResult(compiled, execution)


__all__ = ["PrompletApplicationResult", "apply_promplet"]
