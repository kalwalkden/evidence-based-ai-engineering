# Implementation References: Update Trace Domain Flow

## Primary edit targets

| Path | Symbol / section | Why it changes |
| --- | --- | --- |
| `trace-domain-flow/SKILL.md` | Workflow step 3, `Trace the chosen flow end to end` | Insert the optional, locally schema-gated `trace://` call-walk lead after entry-point confirmation and before the existing manual trace. Require manual resolution of incomplete and dynamic edges. |
| `trace-domain-flow/SKILL.md` | `Constraints` or the adjacent step-3 verification wording | Record the shared warning that schemas, configuration keys, and helper methods do not prove capability wiring; consequential reliance needs a known-positive or planted case plus repository evidence. |

No other production or test file is an expected edit target. The task-local `spec/` files are the
planning deliverable only.

## Entry point and call path

An agent invokes `trace-domain-flow/SKILL.md` -> step 1 uses `ARCHITECTURE.md` or a bounded scan for
orientation -> step 2 chooses the representative flow and confirms its entry-point symbol -> step 3
uses the locally advertised, version-eligible `trace://.?from=<fn>&depth=<n>` query only as an
optional structural lead -> direct full-file reads trace calls, configuration, tests, data, and
runtime wiring through the terminal result -> step 4 writes the single docs deep dive -> step 5
adds the deep-dive link to the `ARCHITECTURE.md` references section and checks root-document
reachability.

`discover-architecture/SKILL.md` is the upstream consumer/producer boundary: its step 7 offers
concrete verified hotspots for selection, and its step 6 defines the common optional-Reveal gates.
It does not replace this skill's deep runtime evidence pass.

## Contracts, state, and invariants

- `trace-domain-flow/SKILL.md` frontmatter must retain `name: trace-domain-flow`; its unchanged
  `agents/openai.yaml` must continue to satisfy `scripts/validate_skills.py`.
- Before `trace://` is used, confirm the entry point and require Reveal >= 0.122.0 plus locally
  advertised `trace://` and query schema support. The local 0.122.0 schema records
  `trace://<path>?from=<FUNC>&depth=2`, with a required string `from` and integer `depth` (default
  2; clamped 1–5). Future users must discover this locally rather than treating this plan as command
  authority.
- `trace://` is static call-graph orientation. Its depth-indented narrative cannot prove external,
  unresolved, framework-driven, dependency-injected, reflected, callback, dispatched, or
  runtime-registered behavior. Resolve each material edge from source, configuration, runtime
  registration, call sites, and tests as applicable.
- Shipped schemas, configuration keys, and helper methods are leads, not behavioral proof. For a
  consequential capability claim, use a planted or known-positive case and repository evidence.
- Keep reading every file on the selected path and tracking data shapes, boundary crossings,
  sequencing, and invariants. The output remains one factual, repository-cited deep dive under
  `docs/`, with only a link added to the architecture report.

## Patterns to reuse

| Evidence | Pattern to preserve |
| --- | --- |
| `trace-domain-flow/SKILL.md` workflow step 3 | The present entry-point-to-terminal manual walk, full-path file reading, data/sequencing/invariant notes, and test evidence remain the main workflow. Extend it in place. |
| `discover-architecture/SKILL.md` constraints and workflow step 6 | Reveal is optional; eligibility requires version plus local advertisement/schema; known-positive checks and direct repository verification prevent authoritative-looking false conclusions. Reuse the terminology, not its nine-adapter matrix. |
| `docs/design-principles.md`, `Evidence before inference` | Treat approved feature scope and repository constraints as binding; static analysis is supporting evidence requiring appropriate verification. |
| `trace-domain-flow/SKILL.md` workflow steps 4-5 and `Output` | Preserve one documentation-owned deep dive, the existing section structure, `ARCHITECTURE.md` link-only update, and root-doc access path. |

## Tests and fixtures

- `scripts/check.sh prose validate` is the focused gate for this Markdown instruction change. It runs
  markdownlint, codespell, cspell, `scripts/validate_skills.py`, and installer synchronization dry
  run.
- `scripts/check.sh lint prose validate test` is the project-wide CI-equivalent gate. It additionally
  runs Ruff, YAML/shell checks, and pytest across configured Python versions.
- There is no fixture that executes prompt behavior. Review the final step 3 against the brief: the
  entry point is confirmed first; the query remains optional and schema-gated; `from` and `depth` are
  named; unresolved/external and dynamic edges require manual work; and the final document relies on
  repository evidence.
- `.markdownlint-cli2.jsonc`, `cspell.json`, and `scripts/validate_skills.py` define current prose
  and skill structure. Change none unless validation demonstrates a narrowly justified vocabulary
  addition is necessary.

## Expected unchanged boundaries

- `trace-domain-flow/agents/openai.yaml`
- `discover-architecture/SKILL.md` and `discover-architecture/agents/openai.yaml`
- `ARCHITECTURE.md`, `AGENTS.md`, `README.md`, `docs/design-principles.md`, `installable-skills.txt`,
  `sync-installable-skills.sh`, `scripts/check.sh`, and `scripts/validate_skills.py`
- The non-Reveal fallback, flow-selection behavior, deep-dive sections, cross-link ownership, and
  all existing documentation-maintenance responsibilities

## Validation commands

```sh
scripts/check.sh prose validate
scripts/check.sh lint prose validate test
```

Source: `scripts/check.sh`, confirmed by `ARCHITECTURE.md` and the repository `AGENTS.md` marker.

## Uncertainties to verify

- No product or scope decision is unresolved.
- The task brief's required URI presentation is `trace://.?from=<fn>&depth=<n>`; the installed
  schema separately documents the general form `trace://<path>?from=<FUNC>&depth=2`. Preserve the
  brief's root-scoped form while directing future users to local schema discovery for exact command
  syntax and capability support.
- Re-check the working tree immediately before implementation. Task 001's applied, currently
  uncommitted `discover-architecture/SKILL.md` update is an upstream dependency and should not be
  overwritten by this task.
