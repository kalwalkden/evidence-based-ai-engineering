# Reveal 0.122 Skill Adapters

Status: Complete.

## Summary

Update `discover-architecture` and `trace-domain-flow` to use Reveal 0.122.0's new
high-level adapters when the installed executable supports them. Preserve direct repository
inspection and verification as the authority for reported findings.

## Requirements

- Add an explicit Reveal 0.122.0 adapter path to `discover-architecture` without removing the
  compatible manual queries used on older installations.
- Require both a detected version of at least 0.122.0 and locally advertised adapter/schema support
  before using the new path. Version alone is never evidence that a command or parameter works.
- Cover all nine evaluated adapters in the discovery capability guidance:
  `deps://`, `trace://`, `surface://`, `contracts://`, `architecture://`, `hotspots://`,
  `overview://`, `testability://`, and `pack://`.
- Prefer `deps://` for dependency centrality and cycles. Retain the bounded Git churn combined with
  complexity or quality evidence for change-risk analysis.
- Treat `surface://`, `contracts://`, and `architecture://` as investigation leads that require
  source, configuration, wiring, or test verification.
- Treat `hotspots://` as a supplementary size/quality signal, not a churn-aware replacement.
- Treat `overview://` as an unreliable optional lead only. Do not instruct users to install
  `reveal-cli[git]` or any other dependency for it.
- Treat `testability://` as optional corroboration and `pack://` as a first-class equivalent of the
  existing pack workflow.
- Strengthen path scoping as the reliable exclusion mechanism. Do not direct agents to use
  `.reveal.yaml`, `--ignore`, or `?ignore=` for scoping based on their verified 0.122.0 behavior.
- Name the silent-empty-result failure mode for unsupported `ast://` query parameters. Require a
  locally advertised schema and a known-positive cross-check before interpreting an empty result.
- If `reveal review` is mentioned, require production-path scoping. Treat skipped cycle detection as
  invalidating its import findings and document that exit code 1 can mean findings were present.
- Require the architecture report's analysis coverage to list new adapters used and adapters skipped
  because the installed version predates them or the local executable does not advertise them.
- Make `trace://.?from=<fn>&depth=<n>` the starting structural lead in `trace-domain-flow`, using the
  verified parameter names. Preserve manual end-to-end tracing for unresolved/external edges,
  framework wiring, dependency injection, reflection, callbacks, and runtime registration.
- State in both skills that shipped schemas, configuration keys, and helper methods are not proof a
  feature is wired up; verify consequential behavior with a planted or known-positive case.

## Constraints

- This is an instruction update, not a rewrite of either skill.
- Reveal remains optional. Neither skill installs dependencies or uses remote documentation to infer
  local capabilities.
- Existing queries verified as byte-identical between Reveal 0.112.0 and 0.122.0 remain valid
  fallbacks.
- Findings from static adapters remain leads. Agents still decide whether evidence represents a
  defect, essential complexity, or settled code.
- Claims about the adapters are limited to the verified Python and TypeScript evidence. Other
  languages require local capability discovery and verification; the skills must not make untested
  language-general promises.
- Vendored, generated, dependency, build, cache, planning, documentation, test-heavy, and bulk-data
  trees must not contaminate production rankings. Path-scope first and manually filter remaining
  contamination.
- Existing ownership rules for `ARCHITECTURE.md`, `AGENTS.md`, root documentation, and deep-dive
  links remain unchanged.
- Each implementation task must leave the repository checks green.

## Success Criteria

- An agent using Reveal 0.122.0 can discover and select the new adapters without reconstructing the
  same evidence from lower-level queries where an adopted adapter is sufficient.
- An agent on an older or partially capable Reveal installation follows the existing manual path and
  records why new adapters were skipped.
- Empty or authoritative-looking adapter output cannot be reported without schema, positive-case,
  and repository verification appropriate to the claim.
