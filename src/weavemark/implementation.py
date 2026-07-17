"""Headless implementation runner for compiled WeaveMark software specs."""

from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from weavemark.protection import ProtectionContext

DEFAULT_IMPLEMENTATION_CONFIG: dict[str, Any] = {
    "default_profile": "copilot",
    "output_root": "outputs/implementations",
    "default_name": "{source_stem}",
    "collision": "timestamp",
    "fresh_directory": True,
    "paths": {
        "implementation_dir": "{output_root}/{implementation_name}",
        "compiled_spec_snapshot": "{implementation_name}.compiled-spec.md",
        "agent_prompt": "{implementation_name}.implementation-prompt.md",
        "transcript": "{implementation_name}.{profile}.transcript.log",
        "manifest": "{implementation_name}.implementation.json",
    },
    "workspace_aliases": {
        "compiled_spec": "compiled-spec.md",
        "agent_prompt": "implementation-prompt.md",
    },
    "prompt": {
        "template": "builtin:compiled-software-spec-implementation",
    },
    "profiles": {
        "copilot": {
            "type": "process",
            "command": "copilot",
            "cwd": "{implementation_dir}",
            "args": [
                "-C",
                "{implementation_dir}",
                "--add-dir",
                "{implementation_dir}",
                "--no-color",
                "--no-ask-user",
                "--autopilot",
                "--max-autopilot-continues",
                "{max_continues}",
                "--allow-all-tools",
                "--name",
                "{session_name}",
                "--prompt",
                "{prompt_text}",
            ],
            "defaults": {
                "max_continues": "8",
                "session_name": "weavemark-implementation",
            },
        },
    },
}

_IMPLEMENTATION_CONFIG_KEYS = {
    "default_profile",
    "output_root",
    "default_name",
    "collision",
    "fresh_directory",
    "paths",
    "workspace_aliases",
    "prompt",
    "profiles",
}
_PATH_TEMPLATE_KEYS = {
    "implementation_dir",
    "compiled_spec_snapshot",
    "agent_prompt",
    "transcript",
    "manifest",
}
_ALIAS_KEYS = {"compiled_spec", "agent_prompt"}
_PROFILE_KEYS = {"type", "command", "cwd", "args", "env", "defaults"}
_PROMPT_KEYS = {"template"}
_PLACEHOLDER_NAMES = {
    "source_path",
    "source_stem",
    "implementation_name",
    "output_root",
    "implementation_dir",
    "compiled_spec_snapshot",
    "agent_prompt",
    "transcript",
    "manifest",
    "profile",
    "prompt_text",
    "prompt_file",
    "model",
    "session_name",
    "max_continues",
}
_PROTECTED_RELATIVE_ROOTS = ("examples", "specs", "src", "studies")


@dataclass(frozen=True)
class ImplementationProfile:
    """A configured headless implementation tool profile."""

    name: str
    type: str
    command: str
    args: tuple[str, ...]
    cwd: str = "{implementation_dir}"
    env: dict[str, str] = field(default_factory=dict)
    defaults: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ImplementationSettings:
    """Resolved implementation settings from built-ins and weavemark.json."""

    default_profile: str
    output_root: str
    default_name: str
    collision: str
    fresh_directory: bool
    paths: dict[str, str]
    workspace_aliases: dict[str, str]
    prompt_template: str
    profiles: dict[str, ImplementationProfile]


@dataclass(frozen=True)
class ImplementationRequest:
    """Inputs for one implementation run."""

    compiled_spec_text: str
    source_path: Path | None
    settings: ImplementationSettings
    invocation_dir: Path
    profile_name: str | None = None
    implementation_name: str | None = None
    output_root: Path | None = None
    dry_run: bool = False
    reuse_dir: bool = False
    model: str | None = None
    extra_instructions: tuple[str, ...] = ()
    protection: ProtectionContext | None = field(
        default=None,
        repr=False,
        compare=False,
    )


@dataclass(frozen=True)
class ImplementationResult:
    """Resolved paths and process result for an implementation run."""

    profile: str
    implementation_name: str
    implementation_dir: Path
    compiled_spec_snapshot: Path
    agent_prompt: Path
    transcript: Path
    manifest: Path
    command: tuple[str, ...]
    dry_run: bool
    exit_code: int | None = None


