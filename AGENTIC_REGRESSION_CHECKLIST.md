# Agentic Regression Checklist

This document records recurring failure modes discovered while developing
WeaveMark, its examples, documentation, generated applications, website, and
release process. It is a mandatory engineering rubric, not a historical report.

## How agents must use this checklist

For every non-trivial change or audit:

1. Read all 60 rubrics before changing files or finalizing an audit.
2. Determine which rubrics the work could affect. Do not consider only the file
   being edited; include downstream documentation, examples, generated
   artifacts, package contents, website surfaces, and release behavior.
3. Validate every applicable rubric with concrete evidence. Reading the code is
   not sufficient when a command, test, generated artifact, or visual result can
   be inspected.
4. Classify each rubric internally as `PASS`, `FAIL`, `NOT APPLICABLE`, or
   `DEFERRED`. `NOT APPLICABLE` requires a concrete reason. `DEFERRED` requires
   an explicit user decision or a documented blocker.
5. Report failures and deferred items. Do not describe the work as complete
   while an applicable rubric remains unverified.

A change is non-trivial when it affects behavior, public APIs, language
semantics, processor behavior, configuration, the CLI, examples, generated
artifacts, documentation claims, UI, packaging, CI, or release state. Purely
local typo corrections may use judgment, but must still consider whether the
same text is duplicated elsewhere.

## How to maintain this checklist

Update this file in the same change whenever a fix reveals a new reusable
failure mode, a better diagnostic procedure, a stronger correction, or a more
precise pass condition. Merge genuinely overlapping rubrics rather than adding
duplicates. Do not weaken or delete a rubric merely because the current code
passes it.

When updating a rubric:

- describe the underlying class of failure, not only one historical symptom;
- name the surfaces and scenarios an agent must inspect;
- prescribe correction at the authoritative layer;
- require observable pass evidence;
- update `AGENTS.md` if the operating protocol itself changes.

# A. Language semantics and compilation

## 1. Canonical contract synchronization

- **Risk:** The system prompt, runtime models, EBNF, parser, manuals, and
  examples may accept or describe different forms of the same directive.
- **Check:** Compare directive names, parameters, defaults, required fields,
  nesting, aliases, and lifecycle meaning across every authoritative surface.
- **Do:** Change the canonical runtime or language contract first, then update
  every projection. Do not preserve undocumented compatibility aliases.
- **Pass evidence:** Contract-parity tests pass, every documented form parses,
  and repository searches find no stale syntax.

## 2. Explicit source-of-truth hierarchy

- **Risk:** Agents may correct runtime behavior from stale prose or update
  documentation without updating the actual language contract.
- **Check:** Identify the canonical language prompt, runtime schemas,
  parser/controller contracts, EBNF, and human references.
- **Do:** Follow the authority order in `AGENTS.md`. A language change must list
  and update every dependent surface.
- **Pass evidence:** A future agent can determine unambiguously where a semantic
  change begins and which artifacts must follow.

## 3. Honest compilation model

- **Risk:** WeaveMark may be portrayed as deterministic when semantic
  composition is substantially LLM-driven.
- **Check:** Search for claims involving "compiler", "deterministic",
  "reproducible", "exact", and "structural".
- **Do:** Explain which phases are deterministic and which depend on model
  judgment. Cached replay improves repeatability but does not make fresh
  compilation deterministic.
- **Pass evidence:** README, site, manuals, and CLI help make the distinction
  consistently.

## 4. Compilation versus execution

- **Risk:** Users and agents may confuse producing a prompt with running it or
  packaging its result.
- **Check:** Trace compile-only, execute, package, save, replay, and `--open`
  paths independently.
- **Do:** Give each stage explicit inputs, outputs, errors, telemetry, and CLI
  semantics. Avoid phrases such as "executable plan" if execution occurs.
- **Pass evidence:** Tests prove each stage separately and at least one
  end-to-end workflow proves their composition.

## 5. Directive schema accuracy

- **Risk:** Documentation or generated examples may use invalid parameters,
  obsolete names, unsupported inline forms, or incorrect indentation.
