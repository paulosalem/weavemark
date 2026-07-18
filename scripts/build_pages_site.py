"""Build and validate the public GitHub Pages artifact."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_TREES = (
    "docs",
    "examples",
    "outputs",
    "promplets",
    "src",
    "studies",
    "vscode-extension",
)
PUBLIC_ROOT_FILES = ("CHANGELOG.md", "LICENSE", "README.md")
GITHUB_REPOSITORY_URL = "https://github.com/paulosalem/weavemark"
REPOSITORY_LINK_PATTERN = re.compile(
    r'href="\.\./(?P<path>(?:examples|outputs|promplets|src|studies|vscode-extension)/[^"#]*)"'
)
LIVE_DEMOS: dict[str, tuple[str, tuple[str, ...]]] = {
    "orbital-drift": (
        "outputs/implementations/orbital-drift",
        ("index.html", "styles.css", "favicon.svg", "src/engine.js", "src/main.js"),
    ),
    "transit-city-swarm": (
        "outputs/implementations/transit-city-swarm",
        ("index.html", "styles.css", "src/app.js", "src/simulation.js"),
    ),
}
CONFIDENTIAL_MARKERS = (
    b"prompting" + b" adventures",
    b"/users/" + b"paulo" + b"salem",
    b"googledrive-" + b"paulo" + b"salem",
)
ROOT_REDIRECT = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="0; url=docs/index.html">
    <link rel="canonical" href="docs/index.html">
    <link rel="icon" href="docs/weavemark_favicon.png" type="image/png">
    <title>WeaveMark</title>
  </head>
  <body>
    <p><a href="docs/index.html">Open the WeaveMark website</a>.</p>
  </body>
</html>
"""
FAVICON_LINK = '    <link rel="icon" href="weavemark_favicon.png" type="image/png">\n'


class _LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        values = dict(attrs)
        identifier = values.get("id")
        if identifier:
            self.ids.add(identifier)
        for attribute in ("href", "src"):
            value = values.get(attribute)
            if value:
                self.links.append(value)


def tracked_paths(root: Path = ROOT) -> list[Path]:
    """Return tracked repository files in stable lexical order."""

    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        capture_output=True,
        check=True,
    )
    paths = (
        root / raw.decode("utf-8")
        for raw in completed.stdout.split(b"\0")
        if raw
    )
    return sorted(
        (path for path in paths if path.is_file()),
        key=lambda path: str(path.relative_to(root)),
    )


def lfs_paths(paths: list[Path], root: Path = ROOT) -> set[Path]:
    """Return tracked paths whose effective Git filter is LFS."""

    if not paths:
        return set()
    relative = [str(path.relative_to(root)) for path in paths]
    completed = subprocess.run(
        ["git", "check-attr", "--stdin", "-z", "filter"],
        cwd=root,
        input=b"\0".join(item.encode("utf-8") for item in relative) + b"\0",
        capture_output=True,
        check=True,
    )
    fields = completed.stdout.split(b"\0")
    result: set[Path] = set()
    for index in range(0, len(fields) - 2, 3):
        raw_path, attribute, value = fields[index : index + 3]
        if attribute == b"filter" and value == b"lfs":
            result.add(root / raw_path.decode("utf-8"))
    return result


def build_site(destination: Path, root: Path = ROOT) -> list[Path]:
    """Build a clean public site and return its copied repository paths."""

    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    paths = tracked_paths(root)
    lfs = lfs_paths(paths, root)
    copied: list[Path] = []
    for source in paths:
        relative = source.relative_to(root)
        if source in lfs or not _is_public_path(relative):
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(relative)

    (destination / "index.html").write_text(ROOT_REDIRECT, encoding="utf-8")
    (destination / ".nojekyll").touch()
    _publish_live_demos(destination, root, set(paths), lfs)
    _rewrite_repository_links(destination / "docs", root)
    _inject_favicon(destination / "docs")
    return copied


