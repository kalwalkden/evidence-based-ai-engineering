# Update Discover Architecture

## Context

Reveal 0.122.0 adds high-level adapters that can replace or supplement several manually assembled
evidence queries in `discover-architecture`. Live testing also exposed silent query failures,
non-functional exclusion controls, over-scanning, and authoritative-looking false positives.

## Objective

Update the discovery skill to select the new adapters safely when locally supported while retaining
the existing compatible fallback and evidence-verification discipline.

## Scope

- Add explicit version eligibility and local schema/capability gates for the Reveal 0.122.0 adapter
  path.
- Classify all nine evaluated adapters by their approved role from `feature.md`.
- Prefer `deps://` for dependency centrality and cycles without replacing the churn-plus-complexity
  change-risk method.
- Make production path scoping the reliable exclusion mechanism and encode the verified ignore,
  empty-result, review-over-scan, and contamination traps.
- Require used, skipped, failed, and version-ineligible adapters in analysis coverage.
- Preserve direct repository verification for consequential findings and dynamic/runtime blind
  spots.

## Non-goals / Later

- Changing `trace-domain-flow`; task 002 owns that update.
- Rewriting the discovery workflow or its artifact ownership rules.
- Installing dependencies or repairing Reveal upstream.
- Making unverified claims for languages beyond the Python and TypeScript evidence.

## Constraints / Caveats

- Version 0.122.0 is only an eligibility gate. Local help and schemas remain the authority for usable
  adapters, parameters, operators, and URI syntax.
- Existing lower-level queries remain the fallback for older or partial installations.
- `overview://` is not part of the recommended path and must not trigger dependency installation.
- Static rankings are leads, not defects or architecture conclusions.
- Keep the instruction change focused and consistent with the evidence-before-inference principle in
  `docs/design-principles.md`.

## Dependent Tasks or Work

None.

## Acceptance Criteria

- The skill gives a bounded, locally discoverable 0.122.0+ path and a clear fallback path.
- The adapter roles and all verified traps from `feature.md` are represented without weakening
  verification.
- Change-risk analysis remains churn-aware and production rankings are path-scoped.
- Analysis coverage distinguishes adapters used from adapters skipped for version, capability, or
  failure reasons.

## Likely Starting Points

- `discover-architecture/SKILL.md` — workflow step 6 owns Reveal use; step 7 and the output template
  own hotspot classification and coverage reporting. `$shape-spec` must re-check these landmarks.
- `docs/design-principles.md` — defines the existing evidence-before-inference boundary the update
  must preserve. `$shape-spec` must re-check this reference.
- `ARCHITECTURE.md` — maps the repository's skill and validation boundaries. `$shape-spec` must
  re-check it for current orientation.

## Expected Change Surface

- Primary change: Reveal instructions, hotspot evidence selection, and coverage requirements in
  `discover-architecture/SKILL.md`.
- Shared contract: optional-tool capability discovery must remain consistent with repository-first
  verification and with task 002's trace guidance.
- Likely test areas: Markdown structure, prose spelling, and skill-structure validation.
- Expected unchanged: `discover-architecture/agents/openai.yaml`, runtime prompts, installer logic,
  report ownership, `AGENTS.md` marker rules, and unrelated skills.

## Open Questions

None.
