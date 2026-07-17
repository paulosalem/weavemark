"""Reflection engine — a production chain followed by a critique → revise loop.

For text outputs this delegates to the WeaveMark ``ReflectionStrategy``. When the
final production stage declares an image output (``@output type: image``), it runs
an *artifact-aware* loop instead.

Reflection generalizes to: **a production chain, then a refinement loop.**
``critique`` and ``revise`` are reserved *loop roles*; every other ``@prompt``
stage is a **production step**, run in source order with chain threading
(``@{previous}`` and ``@{<stage_name>}``). The **last** production stage yields
the artifact that enters the loop: a vision model inspects the RENDERED image
against the ``critique`` prompt, the critique is folded into the ``revise``
prompt, and the image is re-rendered — stopping early when the critique is
satisfied. A single ``generate`` stage is just the degenerate production chain of
length one, so existing specs behave exactly as before. This is the
execution-phase counterpart of ``@iterate``: the model improves the output by
inspecting the produced artifact, not just the prompt.
"""

from __future__ import annotations

import asyncio
import base64
import re
from typing import Any, Optional

from ellements.core import MessageContent
from ellements.core.llm.messages import build_multimodal_user_message
from ellements.execution import OnStepCallback, ReflectionStrategy, StepRecord

from ..compilation.multimodal import OutputContract
from ..compilation.result import CompositionResult
from ..variable_paths import MISSING, resolve_variable_path
from .base import (
    ArtifactCallback,
    BaseEngine,
    ExecutionResult,
    RuntimeConfig,
    decode_generated_image,
    image_generation_kwargs,
    image_refs_to_content,
    image_refs_to_edit_files,
    primary_image_output,
    render_image,
    resolve_call_settings,
)

_EDIT_FLAG_VALUES = {"on", "true", "yes", "1"}
_LOOP_ROLES = ("critique", "revise")
_TEMPLATE_RE = re.compile(r"(?:@\{|\{\{)\s*([A-Za-z_][\w.-]*)\s*(?:\}|\}\})")


def _render(template: str, context: dict[str, Any]) -> str:
    """Substitute ``@{name}`` / ``{{name}}`` placeholders from *context*.

    Names may be dotted paths into nested context values. Unknown placeholders
    are left intact (so a later step like ``_fill_critique`` can still resolve
    ``@{critique}``).
    """

    def replace(match: re.Match[str]) -> str:
        value = resolve_variable_path(context, match.group(1))
        return match.group(0) if value is MISSING else str(value)

    return _TEMPLATE_RE.sub(replace, template)


_SATISFIED_MARKERS = ("OK", "NO DEFECTS", "NO ISSUES", "LGTM")
_CRITIQUE_PLACEHOLDERS = ("{{issues}}", "@{issues}", "{{critique}}", "@{critique}")
_DEFAULT_CRITIQUE = (
    "Inspect the attached image for defects. Reply with exactly OK if it is good, "
    "otherwise list the concrete, fixable defects."
)