def validate_site(destination: Path) -> list[str]:
    """Return missing-link and public-boundary violations."""

    errors: list[str] = []
    html_documents: dict[Path, _LinkCollector] = {}
    for html_path in destination.rglob("*.html"):
        collector = _LinkCollector()
        collector.feed(html_path.read_text(encoding="utf-8"))
        html_documents[html_path.resolve()] = collector

    for html_path, collector in html_documents.items():
        for value in collector.links:
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc or value.startswith(
                ("mailto:", "javascript:", "data:")
            ):
                continue
            raw_path = unquote(parsed.path)
            if not raw_path:
                target = html_path
            elif raw_path.startswith("/"):
                errors.append(
                    f"{html_path.relative_to(destination)} uses root-relative link {value!r}"
                )
                continue
            else:
                target = (html_path.parent / raw_path).resolve()
            if not _within(target, destination.resolve()) or not target.exists():
                errors.append(
                    f"{html_path.relative_to(destination)} -> missing {value}"
                )
                continue
            if parsed.fragment and target.suffix.casefold() == ".html":
                target_collector = html_documents.get(target)
                if (
                    target_collector is not None
                    and parsed.fragment not in target_collector.ids
                ):
                    errors.append(
                        f"{html_path.relative_to(destination)} -> "
                        f"missing anchor {value}"
                    )

    for path in destination.rglob("*"):
        if not path.is_file():
            continue
        content = path.read_bytes().lower()
        if content.startswith(b"version https://git-lfs.github.com/spec/v1"):
            errors.append(f"Git LFS pointer copied into site: {path.relative_to(destination)}")
        for marker in CONFIDENTIAL_MARKERS:
            if marker in content:
                errors.append(
                    f"private context leaked into site: {path.relative_to(destination)}"
                )
    return sorted(set(errors))


def _is_public_path(relative: Path) -> bool:
    if (
        relative.parts
        and relative.parts[0] == "examples"
        and "outputs" in relative.parts
        and relative.name == "book.html"
    ):
        return False
    if relative.parts and relative.parts[0] in PUBLIC_TREES:
        return True
    return relative.as_posix() in PUBLIC_ROOT_FILES


def _inject_favicon(docs_directory: Path) -> None:
    for html_path in docs_directory.glob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        if 'rel="icon"' not in text:
            text = text.replace("</head>", f"{FAVICON_LINK}</head>", 1)
            html_path.write_text(text, encoding="utf-8")


def _publish_live_demos(
    destination: Path,
    root: Path,
    tracked: set[Path],
    lfs: set[Path],
) -> None:
    for slug, (source_directory, assets) in LIVE_DEMOS.items():
        for relative_asset in assets:
            source = root / source_directory / relative_asset
            if source not in tracked:
                raise FileNotFoundError(f"Live demo asset is not tracked: {source}")
            if source in lfs:
                raise ValueError(f"Live demo asset cannot use Git LFS: {source}")
            target = destination / "demos" / slug / relative_asset
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def _rewrite_repository_links(docs_directory: Path, root: Path) -> None:
    def replace(match: re.Match[str]) -> str:
        relative = Path(match.group("path").rstrip("/"))
        source = root / relative
        if not source.exists():
            raise FileNotFoundError(f"Documentation source link is missing: {source}")
        kind = "tree" if source.is_dir() else "blob"
        return f'href="{GITHUB_REPOSITORY_URL}/{kind}/main/{relative.as_posix()}"'

    for html_path in docs_directory.glob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        rewritten = REPOSITORY_LINK_PATTERN.sub(replace, text)
        if rewritten != text:
            html_path.write_text(rewritten, encoding="utf-8")


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def main(arguments: list[str] | None = None) -> int:
    """Build and validate the configured Pages output directory."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(arguments)
    destination = args.output.expanduser().resolve()
    copied = build_site(destination)
    errors = validate_site(destination)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    total_bytes = sum(
        path.stat().st_size for path in destination.rglob("*") if path.is_file()
    )
    print(
        f"GitHub Pages artifact OK: {len(copied)} repository files, "
        f"{total_bytes / (1024 * 1024):.2f} MiB."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
