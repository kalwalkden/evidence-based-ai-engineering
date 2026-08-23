---
name: ship-feature
description: Run every remaining task of one approved feature to completion, not just the next one. Use when the user asks to ship, finish, or run a whole feature end to end from an explicit ai/features feature root, including requests like "ship this feature", "finish the whole feature", or "run all remaining tasks". Preflights feature and brief decisions before automation, shapes and implements each task with stage-specific models, then runs up to three independent feature-review attempts with bounded repair cycles, completion, and archival. For a single task that stops afterward, use ship-task instead.
---

# Ship Feature

Orchestrate one approved feature until it is complete and ready, not merely until its last task has
been attempted. Keep the primary context focused on routing, gates, progress, and verified state.
For every task, delegate current-tree shaping and implementation to separate workers so expensive
reasoning becomes a durable spec that a less expensive capable model can execute. Run the final
`$feature-reviewer` in an independent context.

## Require an Explicit Feature

Require an explicit feature root under `ai/features/`, either directly or inside an epic. A valid
feature root contains `feature.md`, `tasks.md`, and `tasks/`. Do not infer it from the branch, recent
conversation, or nearby files. Do not accept an epic root or standalone spec.

Read `feature.md`, `tasks.md`, and the task directory names before spawning workers. Confirm that
every task entry maps to one task directory containing `brief.md`. Stop and report malformed or
ambiguous inputs before changing implementation code.

## Run the Brief Preflight

On every invocation, including a resumed run or one whose tasks are already complete, audit
`feature.md` and every `brief.md` named by `tasks.md` before any branch change, ship-log creation or
append, model selection, baseline capture, worker spawn, review, status update, completion, or
archive action. When the feature belongs to an epic, also read applicable constraints and decisions
from its `epic.md`.

Read each artifact semantically. Identify explicit open-question sections and unresolved decisions
expressed elsewhere, including TBDs, requests for confirmation, unchosen alternatives, conditional
scope without a selected path, contradictions across artifacts, and user-owned decisions deferred
to a later worker. A stated preference such as “my lean” is not approval, and a generic instruction
to proceed does not waive a specific unresolved decision. An `Open Questions` section containing
`None.` is evidence, not a substitute for checking the rest of the artifact. Older briefs without
that section remain valid when their content is unambiguous.

Do not block on rhetoric, quoted examples, links, test cases, or a question already answered
unambiguously nearby. Leave bounded current-tree facts to `$shape-spec` only when either result stays
within approved scope and task order; express those as verification notes rather than open
questions.

Resolve factual questions through read-only repository inspection and record the evidence-backed
answer in the owning artifact. Never infer a product, scope, architecture, policy, risk, or
sequencing choice. When user input is required, report
`Preflight: Blocked — <count> unresolved decisions.`, then ask every known question together in one
numbered list grouped by feature or task. Stop before all later workflow stages.

After the user answers or explicitly defers every item, record each decision in the relevant durable
section, remove stale alternatives, and put deferrals under non-goals rather than open questions.
Re-run structural validation and this complete audit from disk; repeat until no blocker remains.
Do not create a ship-log entry for blocked or waiting preflight attempts. Once clear, report
`Preflight: Ready — no unresolved feature or brief questions.` and continue to the runtime and
branch gates without asking for redundant permission to start automation.

## Require the Orchestration Runtime

Require a runtime that can:

- Spawn a subagent with an explicitly selected model
- Wait for and steer that subagent
- Start the feature reviewer with no inherited implementation conversation

If any of those is unavailable, stop before implementation and report that this workflow cannot
preserve its model-routing and independent-review contract. Do not simulate independence in the
current context.

Prefer, but do not require:

- Per-subagent reasoning effort
- A background or parallel read-only discovery channel

When a preferred capability is unavailable, continue the workflow, apply the closest available
control, and disclose the gap once in the final report. Treat reasoning-effort guidance below as
advisory in that case rather than as a gate. Some runtimes expose model selection without exposing
reasoning effort; that alone must not stop the run.

## Pass the Branch Gate Once

Derive the feature slug from the feature root basename and inspect the current branch. Accept the
branch when it is exactly the slug, ends in `/<feature-slug>`, or begins with the slug followed by a
separator (`<feature-slug>-...`, `<feature-slug>_...`). A hosted runtime that derives the session's
working branch from the branch you selected commonly produces that last form.