- **Check:** Extract every directive example from public Markdown and HTML and
  parse it with the current processor.
- **Do:** Correct the source example rather than weakening the parser. Remove
  obsolete aliases unless intentionally part of the language.
- **Pass evidence:** All examples parse and scans report the expected semantic
  structure.

## 6. Stage-aware variable discovery

- **Risk:** `--scan` may expose macro parameters, generated outputs, or
  execution-stage placeholders as user inputs, or miss genuinely unresolved
  inputs.
- **Check:** Test entrypoints, definition modules, nested refinement, macro
  bodies, prompts, tool outputs, and engine-produced variables.
- **Do:** Assign every symbol an origin, scope, stage, and producer. Discovery
  should report only values required from the caller.
- **Pass evidence:** Targeted tests cover both false-positive and false-negative
  cases.

## 7. Correct refinement inheritance

- **Risk:** Variables supplied while refining another promplet may incorrectly
  remain free, disappear, or collide with local variables.
- **Check:** Exercise path and module refinement with zero, partial, and complete
  bindings, including nested refinement.
- **Do:** Resolve bindings before propagating the refined promplet's remaining
  input surface. Detect conflicting or duplicate assignments explicitly.
- **Pass evidence:** Only unresolved variables reach the outer promplet, with
  stable ordering and provenance.

## 8. Canonical macro and binding metadata

- **Risk:** LLM compilation may emit semantically equivalent but structurally
  different metadata that later runtime stages cannot execute.
- **Check:** Inspect accepted compiler response shapes for bindings, symbols,
  arguments, dependencies, and tool names.
- **Do:** Normalize accepted variants at one boundary, reject unknown shapes
  clearly, and expose one internal representation downstream.
- **Pass evidence:** Regression fixtures for every supported wire shape produce
  identical runtime objects.

## 9. Precise reference semantics

- **Risk:** `@file`, `@reference`, `keep:true`, and `keep:false` may be
  interpreted as inline substitution, appended context, or compile-only context
  inconsistently.
- **Check:** Test placement, recursion, ordering, metadata, path resolution,
  duplicate references, and missing files.
- **Do:** Implement the documented semantics explicitly. Retained references
  should appear in a clearly separated appendix; compile-only context must not
  leak into final output.
- **Pass evidence:** Golden tests prove exact compiled results for each form.

## 10. Robust structured compilation

- **Risk:** Duplicate JSON keys, nulls, truncated output, invalid enums, or minor
  schema mistakes may destroy otherwise recoverable compilations.
- **Check:** Maintain malformed-response fixtures based on real failures.
- **Do:** Detect rather than silently accept duplicate keys. Permit one bounded
  corrective request for protocol or schema failures, then surface the original
  and repair failures together.
- **Pass evidence:** Recoverable fixtures succeed; unrecoverable ones fail
  explicitly without loops or silent defaults.

# B. Runtime, CLI, safety, and extensibility

## 11. Unified public exceptions

- **Risk:** Multiple unrelated `WeaveMarkError` classes prevent callers from
  catching documented failures consistently.
- **Check:** Inventory all exception definitions, exports, wrapping points, and
  CLI conversions.
- **Do:** Establish one public base hierarchy with meaningful subclasses.
  Preserve causal chaining and avoid broad exception swallowing.
- **Pass evidence:** Public API tests catch parser, compilation, execution,
  packaging, and protection errors through the documented base.

## 12. Uniform engine construction

- **Risk:** Custom engines may not receive the LLM client, protections,
  observers, configuration, or cancellation behavior provided to built-ins.
- **Check:** Compare built-in registry construction with dotted-path or plugin
  engine loading.
- **Do:** Define one explicit factory protocol or constructor contract and
  validate it at load time.
- **Pass evidence:** A test custom engine receives the same runtime services and
  behaves like a built-in engine.

## 13. Binding cache invalidation

- **Risk:** Editing a bound Python file may have no effect until the process
  restarts because modules are cached by path only.
- **Check:** Load a binding, modify its source, and invoke it again in the same
  process.
