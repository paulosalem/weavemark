"""Experimental protection-policy tests."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from weavemark.protection import (
    ProtectionContext,
    ProtectionError,
    ProtectionSettings,
    _has_image_magic,
    protection_settings_from_config,
    tighten_protection_settings,
)
from weavemark.settings import load_weavemark_settings


def _context(
    tmp_path: Path,
    *,
    settings: ProtectionSettings | None = None,
    handler=None,
) -> ProtectionContext:
    entrypoint = tmp_path / "entrypoint"
    invocation = tmp_path / "invocation"
    entrypoint.mkdir(exist_ok=True)
    invocation.mkdir(exist_ok=True)
    return ProtectionContext.create(
        settings or ProtectionSettings(),
        entrypoint_dir=entrypoint,
        invocation_dir=invocation,
        approval_handler=handler,
        approvals_path=tmp_path / "approvals.json",
    )


def test_default_roots_include_entrypoint_cwd_and_outputs(tmp_path: Path) -> None:
    context = _context(tmp_path)

    assert (tmp_path / "entrypoint").resolve() in context.read_roots
    assert (tmp_path / "invocation").resolve() in context.read_roots
    assert (tmp_path / "entrypoint").resolve() in context.write_roots
    assert (tmp_path / "invocation").resolve() in context.write_roots
    assert (tmp_path / "invocation" / "outputs").resolve() in context.write_roots


def test_local_reads_are_canonical_and_symlink_escapes_require_approval(
    tmp_path: Path,
) -> None:
    approvals: list[str] = []
    context = _context(
        tmp_path,
        handler=lambda request: approvals.append(request.subject) or True,
    )
    inside = tmp_path / "entrypoint" / "inside.txt"
    inside.write_text("inside", encoding="utf-8")
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    link = tmp_path / "entrypoint" / "link.txt"
    link.symlink_to(outside)

    assert context.authorize_read(inside, reason="test") == inside.resolve()
    assert context.authorize_read(link, reason="test") == outside.resolve()
    assert approvals == [str(outside.resolve())]


def test_sensitive_files_are_denied_even_inside_roots(tmp_path: Path) -> None:
    context = _context(tmp_path)
    secret = tmp_path / "entrypoint" / ".env"
    secret.write_text("TOKEN=secret", encoding="utf-8")

    with pytest.raises(ProtectionError, match="sensitive local-file read"):
        context.authorize_read(secret, reason="test")


def test_undeclared_model_read_requires_confirmation_inside_project(
    tmp_path: Path,
) -> None:
    context = _context(tmp_path)
    source = tmp_path / "entrypoint" / "unrelated.txt"
    source.write_text("private project context", encoding="utf-8")

    with pytest.raises(ProtectionError, match="model-directed local-file read"):
        context.authorize_read(source, reason="model tool", declared=False)


def test_write_roots_allow_normal_outputs_and_confirm_outside(
    tmp_path: Path,
) -> None:
    context = _context(tmp_path, handler=lambda _request: True)
    output = tmp_path / "invocation" / "outputs" / "result.md"
    outside = tmp_path / "elsewhere" / "result.md"

    assert context.authorize_write(output, reason="test") == output
    assert context.authorize_write(outside, reason="test") == outside


def test_write_symlink_cannot_escape_an_allowed_root(tmp_path: Path) -> None:
    context = _context(tmp_path)
    outside = tmp_path / "elsewhere" / "result.md"
    outside.parent.mkdir()
    outside.write_text("keep", encoding="utf-8")
    link = tmp_path / "entrypoint" / "result.md"
    link.symlink_to(outside)

    with pytest.raises(ProtectionError, match="write outside configured roots"):
        context.authorize_write(link, reason="test")


def test_python_approval_is_remembered_and_invalidated_by_content(
    tmp_path: Path,
) -> None:
    decisions: list[str] = []
    context = _context(
        tmp_path,
        handler=lambda request: decisions.append(request.fingerprint) or True,
    )
    script = tmp_path / "entrypoint" / "machine.py"
    script.write_text("VALUE = 1\n", encoding="utf-8")

    context.authorize_python("machine", path=script, reason="test")
    context.authorize_python("machine", path=script, reason="test")
    assert len(decisions) == 1

    script.write_text("VALUE = 2\n", encoding="utf-8")
    context.authorize_python("machine", path=script, reason="test")
    assert len(decisions) == 2
    approval_data = json.loads(
        (tmp_path / "approvals.json").read_text(encoding="utf-8")
    )
    assert list(approval_data["approvals"].values())[0]["allowed"] is True
    if os.name != "nt":
        assert (tmp_path / "approvals.json").stat().st_mode & 0o777 == 0o600


def test_confirmation_without_interactive_handler_is_blocked(
    tmp_path: Path,
) -> None:
    context = _context(tmp_path)
    script = tmp_path / "entrypoint" / "machine.py"
    script.write_text("VALUE = 1\n", encoding="utf-8")

    with pytest.raises(ProtectionError, match="requires interactive confirmation"):
        context.authorize_python("machine", path=script, reason="test")


def test_bypass_disables_all_enforcement(tmp_path: Path) -> None:
    context = ProtectionContext.create(
        ProtectionSettings(),
        entrypoint_dir=tmp_path,
        bypass=True,
    )
    secret = tmp_path / ".env"

    assert context.authorize_read(secret, reason="test") == secret.resolve()
    context.authorize_python("anything", reason="test")


def test_remote_policy_blocks_http_and_private_networks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = _context(tmp_path)
    monkeypatch.setattr(
        "weavemark.protection._resolve_host_addresses",
        lambda _host, _port, _scheme: {"127.0.0.1"},
    )

    with pytest.raises(ProtectionError, match="active policy denies"):
        context.authorize_remote_url("http://example.com/image.png", reason="test")
    with pytest.raises(ProtectionError, match="private-network"):
        context.authorize_remote_url("https://example.com/image.png", reason="test")
    with pytest.raises(ProtectionError, match="invalid port"):
        context.authorize_remote_url(
            "https://example.com:invalid/image.png", reason="test"
        )


def test_remote_image_magic_validation() -> None:
    assert _has_image_magic(b"\x89PNG\r\n\x1a\npayload") is True
    assert _has_image_magic(b"RIFFxxxxWEBPpayload") is True
    assert _has_image_magic(b"<script>alert(1)</script>") is False


def test_empty_subprocess_source_does_not_fall_back_to_process_environment(
    tmp_path: Path,
) -> None:
    context = _context(tmp_path)

    assert context.sanitized_subprocess_environment({}) == {}


def test_config_parsing_and_project_tightening_are_monotonic() -> None:
    errors: list[str] = []
    settings = protection_settings_from_config(
        {
            "enabled": False,
            "readRoots": ["/shared"],
            "pythonCode": "allow",
            "maxDownloadBytes": 1000,
        },
        source="user",
        errors=errors,
    )
    warnings: list[str] = []
    tightened = tighten_protection_settings(
        ProtectionSettings(
            enabled=True,
            read_roots=settings.read_roots,
            python_code="confirm",
            max_download_bytes=2000,
        ),
        {
            "enabled": False,
            "readRoots": ["/malicious"],
            "pythonCode": "deny",
            "maxDownloadBytes": 500,
        },
        source="project",
        warnings=warnings,
        errors=errors,
    )

    assert errors == []
    assert tightened.enabled is True
    assert tightened.read_roots == ("/shared",)
    assert tightened.python_code == "deny"
    assert tightened.max_download_bytes == 500
    assert len(warnings) == 2


def test_settings_load_user_policy_and_prevent_project_weakening(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_config = tmp_path / "user.json"
    user_config.write_text(
        json.dumps(
            {
                "protections": {
                    "enabled": True,
                    "readRoots": [str(tmp_path / "shared")],
                    "pythonCode": "confirm",
                }
            }
        ),
        encoding="utf-8",
    )
    project = tmp_path / "project"
    project.mkdir()
    (project / "weavemark.json").write_text(
        json.dumps(
            {
                "protections": {
                    "enabled": False,
                    "readRoots": ["/untrusted-grant"],
                    "pythonCode": "allow",
                    "remoteHttps": "deny",
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
    assert result.settings.protections.enabled is True
    assert result.settings.protections.read_roots == (str(tmp_path / "shared"),)
    assert result.settings.protections.python_code == "confirm"
    assert result.settings.protections.remote_https == "deny"
    assert len(result.warnings) == 2
