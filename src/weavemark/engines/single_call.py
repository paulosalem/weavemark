"""Single-call engine — text, multimodal input, or image generation."""

from __future__ import annotations

from typing import Any, Optional

from ellements.core.llm.messages import build_multimodal_user_message
from ellements.execution import OnStepCallback, SingleCallStrategy, StepRecord

from ..compilation.multimodal import ImageRef, OutputContract
from ..compilation.result import CompositionResult
from ..defaults import DEFAULT_IMAGE_MODEL
from .base import (
    ArtifactCallback,
    BaseEngine,
    ExecutionResult,
    RuntimeConfig,
    image_generation_kwargs,
    image_refs_to_content,
    image_refs_to_edit_files,
    primary_image_output,
    render_image,
    resolve_call_settings,
)

_EDIT_FLAG_VALUES = {"on", "true", "yes", "1"}


class SingleCallEngine(BaseEngine):
    """Default engine: one production of the ``default`` prompt.

    Honors the ``default`` output contract and any lifted image inputs:
    ``@output type: image`` routes to image generation, image inputs are sent as
    multimodal parts, and everything else falls back to the text strategy.
    """

    async def execute(
        self,
        result: CompositionResult,
        config: Optional[RuntimeConfig] = None,
        on_step: Optional[OnStepCallback] = None,
        on_artifact: Optional[ArtifactCallback] = None,
    ) -> ExecutionResult:
        prompts = result.prompts or {"default": result.composed_prompt}
        prompt = prompts.get("default", result.composed_prompt)
        contract = result.prompt_outputs.get("default")
        images = result.prompt_images.get("default") or []

        if contract is not None and contract.is_image:
            return await self._generate_image(prompt, contract, images, result, config)

        if images:
            return await self._complete_multimodal(
                prompt,
                prompts.get("system"),
                images,
                result,
                config,
                on_step,
            )

        strategy = SingleCallStrategy()
        sr = await strategy.execute(
            prompts,
            self.client,
            tools=result.tools or None,
            config=self._build_strategy_config(result, config, on_step),
        )
        return self._wrap_result(sr, result, config)

    async def _complete_multimodal(
        self,
        prompt: str,
        system: Optional[str],
        images: list[ImageRef],
        result: CompositionResult,
        config: Optional[RuntimeConfig],
        on_step: Optional[OnStepCallback],
    ) -> ExecutionResult:
        parts = image_refs_to_content(images)
        if not parts:
            strategy = SingleCallStrategy()
            sr = await strategy.execute(
                result.prompts or {"default": prompt},
                self.client,
                tools=result.tools or None,
                config=self._build_strategy_config(result, config),
            )
            return self._wrap_result(sr, result, config)

        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.extend(build_multimodal_user_message(prompt, parts))

        settings = resolve_call_settings(
            result,
            config,
            prompt_key="default",
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
            content = response.content
        else:
            content = await self.client.complete(
                messages,
                model=settings.model,
                temperature=temperature,
            )
        step = StepRecord(name="call", prompt_key="default", response=content)
        if on_step is not None:
            on_step(step)
        return ExecutionResult(
            output=content,
            steps=[step],
            metadata={
                "output_type": "text",
                "image_inputs": len(parts),
                "call_settings": settings.metadata(),
            },
        )

    async def _generate_image(
        self,
        prompt: str,
        contract: OutputContract,
        images: list[ImageRef],
        result: CompositionResult,
        config: Optional[RuntimeConfig],
    ) -> ExecutionResult:
        params = contract.params
        settings = resolve_call_settings(
            result,
            config,
            prompt_key="default",
            modality="image",
            output_contract=contract,
        )
        model = settings.model or DEFAULT_IMAGE_MODEL
        kwargs = image_generation_kwargs(params)

        # Reference-guided editing is opt-in (`@output type: image edit: on`).
        # By default, generate text-to-image even when image inputs are present —
        # a clean prompt usually renders better than literally editing references.
        wants_edit = str(params.get("edit", "")).strip().lower() in _EDIT_FLAG_VALUES
        edit_files = (
            await image_refs_to_edit_files(
                images,
                config.protection if config is not None else result.protection,
            )
            if (images and wants_edit)
            else []
        )
        generated, method = await render_image(
            self.client, prompt, model=model, kwargs=kwargs, edit_files=edit_files
        )

        output = primary_image_output(generated) or f"<{len(generated)} image(s) generated>"
        return ExecutionResult(
            output=str(output),
            steps=[
                StepRecord(
                    name=method,
                    prompt_key="default",
                    response=output,
                )
            ],
            metadata={
                "output_type": "image",
                "model": model,
                "method": method,
                "reference_images": len(edit_files),
                "images": generated,
                "call_settings": settings.metadata(),
            },
        )
