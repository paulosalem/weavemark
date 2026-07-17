"""Experimental trust-boundary enforcement for WeaveMark operations."""

from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import socket
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, cast

ProtectionDecision = Literal["allow", "confirm", "deny"]
ApprovalHandler = Callable[["ProtectionRequest"], bool]

_DECISIONS = {"allow", "confirm", "deny"}
_SENSITIVE_PARTS = frozenset(
    {
        ".aws",
        ".azure",
        ".git",
        ".gnupg",
        ".kube",
        ".ssh",
        "credentials",
        "secrets",
    }
)
_SENSITIVE_NAMES = frozenset(
    {
        ".env",
        ".netrc",
        "authorized_keys",
        "credentials.json",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        "id_rsa",
        "known_hosts",
        "service-account.json",
    }
)
_SENSITIVE_SUFFIXES = frozenset({".key", ".p12", ".pfx", ".pem"})
_APPROVALS_FILE = "protection-approvals.json"
_MAX_APPROVAL_FILE_BYTES = 2 * 1024 * 1024
_PROJECT_ROOT_MARKERS = (
    ".weavemark-root",
    "weavemark.json",
    ".git",
    "pyproject.toml",
)


@dataclass(frozen=True)
class ProtectionSettings:
    """User-controlled experimental protection policy."""

    enabled: bool = True
    read_roots: tuple[str, ...] = ()
    write_roots: tuple[str, ...] = ()
    sensitive_files: ProtectionDecision = "deny"
    dynamic_reads: ProtectionDecision = "confirm"
    writes_outside_roots: ProtectionDecision = "confirm"
    python_code: ProtectionDecision = "confirm"
    external_process: ProtectionDecision = "confirm"
    remote_https: ProtectionDecision = "allow"
    remote_http: ProtectionDecision = "deny"
    private_networks: ProtectionDecision = "deny"
    max_download_bytes: int = 20_000_000
    download_timeout_seconds: float = 30.0
    max_redirects: int = 3
    subprocess_environment: tuple[str, ...] = ("PATH",)


@dataclass(frozen=True)
class ProtectionRequest:
    """One high-risk operation requiring a remembered user decision."""

    capability: str
    subject: str
    fingerprint: str
    reason: str
    danger: str
    config_key: str


class ProtectionError(PermissionError):
    """Raised when experimental protections block an operation."""

    def __init__(
        self,
        *,
        capability: str,
        subject: str,
        reason: str,
        danger: str,
        config_key: str,
    ) -> None:
        self.capability = capability
        self.subject = subject
        self.reason = reason
        self.danger = danger
        self.config_key = config_key
        super().__init__(self.cli_message())

    def cli_message(self) -> str:
        """Return a clear, warning-flavored CLI diagnostic."""

        return (
            f"🛑 [bold red]WEAVEMARK PROTECTION BLOCKED[/]\n\n"
            f"[bold]Operation:[/] {self.capability}\n"
            f"[bold]Target:[/] {self.subject}\n"
            f"[bold]Why blocked:[/] {self.reason}\n"
            f"[bold]Why this may be dangerous:[/] {self.danger}\n\n"
            f"[bold]Policy:[/] {self.config_key}\n"
            "Options:\n"
            "  • adjust the user-level `protections` configuration;\n"
            "  • add an explicit allowed root where applicable;\n"
            "  • rerun interactively to approve and remember this exact item; or\n"
            "  • use `--no-protections` only when you deliberately trust the promplet.\n\n"
            "[bold yellow]Experimental protections reduce risk but do not make "
            "untrusted promplets safe.[/]"
        )


