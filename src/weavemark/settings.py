"""JSON-backed WeaveMark settings discovery."""

from __future__ import annotations

import copy
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from weavemark.implementation import (
    DEFAULT_IMPLEMENTATION_CONFIG,
    ImplementationSettings,
    implementation_settings_from_config,
    merge_implementation_config,
)
from weavemark.logging_policy import (
    LoggingSettings,
    logging_settings_from_config,
    tighten_logging_settings,
)
from weavemark.protection import (
    ProtectionSettings,
    protection_settings_from_config,
    tighten_protection_settings,
)

WEAVEMARK_CONFIG_NAME = "weavemark.json"


@dataclass(frozen=True)
class FormatDefinition:
    """A configured WeaveMark format and its file-extension mapping."""

    name: str
    extension: str
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class DefaultModuleImport:
    """A module whose exported definitions are available without ``@use``."""

    name: str
    alias: str | None = None
    exposing: tuple[str, ...] | None = None


@dataclass(frozen=True)
class WeaveMarkSettings:
    """Resolved WeaveMark settings from built-ins and JSON config files."""

    formats: dict[str, FormatDefinition]
    default_module_imports: tuple[DefaultModuleImport, ...] = ()
    fragment_aliases: dict[str, Path] = field(default_factory=dict)
    implementation: ImplementationSettings = field(
        default_factory=lambda: implementation_settings_from_config(
            copy.deepcopy(DEFAULT_IMPLEMENTATION_CONFIG),
            source="built-in implementation settings",
            errors=[],
        )
    )
    protections: ProtectionSettings = field(default_factory=ProtectionSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    sources: tuple[Path, ...] = ()

    def normalize_format(self, value: object) -> str | None:
        """Return the canonical format name for *value*, if configured."""

        text = _normalize_format_token(value)
        aliases = self._format_aliases()
        return aliases.get(text)

    def format_extension(self, value: object | None) -> str:
        """Return the configured extension for *value* or the default format."""

        normalized = (
            self.normalize_format(value)
            if value is not None
            else self.normalize_format("markdown")
        )
        if normalized is None:
            return str(value or "markdown").strip().lower().removeprefix(".")
        return self.formats[normalized].extension

    def supported_formats_text(self) -> str:
        """Return a human-readable list of configured canonical formats."""

        return ", ".join(sorted(self.formats))

    def _format_aliases(self) -> dict[str, str]:
        aliases: dict[str, str] = {}
        for name, definition in self.formats.items():
            aliases[_normalize_format_token(name)] = name
            aliases[_normalize_format_token(definition.extension)] = name
            aliases[f".{_normalize_format_token(definition.extension)}"] = name
            for alias in definition.aliases:
                aliases[_normalize_format_token(alias)] = name
        return aliases


@dataclass(frozen=True)
class WeaveMarkSettingsResult:
    """Settings plus diagnostics discovered while loading JSON config files."""

    settings: WeaveMarkSettings
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class _RawSettings:
    formats: dict[str, FormatDefinition] = field(default_factory=dict)
    default_module_imports: tuple[DefaultModuleImport, ...] = ()
    fragment_aliases: dict[str, Path] = field(default_factory=dict)
    implementation_config: dict[str, Any] | None = None
    protection_config: dict[str, Any] | None = None
    logging_config: dict[str, Any] | None = None


_BUILTIN_FORMATS: dict[str, FormatDefinition] = {
    "markdown": FormatDefinition("markdown", "md", ("md", ".md")),
    "json": FormatDefinition("json", "json", (".json",)),
    "mustache": FormatDefinition("mustache", "mustache", ()),
    "jinja": FormatDefinition("jinja", "jinja", ("jinja2",)),
}
_FRAGMENT_ALIAS_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")
_MODULE_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$")
_DEFINITION_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
_BUILTIN_DEFAULT_MODULES: tuple[DefaultModuleImport, ...] = (
    DefaultModuleImport("weavemark.prelude.semantics"),
    DefaultModuleImport(
        "weavemark.prelude.presentation",
        exposing=("concise",),
    ),
)


def builtin_weavemark_settings() -> WeaveMarkSettings:
    """Return WeaveMark's built-in settings."""

    return WeaveMarkSettings(
        formats=dict(_BUILTIN_FORMATS),
        default_module_imports=_BUILTIN_DEFAULT_MODULES,
    )


def load_weavemark_settings(base_dir: Path | None = None) -> WeaveMarkSettingsResult:
    """Load built-in, global, user, and project WeaveMark JSON settings."""

    warnings: list[str] = []
    errors: list[str] = []
    formats = dict(_BUILTIN_FORMATS)
    implementation_config = copy.deepcopy(DEFAULT_IMPLEMENTATION_CONFIG)
    protection_config: dict[str, Any] = {}
    logging_config: dict[str, Any] = {}
    sources: list[Path] = []

    global_paths = _configured_paths(
        env_var="WEAVEMARK_GLOBAL_CONFIG",
        default_path=default_global_config_path(),
    )
    user_paths = _configured_paths(
        env_var="WEAVEMARK_USER_CONFIG",
        default_path=default_user_config_path(),
    )
    project_paths = _project_config_paths(base_dir or Path.cwd())

    default_module_imports: list[DefaultModuleImport] = list(_BUILTIN_DEFAULT_MODULES)
    fragment_aliases: dict[str, Path] = {}

    project_settings: dict[Path, _RawSettings] = {}

    for level, config_paths in (
        ("global", global_paths),
        ("user", user_paths),
        ("project", tuple(reversed(project_paths))),
    ):
        for config_path in config_paths:
            raw = _read_settings_file(config_path, errors)
            if raw is None:
                continue
            sources.append(config_path.expanduser().resolve())
            formats.update(raw.formats)
            fragment_aliases.update(raw.fragment_aliases)
            implementation_config = merge_implementation_config(
                implementation_config,
                raw.implementation_config,
                source=str(config_path),
                errors=errors,
            )
            if level != "project" and raw.protection_config is not None:
                protection_config.update(raw.protection_config)
            if level != "project" and raw.logging_config is not None:
                logging_config.update(raw.logging_config)
            if level == "project":
                project_settings[config_path] = raw
                # Preserve nearest-project-first search order even though formats
                # are applied root-to-leaf so nearer config overrides names.
                continue
            default_module_imports.extend(raw.default_module_imports)

    for config_path in reversed(project_paths):
        raw = project_settings.get(config_path)
        if raw is not None:
            default_module_imports.extend(raw.default_module_imports)

    implementation = implementation_settings_from_config(
        implementation_config,
        source="merged implementation settings",
        errors=errors,
    )
    protections = protection_settings_from_config(
        protection_config,
        source="merged user/global settings",
        errors=errors,
    )
    logging_settings = logging_settings_from_config(
        logging_config,
        source="merged user/global settings",
        errors=errors,
    )
    for config_path in reversed(project_paths):
        raw = project_settings.get(config_path)
        if raw is not None:
            protections = tighten_protection_settings(
                protections,
                raw.protection_config,
                source=str(config_path),
                warnings=warnings,
                errors=errors,
            )
            logging_settings = tighten_logging_settings(
                logging_settings,
                raw.logging_config,
                source=str(config_path),
                warnings=warnings,
                errors=errors,
            )

    return WeaveMarkSettingsResult(
        settings=WeaveMarkSettings(
            formats=formats,
            default_module_imports=_dedupe_default_module_imports(
                default_module_imports
            ),
            fragment_aliases=dict(fragment_aliases),
            implementation=implementation,
            protections=protections,
            logging=logging_settings,
            sources=tuple(sources),
        ),
        warnings=tuple(warnings),
        errors=tuple(errors),
    )


def default_user_config_path() -> Path:
    """Return the per-user WeaveMark JSON settings path."""

    if sys.platform == "darwin":
        return (
            Path.home()
            / "Library"
            / "Application Support"
            / "WeaveMark"
            / WEAVEMARK_CONFIG_NAME
        )
    if sys.platform == "win32":
        root = os.environ.get("APPDATA")
        if root:
            return Path(root) / "WeaveMark" / WEAVEMARK_CONFIG_NAME
        return Path.home() / "AppData" / "Roaming" / "WeaveMark" / WEAVEMARK_CONFIG_NAME
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        return Path(config_home) / "weavemark" / WEAVEMARK_CONFIG_NAME
    return Path.home() / ".config" / "weavemark" / WEAVEMARK_CONFIG_NAME


def default_global_config_path() -> Path:
    """Return the system-wide WeaveMark JSON settings path."""

    if sys.platform == "darwin":
        return Path("/Library/Application Support/WeaveMark") / WEAVEMARK_CONFIG_NAME
    if sys.platform == "win32":
        root = os.environ.get("PROGRAMDATA", r"C:\ProgramData")
        return Path(root) / "WeaveMark" / WEAVEMARK_CONFIG_NAME
    return Path("/etc/weavemark") / WEAVEMARK_CONFIG_NAME


def _configured_paths(env_var: str, default_path: Path) -> tuple[Path, ...]:
    override = os.environ.get(env_var)
    if override:
        return tuple(
            Path(item).expanduser() for item in override.split(os.pathsep) if item
        )
    return (default_path,) if default_path.is_file() else ()


def _project_config_paths(base_dir: Path) -> tuple[Path, ...]:
    paths: list[Path] = []
    for directory in _ancestors_from(base_dir):
        config_path = directory / WEAVEMARK_CONFIG_NAME
        if config_path.is_file():
            paths.append(config_path)
    return tuple(paths)


def _read_settings_file(path: Path, errors: list[str]) -> _RawSettings | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        errors.append(f"Could not read {path}: {exc}")
        return None
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {path}: {exc}")
        return None

    if not isinstance(data, dict):
        errors.append(f"{path} must contain a JSON object.")
        return None

    return _parse_settings_object(path, data, errors)


def _parse_settings_object(
    path: Path,
    data: dict[str, Any],
    errors: list[str],
) -> _RawSettings:
    formats = _parse_formats(path, data.get("formats", {}), errors)
    raw_modules = data.get("modules", {})
    default_module_imports = _parse_default_module_imports(
        path,
        raw_modules,
        errors,
    )
    fragment_aliases = _parse_fragment_aliases(
        path,
        data.get("fragments", {}),
        errors,
    )
    raw_implementation = data.get("implementation")
    implementation_config: dict[str, Any] | None = None
    if raw_implementation is not None:
        if isinstance(raw_implementation, dict):
            implementation_config = raw_implementation
        else:
            errors.append(f"{path} implementation must be a JSON object.")
    raw_protections = data.get("protections")
    protection_config: dict[str, Any] | None = None
    if raw_protections is not None:
        if isinstance(raw_protections, dict):
            protection_config = raw_protections
        else:
            errors.append(f"{path} protections must be a JSON object.")
    raw_logging = data.get("log")
    logging_config: dict[str, Any] | None = None
    if raw_logging is not None:
        if isinstance(raw_logging, dict):
            logging_config = raw_logging
        else:
            errors.append(f"{path} log must be a JSON object.")
    return _RawSettings(
        formats=formats,
        default_module_imports=default_module_imports,
        fragment_aliases=fragment_aliases,
        implementation_config=implementation_config,
        protection_config=protection_config,
        logging_config=logging_config,
    )


def _parse_formats(
    path: Path,
    raw_formats: object,
    errors: list[str],
) -> dict[str, FormatDefinition]:
    if raw_formats in ({}, None):
        return {}
    if not isinstance(raw_formats, dict):
        errors.append(f"{path} formats must be a JSON object.")
        return {}

    formats: dict[str, FormatDefinition] = {}
    for raw_name, raw_definition in raw_formats.items():
        if not isinstance(raw_name, str):
            errors.append(f"{path} format names must be strings.")
            continue
        name = _normalize_format_token(raw_name)
        if not _is_format_identifier(name):
            errors.append(f"{path} format name is invalid: {raw_name!r}")
            continue

        extension: str | None = None
        aliases: tuple[str, ...] = ()
        if isinstance(raw_definition, str):
            extension = raw_definition
        elif isinstance(raw_definition, dict):
            raw_extension = raw_definition.get("extension")
            if isinstance(raw_extension, str):
                extension = raw_extension
            raw_aliases = raw_definition.get("aliases", [])
            if isinstance(raw_aliases, str):
                aliases = (raw_aliases,)
            elif isinstance(raw_aliases, list) and all(
                isinstance(item, str) for item in raw_aliases
            ):
                aliases = tuple(raw_aliases)
            else:
                errors.append(f"{path} aliases for format {name!r} must be strings.")
                continue
        else:
            errors.append(f"{path} format {name!r} must be a string or an object.")
            continue

        if extension is None:
            errors.append(f"{path} format {name!r} requires an extension.")
            continue
        normalized_extension = _normalize_extension(extension)
        if normalized_extension is None:
            errors.append(f"{path} format {name!r} has invalid extension.")
            continue
        formats[name] = FormatDefinition(
            name=name,
            extension=normalized_extension,
            aliases=aliases,
        )
    return formats


def _parse_default_module_imports(
    path: Path,
    raw_modules: object,
    errors: list[str],
) -> tuple[DefaultModuleImport, ...]:
    if raw_modules in ({}, None):
        return ()
    if not isinstance(raw_modules, dict):
        return ()

    raw_defaults = raw_modules.get("defaults", [])
    if raw_defaults in ([], None):
        return ()
    if isinstance(raw_defaults, str):
        raw_defaults = [raw_defaults]
    if not isinstance(raw_defaults, list):
        errors.append(f"{path} modules.defaults must be a string or a list.")
        return ()

    imports: list[DefaultModuleImport] = []
    for item in raw_defaults:
        parsed = _parse_default_module_import(path, item, errors)
        if parsed is not None:
            imports.append(parsed)
    return tuple(imports)


def _parse_default_module_import(
    path: Path,
    raw_import: object,
    errors: list[str],
) -> DefaultModuleImport | None:
    if isinstance(raw_import, str):
        module_name = raw_import.strip()
        if not _MODULE_NAME_RE.fullmatch(module_name):
            errors.append(f"{path} default module name is invalid: {raw_import!r}")
            return None
        return DefaultModuleImport(module_name)

    if not isinstance(raw_import, dict):
        errors.append(f"{path} modules.defaults entries must be strings or objects.")
        return None

    raw_name = raw_import.get("name")
    if not isinstance(raw_name, str) or not _MODULE_NAME_RE.fullmatch(raw_name):
        errors.append(f"{path} default module object requires a valid name.")
        return None

    alias: str | None = None
    raw_alias = raw_import.get("alias")
    if raw_alias is not None:
        if not isinstance(raw_alias, str) or not _DEFINITION_NAME_RE.fullmatch(
            raw_alias
        ):
            errors.append(f"{path} default module {raw_name!r} has invalid alias.")
            return None
        alias = raw_alias

    exposing: tuple[str, ...] | None = None
    raw_exposing = raw_import.get("exposing")
    if raw_exposing is not None:
        if isinstance(raw_exposing, str):
            raw_exposing = [
                item.strip()
                for item in raw_exposing.replace(",", " ").split()
                if item.strip()
            ]
        if not isinstance(raw_exposing, list) or not all(
            isinstance(item, str) for item in raw_exposing
        ):
            errors.append(
                f"{path} default module {raw_name!r} exposing must be a string "
                "or a list of strings."
            )
            return None
        invalid = [
            item for item in raw_exposing if not _DEFINITION_NAME_RE.fullmatch(item)
        ]
        if invalid:
            errors.append(
                f"{path} default module {raw_name!r} has invalid exposed "
                f"name(s): {', '.join(invalid)}."
            )
            return None
        exposing = tuple(raw_exposing)

    return DefaultModuleImport(raw_name, alias=alias, exposing=exposing)


def _parse_fragment_aliases(
    path: Path,
    raw_fragments: object,
    errors: list[str],
) -> dict[str, Path]:
    if raw_fragments in ({}, None):
        return {}
    if not isinstance(raw_fragments, dict):
        errors.append(f"{path} fragments must be a JSON object.")
        return {}

    raw_aliases = raw_fragments.get("aliases", {})
    if raw_aliases in ({}, None):
        return {}
    if not isinstance(raw_aliases, dict):
        errors.append(f"{path} fragments.aliases must be a JSON object.")
        return {}

    aliases: dict[str, Path] = {}
    for raw_alias, raw_root in raw_aliases.items():
        if not isinstance(raw_alias, str):
            errors.append(f"{path} fragment alias names must be strings.")
            continue
        alias = raw_alias.strip()
        if not _FRAGMENT_ALIAS_RE.fullmatch(alias):
            errors.append(f"{path} fragment alias is invalid: {raw_alias!r}")
            continue
        if not isinstance(raw_root, str):
            errors.append(f"{path} fragment alias {alias!r} must be a string path.")
            continue
        root = raw_root.strip()
        if not root:
            errors.append(f"{path} fragment alias {alias!r} must not be empty.")
            continue
        aliases[alias] = _resolve_config_path(path.parent, root)
    return aliases


def _normalize_format_token(value: object) -> str:
    return str(value).strip().lower()


def _normalize_extension(value: str) -> str | None:
    extension = value.strip().lower().removeprefix(".")
    if (
        not extension
        or "/" in extension
        or "\\" in extension
        or extension in {".", ".."}
    ):
        return None
    return extension


def _is_format_identifier(value: str) -> bool:
    if not value or value.startswith(".") or value.endswith(".") or ".." in value:
        return False
    return all(part.replace("-", "_").isidentifier() for part in value.split("."))


def _resolve_config_path(base_dir: Path, raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    return base_dir / path


def _ancestors_from(base_dir: Path) -> tuple[Path, ...]:
    start = base_dir.expanduser().resolve()
    return (start, *start.parents)


def _dedupe_paths(paths: list[Path]) -> tuple[Path, ...]:
    seen: set[Path] = set()
    result: list[Path] = []
    for path in paths:
        resolved = path.expanduser().resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        result.append(resolved)
    return tuple(result)


def _dedupe_default_module_imports(
    imports: list[DefaultModuleImport],
) -> tuple[DefaultModuleImport, ...]:
    seen: set[tuple[str, str | None, tuple[str, ...] | None]] = set()
    result: list[DefaultModuleImport] = []
    for default_import in imports:
        key = (
            default_import.name,
            default_import.alias,
            default_import.exposing,
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(default_import)
    return tuple(result)