- Dependency centrality uses `deps://` when supported; change risk still uses churn combined with a
  separate complexity or quality signal.
- Domain-flow tracing begins with the supported `trace://` query but the final deep dive follows and
  verifies the real code path.
- Canonical prose, skill-structure, and repository checks pass.

## Non-goals / Out of Scope

- Rewriting either skill's purpose, output ownership, or overall workflow.
- Replacing repository inspection, Git evidence, source reading, tests, or human judgment with
  Reveal output.
- Installing `pygit2`, `reveal-cli[git]`, Reveal itself, or any other dependency.
- Validating adapter behavior on Go, Rust, Java, or other untested language stacks.
- Fixing Reveal's ignored configuration, query validation, review scanning, or adapter ranking
  behavior upstream.
- Updating runtime interface manifests, installer behavior, README product copy, or unrelated skills.
- Adding UI or visual design; this feature changes agent instructions only.

## Approach and Key Decisions

1. Update discovery guidance first. Keep the baseline inspection workflow, then add a compact
   capability matrix for Reveal 0.122.0+ whose entries distinguish adopted, lead-only,
   supplementary, optional, and fallback behavior.
2. Encode two gates: the version determines whether the new adapter path is eligible; local help and
   schemas determine whether a specific adapter and query are usable.
3. Make path-scoped production roots the default query boundary. Describe config and ignore controls
   as untrusted until a planted positive case proves them effective on the installed executable.
4. Preserve the current evidence classes while changing their preferred source: `deps://` can replace
   manual centrality/cycle assembly, but no adapter replaces churn joined with complexity or quality.
5. Update domain tracing second. Use `trace://` to generate the first call-walk lead, then require the
   existing manual verification pass to resolve framework and dynamic behavior.
6. Keep `overview://` out of the recommended path. It may be recorded as an optional lead only when
   it already works locally; the skills never ask users to install its optional Git dependency.

The main tradeoff is slightly denser Reveal guidance in exchange for fewer manual calls and clearer
failure handling. A version-only recipe would be shorter but would contradict the observed dead and
partially validated capability surfaces, so local schema and positive-case checks remain mandatory.

## Implementation Map

- `discover-architecture/SKILL.md` — primary owner. Step 6 owns Reveal discovery, capability gating,
  source-root scoping, adapter roles, and verification traps. Step 7 owns hotspot classification.
  `Analysis coverage and limitations` owns used/skipped adapter reporting.
- `trace-domain-flow/SKILL.md` — secondary owner. Workflow step 3 owns the structural trace lead and
  the manual evidence pass needed for unresolved and dynamically wired edges.
- `docs/design-principles.md` — representative evidence for the existing “evidence before inference”
  and durable-artifact boundaries; expected to remain unchanged.
- `ARCHITECTURE.md` — repository orientation and skill-boundary map; expected to remain unchanged by
  implementation.
- `scripts/check.sh` — canonical validation entry point. Prose and structural validation are the
  relevant test areas; the runner itself is expected to remain unchanged.
- `.markdownlint-cli2.jsonc`, `cspell.json`, and `scripts/validate_skills.py` — enforce Markdown,
  spelling, and skill structure. Only vocabulary configuration may need adjustment if required by
  final wording; validator behavior is expected to remain unchanged.
- `discover-architecture/agents/openai.yaml` and `trace-domain-flow/agents/openai.yaml` — runtime
  interfaces are not expected to change because skill purposes and default prompts remain stable.

## Expected Task Sequence

1. Update `discover-architecture` with the version/schema gates, adapter matrix, path-scoping rules,
   verification traps, hotspot recipe, and coverage reporting.
2. Update `trace-domain-flow` with the `trace://` starting lead and shared verification warning,
   preserving its manual end-to-end evidence requirements.

These are separate green-keeping boundaries: the discovery skill can adopt its adapter guidance and
validate independently before the trace skill consumes the related tracing capability.

## Open Questions

None.
