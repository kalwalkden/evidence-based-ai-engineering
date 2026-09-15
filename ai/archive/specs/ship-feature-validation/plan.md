# Ship-feature validation scope

## Scope

Update the existing orchestration and implementation skills so intermediate tasks inside
`$ship-feature` use focused validation. Preserve mandatory full-suite validation for the task that
finishes the remaining feature work and mandatory independent full validation before feature
readiness. This is one standalone, non-visual task; no visual design is needed.

The user's request is the equivalent scoped task input. This package is a planning handoff;
implementation has not begun.

## Decisions, constraints, and provenance

- **User requirement:** Remove the requirement to run the whole test suite at every intermediate
  `$ship-feature` task boundary. Keep it for final review of the last task and independent review.
- **Design decision:** Extend `$developer` with an explicit, narrowly scoped validation mode rather
  than introduce another developer skill. Implementation, baseline capture, task review, status,
  and archival behavior are shared; duplicating them would create unnecessary maintenance work.
- **Scope interpretation:** Direct `$developer`, standalone tasks, and `$ship-task` retain their
  current full-suite default. Only a verified intermediate task dispatched by `$ship-feature`
  qualifies for focused validation.
- **Repository constraint:** Preserve tasks that can independently keep the project correct.
  `architect-feature/SKILL.md` and `docs/design-principles.md` prohibit deliberately broken
  intermediate states. Deferring a full run does not authorize ignoring known failures.
- **Existing contract:** Every task still needs an exact baseline, local `$task-reviewer` pass,
  repairs and renewed review of the latest target, and passing required checks before completion.
- **Existing contract:** `feature-reviewer/SKILL.md` requires fresh-context canonical full
  validation. Keep that independent execution and its blocking failure behavior intact.
- **Existing contract:** Feature-review repairs retain affected tests and canonical full
  validation before a new independent review. They are not intermediate-task exemptions, even
  when the finding belongs to an early task.
- **Evidence:** Current behavior and all named sections were inspected in the working tree at
  shaping time. No external guidance was selected. No earlier task in this change exists.

## Intended behavior

| Context | Required validation before task completion or verdict |
| --- | --- |
| Intermediate task explicitly dispatched by `$ship-feature` | Relevant task tests, affected integration or regression checks, and applicable lint/type checks |
| Task that completes all remaining feature tasks, including a one-task feature | Full test suite plus applicable canonical checks before final local task review |
| Repair during intermediate local task review | Rerun required focused checks against the repaired result |
| Repair during final-task local review | Rerun full suite and applicable checks against the repaired result |
| Feature-review repair, regardless of owning task | Preserve full validation requirements before independent re-review |
| Independent feature review | Reviewer runs canonical full validation itself, including the full test suite |
| Direct developer, standalone spec, or ship-task | Existing full-suite requirement |
| All tasks complete when ship-feature resumes | Preserve skip of completed task work; proceed to independent full validation and review |

Focused validation is a minimum, not a prohibition on broader tests when the change requires them.
Keep stricter applicable repository requirements. A known failure remains a blocker. Never report
that the whole suite passed when only a subset ran.

## Implementation approach

### 1. Define the developer validation contract

Edit `developer/SKILL.md`, chiefly `Role`, `Core Rules`, `Validation`, `Review Loop`, and
`Completion Report`:

- Centralize the policy under `Validation` with `full` as the default and
  `ship-feature-intermediate` as the explicit exception.
- Accept the exception only when the caller identifies itself as the `$ship-feature` parent,
  supplies the exact feature/task paths, and on-disk `tasks.md` confirms another task will remain
  incomplete after this task. Feature-folder membership alone is insufficient.
- Missing, ambiguous, stale, or ineligible mode information resolves to `full`. Repairs responding
  to independent feature review use `full` regardless of task position.
- Discover both focused commands and the canonical full-suite/full-validation commands. In focused
  mode, choose meaningful checks from the spec and actual change surface; justify their coverage.
  If no useful subset exists, use the full command. For a repository without tests, identify that
  fact and run appropriate available checks; final gates retain project-wide fallback validation.
- Replace each unconditional full-suite instruction with a reference to this policy, including
  the role sentence, core rule, validation bullets, and review-loop repair instruction. Do not
  leave conflicting absolute instructions elsewhere in the skill.
