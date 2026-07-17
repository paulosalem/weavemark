"""Chain engine — sequential prompt chaining (a general pipeline pattern).

`@execute chain` runs the spec's named ``@prompt`` stages in source order. Each
stage's output is threaded forward as runtime context — ``@{previous}`` (the
immediately preceding output) and ``@{<stage_name>}`` (a completed stage's
output) — so a later stage can build on earlier ones. Each stage carries its own
``@output`` contract, so a stage may produce text or an image; an image stage
with ``edit: on`` also receives the previous image as an edit base, giving visual
carry ("one panel/page after the other").

A stage may be repeated a data-driven number of times via ``@execute`` config:

    @execute chain
      repeat: page          # the name of the stage to repeat
      count: 5              # how many times (int, or @{var})

The repeated stage runs ``count`` times; each iteration sees ``@{index}`` (1..N),
``@{count}``, and ``@{previous}``. This is the general "iterate a production over
a sequence" pattern (multi-section documents, image sequences, storyboards, …)
without being specialized to any one domain.
"""

from __future__ import annotations

import asyncio
import re
from typing import Any, Optional

from ellements.execution import OnStepCallback, StepRecord

from ..compilation.multimodal import OutputContract
from ..compilation.result import CompositionResult
from ..defaults import DEFAULT_IMAGE_MODEL
from ..variable_paths import MISSING, resolve_variable_path
from .base import (
    ArtifactCallback,
    BaseEngine,
    ExecutionResult,
    RuntimeConfig,
    decode_generated_image,
    image_generation_kwargs,
    primary_image_output,
    render_image,
    resolve_call_settings,
)

_EDIT_FLAG_VALUES = {"on", "true", "yes", "1"}
_TEMPLATE_RE = re.compile(r"(?:@\{|\{\{)\s*([A-Za-z_][\w.-]*)\s*(?:\}|\}\})")


def _render(template: str, context: dict[str, Any]) -> str:
    """Substitute ``@{name}`` / ``{{name}}`` placeholders from *context*.

    Names may be dotted paths into nested context values (``@{page.beat}``);
    unknown placeholders are left intact.
    """

    def replace(match: re.Match[str]) -> str:
        value = resolve_variable_path(context, match.group(1))
        return match.group(0) if value is MISSING else str(value)

    return _TEMPLATE_RE.sub(replace, template)


