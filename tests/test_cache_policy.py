"""Local API-response cache policy, wiring, and observability tests."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import litellm
import pytest
from ellements.core import LLMClient, LocalCacheConfig
from ellements.core.observability import LLMResponseEvent
from rich.console import Console

from weavemark.app import WeaveMarkEventRenderer
from weavemark.cache_policy import CacheSettings
from weavemark.cache_setup import (
    LocalCacheObserver,
    cache_enabled,
    default_cache_dir,
)
from weavemark.engines.base import render_image
from weavemark.engines.chat import ChatEngine
from weavemark.logging_policy import LoggingSettings
from weavemark.logging_setup import new_client
from weavemark.settings import load_weavemark_settings

_MODEL = "openai/gpt-4o-mini"


def test_local_cache_is_enabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WEAVEMARK_CACHE", raising=False)
    assert cache_enabled() is True


@pytest.mark.parametrize("value", ["0", "off", "false", "no", "OFF", "False"])
def test_local_cache_environment_opt_out(
    monkeypatch: pytest.MonkeyPatch,
    value: str,
) -> None:
    monkeypatch.setenv("WEAVEMARK_CACHE", value)
    assert cache_enabled() is False
    assert default_cache_dir() is None


def test_local_cache_directory_environment_override(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    target = tmp_path / "responses"
    monkeypatch.setenv("WEAVEMARK_CACHE_DIR", str(target))
    assert default_cache_dir() == target


def test_project_can_disable_but_not_force_or_redirect_user_cache(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_config = tmp_path / "user.json"
    user_directory = tmp_path / "user-cache"
    user_config.write_text(
        json.dumps(
            {
                "cache": {
                    "enabled": False,
                    "directory": str(user_directory),
                }
            }
        ),
        encoding="utf-8",
    )
    project = tmp_path / "project"
    project.mkdir()
    project_directory = tmp_path / "project-cache"
    (project / "weavemark.json").write_text(
        json.dumps(
            {
                "cache": {
                    "enabled": True,
                    "directory": str(project_directory),
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("WEAVEMARK_USER_CONFIG", str(user_config))
    global_config = tmp_path / "global.json"
    global_config.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("WEAVEMARK_GLOBAL_CONFIG", str(global_config))

    result = load_weavemark_settings(project)

    assert result.errors == ()
    assert result.settings.cache == CacheSettings(
        enabled=False,
        directory=user_directory,
    )
    assert result.warnings == (
        f"{project / 'weavemark.json'} cannot change user-level cache.directory.",
    )


def test_invalid_cache_config_is_reported(tmp_path: Path) -> None:
    (tmp_path / "weavemark.json").write_text(
        json.dumps(
            {
                "cache": {
                    "enabled": "yes",
                    "directory": 42,
                    "unknown": True,
                }
            }
        ),
        encoding="utf-8",
    )

    result = load_weavemark_settings(tmp_path)

    assert any("unsupported key" in error for error in result.errors)
    assert any("cache.enabled must be boolean" in error for error in result.errors)
    assert any("cache.directory" in error for error in result.errors)


@pytest.mark.asyncio
async def test_local_cache_observer_logs_and_reports_explicit_local_hit(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reported: list[dict[str, object]] = []
    observer = LocalCacheObserver(reported.append)
    monkeypatch.setattr(logging.getLogger("weavemark"), "propagate", True)

    with caplog.at_level(logging.INFO, logger="weavemark"):
        await observer.on_response(
            LLMResponseEvent(
                call_id="cache-call",
                method="complete",
                model=_MODEL,
                response="cached",
                duration_ms=1,
                metadata={
                    "local_cache": {
                        "hit": True,
                        "hits": 1,
                        "backend": "litellm-disk",
                    }
                },
            )
        )

    assert "LOCAL cache used" in caplog.text
    assert reported == [
        {
            "method": "complete",
            "model": _MODEL,
            "backend": "litellm-disk",
            "hits": 1,
        }
    ]


def test_verbose_renderer_names_local_cache_explicitly() -> None:
    console = Console(record=True)
    WeaveMarkEventRenderer().render(
        "local_cache_hit",
        {"method": "complete", "model": _MODEL},
        console,
    )
    assert "LOCAL cache used" in console.export_text()


@pytest.mark.asyncio
async def test_new_client_reuses_exact_text_request_from_disk(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("WEAVEMARK_CACHE", raising=False)
    monkeypatch.setenv("WEAVEMARK_CACHE_DIR", str(tmp_path / "cache"))
    hits: list[dict[str, object]] = []
    client = new_client(
        model=_MODEL,
        logging_settings=LoggingSettings(enabled=False),
        on_cache_hit=hits.append,
    )

    try:
        first = await client.complete(
            "weavemark exact local cache test",
            temperature=0.3,
            mock_response="FIRST",
        )
        await asyncio.sleep(0.5)
        repeated = await client.complete(
            "weavemark exact local cache test",
            temperature=0.3,
            mock_response="FIRST",
        )
        changed = await client.complete(
            "weavemark exact local cache test",
            temperature=0.2,
            mock_response="THIRD",
        )
    finally:
        litellm.cache = None

    assert first == repeated == "FIRST"
    assert changed == "THIRD"
    assert hits[0]["backend"] == "litellm-disk"


@pytest.mark.asyncio
async def test_disabled_client_does_not_write_to_process_cache(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("WEAVEMARK_CACHE", raising=False)
    monkeypatch.setenv("WEAVEMARK_CACHE_DIR", str(tmp_path / "cache"))
    new_client(
        model=_MODEL,
        logging_settings=LoggingSettings(enabled=False),
    )
    configured_cache = litellm.cache
    assert configured_cache is not None
    disk_cache = configured_cache.cache.disk_cache
    assert len(disk_cache) == 0
    disabled_client = LLMClient(model=_MODEL)

    try:
        await disabled_client.complete(
            "do not persist this request",
            mock_response="uncached",
        )
        await asyncio.sleep(0.5)
        assert len(disk_cache) == 0
    finally:
        litellm.cache = None


def test_new_client_honors_disabled_cache(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WEAVEMARK_CACHE", "0")
    client = new_client(
        model=_MODEL,
        logging_settings=LoggingSettings(enabled=False),
    )
    assert client.local_cache is None
    assert not any(
        isinstance(observer, LocalCacheObserver) for observer in client.observers
    )


@pytest.mark.asyncio
async def test_cached_weavemark_image_calls_request_durable_base64(
    tmp_path: Path,
) -> None:
    client = LLMClient(
        model="openai/dall-e-3",
        local_cache=LocalCacheConfig(
            tmp_path,
            cache_responses=False,
        ),
    )
    provider = AsyncMock(
        return_value=SimpleNamespace(
            created=1,
            data=[{"b64_json": "image-data"}],
            model="openai/dall-e-3",
            usage=None,
        )
    )

    with patch("ellements.core.llm.client.litellm.aimage_generation", provider):
        generated, method = await render_image(
            client,
            "A durable image.",
            model="openai/dall-e-3",
            kwargs={},
        )

    assert method == "generate_image"
    assert generated[0]["b64_json"] == "image-data"
    assert provider.await_args.kwargs["response_format"] == "b64_json"


@pytest.mark.asyncio
async def test_cached_gpt_image_edits_omit_rejected_response_format(
    tmp_path: Path,
) -> None:
    client = LLMClient(
        model="openai/gpt-image-1.5",
        local_cache=LocalCacheConfig(
            tmp_path,
            cache_responses=False,
        ),
    )
    provider = AsyncMock(
        return_value=SimpleNamespace(
            created=1,
            data=[{"b64_json": "edited-image-data"}],
            model="openai/gpt-image-1.5",
            usage=None,
        )
    )

    with patch("ellements.core.llm.client.litellm.aimage_edit", provider):
        generated, method = await render_image(
            client,
            "Edit from references.",
            model="openai/gpt-image-1.5",
            kwargs={"response_format": "b64_json"},
            edit_files=[("reference.png", b"reference")],
        )

    assert method == "edit_image"
    assert generated[0]["b64_json"] == "edited-image-data"
    assert "response_format" not in provider.await_args.kwargs


@pytest.mark.asyncio
async def test_cached_dall_e_edits_request_durable_base64(tmp_path: Path) -> None:
    client = LLMClient(
        model="openai/dall-e-2",
        local_cache=LocalCacheConfig(
            tmp_path,
            cache_responses=False,
        ),
    )
    provider = AsyncMock(
        return_value=SimpleNamespace(
            created=1,
            data=[{"b64_json": "edited-image-data"}],
            model="openai/dall-e-2",
            usage=None,
        )
    )

    with patch("ellements.core.llm.client.litellm.aimage_edit", provider):
        generated, method = await render_image(
            client,
            "Edit from references.",
            model="openai/dall-e-2",
            kwargs={},
            edit_files=[("reference.png", b"reference")],
        )

    assert method == "edit_image"
    assert generated[0]["b64_json"] == "edited-image-data"
    assert provider.await_args.kwargs["response_format"] == "b64_json"


@pytest.mark.asyncio
async def test_chat_engine_passes_resolved_cache_policy_to_client() -> None:
    logging_settings = LoggingSettings(enabled=False)
    cache_settings = CacheSettings(enabled=False)
    engine = ChatEngine(
        system_prompt="Help select a promplet.",
        tools=[],
        tool_executor=AsyncMock(),
        ui=SimpleNamespace(get_user_input=lambda: ""),
        model=_MODEL,
        logging_settings=logging_settings,
        cache_settings=cache_settings,
    )

    with patch("weavemark.logging_setup.new_client") as client_factory:
        await engine.run()

    client_factory.assert_called_once_with(
        model=_MODEL,
        logging_settings=logging_settings,
        cache_settings=cache_settings,
    )
