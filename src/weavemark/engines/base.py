"""Engine protocol, base class, and runtime configuration."""

from __future__ import annotations

import asyncio
import json
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Protocol, runtime_checkable

from ellements.core import LLMClient, MessageContent
from ellements.execution import OnStepCallback, StepRecord, StrategyResult

from ..compilation.multimodal import ImageRef
from ..compilation.result import CompositionResult
from ..defaults import DEFAULT_IMAGE_MODEL, DEFAULT_MODEL
from ..logging_setup import new_client
from ..protection import ProtectionContext, ProtectionError

# Called with each ``@output file:`` artifact record the moment an engine produces
# it, so a caller can persist it immediately (streaming) instead of only after the
# whole run finishes. The record mirrors the entries in
# ``ExecutionResult.metadata["artifacts"]`` (``stage``, ``index``, ``file``, and
# either ``images`` or ``text``).
ArtifactCallback = Callable[[Dict[str, Any]], None]


def image_refs_to_content(refs: List[ImageRef]) -> List[MessageContent]:
    """Convert resolved :class:`ImageRef` inputs to multimodal content parts."""

    parts: List[MessageContent] = []
    for ref in refs:
        detail = ref.detail if ref.detail in {"low", "high", "auto"} else "auto"
        if ref.source == "url":
            parts.append(MessageContent.image_part(url=ref.ref, detail=detail))
            continue
        data_uri = ref.data_uri
        if data_uri is not None:
            parts.append(MessageContent.image_part(url=data_uri, detail=detail))
    return parts


async def image_refs_to_edit_files(
    refs: List[ImageRef],
    protection: ProtectionContext | None = None,
) -> List[tuple[str, bytes]]:
    """Materialize :class:`ImageRef` inputs as ``(filename, bytes)`` for editing.

    Local/data references decode their base64 payload; remote references are
    fetched. References that cannot be materialized are skipped.
    """

    import base64

    files: List[tuple[str, bytes]] = []
    for index, ref in enumerate(refs):
        payload: bytes | None = None
        if ref.data is not None:
            try:
                payload = base64.b64decode(ref.data)
            except (ValueError, TypeError):
                payload = None
        elif ref.source == "url":
            try:
                if protection is not None:
                    payload = await asyncio.to_thread(
                        protection.fetch_remote_bytes,
                        ref.ref,
                        reason="Materializing a remote image for image editing",
                        expected_content_prefix="image/",
                    )
                else:
                    payload = await asyncio.to_thread(_unprotected_fetch, ref.ref)
            except ProtectionError:
                raise
            except OSError:
                payload = None
        if payload is None:
            continue
        extension = (ref.media_type or "image/png").split("/")[-1]
        files.append((f"reference_{index}.{extension}", payload))
    return files


def image_generation_kwargs(params: Dict[str, Any]) -> Dict[str, Any]:
    """Extract image size/quality/style/n kwargs from output-contract params."""

    kwargs: Dict[str, Any] = {}
    for key in ("size", "quality", "style", "n"):
        value = params.get(key)
        if value is not None:
            kwargs[key] = value
    return kwargs


async def render_image(
    client: LLMClient,
    prompt: str,
    *,
    model: str,
    kwargs: Dict[str, Any],
    edit_files: Optional[List[tuple[str, bytes]]] = None,
) -> tuple[List[Dict[str, Any]], str]:
    """Produce an image for *prompt*, editing when *edit_files* are supplied.

    Returns ``(generated, method)`` where ``generated`` is a list of provider
    image dicts and ``method`` is ``"edit_image"`` or ``"generate_image"``.
    """

    call_kwargs = dict(kwargs)
    if edit_files:
        call_kwargs.pop("style", None)
        response = await client.edit_image(
            prompt, edit_files, model=model, **call_kwargs
        )
        method = "edit_image"
    else:
        response = await client.generate_image(prompt, model=model, **call_kwargs)
        method = "generate_image"
    generated = [image.model_dump() for image in response.data]
    return generated, method


def primary_image_output(generated: List[Dict[str, Any]]) -> str:
    """Return the primary URL or base64 payload from produced images."""

    if not generated:
        return ""
    first = generated[0]
    return first.get("url") or first.get("b64_json") or ""