- Before final-task review and after its repairs, full-suite results must cover the current
  assembled implementation. Preserve baseline and latest-after-tree review semantics.
- Apply the selected policy consistently before a commit or completion report. This includes
  existing authorized hosted-session commits; it introduces no new permission to commit.
- Report mode, commands, exit statuses, coverage limits, and whether the full suite was deferred.

### 2. Pass and verify the policy in ship-feature

Edit `ship-feature/SKILL.md`, chiefly `Ship Every Task Sequentially`, `Keep a Durable Run Log`,
`Launch the Independent Feature Review`, and `Repair Within Three Review Attempts`:

- Determine task position from the current `tasks.md`, not the task number or remembered state.
  The last remaining task uses `full`, including on resumed runs and one-task features.
- Give the shaping worker this validation context. Require `spec/plan.md` and
  `spec/references.md` to distinguish checks required now from full commands deferred to final
  gates. Keep both command sets concrete. No generic shape-spec policy change is necessary.
- Verify that distinction when accepting the spec. Re-read task status before implementation;
  correct stale policy in the handoff if the remaining work changed.
- Replace the implementation worker prompt's unconditional full runs, including repair wording,
  with the explicit mode and policy. Keep local review and completion gates for every task.
- Require the worker result and durable per-task log to identify the mode and actual commands,
  results, and full-suite deferral. Check these before advancing; a bare completion claim is
  insufficient. Keep existing execution-count semantics: focused runs do not count as canonical
  full-validation runs, and unknown historical counts remain unknown.
- Retain full validation at the final-task gate and the independent review gate. Avoid an extra
  parent rerun when current final-task evidence already covers the assembled implementation.
  Preserve the existing all-tasks-complete resume path directly to independent review.
- Pass `full` explicitly to feature-review repair workers so early task ownership cannot reactivate
  the intermediate exception. Preserve canonical full validation after all repairs and another
  fresh reviewer run before readiness.

### 3. Keep explanatory documentation aligned

Add a concise distinction to `docs/design-principles.md`, under `Verification should match the
claim`: intermediate whole-feature work uses focused validation, the final task and independent
feature review retain full checks, and individual task execution keeps the full default.

Keep `feature-reviewer/SKILL.md`, `task-reviewer/SKILL.md`, `ship-task/SKILL.md`, skill manifests,
installation lists, model routing, and check tooling unchanged unless focused verification exposes
a direct contradiction. None was found during shaping. Do not relax independent review or task
decomposition rules.

## Validation and acceptance

This changes agent instructions, not executable behavior. The existing structural validator does
not prove orchestration semantics. Do not add tests that merely assert matching prose strings.

Review the changed instructions against every row of the behavior table, including these edges:

1. A three-task feature selects focused, focused, full; every task still receives local review.
2. One remaining task selects full, irrespective of its numeric position or earlier run history.
3. A direct developer invocation on a feature task defaults to full.
4. An intermediate repair retains focused mode; a final-task repair reruns the full suite.
5. Independent-review repairs to the first task use full validation, followed by a fresh reviewer
   that runs full validation again before Ready.
6. Missing mode, incorrect feature/task paths, or stale last-task status cannot waive full checks.
7. Focused failures prevent completion; final full-suite failures prevent completion/readiness.
8. All-complete resumes retain independent full validation without reopening completed tasks.
9. Ship logs distinguish deferred checks from successful runs and preserve truthful counts.
10. Canonical full validation must include the full test suite; run it separately if the aggregate
    command omits tests. Do not mistake a lint-only command for full-suite evidence.

Run `scripts/check.sh lint prose` and `scripts/check.sh validate test` after implementation.
`scripts/check.sh` is the equivalent all-groups command. Source: `AGENTS.md` and
`scripts/check.sh`; the default test matrix is Python 3.10 through 3.13. Record actual results and
any unavailable tooling. This standalone implementation uses the full default itself.

## Open questions and risks

No user decision is required to finish this spec. The main risk is inconsistent wording across
worker prompts, developer rules, and repair paths. Verify all full-suite references together.
Focused checks can miss cross-task regressions until the final gates; the retained final task run
and independent review are the required controls for that tradeoff.