Otherwise the branch is unexpected, and the response depends on whether this run can reach the user:

- **Interactive run:** warn the user and ask once whether to create or switch to a feature branch.
  Prefer the repository's branch convention, otherwise `<feature-slug>`. Do not start task
  work until the user answers. If the user declines, continue on the current branch.
- **Run that cannot reach the user** — an unattended, scheduled, or hosted session, including one
  whose environment marks it remote: never stop here. Continue on the current branch, record the
  branch name and the mismatch in `ship-log.md`, and state it once in the final report. A branch
  naming convention is not worth failing an automated run over.

Never create or switch branches on your own initiative in a hosted session. Such runtimes commonly
restrict pushes to the working branch the session started on, so a branch created inside the session
can strand the run's output where it cannot be pushed.

Tell every implementation worker that the parent already completed the branch gate so it must not
ask again. Do not create commits, push, or open a pull request unless the user explicitly requests
it, with one exception: in a hosted session, commit and push completed work to the session's own
working branch as described under "Persist the Run in a Hosted Session".

## Choose Models Deliberately

Honor explicit user choices for implementation model, review model, reasoning effort, speed, or
cost. Otherwise choose from models the runtime actually advertises; never invent an unavailable
model identifier.

Choose the shaping model before the spec exists. Classify the task from its brief, feature map,
constraints, relevant code, and dependencies:

- Use the general workhorse model for straightforward shaping with a clear code surface.
- Use the strongest capable model when shaping requires ambiguous architecture, security analysis,
  migrations, concurrency, broad cross-cutting reasoning, or difficult product decisions.

After shaping is complete, choose the implementation model from the approved spec package:

- Use the fastest efficient model only for clear, repetitive, low-risk execution with precise
  references and acceptance criteria.
- Use the general workhorse model by default for ordinary implementation, integration, tests, and
  repository-aware changes.
- Use the strongest capable model when the shaped spec still exposes difficult or high-risk
  implementation reasoning. Do not force a cheaper model when the task exceeds its likely capability.

Read `references/model-routing.md` for the per-runtime identifiers behind these tiers and the
reasoning-effort guidance for the current runtime. The tier decision lives here; that file is only
the lookup.

Before each spawn, state the selected model, stage, and one-line reason, plus the reasoning effort
when the runtime accepts one. Keep a compact per-task record of both shaping and implementation
selections for the final report. When the runtime exposes no reasoning-effort control, select the
model on the same criteria, record the effort as unavailable, and continue.

Choose the feature-review model only after seeing which models implemented the feature:

- Prefer a different capable model from the primary implementation model. A parent and subagent
  running the same inherited model are not a different model.
- Prefer the strongest capable review model for broad or risky features.
- If no different model is capable or available, use the strongest available model in a fresh
  context and disclose that model diversity was unavailable. Fresh context is mandatory; a
  different model is preferred.

Explicit model values passed at spawn time override general subagent defaults. Do not change the
user's persistent runtime configuration as part of this skill.

## Start Workers Without Inherited Conversation

Every worker must start without the implementation conversation that preceded it. The requirement is
the property, not any one runtime's flag for it:

- The worker sees the repository, the artifacts on disk, and the instruction it is given.
- It does not see prior workers' reasoning, the orchestration transcript, or a proposed answer.
- An explicitly selected model must survive the spawn.

In Codex, always use `fork_turns="none"`. Do not use a positive-history or full-history fork for any
shaping, implementation, repair, or feature-review worker, even when that fork would accept the
requested model override. In Claude Code, every new agent spawn is already a fresh context, so the
requirement is met by default. In any other runtime, use a mechanism only when it guarantees the
same no-inherited-conversation property and say once which mechanism you used.

If a runtime can only spawn workers that inherit the current conversation, stop; that defeats both
the model-routing and the independent-review contract.

## Ship Every Task Sequentially

Never run two write-capable workers concurrently in the same worktree. Read-heavy discovery may run
in parallel only when it cannot edit the same repository.