- **Do:** Incorporate a content hash or reliable file identity into loading, or
  implement explicit reload semantics.
- **Pass evidence:** The second invocation uses the changed implementation
  without cross-run contamination.

## 14. Coherent trust model

- **Risk:** Reads, writes, code loading, tools, network effects, and browser
  actions may execute without clear boundaries.
- **Check:** Enumerate every side effect and entry path, including defaults
  supplied by imported modules.
- **Do:** Define protected and trusted modes, allowed roots, confirmation rules,
  persistent grants, denials, and an explicit bypass.
- **Pass evidence:** Tests prove allow, deny, prompt, remembered approval, and
  bypass behavior for each effect category.

## 15. Protected-mode example compatibility

- **Risk:** Shipped examples may work only when users disable protections,
  undermining the default security model.
- **Check:** Run every maintained example under fresh default configuration
  without preexisting grants.
- **Do:** Keep required access within documented roots and request narrow
  approvals only when genuinely necessary.
- **Pass evidence:** The example matrix records required grants and confirms no
  blanket bypass is needed.

## 16. Executable CLI help

- **Risk:** Copy-pasted help commands may reference removed promplets,
  nonexistent paths, stale flags, or impossible combinations.
- **Check:** Extract commands from root and subcommand help.
- **Do:** Use current maintained examples and test the commands from a clean
  installation context.
- **Pass evidence:** Every help example exits as documented and produces the
  promised output type.

## 17. Correct CLI process contract

- **Risk:** Progress may pollute stdout, errors may return zero, or successful
  output may be hidden in diagnostics.
- **Check:** Capture stdout, stderr, and exit code for success, validation
  failure, provider failure, protection denial, and replay.
- **Do:** Reserve stdout for primary machine-consumable results; send status and
  diagnostics to stderr.
- **Pass evidence:** Shell-level tests verify exact channel and exit-code
  behavior.

## 18. Clean missing-provider behavior

- **Risk:** No-key workflows may emit repeated LiteLLM banners or appear
  successful despite doing nothing useful.
- **Check:** Run provider-dependent commands with credentials intentionally
  absent.
- **Do:** Fail once with a concise WeaveMark-owned explanation, required
  environment information, and any available offline alternative.
- **Pass evidence:** No third-party spam appears and the exit status is nonzero.

## 19. Fast lightweight commands

- **Risk:** Simple commands may take several seconds and import hundreds of
  megabytes of dependencies.
- **Check:** Measure cold `--version`, `--help`, `--scan`, and library listing;
  profile import chains.
- **Do:** Lazy-load LLM, UI, provider, and heavy runtime dependencies. Consider
  optional extras where justified.
- **Pass evidence:** Recorded startup budgets are met on a clean environment and
  guarded by performance smoke tests.

## 20. Configurable privacy-conscious logging

- **Risk:** Logs may leak secrets, binary data, absolute paths, or sensitive
  variables, or omit too much to debug failures.
- **Check:** Inspect logs from representative compilation, execution, tool, and
  packaging runs.
- **Do:** Provide granular categories and redaction. Default to useful textual
  context while excluding secrets and binary payloads.
- **Pass evidence:** Privacy tests find no forbidden material, while a failed run
  remains diagnosable.

# C. Replay, caching, provenance, and artifacts

## 21. Behavioral replay fidelity

- **Risk:** Replay may only rehydrate compiled Markdown rather than reproduce
  execution, packaging, and final products.
- **Check:** Compare original and replay lifecycle events for compile-only and
  executable examples.
- **Do:** Record enough structured state to replay the original public behavior
  without new provider calls.
- **Pass evidence:** Replay produces the same artifact roles and final
  user-visible outcome as the original run.

## 22. Correct `--open` target

- **Risk:** `--open` may select an intermediate prompt instead of the final HTML,
  PDF, image, or application.
- **Check:** Test workflows with multiple artifacts and multiple packaging
  stages.
- **Do:** Record artifact roles such as intermediate, execution output, package,
  and primary final. Open only the declared primary final artifact unless
  explicitly overridden.