@dataclass
class ProtectionContext:
    """Resolved protection policy for one compile/execute invocation."""

    settings: ProtectionSettings
    entrypoint_dir: Path
    invocation_dir: Path
    read_roots: tuple[Path, ...]
    write_roots: tuple[Path, ...]
    approval_handler: ApprovalHandler | None = None
    approvals_path: Path = field(default_factory=lambda: default_approvals_path())

    @classmethod
    def create(
        cls,
        settings: ProtectionSettings,
        *,
        entrypoint_dir: Path,
        invocation_dir: Path | None = None,
        library_roots: tuple[Path, ...] = (),
        bypass: bool = False,
        approval_handler: ApprovalHandler | None = None,
        approvals_path: Path | None = None,
    ) -> ProtectionContext:
        """Resolve built-in and configured roots for one entrypoint."""

        entrypoint = entrypoint_dir.expanduser().resolve()
        invocation = (invocation_dir or Path.cwd()).expanduser().resolve()
        effective = ProtectionSettings(enabled=False) if bypass else settings
        read_roots = _dedupe_paths(
            (
                entrypoint,
                invocation,
                _find_project_root(entrypoint),
                Path.home() / ".weavemark" / "promplets",
                *library_roots,
                *(
                    _expand_configured_root(value, entrypoint, invocation)
                    for value in effective.read_roots
                ),
            )
        )
        write_roots = _dedupe_paths(
            (
                entrypoint,
                invocation,
                invocation / "outputs",
                entrypoint / "outputs",
                *(
                    _expand_configured_root(value, entrypoint, invocation)
                    for value in effective.write_roots
                ),
            )
        )
        return cls(
            settings=effective,
            entrypoint_dir=entrypoint,
            invocation_dir=invocation,
            read_roots=read_roots,
            write_roots=write_roots,
            approval_handler=approval_handler,
            approvals_path=approvals_path or default_approvals_path(),
        )

    @property
    def enabled(self) -> bool:
        """Whether boundary enforcement is active."""

        return self.settings.enabled

    def authorize_read(
        self,
        path: Path,
        *,
        reason: str,
        declared: bool = True,
    ) -> Path:
        """Authorize one canonical local-file read."""

        resolved = path.expanduser().resolve()
        if not self.enabled:
            return resolved
        if _is_sensitive_path(resolved):
            self._enforce(
                self.settings.sensitive_files,
                ProtectionRequest(
                    capability="sensitive local-file read",
                    subject=str(resolved),
                    fingerprint=_file_fingerprint(resolved),
                    reason=reason,
                    danger=(
                        "Sensitive files may contain credentials, private keys, "
                        "tokens, repository internals, or personal data that could "
                        "be sent to a model provider."
                    ),
                    config_key="protections.sensitiveFiles",
                ),
            )
            return resolved
        if not declared:
            self._enforce(
                self.settings.dynamic_reads,
                ProtectionRequest(
                    capability="model-directed local-file read",
                    subject=str(resolved),
                    fingerprint=_file_fingerprint(resolved),
                    reason=reason,
                    danger=(
                        "The model requested a file that was not declared as a "
                        "resource by the promplet. Prompt injection could use this "
                        "to inspect unrelated project files."
                    ),
                    config_key="protections.dynamicReads",
                ),
            )
            return resolved
        if _is_within_any(resolved, self.read_roots):
            return resolved
        self._enforce(
            self.settings.dynamic_reads,
            ProtectionRequest(
                capability="declared local-file read",
                subject=str(resolved),
                fingerprint=_file_fingerprint(resolved),
                reason=reason,
                danger=(
                    "The path is outside the entrypoint, invocation directory, "
                    "promplet libraries, and configured read roots. Reading it may "
                    "disclose unrelated local data to the promplet or model."
                ),
                config_key="protections.dynamicReads / protections.readRoots",
            ),
        )
        return resolved

    def authorize_write(self, path: Path, *, reason: str) -> Path:
        """Authorize one canonical output write."""

        resolved = _resolve_write_target(path)
        if not self.enabled:
            return resolved
        if _is_within_any(resolved, self.write_roots):
            return resolved
        self._enforce(
            self.settings.writes_outside_roots,
            ProtectionRequest(
                capability="write outside configured roots",
                subject=str(resolved),
                fingerprint=_text_fingerprint(str(resolved)),
                reason=reason,
                danger=(
                    "Writing outside the entrypoint, invocation directory, "
                    "outputs folders, or configured write roots may overwrite "
                    "unrelated user files."
                ),
                config_key=("protections.writesOutsideRoots / protections.writeRoots"),
            ),
        )
        return resolved

    def authorize_python(
        self,
        reference: str,
        *,
        path: Path | None = None,
        reason: str,
    ) -> None:
        """Authorize executable Python machine or binding code."""

        if not self.enabled:
            return
        subject = str(path.expanduser().resolve()) if path is not None else reference
        fingerprint = (
            _file_fingerprint(path.expanduser().resolve())
            if path is not None
            else _text_fingerprint(reference)
        )
        self._enforce(
            self.settings.python_code,
            ProtectionRequest(
                capability="Python code execution",
                subject=subject,
                fingerprint=fingerprint,
                reason=reason,
                danger=(
                    "Importing a Python machine or binding executes code with the "
                    "same operating-system permissions and environment as WeaveMark. "
                    "Protected mode is not an OS sandbox."
                ),
                config_key="protections.pythonCode",
            ),
        )

    def authorize_remote_url(self, url: str, *, reason: str) -> str:
        """Validate a remote resource URL and its resolved network targets."""

        if not self.enabled:
            return url

        parsed = urllib.parse.urlsplit(url)
        scheme = parsed.scheme.lower()
        if scheme not in {"http", "https"} or not parsed.hostname:
            raise self._blocked(
                capability="remote resource fetch",
                subject=url,
                reason="Only absolute HTTP(S) URLs with a hostname are supported.",
                danger="Malformed or non-network URLs can cross unintended protocols.",
                config_key="protections.remoteHttps / protections.remoteHttp",
            )
        try:
            port = parsed.port
        except ValueError as exc:
            raise self._blocked(
                capability="remote resource fetch",
                subject=url,
                reason=f"The URL contains an invalid port: {exc}",
                danger="Malformed destinations cannot be checked against network policy.",
                config_key="protections.remoteHttps / protections.remoteHttp",
            ) from exc
        decision = (
            self.settings.remote_https
            if scheme == "https"
            else self.settings.remote_http
        )
        self._enforce(
            decision,
            ProtectionRequest(
                capability=f"remote {scheme.upper()} fetch",
                subject=url,
                fingerprint=_text_fingerprint(url),
                reason=reason,
                danger=(
                    "Remote resources disclose the request target and can return "
                    "malicious, oversized, or misleading content."
                ),
                config_key=(
                    "protections.remoteHttps"
                    if scheme == "https"
                    else "protections.remoteHttp"
                ),
            ),
        )
        addresses = _resolve_host_addresses(parsed.hostname, port, scheme)
        if any(_is_private_address(address) for address in addresses):
            self._enforce(
                self.settings.private_networks,
                ProtectionRequest(
                    capability="private-network resource fetch",
                    subject=f"{url} -> {', '.join(sorted(addresses))}",
                    fingerprint=_text_fingerprint(
                        f"{url}|{','.join(sorted(addresses))}"
                    ),
                    reason="The hostname resolves to a non-public network address.",
                    danger=(
                        "Private, loopback, link-local, and metadata endpoints can "
                        "expose local services or cloud credentials (SSRF)."
                    ),
                    config_key="protections.privateNetworks",
                ),
            )
        return url

    def authorize_process(
        self,
        command: Path,
        *,
        reason: str,
    ) -> None:
        """Authorize launching one external executable."""

        if not self.enabled:
            return
        resolved = command.expanduser().resolve()
        self._enforce(
            self.settings.external_process,
            ProtectionRequest(
                capability="external process execution",
                subject=str(resolved),
                fingerprint=_file_fingerprint(resolved),
                reason=reason,
                danger=(
                    "An external process runs with user privileges and may read, "
                    "write, access the network, or invoke additional tools. "
                    "Reduced environment inheritance is not an OS sandbox."
                ),
                config_key="protections.externalProcess",
            ),
        )

    def fetch_remote_bytes(
        self,
        url: str,
        *,
        reason: str,
        expected_content_prefix: str | None = None,
    ) -> bytes:
        """Fetch a bounded resource while revalidating every redirect."""

        if not self.enabled:
            with urllib.request.urlopen(url) as response:  # noqa: S310
                return bytes(response.read())
        opener = urllib.request.build_opener(_NoRedirectHandler())
        current = url
        for redirect_index in range(self.settings.max_redirects + 1):
            self.authorize_remote_url(current, reason=reason)
            request = urllib.request.Request(
                current,
                headers={"User-Agent": "WeaveMark/experimental-protected-fetch"},
            )
            try:
                response = opener.open(
                    request,
                    timeout=self.settings.download_timeout_seconds,
                )
            except urllib.error.HTTPError as exc:
                if exc.code not in {301, 302, 303, 307, 308}:
                    raise
                location = exc.headers.get("Location")
                if not location or redirect_index >= self.settings.max_redirects:
                    raise self._blocked(
                        capability="remote resource redirect",
                        subject=current,
                        reason="The redirect chain is missing a target or exceeds the limit.",
                        danger="Unbounded redirects can bypass target validation.",
                        config_key="protections.maxRedirects",
                    ) from exc
                current = urllib.parse.urljoin(current, location)
                continue
            with response:
                content_type = response.headers.get_content_type()
                if expected_content_prefix is not None and not content_type.startswith(
                    expected_content_prefix
                ):
                    raise self._blocked(
                        capability="remote resource content validation",
                        subject=current,
                        reason=f"Expected {expected_content_prefix}*, got {content_type}.",
                        danger="A remote endpoint may disguise active or unexpected content.",
                        config_key="protections.remoteHttps",
                    )
                length = response.headers.get("Content-Length")
                if (
                    length is not None
                    and int(length) > self.settings.max_download_bytes
                ):
                    raise self._blocked(
                        capability="remote resource download",
                        subject=current,
                        reason=f"Declared size {length} exceeds the configured limit.",
                        danger="Oversized downloads can exhaust memory or disk.",
                        config_key="protections.maxDownloadBytes",
                    )
                payload = bytes(response.read(self.settings.max_download_bytes + 1))
                if len(payload) > self.settings.max_download_bytes:
                    raise self._blocked(
                        capability="remote resource download",
                        subject=current,
                        reason="The response exceeded the configured byte limit.",
                        danger="Oversized or endless responses can exhaust resources.",
                        config_key="protections.maxDownloadBytes",
                    )
                if expected_content_prefix == "image/" and not _has_image_magic(
                    payload
                ):
                    raise self._blocked(
                        capability="remote image content validation",
                        subject=current,
                        reason="The response does not have a recognized image signature.",
                        danger=(
                            "Content-Type headers can lie; validating file signatures "
                            "prevents non-image payloads from entering image workflows."
                        ),
                        config_key="protections.remoteHttps",
                    )
                return payload
        raise AssertionError("redirect loop exhausted unexpectedly")

    def sanitized_subprocess_environment(
        self,
        source: Mapping[str, str] | None = None,
    ) -> dict[str, str]:
        """Return only explicitly allowed environment variables."""

        environment = os.environ if source is None else source
        if not self.enabled:
            return dict(environment)
        return {
            name: environment[name]
            for name in self.settings.subprocess_environment
            if name in environment
        }

    def _enforce(
        self,
        decision: ProtectionDecision,
        request: ProtectionRequest,
    ) -> None:
        if decision == "allow":
            return
        if decision == "deny":
            raise self._blocked_from_request(request, "The active policy denies it.")
        remembered = _read_approval(self.approvals_path, request)
        if remembered is True:
            return
        if remembered is False:
            raise self._blocked_from_request(
                request,
                "A remembered user decision denies this exact item.",
            )
        if self.approval_handler is None:
            raise self._blocked_from_request(
                request,
                "This operation requires interactive confirmation, but none is available.",
            )
        allowed = bool(self.approval_handler(request))
        _write_approval(self.approvals_path, request, allowed)
        if not allowed:
            raise self._blocked_from_request(request, "The user denied this operation.")

    @staticmethod
    def _blocked_from_request(
        request: ProtectionRequest,
        reason: str,
    ) -> ProtectionError:
        return ProtectionError(
            capability=request.capability,
            subject=request.subject,
            reason=reason,
            danger=request.danger,
            config_key=request.config_key,
        )

    @staticmethod
    def _blocked(**kwargs: str) -> ProtectionError:
        return ProtectionError(**kwargs)


