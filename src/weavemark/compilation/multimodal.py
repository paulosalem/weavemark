"""Multimodal input/output primitives for WeaveMark composition.

This module owns the deterministic, compile-time pieces of WeaveMark's image
support:

- :class:`ImageRef` — an image *input* lifted from a composed prompt's Markdown
  image references (``![alt](target)``) or ``data:image/...`` URIs.
- :func:`extract_image_refs` — the deterministic lift that resolves local paths
  and base64-encodes them, so downstream engines can send true multimodal parts.
- :class:`OutputContract` — the ``@output`` production contract (``type: text``
  or ``type: image`` plus type-specific parameters).

Nothing here calls an LLM or a network; conversion to the ``ellements``
multimodal message model lives in the engine layer.
"""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from weavemark.protection import ProtectionContext, ProtectionSettings

_MEDIA_TYPE_BY_EXT: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
}

_IMAGE_EXTENSIONS = frozenset(_MEDIA_TYPE_BY_EXT)

# Markdown image reference: ![alt](target "optional title"), target may be
# wrapped in angle brackets. Titles and surrounding whitespace are ignored.
_MD_IMAGE_RE = re.compile(
    r"!\[(?P<alt>[^\]]*)\]\(\s*<?(?P<target>[^)>\s]+)>?"
    r"(?:\s+\"[^\"]*\"|\s+'[^']*')?\s*\)"
)

_DATA_URI_RE = re.compile(
    r"^data:(?P<media>image/[A-Za-z0-9.+-]+);base64,(?P<data>.+)$",
    re.DOTALL,
)

_VALID_OUTPUT_TYPES = frozenset({"text", "image"})


@dataclass
class ImageRef:
    """A resolved image input lifted from a composed prompt.

    ``source`` is one of ``"url"`` (remote), ``"path"`` (local file, base64 in
    ``data``), or ``"data"`` (inline ``data:`` URI, base64 in ``data``).
    """

    source: str
    ref: str
    alt: str = ""
    media_type: str | None = None
    data: str | None = None
    detail: str = "auto"

    @property
    def data_uri(self) -> str | None:
        """Return a ``data:`` URI for base64 sources, else ``None``."""
        if self.data is None or not self.media_type:
            return None
        return f"data:{self.media_type};base64,{self.data}"

    def to_dict(self, *, include_data: bool = False) -> dict[str, Any]:
        """Serialize for diagnostics/JSON, eliding base64 payloads by default."""
        payload: dict[str, Any] = {
            "source": self.source,
            "ref": self.ref,
            "alt": self.alt,
            "detail": self.detail,
        }
        if self.media_type:
            payload["media_type"] = self.media_type
        if self.data is not None:
            payload["data"] = (
                self.data if include_data else f"<base64: {len(self.data)} chars>"
            )
        return payload


@dataclass
class OutputContract:
    """The declared output contract for a production point.

    ``type`` is ``"text"`` (default) or ``"image"``. ``params`` carries
    type-specific settings (text: ``format``/``enforce``; image:
    ``size``/``quality``/``model``/``n``/…).
    """

    type: str = "text"
    params: dict[str, Any] = field(default_factory=dict)

    @property
    def is_image(self) -> bool:
        return self.type == "image"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"type": self.type}
        payload.update(self.params)
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OutputContract:
        params = {k: v for k, v in data.items() if k != "type"}
        raw_type = str(data.get("type", "text")).strip().lower()
        output_type = raw_type if raw_type in _VALID_OUTPUT_TYPES else "text"
        return cls(type=output_type, params=params)


def _media_type_for(path: Path) -> str | None:
    return _MEDIA_TYPE_BY_EXT.get(path.suffix.lower())


def _target_extension(target: str) -> str:
    """Return the lowercased extension of a URL/path target, ignoring queries."""
    cleaned = target.split("?", 1)[0].split("#", 1)[0]
    return Path(cleaned).suffix.lower()


def _load_image_ref(
    target: str,
    alt: str,
    base_dir: Path,
    protection: ProtectionContext | None = None,
) -> tuple[ImageRef | None, str | None]:
    """Classify and resolve a single Markdown image target.

    Returns ``(ref, warning)``. Non-image targets yield ``(None, None)`` so they
    stay as ordinary text; missing local files yield ``(None, warning)``.
    """

    protection = protection or ProtectionContext.create(
        ProtectionSettings(enabled=False),
        entrypoint_dir=base_dir,
    )
    data_match = _DATA_URI_RE.match(target)
    if data_match is not None:
        return (
            ImageRef(
                source="data",
                ref="data:",
                alt=alt,
                media_type=data_match.group("media"),
                data=data_match.group("data"),
            ),
            None,
        )

    if target.startswith(("http://", "https://")):
        extension = _target_extension(target)
        if extension not in _IMAGE_EXTENSIONS:
            return None, None
        protection.authorize_remote_url(
            target,
            reason="Markdown image reference included in a model request",
        )
        return (
            ImageRef(
                source="url",
                ref=target,
                alt=alt,
                media_type=_MEDIA_TYPE_BY_EXT.get(extension),
            ),
            None,
        )

    extension = _target_extension(target)
    if extension not in _IMAGE_EXTENSIONS:
        return None, None

    path = protection.authorize_read(
        (base_dir / target).expanduser(),
        reason=f"Markdown image reference {target!r}",
    )
    if not path.is_file():
        return None, f"Image reference not found: {target}"
    try:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    except OSError as exc:
        return None, f"Could not read image '{target}': {exc}"
    return (
        ImageRef(
            source="path",
            ref=target,
            alt=alt,
            media_type=_media_type_for(path),
            data=encoded,
        ),
        None,
    )


def extract_image_refs(
    text: str,
    base_dir: Path,
    *,
    protection: ProtectionContext | None = None,
) -> tuple[list[ImageRef], list[str]]:
    """Lift image references from *text* into resolved :class:`ImageRef` parts.

    Scans for Markdown image references and inline ``data:image`` URIs. Only
    genuine images are lifted (extension allowlist + ``data:image`` URIs); other
    links are left untouched. The Markdown stays in the text as a human-readable
    label. Returns ``(refs, warnings)``.
    """

    refs: list[ImageRef] = []
    warnings: list[str] = []
    for match in _MD_IMAGE_RE.finditer(text):
        target = match.group("target").strip()
        alt = match.group("alt").strip()
        ref, warning = _load_image_ref(target, alt, base_dir, protection)
        if ref is not None:
            refs.append(ref)
        if warning is not None:
            warnings.append(warning)
    return refs, warnings


__all__ = [
    "ImageRef",
    "OutputContract",
    "extract_image_refs",
]