def decode_generated_image(
    generated: List[Dict[str, Any]],
    protection: ProtectionContext | None = None,
) -> Optional[bytes]:
    """Return PNG bytes for the first produced image (decoding/fetching as needed)."""

    if not generated:
        return None
    import base64

    first = generated[0]
    if first.get("b64_json"):
        return base64.b64decode(first["b64_json"])
    if first.get("url"):
        if protection is not None:
            return protection.fetch_remote_bytes(
                first["url"],
                reason="Downloading an image returned by the configured model provider",
                expected_content_prefix="image/",
            )
        return _unprotected_fetch(first["url"])
    return None


def _unprotected_fetch(url: str) -> bytes:
    with urllib.request.urlopen(url) as response:  # noqa: S310
        return bytes(response.read())


@dataclass
class PromptConfig:
    """Per-prompt runtime configuration."""

    model: Optional[str] = None
    temperature: Optional[float] = None


@dataclass
class RuntimeConfig:
    """Runtime configuration loaded from a .weavemark.yaml file."""

    engine: str = "single-call"
    model: str | None = None
    image_model: str | None = None
    temperature: float | None = None
    allowed_models: tuple[str, ...] = ()
    engine_config: Dict[str, Any] = field(default_factory=dict)
    prompts: Dict[str, PromptConfig] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    protection: ProtectionContext | None = field(
        default=None,
        repr=False,
        compare=False,
    )

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "RuntimeConfig":
        """Validate and load runtime configuration from a mapping."""
        engine = data.get("engine", "single-call")
        if not isinstance(engine, str) or not engine:
            raise ValueError("Runtime config 'engine' must be a non-empty string.")

        prompts_data = _runtime_mapping(data.get("prompts"), "prompts")
        prompt_configs: dict[str, PromptConfig] = {}
        for name, value in prompts_data.items():
            if not isinstance(name, str) or not isinstance(value, Mapping):
                raise ValueError("Runtime config 'prompts' must map names to objects.")
            prompt_configs[name] = PromptConfig(
                model=_runtime_optional_string(
                    value.get("model"), f"prompts.{name}.model"
                ),
                temperature=_runtime_optional_temperature(
                    value.get("temperature"),
                    f"prompts.{name}.temperature",
                ),
            )

        allowed_models_value = data.get("allowed_models")
        if allowed_models_value is None:
            allowed_models: tuple[str, ...] = ()
        elif isinstance(allowed_models_value, (list, tuple)) and all(
            isinstance(item, str) and item for item in allowed_models_value
        ):
            allowed_models = tuple(allowed_models_value)
        else:
            raise ValueError(
                "Runtime config 'allowed_models' must be an array of "
                "non-empty model names."
            )

        return cls(
            engine=engine,
            model=_runtime_optional_string(data.get("model"), "model"),
            image_model=_runtime_optional_string(
                data.get("image_model"),
                "image_model",
            ),
            temperature=_runtime_optional_temperature(
                data.get("temperature"),
                "temperature",
            ),
            allowed_models=allowed_models,
            engine_config=dict(
                _runtime_mapping(data.get("engine_config"), "engine_config")
            ),
            prompts=prompt_configs,
            variables=dict(_runtime_mapping(data.get("variables"), "variables")),
        )

    @classmethod
    def from_yaml(cls, path: Path) -> "RuntimeConfig":
        """Load config from a YAML file."""
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML is required for .weavemark.yaml config files. "
                "Install it with: pip install pyyaml"
            ) from None
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if data is None:
            return cls()
        if not isinstance(data, Mapping):
            raise ValueError("Runtime config root must be an object.")
        return cls.from_mapping(data)

    @classmethod
    def from_json(cls, path: Path) -> "RuntimeConfig":
        """Load config from a JSON file."""
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, Mapping):
            raise ValueError("Runtime config root must be an object.")
        return cls.from_mapping(data)


def _runtime_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"Runtime config {label!r} must be an object.")
    return value


