# Toolkit Simplicity and Validation

Status: Complete — implementation and independent feature review passed.

## Requirements

Make the toolkit favor the smallest correct implementation for the work being designed, with
testing and compatibility decisions proportional to deployment stage and real risk.

1. Add explicit KISS and YAGNI guidance to `architect-feature` and `shape-spec`. Avoid speculative
   abstractions, future-proofing, compatibility layers, and support for hypothetical consumers.
   Preserve compatibility when deployed consumers or approved requirements justify it.
2. Ask whether the affected project or feature is under development / pre-production or deployed /
   production. Record the answer durably in the feature plan and carry it into task specs.
   Standalone shaping must resolve the same decision. Reuse an explicit recorded answer rather
   than asking again at each stage. A feature in development must still account for any deployed
   contracts it touches.
3. For pre-production work, optimize for development speed and prefer targeted validation. Ask
   what approach to take when breaking APIs, integrations, or existing behavior is implicated;
   do not silently assume either compatibility layers or permission to break consumers.
4. For production work, preserve backwards compatibility unless explicitly changing it. Treat
   database migrations, APIs, integrations, existing behavior, and external side effects
   conservatively. Use stronger integration coverage and critical-workflow E2E coverage, and run
   broader suites before completing significant changes.
5. Keep per-task review as a brief local check of the actual diff, scope, and directly affected
   boundaries. Reserve cumulative integration and cross-task readiness review for the independent
   feature reviewer. Documentation-only P3 findings must not fail task review or force repair loops.
6. Archive through filesystem moves, including inside Git worktrees. Leave staging and Git move
   handling to the user while preserving collision and artifact-completion safeguards.

## Approved Decisions

- Feature slug: `toolkit-simplicity-and-validation`; one ungrouped feature.
- Keep a brief local per-task check rather than removing task review.
- This toolkit is still evolving; breaking workflow changes are acceptable for these updates.
- Use YAGNI alongside KISS as the requested simplicity principles.
- No visual design is needed: this changes agent instructions and archival behavior.

## Testing Policy to Carry Through the Workflow

Prefer the cheapest test that gives meaningful confidence. Do not add tests merely because code
changed, to increase coverage, or as a substitute for understanding the application by inspecting
its source and existing evidence. Inspect existing coverage before proposing additions.

- Use unit tests for non-trivial business/domain logic.
- Use integration tests for important boundaries: ERP integrations, database behavior, email
  processing, parsing, authentication, and external APIs.
- Use E2E tests selectively for critical workflows, such as receiving/processing orders, approving
  orders, submitting orders to an ERP, authentication/organization access, and critical customer
  or product resolution. Do not add E2E tests automatically for every feature or bug fix.
- Add regression tests when a bug reveals a meaningful invariant, risks silent data corruption or
  duplicate external actions, is likely to recur, is hard to notice manually, or affects
  business-critical behavior. Do not automatically test every bug.

For pre-production work, add tests only for meaningful business logic, complex behavior, data
integrity, or behavior that is realistically easy to break. Avoid excessive or low-value tests;
prefer targeted checks over running or expanding the full suite by default.

For production work, increase regression coverage for meaningful production bugs, favor stronger
integration coverage, and maintain E2E coverage for critical workflows. Production still does not
justify tests of every implementation detail.

Across all stages, avoid redundant coverage across layers, Tailwind/CSS class assertions, exact
markup structure unless behavior depends on it, trivial rendering, simple getters/setters,
framework behavior, straightforward CRUD wiring, components without meaningful logic, E2E tests
for minor UI changes, and snapshots without explicit usefulness.

Before adding a test, ask internally:

1. What meaningful behavior does it protect?
2. Could that behavior realistically regress?
3. Is it already covered elsewhere?
4. Would the test constrain harmless refactoring?
5. Is the maintenance cost justified at this product stage?

If the justification is unclear, do not add the test. Record concise test and validation decisions,
including when no new test is warranted; do not create a lengthy checklist for every change.

## Approach

Update planning and execution together so downstream defaults cannot undo the approved testing
policy. `architect-feature` records stage, compatibility decisions, and testing direction;
`shape-spec` turns those into task-specific test choices and validation commands. `developer`,
`ship-task`, and `ship-feature` honor that policy instead of requiring full-suite execution for
every task regardless of stage. Explicit repository-required checks remain binding; known failures
must not be ignored.

Retain canonical full validation at the independent feature-readiness gate. Pre-production tasks
can use focused checks, including standalone and final implementation tasks; the separate assembled
feature gate still validates the complete result. Production changes use broader validation when
their significance and affected boundaries warrant it.

