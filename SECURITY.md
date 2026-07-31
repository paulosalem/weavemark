# Security policy

## Reporting a vulnerability

Report suspected vulnerabilities privately to **paulosalem@paulosalem.com**.
Please include what you observed, the promplet or command that triggered it, and
the WeaveMark version (`weavemark --version`). Do not open a public issue for an
unfixed vulnerability.

WeaveMark is an experimental single-maintainer project, so there is no formal
response-time commitment. I will acknowledge reports and, when a fix ships, credit
you in the changelog unless you prefer otherwise.

## The threat model you should assume

WeaveMark runs prompts that can read files, call tools, download data, execute
Python companion implementations, and launch external processes. The most
important thing to understand is this:

> **Protected mode is not an operating-system sandbox.** Python modules and
> approved external programs run with your user account's permissions.
> **Do not run promplets you do not trust, even with protections enabled.**

A promplet is executable material. Treat one from an untrusted source exactly as
you would treat an untrusted shell script.

## What protections do

Protections are **enabled by default** and are designed to reduce the chance
that a malicious or merely surprising promplet reads unrelated files, overwrites
unrelated outputs, reaches private network services, executes code, launches a
process, or downloads an oversized payload.

- **Read and write roots.** Reads are confined to the entrypoint promplet
  directory, the invocation directory, the discovered project root, configured
  library roots, and `~/.weavemark/promplets`. Writes are confined to the
  entrypoint directory, the invocation directory, and their `outputs/` folders.
  Paths are canonicalized, so a symlink cannot silently escape a root.
- **Sensitive files stay denied.** `.env`, private keys, credential stores,
  `.ssh`, and `.aws` are refused even when they sit inside a read root.
- **Confirmation before dangerous operations.** Dynamic reads, writes outside
  roots, Python execution, and external processes prompt with a warning panel
  that defaults to **No**. Decisions are recorded per exact item in
  `~/.weavemark/protection-approvals.json`, and a changed Python file must be
  approved again.
- **Network limits.** HTTPS is allowed, plain HTTP and private-network addresses
  are denied, and downloads are bounded by size, timeout, and redirect count.
- **Non-interactive runs fail closed.** Batch mode and API calls cannot ask, so
  an unapproved confirmation-required operation is blocked rather than assumed.
- **Projects can only tighten.** A project-level `weavemark.json` may harden
  policy but cannot disable protections, grant roots, raise download limits, or
  add inherited environment variables. Only user or system configuration can
  loosen them.

`--no-protections` disables these checks for a single invocation. Use it only on
promplets you have read and trust.

Full configuration reference:
[Experimental protections](docs/usage-reference.md#experimental-protections).

## Secrets

WeaveMark reads provider credentials from the environment (for example
`OPENAI_API_KEY`); they are not part of promplet source or of the compiled
prompt it produces. Protections additionally deny reads of `.env` files, private
keys, and credential stores, so a promplet cannot pull them into its own context.
Prompt and response bodies are not written to logs by default.

Effect and tool outputs, however, become part of your artifacts by design. If a
tool you bind returns a credential, that credential will be in the run's output.
Review what your companion implementations return before committing artifacts.
If you find a credential in a generated artifact that you did not put there,
please report it.

## Supported versions

Only the latest release on [PyPI](https://pypi.org/project/weavemark/) receives
fixes. WeaveMark is pre-1.0 and its interfaces are still changing.