def _runtime_optional_string(value: Any, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(
            f"Runtime config {label!r} must be a non-empty string or null."
        )
    return value


def _runtime_optional_temperature(value: Any, label: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Runtime config {label!r} must be a number or null.")
    return float(value)


@dataclass
class ExecutionResult:
    """Result of executing a compiled spec via an engine."""

    output: str
    steps: List[StepRecord] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EffectiveCallSettings:
    """Resolved provider-call settings with auditable provenance."""

    model: str
    temperature: float | None
    modality: Literal["text", "vision", "image"]
    prompt_key: str
    stage: str
    model_source: str
    temperature_source: str

    def metadata(self) -> dict[str, Any]:
        """Return serializable provenance for execution traces."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "modality": self.modality,
            "prompt_key": self.prompt_key,
            "stage": self.stage,
            "model_source": self.model_source,
            "temperature_source": self.temperature_source,
        }


def resolve_call_settings(
    result: CompositionResult,
    config: RuntimeConfig | None,
    *,
    prompt_key: str,
    stage: str | None = None,
    modality: Literal["text", "vision", "image"] = "text",
    output_contract: Any | None = None,
) -> EffectiveCallSettings:
    """Resolve one provider call using the canonical precedence policy."""
    stage_name = stage or prompt_key
    prompt_config = config.prompts.get(prompt_key) if config else None
    default_prompt_config = config.prompts.get("default") if config else None
    engine_config = config.engine_config if config else {}
    execution = result.execution or {}

    model_candidates: list[tuple[Any, str]]
    if modality == "image":
        output_model = (
            output_contract.params.get("model") if output_contract is not None else None
        )
        model_candidates = [
            (config.image_model if config else None, "runtime.image_model"),
            (
                prompt_config.model if prompt_config else None,
                f"prompts.{prompt_key}.model",
            ),
            (
                engine_config.get(f"{stage_name}_model"),
                f"engine_config.{stage_name}_model",
            ),
            (engine_config.get("image_model"), "engine_config.image_model"),
            (output_model, f"outputs.{prompt_key}.model"),
            (execution.get("image_model"), "@execute.image_model"),
            (DEFAULT_IMAGE_MODEL, "built-in image default"),
        ]
    else:
        model_candidates = [
            (config.model if config else None, "runtime.model"),
            (
                prompt_config.model if prompt_config else None,
                f"prompts.{prompt_key}.model",
            ),
            (
                engine_config.get(f"{stage_name}_model"),
                f"engine_config.{stage_name}_model",
            ),
            (engine_config.get("model"), "engine_config.model"),
            (execution.get("model"), "@execute.model"),
            (
                default_prompt_config.model if default_prompt_config else None,
                "prompts.default.model",
            ),
            (DEFAULT_MODEL, "built-in text default"),
        ]
    model, model_source = _first_setting(model_candidates)

    temperature, temperature_source = _first_setting(
        [
            (config.temperature if config else None, "runtime.temperature"),
            (
                prompt_config.temperature if prompt_config else None,
                f"prompts.{prompt_key}.temperature",
            ),
            (
                engine_config.get(f"{stage_name}_temperature"),
                f"engine_config.{stage_name}_temperature",
            ),
            (engine_config.get("temperature"), "engine_config.temperature"),
            (execution.get("temperature"), "@execute.temperature"),
            (
                default_prompt_config.temperature if default_prompt_config else None,
                "prompts.default.temperature",
            ),
            (None if modality == "image" else 0.7, "built-in default"),
        ],
        allow_none=modality == "image",
    )

    model = str(model)
    if config and config.allowed_models and model not in config.allowed_models:
        allowed = ", ".join(config.allowed_models)
        raise ValueError(
            f"Resolved model {model!r} is not allowed by runtime policy "
            f"(allowed: {allowed})."
        )
    return EffectiveCallSettings(
        model=model,
        temperature=(float(temperature) if temperature is not None else None),
        modality=modality,
        prompt_key=prompt_key,
        stage=stage_name,
        model_source=model_source,
        temperature_source=temperature_source,
    )


def _first_setting(
    candidates: list[tuple[Any, str]],
    *,
    allow_none: bool = False,
) -> tuple[Any, str]:
    for value, source in candidates:
        if value is not None:
            return value, source
    if allow_none:
        return None, "not applicable"
    raise ValueError("No provider-call setting could be resolved.")


@runtime_checkable
class Engine(Protocol):
    """Protocol for execution engines.

    Any object with an ``execute`` method matching this signature works.
    No inheritance required — duck typing is sufficient. ``on_artifact`` is
    optional: engines predating streaming persistence that omit it are invoked
    through :func:`call_engine_execute`, which forwards it only when accepted.
    """

    async def execute(
        self,
        result: CompositionResult,
        config: Optional[RuntimeConfig] = None,
        on_step: Optional[OnStepCallback] = None,
        on_artifact: Optional[ArtifactCallback] = None,
    ) -> ExecutionResult: ...


def _execute_accepts_on_artifact(execute: Any) -> bool:
    """Whether an engine's ``execute`` accepts an ``on_artifact`` keyword."""

    import inspect

    try:
        parameters = inspect.signature(execute).parameters
    except (TypeError, ValueError):
        return False
    return any(
        name == "on_artifact" or param.kind is inspect.Parameter.VAR_KEYWORD
        for name, param in parameters.items()
    )


async def call_engine_execute(
    engine: "Engine",
    result: CompositionResult,
    config: Optional[RuntimeConfig] = None,
    *,
    on_step: Optional[OnStepCallback] = None,
    on_artifact: Optional[ArtifactCallback] = None,
) -> ExecutionResult:
    """Invoke ``engine.execute``, forwarding ``on_artifact`` only when supported.

    The engine interface is duck-typed, so engines predating streaming
    persistence accept only ``on_step``. This keeps those engines working while
    forwarding ``on_artifact`` to the ones that support it.
    """

    if on_artifact is not None and _execute_accepts_on_artifact(engine.execute):
        return await engine.execute(
            result, config, on_step=on_step, on_artifact=on_artifact
        )
    return await engine.execute(result, config, on_step=on_step)


class BaseEngine:
    """Convenience base class for engines that delegate to ellements strategies.

    Prompt validation lives inside the strategies themselves: they raise
    :class:`ellements.core.PromptKeyMissingError` when a required named
    prompt is not supplied, so engines do not pre-check anything here.
    """

    def __init__(self, client: Optional[LLMClient] = None) -> None:
        self.client = client or new_client(model=DEFAULT_MODEL)

    @staticmethod
    def _require_text_only(result: CompositionResult, engine_name: str) -> None:
        image_inputs = [key for key, images in result.prompt_images.items() if images]
        image_outputs = [
            key for key, contract in result.prompt_outputs.items() if contract.is_image
        ]
        if image_inputs or image_outputs:
            raise ValueError(
                f"The {engine_name} engine does not support multimodal inputs or "
                "image outputs. Use single-call, chain, or reflection instead."
            )

    def _build_strategy_config(
        self,
        result: CompositionResult,
        config: Optional[RuntimeConfig] = None,
        on_step: Optional[OnStepCallback] = None,
        *,
        prompt_key: str = "default",
        stage: str | None = None,
    ) -> Dict[str, Any]:
        """Merge execution metadata from the spec with runtime config."""
        strategy_config: Dict[str, Any] = {}
        # Start with spec-level @execute config
        if result.execution:
            strategy_config.update(
                {k: v for k, v in result.execution.items() if k != "type"}
            )
        # Override with runtime engine_config
        if config and config.engine_config:
            strategy_config.update(config.engine_config)
        call_settings = resolve_call_settings(
            result,
            config,
            prompt_key=prompt_key,
            stage=stage,
        )
        strategy_config["model"] = call_settings.model
        if call_settings.temperature is not None:
            strategy_config["temperature"] = call_settings.temperature
        # Inject on_step callback
        if on_step:
            strategy_config["on_step"] = on_step
        return strategy_config

    def _wrap_result(
        self,
        sr: StrategyResult,
        result: CompositionResult,
        config: RuntimeConfig | None,
    ) -> ExecutionResult:
        """Convert a strategy result to an ExecutionResult."""
        metadata = dict(sr.metadata)
        metadata["call_settings"] = resolve_call_settings(
            result,
            config,
            prompt_key="default",
        ).metadata()
        return ExecutionResult(
            output=sr.output,
            steps=sr.steps,
            metadata=metadata,
        )
