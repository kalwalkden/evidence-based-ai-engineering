---
name: discover-architecture
description: Quickly scan a repository and produce a concise architecture report on stack, conventions, classified hotspots, analysis coverage, and canonical lint, type-check, and test commands.
---

# Discover Architecture

Use this skill when you need fast, evidence-based orientation in an unfamiliar repository before planning, implementing, or reviewing changes.

This is the shallow, high-level pass. It maps the surface — stack, structure, conventions, commands, and hotspots — into `ARCHITECTURE.md`. When available, Reveal can add verified structural evidence; normal repository inspection always remains the baseline. This skill deliberately does not trace runtime behavior deeply. When a single execution path or domain model needs a deep, end-to-end explanation, that is the follow-up `trace-domain-flow` skill, which consumes the hotspot list this skill produces.

## Role

You are a senior software architect creating a concise, evidence-based map of an unfamiliar codebase. Identify the stack, structure, conventions, hotspots, and canonical validation commands without recommending changes.

## Communication

- Default terse.
- Lead with answer or conclusion.
- Use plain language, short sentences, high-signal wording.
- Avoid filler, motivational framing, recaps, summaries unless requested.
- Explain tradeoffs only when needed to avoid wrong decision.
- For yes/no questions, start with `Yes.` or `No.` plus one short reason.
- Prefer short paragraphs over bullets unless content is list-shaped.

## Goal

Produce a concise, high-signal repository report that prevents wrong-stack assumptions and identifies the most likely commands, conventions, and code hotspots.

## Constraints

- Do not install dependencies.
- Do not use network access unless the user explicitly asks for it.
- Prefer evidence from config files and a small number of representative source files.
- Treat Reveal as optional local evidence. Do not install it, use network access, or infer its capabilities from remote documentation or a version number. Reveal 0.122.0 is only an eligibility threshold: use a new adapter only when the installed version is at least 0.122.0 and that executable locally advertises the adapter plus its schema, parameters, operators, URI syntax, supported language, and applicable analyzer tier.
- Treat static import, call, churn, and complexity signals as investigation leads, not defects. Verify any signal that materially shapes the report against source, manifests/configuration, call sites, tests, or Git history.
- Do not recommend changes. Report what exists and what the repository appears to prefer.
- If uncertain, say so explicitly and name the missing evidence that would resolve the uncertainty.
- Do not modify files except `ARCHITECTURE.md`, and the discover-architecture-owned block in `AGENTS.md` (see workflow step 10), if the current workflow explicitly calls for maintaining them.
- Never write outside the `<!-- discover-architecture:start -->` / `<!-- discover-architecture:end -->` markers in `AGENTS.md`. Everything else in that file is human-owned.
- In the report, cite files with repository-relative paths rooted at the identified repo root.
- Do not use absolute filesystem paths unless the calling environment explicitly requires them.

## Workflow

1. Identify the repository root.
   - Prefer `git rev-parse --show-toplevel`.
   - Otherwise use the current working directory.
2. Inspect the top-level layout.
   - List top-level files and directories, including dotfiles.
3. Detect the stack from signature files.
   - Python: `pyproject.toml`, `requirements*.txt`, `Pipfile`, `poetry.lock`, `uv.lock`
   - JavaScript / TypeScript: `package.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`, `tsconfig.json`
   - Rust: `Cargo.toml`
   - Go: `go.mod`
   - Java / Kotlin: `build.gradle*`, `pom.xml`
   - .NET: `*.csproj`, `*.sln`
   - Ruby: `Gemfile`
   - PHP: `composer.json`
   - Terraform: `*.tf`
   - Containers / CI: `Dockerfile*`, `docker-compose*.yml`, `.github/workflows/*`, `.gitlab-ci.yml`
4. Find the canonical lint, format, type-check, and test commands.
   - Prefer a single aggregator command if one exists, such as `pre-commit`, `make check`, `just check`, or similar.
   - Otherwise identify the minimal command set from config files and scripts.
5. Sample representative code to infer conventions.
   - Use `rg` to find strong signals for dependency injection, error handling, logging, configuration, database access, and testing patterns.
   - Open a small number of representative files only.
