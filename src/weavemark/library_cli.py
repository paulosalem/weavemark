"""CLI browsing and direct execution for effective promplet libraries."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TextIO

from weavemark.promplet_library import (
    LibraryPromplet,
    PrompletLibraryLookupError,
    PrompletLibrarySource,
    collect_library_promplets,
    copy_bundled_promplets,
    library_sources,
    resolve_library_promplet,
    set_process_library_dirs,
)

LIBRARY_MANAGEMENT_COMMANDS = frozenset({"sources", "list", "show", "copy"})
_SOURCE_CHOICES = ("all", "project", "user", "extra", "builtin")
_COLLECTION_CHOICES = (
    "stdlib",
    "domains",
    "catalog",
    "tutorials",
    "experimental",
    "personal",
)
_KIND_CHOICES = ("definition", "fragment", "standalone", "executable", "tutorial")


def _add_library_dirs(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--library-dir",
        action="append",
        type=Path,
        metavar="DIR",
        help="Additional promplet-library root (repeatable).",
    )


def _add_filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--source",
        choices=_SOURCE_CHOICES,
        default="all",
        help="Limit results by physical library source.",
    )
    parser.add_argument(
        "--collection",
        choices=_COLLECTION_CHOICES,
        help="Limit results by collection.",
    )
    parser.add_argument(
        "--kind",
        choices=_KIND_CHOICES,
        help="Limit results by promplet role.",
    )
    _add_library_dirs(parser)


def create_library_parser() -> argparse.ArgumentParser:
    """Create the parser for ``weavemark library`` management commands."""
    parser = argparse.ArgumentParser(
        prog="weavemark library",
        description=(
            "Run a library target directly, or browse built-in, project, user, "
            "and additional promplet libraries."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Direct execution:\n"
            "  weavemark library tutorial-generator\n"
            "  weavemark library investment-brief --var ticker=MSFT --batch-only\n"
            "  weavemark library reflection-solver --run --batch-only\n"
            "  weavemark library module:weavemark.std.reasoning.base_analyst --scan\n\n"
            "Management:\n"
            "  weavemark library sources\n"
            "  weavemark library list finance --collection domains\n"
            "  weavemark library show builtin:catalog/standalone/investment-brief\n"
            "  weavemark library copy ./weavemark-promplets\n\n"
            "Bare targets search project, user, additional, then built-in roots. "
            "Use project:, user:, extra:, builtin:, or module: explicitly."
        ),
    )
    commands = parser.add_subparsers(dest="library_command")

    sources = commands.add_parser(
        "sources",
        help="Show effective promplet-library roots.",
    )
    sources.add_argument("--json", action="store_true", help="Emit JSON.")
    _add_library_dirs(sources)

    list_parser = commands.add_parser("list", help="List available promplets.")
    list_parser.add_argument(
        "query",
        nargs="?",
        help="Text matched against path, title, module, variables, and engine.",
    )
    _add_filters(list_parser)
    list_parser.add_argument("--json", action="store_true", help="Emit JSON.")

    show = commands.add_parser("show", help="Print one promplet source to stdout.")
    show.add_argument(
        "reference",
        help="Module reference, source:path, relative path, or unique short name.",
    )
    _add_library_dirs(show)

    copy_parser = commands.add_parser(
        "copy",
        help="Copy the complete built-in promplet corpus.",
    )
    copy_parser.add_argument("destination", type=Path)
    copy_parser.add_argument(
        "--force",
        action="store_true",
        help="Merge into an existing directory and overwrite matching files.",
    )
    return parser


def parse_library_target(
    argv: list[str],
    *,
    cwd: Path | None = None,
) -> tuple[Path, list[str]]:
    """Resolve ``library TARGET`` and return its path plus Processor arguments."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("target")
    _add_library_dirs(parser)
    args, processor_args = parser.parse_known_args(argv)
    working_dir = (cwd or Path.cwd()).resolve()
    with library_sources(
        cwd=working_dir,
        extra_library_dirs=args.library_dir,
    ) as sources:
        promplets = collect_library_promplets(sources)
        selected = resolve_library_promplet(promplets, args.target)
        set_process_library_dirs(args.library_dir)
        forwarded_library_dirs = [
            argument
            for directory in args.library_dir or []
            for argument in ("--library-dir", str(directory))
        ]
        return selected.entry.path, [*forwarded_library_dirs, *processor_args]