- **Pass evidence:** The Market Snapshot replay opens its final HTML report, not
  draft Markdown.

## 23. Complete replay telemetry

- **Risk:** Replay statistics may show replay activity while omitting the
  original run's real cost and token usage.
- **Check:** Compare original verbose statistics with replay output.
- **Do:** Preserve original model, call count, input, output, and cached tokens,
  latency, provider cost, tool calls, and output sizes.
- **Pass evidence:** Replay labels historical telemetry clearly and values match
  the recorded manifest.

## 24. Complete provenance manifests

- **Risk:** An artifact may exist without enough information to explain how it
  was produced.
- **Check:** Inspect whether manifests include source identity, variables, model
  and settings, transformations, tools, outputs, timestamps, cost, and lineage.
- **Do:** Keep provenance optional but structurally complete when enabled.
- **Pass evidence:** A reviewer can trace each final artifact to its source files
  and runtime decisions.

## 25. Sound cache semantics

- **Risk:** A changed source, variable, model, configuration, or tool may
  incorrectly reuse an old response.
- **Check:** Enumerate every behavior-affecting input and mutate each
  independently.
- **Do:** Build cache keys from normalized content and settings, document scope
  and expiration, and distinguish provider-side from local caching.
- **Pass evidence:** Relevant mutations miss the cache; irrelevant filesystem
  changes do not.

## 26. Incremental artifact persistence

- **Risk:** A later failure may discard valuable outputs already produced.
- **Check:** Force failures after individual emit or package stages.
- **Do:** Write artifacts atomically as soon as valid, register them
  incrementally, and preserve partial-run status.
- **Pass evidence:** Earlier artifacts survive and the manifest identifies the
  run as partial rather than complete.

## 27. Content-preserving normalization

- **Risk:** Cleanup may add a final newline, change blank lines, or otherwise
  violate exact persisted-content expectations.
- **Check:** Test files with and without terminal newlines, trailing spaces,
  empty content, and binary-adjacent boundaries.
- **Do:** Normalize only explicitly targeted whitespace.
- **Pass evidence:** Golden byte comparisons prove unrelated content remains
  unchanged.

## 28. Portable, sanitized artifacts

- **Risk:** Generated JSON, HTML, transcripts, or manifests may expose private
  workspace names and local absolute paths.
- **Check:** Scan all committed and Pages-published outputs for home paths,
  cloud-storage paths, secrets, and private project names.
- **Do:** Serialize logical identifiers or relative paths; sanitize recordings
  before publication.
- **Pass evidence:** Repository privacy checks and manual artifact inspection are
  clean.

# D. Library, catalog, examples, and generated applications

## 29. Explicit packaging contract

- **Risk:** Packaging may produce an intermediate format or interpret a
  parameter called `template` as something it is not.
- **Check:** Inspect instruction sources, body semantics, `from`, output
  extension, MIME type, and final role.
- **Do:** Use accurate terms such as packaging instructions and define
  precedence when multiple instruction sources exist.
- **Pass evidence:** Tests confirm the intended final format and artifact role.

## 30. Predictable library namespace

- **Risk:** Built-in and personal promplets may shadow one another silently or
  require inconsistent addressing.
- **Check:** Test built-in names, personal names, paths, collisions, missing
  targets, and duplicate module declarations.
- **Do:** Define explicit roots and resolution precedence with diagnostic
  provenance.
- **Pass evidence:** Resolution tests show exactly which source was selected and
  why.

## 31. Repository/package catalog parity

- **Risk:** GitHub and the website may advertise promplets absent from the
  released wheel.
- **Check:** Build wheel and sdist, inspect their contents, install in a clean
  environment, and list the library.
- **Do:** Package catalog resources explicitly and test against the maintained
  repository inventory.
- **Pass evidence:** Clean PyPI-style installation exposes every advertised
  bundled promplet and replay.

## 32. Quality density over quantity

- **Risk:** A large catalog can obscure flagship work and reduce confidence
  through weak examples.