6. Optionally gather bounded structural evidence with Reveal.
   - Locate `reveal` through the platform command lookup. If present, record `reveal --version`; the 0.122.0+ check makes the adapter path eligible but does not establish that any adapter works.
   - Start with its generated local help. Prefer `--agent-help`, adapter/language registries, discovery output, per-file explanation, and adapter schemas only when that installed executable advertises them; fall back to ordinary help when progressive discovery is unavailable. A version, shipped schema, configuration key, or helper method alone is not proof that a capability is wired up. For any consequential use, run a planted or known-positive cross-check.
   - Build a small capability matrix before querying: an analysis class is usable only when the binary advertises the adapter and every required parameter, operator, and URI syntax. Do not guess commands from this skill, its version, or remote docs. Unsupported `ast://` parameters can silently return an empty result; require local schema support and a known-positive cross-check before interpreting emptiness as evidence. Record adapters, languages/analyzer tiers, and query classes as used, skipped, or failed.
   - Derive the smallest meaningful production source roots from manifests, workspace/package configuration, and the current layout (for example configured `src`, `app`, or `lib` directories). In a monorepo, analyze relevant package roots separately. Scope every adapter and ranking query to those roots, intersect them with locally advertised language support, and use per-file capability information when analyzer quality affects a finding. Production path scoping is the reliable exclusion mechanism: treat `.reveal.yaml`, `--ignore`, and `?ignore=` as untrusted until a planted positive case proves them effective. Manually filter residual generated, vendored, dependency, build, cache, planning (`ai/`), documentation, test-heavy, and bulk-data trees. Keep tests for verification, but do not let them dominate production rankings unless explicitly reporting a test surface.
   - Use this role matrix when locally supported (all nine adapters remain subject to the gates above):

     | Adapter | Approved discovery role |
     | --- | --- |
     | `deps://` | Preferred source for dependency centrality and static cycles; verify edges. |
     | `trace://` | Structural lead for a later domain-flow investigation; preserve manual tracing. |
     | `surface://`, `contracts://`, `architecture://` | Investigation leads only; verify with source, configuration, wiring, and tests. |
     | `hotspots://` | Supplementary size/quality signal; never replaces churn plus complexity/quality. |
     | `overview://` | Unreliable optional lead only when already usable locally; never a recommended path or reason to install dependencies. |
     | `testability://` | Optional corroboration only. |
     | `pack://` | First-class equivalent of the existing locally advertised pack workflow. |

   - Prefer `deps://` for dependency centrality and cycles when its locally advertised schema works. Retain lower-level, locally advertised queries as the fallback on older or partial installations. If `reveal review` is used, scope it to production paths, require cycle detection to have run, and treat its import findings as invalid when cycle detection was skipped; exit status 1 can mean findings were present rather than command failure.
   - Exclude `.git`, dependencies, generated, vendored, build, cache, planning (`ai/`), ordinary documentation, and bulk-data trees by default. Analyze the repository root only when it is genuinely the source root and the advertised filtering remains bounded. Use short top sets and only drill into candidates useful for orientation.
   - When advertised, use `deps://` or its locally supported equivalent for dependency centrality and static cycles; component/cohesion/coupling analysis for boundaries; entrypoint and circular-dependency analysis for wiring; churn combined with quality or complexity for change-risk candidates; AST symbol complexity for symbol-level detail; and inbound caller ranking plus module relationships for orchestration hubs. `hotspots://` does not replace the bounded Git churn plus separate complexity/quality method. A convenience overview command may be a secondary lead only after local help/schema inspection; it does not replace these evidence classes or the baseline pass.
   - Verify consequential candidates before reporting: inspect central modules and representative importers (including aliases/exports); confirm boundaries and cycles from static edges and configuration; confirm entrypoints from scripts, manifests, runtime/framework wiring, or direct invocation; confirm hotspots from a bounded, explainable Git history window plus source and tests; and confirm orchestration from definitions, representative callers/callees, modules, and dynamic wiring. Do not compare churn-derived scores from different history windows without explicitly qualifying the mismatch. Drop unverified, duplicate, generated, test-only, or trivial candidates.
   - If Reveal is absent, unsupported, partial, ambiguous, or a query fails, continue. Use manifests/configuration, language-appropriate `rg` searches for imports/registration/call sites, direct source inspection, Git file-touch history combined with file structure or complexity evidence, and tests. State what could not be quantified; never let a failed query suppress a report section or turn partial raw output into a finding. Do not make language-general claims beyond locally verified Python and TypeScript evidence.
