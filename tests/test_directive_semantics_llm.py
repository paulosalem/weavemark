"""LLM-backed functional tests for semantic directive behavior.

These tests are intentionally integration-gated. Directive semantics are core
functionality, so the tests use the real compiler and an LLM judge rather than
only mocked structural checks.
"""

from __future__ import annotations

import json
import os
import re
import textwrap
from pathlib import Path
from typing import Any

import pytest
from ellements.core import LLMClient

from weavemark.controller import WeaveMarkConfig, WeaveMarkController
from weavemark.defaults import DEFAULT_MODEL

_skip_no_api_key = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set — directive functional tests require a real LLM",
)

_MODEL = os.getenv("WEAVEMARK_TEST_MODEL", DEFAULT_MODEL)


async def _compile(
    source: str,
    tmp_path: Path,
    *,
    variables: dict[str, Any] | None = None,
) -> str:
    controller = WeaveMarkController(WeaveMarkConfig(model=_MODEL, temperature=0.0))
    result = await controller.compose(
        textwrap.dedent(source).strip(),
        variables=variables or {},
        base_dir=tmp_path,
    )
    assert result.errors == []
    assert result.composed_prompt.strip()
    return result.composed_prompt


async def _judge(
    *,
    directive: str,
    contract: str,
    source: str,
    output: str,
) -> dict[str, Any]:
    client = LLMClient(model=_MODEL)
    response = await client.complete(
        [
            {
                "role": "system",
                "content": (
                    "You are a strict WeaveMark directive functional-test judge. "
                    "Return JSON only with keys: passes (boolean), violations "
                    "(array of strings), and evidence (array of strings). A test "
                    "passes only when the output satisfies the directive contract "
                    "without relying on raw directive text."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Directive under test: {directive}\n\n"
                    f"Contract:\n{contract}\n\n"
                    f"Source WeaveMark:\n```promplet\n{source}\n```\n\n"
                    f"Compiled output:\n```markdown\n{output}\n```"
                ),
            },
        ],
        model=_MODEL,
        temperature=0.0,
    )
    return _parse_json_response(response)


def _parse_json_response(response: str) -> dict[str, Any]:
    stripped = response.strip()
    fence = re.fullmatch(r"```(?:json)?\s*(?P<body>.*?)\s*```", stripped, re.DOTALL)
    if fence:
        stripped = fence.group("body").strip()
    data = json.loads(stripped)
    assert isinstance(data, dict)
    return data


async def _assert_directive_passes(
    *,
    directive: str,
    contract: str,
    source: str,
    output: str,
) -> None:
    verdict = await _judge(
        directive=directive,
        contract=contract,
        source=source,
        output=output,
    )
    assert verdict.get("passes") is True, verdict


