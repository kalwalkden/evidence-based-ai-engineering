# Implementation References

## Primary Edit Targets

- task-reviewer/SKILL.md — Resolve the Task/Change, Reveal enrichment, review contract, report.
- developer/SKILL.md — Review Loop repair and completion conditions.
- ship-feature/SKILL.md — implementation prompt, completion checks, log fields, persistence wording.
- ship-task/SKILL.md — local review handoff verification.
- task-reviewer/agents/openai.yaml — task-review display/default prompt.
- docs/design-principles.md and README.md — public review descriptions.

## Contracts and Flow

Task reviewer returns Pass or Needs fixes plus blocking/advisory findings; developer and shipping
honor this verdict. Documentation-only P3 advice is non-blocking, not silently discarded. Feature
review readiness continues requiring no findings. Task 001 established focused/full validation.

## Expected Unchanged Boundaries

Git baseline capture and cleanup, exact review attribution, read-only review, independent feature
review threshold, validation-mode selection, and archival.

## Tests and Validation Commands

`scripts/check.sh lint prose validate` from AGENTS.md/scripts/check.sh. No new test fixtures or
wording assertions. Review the exact delta, with directly affected call sites/instructions.

## Uncertainties to Verify

Search every developer/shipping no-findings requirement and unresolved finding counter so advisory
P3 documentation does not still trigger repair or block completion downstream.