class ReflectionEngine(BaseEngine):
    """Production chain → critique/revise loop (text, or artifact-aware for images)."""

    async def execute(
        self,
        result: CompositionResult,
        config: Optional[RuntimeConfig] = None,
        on_step: Optional[OnStepCallback] = None,
        on_artifact: Optional[ArtifactCallback] = None,
    ) -> ExecutionResult:
        production_stages = self._production_stages(result)
        artifact_stage = production_stages[-1]
        artifact_contract = result.prompt_outputs.get(
            artifact_stage
        ) or result.prompt_outputs.get("default")
        if artifact_contract is not None and artifact_contract.is_image:
            return await self._image_reflection(
                result, config, on_step, production_stages, artifact_stage
            )

        strategy = ReflectionStrategy()
        sr = await strategy.execute(
            result.prompts or {"default": result.composed_prompt},
            self.client,
            tools=result.tools or None,
            config=self._build_strategy_config(result, config, on_step),
        )
        return self._wrap_result(sr, result, config)

    @staticmethod
    def _production_stages(result: CompositionResult) -> list[str]:
        """Ordered production stages: every @prompt stage but the loop roles."""

        stages = [
            name
            for name in (result.prompts or {})
            if name != "system" and name not in _LOOP_ROLES
        ]
        return stages or ["default"]

    async def _image_reflection(
        self,
        result: CompositionResult,
        config: Optional[RuntimeConfig],
        on_step: Optional[OnStepCallback],
        production_stages: list[str],
        artifact_stage: str,
    ) -> ExecutionResult:
        prompts = result.prompts or {}
        strategy_config = self._build_strategy_config(result, config)
        max_rounds = _int_or(
            strategy_config.get("rounds", strategy_config.get("max_rounds")), 3
        )
        artifact_contract = result.prompt_outputs.get(
            artifact_stage
        ) or result.prompt_outputs.get("default")
        image_model = ""

        steps: list[StepRecord] = []
        context: dict[str, Any] = dict(config.variables) if config else {}
        previous_text = ""
        previous_image: Optional[bytes] = None
        current_png: Optional[bytes] = None
        generated: list[dict[str, Any]] = []
        call_settings: list[dict[str, Any]] = []
        method = ""
        file_target: Optional[str] = None

        # ── Production chain: run each production stage in source order ──
        for stage in production_stages:
            template = prompts.get(stage, result.composed_prompt)
            contract = result.prompt_outputs.get(stage)
            ctx = {**context, "previous": previous_text}
            prompt = _render(template, ctx)
            stage_images = result.prompt_images.get(stage, [])
            if contract is not None and contract.is_image:
                base_image = previous_image if _wants_edit(contract) else None
                generated, method, image_model = await self._render_stage(
                    prompt,
                    stage,
                    contract,
                    stage_images,
                    result,
                    config,
                    base_image=base_image,
                )
                call_settings.append(
                    resolve_call_settings(
                        result,
                        config,
                        prompt_key=stage,
                        stage=stage,
                        modality="image",
                        output_contract=contract,
                    ).metadata()
                )
                current_png = await asyncio.to_thread(
                    decode_generated_image,
                    generated,
                    config.protection if config is not None else result.protection,
                )
                previous_image = current_png
                response = primary_image_output(generated)
                if stage == artifact_stage and contract.params.get("file"):
                    file_target = _render(str(contract.params["file"]), ctx)
            else:
                response = await self._author(
                    prompt,
                    stage,
                    stage_images,
                    result,
                    config,
                )
                call_settings.append(
                    resolve_call_settings(
                        result,
                        config,
                        prompt_key=stage,
                        stage=stage,
                        modality="vision" if stage_images else "text",
                    ).metadata()
                )
                previous_image = None
            previous_text = response
            context[stage] = response
            steps.append(
                StepRecord(name=stage, prompt_key=stage, response=response)
            )
            self._emit_step(on_step, steps[-1])

        # ── Refinement loop: inspect the artifact, then revise ──
        critique_template = prompts.get("critique") or _DEFAULT_CRITIQUE
        revise_template = (
            prompts.get("revise") or prompts.get(artifact_stage) or result.composed_prompt
        )
        revise_contract = result.prompt_outputs.get("revise") or artifact_contract
        revise_images = result.prompt_images.get("revise", [])
        revise_edits = _wants_edit(revise_contract)
        satisfied = False
        for round_num in range(max_rounds):
            critique = await self._inspect(
                current_png,
                _render(critique_template, context),
                result,
                config,
            )
            call_settings.append(
                resolve_call_settings(
                    result,
                    config,
                    prompt_key="critique",
                    stage="critique",
                    modality="vision",
                ).metadata()
            )
            is_ok = _looks_satisfied(critique)
            steps.append(
                StepRecord(
                    name=f"critique_{round_num}",
                    prompt_key="critique",
                    response=critique,
                    metadata={"round": round_num, "is_satisfied": is_ok},
                )
            )
            self._emit_step(on_step, steps[-1])
            if is_ok:
                satisfied = True
                steps.append(
                    StepRecord(
                        name="stop",
                        prompt_key="critique",
                        response=f"Stopped at round {round_num}: critique satisfied.",
                        metadata={"round": round_num, "reason": "satisfied"},
                    )
                )
                self._emit_step(on_step, steps[-1])
                break

            revise_prompt = _fill_critique(_render(revise_template, context), critique)
            # Edit-based revise: when the revise stage opts in with `edit: on`,
            # fix the PREVIOUS render in place instead of re-rolling from scratch.
            base_image = current_png if revise_edits else None
            generated, method, image_model = await self._render_stage(
                revise_prompt,
                "revise",
                revise_contract,
                revise_images,
                result,
                config,
                base_image=base_image,
            )
            call_settings.append(
                resolve_call_settings(
                    result,
                    config,
                    prompt_key="revise",
                    stage="revise",
                    modality="image",
                    output_contract=revise_contract,
                ).metadata()
            )
            current_png = await asyncio.to_thread(
                decode_generated_image,
                generated,
                config.protection if config is not None else result.protection,
            )
            steps.append(
                StepRecord(
                    name=f"revise_{round_num}",
                    prompt_key="revise",
                    response=primary_image_output(generated),
                    metadata={"round": round_num, "method": method},
                )
            )
            self._emit_step(on_step, steps[-1])

        revise_count = sum(1 for step in steps if step.name.startswith("revise_"))
        output = primary_image_output(generated) or "<image generated>"
        metadata: dict[str, Any] = {
            "output_type": "image",
            "method": method,
            "model": image_model,
            "rounds_used": revise_count + 1,
            "satisfied": satisfied,
            "images": generated,
            "call_settings": call_settings,
        }
        if file_target:
            metadata["file"] = file_target
        return ExecutionResult(output=str(output), steps=steps, metadata=metadata)

    async def _author(
        self,
        prompt: str,
        stage: str,
        stage_images: list[Any],
        result: CompositionResult,
        config: Optional[RuntimeConfig],
    ) -> str:
        """Run a text/vision production stage, attaching any reference images."""

        parts = image_refs_to_content(stage_images) if stage_images else []
        settings = resolve_call_settings(
            result,
            config,
            prompt_key=stage,
            stage=stage,
            modality="vision" if parts else "text",
        )
        temperature = (
            settings.temperature if settings.temperature is not None else 0.7
        )
        messages = build_multimodal_user_message(prompt, parts) if parts else prompt
        if result.tools:
            response = await self.client.complete_with_tools(
                messages,
                tools=result.tools,
                model=settings.model,
                temperature=temperature,
            )
            return str(response.content).strip()
        return str(
            await self.client.complete(
                messages,
                model=settings.model,
                temperature=temperature,
            )
        ).strip()

    async def _render_stage(
        self,
        prompt: str,
        stage: str,
        contract: Optional[OutputContract],
        stage_images: list[Any],
        result: CompositionResult,
        config: Optional[RuntimeConfig],
        base_image: Optional[bytes] = None,
    ) -> tuple[list[dict[str, Any]], str, str]:
        params = contract.params if contract else {}
        settings = resolve_call_settings(
            result,
            config,
            prompt_key=stage,
            stage=stage,
            modality="image",
            output_contract=contract,
        )
        kwargs = image_generation_kwargs(params)
        wants_edit = _wants_edit(contract)
        edit_files: list[tuple[str, bytes]] = []
        if wants_edit:
            # The prior render (when supplied) is the base image to fix in place;
            # any declared reference images follow as additional conditioning.
            if base_image is not None:
                edit_files.append(("previous.png", base_image))
            if stage_images:
                edit_files.extend(
                    await image_refs_to_edit_files(
                        stage_images,
                        (
                            config.protection
                            if config is not None
                            else result.protection
                        ),
                    )
                )
        generated, method = await render_image(
            self.client,
            prompt,
            model=settings.model,
            kwargs=kwargs,
            edit_files=edit_files,
        )
        return generated, method, settings.model

    async def _inspect(
        self,
        png_bytes: Optional[bytes],
        critique_prompt: str,
        result: CompositionResult,
        config: Optional[RuntimeConfig],
    ) -> str:
        """Vision-inspect a produced image against the critique prompt."""
        if png_bytes is None:
            return "OK"
        data_uri = "data:image/png;base64," + base64.b64encode(png_bytes).decode("ascii")
        parts = [MessageContent.image_part(url=data_uri, detail="high")]
        messages = build_multimodal_user_message(critique_prompt, parts)
        settings = resolve_call_settings(
            result,
            config,
            prompt_key="critique",
            stage="critique",
            modality="vision",
        )
        temperature = (
            settings.temperature if settings.temperature is not None else 0.7
        )
        if result.tools:
            response = await self.client.complete_with_tools(
                messages,
                tools=result.tools,
                model=settings.model,
                temperature=temperature,
            )
            return str(response.content).strip()
        return str(
            await self.client.complete(
                messages,
                model=settings.model,
                temperature=temperature,
            )
        ).strip()

    @staticmethod
    def _emit_step(on_step: Optional[OnStepCallback], step: StepRecord) -> None:
        if on_step is not None:
            on_step(step)


def _wants_edit(contract: Optional[OutputContract]) -> bool:
    if contract is None:
        return False
    return str(contract.params.get("edit", "")).strip().lower() in _EDIT_FLAG_VALUES


def _looks_satisfied(critique: str) -> bool:
    upper = critique.strip().upper()
    return upper.startswith("OK") or any(marker in upper for marker in _SATISFIED_MARKERS)


def _fill_critique(template: str, critique: str) -> str:
    filled = template
    for placeholder in _CRITIQUE_PLACEHOLDERS:
        filled = filled.replace(placeholder, critique)
    if filled == template:
        filled = (
            f"{template}\n\nThe previous render had these defects — fix ALL of them "
            f"exactly, and do NOT introduce new issues:\n{critique}"
        )
    return filled


def _int_or(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