Sequential is the default because feature tasks usually share a code surface, and the baseline,
validation, and task-review contracts all assume one writer at a time. When a runtime can give each
worker its own git worktree, tasks with no declared dependency in `tasks.md` may run in parallel
there. Take that path only when the user asks for it or the wall-clock win is real, and only for
tasks whose change surfaces genuinely do not overlap. Merging the worktrees, revalidating the merged
result, and reviewing each task's delta afterward is the cost; on a shared surface it usually exceeds
the saving. Never treat per-worker worktrees as license to run two writers against the same one.

This context owns every user interaction. Workers may be unable to reach the user at all, and a
worker that blocks waiting for an answer it cannot receive will stall or guess. Require each worker
to stop and return an unresolved decision as a blocking question instead of asking it. Put that
question to the user here, then resume the same worker with the answer.

Only after preflight is Ready and the branch gate has passed, initialize
`<feature-root>/ship-log.md` as described in "Keep a Durable Run Log" before checking task status or
spawning a worker. Do this even when every task may already be complete, because the independent
review and final report still need a durable cycle record.

Immediately after initialization, append a new `ship-feature` run heading with an absolute UTC
start timestamp. This timestamp identifies this invocation. A resumed invocation appends a new run;
never continue or rewrite timing for an earlier run. Timing begins here and deliberately excludes
preflight and branch-gate waiting.

Before the first spawn, check whether any task is actually incomplete. If every task in `tasks.md` is
already complete, say so, skip this section entirely, and go straight to the independent feature
review. Do not re-shape, re-implement, or re-validate a completed task to confirm it. An
already-complete feature still needs its review, verdict, completion status, and archival, so this is
a skip to that gate, not an exit from the workflow.

Repeat until every task in `tasks.md` is complete:

1. Re-read `tasks.md` from disk and select the first incomplete task in implementation order.
2. Inspect its `brief.md`, dependencies, feature-level implementation map, and relevant completed
   tasks enough to select a shaping model.
3. Immediately before spawning, append a UTC shaping-start timestamp for this task. Spawn one shaping
   worker with the selected planner model. Start it with no inherited
   implementation conversation, using whatever mechanism the runtime provides for that; see
   "Start Workers Without Inherited Conversation" below. Give the worker the repository root, exact
   feature root, exact task path, and this instruction:

   ```text
   Use the shape-spec skill on the supplied exact task path. Read the feature artifacts, verify the
   brief's likely starting points against the current working tree, account for relevant completed
   tasks, and write a complete implementation handoff in spec/plan.md and spec/references.md. Include
   current file and symbol targets, the relevant call path, contracts and
   invariants, patterns, tests, expected unchanged boundaries, exact validation commands, and
   uncertainties. Do not modify production code, tests, task status, or feature status. Do not ask
   the user anything; you have no channel to them. If a material decision is unresolved, stop and
   return it as a blocking question with the options you considered. Return the task identifier,
   created or changed spec paths, resolved questions, and any blocker. Keep the return under about
   200 words; the spec files are the deliverable, so put any detail worth keeping in them rather than
   in the return.
   ```

4. Wait for the shaping worker. If it returns a blocking question, append a UTC user-wait start for
   this task immediately before putting the question to the user. When the user responds, append the
   UTC wait end and elapsed wait, then send the answer back to the same worker and require it to
   record the approved decision in the task spec or applicable feature artifact before finishing.
   When shaping completes, append its UTC end and elapsed wall-clock duration.
5. Re-read the complete task package directly. Require both spec files and verify that the
   implementation map is current, specific, and includes validation. Resume shaping if the handoff
   is missing, vague, or still requires broad repository rediscovery.
6. Choose the implementation model and reasoning effort from the completed spec, remaining
   uncertainty, risk, and size. Record the shaping and implementation choices separately.
7. Immediately before implementation, capture or require the worker to capture an exact read-only
   baseline of the tracked and untracked working-tree state. This baseline must distinguish the next
   task's changes from prior uncommitted task and user changes without mutating the real Git metadata,
   working tree, or commits. Use the temporary-index and temporary-object-directory recipe in
   `$developer`. Record the complete baseline bundle: before-tree SHA, baseline root and marker,
   temporary Git directory, empty Git-config path, real Git directory, working-tree path, and
   captured HEAD tree. Keep that bundle until task review finishes. Capture it after shaping,
   so the task's shaped `spec/` package falls outside the reviewed delta by design; the reviewer reads
   that package as intent, not as change.
