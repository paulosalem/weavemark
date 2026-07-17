"""Directive-header argument parsing helpers."""

from __future__ import annotations

import re
import shlex
from dataclasses import dataclass

_IDENT_RE = re.compile(r"^[A-Za-z_][\w.-]*$")


@dataclass(frozen=True)
class HeaderToken:
    """One token from a directive header."""

    text: str
    quoted: bool = False


@dataclass(frozen=True)
class ParsedArgs:
    """Parsed directive header arguments."""

    positional: list[str]
    options: dict[str, str]
    errors: list[str]


def parse_header_args(rest: str, *, allow_equals: bool = False) -> ParsedArgs:
    """Parse a WeaveMark directive header.

    Free-form positional strings may contain multiple unquoted words, but they
    must appear before named parameters. Quoting remains mandatory for ambiguous
    positional text containing ``:`` or bracket/list syntax.
    """

    tokens, token_errors = split_header_tokens(rest)
    positional: list[str] = []
    options: dict[str, str] = {}
    errors = list(token_errors)
    index = 0
    saw_named = False
    while index < len(tokens):
        token = tokens[index]
        option = _parse_option_token(token, allow_equals=allow_equals)
        if option is not None:
            key, value = option
            saw_named = True
            duplicate = key in options
            if duplicate:
                errors.append(f"Duplicate named parameter '{key}'.")
            if value:
                if not duplicate:
                    options[key] = value
                index += 1
                continue
            if index + 1 < len(tokens):
                if not duplicate:
                    options[key] = tokens[index + 1].text
                index += 2
                continue
            errors.append(f"Named parameter '{key}' requires a value.")
            index += 1
            continue

        if saw_named:
            errors.append(
                f"Unexpected positional token {token.text!r} after named "
                "parameters; put free-form text before named parameters or quote "
                "it as a named parameter value."
            )
            index += 1
            continue

        if not token.quoted and ":" in token.text:
            errors.append(
                f"Unquoted positional token {token.text!r} contains ':'; quote "
                "the string to avoid confusion with named parameters."
            )
        if not token.quoted and ("[" in token.text or "]" in token.text):
            errors.append(
                f"Unquoted positional token {token.text!r} contains bracket/list "
                "syntax; quote the string if it is literal text."
            )
        positional.append(token.text)
        index += 1
    return ParsedArgs(positional=positional, options=options, errors=errors)


def split_header_tokens(rest: str) -> tuple[list[HeaderToken], list[str]]:
    """Split directive-header text while preserving quote information."""

    if not rest.strip():
        return [], []
    lexer = shlex.shlex(rest.strip(), posix=False)
    lexer.whitespace_split = True
    lexer.commenters = ""
    try:
        raw_tokens = list(lexer)
    except ValueError as exc:
        return [HeaderToken(token) for token in rest.strip().split()], [str(exc)]

    tokens: list[HeaderToken] = []
    index = 0
    while index < len(raw_tokens):
        token = raw_tokens[index]
        quoted, text = _strip_quotes(token)
        if not quoted and text.startswith("[") and not text.endswith("]"):
            parts = [text]
            index += 1
            while index < len(raw_tokens):
                part_quoted, part_text = _strip_quotes(raw_tokens[index])
                quoted = quoted or part_quoted
                parts.append(part_text)
                if part_text.endswith("]"):
                    break
                index += 1
            tokens.append(HeaderToken(" ".join(parts), quoted=quoted))
            index += 1
            continue
        tokens.append(HeaderToken(text, quoted=quoted))
        index += 1
    return tokens, []


def _parse_option_token(
    token: HeaderToken,
    *,
    allow_equals: bool,
) -> tuple[str, str] | None:
    if token.quoted:
        return None
    text = token.text
    if text.endswith(":") and _IDENT_RE.fullmatch(text[:-1]):
        return text[:-1], ""
    if ":" in text:
        key, value = text.split(":", 1)
        if _IDENT_RE.fullmatch(key):
            return key, _strip_quotes(value)[1]
    if allow_equals and "=" in text:
        key, value = text.split("=", 1)
        if _IDENT_RE.fullmatch(key):
            return key, _strip_quotes(value)[1]
    return None


def _strip_quotes(token: str) -> tuple[bool, str]:
    if len(token) >= 2 and token[0] == token[-1] and token[0] in {"'", '"'}:
        return True, token[1:-1]
    return False, token
