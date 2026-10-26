# Stage-aware planning and testing

## Context

Planning must favor KISS/YAGNI and carry deployment stage and risk-based testing decisions into execution.

## Objective

Align simplicity, compatibility decisions, test selection, and validation across the complete planning-to-implementation handoff.

## Scope

Update architect-feature and shape-spec to resolve and record deployment stage and breaking-change decisions. Carry the approved feature testing policy into developer, ship-task, ship-feature, and feature-reviewer expectations. Keep full validation at the independent feature gate. Align public documentation where needed.

## Non-goals / Later

Do not change task-review severity or archival behavior in this task. Do not add tests that match prose.

## Constraints / Caveats

Use the approved decisions and testing policy in `../../feature.md`. This toolkit is under
development; breaking workflow changes are acceptable. No visual design is needed. Keep this task
green without relying on a later task to repair a contradictory handoff.

## Dependent Tasks or Work

None.

## Likely Starting Points

Recheck these landmarks against the current tree during shaping:

- `architect-feature/SKILL.md` — feature discovery and task-brief handoff.
- `shape-spec/SKILL.md` — task policy and validation strategy.
- `developer/SKILL.md` — test and validation defaults.
- `ship-feature/SKILL.md` — validation selection and worker dispatch.
- `ship-task/SKILL.md` — single-task validation handoff.
- `feature-reviewer/SKILL.md` — assembled-feature testing expectations.
- `docs/design-principles.md` — public validation principles.
- `README.md` — workflow descriptions.

## Expected Change Surface

Planning and execution policy, validation-mode contracts, and public guidance. Preserve exact task baselines, review independence, and archive lifecycle.

## Open Questions

None.