- **Check:** Score each promplet for distinctiveness, correctness, realism,
  output quality, maintenance status, reuse, and user appeal.
- **Do:** Keep only strong maintained items in the primary catalog; move studies
  and experiments to clearly secondary locations.
- **Pass evidence:** Every catalog item has an owner, purpose, validation path,
  and maintained-output expectation.

## 33. Documentation examples backed by real sources

- **Risk:** Attractive snippets may never have been parsed or executed.
- **Check:** Map each public snippet to a canonical source file and identify
  intentional abridgements.
- **Do:** Generate snippets where practical or test them as extracted fragments.
- **Pass evidence:** Each snippet has a source link and passes syntax and
  semantic validation.

## 34. Derived-artifact synchronization

- **Risk:** Generated apps, screenshots, replay bundles, and tutorials may
  reflect different promplet revisions.
- **Check:** Compare source hashes or regeneration metadata across derived
  outputs.
- **Do:** Provide one regeneration workflow and a manifest connecting all
  products.
- **Pass evidence:** Drift tests fail when a source changes without refreshing
  maintained derivatives.

## 35. Specification versus meta-specification

- **Risk:** A promplet intended for a coding agent may ask it to return another
  specification rather than implement the described product.
- **Check:** Search software promplets for instructions to write, create, return,
  or output a specification.
- **Do:** Express architecture, behavior, constraints, and acceptance criteria
  directly. Use meta-specification only when explicitly intended.
- **Pass evidence:** Compiled output is directly actionable by the target agent.

## 36. WeaveMark owns the orchestration

- **Risk:** A supposedly WeaveMark-native example may rely on a Python runner for
  summarization, memory, branching, or workflow control.
- **Check:** Trace responsibility across the promplet, bindings, shell scripts,
  and companion code.
- **Do:** Keep subjective transformations in WeaveMark; reserve Python for
  deterministic external capabilities.
- **Pass evidence:** The documented entrypoint is a normal WeaveMark command and
  produces the complete workflow.

## 37. Realistic grounding

- **Risk:** Reports may imply full-source research when they received only
  search-result snippets.
- **Check:** Trace every factual claim to tool output, user input, or model
  inference.
- **Do:** Label evidence types and require uncertainty where source depth is
  limited.
- **Pass evidence:** Final artifacts contain no stronger sourcing claim than the
  available material supports.

## 38. Feed UX discoveries back into specifications

- **Risk:** Generated code may be patched manually while the source promplet
  continues reproducing the defect.
- **Check:** For every generated-app fix, locate the missing or ambiguous source
  requirement.
- **Do:** Update the promplet first, regenerate, and retain direct code patches
  only when generation cannot express the correction.
- **Pass evidence:** A fresh generation contains the fix without manual
  intervention.

## 39. Provider-valid configuration

- **Risk:** Example sidecars may contain unsupported settings or redundant
  divisions between model configuration and variables.
- **Check:** Validate every shipped configuration against the selected provider
  and model and document each file's purpose.
- **Do:** Remove unsupported or legacy settings and consolidate files where
  separation adds no value.
- **Pass evidence:** Every maintained configuration loads without provider
  warnings.

## 40. Model migration gate

- **Risk:** Changing the default model after one successful run may break other
  examples or degrade their quality.
- **Check:** Run the complete maintained matrix, including long, tool-using,
  structured-output, and refinement-heavy cases.
- **Do:** Compare correctness, output quality, latency, tokens, and cost before
  changing defaults or public claims.
- **Pass evidence:** Results are recorded and all failures are resolved or
  explicitly excluded before migration.

# E. Documentation and communication

## 41. Atomic renaming

- **Risk:** Old names, extensions, commands, links, or package identifiers may
  survive a project rename.
- **Check:** Search case variants, abbreviations, filenames, URLs, metadata,
  generated outputs, and release workflows.
- **Do:** Perform one coordinated migration without hidden aliases unless
  compatibility is explicitly required.
- **Pass evidence:** Only intentional historical mentions of the old name
  remain.

## 42. Terminological precision