Make routine task review a narrow in-context pass. Remove the automatic Reveal discovery and
structural pass from this skill. Inspect the exact task delta and enough nearby source/contracts to
catch concrete local defects, scope drift, and violated approved constraints. Reuse validation
evidence unless a gap or defect requires another check. Do not repeat feature-wide discovery or
the cumulative feature review at every task.

Replace the developer loop's literal `No findings.` completion requirement with no unresolved
blocking findings. Report documentation-only P3 observations as advisory and permit task completion
without repairing them. Keep other severity semantics and the independent feature-readiness
threshold unchanged; this request changes the per-task documentation gate.

Use the existing archival utility and its safeguards. Remove its Git-dependent move selection;
continue returning the filesystem move result through the existing report. Git may still locate
the repository root, but archival must not stage changes or mutate the Git index.

Update public workflow documentation and interface manifests where their current wording would
contradict the resulting behavior. Do not introduce a new policy engine or compatibility mode for
the old workflow.

## Implementation Map

- `architect-feature/SKILL.md`: priorities, discovery/alignment, feature planning, and task-brief
  handoff own stage and feature-wide compatibility/testing decisions.
- `shape-spec/SKILL.md`: workflow, planning rules, and `plan.md` guidance own current-tree task
  shaping and the concrete validation strategy.
- `developer/SKILL.md`: Testing Policy, Validation, and Review Loop currently default to full
  validation and require a literal no-findings verdict. These are execution-policy consumers.
- `task-reviewer/SKILL.md`: complete-target resolution, optional Reveal enrichment, local review
  contract, and severity reporting own the per-task check. Preserve correct diff attribution.
- `ship-task/SKILL.md`: implementation handoff currently repeats the full-suite requirement.
- `ship-feature/SKILL.md`: task validation selection, worker dispatch, repair instructions, and
  logging consume validation/review outcomes. Reconcile these with the revised policy; preserve
  independent feature review and its bounded repair cycles.
- `feature-reviewer/SKILL.md`: assembled-feature checks and canonical full-validation requirement
  define the retained cumulative gate. Its risk-based test expectations must respect the approved
  testing policy without automatically demanding tests for every change.
- `archive-work-artifact/scripts/archive_work_artifact.py`: `move_artifact` currently selects
  `git mv` inside worktrees and `shutil.move` elsewhere; `find_repo_root` independently uses Git.
- `archive-work-artifact/tests/test_archive_work_artifact.py`: existing subprocess-based lifecycle
  tests cover grouped epics, legacy layouts, and already-archived specs. Git index preservation
  is a meaningful boundary to validate when changing move behavior.
- `archive-work-artifact/SKILL.md`: Behavior currently promises Git moves.
- `README.md`, `docs/design-principles.md`, and affected `agents/openai.yaml` files: public
  descriptions and default prompts may need alignment after the skill edits.
- `ARCHITECTURE.md`, `scripts/check.sh`, and `scripts/validate_skills.py`: repository orientation,
  canonical validation, and structural skill contracts. No validation-tool redesign is needed.

These are verified landmarks, not a task-level edit prescription. Shaping must recheck the current
tree, including earlier completed tasks.

## Constraints

- Keep each task independently green; change coupled policy producers and consumers atomically.
- Keep approved decisions in artifacts; do not depend on conversation history.
- Preserve exact task-diff attribution and the read-only boundary of review.
- Preserve archive collision prevention, completion checks, dry runs, and epic checklist behavior.
- Existing legacy archive layouts are outside this simplification request.
- Do not automatically rewrite historical archived planning artifacts.
- Follow repository-required checks. For this feature, validate instruction consistency and skill
  structure, and use the existing archive tests plus focused coverage of the changed Git boundary.
  Do not add prose-matching tests that merely mirror instructions.

## Success Criteria

- Planning records deployment stage and explicit breaking-change decisions before downstream work
  depends on them. No skill reintroduces speculative compatibility or future scope by default.
- Planning, shaping, implementation, and shipping agree on risk-based testing and stage-sensitive
  validation. No new test is required solely because code changed.
- Per-task review is brief, checks real local behavior, and accepts documentation-only P3 advice
  without a mandatory repair. Feature review still checks cross-task integration independently.
- Archival works for tracked and untracked artifacts in Git worktrees using filesystem moves,
  without staging changes; existing artifact lifecycle safeguards continue to work.
- Public instructions describe the resulting workflow consistently.

## Non-goals / Out of Scope

- Removing per-task review, weakening the independent feature gate, or changing review models.
- Automatically deleting existing tests or changing consumer projects' test suites.
- Adding deployment detection tooling, coverage targets, or a generic policy configuration system.
- Redesigning archival layouts, the installer, CI, or Git baseline capture.
- UI changes or visual assets.

## Open Questions

None.
