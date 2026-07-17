"""Bundled, project, user, and additional WeaveMark promplet libraries.

The canonical built-in corpus lives at the repository root in ``promplets/``.
Wheel builds map that same tree to ``weavemark/promplets``. Project, user, and
configured roots participate in the same catalog and module namespace.
"""

from __future__ import annotations

import os
import re
import shutil
import tempfile
from collections import defaultdict
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from importlib.resources import as_file, files
from importlib.resources.abc import Traversable
from pathlib import Path, PurePosixPath

from weavemark.defaults import SPEC_EXTENSIONS
from weavemark.discovery.catalog import SpecEntry, index_spec
from weavemark.discovery.config import GLOBAL_DIR, load_config

_SOURCE_KINDS = {"all", "project", "user", "extra", "builtin"}
_COLLECTIONS = {"stdlib", "domains", "catalog", "tutorials", "experimental"}
_KINDS = {"definition", "fragment", "standalone", "executable", "tutorial"}
_LIBRARY_PATH_ENV = "WEAVEMARK_LIBRARY_PATH"
_MODULE_DECLARATION_RE = re.compile(
    r"(?m)^@module[ \t]+([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)[ \t]*$"
)


@dataclass(frozen=True)
class PrompletLibrarySource:
    """One ordered root contributing promplets to the effective library."""

    kind: str
    root: Path
    name: str


@dataclass(frozen=True)
class LibraryPromplet:
    """One indexed promplet together with its library provenance and role."""

    source: PrompletLibrarySource
    relative_path: PurePosixPath
    entry: SpecEntry
    collection: str
    kind: str

    @property
    def reference(self) -> str:
        """Return the explicit ``source:path`` reference for this promplet."""
        return f"{self.source.kind}:{self.relative_path.as_posix()}"

    @property
    def module_reference(self) -> str | None:
        """Return the stable ``module:name`` reference, when declared."""
        if self.entry.module_name is None:
            return None
        return f"module:{self.entry.module_name}"


class PrompletLibraryLookupError(ValueError):
    """Raised when a library reference is missing, invalid, or ambiguous."""


@dataclass(frozen=True)
class PrompletModuleSource:
    """Resolved source text and lexical base for one declared module."""

    name: str
    text: str
    path: Path
    source: PrompletLibrarySource


def _source_checkout_promplets() -> Path:
    return Path(__file__).resolve().parents[2] / "promplets"


def _find_project_promplets(start: Path) -> Path:
    current = start.expanduser().resolve()
    for directory in (current, *current.parents):
        candidate = directory / "promplets"
        if candidate.is_dir():
            return candidate
    return current / "promplets"


def bundled_promplets() -> Traversable:
    """Return the built-in promplet-library root as a resource traversable."""
    packaged = files("weavemark").joinpath("promplets")
    if packaged.is_dir():
        return packaged

    checkout = _source_checkout_promplets()
    if checkout.is_dir():
        return checkout

    raise FileNotFoundError(
        "The built-in WeaveMark promplet library is unavailable. Reinstall "
        "WeaveMark from a wheel that includes package resources."
    )


def _validated_relative_path(relative_path: str | PurePosixPath) -> PurePosixPath:
    path = PurePosixPath(str(relative_path).replace("\\", "/"))
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError(
            "Promplet resource paths must be relative and may not contain '..'."
        )
    return path


def bundled_promplet(relative_path: str | PurePosixPath) -> Traversable:
    """Return one built-in promplet resource, rejecting path traversal."""
    relative = _validated_relative_path(relative_path)
    resource = bundled_promplets().joinpath(*relative.parts)
    if not resource.is_file():
        raise FileNotFoundError(f"Built-in promplet not found: {relative.as_posix()}")
    return resource


def read_bundled_promplet(relative_path: str | PurePosixPath) -> str:
    """Read one built-in promplet as UTF-8 text."""
    return bundled_promplet(relative_path).read_text(encoding="utf-8")


def _walk_promplets(
    root: Traversable,
    relative: PurePosixPath | None = None,
) -> Iterator[PurePosixPath]:
    if relative is None:
        relative = PurePosixPath()
    for child in sorted(root.iterdir(), key=lambda item: item.name):
        child_relative = relative / child.name
        if child.is_dir():
            yield from _walk_promplets(child, child_relative)
        elif child.is_file() and child.name.endswith(SPEC_EXTENSIONS):
            yield child_relative


def iter_bundled_promplets() -> Iterator[PurePosixPath]:
    """Yield every built-in promplet path in stable lexical order."""
    yield from _walk_promplets(bundled_promplets())


@contextmanager
def bundled_promplets_path() -> Iterator[Path]:
    """Materialize the built-in library as a filesystem path."""
    resource = bundled_promplets()
    if isinstance(resource, Path):
        yield resource
        return

    with tempfile.TemporaryDirectory(prefix="weavemark-promplets-") as temporary:
        destination = Path(temporary) / "promplets"
        _copy_traversable(resource, destination)
        yield destination