def default_approvals_path() -> Path:
    """Return the user-level remembered-decision store."""

    return Path.home() / ".weavemark" / _APPROVALS_FILE


def protection_settings_from_config(
    value: object,
    *,
    source: str,
    errors: list[str],
) -> ProtectionSettings:
    """Parse one complete user/global protection configuration."""

    if value is None:
        return ProtectionSettings()
    if not isinstance(value, Mapping):
        errors.append(f"{source} protections must be a JSON object.")
        return ProtectionSettings()
    data = dict(value)
    return ProtectionSettings(
        enabled=_bool_value(data, "enabled", True, source, errors),
        read_roots=_string_tuple(data, "readRoots", source, errors),
        write_roots=_string_tuple(data, "writeRoots", source, errors),
        sensitive_files=_decision(data, "sensitiveFiles", "deny", source, errors),
        dynamic_reads=_decision(data, "dynamicReads", "confirm", source, errors),
        writes_outside_roots=_decision(
            data, "writesOutsideRoots", "confirm", source, errors
        ),
        python_code=_decision(data, "pythonCode", "confirm", source, errors),
        external_process=_decision(
            data,
            "externalProcess",
            "confirm",
            source,
            errors,
        ),
        remote_https=_decision(data, "remoteHttps", "allow", source, errors),
        remote_http=_decision(data, "remoteHttp", "deny", source, errors),
        private_networks=_decision(data, "privateNetworks", "deny", source, errors),
        max_download_bytes=_positive_int(
            data, "maxDownloadBytes", 20_000_000, source, errors
        ),
        download_timeout_seconds=_positive_float(
            data, "downloadTimeoutSeconds", 30.0, source, errors
        ),
        max_redirects=_nonnegative_int(data, "maxRedirects", 3, source, errors),
        subprocess_environment=_string_tuple(
            data,
            "subprocessEnvironment",
            source,
            errors,
            default=("PATH",),
        ),
    )