class ChainEngine(BaseEngine):
    """Run ``@prompt`` stages sequentially, threading each output to the next."""

    async def execute(
        self,
        result: CompositionResult,
        config: Optional[RuntimeConfig] = None,
        on_step: Optional[OnStepCallback] = None,
        on_artifact: Optional[ArtifactCallback] = None,
    ) -> ExecutionResult:
        base_vars: dict[str, Any] = dict(config.variables) if config else {}
        stages = [name for name in result.prompts if name != "system"]
        if not stages:
            stages = ["default"]
        execution = result.execution or {}
        repeat_stage = execution.get("repeat")
        repeat_count = _resolve_count(execution.get("count"), base_vars)

        context: dict[str, Any] = dict(base_vars)
        steps: list[StepRecord] = []
        artifacts: list[dict[str, Any]] = []
        call_settings: list[dict[str, Any]] = []
        previous_text = ""
        previous_image: Optional[bytes] = None
        final_output = ""

        for stage in stages:
            template = result.prompts.get(stage, result.composed_prompt)
            contract = result.prompt_outputs.get(stage)
            reps = repeat_count if stage == repeat_stage else 1
            stage_outputs: list[str] = []

            for index in range(1, reps + 1):
                ctx = {
                    **context,
                    "previous": previous_text,
                    "index": index,
                    "count": reps,
                }
                prompt = _render(template, ctx)
                file_target = None
                if contract is not None and contract.params.get("file"):
                    file_target = _render(str(contract.params["file"]), ctx)
                iteration_artifact: Optional[dict[str, Any]] = None
                if contract is not None and contract.is_image:
                    payload, image_bytes, meta = await self._run_image_stage(
                        prompt, stage, contract, previous_image, config, result
                    )
                    previous_image = image_bytes
                    meta.update({"stage": stage, "index": index})
                    call_settings.append(meta["call_settings"])
                    if file_target:
                        meta["file"] = file_target
                    artifacts.append(meta)
                    iteration_artifact = meta
                    # Thread a COMPACT reference (the artifact's file path) forward as
                    # this stage's text, never the multi-MB image payload — otherwise
                    # @{previous}/@{<stage>} and the packaging context would balloon
                    # with base64 and blow the model's context window. The real bytes
                    # travel in ``meta["images"]`` (for persistence) and
                    # ``previous_image`` (for edit chaining). When no file target is
                    # declared, fall back to the payload so the image is still surfaced.
                    text = file_target or payload
                else:
                    text, stage_call_settings = await self._run_text_stage(
                        prompt,
                        stage,
                        config,
                        result,
                    )
                    call_settings.append(stage_call_settings)
                    previous_image = None
                    if file_target:
                        iteration_artifact = {
                            "stage": stage,
                            "index": index,
                            "file": file_target,
                            "text": text,
                        }
                        artifacts.append(iteration_artifact)

                # Stream each file-bearing artifact to the caller the moment it is
                # produced, so long runs persist page-by-page instead of only at the
                # very end (resilient, and visible as it goes).
                if on_artifact is not None and iteration_artifact is not None:
                    on_artifact(iteration_artifact)

                previous_text = text
                final_output = text
                stage_outputs.append(text)
                step = StepRecord(
                    name=stage if reps == 1 else f"{stage}_{index}",
                    prompt_key=stage,
                    response=text,
                    metadata={
                        "stage": stage,
                        "index": index,
                        "count": reps,
                        "call_settings": call_settings[-1],
                    },
                )
                steps.append(step)
                if on_step is not None:
                    on_step(step)

            context[stage] = "\n".join(stage_outputs)

        return ExecutionResult(
            output=str(final_output),
            steps=steps,
            metadata={
                "engine": "chain",
                "stages": stages,
                "artifacts": artifacts,
                "call_settings": call_settings,
            },
        )

    async def _run_text_stage(
        self,
        prompt: str,
        stage: str,
        config: Optional[RuntimeConfig],
        result: CompositionResult,
    ) -> tuple[str, dict[str, Any]]:
        settings = resolve_call_settings(
            result,
            config,
            prompt_key=stage,
            stage=stage,
        )
        temperature = (
            settings.temperature if settings.temperature is not None else 0.7
        )
        response = str(
            await self.client.complete(
                prompt,
                model=settings.model,
                temperature=temperature,
            )
        )
        return response, settings.metadata()

    async def _run_image_stage(
        self,
        prompt: str,
        stage: str,
        contract: OutputContract,
        previous_image: Optional[bytes],
        config: Optional[RuntimeConfig],
        result: CompositionResult,
    ) -> tuple[str, Optional[bytes], dict[str, Any]]:
        """Render one image; return ``(payload, image_bytes, meta)``.

        ``payload`` is the raw provider text (a URL or base64 image) used only as a
        last-resort fallback when the stage declares no ``file:`` target; the caller
        prefers the file path for context threading. ``meta["images"]`` carries the
        provider image dicts for persistence, and ``image_bytes`` feeds edit chaining.
        """

        params = contract.params
        settings = resolve_call_settings(
            result,
            config,
            prompt_key=stage,
            stage=stage,
            modality="image",
            output_contract=contract,
        )
        model = settings.model or DEFAULT_IMAGE_MODEL
        kwargs = image_generation_kwargs(params)
        wants_edit = str(params.get("edit", "")).strip().lower() in _EDIT_FLAG_VALUES
        edit_files = (
            [("previous.png", previous_image)]
            if (wants_edit and previous_image is not None)
            else []
        )
        generated, method = await render_image(
            self.client, prompt, model=model, kwargs=kwargs, edit_files=edit_files
        )
        payload = primary_image_output(generated) or "<image>"
        try:
            image_bytes = await asyncio.to_thread(
                decode_generated_image,
                generated,
                config.protection if config is not None else result.protection,
            )
        except OSError:
            image_bytes = None
        meta = {
            "method": method,
            "model": model,
            "images": generated,
            "call_settings": settings.metadata(),
        }
        return payload, image_bytes, meta
def _resolve_count(raw: Any, variables: dict[str, Any]) -> int:
    if raw is None:
        return 1
    if isinstance(raw, int):
        return max(raw, 0)
    text = _render(str(raw), variables).strip()
    try:
        return max(int(text), 0)
    except ValueError:
        return 1