@contextmanager
def bundled_promplet_path(
    relative_path: str | PurePosixPath,
) -> Iterator[Path]:
    """Materialize one built-in promplet as a filesystem path."""
    with as_file(bundled_promplet(relative_path)) as path:
        yield path


def _copy_traversable(source: Traversable, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        target = destination / child.name
        if child.is_dir():
            _copy_traversable(child, target)
        elif child.is_file():
            target.write_bytes(child.read_bytes())


def copy_bundled_promplets(destination: Path, *, overwrite: bool = False) -> int:
    """Copy the complete built-in corpus to *destination* and return its count."""
    destination = destination.expanduser().resolve()
    if destination.exists() and any(destination.iterdir()) and not overwrite:
        raise FileExistsError(
            f"Destination is not empty: {destination}. Use --force to merge."
        )

    with bundled_promplets_path() as source:
        shutil.copytree(source, destination, dirs_exist_ok=destination.exists())

    return sum(
        1
        for path in destination.rglob("*")
        if path.is_file() and path.name.endswith(SPEC_EXTENSIONS)
    )


@contextmanager
def library_sources(
    *,
    cwd: Path | None = None,
    extra_library_dirs: list[Path] | None = None,
) -> Iterator[list[PrompletLibrarySource]]:
    """Yield project, user, additional, then built-in library roots."""
    working_dir = (cwd or Path.cwd()).resolve()
    config = load_config(
        project_dir=working_dir,
        extra_library_dirs=extra_library_dirs,
    )

    with bundled_promplets_path() as builtin_root:
        builtin = builtin_root.resolve()
        project = _find_project_promplets(working_dir)
        user = (GLOBAL_DIR / "promplets").resolve()
        sources: list[PrompletLibrarySource] = []
        seen: set[Path] = set()

        def add(kind: str, name: str, root: Path) -> None:
            resolved = root.expanduser().resolve()
            if not resolved.is_dir() or resolved in seen or resolved == builtin:
                return
            seen.add(resolved)
            sources.append(PrompletLibrarySource(kind, resolved, name))

        add("project", "project", project)
        add("user", "user", user)
        additional = [*config.library_dirs, *_environment_library_dirs()]
        for index, directory in enumerate(additional, start=1):
            add("extra", f"extra-{index}", directory)

        sources.append(PrompletLibrarySource("builtin", builtin, "builtin"))
        yield sources


def _environment_library_dirs() -> list[Path]:
    value = os.environ.get(_LIBRARY_PATH_ENV, "")
    return [
        Path(item).expanduser()
        for item in value.split(os.pathsep)
        if item.strip()
    ]


def set_process_library_dirs(directories: list[Path] | None) -> None:
    """Set additional library roots for the current Processor invocation."""
    if not directories:
        return
    os.environ[_LIBRARY_PATH_ENV] = os.pathsep.join(
        str(directory.expanduser().resolve()) for directory in directories
    )


def resolve_module_source(
    module_name: str,
    *,
    cwd: Path,
    extra_library_dirs: list[Path] | None = None,
) -> PrompletModuleSource:
    """Resolve one globally unique module declaration across library roots."""
    matches: list[PrompletModuleSource] = []
    with library_sources(
        cwd=cwd,
        extra_library_dirs=extra_library_dirs,
    ) as sources:
        for source in sources:
            for path in sorted(source.root.rglob("*.weavemark.md")):
                try:
                    text = path.read_text(encoding="utf-8")
                except (OSError, UnicodeError):
                    continue
                declaration = _MODULE_DECLARATION_RE.search(text)
                if declaration is None or declaration.group(1) != module_name:
                    continue
                if module_name.startswith("weavemark.") and source.kind != "builtin":
                    raise PrompletLibraryLookupError(
                        f"Module namespace 'weavemark.*' is reserved; {path} "
                        f"declares {module_name}."
                    )
                matches.append(
                    PrompletModuleSource(
                        name=module_name,
                        text=text,
                        path=path.resolve(),
                        source=source,
                    )
                )

    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise PrompletLibraryLookupError(f"Module '{module_name}' was not found.")
    paths = "\n".join(f"  {match.path}" for match in matches)
    raise PrompletLibraryLookupError(
        f"Duplicate module '{module_name}':\n{paths}"
    )


def _classify(relative_path: PurePosixPath, entry: SpecEntry) -> tuple[str, str]:
    parts = relative_path.parts
    collection = parts[0] if parts and parts[0] in _COLLECTIONS else "personal"
    if entry.module_name is not None:
        kind = "definition" if "definitions" in parts or "prelude" in parts else "fragment"
    elif entry.execution_strategy is not None or "executable" in parts:
        kind = "executable"
    elif collection == "tutorials":
        kind = "tutorial"
    else:
        kind = "standalone"
    return collection, kind


def _validate_module_namespace(promplets: list[LibraryPromplet]) -> None:
    modules: dict[str, list[LibraryPromplet]] = defaultdict(list)
    for promplet in promplets:
        name = promplet.entry.module_name
        if name is None:
            continue
        if name.startswith("weavemark.") and promplet.source.kind != "builtin":
            raise PrompletLibraryLookupError(
                f"Module namespace 'weavemark.*' is reserved; {promplet.entry.path} "
                f"declares {name}."
            )
        modules[name].append(promplet)

    duplicates = {name: items for name, items in modules.items() if len(items) > 1}
    if not duplicates:
        return
    details = []
    for name, items in sorted(duplicates.items()):
        paths = "\n".join(f"  {item.entry.path}" for item in items)
        details.append(f"Duplicate module '{name}':\n{paths}")
    raise PrompletLibraryLookupError("\n".join(details))


def collect_library_promplets(
    sources: list[PrompletLibrarySource],
    *,
    source_kind: str = "all",
    collection: str | None = None,
    kind: str | None = None,
    query: str | None = None,
) -> list[LibraryPromplet]:
    """Index and filter promplets from ordered library roots."""
    if source_kind not in _SOURCE_KINDS:
        raise ValueError(f"Unknown library source: {source_kind}")
    if collection is not None and collection not in {*_COLLECTIONS, "personal"}:
        raise ValueError(f"Unknown promplet collection: {collection}")
    if kind is not None and kind not in _KINDS:
        raise ValueError(f"Unknown promplet kind: {kind}")

    all_promplets: list[LibraryPromplet] = []
    for source in sources:
        matches: list[Path] = []
        for extension in SPEC_EXTENSIONS:
            matches.extend(source.root.rglob(f"*{extension}"))
        for path in sorted(set(matches)):
            try:
                entry = index_spec(path)
            except (OSError, UnicodeError, ValueError):
                continue
            relative = PurePosixPath(path.relative_to(source.root).as_posix())
            item_collection, item_kind = _classify(relative, entry)
            all_promplets.append(
                LibraryPromplet(
                    source=source,
                    relative_path=relative,
                    entry=entry,
                    collection=item_collection,
                    kind=item_kind,
                )
            )

    _validate_module_namespace(all_promplets)

    needle = query.casefold() if query else None
    results: list[LibraryPromplet] = []
    for item in all_promplets:
        if source_kind != "all" and item.source.kind != source_kind:
            continue
        if collection is not None and item.collection != collection:
            continue
        if kind is not None and item.kind != kind:
            continue
        searchable = " ".join(
            (
                item.relative_path.as_posix(),
                item.entry.title,
                item.entry.module_name or "",
                item.entry.execution_strategy or "",
                " ".join(item.entry.variables),
            )
        ).casefold()
        if needle and needle not in searchable:
            continue
        results.append(item)
    return results


def _reference_parts(reference: str) -> tuple[str | None, str]:
    value = reference.strip().replace("\\", "/")
    if value.startswith("module:"):
        return "module", value.removeprefix("module:")
    if ":" in value:
        prefix, rest = value.split(":", 1)
        if prefix in _SOURCE_KINDS - {"all"}:
            return prefix, rest.lstrip("/")
    return None, value.lstrip("/")


def resolve_library_promplet(
    promplets: list[LibraryPromplet],
    reference: str,
) -> LibraryPromplet:
    """Resolve a module, source-qualified path, relative path, or short name."""
    reference_kind, value = _reference_parts(reference)
    if reference_kind == "module":
        matches = [
            item for item in promplets if item.entry.module_name == value
        ]
        if len(matches) == 1:
            return matches[0]
        if not matches:
            raise PrompletLibraryLookupError(f"Module '{value}' was not found.")
        raise PrompletLibraryLookupError(f"Module '{value}' is defined more than once.")

    candidates = [
        item
        for item in promplets
        if reference_kind is None or item.source.kind == reference_kind
    ]
    exact_values = {value}
    if not value.endswith(SPEC_EXTENSIONS):
        exact_values.update(f"{value}{extension}" for extension in SPEC_EXTENSIONS)
    exact = [
        item
        for item in candidates
        if item.relative_path.as_posix() in exact_values
    ]
    if exact:
        return exact[0]

    short_matches = [
        item
        for item in candidates
        if item.entry.short_name == value or item.relative_path.stem == value
    ]
    effective: list[LibraryPromplet] = []
    seen_paths: set[PurePosixPath] = set()
    for item in short_matches:
        if item.relative_path in seen_paths:
            continue
        seen_paths.add(item.relative_path)
        effective.append(item)
    if len(effective) == 1:
        return effective[0]
    if not effective:
        raise PrompletLibraryLookupError(f"No library promplet matches '{reference}'.")

    match_details = "\n".join(f"  {item.reference}" for item in effective)
    raise PrompletLibraryLookupError(
        f"Library reference '{reference}' is ambiguous. Use one of:\n{match_details}"
    )


__all__ = [
    "LibraryPromplet",
    "PrompletLibraryLookupError",
    "PrompletLibrarySource",
    "PrompletModuleSource",
    "bundled_promplet",
    "bundled_promplet_path",
    "bundled_promplets",
    "bundled_promplets_path",
    "collect_library_promplets",
    "copy_bundled_promplets",
    "iter_bundled_promplets",
    "library_sources",
    "read_bundled_promplet",
    "resolve_module_source",
    "resolve_library_promplet",
    "set_process_library_dirs",
]
