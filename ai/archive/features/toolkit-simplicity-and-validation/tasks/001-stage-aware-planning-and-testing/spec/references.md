# Implementation References

## Primary Edit Targets

- architect-feature/SKILL.md — Priorities, discovery/alignment, plan and brief guidance.
- shape-spec/SKILL.md — Workflow, Planning Rules, plan.md and references.md guidance.
- developer/SKILL.md — Testing Policy, Validation, Core Rules.
- ship-feature/SKILL.md — Select Validation Per Task and shaping/implementation prompts.
- ship-task/SKILL.md — Validation handoff.
- feature-reviewer/SKILL.md — Review the Assembled Feature.
- docs/design-principles.md and README.md — public workflow expectations.

## Entry Point and Contracts

Feature decisions feed task specs; developer and shipping consume the recorded testing and validation
strategy. The existing full/ship-feature-intermediate distinction is an instruction contract,
not executable code; replace all live consumers together with focused/full. Archived artifacts
remain historical. No external guidance is selected.

## Tests and Validation Commands

No useful prose assertion tests. `scripts/check.sh lint prose validate` checks these instruction
surfaces; full assembled validation also uses `scripts/check.sh validate test`, sourced from
AGENTS.md and scripts/check.sh. Archive Python behavior remains unchanged in this task.

## Expected Unchanged Boundaries

Git baseline capture, review severity and attribution, archival and installer behavior, independent
full feature validation, and bounded feature repair cycles.

## Uncertainties to Verify

Recheck every shipping prompt and report field for stale mode names or unconditional full-suite
requirements after edits. Preserve explicit full checks for independent review and repairs.
