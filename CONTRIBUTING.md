# Contributing to WeaveMark

Thank you for looking. Please read this short page first — the kind of
contribution that helps most right now is probably not the one you expect.

## Where the project is

**WeaveMark is in a research stage and the language is still evolving.** The
notation, the Processor's behavior, and the public interfaces all still change
between releases. That has a direct consequence for contributions: a pull
request against the core implementation may conflict with a language decision
that is still being worked out, and I may have to decline it for reasons that
have nothing to do with its quality.

So please **open an issue before writing code** for the compiler, the engines,
or the CLI. Let us agree on the shape first.

## What I am actively looking for

**Promplets** — for the reusable library and for the examples. This is where
outside contributions compound, because the language is only as useful as the
material written in it.

**Promplets from domain experts are especially encouraged.** If you know how
work is really done in medicine, law, teaching, accounting, engineering,
scientific writing, translation, or any other practice, you know constraints and
quality criteria that I do not. Encoding those into a reusable promplet is
genuinely valuable and does not require you to understand the compiler at all.

Good places to add material:

| Location | For |
|---|---|
| [`promplets/stdlib/`](promplets/stdlib) | General building blocks usable across domains |
| [`promplets/domains/`](promplets/domains) | Domain-specific reusable modules |
| [`promplets/catalog/`](promplets/catalog) | Complete, standalone or executable examples |

Start from [the tutorial](https://paulosalem.github.io/weavemark/docs/tutorial.html)
and read a few neighbours in the directory you are adding to; matching the local
conventions matters more than any rule I could write here.

## What makes a promplet contribution easy to accept

- **It is genuinely reusable.** A module should say something true for a whole
  class of tasks, not encode one person's single request.
- **It compiles.** Run `weavemark path/to/your.weavemark.md` and check the
  result reads the way you intended.
- **It explains itself.** A short comment on why a constraint exists is worth
  more than the constraint alone, especially for domain rules a reader may not
  know.

Please do not commit large generated media. Full-resolution artifacts live in
Git LFS; if your example produces heavy output, include the source and a small
representative sample.

## Bug reports

Bug reports are welcome and need no prior discussion. Include the promplet (or a
reduced version of it), the exact command, the WeaveMark version
(`weavemark --version`), and what you expected instead. A reproducible case is
worth far more than a description.

For security issues, follow [SECURITY.md](SECURITY.md) instead — do not open a
public issue.

## Development setup

```bash
pip install -e ".[dev]"
pytest -q
```

Architecture notes, the reference-authority hierarchy, and the editor extension
are documented in [docs/development.md](docs/development.md). Note that
`src/weavemark/prompts/weavemark.system.md` is the canonical definition of the
language; changes there affect everything downstream and always warrant an issue
first.

## License

Contributions are accepted under the [MIT License](LICENSE) that covers the
project.
