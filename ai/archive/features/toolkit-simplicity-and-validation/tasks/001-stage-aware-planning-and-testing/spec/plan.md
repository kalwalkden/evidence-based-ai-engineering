# Stage-aware Planning and Testing

## Scope and Decisions

Implement task 001 from the approved feature. The user explicitly classifies this toolkit as under
development and permits breaking workflow changes. Feature-level testing policy is authoritative.
No visual work is involved. Earlier tasks: none.

## Approach

- Add KISS/YAGNI and stage/compatibility discovery to architect-feature. Record stage, affected
  deployed contracts, breaking-change decisions, and testing direction in feature.md and carry
  relevant decisions into briefs.
- Have shape-spec inherit those decisions, resolve missing stage and breaking-change intent, and
  document the cheapest meaningful tests and exact validation commands. Source inspection remains
  the discovery mechanism; do not build tests to learn how the application works.
- Put concise, self-contained stage-sensitive testing guidance in the architect, shaper, and
  developer. Cover the approved exclusions, regression criteria, and five internal questions.
- Replace developer's full-by-default and ship-feature-intermediate modes with focused/full selected
  from recorded stage, task risk, and repository requirements. Focused applies to pre-production
  standalone, intermediate, and final tasks where useful. Production significant changes and
  feature-review repairs use full. Preserve full canonical independent feature validation.
- Update ship-task and ship-feature dispatch, reporting, and validation selection to the same
  contract. Do not retain a compatibility alias for the old mode. Preserve review semantics until
  task 002.
- Align feature-reviewer test expectations and public descriptions without changing readiness gates.

## Contracts and Unchanged Boundaries

Stage and approved breaking-change decisions flow feature.md -> brief/spec -> developer and shipping
validation. Unknown stage is a question, not implicit production or permission to break consumers.
Repository-required checks remain binding. Keep exact Git baselines, independent review, feature
status/archival ownership, and review severity unchanged.

## Validation

No new automated tests: behavior is prompt guidance, and matching wording would add little
confidence. Inspect the full task diff and search live skills for contradictory old validation
requirements. Run `scripts/check.sh lint prose validate` (AGENTS.md, scripts/check.sh); run the
canonical `scripts/check.sh validate test` and lint/prose again for the assembled feature gate.
Report unavailable tools or failed checks. This repository requires canonical checks; the new
consumer policy does not waive them.

## Open Questions

None.