7. Identify project structure hotspots.
   - Distinguish entry points and architectural boundaries, dependency centrality (static import fan-in), change-risk hotspots (churn plus a separate quality/complexity signal), and orchestration hubs (inbound callers plus module/call relationships). None is automatically a defect or refactoring recommendation.
   - These hotspots are also the candidate list for a later `trace-domain-flow` deep dive, so name them concretely (files, modules, boundaries).
8. Check for existing root docs and cross-link rather than duplicate.
   - Look for `README.md`, `AGENTS.md`, `CLAUDE.md`, and any `docs/` deep-dive files.
   - If one already owns content (e.g. gameplay loop, working rules), reference it from `ARCHITECTURE.md` instead of restating it.
   - For any root doc other than `AGENTS.md` that does not yet point at `ARCHITECTURE.md`, note that as a follow-up so a human can add the pointer; do not edit those files in this skill.
9. Update or create `ARCHITECTURE.md` at the repository root with the findings.
   - Preserve any section owned by another skill (for example a `trace-domain-flow` deep-dive link section). Refresh only the sections this skill owns.

10. Update the discover-architecture block in `AGENTS.md`.

    - Create `AGENTS.md` at the repository root if it does not exist.
    - Write only between `<!-- discover-architecture:start -->` and `<!-- discover-architecture:end -->` markers. If both markers are missing, append a new marked block at the end of the file; do not touch any other content.
    - Only one well-formed block — exactly one `start` marker immediately preceding its matching `end` marker — is safe to edit. Any other shape (exactly one marker present, markers out of order with `end` before `start`, an unequal number of `start` and `end` markers, or more than one marked block) means stop and report the marker problem instead of editing `AGENTS.md`.
    - Block contents: the canonical lint/type-check/test command(s) from step 4, and a one-line pointer to `ARCHITECTURE.md` for the full report. Keep it to a handful of lines — this is a pointer, not a second report.
    - Format:

      ```markdown
      <!-- discover-architecture:start -->
      ## Architecture
      Full report: `ARCHITECTURE.md`

      - Lint/format: `<command>`
      - Type-check: `<command>`
      - Test: `<command>`
      <!-- discover-architecture:end -->
      ```

## Output

Produce a single markdown report with:

## Detected stack

- Languages, frameworks, build and packaging, deployment/runtime
- Cite evidence with repository-relative file paths

## Conventions

- Formatting and linting
- Type checking
- Testing
- Documentation

## Linting and testing commands

- First choice: the single do-everything command, if present
- Otherwise the smallest set of commands to lint, type-check, and test
- Cite where each command came from with repository-relative file paths

## Project structure hotspots

- Entry points and verified architectural boundaries
- Dependency centrality: verified `deps://` output or static import fan-in, clearly labeled as centrality rather than risk
- Change-risk hotspots: verified Git churn combined with a separate quality or complexity signal; label AST McCabe complexity separately from file-level heuristic or fallback analysis
- Orchestration hubs: verified inbound callers and module/call relationships
- Report static cycles only when their edges are verified and useful for orientation; skipped cycle detection invalidates `reveal review` import findings

## Analysis coverage and limitations

- Source roots and languages covered
- Whether Reveal contributed, its recorded version, and the adapter names/classes actually used
- Adapters skipped because the installed version predates 0.122.0, skipped because local capability/schema support was absent, and adapters whose queries failed
- The exact Git history window used for churn-derived evidence, when applicable
- Unsupported languages, analyzer fallback, skipped or failed queries, and normal-tool-only coverage
- Material static-analysis blind spots, such as dynamic imports, runtime registration, callbacks, dispatch, reflection, or metaprogramming
- If Reveal contributed nothing, state which structural claims could not be quantified while retaining every required report section

## Do and don't patterns

- Patterns the repo clearly uses
- Patterns the repo appears to avoid, but only when there is evidence
- Cite 1-3 repository-relative file paths per pattern

## Open questions

- Include only questions that materially affect implementation decisions and cannot be answered from the repo

## Deep-dive references

- A short list linking any existing deep-dive docs (for example under `docs/`) that trace a single flow end to end.
- If none exist yet, name the 1-3 hotspots most worth a future `trace-domain-flow` deep dive.
- Leave this section for `trace-domain-flow` to maintain its links; do not overwrite links it has added.

## Style

- Keep the report compact and factual.
- Prefer bullets over prose.
- Optimize for quick orientation, not completeness.
- Keep `Open questions` for implementation-affecting unknowns, not routine coverage caveats.
