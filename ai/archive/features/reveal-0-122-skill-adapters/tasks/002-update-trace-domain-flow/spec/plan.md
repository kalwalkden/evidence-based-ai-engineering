# Task Plan: Update Trace Domain Flow

## Scope

Update only `trace-domain-flow/SKILL.md` so, after an agent confirms a concrete entry point, it may
use the locally supported Reveal `trace://` adapter as its first structural call-walk lead. Preserve
the mandatory manual end-to-end trace and every deep-dive output, documentation, and cross-link
contract. This is an instruction-only task; it does not add Reveal as a dependency or alter runtime
interfaces.

## Decisions and constraints

- The approved feature and task brief are binding. Reveal 0.122.0+ makes this adapter path eligible,
  but the agent must first discover that its installed executable advertises `trace://` and its query
  schema. Reveal remains optional, local-only evidence; do not install it or consult remote
  documentation to fill a capability gap.
- The locally installed `reveal 0.122.0` advertises `trace://<path>?from=<FUNC>&depth=2`. Its schema
  makes `from` a required string entry-point function and `depth` an optional integer (default 2,
  clamped 1–5). The instruction should use the approved root-scoped form
  `trace://.?from=<fn>&depth=<n>` only after local schema discovery, not invent further query syntax.
- Adapter output is a structural lead, not deep-dive authority. The final document must cite direct
  repository source and tests. Manually resolve unresolved or external edges and verify framework
  wiring, dependency injection, reflection, callbacks, dispatch, and runtime registration.
- A shipped schema, configuration key, or helper method does not prove capability wiring. For any
  consequential reliance on an adapter or runtime behavior, require a planted or known-positive
  case, then repository evidence. This matches task 001 and `docs/design-principles.md`'s
  evidence-before-inference rule.
- No task-local visual work is needed. The feature has no `visuals/` directory and changes agent
  instructions only.

## Current-tree findings

The brief's primary landmark is current: workflow step 3, `Trace the chosen flow end to end`, is the
sole trace-method owner in `trace-domain-flow/SKILL.md`. It now begins direct entry-point-to-terminal
manual tracing and requires full-path source reads, data-shape, sequencing, invariant, and test
evidence. Its `Output` and step 5 own the deep-dive sections and root-document reachability rules;
they need no scope change.

Task 001 is complete in feature state (`tasks.md` marks it complete) and its working-tree update to
`discover-architecture/SKILL.md` supplies the shared contract: Reveal 0.122.0 is eligibility only;
local schema/capability discovery and known-positive checks are required; static output is a lead;
dynamic wiring requires direct evidence; absent or partial Reveal falls back to ordinary inspection.
Do not edit task 001's skill in this task. Its older task-local spec says the prerequisite was not
complete, but that statement is stale versus the current feature checklist and working tree.

`docs/design-principles.md` confirms that approved scope and enforceable repository configuration are
binding, while source, tests, and analysis outputs require appropriate verification. `ARCHITECTURE.md`
and the checked-in `AGENTS.md` block identify `scripts/check.sh` as the canonical checker.

## Implementation approach

1. In workflow step 3, retain the existing entry-point-first order. Immediately after that entry point
   is confirmed, add one compact optional structural action: detect local Reveal support using the
   shared version and schema gates, then run the locally advertised
   `trace://.?from=<fn>&depth=<n>` form as the starting call-walk lead.
2. State the actual local schema contract without broadening it: derive the function name from the
   confirmed entry point, use locally advertised `from` and `depth`, and choose a bounded depth that
   the installed schema accepts. Do not hard-code a Reveal binary command or promise support for
   unverified languages.
3. Follow that optional lead with the existing manual source-and-test walk. Explicitly require manual
   resolution of adapter-marked unresolved/external edges and direct evidence for framework or dynamic
   connections: dependency injection, reflection, callbacks, dispatch, and runtime registration.
4. Add the shared false-proof warning close to adapter use. A locally visible schema, configuration,
   or helper is insufficient; consequential claims require a known-positive or planted case and
   repository verification. Keep the fallback path complete when Reveal is absent, pre-0.122.0,
   partially advertised, ambiguous, or produces an incomplete trace.
5. Preserve the workflow's complete-file reading, ordered data-shape and sequencing analysis, test
   evidence, deep-dive headings, `docs/` ownership, `ARCHITECTURE.md` link-only update, and root-doc
   cross-link reachability checks. Do not duplicate task 001's full adapter matrix.

## Call path and invariants

`trace-domain-flow` invocation -> step 1 reads existing `ARCHITECTURE.md` or performs a bounded
orientation scan -> step 2 selects a representative flow and confirms its concrete entry point ->
step 3 conditionally discovers a locally usable `trace://` schema and obtains a bounded structural
lead -> manual source, call-site, configuration/wiring, and test inspection resolves the real path
to its terminal result -> step 4 writes one evidence-backed `docs/<flow-name>-flow.md` deep dive ->
step 5 cross-links it without overwriting `discover-architecture`-owned architecture content.

The manual path is mandatory whether or not Reveal runs. Preserve these rules: every behavior claim
uses repository-relative evidence; static or partial adapter output cannot establish runtime behavior;
data shapes, boundary crossings, ordering, and invariants are tracked through the actual code path;
and the final artifact cites repository evidence rather than adapter output.

## Tests and validation

After the Markdown-only edit, run:

```sh
scripts/check.sh prose validate
```

Before handoff, run the full project gate:

```sh
scripts/check.sh lint prose validate test
```

These commands come from `scripts/check.sh` and are confirmed by `ARCHITECTURE.md` and `AGENTS.md`.
The focused command checks Markdown/spelling plus skill structure and installer synchronization; the
full command also runs lint and the pytest matrix. No executable test exercises this prompt-level
workflow. Manually review the final skill for entry-point ordering, local-schema gating, the exact
`from`/`depth` intent, mandatory dynamic-edge verification, the optional fallback, and unchanged
deep-dive/cross-link contracts.

## Expected unchanged boundaries

- `trace-domain-flow/agents/openai.yaml`: its name, prompt, and runtime interface remain valid.
- `discover-architecture/SKILL.md`: task 001's complete adapter matrix and shared discovery workflow
  remain untouched; this task only consumes their vocabulary.
- `ARCHITECTURE.md`, `AGENTS.md`, `README.md`, `docs/design-principles.md`, `installable-skills.txt`,
  `sync-installable-skills.sh`, `scripts/check.sh`, `scripts/validate_skills.py`, and validation
  configuration: no change is required for this instruction update.
- Flow selection, deep-dive headings, file ownership, root-document reachability, and the baseline
  manual trace remain intact.

## Open questions

None. The installed executable's specific supported languages, adapter details, and accepted depth
range are runtime facts that each future trace must discover locally; the verified 0.122.0 schema is
orientation, not a reason to skip that gate.