- **Risk:** Readers may not know whether "WeaveMark" means the language,
  processor, ecosystem, or artifact.
- **Check:** Review first definitions and recurring nouns across public
  surfaces.
- **Do:** Define language, processor, promplet, compiler, runtime, execution
  engine, package, replay, and artifact once and use them consistently.
- **Pass evidence:** A terminology search finds no contradictory usages.

## 43. Cross-surface synchronization

- **Risk:** README and website FAQs, model recommendations, safety explanations,
  or quick starts may diverge.
- **Check:** Inventory repeated information and compare exact claims.
- **Do:** Establish a canonical source or explicit synchronization test. Prefer
  the clearest concise answer.
- **Pass evidence:** Shared questions and facts agree across all public
  surfaces.

## 44. Self-contained technical references

- **Risk:** Users may need to read marketing pages to learn configuration,
  library roots, protections, CLI behavior, or language semantics.
- **Check:** Follow the manuals as a new user in a clean environment.
- **Do:** Repeat necessary information rather than merely linking elsewhere;
  keep the processor and language references dry and operational.
- **Pass evidence:** Setup and representative use can be completed using the
  manuals alone.

## 45. Portable, validated links

- **Risk:** A link may work on GitHub Pages but fail locally, in README, or from
  a nested tutorial.
- **Check:** Validate relative bases, anchors, case sensitivity, images, source
  links, and local-demo assumptions.
- **Do:** Use canonical public URLs where context varies; use `?plain=1` when
  linking to readable WeaveMark sources on GitHub.
- **Pass evidence:** Automated link checks plus local and deployed smoke tests
  pass.

## 46. Derived factual claims

- **Risk:** Statements such as engine counts, fragment counts, or supported
  language versions become stale.
- **Check:** Search prose for counts, versions, model names, and compatibility
  claims.
- **Do:** Generate facts from registries and manifests or assert them in tests.
- **Pass evidence:** Changing the underlying inventory causes a test or
  generated-document update.

## 47. Sober related-work comparisons

- **Risk:** The comparison may omit important projects, misclassify
  capabilities, or sound superior and defensive.
- **Check:** Verify each project from primary sources, including previously
  cited "promptlet" work.
- **Do:** Separate fact from interpretation, include links, state comparison
  dimensions clearly, and avoid unsupported exclusivity claims.
- **Pass evidence:** Every matrix cell is sourced or marked unknown, with no
  unresolved placeholders.

## 48. External-ready copy

- **Risk:** Public pages may expose internal instructions, template variables,
  defensive language, or excessive jokes.
- **Check:** Scan for braces, TODOs, internal audiences, temporary notes, private
  initiatives, and unsupported claims.
- **Do:** Preserve personality only where it does not obscure technical answers.
- **Pass evidence:** Placeholder and internal-language checks pass, and a fresh
  reader review finds no unexplained context.

# F. Website and visual UX

## 49. Durable homepage over launch-specific clutter

- **Risk:** Optimizing for one Hacker News post may turn the permanent homepage
  into a long argumentative landing page.
- **Check:** Evaluate whether the page still explains the project naturally
  without launch context.
- **Do:** Keep one concise value proposition, one core mechanism proof,
  representative outcomes, and links to deeper material.
- **Pass evidence:** A first-time reader can explain WeaveMark after the first
  one or two viewports.

## 50. Unambiguous replay messaging

- **Risk:** "No API key" beside a replay command may imply a free fresh
  execution.
- **Check:** Review every replay CTA, hero command, README example, and CLI
  message.
- **Do:** Label replay as a recorded prior run and explain separately how live
  execution works.
- **Pass evidence:** User testing shows readers distinguish replay from fresh
  compilation and execution.

## 51. Responsive navigation

- **Risk:** Main and tutorial navigation may overflow horizontally without an
  obvious affordance.
- **Check:** Inspect all navigation at narrow mobile, compact desktop, zoomed,
  and long-label states.
- **Do:** Use collapsible menus or another platform-appropriate compact
  treatment; preserve current-page orientation.