@_skip_no_api_key
class TestDirectiveSemanticFunctionality:
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_refine_preserves_imported_obligations_and_specializes(
        self, tmp_path: Path
    ) -> None:
        (tmp_path / "base.weavemark.md").write_text(
            textwrap.dedent("""
            @note
              Private author note that must not appear.

            The output must include:
            - Exact identifier `RISK_GATE_ALPHA`
            - A Review Cadence section
            - A Failure Mode Handling section
            """).strip(),
            encoding="utf-8",
        )
        source = """
        @refine ./base.weavemark.md

        Adapt this for a launch-readiness checklist for a browser game.
        """
        output = await _compile(source, tmp_path)
        await _assert_directive_passes(
            directive="@refine",
            contract=(
                "The compiled output must preserve the imported public obligations, "
                "including exact identifier RISK_GATE_ALPHA, Review Cadence, and "
                "Failure Mode Handling; specialize them for browser-game launch "
                "readiness; and omit private @note material and raw @refine syntax."
            ),
            source=source,
            output=output,
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_normalize_harmonizes_without_losing_requirements(
        self, tmp_path: Path
    ) -> None:
        source = """
        @normalize use consistent terminology and headings scope: both terminology: normalize
          # Responsibilities
          - The app must keep user Tasks.
          ## Duties
          - The system must archive completed to-dos.
          - It must not delete audit logs.
        """
        output = await _compile(source, tmp_path)
        await _assert_directive_passes(
            directive="@normalize",
            contract=(
                "The output should harmonize terminology/headings while preserving "
                "all three requirements: keep tasks, archive completed to-dos/tasks, "
                "and not delete audit logs. It must not add unrelated requirements."
            ),
            source=source,
            output=output,
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_revise_applies_change_preserving_unrelated_content(
        self, tmp_path: Path
    ) -> None:
        source = """
        @revise require YAML output instead of JSON mode: minimal
          The assistant must return JSON.
          It must include a risk summary.
          It must cite unknowns explicitly.
        """
        output = await _compile(source, tmp_path)
        await _assert_directive_passes(
            directive="@revise",
            contract=(
                "The output must change the format requirement from JSON to YAML "
                "while preserving the risk summary and explicit unknowns requirements. "
                "Minimal mode should avoid unrelated rewrites."
            ),
            source=source,
            output=output,
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_style_changes_presentation_not_information(self, tmp_path: Path) -> None:
        source = """
        @style executive concise bullets
          Include latency budget: 120ms.
          Include fallback mode: offline cache.
          Include owner: Release Engineering.
        """
        output = await _compile(source, tmp_path)
        await _assert_directive_passes(
            directive="@style",
            contract=(
                "The output must become executive/concise/bullet-oriented while "
                "preserving latency budget 120ms, fallback mode offline cache, and "
                "owner Release Engineering."
            ),
            source=source,
            output=output,
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_compress_reduces_text_while_preserving_hard_requirements(
        self, tmp_path: Path
    ) -> None:
        source = """
        @compress concise release checklist target: tokens budget: 80 preserve: hard
          The release checklist must include database backup verification.
          It must include rollback owner assignment.
          It must include customer communication approval.
          It must include monitoring thresholds for error rate and latency.
          It must include a sign-off record with timestamp and approver.
        """
        output = await _compile(source, tmp_path)
        await _assert_directive_passes(
            directive="@compress",
            contract=(
                "The output should be more concise than the source while preserving "
                "all five hard requirements: backup verification, rollback owner, "
                "customer communication approval, error/latency thresholds, and "
                "sign-off record with timestamp and approver."
            ),
            source=source,
            output=output,
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_extract_is_source_grounded_and_marks_missing_info(
        self, tmp_path: Path
    ) -> None:
        source = """
        @extract risks owners missing-deadline format: bullets
          Migration risk: search indexing may lag. Owner: Mira.
          Security risk: API token rotation may fail. Owner: Jules.
          No deadline is provided in the source.
        """
        output = await _compile(source, tmp_path)
        await _assert_directive_passes(
            directive="@extract",
            contract=(
                "The output must extract the two risks and their owners from the "
                "source, and it must not invent a deadline; missing deadline should "
                "be absent or marked missing/unknown."
            ),
            source=source,
            output=output,
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_iterate_records_trace_and_returns_compiled_improvement(
        self, tmp_path: Path
    ) -> None:
        source = """
        @iterate 1
          @expand mode: intention focus: "acceptance criteria"
            onboarding checklist
        """
        controller = WeaveMarkController(WeaveMarkConfig(model=_MODEL, temperature=0.0))
        result = await controller.compose(textwrap.dedent(source).strip(), base_dir=tmp_path)
        assert result.errors == []
        assert result.compilation_trace is not None
        assert result.compilation_trace.steps
        await _assert_directive_passes(
            directive="@iterate",
            contract=(
                "The output must be a compiled expansion of onboarding checklist "
                "with acceptance-criteria intent and no raw @iterate/@expand syntax. "
                "The Python result object, which was checked before this judgment, "
                "must expose a non-empty compilation trace; do not expect trace "
                "metadata inside the markdown output itself."
            ),
            source=source,
            output=result.composed_prompt,
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_output_installs_output_shape_requirements(
        self, tmp_path: Path
    ) -> None:
        source = """
        Draft a triage response.

        @output Return JSON with keys severity, rationale, next_action.
        """
        output = await _compile(source, tmp_path)
        await _assert_directive_passes(
            directive="@output",
            contract=(
                "The output must clearly require JSON output with severity, "
                "rationale, and next_action keys, without leaking raw @output syntax."
            ),
            source=source,
            output=output,
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_summarize_shortens_while_preserving_decision_useful_points(
        self, tmp_path: Path
    ) -> None:
        source = """
        @summarize goal: "decision brief" length: short focus: requirements
          The vendor migration has three required gates. Gate one is legal approval.
          Gate two is data export validation. Gate three is rollback rehearsal.
          Rationale: legal approval prevents contract exposure, export validation
          prevents data loss, and rollback rehearsal reduces operational risk.
        """
        output = await _compile(source, tmp_path)
        await _assert_directive_passes(
            directive="@summarize",
            contract=(
                "The output should be a shorter decision-oriented summary that "
                "preserves all three gates: legal approval, data export validation, "
                "and rollback rehearsal. It must not invent gates."
            ),
            source=source,
            output=output,
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_polish_unifies_presentation_without_adding_or_removing_information(
        self, tmp_path: Path
    ) -> None:
        source = """
        @polish harmonize headings and remove duplicated wording
          Launch things:
          - Need a rollback owner.
          ## Release checklist
          - Rollback owner must be named.
          - QA signoff required.
          Random note: QA signoff is required before release.
        """
        output = await _compile(source, tmp_path)
        await _assert_directive_passes(
            directive="@polish",
            contract=(
                "The output must organize the existing launch/checklist information "
                "coherently, remove duplicate presentation, preserve rollback owner "
                "and QA signoff requirements, and avoid adding new substantive requirements."
            ),
            source=source,
            output=output,
        )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_expand_elaborates_original_intent_without_drift(
        self, tmp_path: Path
    ) -> None:
        source = """
        @expand mode: intention focus: "implementation implications" length: 80%
          local-first task inbox
        """
        output = await _compile(source, tmp_path)
        await _assert_directive_passes(
            directive="@expand",
            contract=(
                "The output must elaborate the local-first task inbox idea into "
                "implementation-relevant prompt content, preserve the local-first "
                "and task inbox intent, and avoid drifting into unrelated product domains."
            ),
            source=source,
            output=output,
        )