8. Immediately before spawning, append a UTC implementation-and-local-review start timestamp for
   this task. Spawn a new implementation worker with no inherited implementation conversation. Give it the
   repository root, exact feature root, exact task path, and this instruction:

   ```text
   Use the developer skill on the supplied exact task path. The ship-feature parent already passed
   the branch gate and owns the final independent feature review. Read the full approved task
   package, verify its named paths and symbols against the current tree, and use the supplied
   pre-implementation baseline bundle unchanged, or capture one the same way before editing. The
   bundle contains <baseline-sha>, <baseline-root>, <baseline-marker>, <temporary-git-directory>,
   <empty-git-config>, <real-git-directory>, <working-tree>, and <captured-head-tree>. Implement
   exactly this task, run the required validation and full test suite, then capture the current tree
   in that temporary Git directory and invoke the task-reviewer skill locally with the delta from the
   original before-tree, so the verdict covers only this task's staged, unstaged, new, and deleted
   files. If review returns an in-scope finding, repair it, rerun validation and the final full test
   suite, capture a new after-tree through a fresh after-index path, and rerun task-reviewer from the
   original before-tree to the latest after-tree. Repeat until that exact latest target receives
   `No findings.` Only then update this task's status. Do not dispatch the feature-reviewer skill. Do
   not ask the user anything; you have
   no channel to them. If a material decision is unresolved, stop and return it as a blocking
   question with the options you considered. Clean up only the verified temporary baseline directory
   after review finishes. Return the task identifier, exact reviewed change target, changed paths,
   validation commands and exit statuses, exact local task-review verdict, unresolved findings
   count, status update, and any blocker. Keep the return under about 200 words:
   report these as short labeled values, not prose, and write any longer detail into the task
   package instead.
   ```

9. Wait for the implementation worker. If it returns a blocking question, append a UTC user-wait
   start for this task immediately before putting the question to the user. When the user responds,
   append the UTC wait end and elapsed wait, then send the answer back to the same worker and require
   it to record the approved decision in the task spec or applicable feature artifact before
   continuing. When the worker returns its final accepted result, append the UTC end and elapsed
   duration for implementation and local task review.
10. Re-read `tasks.md`, repository status, and relevant task artifacts directly. Use the worker's
   exact final reviewed change target, validation commands, exit statuses, and task-review verdict
   as evidence for results that are not persisted on disk. Require confirmation that the final
   after-tree was captured after the last implementation or repair edit; do not accept a vague
   completion summary or a verdict against an earlier tree.
11. Treat the task as complete only when its status is updated, required validation passed, and its
   local `$task-reviewer` pass has no unresolved finding. Resume the worker or rerun the missing
   check before advancing when any evidence is absent or ambiguous.
12. Append the task's entry to the run log before advancing. See "Keep a Durable Run Log".
13. In a hosted session, commit and push this task now, including its `tasks.md` status update and
   the `ship-log.md` entry from step 12. See "Persist the Run in a Hosted Session". Do this after
   both of those are written, never before the task's local review is clean, and never while a
   baseline bundle for it is still open.
14. If either worker stopped on a fixable in-scope failure, steer it or spawn a replacement worker with
   the failure evidence and continue. Do not skip ahead.

Do not stop because the feature has many tasks or the run has taken multiple turns. Continue while
safe, meaningful in-scope progress remains possible.

## Keep a Durable Run Log

This workflow spans many turns and many workers, so its own state must survive context loss the same
way task decisions do. Do not hold routing history, validation evidence, or cycle counts only in this
conversation.

Maintain `<feature-root>/ship-log.md`. At automated workflow start, after preflight is Ready and the
branch gate has passed, create it when absent with a short heading and the feature path before
checking task status or launching review. Never truncate an existing log or rewrite earlier entries.
Append after each task completes, immediately after every feature-review verdict returns, and after
every repair pass.

Use absolute UTC timestamps and simple wall-clock durations. The parent orchestrator takes every
clock reading; workers do not self-report duration. Append each stage start when it is taken so
timing survives context loss, then append its end and elapsed duration when it completes. Use
`unknown` rather than zero or an estimate for missing timing or counts.

