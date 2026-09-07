# Update Trace Domain Flow

## Context

Reveal 0.122.0's `trace://` adapter produces a useful depth-indented static call narrative, but it
marks unresolved/external edges and cannot observe framework wiring or other dynamic behavior. The
current skill manually walks the complete path.

## Objective

Use `trace://.?from=<fn>&depth=<n>` as the recommended structural starting lead, then retain the
manual verification needed for an evidence-backed end-to-end domain-flow document.

## Scope

- Add the locally advertised `trace://` query as the first optional structural move after the entry
  point is confirmed.
- Use the verified `from` and `depth` parameter names and require local schema discovery before use.
- Require manual resolution of external/unresolved edges and verification of framework wiring,
  dependency injection, reflection, callbacks, dispatch, and runtime registration.
- Add the shared warning that shipped schemas, configuration keys, and helper methods do not prove a
  capability is wired up; use a known-positive or planted case for consequential reliance.
- Preserve complete source reading, test evidence, data-shape tracking, sequencing contracts, and
  documentation ownership.

## Non-goals / Later

- Replacing the manual end-to-end trace with adapter output.
- Changing flow selection, deep-dive structure, or cross-link ownership.
- Installing or requiring Reveal.
- Extending the discovery adapter matrix owned by task 001.

## Constraints / Caveats

- Depends on task 001's shared version/schema and verification vocabulary.
- `trace://` is optional and static; the workflow must remain complete when it is absent or partial.
- Claims about adapter behavior must stay within the verified Python and TypeScript evidence and be
  re-checked against the locally installed executable.
- The final deep dive cites repository source and tests, not adapter output as authority.

## Dependent Tasks or Work

- `001-update-discover-architecture` must be complete first so both skills use consistent capability
  and verification rules.

## Acceptance Criteria

- The skill starts with the correctly parameterized `trace://` lead when supported.
- Unresolved, external, framework-driven, and dynamic edges still require manual tracing.
- Reveal absence or partial support does not prevent the existing workflow from completing.
- Existing deep-dive content and cross-link contracts remain intact.

## Likely Starting Points

- `trace-domain-flow/SKILL.md` — workflow step 3 owns the end-to-end trace method. `$shape-spec` must
  re-check this landmark.
- `discover-architecture/SKILL.md` — task 001 establishes the shared local capability and verification
  language this task should align with. `$shape-spec` must re-check its completed state.
- `docs/design-principles.md` — defines evidence-before-inference and durable documentation
  expectations. `$shape-spec` must re-check this reference.

## Expected Change Surface

- Primary change: trace workflow and verification constraints in `trace-domain-flow/SKILL.md`.
- Shared contract: optional Reveal evidence must align with completed discovery guidance without
  duplicating its full capability matrix.
- Likely test areas: Markdown structure, prose spelling, and skill-structure validation.
- Expected unchanged: `trace-domain-flow/agents/openai.yaml`, deep-dive output sections, root-doc
  cross-link behavior, installer logic, and unrelated skills.

## Open Questions

None.