def builtin_implementation_settings() -> ImplementationSettings:
    """Return WeaveMark's built-in implementation settings."""

    errors: list[str] = []
    settings = implementation_settings_from_config(
        copy.deepcopy(DEFAULT_IMPLEMENTATION_CONFIG),
        source="built-in implementation settings",
        errors=errors,
    )
    if errors:
        raise RuntimeError("; ".join(errors))
    return settings


def merge_implementation_config(
    base: dict[str, Any],
    override: object,
    *,
    source: str,
    errors: list[str],
) -> dict[str, Any]:
    """Merge a raw ``implementation`` settings object into *base*."""

    if override in ({}, None):
        return base
    if not isinstance(override, dict):
        errors.append(f"{source} implementation must be a JSON object.")
        return base

    merged = copy.deepcopy(base)
    for key, value in override.items():
        if key not in _IMPLEMENTATION_CONFIG_KEYS:
            errors.append(f"{source} implementation has unknown key: {key!r}.")
            continue
        if key in {"paths", "workspace_aliases", "prompt"}:
            _merge_named_object(merged, key, value, source, errors)
        elif key == "profiles":
            _merge_profiles(merged, value, source, errors)
        else:
            merged[key] = value
    return merged


def implementation_settings_from_config(
    config: dict[str, Any],
    *,
    source: str,
    errors: list[str],
) -> ImplementationSettings:
    """Build validated implementation settings from a merged config mapping."""

    default_profile = _string_value(config, "default_profile", source, errors)
    output_root = _string_value(config, "output_root", source, errors)
    default_name = _string_value(config, "default_name", source, errors)
    collision = _string_value(config, "collision", source, errors)
    if collision not in {"error", "timestamp"}:
        errors.append(f"{source} implementation.collision must be 'error' or 'timestamp'.")
    fresh_directory = config.get("fresh_directory")
    if not isinstance(fresh_directory, bool):
        errors.append(f"{source} implementation.fresh_directory must be a boolean.")
        fresh_directory = True

    paths = _string_mapping(
        config,
        "paths",
        required=_PATH_TEMPLATE_KEYS,
        allowed=_PATH_TEMPLATE_KEYS,
        source=source,
        errors=errors,
    )
    workspace_aliases = _string_mapping(
        config,
        "workspace_aliases",
        required=set(),
        allowed=_ALIAS_KEYS,
        source=source,
        errors=errors,
    )

    raw_prompt = config.get("prompt", {})
    if not isinstance(raw_prompt, dict):
        errors.append(f"{source} implementation.prompt must be a JSON object.")
        raw_prompt = {}
    for key in raw_prompt:
        if key not in _PROMPT_KEYS:
            errors.append(f"{source} implementation.prompt has unknown key: {key!r}.")
    prompt_template = raw_prompt.get("template", "")
    if not isinstance(prompt_template, str) or not prompt_template.strip():
        errors.append(f"{source} implementation.prompt.template must be a string.")
        prompt_template = "builtin:compiled-software-spec-implementation"

    profiles = _parse_profiles(config.get("profiles"), source, errors)
    if default_profile not in profiles:
        errors.append(
            f"{source} implementation.default_profile {default_profile!r} "
            "does not name a configured profile."
        )

    return ImplementationSettings(
        default_profile=default_profile,
        output_root=output_root,
        default_name=default_name,
        collision=collision,
        fresh_directory=fresh_directory,
        paths=paths,
        workspace_aliases=workspace_aliases,
        prompt_template=prompt_template,
        profiles=profiles,
    )