Maintain one run-level count of known executions of the repository's canonical full validation.
Increment it only when returned or logged evidence identifies that command and its result. Include
repeated full validation after implementation corrections, repairs, and fresh feature reviews when
the evidence supports it. Record `unknown` in the terminal summary if a complete count cannot be
established from durable evidence.

When the log is first created for a partially or fully completed feature, append a resume-state entry
listing tasks already marked complete. Record their model and validation history as `unknown —
predates ship log` unless durable evidence provides those values. Do not invent missing history.

Record per task:

- Task identifier and title
- Shaping model and reasoning effort, or `effort: unavailable`
- Implementation model and reasoning effort, or `effort: unavailable`
- Validation commands and exit statuses
- Local task-review verdict and unresolved findings count
- Any approved user decision, with a pointer to the artifact that records it in full
- Shaping start, end, and elapsed duration
- Implementation-and-local-review start, end, and elapsed duration
- Any separately observed user wait during this task

Record per feature-review cycle:

- Cycle number, review model and effort, and verdict
- Validation commands and exit statuses from that reviewer context
- Verified findings and the task each was routed to
- `Repairs: none` for a Ready verdict, `Repairs: pending` for a Not ready verdict on attempts 1–2,
  or `Repairs: not run — attempt limit reached` for a Not ready verdict on attempt 3
- Feature-review start, end, and elapsed duration
- Any separately observed user wait during this cycle

After repairs for a Not ready cycle, append a separate repair entry with the cycle number, changes
made, owning tasks, revalidation commands and results, and repair start, end, and elapsed duration.
Do not delay or rewrite the original review-cycle entry while waiting for repairs.

At a terminal state reached after the run starts, append one short timing summary before the final
report. Terminal states are a Ready verdict followed by completion/archive handoff, a third Not
ready verdict, or a genuine blocker or denied permission that ends safe progress. A temporary
blocking question is a pause, not a terminal state. Before appending, check this run's earlier
entries and do not duplicate an existing terminal timing summary. The summary must contain:

- Run start, run end, and total elapsed duration
- Completed task, review, and repair stages with their elapsed durations
- Total observed user wait, or `none observed`
- Known canonical full-validation executions, or `unknown`
- Longest completed stage, or `unknown` when the available durations are incomplete

Append the successful-run summary to the log at its verified final artifact path before building the
final report. For a stopped run, append it at the verified active feature path.

At the start of every turn, and before the final report, read this log from disk. Treat it as the
source of truth for what already happened; use conversation memory only to supplement it. When the
log and this context disagree, trust the log and say so.

The log is a run artifact, not a planning artifact. Leave it beside `feature.md` so it archives with
the feature.

## Launch the Independent Feature Review

After all tasks are complete, confirm that the latest project-wide validation covers the assembled
working tree. The independent `$feature-reviewer` must run the canonical full validation in its own
fresh context before issuing a ready verdict; conversational evidence from task workers is not
available there. The orchestrator may run validation earlier for faster feedback, but that does not
replace the reviewer's final run.

Resolve or obtain the feature comparison base before review. Honor a base branch or commit supplied
by the user. Otherwise let `$feature-reviewer` resolve the remote default branch, and surface any
ambiguity it reports.

Immediately before spawning, append a UTC feature-review start timestamp for the next cycle. Spawn a
new feature-review agent with the selected review model and reasoning effort. Start it with
no inherited conversation history. Pass only:

- The repository root
- The exact current feature root
- The user-specified comparison target, when present
- The instruction to use `$feature-reviewer`

Use a prompt equivalent to:

```text
Use the feature-reviewer skill on <feature-root>. Work in a fresh independent context. Read the raw
feature artifacts, cumulative diff, source, tests, and validation evidence directly. Do not rely on
any implementation summary. Run the repository's canonical full validation yourself before a ready
verdict. Use <comparison-target> when supplied. Do not ask the user anything; you have no channel to
them. If an ambiguous comparison target or contradictory requirement blocks the verdict, stop and
return it as a blocking question. Return verified findings, validation commands and exit statuses,
the exact feature-readiness verdict, and the exact reviewed feature path. Do not modify feature
status, orchestration logs, or artifact locations, and do not invoke archive-work-artifact. Findings
must be complete enough to act on, but keep everything else terse.
```

