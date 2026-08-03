"""Contracts for clean LiteLLM background-worker shutdown."""

from __future__ import annotations

import asyncio

import pytest

from weavemark.controller import _cleanup_litellm_logging_worker


@pytest.mark.asyncio
async def test_cleanup_finishes_running_tasks_before_reset() -> None:
    import litellm.litellm_core_utils.logging_worker as logging_worker

    worker = logging_worker.GLOBAL_LOGGING_WORKER
    await _cleanup_litellm_logging_worker()
    completed = asyncio.Event()

    async def callback() -> None:
        await asyncio.sleep(0)
        completed.set()

    worker.ensure_initialized_and_enqueue(callback())
    await _cleanup_litellm_logging_worker()

    assert completed.is_set()
    assert worker._queue is None
    assert worker._worker_task is None
    assert worker._running_tasks == set()
    assert worker._sem is None
    assert worker._bound_loop is None
