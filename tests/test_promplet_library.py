"""Tests for bundled resources and the unified promplet library."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from weavemark.controller import WeaveMarkConfig, WeaveMarkController
from weavemark.library_cli import (
    create_library_parser,
    parse_library_target,
    run_library_command,
)
from weavemark.promplet_library import (
    PrompletLibraryLookupError,
    collect_library_promplets,
    copy_bundled_promplets,
    iter_bundled_promplets,
    library_sources,
    read_bundled_promplet,
    resolve_library_promplet,
    resolve_module_source,
)


def _write_promplet(
    path: Path,
    title: str,
    *,
    module_name: str | None = None,
    execute: str | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = "@promplet version: 0.7\n\n"
    if module_name:
        header += f"@module {module_name}\n\n"
    if execute:
        header += f"@execute {execute}\n\n"
    path.write_text(
        f"{header}# {title}\n\nHello @{{name}}.\n",
        encoding="utf-8",
    )


def test_bundled_promplets_are_available_from_source_checkout() -> None:
    paths = list(iter_bundled_promplets())
    names = {path.as_posix() for path in paths}

    assert len(paths) > 100
    assert "catalog/standalone/investment-brief.weavemark.md" in names
    assert "# " in read_bundled_promplet(
        "catalog/standalone/investment-brief.weavemark.md"
    )


@pytest.mark.parametrize(
    "path",
    ("../secrets.txt", "/tmp/promplet.weavemark.md", "nested/../../escape"),
)
def test_bundled_promplet_rejects_unsafe_paths(path: str) -> None:
    with pytest.raises(ValueError):
        read_bundled_promplet(path)


def test_source_order_is_project_user_extra_builtin(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = tmp_path / "project"
    user_home = tmp_path / "home"
    extra = tmp_path / "extra"
    (project / "promplets").mkdir(parents=True)
    (user_home / "promplets").mkdir(parents=True)
    extra.mkdir()
    monkeypatch.setattr("weavemark.promplet_library.GLOBAL_DIR", user_home)

    with library_sources(cwd=project, extra_library_dirs=[extra]) as sources:
        assert [source.kind for source in sources] == [
            "project",
            "user",
            "extra",
            "builtin",
        ]


def test_project_promplet_precedes_user_extra_and_builtin(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = tmp_path / "project"
    user_home = tmp_path / "home"
    extra = tmp_path / "extra"
    relative = Path("catalog/standalone/investment-brief.weavemark.md")
    _write_promplet(project / "promplets" / relative, "Project Investment Brief")
    _write_promplet(user_home / "promplets" / relative, "User Investment Brief")
    _write_promplet(extra / relative, "Extra Investment Brief")
    monkeypatch.setattr("weavemark.promplet_library.GLOBAL_DIR", user_home)

    with library_sources(cwd=project, extra_library_dirs=[extra]) as sources:
        promplets = collect_library_promplets(sources)
        selected = resolve_library_promplet(
            promplets,
            "catalog/standalone/investment-brief",
        )
        builtin = resolve_library_promplet(
            promplets,
            "builtin:catalog/standalone/investment-brief",
        )

    assert selected.source.kind == "project"
    assert selected.entry.title == "Project Investment Brief"
    assert builtin.source.kind == "builtin"


def test_module_reference_resolves_across_extra_root(tmp_path: Path) -> None:
    extra = tmp_path / "team"
    module = extra / "fragments" / "policy.weavemark.md"
    _write_promplet(module, "Team Policy", module_name="acme.support.policy")

    with library_sources(cwd=tmp_path, extra_library_dirs=[extra]) as sources:
        promplets = collect_library_promplets(sources)
        selected = resolve_library_promplet(
            promplets,
            "module:acme.support.policy",
        )
        source = resolve_module_source(
            "acme.support.policy",
            cwd=tmp_path,
            extra_library_dirs=[extra],
        )

    assert selected.entry.path == module.resolve()
    assert source.path == module.resolve()


def test_reserved_namespace_is_rejected_outside_builtin(tmp_path: Path) -> None:
    project = tmp_path / "project"
    _write_promplet(
        project / "promplets" / "bad.weavemark.md",
        "Bad",
        module_name="weavemark.std.bad",
    )

    with (
        library_sources(cwd=project) as sources,
        pytest.raises(PrompletLibraryLookupError, match="reserved"),
    ):
        collect_library_promplets(sources)


def test_duplicate_module_names_are_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = tmp_path / "project"
    user_home = tmp_path / "home"
    _write_promplet(
        project / "promplets" / "project.weavemark.md",
        "Project",
        module_name="acme.duplicate",
    )
    _write_promplet(
        user_home / "promplets" / "user.weavemark.md",
        "User",
        module_name="acme.duplicate",
    )
    monkeypatch.setattr("weavemark.promplet_library.GLOBAL_DIR", user_home)

    with (
        library_sources(cwd=project) as sources,
        pytest.raises(PrompletLibraryLookupError, match="Duplicate module"),
    ):
        collect_library_promplets(sources)


def test_ambiguous_short_name_lists_explicit_references(tmp_path: Path) -> None:
    extra = tmp_path / "extra"
    _write_promplet(extra / "one" / "duplicate.weavemark.md", "First")
    _write_promplet(extra / "two" / "duplicate.weavemark.md", "Second")

    with library_sources(cwd=tmp_path, extra_library_dirs=[extra]) as sources:
        promplets = collect_library_promplets(sources, source_kind="extra")
        with pytest.raises(PrompletLibraryLookupError) as exc:
            resolve_library_promplet(promplets, "duplicate")

    assert "extra:one/duplicate.weavemark.md" in str(exc.value)
    assert "extra:two/duplicate.weavemark.md" in str(exc.value)


def test_collections_and_kinds_are_derived() -> None:
    with library_sources(cwd=Path.cwd()) as sources:
        std_fragments = collect_library_promplets(
            sources,
            source_kind="builtin",
            collection="stdlib",
            kind="fragment",
        )
        executables = collect_library_promplets(
            sources,
            source_kind="builtin",
            collection="catalog",
            kind="executable",
        )

    assert any(item.entry.module_name for item in std_fragments)
    assert any(item.entry.execution_strategy for item in executables)


def test_curated_reusable_promplets_are_versioned_modules() -> None:
    with library_sources(cwd=Path.cwd()) as sources:
        promplets = collect_library_promplets(
            sources,
            source_kind="builtin",
        )

    curated = [
        item
        for item in promplets
        if item.collection in {"stdlib", "domains"}
    ]
    assert curated
    assert all(item.entry.module_name for item in curated)
    assert all(
        item.entry.raw_text.startswith("@promplet version: 0.7")
        for item in curated
    )


def test_every_builtin_promplet_declares_language_version() -> None:
    with library_sources(cwd=Path.cwd()) as sources:
        promplets = collect_library_promplets(sources, source_kind="builtin")

    assert promplets
    assert all(
        item.entry.raw_text.startswith("@promplet version:")
        for item in promplets
    )


def test_story_example_uses_one_flat_local_promplet_folder() -> None:
    root = (
        Path(__file__).resolve().parents[1]
        / "examples"
        / "saved-artifact-workflows"
        / "childrens-book-bebe-fusquinha"
        / "promplets"
    )

    assert sorted(path.name for path in root.iterdir() if path.is_dir()) == []
    assert {
        path.name for path in root.glob("*.weavemark.md")
    } == {
        "baby-bug-universe.weavemark.md",
        "book-en.weavemark.md",
        "book-pt.weavemark.md",
        "library-of-questions-en.weavemark.md",
        "library-of-questions-pt.weavemark.md",
    }


def test_copy_bundled_promplets_preserves_complete_corpus(tmp_path: Path) -> None:
    destination = tmp_path / "library"
    expected = len(list(iter_bundled_promplets()))

    copied = copy_bundled_promplets(destination)

    assert copied == expected
    assert (
        destination
        / "catalog"
        / "standalone"
        / "investment-brief.weavemark.md"
    ).is_file()


def test_copy_requires_force_for_nonempty_destination(tmp_path: Path) -> None:
    destination = tmp_path / "library"
    destination.mkdir()
    (destination / "keep.txt").write_text("keep", encoding="utf-8")

    with pytest.raises(FileExistsError):
        copy_bundled_promplets(destination)


def test_library_list_json_includes_metadata() -> None:
    parser = create_library_parser()
    args = parser.parse_args(
        [
            "list",
            "base analyst",
            "--source",
            "builtin",
            "--json",
        ]
    )
    stdout = io.StringIO()

    exit_code = run_library_command(args, stdout=stdout)
    data = json.loads(stdout.getvalue())

    assert exit_code == 0
    assert data[0]["collection"] == "stdlib"
    assert data[0]["kind"] == "fragment"
    assert data[0]["module_reference"] == (
        "module:weavemark.std.reasoning.base_analyst"
    )


def test_library_show_prints_exact_extra_source(tmp_path: Path) -> None:
    extra = tmp_path / "extra"
    promplet = extra / "team" / "support.weavemark.md"
    _write_promplet(promplet, "Team Support")
    parser = create_library_parser()
    args = parser.parse_args(
        ["show", "extra:team/support", "--library-dir", str(extra)]
    )
    stdout = io.StringIO()

    exit_code = run_library_command(args, cwd=tmp_path, stdout=stdout)

    assert exit_code == 0
    assert stdout.getvalue() == promplet.read_text(encoding="utf-8")


def test_parse_library_target_returns_processor_arguments() -> None:
    path, remaining = parse_library_target(
        ["tutorial-generator", "--scan"],
        cwd=Path.cwd(),
    )

    assert path.name == "tutorial-generator.weavemark.md"
    assert remaining == ["--scan"]


@pytest.mark.parametrize(
    ("target", "expected"),
    (
        ("deep-summary-prompt", "deep-summary-prompt.weavemark.md"),
        (
            "financial-independence-goal-plan-prompt",
            "financial-independence-goal-plan-prompt.weavemark.md",
        ),
        ("recurring-topic-monitor", "recurring-topic-monitor.weavemark.md"),
    ),
)
def test_builtin_public_targets_have_unambiguous_short_names(
    target: str,
    expected: str,
) -> None:
    path, remaining = parse_library_target([target, "--scan"], cwd=Path.cwd())

    assert path.name == expected
    assert remaining == ["--scan"]


def test_news_board_reuses_workflow_module_family() -> None:
    source = (
        Path("promplets/catalog/standalone/news-intelligence-board.weavemark.md")
        .read_text(encoding="utf-8")
    )
    required_modules = (
        "workflow_board",
        "card",
        "activity_stream",
        "context_attachments",
        "output_surfaces",
        "local_sqlite_storage",
        "dashboard",
        "ai_features",
        "notifications",
        "realtime",
        "rest_api",
    )

    for module in required_modules:
        assert f"weavemark.domains.programming.modules.{module}" in source
    assert "weavemark.domains.work_intelligence.topic_intelligence_monitor" in source


@pytest.mark.asyncio
async def test_direct_target_keeps_all_library_dirs_for_module_resolution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WEAVEMARK_LIBRARY_PATH", "")
    entries = tmp_path / "entries"
    modules = tmp_path / "modules"
    _write_promplet(
        entries / "report.weavemark.md",
        "Report",
    )
    (entries / "report.weavemark.md").write_text(
        "@promplet version: 0.7\n\n"
        "@refine module:acme.shared.policy mingle: false\n\n"
        "Prepare the report.\n",
        encoding="utf-8",
    )
    _write_promplet(
        modules / "policy.weavemark.md",
        "Shared Policy",
        module_name="acme.shared.policy",
    )

    path, remaining = parse_library_target(
        [
            "report",
            "--library-dir",
            str(entries),
            "--library-dir",
            str(modules),
            "--batch-only",
        ],
        cwd=tmp_path,
    )
    result = await WeaveMarkController(WeaveMarkConfig()).compose(
        path.read_text(encoding="utf-8"),
        {"name": "team"},
        path.parent,
    )

    assert remaining == [
        "--library-dir",
        str(entries),
        "--library-dir",
        str(modules),
        "--batch-only",
    ]
    assert result.errors == []
    assert "Shared Policy" in result.composed_prompt
    assert "Prepare the report." in result.composed_prompt