Do not pass task-worker reasoning, expected findings, repair hypotheses, or a proposed verdict.
Wait for the reviewer and inspect its returned verdict. If it returns a blocking question instead
of a verdict, append a UTC user-wait start for that cycle immediately before putting the question to
the user. When the user responds, append the UTC wait end and elapsed wait, then resume the same
reviewer with the answer; do not log a review cycle until a verdict exists. When a verdict returns,
append the UTC review end and elapsed wall-clock duration.

Immediately after a verdict returns, verify that the reviewer left the feature at its active path and
append the complete cycle entry to its `ship-log.md`. Record `Repairs: none` for Ready and `Repairs:
pending` for Not ready. For a Not ready verdict on attempt 3, instead record `Repairs: not run —
attempt limit reached`. Complete this append before routing findings, changing feature status,
invoking archival, or producing the final report. Do not perform the adversarial review again inside
the orchestration context.

Treat each returned feature-readiness verdict as one independent-review attempt. Blocking questions
that return no verdict do not consume an attempt. Before spawning a reviewer, count the completed
feature-review cycle entries in `ship-log.md`; never launch an attempt when three verdict cycles are
already recorded. If three cycles are already recorded and the latest verdict is Not ready, append
the exhaustion entry if it is absent, append the terminal timing summary, and alert the user as
described in "Final Report". This count is durable across turns and resumed runs.

## Repair Within Three Review Attempts

If the reviewer returns `Feature readiness: Not ready`:

1. Read the just-appended cycle number from `ship-log.md`. If it is attempt 3, stop immediately:
   do not launch repairs or another independent reviewer. Leave the feature active and unarchived,
   append an `Independent review attempts exhausted` entry containing the unresolved findings and
   latest validation results, append the terminal timing summary, and alert the user as described in
   "Final Report".
2. Confirm that feature status and artifacts remain active and unarchived.
3. Route each verified finding to the narrowest owning task when possible.
4. Immediately before starting repairs, append a UTC repair-start timestamp for this cycle. Spawn a
   suitably capable repair worker with the raw finding, feature root, owning task package,
   and cited source locations. Tell it the `$ship-feature` parent owns feature review, so it must not
   dispatch `$feature-reviewer`, and that it must return an unresolved decision as a blocking
   question rather than asking the user.
5. Use `$developer` and local `$task-reviewer` for a correction owned by one task. For a genuinely
   cross-task integration defect, make the smallest feature-scoped correction, review every
   affected task package locally, and avoid unrelated refactoring.
6. Run affected tests and the canonical full validation after all repairs.
7. Append a repair entry to the run log for this cycle: changes made, owning tasks, revalidation
   commands and results, plus the UTC repair end and elapsed duration. Keep the earlier review-cycle
   verdict entry unchanged.
8. Launch a brand-new feature-review context through the complete independent-review procedure
   above, including its no-inherited-conversation requirement. Never resume or reuse the
   previous reviewer for the readiness verdict, and never pass it the repair conversation.

Repeat repair and fresh-review cycles until the verdict is `Feature readiness: Ready` or the third
independent-review attempt returns `Feature readiness: Not ready`. Never run a fourth attempt. Also
stop when a user decision, denied permission, missing external dependency, ambiguous comparison
target, contradictory approved requirements, or exhausted safe repair path prevents further
progress. Before reporting that terminal blocker, append the terminal timing summary at the active
feature path. Report the exact blocker and leave the feature active.

## Verify Completion and Archival

Let `$feature-reviewer` own only the independent readiness verdict. This `$ship-feature`
orchestrator owns the resulting state transition and `$archive-work-artifact` handoff. After the
Ready cycle has been appended to `ship-log.md`:

1. Verify the feature remains at the active feature root and the reviewer did not modify status or
   artifact locations.
2. Mark the feature complete in `feature.md`, preserving the existing status format. If no format
   exists, add the smallest clear completion note.
3. Invoke/use `$archive-work-artifact` on the feature root with feature completion confirmed. Do not
   hand-move it or overwrite an existing archive target.