def _promplet_data(promplet: LibraryPromplet) -> dict[str, object]:
    return {
        "reference": promplet.reference,
        "module_reference": promplet.module_reference,
        "source": promplet.source.kind,
        "source_name": promplet.source.name,
        "source_root": str(promplet.source.root),
        "collection": promplet.collection,
        "kind": promplet.kind,
        "relative_path": promplet.relative_path.as_posix(),
        "path": str(promplet.entry.path),
        "title": promplet.entry.title,
        "variables": promplet.entry.variables,
        "execution_strategy": promplet.entry.execution_strategy,
        "has_tools": promplet.entry.has_tools,
    }


@contextmanager
def _load_promplets(
    args: argparse.Namespace,
    *,
    cwd: Path,
) -> Iterator[tuple[list[PrompletLibrarySource], list[LibraryPromplet]]]:
    with library_sources(
        cwd=cwd,
        extra_library_dirs=getattr(args, "library_dir", None),
    ) as sources:
        promplets = collect_library_promplets(
            sources,
            source_kind=getattr(args, "source", "all"),
            collection=getattr(args, "collection", None),
            kind=getattr(args, "kind", None),
            query=getattr(args, "query", None),
        )
        yield list(sources), promplets


def run_library_command(
    args: argparse.Namespace,
    *,
    cwd: Path | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Execute a parsed ``weavemark library`` management command."""
    working_dir = (cwd or Path.cwd()).resolve()
    output = stdout or sys.stdout
    errors = stderr or sys.stderr

    if args.library_command is None:
        create_library_parser().print_help(file=output)
        return 0

    if args.library_command == "copy":
        try:
            count = copy_bundled_promplets(args.destination, overwrite=args.force)
        except (FileExistsError, OSError) as exc:
            print(f"weavemark library: {exc}", file=errors)
            return 1
        print(str(args.destination.expanduser().resolve()), file=output)
        print(f"Copied {count} built-in promplets.", file=errors)
        return 0

    try:
        with _load_promplets(args, cwd=working_dir) as (sources, promplets):
            if args.library_command == "sources":
                data = [
                    {
                        "source": source.kind,
                        "name": source.name,
                        "path": str(source.root),
                    }
                    for source in sources
                ]
                if args.json:
                    print(json.dumps(data, indent=2, ensure_ascii=False), file=output)
                else:
                    print("SOURCE\tNAME\tPATH", file=output)
                    for source in sources:
                        print(
                            f"{source.kind}\t{source.name}\t{source.root}",
                            file=output,
                        )
                return 0

            if args.library_command == "list":
                if args.json:
                    print(
                        json.dumps(
                            [_promplet_data(promplet) for promplet in promplets],
                            indent=2,
                            ensure_ascii=False,
                        ),
                        file=output,
                    )
                else:
                    print("SOURCE\tCOLLECTION\tKIND\tREFERENCE\tTITLE", file=output)
                    for promplet in promplets:
                        print(
                            f"{promplet.source.name}\t{promplet.collection}\t"
                            f"{promplet.kind}\t{promplet.reference}\t"
                            f"{promplet.entry.title}",
                            file=output,
                        )
                return 0

            selected = resolve_library_promplet(promplets, args.reference)
            print(selected.entry.raw_text, end="", file=output)
            return 0
    except (FileNotFoundError, OSError, PrompletLibraryLookupError, ValueError) as exc:
        print(f"weavemark library: {exc}", file=errors)
        return 1


__all__ = [
    "LIBRARY_MANAGEMENT_COMMANDS",
    "create_library_parser",
    "parse_library_target",
    "run_library_command",
]