def run_implementation(request: ImplementationRequest) -> ImplementationResult:
    """Prepare an implementation workspace and optionally run its agent profile."""

    resolved = _resolve_request(request)
    if request.protection is not None:
        _authorize_implementation_paths(request.protection, resolved)
    _prepare_workspace(request, resolved)

    if request.dry_run:
        return resolved

    command_path = shutil.which(resolved.command[0])
    if command_path is None:
        raise ImplementationError(f"Implementation command not found: {resolved.command[0]}")
    if request.protection is not None:
        request.protection.authorize_process(
            Path(command_path),
            reason=f"Running implementation profile {resolved.profile!r}",
        )

    profile = request.settings.profiles[resolved.profile]
    values = _base_template_values(request, resolved.profile, resolved.implementation_name)
    values.update(_path_template_values(resolved))
    env = (
        request.protection.sanitized_subprocess_environment()
        if request.protection is not None
        else os.environ.copy()
    )
    for key, value in profile.env.items():
        env[key] = _expand_template(value, values)

    completed = subprocess.run(
        resolved.command,
        cwd=resolved.implementation_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    resolved.transcript.write_text(completed.stdout, encoding="utf-8")
    if completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
    return ImplementationResult(
        profile=resolved.profile,
        implementation_name=resolved.implementation_name,
        implementation_dir=resolved.implementation_dir,
        compiled_spec_snapshot=resolved.compiled_spec_snapshot,
        agent_prompt=resolved.agent_prompt,
        transcript=resolved.transcript,
        manifest=resolved.manifest,
        command=resolved.command,
        dry_run=False,
        exit_code=completed.returncode,
    )


def _authorize_implementation_paths(
    protection: ProtectionContext,
    resolved: ImplementationResult,
) -> None:
    for path, reason in (
        (resolved.implementation_dir, "Creating the implementation workspace"),
        (resolved.compiled_spec_snapshot, "Writing the compiled spec snapshot"),
        (resolved.agent_prompt, "Writing the implementation-agent prompt"),
        (resolved.transcript, "Writing the implementation transcript"),
        (resolved.manifest, "Writing the implementation manifest"),
    ):
        protection.authorize_write(path, reason=reason)


class ImplementationError(ValueError):
    """Raised when implementation configuration or execution is invalid."""


def _merge_named_object(
    merged: dict[str, Any],
    key: str,
    value: object,
    source: str,
    errors: list[str],
) -> None:
    if value in ({}, None):
        return
    if not isinstance(value, dict):
        errors.append(f"{source} implementation.{key} must be a JSON object.")
        return
    current = merged.setdefault(key, {})
    if not isinstance(current, dict):
        current = {}
        merged[key] = current
    current.update(value)


def _merge_profiles(
    merged: dict[str, Any],
    value: object,
    source: str,
    errors: list[str],
) -> None:
    if value in ({}, None):
        return
    if not isinstance(value, dict):
        errors.append(f"{source} implementation.profiles must be a JSON object.")
        return
    current = merged.setdefault("profiles", {})
    if not isinstance(current, dict):
        current = {}
        merged["profiles"] = current
    for profile_name, profile_value in value.items():
        if not isinstance(profile_name, str) or not profile_name.strip():
            errors.append(f"{source} implementation profile names must be strings.")
            continue
        if not isinstance(profile_value, dict):
            errors.append(
                f"{source} implementation profile {profile_name!r} must be an object."
            )
            continue
        existing = current.get(profile_name, {})
        if isinstance(existing, dict):
            merged_profile = copy.deepcopy(existing)
            merged_profile.update(profile_value)
            current[profile_name] = merged_profile
        else:
            current[profile_name] = profile_value


def _string_value(
    config: dict[str, Any],
    key: str,
    source: str,
    errors: list[str],
) -> str:
    value = config.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{source} implementation.{key} must be a non-empty string.")
        return ""
    return value.strip()


def _string_mapping(
    config: dict[str, Any],
    key: str,
    *,
    required: set[str],
    allowed: set[str],
    source: str,
    errors: list[str],
) -> dict[str, str]:
    value = config.get(key, {})
    if not isinstance(value, dict):
        errors.append(f"{source} implementation.{key} must be a JSON object.")
        return {}
    parsed: dict[str, str] = {}
    for raw_name, raw_template in value.items():
        if raw_name not in allowed:
            errors.append(f"{source} implementation.{key} has unknown key: {raw_name!r}.")
            continue
        if not isinstance(raw_template, str) or not raw_template.strip():
            errors.append(
                f"{source} implementation.{key}.{raw_name} must be a non-empty string."
            )
            continue
        parsed[raw_name] = raw_template
    missing = required - set(parsed)
    if missing:
        errors.append(
            f"{source} implementation.{key} is missing: {', '.join(sorted(missing))}."
        )
    return parsed


def _parse_profiles(
    raw_profiles: object,
    source: str,
    errors: list[str],
) -> dict[str, ImplementationProfile]:
    if not isinstance(raw_profiles, dict) or not raw_profiles:
        errors.append(f"{source} implementation.profiles must be a non-empty object.")
        return {}

    profiles: dict[str, ImplementationProfile] = {}
    for raw_name, raw_profile in raw_profiles.items():
        if not isinstance(raw_name, str) or not raw_name.strip():
            errors.append(f"{source} implementation profile names must be strings.")
            continue
        name = raw_name.strip()
        if not isinstance(raw_profile, dict):
            errors.append(f"{source} implementation profile {name!r} must be an object.")
            continue
        for key in raw_profile:
            if key not in _PROFILE_KEYS:
                errors.append(
                    f"{source} implementation profile {name!r} has unknown key: {key!r}."
                )
        profile_type = raw_profile.get("type")
        if profile_type != "process":
            errors.append(
                f"{source} implementation profile {name!r} type must be 'process'."
            )
            continue
        command = raw_profile.get("command")
        if not isinstance(command, str) or not command.strip():
            errors.append(
                f"{source} implementation profile {name!r} requires command."
            )
            continue
        raw_args = raw_profile.get("args", [])
        if not isinstance(raw_args, list) or not all(
            isinstance(item, str) for item in raw_args
        ):
            errors.append(
                f"{source} implementation profile {name!r} args must be strings."
            )
            continue
        cwd = raw_profile.get("cwd", "{implementation_dir}")
        if not isinstance(cwd, str) or not cwd.strip():
            errors.append(f"{source} implementation profile {name!r} cwd is invalid.")
            continue
        env = _profile_string_dict(raw_profile.get("env", {}), source, name, "env", errors)
        defaults = _profile_string_dict(
            raw_profile.get("defaults", {}),
            source,
            name,
            "defaults",
            errors,
        )
        profiles[name] = ImplementationProfile(
            name=name,
            type=profile_type,
            command=command.strip(),
            args=tuple(raw_args),
            cwd=cwd,
            env=env,
            defaults=defaults,
        )
    return profiles


def _profile_string_dict(
    value: object,
    source: str,
    profile_name: str,
    key: str,
    errors: list[str],
) -> dict[str, str]:
    if value in ({}, None):
        return {}
    if not isinstance(value, dict):
        errors.append(
            f"{source} implementation profile {profile_name!r} {key} must be an object."
        )
        return {}
    parsed: dict[str, str] = {}
    for raw_key, raw_value in value.items():
        if not isinstance(raw_key, str) or not isinstance(raw_value, (str, int, float)):
            errors.append(
                f"{source} implementation profile {profile_name!r} {key} "
                "must map strings to scalar values."
            )
            continue
        parsed[raw_key] = str(raw_value)
    return parsed


def _resolve_request(request: ImplementationRequest) -> ImplementationResult:
    profile_name = request.profile_name or request.settings.default_profile
    if profile_name not in request.settings.profiles:
        raise ImplementationError(f"Unknown implementation profile: {profile_name}")
    profile = request.settings.profiles[profile_name]

    source_stem = _source_stem(request.source_path)
    base_values = _base_template_values(request, profile_name, source_stem)
    raw_name = request.implementation_name or _expand_template(
        request.settings.default_name,
        base_values,
    )
    implementation_name = _validate_implementation_name(raw_name)
    values = _base_template_values(request, profile_name, implementation_name)

    implementation_dir = _resolve_path_template(
        request.settings.paths["implementation_dir"],
        values,
        request.invocation_dir,
    )
    implementation_dir = _resolve_collision(request, implementation_dir)
    _check_implementation_dir(request.invocation_dir, implementation_dir)
    path_values = {
        **values,
        "implementation_dir": str(implementation_dir),
    }

    compiled_spec_snapshot = _resolve_workspace_path(
        request.settings.paths["compiled_spec_snapshot"],
        path_values,
        implementation_dir,
    )
    agent_prompt = _resolve_workspace_path(
        request.settings.paths["agent_prompt"],
        path_values,
        implementation_dir,
    )
    path_values.update(
        {
            "compiled_spec_snapshot": str(compiled_spec_snapshot),
            "agent_prompt": str(agent_prompt),
            "prompt_file": str(agent_prompt),
        }
    )
    transcript = _resolve_workspace_path(
        request.settings.paths["transcript"],
        path_values,
        implementation_dir,
    )
    manifest = _resolve_workspace_path(
        request.settings.paths["manifest"],
        {**path_values, "transcript": str(transcript)},
        implementation_dir,
    )

    prompt_text = _render_prompt(request, compiled_spec_snapshot)
    command_values = {
        **path_values,
        "transcript": str(transcript),
        "manifest": str(manifest),
        "prompt_text": prompt_text,
    }
    command_values.update(profile.defaults)
    if request.model:
        command_values["model"] = request.model

    command = tuple(
        [_expand_template(profile.command, command_values)]
        + [_expand_template(arg, command_values) for arg in profile.args]
    )
    cwd = _resolve_path_template(profile.cwd, command_values, implementation_dir)
    try:
        cwd.relative_to(implementation_dir)
    except ValueError as exc:
        raise ImplementationError(
            f"Implementation profile {profile.name!r} cwd escapes implementation dir: {cwd}"
        ) from exc

    return ImplementationResult(
        profile=profile_name,
        implementation_name=implementation_name,
        implementation_dir=implementation_dir,
        compiled_spec_snapshot=compiled_spec_snapshot,
        agent_prompt=agent_prompt,
        transcript=transcript,
        manifest=manifest,
        command=command,
        dry_run=request.dry_run,
    )


def _prepare_workspace(
    request: ImplementationRequest,
    result: ImplementationResult,
) -> None:
    result.implementation_dir.mkdir(parents=True, exist_ok=True)
    result.compiled_spec_snapshot.write_text(
        request.compiled_spec_text,
        encoding="utf-8",
    )
    prompt_text = _render_prompt(request, result.compiled_spec_snapshot)
    result.agent_prompt.write_text(prompt_text, encoding="utf-8")

    aliases = request.settings.workspace_aliases
    compiled_alias = aliases.get("compiled_spec")
    if compiled_alias:
        alias_path = _resolve_workspace_path(
            compiled_alias,
            {"implementation_name": result.implementation_name},
            result.implementation_dir,
        )
        if alias_path != result.compiled_spec_snapshot:
            alias_path.write_text(request.compiled_spec_text, encoding="utf-8")
    prompt_alias = aliases.get("agent_prompt")
    if prompt_alias:
        alias_path = _resolve_workspace_path(
            prompt_alias,
            {"implementation_name": result.implementation_name},
            result.implementation_dir,
        )
        if alias_path != result.agent_prompt:
            alias_path.write_text(prompt_text, encoding="utf-8")

    manifest = {
        "source": str(request.source_path) if request.source_path else None,
        "implementation_name": result.implementation_name,
        "profile": result.profile,
        "command": list(result.command),
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "dry_run": request.dry_run,
        "artifacts": {
            "compiled_spec_snapshot": str(result.compiled_spec_snapshot),
            "agent_prompt": str(result.agent_prompt),
            "transcript": str(result.transcript),
            "manifest": str(result.manifest),
        },
    }
    result.manifest.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _base_template_values(
    request: ImplementationRequest,
    profile: str,
    implementation_name: str,
) -> dict[str, str]:
    output_root = request.output_root or Path(request.settings.output_root)
    if not output_root.is_absolute():
        output_root = request.invocation_dir / output_root
    source_path = request.source_path
    source_stem = _source_stem(source_path)
    return {
        "source_path": str(source_path) if source_path else "",
        "source_stem": source_stem,
        "implementation_name": implementation_name,
        "output_root": str(output_root.resolve()),
        "profile": profile,
        "model": request.model or "",
    }


def _path_template_values(result: ImplementationResult) -> dict[str, str]:
    return {
        "implementation_dir": str(result.implementation_dir),
        "compiled_spec_snapshot": str(result.compiled_spec_snapshot),
        "agent_prompt": str(result.agent_prompt),
        "transcript": str(result.transcript),
        "manifest": str(result.manifest),
        "prompt_file": str(result.agent_prompt),
    }


def _source_stem(source_path: Path | None) -> str:
    if source_path is None:
        return "implementation"
    name = source_path.name
    if name.endswith(".weavemark.md"):
        return name[: -len(".weavemark.md")]
    return source_path.stem or "implementation"


def _validate_implementation_name(value: str) -> str:
    name = value.strip()
    if not name:
        raise ImplementationError("Implementation name must not be empty.")
    if name in {".", ".."} or "/" in name or "\\" in name:
        raise ImplementationError(
            f"Implementation name must be a single path segment: {value!r}"
        )
    return name


def _resolve_path_template(template: str, values: dict[str, str], base: Path) -> Path:
    expanded = Path(_expand_template(template, values)).expanduser()
    if not expanded.is_absolute():
        expanded = base / expanded
    return expanded.resolve()


def _resolve_workspace_path(
    template: str,
    values: dict[str, str],
    implementation_dir: Path,
) -> Path:
    path = _resolve_path_template(template, values, implementation_dir)
    try:
        path.relative_to(implementation_dir)
    except ValueError as exc:
        raise ImplementationError(
            f"Implementation artifact path escapes implementation directory: {path}"
        ) from exc
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _resolve_collision(
    request: ImplementationRequest,
    implementation_dir: Path,
) -> Path:
    if request.reuse_dir:
        return implementation_dir
    if not implementation_dir.exists() or not any(implementation_dir.iterdir()):
        return implementation_dir
    if request.settings.collision == "error":
        raise ImplementationError(
            f"Implementation directory is not empty: {implementation_dir}"
        )
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    candidate = implementation_dir.with_name(f"{implementation_dir.name}-{timestamp}")
    index = 2
    while candidate.exists() and any(candidate.iterdir()):
        candidate = implementation_dir.with_name(
            f"{implementation_dir.name}-{timestamp}-{index}"
        )
        index += 1
    return candidate


def _check_implementation_dir(invocation_dir: Path, implementation_dir: Path) -> None:
    root = invocation_dir.resolve()
    try:
        relative = implementation_dir.resolve().relative_to(root)
    except ValueError:
        return
    if relative.parts and relative.parts[0] in _PROTECTED_RELATIVE_ROOTS:
        raise ImplementationError(
            "Implementation directory cannot be inside "
            f"{relative.parts[0]}/; choose outputs/implementations or pass --output-root."
        )


def _render_prompt(
    request: ImplementationRequest,
    compiled_spec_snapshot: Path,
) -> str:
    if request.settings.prompt_template != "builtin:compiled-software-spec-implementation":
        raise ImplementationError(
            "Only builtin:compiled-software-spec-implementation prompt templates "
            "are supported in this release."
        )
    compiled_alias = request.settings.workspace_aliases.get("compiled_spec")
    spec_reference = f"./{compiled_alias}" if compiled_alias else str(compiled_spec_snapshot)
    parts = [
        "You are implementing a compiled WeaveMark software specification.",
        "",
        f"Read {spec_reference} and build the smallest complete, runnable "
        "implementation that satisfies it in the current directory.",
        "",
        "Operating constraints:",
        "- Work only inside the current directory.",
        "- Do not edit the source WeaveMark repository or the original study/example files.",
        "- Prefer a simple, inspectable project structure over framework ceremony unless",
        "  the spec explicitly requires a framework.",
        "- If the spec names a platform or stack, use it. If it does not, choose the",
        "  simplest local stack that can satisfy the behavior.",
        "- Add concise run and verification instructions in README.md.",
        "- Run the relevant available build, test, lint, or smoke checks before finishing.",
        "- If a requirement cannot be implemented in this pass, document the gap clearly",
        "  in README.md instead of pretending it is complete.",
    ]
    if request.extra_instructions:
        parts.extend(["", "Additional user instructions:"])
        parts.extend(f"- {instruction}" for instruction in request.extra_instructions)
    return "\n".join(parts) + "\n"


def _expand_template(template: str, values: dict[str, str]) -> str:
    output: list[str] = []
    index = 0
    while index < len(template):
        char = template[index]
        if char == "{":
            end = template.find("}", index + 1)
            if end == -1:
                raise ImplementationError(f"Unclosed placeholder in template: {template}")
            name = template[index + 1 : end]
            if name not in _PLACEHOLDER_NAMES:
                raise ImplementationError(f"Unsupported implementation placeholder: {name}")
            if name not in values:
                raise ImplementationError(f"No value for implementation placeholder: {name}")
            output.append(values[name])
            index = end + 1
        elif char == "}":
            raise ImplementationError(f"Unmatched '}}' in template: {template}")
        else:
            output.append(char)
            index += 1
    return "".join(output)


def print_dry_run(result: ImplementationResult) -> None:
    """Print a shell-escaped dry-run command for humans."""

    print(f"Implementation workspace: {result.implementation_dir}")
    print(f"Compiled spec snapshot: {result.compiled_spec_snapshot}")
    print(f"Implementation prompt: {result.agent_prompt}")
    print(f"Transcript: {result.transcript}")
    print(f"Manifest: {result.manifest}")
    print("Command:", " ".join(shlex_quote(part) for part in result.command))


def shlex_quote(value: str) -> str:
    """Small wrapper to keep imports narrow in the CLI-facing output helper."""

    import shlex

    return shlex.quote(value)