def tighten_protection_settings(
    current: ProtectionSettings,
    value: object,
    *,
    source: str,
    warnings: list[str],
    errors: list[str],
) -> ProtectionSettings:
    """Apply only monotonic project-level protection restrictions."""

    if value is None:
        return current
    parsed = protection_settings_from_config(value, source=source, errors=errors)
    if not isinstance(value, Mapping):
        return current
    data = dict(value)
    if data.get("enabled") is False and current.enabled:
        warnings.append(
            f"{source} cannot disable user/global WeaveMark protections; ignored."
        )
    ignored_grants = sorted(key for key in ("readRoots", "writeRoots") if key in data)
    if ignored_grants:
        warnings.append(
            f"{source} cannot grant protection roots ({', '.join(ignored_grants)}); "
            "configure them at user/global level."
        )

    def decision(
        key: str,
        current_value: ProtectionDecision,
        parsed_value: ProtectionDecision,
    ) -> ProtectionDecision:
        return _stricter(current_value, parsed_value) if key in data else current_value

    return ProtectionSettings(
        enabled=(
            current.enabled or parsed.enabled if "enabled" in data else current.enabled
        ),
        read_roots=current.read_roots,
        write_roots=current.write_roots,
        sensitive_files=decision(
            "sensitiveFiles",
            current.sensitive_files,
            parsed.sensitive_files,
        ),
        dynamic_reads=decision(
            "dynamicReads",
            current.dynamic_reads,
            parsed.dynamic_reads,
        ),
        writes_outside_roots=decision(
            "writesOutsideRoots",
            current.writes_outside_roots,
            parsed.writes_outside_roots,
        ),
        python_code=decision(
            "pythonCode",
            current.python_code,
            parsed.python_code,
        ),
        external_process=decision(
            "externalProcess",
            current.external_process,
            parsed.external_process,
        ),
        remote_https=decision(
            "remoteHttps",
            current.remote_https,
            parsed.remote_https,
        ),
        remote_http=decision(
            "remoteHttp",
            current.remote_http,
            parsed.remote_http,
        ),
        private_networks=decision(
            "privateNetworks",
            current.private_networks,
            parsed.private_networks,
        ),
        max_download_bytes=(
            min(current.max_download_bytes, parsed.max_download_bytes)
            if "maxDownloadBytes" in data
            else current.max_download_bytes
        ),
        download_timeout_seconds=(
            min(
                current.download_timeout_seconds,
                parsed.download_timeout_seconds,
            )
            if "downloadTimeoutSeconds" in data
            else current.download_timeout_seconds
        ),
        max_redirects=(
            min(current.max_redirects, parsed.max_redirects)
            if "maxRedirects" in data
            else current.max_redirects
        ),
        subprocess_environment=(
            tuple(
                item
                for item in current.subprocess_environment
                if item in parsed.subprocess_environment
            )
            if "subprocessEnvironment" in data
            else current.subprocess_environment
        ),
    )


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


