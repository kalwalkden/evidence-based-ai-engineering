# Implementation References: Update Discover Architecture

## Primary edit targets

| Path | Symbol / section | Why it changes |
| --- | --- | --- |
| `discover-architecture/SKILL.md` | `Constraints` Reveal bullets | Add explicit 0.122.0 eligibility, local-capability authority, and verified-use limits without weakening optional-tool or direct-evidence rules. |
| `discover-architecture/SKILL.md` | Workflow step 6, `Optionally gather bounded structural evidence with Reveal` | Owns version/schema gates, production-path scoping, nine-adapter role matrix, query traps, `reveal review` handling, and compatible fallback. |
| `discover-architecture/SKILL.md` | Workflow step 7, `Identify project structure hotspots` | Preserve the separate meanings of centrality, static cycles, change risk, and orchestration; make `deps://` preferred only for the first two. |
| `discover-architecture/SKILL.md` | Output, `Analysis coverage and limitations` | Require adapter names/classes used, skipped by old version, skipped by unavailable capability, and failed, alongside ordinary evidence and blind spots. |

No other file is an expected edit target. The task-local `spec/` files record planning evidence only.

## Entry point and call path

An agent invokes `discover-architecture/SKILL.md` -> steps 1-5 determine repository root, stack,
canonical commands, conventions, and actual production roots -> step 6 optionally discovers the
local Reveal executable and its version/help/schemas -> scoped adapter or lower-level queries offer
structural leads -> source/configuration/call-site/test/Git evidence validates material candidates
-> step 7 classifies hotspots -> the report template's coverage section records how the evidence was
obtained or why it could not be -> steps 8-10 write only the report and the owned `AGENTS.md` block.

`trace-domain-flow/SKILL.md` is a downstream consumer: discovery names concrete, verified hotspot
candidates for a later deep dive. Its task 002 will add the `trace://` call narrative; task 001 may
only classify `trace://` as a locally discovered structural lead and must not change that workflow.

## Contracts, state, and invariants

- The `SKILL.md` frontmatter `name` must remain `discover-architecture`; its
  `agents/openai.yaml` interface remains valid and unchanged (`scripts/validate_skills.py`).
- Reveal is optional local evidence. A usable new-adapter path requires an installed version >=
  0.122.0 and positive local advertisement of the individual adapter plus its schema/query surface.
  Version, shipped schema/config/helper presence, and remote docs alone are insufficient.
- Each consequential query needs appropriate repository verification. Static import/call/cycle,
  ranking, and adapter output are leads; dynamic imports, registration, callbacks, reflection,
  dispatch, and metaprogramming remain blind spots unless directly evidenced.
- Production source roots are the primary boundary. Do not rely on `.reveal.yaml`, `--ignore`, or
  `?ignore=` to exclude contamination without an installed-binary positive control. Keep tests for
  verification, but out of production rankings unless the report intentionally covers tests.
- `deps://` can replace manual assembly only for static dependency centrality and cycles. Change-risk
  continues to be a bounded, explainable Git history window plus a separate complexity or quality
  signal. Do not compare churn scores from incompatible windows.
- Unsupported `ast://` query parameters may return silent empties; no empty result is interpretable
  without local schema support and a known-positive cross-check. `reveal review` must use scoped
  production paths; its import findings are invalid when cycle detection was skipped, and exit 1 may
  indicate findings rather than command failure.
- The report remains concise, factual, repository-relative, and non-prescriptive. It retains all
  required sections even when Reveal is unavailable or contributes nothing.

## Patterns to reuse

| Evidence | Pattern to preserve |
| --- | --- |
| `discover-architecture/SKILL.md` step 6 | Progressive local help/schema discovery, bounded source-root analysis, consequential-candidate verification, and a normal-tool fallback already exist; extend these paragraphs instead of introducing a separate workflow. |
| `discover-architecture/SKILL.md` step 7 and `Output` | Classify centrality, change risk, and orchestration independently, then document coverage and limitations rather than promoting raw rankings to defects. |
| `docs/design-principles.md`, `Evidence before inference` | Approved scope and enforceable repository constraints are binding; static analysis is supporting evidence and material claims need direct verification. |
| `feature.md`, `Approach and Key Decisions` | A compact capability matrix is preferred to scattered adapter instructions; keep only locally discoverable behavior and use fallback queries on older/partial installations. |

## Tests and fixtures

- `scripts/check.sh` groups `prose` and `validate` are the focused checks for this Markdown-only
  instruction edit. They run markdownlint, codespell, cspell, `scripts/validate_skills.py`, and the
  installer dry run.
- `scripts/check.sh lint prose validate test` is the complete CI-equivalent gate. `test` runs pytest
  over the configured Python versions; no test fixture directly executes this skill.
- `cspell.json`, `.markdownlint-cli2.jsonc`, and `scripts/validate_skills.py` define the relevant
  prose and skill-structure constraints. Do not change them unless a final new technical term is
  actually rejected and an allow-list addition is justified.
- Review the final `discover-architecture/SKILL.md` manually for all nine adapter roles, the four
  coverage outcomes, old/partial fallback, production-path scoping, empty-result positive control,
  `reveal review` caveats, and unchanged report ownership.

## Expected unchanged boundaries

- `discover-architecture/agents/openai.yaml`
- `trace-domain-flow/SKILL.md` and `trace-domain-flow/agents/openai.yaml`
- `ARCHITECTURE.md`, `AGENTS.md`, `README.md`, `installable-skills.txt`,
  `sync-installable-skills.sh`, and `scripts/validate_skills.py`
- The existing non-Reveal inspection workflow, lower-level locally advertised fallback queries,
  report headings, and `ARCHITECTURE.md`/marked-`AGENTS.md` ownership rules

## Validation commands

```sh
scripts/check.sh prose validate
scripts/check.sh lint prose validate test
```

Source: `scripts/check.sh`; confirmed by `ARCHITECTURE.md` and the repository `AGENTS.md` marker.

## Uncertainties to verify

- No product or scope decision is unresolved.
- Do not invent exact Reveal command forms while editing. The skill must direct its future user to
  discover the installed executable's schemas, parameters, operators, URI syntax, supported
  languages, and analyzer tier. This task's verified feature evidence is limited to Python and
  TypeScript.
- The current tree has no completed prerequisite task and no existing task spec. Re-check the
  working tree immediately before implementation for concurrent edits to `discover-architecture/SKILL.md`;
  preserve unrelated changes if present.
