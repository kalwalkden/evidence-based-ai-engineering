# Brief Local Task Review

## Scope and Decisions

Implement approved task 002 after task 001. Keep a brief local review, as explicitly selected by the
user. This toolkit is pre-production; breaking workflow changes are allowed. No visual work.

## Approach

- Remove automatic Reveal enrichment and broad review instructions from task-reviewer. Read the
  task contract and exact diff, follow directly affected boundaries only as needed, and reuse
  validation evidence. Keep exact tree-to-tree, uncommitted, and base-branch target resolution.
- Explicitly reserve cumulative cross-task integration/readiness review for feature-reviewer.
- Report documentation-only P3 findings as advisory. Add an unambiguous task verdict:
  `Task review: Pass` with no unresolved blocking findings, or `Task review: Needs fixes` otherwise.
  Keep `No findings.` when appropriate. Other findings retain existing blocking treatment.
- Make developer and shipping consumers accept Pass with advisory findings, repair only blockers,
  and count/log unresolved blocking and advisory findings separately. Preserve read-only review,
  exact attribution, current-context execution, and feature-review readiness semantics.
- Align reviewer interface metadata and public review guidance with the brief local contract.

## Validation

No new tests: this changes prompt guidance; tests that assert wording would add little value.
Run `scripts/check.sh lint prose validate` and inspect the full exact task delta plus all live
consumers of no-findings and unresolved-findings wording. Task 001 validation already passed; no
Python behavior changes yet. Canonical assembled feature validation remains mandatory later.

## Open Questions

None.