def _read_approval(path: Path, request: ProtectionRequest) -> bool | None:
    data = _load_approvals(path)
    record = data.get("approvals", {}).get(_approval_key(request))
    if not isinstance(record, dict):
        return None
    if record.get("fingerprint") != request.fingerprint:
        return None
    allowed = record.get("allowed")
    return allowed if isinstance(allowed, bool) else None


def _write_approval(
    path: Path,
    request: ProtectionRequest,
    allowed: bool,
) -> None:
    data = _load_approvals(path)
    approvals = data.setdefault("approvals", {})
    approvals[_approval_key(request)] = {
        "allowed": allowed,
        "capability": request.capability,
        "subject": request.subject,
        "fingerprint": request.fingerprint,
        "decided_at": datetime.now(UTC).isoformat(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=path.parent,
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
        os.chmod(temporary, 0o600)
        temporary.replace(path)
        os.chmod(path, 0o600)
    finally:
        temporary.unlink(missing_ok=True)


def _load_approvals(path: Path) -> dict[str, Any]:
    try:
        if path.stat().st_size > _MAX_APPROVAL_FILE_BYTES:
            raise ValueError("approval store exceeds the maximum size")
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"version": 1, "approvals": {}}
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise ProtectionError(
            capability="protection approval loading",
            subject=str(path),
            reason=f"The approval store could not be read safely: {exc}",
            danger="Corrupt approvals must never silently grant capabilities.",
            config_key="~/.weavemark/protection-approvals.json",
        ) from exc
    if not isinstance(data, dict) or not isinstance(data.get("approvals", {}), dict):
        raise ProtectionError(
            capability="protection approval loading",
            subject=str(path),
            reason="The approval store has an invalid schema.",
            danger="Malformed approvals must never silently grant capabilities.",
            config_key="~/.weavemark/protection-approvals.json",
        )
    return data


def _approval_key(request: ProtectionRequest) -> str:
    return f"{request.capability}:{request.subject}"


def _file_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(str(path).encode())
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError:
        digest.update(b"<unreadable>")
    return digest.hexdigest()


def _text_fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _is_sensitive_path(path: Path) -> bool:
    lowered_parts = {part.casefold() for part in path.parts}
    name = path.name.casefold()
    return (
        bool(lowered_parts & _SENSITIVE_PARTS)
        or name in _SENSITIVE_NAMES
        or name.startswith(".env.")
        or path.suffix.casefold() in _SENSITIVE_SUFFIXES
    )


def _is_within_any(path: Path, roots: tuple[Path, ...]) -> bool:
    for root in roots:
        try:
            path.relative_to(root)
        except ValueError:
            continue
        return True
    return False


def _resolve_write_target(path: Path) -> Path:
    return path.expanduser().resolve()


def _dedupe_paths(paths: tuple[Path, ...]) -> tuple[Path, ...]:
    result: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        resolved = path.expanduser().resolve()
        if resolved not in seen:
            seen.add(resolved)
            result.append(resolved)
    return tuple(result)


def _expand_configured_root(
    value: str,
    entrypoint: Path,
    invocation: Path,
) -> Path:
    aliases = {
        "entrypoint": entrypoint,
        "cwd": invocation,
        "outputs": invocation / "outputs",
    }
    return aliases.get(value, Path(value).expanduser())


def _find_project_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if any((candidate / marker).exists() for marker in _PROJECT_ROOT_MARKERS):
            return candidate
    return start


def _resolve_host_addresses(host: str, port: int | None, scheme: str) -> set[str]:
    service = port or (443 if scheme == "https" else 80)
    try:
        return {
            str(item[4][0])
            for item in socket.getaddrinfo(
                host,
                service,
                type=socket.SOCK_STREAM,
            )
        }
    except socket.gaierror as exc:
        raise ProtectionError(
            capability="remote resource DNS resolution",
            subject=host,
            reason=f"The hostname could not be resolved: {exc}",
            danger="Unresolved destinations cannot be checked against network policy.",
            config_key="protections.privateNetworks",
        ) from exc


def _is_private_address(value: str) -> bool:
    address = ipaddress.ip_address(value)
    return not address.is_global


def _has_image_magic(payload: bytes) -> bool:
    return (
        payload.startswith(b"\x89PNG\r\n\x1a\n")
        or payload.startswith(b"\xff\xd8\xff")
        or payload.startswith((b"GIF87a", b"GIF89a"))
        or payload.startswith(b"BM")
        or (
            len(payload) >= 12
            and payload.startswith(b"RIFF")
            and payload[8:12] == b"WEBP"
        )
    )


def _decision(
    data: dict[str, Any],
    key: str,
    default: ProtectionDecision,
    source: str,
    errors: list[str],
) -> ProtectionDecision:
    value = data.get(key, default)
    if value not in _DECISIONS:
        errors.append(f"{source} protections.{key} must be allow, confirm, or deny.")
        return default
    return cast(ProtectionDecision, value)


def _bool_value(
    data: dict[str, Any],
    key: str,
    default: bool,
    source: str,
    errors: list[str],
) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        errors.append(f"{source} protections.{key} must be boolean.")
        return default
    return value


def _string_tuple(
    data: dict[str, Any],
    key: str,
    source: str,
    errors: list[str],
    *,
    default: tuple[str, ...] = (),
) -> tuple[str, ...]:
    value = data.get(key, default)
    if not isinstance(value, list | tuple) or not all(
        isinstance(item, str) and item for item in value
    ):
        errors.append(f"{source} protections.{key} must be an array of strings.")
        return default
    return tuple(value)


def _positive_int(
    data: dict[str, Any],
    key: str,
    default: int,
    source: str,
    errors: list[str],
) -> int:
    value = data.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        errors.append(f"{source} protections.{key} must be a positive integer.")
        return default
    return int(value)


def _nonnegative_int(
    data: dict[str, Any],
    key: str,
    default: int,
    source: str,
    errors: list[str],
) -> int:
    value = data.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        errors.append(f"{source} protections.{key} must be a non-negative integer.")
        return default
    return int(value)


def _positive_float(
    data: dict[str, Any],
    key: str,
    default: float,
    source: str,
    errors: list[str],
) -> float:
    value = data.get(key, default)
    if (
        isinstance(value, bool)
        or not isinstance(value, int | float)
        or float(value) <= 0
    ):
        errors.append(f"{source} protections.{key} must be a positive number.")
        return default
    return float(value)


def _stricter(
    first: ProtectionDecision,
    second: ProtectionDecision,
) -> ProtectionDecision:
    order = {"allow": 0, "confirm": 1, "deny": 2}
    return first if order[first] >= order[second] else second


__all__ = [
    "ApprovalHandler",
    "ProtectionContext",
    "ProtectionDecision",
    "ProtectionError",
    "ProtectionRequest",
    "ProtectionSettings",
    "default_approvals_path",
    "protection_settings_from_config",
    "tighten_protection_settings",
]