4. Locate and verify the final artifact path returned by the archive handoff.
5. Append the terminal timing summary to `ship-log.md` at that verified final path.
6. For an ungrouped feature, verify the feature was archived without overwriting an existing
   artifact.
7. For a grouped feature whose epic remains active, verify the epic checklist was updated and
   report that no directory moved.
8. If completion or archival fails after a Ready verdict, continue the safe handoff when possible or
   append the terminal timing summary at the verified active path and report that operational failure
   separately. Do not rerun implementation or independent review merely because the post-verdict
   state transition failed.

The feature is done only when all tasks are complete, final validation is material, the independent
review verdict is ready, completion status is recorded, and archival or grouped-epic handoff is
verified.

## Final Report

Build this report from the `ship-log.md` under the feature's verified final active or archived path,
not from memory of the run. Report concisely:

- Final feature and artifact path
- Tasks completed and the shaping model/reasoning plus implementation model/reasoning used for each
- Final validation performed
- Number of independent feature-review cycles and review model used for each
- Repairs made in response to feature findings
- Completion and archive or epic-checklist result
- Run elapsed duration and longest completed stage
- Any preferred runtime capability that was unavailable, stated once
- Material residual risks, if any

If all three independent-review attempts returned `Feature readiness: Not ready`, lead with an
explicit alert that the feature failed independent verification after three attempts and was not
shipped. Include the active feature path, the unresolved findings from attempt 3, the latest
validation commands and exit statuses, and the next user decision or intervention needed. State
that no fourth attempt was run and that completion or archival did not occur. Do not bury this alert
under the normal completion summary or imply that the feature is ready.

Produce a concise commit message. In a local run, stop there and do not commit unless explicitly
asked. In a hosted session, the run has already been committed incrementally, so use this message
for the final completion commit described below and report the branch every commit went to.

## Persist the Run in a Hosted Session

A hosted session works in a disposable clone on a working branch the runtime created for it, and
that clone is reclaimed when the session expires or stops. Everything this workflow produces —
`ship-log.md`, each task's `spec/` package, the implementation itself, and the archival move —
lives only on that VM until it is pushed. A commit is not enough on its own: local commits are on
the same disk and die with it. Only a push puts the work somewhere that survives the session.

So in a hosted session, commit **and push** to the session's own working branch at each of these
points, rather than once at the end:

- After each task is complete — status updated, validation passed, local task review clean, and
  its `ship-log.md` entry appended. This is step 13 of "Ship Every Task Sequentially".
- After each repair pass that answers a feature-review finding, once its validation is green.
- After completion status and archival or epic handoff are verified, as the run's final commit.

Commit the whole tree state at that moment, always including the `ship-log.md` entry for what just
finished, so the durable run record advances with the work it describes and a resumed run reads
timing, routing, and cycle counts from the branch rather than from a lost VM. Message each commit
for what it contains — the task identifier, the repair, or the final report's concise message —
and push it immediately; a commit that is never pushed protects nothing. A run that ends early then
leaves every finished task durable on the branch, and loses at most the task in flight.

Committing between tasks is safe for the per-task baseline. That baseline compares captured tree
states through a temporary index, so it measures one task's delta identically whether prior tasks
are committed or uncommitted; committing simply leaves less prior uncommitted state to distinguish.
Still take each commit only after that task's review is finished and its baseline bundle is
released, so nothing captures a tree mid-repair.

A lifecycle or stop-hook request to commit is not a task or repair boundary. Never commit
implementation code while editing, validation, or review is incomplete. If the runtime requires an
interim persistence response, commit and push only the updated run log, clearly recording that the
task or repair remains in flight; otherwise defer persistence until the next verified boundary.

If a push is rejected, do not work around it by creating or switching branches — that strands the
work further. Record the rejection and its reason in `ship-log.md`, keep committing locally at the
same points so the history is ready to push, surface it once in the final report, and continue.

Report the branch and the final commit in the final report.

Nothing here widens any other permission. Never push to a branch other than the session's own, never
open a pull request, never merge, and never commit in a local run. In a local run the user's working
tree is shared with their own work and other agents, so an uninvited commit there is a different act
entirely, and this exception does not reach it.
