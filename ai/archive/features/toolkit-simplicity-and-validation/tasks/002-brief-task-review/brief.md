# Brief local task review

## Context

Routine task reviews consume effort without reliably exposing the cross-task problems found by feature review.

## Objective

Make task review a brief local correctness/scope check and let documentation-only P3 findings remain advisory.

## Scope

Remove routine Reveal enrichment from task-reviewer. Focus on the exact task delta and directly affected boundaries. Align developer repair loops and shipping handoffs so documentation-only P3 advice does not block completion. Preserve the independent cumulative feature gate.

## Non-goals / Later

Do not remove task review or change feature-review readiness thresholds. Do not redesign Git baseline capture.

## Constraints / Caveats

Use the approved decisions and testing policy in `../../feature.md`. This toolkit is under
development; breaking workflow changes are acceptable. No visual design is needed. Keep this task
green without relying on a later task to repair a contradictory handoff.

## Dependent Tasks or Work

001-stage-aware-planning-and-testing.

## Likely Starting Points

Recheck these landmarks against the current tree during shaping:

- `task-reviewer/SKILL.md` — local review contract and report.
- `developer/SKILL.md` — review repair/completion loop.
- `ship-feature/SKILL.md` — review handoffs and log wording.
- `ship-task/SKILL.md` — local review verification.
- `task-reviewer/agents/openai.yaml` — review interface description.
- `docs/design-principles.md` — review cost and responsibilities.

## Expected Change Surface

Reviewer instructions, completion semantics, shipping records, and public descriptions. Preserve precise task attribution and the read-only review boundary.

## Open Questions

None.
