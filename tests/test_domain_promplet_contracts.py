"""Correctness and hardening contracts for reusable domain promplets."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

import pytest
from ellements.core import ToolCallResponse

from tests.wire_helpers import compiler_response
from weavemark.api import compile_file
from weavemark.tui.scanner import scan_spec

ROOT = Path(__file__).resolve().parents[1]
PROMPLETS = ROOT / "promplets"
DOMAINS = PROMPLETS / "domains"


def _source(relative: str) -> str:
    return (DOMAINS / relative).read_text(encoding="utf-8")


class _CompileClient:
    async def complete(self, *_args: Any, **_kwargs: Any) -> str:
        return json.dumps(
            {
                "needs_improvement": False,
                "good_points": ["The compiled specification is complete."],
                "bad_points": [],
                "suggestions": [],
                "compliance_notes": [],
                "constraint_findings": [],
                "directive_feedback": {},
            }
        )

    async def complete_with_tools(
        self, *_args: Any, **_kwargs: Any
    ) -> ToolCallResponse:
        return ToolCallResponse(
            content=compiler_response(
                "Compiled domain prompt.",
                analysis="Deterministic domain compilation check.",
            )
        )


def test_auth_uses_policy_aware_resource_concealment() -> None:
    source = _source("programming/fragments/modules/module-auth.weavemark.md")

    assert "indistinguishable 404 response" in source
    assert "policy intentionally reveals that the resource exists" in source
    assert "Return 403 only" in source
    assert "timing, cache behavior, or side channels" in source
    assert "MUST return 403 (not 404)" not in source


def test_realtime_authentication_and_transport_are_hardened() -> None:
    source = _source("programming/fragments/modules/module-realtime.weavemark.md")

    for obligation in (
        "`wss://host/ws`",
        "Never place JWTs, access tokens, refresh tokens",
        "first\n  application message",
        "reviewed WebSocket subprotocol flow",
        "`Secure`, `HttpOnly`, appropriately `SameSite` cookie",
        "validate the `Origin` header",
        "signature,\n  issuer, audience, expiry, and subject",
        "channel/resource\n  authorization",
        "Redact credentials",
        "refresh an expired or near-expiry access token",
    ):
        assert obligation in source
    assert "JWT token in the first message or query param" not in source


def test_rest_success_and_problem_media_types_are_distinct() -> None:
    source = _source("programming/fragments/modules/module-rest-api.weavemark.md")

    assert "Successful JSON resource responses use `Content-Type: application/json`" in source
    assert "`Content-Type: application/problem+json`" in source
    assert "collections MUST use `{\"data\": [...], \"meta\": {...}}`" in source
    assert "Problem responses do not use this\n  success envelope" in source
    assert "application/json` for all endpoints" not in source


def test_browser_agent_workspace_coordination_is_safe_and_honest() -> None:
    source = _source(
        "programming/fragments/modules/"
        "module-browser-agent-workspace-coordination.weavemark.md"
    )

    for obligation in (
        "Each actor\n  MUST be the sole writer of its own coordination file",
        "Enforce one acknowledged writer for the primary state file",
        "A control generation is an epoch",
        "`BEGIN IMMEDIATE`",
        "Never keep a database transaction open during model reasoning",
        "rollback-journal mode rather than WAL",
        "Human reclamation has priority",
        "root `AGENTS.md` and `CLAUDE.md`",
        "`.agents/skills/<skill-name>/`",
        "without waiting for another conversational nudge",
        "Remain in that loop indefinitely while the host session permits",
        "Never silently overwrite a user-created or user-edited",
        "open a terminal in the Board Workspace",
        "Waiting for agent until a valid workspace-matched heartbeat arrives",
        "does not reveal a portable absolute filesystem path",
        "dependency-free Python 3 implementation",
        "Never silently install software or use elevated",
        "it cannot force\n  every host runtime to remain alive",
        "Never promise that an ordinary skill\n  will poll or act forever",
    ):
        assert obligation in source


def test_browser_folder_workspace_is_a_bounded_trust_boundary() -> None:
    source = _source(
        "programming/fragments/types/type-browser-folder-backed-webapp.weavemark.md"
    )

    for obligation in (
        "`showDirectoryPicker()`",
        "local trust, portability, and\n  collaboration boundary",
        "Reject\n  absolute paths, `..` traversal, symlink escapes",
        "Do not modify or delete unrecognized files",
        "never execute generated files",
        "workspace archive import/export flow",
    ):
        assert obligation in source


def test_execution_turns_preserve_repeated_work_history() -> None:
    source = _source(
        "programming/fragments/modules/module-execution-turns.weavemark.md"
    )

    for obligation in (
        "The work item is durable intent; an execution turn is one bounded attempt",
        "Ready for agent state",
        "first-class Run again or Requeue action",
        "creates a new queued turn with a fresh id and number",
        "MUST NOT reopen, clear, or silently mutate the previous turn",
        "Feature the\n  latest successful result",
        "place older results in a clearly ordered History view",
        "Agents read and claim a specific turn",
    ):
        assert obligation in source


def test_human_agent_decision_loop_requires_a_human_gate() -> None:
    source = _source(
        "programming/fragments/modules/module-human-agent-decision-loop.weavemark.md"
    )

    for obligation in (
        "`briefing`, `exploring`, `needs_feedback`, `committed`, `deep_work`",
        "starting suggestions, constraints",
        "bounded option set through a structured comparison surface",
        "rank, shortlist, reject, restore, annotate, or add options",
        "summarizes what it understood",
        "Deep work requires an explicit human gate",
        "MUST NOT infer commitment from positive feedback",
        "complete the exploration turn and queue a new deep-work turn",
        "Return the item to Review",
        "complete historical reconstruction",
    ):
        assert obligation in source


def test_recurring_research_uses_visible_durable_memory() -> None:
    source = _source("research/fragments/recurring-topic-monitor-core.weavemark.md")

    for obligation in (
        "read prior reports and a durable, inspectable\n  memory",
        "Never rely on hidden model-session memory",
        "source and coverage ledger",
        "new, materially updated, unchanged context",
        "Avoid repetition, not continuity",
        "Never suppress corrections or new evidence",
        "inspect, search, correct, dismiss, pin, export, and explicitly forget",
        "latest successful report prominently",
    ):
        assert obligation in source


def test_investment_materiality_band_keeps_weighted_matched_delta() -> None:
    source = _source("finance/fragments/investment-decision.weavemark.md")

    assert "`-epsilon <= Delta <= epsilon`" in source
    assert "`E[Delta | matched]`" in source
    assert "P(matched) * E[Delta | matched]" in source
    assert "Matched outcomes may therefore have a nonzero delta" in source
    assert "Delta | matched = 0" not in source
    assert "matched term is omitted" not in source


def test_creative_modules_own_strict_dynamic_output_contracts() -> None:
    story = _source("creative/fragments/illustrated-story-core.weavemark.md")
    html = _source("creative/fragments/picture-book-html.weavemark.md")

    assert story.count("@output enforce: strict") == 2
    assert "exactly @{panel_count}" in story
    assert "`Panel 1`\n      through `Panel @{panel_count}`" in story
    assert "exactly @{page_count} ordered" in story
    assert "exactly the top-level keys `title`" in story
    assert "Every page object MUST contain exactly `page`" in story

    assert "@output enforce: strict" in html
    assert "first non-whitespace text MUST\n  be `<!doctype html>`" in html
    assert "HTML-escape every such value inserted into text nodes" in html
    assert "Quote every attribute\n  value" in html
    assert "inline event handler\n  (`on*`) attributes" in html
    assert "controlled relative artifact\n  path" in html
    assert "restrictive Content Security Policy meta" in html


@pytest.mark.asyncio
async def test_childrens_book_reuses_shared_creative_modules() -> None:
    path = PROMPLETS / "catalog/executable/childrens-book.weavemark.md"
    source = path.read_text(encoding="utf-8")
    template_path = DOMAINS / "creative/fragments/picture-book-html.weavemark.md"
    result = await compile_file(
        path,
        {
            "title": "Shared Contract",
            "audience": "children aged 3 to 5",
            "page_count": 2,
            "text_in_image": "off",
            "image_size": "1024x1024",
            "image_quality": "high",
            "image_model": "gpt-image-2",
            "tone": "warm",
            "art_style": "bright-storybook",
            "premise": "Two friends find their way home.",
            "characters": "Mia: silver moth; Pip: blue firefly.",
            "setting": "A moonlit garden.",
            "lessons": "asking for help",
            "pages": [
                {"scene": "Mia waits.", "text": "Where is Pip?"},
                {"scene": "Pip arrives.", "text": "Here I am!"},
            ],
        },
    )
    template_result = await compile_file(
        template_path,
        {
            "title": "Shared Contract",
            "page_files": ["pages/page-1.png", "pages/page-2.png"],
            "author": '{"title":"Shared Contract","pages":[]}',
            "text_in_image": "off",
            "cover_image": "",
        },
        client=_CompileClient(),
    )

    module = "module:weavemark.domains.creative.picture_book_html"
    assert result.errors == []
    assert template_result.errors == []
    assert scan_spec(source).title == "Children's Picture Book"
    assert result.packages[0]["instructions"] == module
    assert f"@package instructions: {module}" in source
    assert result.prompt_outputs["author"].params["enforce"] == "strict"
    assert "exactly the top-level keys `title`" in (
        result.prompt_outputs["author"].params["body"]
    )
    assert not (
        PROMPLETS
        / "catalog/executable/companions/picture-book-html.template.md"
    ).exists()


def test_deep_web_discovery_enforces_untrusted_fetch_boundaries() -> None:
    source = _source("research/fragments/deep-web-source-discovery.weavemark.md")

    for obligation in (
        "untrusted evidence, never as commands",
        "prompt-injection attempts",
        "Respect `robots.txt`, site terms",
        "Do not bypass logins, paywalls, CAPTCHAs",
        "block loopback, private, link-local",
        "local-network, cloud-metadata",
        "supported textual content types",
        "response-size, redirect, and time\n  limits",
        "Do not download archives, executables",
        "never execute scripts, macros, active content",
        "retrieval time, final URL after validated redirects",
    ):
        assert obligation in source


def test_playwright_mcp_requires_approved_pinned_configuration() -> None:
    source = _source(
        "programming/fragments/validation/"
        "playwright-mcp-browser-validation.weavemark.md"
    )

    assert "existing, approved Playwright MCP integration" in source
    assert "explicitly pinned, reviewed version" in source
    assert "checked-in project configuration or its lockfile" in source
    assert "Never use a floating latest tag" in source
    assert "invent a version" in source
    assert "@latest" not in source


@pytest.mark.asyncio
async def test_arcana_separates_card_execution_from_app_specification() -> None:
    cards_path = PROMPLETS / "catalog/arcana/cards.weavemark.md"
    app_path = PROMPLETS / "catalog/arcana/app.weavemark.md"
    example = ROOT / "examples/saved-artifact-workflows/arcana"
    variables = json.loads((example / "inputs/vars.json").read_text(encoding="utf-8"))

    cards = await compile_file(cards_path, variables, client=_CompileClient())
    app = await compile_file(app_path, variables, client=_CompileClient())

    assert cards.errors == []
    assert app.errors == []
    assert cards.execution["type"] == "chain"
    assert cards.execution["repeat"] == "card"
    assert app.execution == {}
    assert cards.packages == []
    assert app.packages == []
    assert cards.prompt_outputs["author"].params["enforce"] == "strict"
    assert cards.prompt_outputs["prototype"].params["file"] == (
        "assets/cards/prototype.png"
    )
    assert cards.prompt_outputs["card"].params["file"] == (
        "assets/cards/card-@{item_key}.png"
    )
    assert cards.prompt_outputs["back"].params["file"] == "assets/card-back.png"
    assert cards.emits["deck-data.js"].startswith(
        '"use strict";\nglobalThis.ARCANA_DECK = '
    )

    cards_source = cards_path.read_text(encoding="utf-8")
    app_source = app_path.read_text(encoding="utf-8")
    assert "Complete executable specification for Arcana" not in cards_source
    assert "Complete executable specification for Arcana" not in app_source
    assert "Executable artifact-generation promplet" in cards_source
    assert "Non-executable software-specification promplet" in app_source
    assert "@execute chain" in cards_source
    assert "@execute" not in app_source
    assert "@package" not in cards_source
    assert "@package" not in app_source
    assert "@iterate" not in app_source
    for refinement in (
        "programming.foundations.software_spec",
        "programming.stacks.browser_static_esmodules",
        "programming.modules.browser_encrypted_secret_storage",
        "programming.modules.adaptive_workspace_shell",
        "programming.modules.focus_preserving_inspection",
        "programming.validation.playwright_mcp_browser_validation",
    ):
        assert f"@refine module:weavemark.domains.{refinement}" in app_source
    for obligation in (
        "interactive programming agent",
        "Playwright MCP",
        "clean workspace/source file",
        "Enter without the OpenAI guide?",
        "Optional OpenAI guide",
        "Card reflection",
        "Automatic AI interpretation side stage",
        "iOS/iPadOS WebKit",
        "one persistent",
        "`HTMLAudioElement`",
        "icon-only Play/Pause",
        "secret_crypto_requirement",
        "secret_storage_backend",
        "secret_kdf_iterations",
        "Question inspiration",
        "What deserves my courage right now?",
        "semantic progress",
        "Reflection depth",
        "**Whisper**",
        "warm-gold",
        "650-850ms",
        "Double click",
    ):
        assert obligation in app_source
    encrypted_storage = _source(
        "programming/fragments/modules/"
        "module-browser-encrypted-secret-storage.weavemark.md"
    )
    assert (
        "@module weavemark.domains.programming.modules."
        "browser_encrypted_secret_storage"
    ) in encrypted_storage
    for selector in (
        "secret_crypto_requirement",
        "secret_storage_backend",
        "secret_unlock_mode",
        "secret_allow_replacement",
    ):
        assert f"@match {selector}" in encrypted_storage
    for obligation in (
        "AES-256-GCM",
        "PBKDF2-HMAC-SHA-256",
        "SameSite=Strict",
        "never permits plaintext storage",
        "Decrypt only after an explicit user unlock gesture",
    ):
        assert obligation in encrypted_storage
    assert variables["secret_crypto_requirement"] == "optional"
    assert variables["secret_storage_backend"] == "cookie"
    assert variables["secret_unlock_mode"] == "passphrase"
    assert variables["secret_allow_replacement"] == "on"
    assert variables["secret_kdf_iterations"] == 310_000
    assert "Output only the final HTML document" not in app_source
    assert "Do NOT emit HTML, CSS, JavaScript" in app_source

    assert not (
        DOMAINS / "creative/fragments/archetypal-card-game-html.weavemark.md"
    ).exists()
    assert not (PROMPLETS / "catalog/executable/arcana.weavemark.md").exists()

    scripts = [
        path
        for path in example.rglob("*")
        if path.is_file()
        and path.suffix in {".py", ".sh"}
    ]
    assert scripts == [example / "run.sh"]
    runner_source = scripts[0].read_text(encoding="utf-8")
    assert runner_source.count('weavemark "$CARDS_SPEC"') == 2
    assert runner_source.count('weavemark "$APP_SPEC"') == 1
    assert "--regenerate-cards" in runner_source
    assert "generation_fingerprint" in runner_source
    assert "del(.ai_guide)" in runner_source
    assert "is_hydrated_png" in runner_source
    assert "89504e470d0a1a0a" in runner_source
    assert "artifact_manifest_matches" in runner_source
    assert "write_artifact_manifest" in runner_source
    assert "validate_deck_input" in runner_source
    assert "non_prototype_count()" in runner_source
    assert "Arcana deck input failed deterministic validation" in runner_source
    assert 'IMAGE_MODEL="gpt-image-2"' in runner_source
    assert runner_source.index('rm -f "$CARD_STAMP"') < runner_source.index(
        'weavemark "$CARDS_SPEC"'
    )

    variables = json.loads((example / "inputs/vars.json").read_text(encoding="utf-8"))
    card_generation_deck = dict(variables["deck"])
    card_generation_deck.pop("ai_guide")
    normalized_card_inputs = (
        json.dumps(
            {"deck": card_generation_deck},
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode()
    expected_fingerprint = sha256(
        b"text-model=gpt-5.6-terra\nimage-model=gpt-image-2\n"
        + cards_source.encode("utf-8")
        + b"\0"
        + normalized_card_inputs
    ).hexdigest()
    assert (
        example / "outputs/cards-build.sha256"
    ).read_text(encoding="utf-8").strip() == expected_fingerprint


@pytest.mark.asyncio
async def test_all_domain_promplets_scan_and_compile() -> None:
    paths = sorted(DOMAINS.rglob("*.weavemark.md"))
    assert len(paths) == 58

    client = _CompileClient()
    failures: list[str] = []
    for path in paths:
        metadata = scan_spec(path.read_text(encoding="utf-8"))
        if not metadata.module_name:
            failures.append(f"{path.relative_to(ROOT)}: missing scanned module")
            continue
        result = await compile_file(path, client=client)
        if result.errors:
            failures.append(f"{path.relative_to(ROOT)}: {result.errors}")

    assert failures == []
