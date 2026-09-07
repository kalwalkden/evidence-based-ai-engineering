# Task Plan: Update Discover Architecture

## Scope

Update only `discover-architecture/SKILL.md` so its optional Reveal workflow can use the approved
Reveal 0.122.0+ adapters safely. Preserve the ordinary repository-inspection workflow and every
existing report and ownership boundary. This task does not change `trace-domain-flow`; task 002
will consume this task's shared terminology after it is complete.

## Decisions and constraints

- The approved feature and this task brief are binding: Reveal 0.122.0 is an eligibility threshold,
  not proof that an adapter, parameter, operator, URI form, language, or analyzer tier works.
- A new adapter may be used only after both gates pass: the installed version is at least 0.122.0,
  and that exact local executable advertises the adapter plus the required schema and query surface.
  `reveal --agent-help` is preferred; ordinary local help remains the fallback.
- Reveal remains optional and local. Do not install Reveal, `reveal-cli[git]`, `pygit2`, or any
  other dependency; do not use remote documentation to fill capability gaps.
- Static output is an investigation lead. Consequential report claims still require repository
  verification, matching the evidence-before-inference rule in `docs/design-principles.md`.
- Scope adapter queries to independently derived production source roots. Treat `.reveal.yaml`,
  `--ignore`, and `?ignore=` as untrusted exclusion mechanisms unless a locally run planted or
  known-positive case proves their behavior. Manually filter residual generated, vendor, dependency,
  build, cache, planning, documentation, test-heavy, and bulk-data contamination.
- Keep bounded Git churn joined to a separate source-level complexity or quality signal for
  change-risk. No static ranking is a defect or a substitute for that evidence class.
- No task-local visual work is needed. The feature explicitly changes instructions only and has no
  `visuals/` directory.

## Current-tree findings

The brief's landmarks are current. `discover-architecture/SKILL.md` owns optional Reveal work in
workflow step 6, hotspot classification in step 7, and report coverage in the `Output` template.
It already mandates local help, bounded production roots, verification, and a normal-tool fallback,
but it has no 0.122.0 eligibility gate, adapter-role matrix, silent-empty safeguard, or distinct
used/skipped/failed/version-ineligible coverage.

`ARCHITECTURE.md` confirms Markdown skill definitions are the product surface and names
`scripts/check.sh` as the canonical runner. `docs/design-principles.md` makes approved decisions
and repository configuration binding, ranks static analysis as supporting evidence, and requires
durable, bounded handoffs. No earlier feature task is complete: both task checkboxes remain open,
and task 002's brief declares a dependency on this task. Do not edit its skill now.

## Implementation approach

1. Refine the Reveal constraints and workflow step 6 without moving the baseline scan or normal-tool
   fallback. Make the 0.122.0 version check explicit, then require per-adapter local discovery of
   adapter availability, schema, parameters, operators, URI syntax, language support, and applicable
   analyzer quality before a query can contribute.
2. Replace the generic Reveal evidence-class wording with a compact, scannable adapter matrix. Keep
   the existing lower-level, locally advertised queries as the compatible fallback. Record each
   adapter's approved role:

   | Adapter | Role in discovery guidance |
   | --- | --- |
   | `deps://` | Preferred adopted source for dependency centrality and static cycles when supported; verify edges. |
   | `trace://` | Structural lead for a later domain-flow investigation; task 002 owns the trace workflow. |
   | `surface://`, `contracts://`, `architecture://` | Lead-only evidence; verify with source, configuration, wiring, and tests. |
   | `hotspots://` | Supplementary size/quality signal only; never replaces bounded churn plus complexity/quality. |
   | `overview://` | Unreliable optional lead only if already locally usable; never a recommended path or reason to install dependencies. |
   | `testability://` | Optional corroboration only. |
   | `pack://` | First-class equivalent to the established locally advertised pack workflow. |

3. Make path-scoped production roots the exclusion contract for every ranking or `reveal review`
   invocation. If review is used, require cycle detection to have run; missing/skipped cycle
   detection invalidates its import findings. Explain that exit status 1 may mean findings were
   reported, not that the command failed.
4. Add the observed failure modes close to query selection: unsupported `ast://` parameters can
   silently produce empty results, so require a locally advertised schema and a known-positive
   cross-check before treating an empty result as evidence. State that shipped schemas, config keys,
   or helper methods do not prove a capability is wired; consequential use needs a planted or
   known-positive behavioral check.
5. Update step 7 and the report template only as needed to retain semantic distinctions: `deps://`
   may supply centrality/cycles, while change risk continues to require bounded Git churn plus a
   distinct quality or complexity signal. Require `Analysis coverage and limitations` to separately
   list adapter names/classes used, skipped for old version, skipped for absent local capability,
   and failed queries, as well as normal-tool-only coverage and blind spots.
6. Keep prose compact and preserve existing output headings, report ownership (`ARCHITECTURE.md` and
   the marked `AGENTS.md` block), local-only behavior, and the direct verification paragraph.

## Call path and invariants

`Discover Architecture` invocation -> workflow steps 1-5 establish repository evidence and source
roots -> step 6 optionally locates Reveal and runs version plus local capability discovery ->
version/schema-qualified adapter queries operate only on scoped production paths -> source, config,
tests, and bounded Git history verify any material candidates -> step 7 classifies verified hotspots
-> `ARCHITECTURE.md` `Analysis coverage and limitations` records both evidence and omitted adapter
paths -> steps 8-10 preserve documentation and `AGENTS.md` ownership rules.

The fallback path is mandatory, not an error condition: an absent, pre-0.122.0, partial, ambiguous,
or failed Reveal installation must still yield every required report section from repository evidence.
Never report an adapter ranking, empty result, review import finding, static cycle, centrality, or
dynamic behavior as an architecture conclusion without the stated verification. Do not make claims
about languages beyond the verified Python and TypeScript evidence; require local discovery and
verification for any other language.

## Tests and validation

Run focused checks after the Markdown edit:

```sh
scripts/check.sh prose validate
```

Run the full project gate before handoff:

```sh
scripts/check.sh lint prose validate test
```

These are the relevant project groups in `scripts/check.sh`; `ARCHITECTURE.md` and `AGENTS.md`
identify the same canonical runner. The focused command exercises Markdown structure/spelling and
skill structure plus install-list synchronization. The full command additionally runs lint and the
pytest matrix. No behavioral test harness exists for skill prose, so review the final matrix,
fallback, coverage wording, and untouched output/ownership sections directly against this plan.

## Expected unchanged boundaries

- `discover-architecture/agents/openai.yaml`: default prompt and interface contract stay stable.
- `trace-domain-flow/SKILL.md` and its manifest: task 002 exclusively owns the trace-specific edit.
- `ARCHITECTURE.md`, `AGENTS.md`, `README.md`, installer scripts, validator behavior, and runtime
  prompts: no edit is needed for this instruction-only task.
- Existing low-level Reveal path, ordinary repository inspection, direct verification, report
  headings, and artifact ownership: preserve them as the compatible baseline.

## Open questions

None. Exact command forms, parameters, operators, and URI syntax must deliberately remain locally
discovered rather than being frozen in this repository instruction; this is an approved safety
constraint, not an unresolved product decision.
