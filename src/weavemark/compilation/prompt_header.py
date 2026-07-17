"""Parser for ``@prompt`` directive headers.

Parses a single ``@prompt`` directive line into its constituent parameters:

- ``name``       — the prompt's identifier (required)
- ``role``       — strict LLM chat role (``system|user|assistant|tool``)
- ``format``     — optional content/template format (e.g. ``mustache``)

The filename composed for emitted artifacts follows the rule:

    <name>.<role>[.<format-if-different-from-compile-format>].<ext>

The parser performs strict validation: duplicate keys, missing values,
unknown parameters, invalid role values, and malformed ``format`` values.

This module is intentionally shared between the structural compiler
(``compilation/structural.py``) and the TUI/IDE scanner
(``tui/scanner.py``) to guarantee parser parity.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

VALID_LLM_ROLES: frozenset[str] = frozenset({"system", "user", "assistant", "tool"})

# Free-form value: alphanumerics (plus _ and -), optionally joined by dots.
# Forbids leading/trailing dots and consecutive dots to keep filenames
# unambiguous.
_VARIANT_VALUE_RE = re.compile(r"^[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*$")

# Prompt name: identifier (may contain dots / hyphens) OR a ``@{var}``
# template reference.
_NAME_RE = re.compile(r"^(?:@\{\s*[A-Za-z_][\w.-]*\s*\}|[A-Za-z_][\w.-]*)")

_KEY_RE = re.compile(r"^([A-Za-z_]\w*)\s*:")
_VALUE_RE = re.compile(r"^(\S+)")

# Quick check used by callers that only need to know whether a line is
# *some* ``@prompt`` header (parsing the parameters comes later).
PROMPT_LINE_RE = re.compile(r"^@prompt\s")

_KNOWN_KEYS = frozenset({"role", "format"})


@dataclass
class ParsedPromptHeader:
    """Result of parsing an ``@prompt`` directive line."""

    name: str
    role: str | None = None
    format: str | None = None
    errors: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors

    @property
    def has_dynamic_name(self) -> bool:
        return self.name.startswith("@{")

    def emit_filename(
        self,
        extension: str,
        *,
        prompt_format_extension: str | None = None,
    ) -> str | None:
        """Compose the emitted artifact filename.

        Returns ``None`` when ``role`` is unset (emission requires a role)
        or when the name is dynamic (``@{var}``) — both are situations
        where a static filename cannot be predicted.
        """

        if not self.role or self.has_dynamic_name:
            return None
        parts: list[str] = [self.name, self.role]
        if prompt_format_extension:
            parts.append(prompt_format_extension)
        return ".".join(parts) + "." + extension


def parse_prompt_header(line: str) -> ParsedPromptHeader | None:
    """Parse the header portion of an ``@prompt`` line.

    Returns ``None`` when the line is not an ``@prompt`` header at all.
    Returns a :class:`ParsedPromptHeader` (possibly carrying errors) when
    the line *is* an ``@prompt`` directive — even if it is malformed.

    The caller is expected to surface ``result.errors`` to the user. A
    parsed-with-errors result still carries best-effort ``name``/``role``
    extraction so downstream code can continue producing output.
    """

    # Allow the caller to pass either an indented or unindented line; we
    # strip leading whitespace for parsing.
    stripped = line.rstrip("\r\n").lstrip()
    if not stripped.startswith("@prompt"):
        return None
    rest = stripped[len("@prompt") :]
    if not rest or not rest[0].isspace():
        # ``@prompts``, ``@promptz``, etc. are not us.
        return None
    rest = rest.lstrip()

    name_match = _NAME_RE.match(rest)
    if not name_match:
        return ParsedPromptHeader(
            name="",
            errors=[
                f"@prompt requires a name; got: {line.strip()!r}",
            ],
        )
    name = name_match.group(0)
    rest = rest[name_match.end() :].lstrip()

    parsed = ParsedPromptHeader(name=name)
    seen_keys: set[str] = set()

    while rest:
        key_match = _KEY_RE.match(rest)
        if not key_match:
            parsed.errors.append(
                f"@prompt {name}: unexpected token after parameters: "
                f"{rest.strip()!r}"
            )
            return parsed
        key = key_match.group(1).lower()
        after_key = rest[key_match.end() :].lstrip()
        value_match = _VALUE_RE.match(after_key)
        if not value_match:
            parsed.errors.append(f"@prompt {name}: missing value for {key!r}")
            return parsed
        value = value_match.group(1)

        if key in seen_keys:
            parsed.errors.append(f"@prompt {name}: duplicate parameter {key!r}")
            return parsed
        seen_keys.add(key)

        if key not in _KNOWN_KEYS:
            parsed.errors.append(
                f"@prompt {name}: unknown parameter {key!r}; "
                f"supported parameters are role and format"
            )
            return parsed

        if key == "role":
            normalized = value.lower()
            if normalized not in VALID_LLM_ROLES:
                parsed.errors.append(
                    f"@prompt {name}: invalid role {value!r}. "
                    f"Valid roles are: system, user, assistant, tool."
                )
                return parsed
            parsed.role = normalized
        else:  # key == "format"
            if not _VARIANT_VALUE_RE.match(value):
                parsed.errors.append(
                    f"@prompt {name}: invalid format {value!r}; "
                    f"must be alphanumerics with optional . - _ separators "
                    f"(no leading/trailing/consecutive dots)"
                )
                return parsed
            parsed.format = value

        rest = after_key[value_match.end() :].lstrip()

    if parsed.format and not parsed.role:
        parsed.errors.append(
            f"@prompt {name}: format: requires role: to also be set "
            f"(an emitted artifact must declare its LLM role)"
        )

    return parsed