- **Pass evidence:** Every destination is discoverable without unexplained
  horizontal scrolling.

## 52. Disciplined spatial composition

- **Risk:** Successive additions may create excessive top whitespace, crowded
  heroes, clipping, uneven cards, or nested scroll panels.
- **Check:** Capture standard-width screenshots after material changes and
  compare against the last accepted design.
- **Do:** Fix hierarchy and layout structurally rather than stacking local CSS
  exceptions.
- **Pass evidence:** Desktop, tablet, and mobile screenshots show no overflow,
  wasted major regions, or competing focal points.

## 53. Consistent visual language

- **Risk:** New command blocks or cards may use unrelated syntax colors, borders,
  icons, or spacing.
- **Check:** Compare components with the established hero and design tokens.
- **Do:** Reuse shared classes and tokens; apply color semantically and maintain
  accessible contrast.
- **Pass evidence:** Automated contrast checks pass and visual review finds no
  one-off styling systems.

## 54. No obstruction before value

- **Risk:** Analytics consent, banners, or overlays may cover the install command
  and primary action.
- **Check:** Inspect the first visit with empty storage on mobile and desktop.
- **Do:** Remove unnecessary analytics or defer unobtrusive consent until primary
  content is usable.
- **Pass evidence:** First-load screenshots show all essential actions
  unobstructed.

# G. Release and repository integrity

## 55. Clean reproducible release candidate

- **Risk:** Tests may run against a dirty tree containing unrelated, untracked,
  or concurrent work.
- **Check:** Record status, branch, commit, untracked assets, intent-to-add
  entries, and generated changes before validation.
- **Do:** Isolate release work in a clean commit or worktree and exclude unrelated
  sessions.
- **Pass evidence:** The exact validated commit can be checked out and reproduce
  the release results.

## 56. Version and metadata consistency

- **Risk:** Tag, package version, changelog, citation date, release page, website,
  and PyPI may describe different releases.
- **Check:** Compare every release-bearing surface automatically.
- **Do:** Update them in one release workflow and reject stale dates or
  descriptions.
- **Pass evidence:** The release check passes against the intended tag and
  freshly built distributions.

## 57. Full supported-platform CI

- **Risk:** PyPI may advertise Python versions that CI does not test.
- **Check:** Compare classifiers, `requires-python`, documentation, and the CI
  matrix.
- **Do:** Run lightweight install, import, and scan tests on every supported
  version and heavy tests on the primary version.
- **Pass evidence:** All advertised versions install and execute representative
  commands successfully.

## 58. Supply-chain and publication consistency

- **Risk:** Moving GitHub Action tags, leaked secrets, private project names,
  unmanaged binaries, or mismatched Pages and PyPI states reduce trust.
- **Check:** Inspect workflows, package contents, secret scans, LFS usage,
  generated sites, repository metadata, and public endpoints.
- **Do:** Pin actions by immutable SHA, manage large assets intentionally, and
  publish code, package, and site changes coherently.
- **Pass evidence:** CI, secret, privacy, package-content, Pages, and PyPI
  verification all pass.

# H. Agentic development process

## 59. Read-only and concurrency discipline

- **Risk:** A review agent may stash or edit files while simultaneous sessions
  modify the same release tree.
- **Check:** Before delegation, inspect repository state and assign
  non-overlapping ownership.
- **Do:** Give read-only agents no mutation instructions; use separate worktrees
  for concurrent writers; never stash or reset another session's work.
- **Pass evidence:** Audit logs show no unauthorized mutation and validation runs
  against a stable tree.

## 60. Observable, recoverable execution

- **Risk:** Long silent work looks stuck; broken browser or server state is
  mistaken for a product bug; failing hooks are retried without diagnosis.
- **Check:** Establish expected duration, tool availability, server health, and
  checkpoints before long operations.
- **Do:** Use short inspect-act-verify loops, report material phase changes, stop
  repeated failing approaches, and create precise handoffs when blocked.
- **Pass evidence:** The session history clearly shows progress, verification,
  blockers, recovery actions, and final state.
