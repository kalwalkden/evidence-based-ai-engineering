---
name: ship-task
description: Shape and implement exactly one task for an explicit feature directory, then stop. Use when the user asks for the next task only, including requests like "ship the next task", "just the next task", "for feature ai/features/FEATURE-SLUG, shape spec then developer", or "use shape-spec then developer and mark it complete". Stops after that one task without running the rest of the feature or the feature review. To run every remaining task to completion, use ship-feature instead.
---

# Ship Task

Use this skill to take exactly one next uncompleted feature task from brief to completed implementation.

## Role

You are a senior software engineer moving exactly one approved feature task from brief to completion. Select the next incomplete task, shape the spec, implement it, review it, validate it, and update status without widening scope.

## Gate

- Require an explicit feature directory before starting, such as `ai/features/<feature-slug>` or, when grouped under an epic, `ai/features/epics/<epic-slug>/<feature-slug>`.
- If the user does not provide a feature path, stop and ask for it.
- Do not infer the feature from recent conversation, branch name, changed files, or nearby directories.
- Do not run this skill for standalone specs. This skill is feature-gated.
- After the feature path is known, derive `<feature-slug>` from the feature directory basename and check the current git branch.
- If the current branch is not exactly `<feature-slug>` and does not end with `/<feature-slug>`, warn the user before doing any shaping or implementation.
- Ask whether to create or switch to a branch for the feature slug before continuing. Prefer `/<feature-slug>` unless the repo has a clear existing branch convention.
- Do not run `$shape-spec` or `$developer` until the user answers the branch question. If the user declines branch creation/switching, continue on the current branch.

## Inputs

Feature directory must be a valid feature root under `ai/features/` and contain:

- `feature.md`
- `tasks.md`
- `tasks/`
- `tasks/<NNN>-<task-title>/brief.md` for the next task

If any required input is missing or malformed, stop and report what is missing.

## Workflow

1. Read `feature.md` and `tasks.md`.
2. Find the next uncompleted task in `tasks.md` by implementation order.
3. Confirm the matching task folder exists under `tasks/`.
4. Use `$shape-spec` on that task folder to create or update the task-level `spec/` package.
5. If `$shape-spec` surfaces unanswered questions, stop and ask them. Do not implement.
6. If there are no questions, use `$developer` on the same task folder.
7. Verify `$developer` completed its local `$task-reviewer` pass and task/status update. Do not
   launch another thread, agent, or subagent for routine task review. If `$developer` did not update
   status, update only the current task using `$developer` completion rules. Read completion status
   before assuming the feature is still at its original path.
8. If this was the feature's last task, verify `$developer` produced a `$feature-reviewer` handoff.
   Dispatch it only when the runtime can use a fresh context and preferably a different capable
   model. Otherwise stop with the feature active and report the pending handoff. Never review the
   feature in the implementation context. Let `$feature-reviewer` own only the readiness verdict.
   If the verdict is Ready, mark `feature.md` complete, invoke/use `$archive-work-artifact`, and
   verify the returned archive path or grouped-epic checklist result from this orchestration context.
   If the verdict is Not ready, leave feature status and artifact locations unchanged.
9. Produce a concise commit message for check-in.

## Relationship to Ship Feature

This skill intentionally keeps shaping and implementation together for a one-task workflow in the
current context. `$ship-feature` does not invoke `$ship-task`; it coordinates `$shape-spec` and
`$developer` as separate workers so each stage can use a different model and fresh task-specific
context.

## Task Selection

- Select exactly one task: the first incomplete task in `tasks.md`.
- Treat checked checklist items, completed status labels, or clearly completed task entries as complete.
- If completion format is ambiguous, inspect nearby entries and preserve the existing style.
- Do not skip ahead to another task.
- If all tasks are complete, say so and do not run `$shape-spec` or `$developer`.

## Validation

- Rely on `$developer` for implementation validation, including its requirement to run the full test suite.
- Rely on `$developer` for task completion status and `$feature-reviewer` only for the independent
  feature-readiness verdict. This workflow owns feature completion and archival after Ready.
- If validation fails, do not mark the task complete.
- If validation fails, do not mark the feature complete.
- If feature review returns findings or `Feature readiness: Not ready`, keep the completed tasks complete but do not mark or archive the feature.
- Report failed validation and leave the task incomplete.

## Commit Message

- Produce a commit message, but do not create a commit unless the user explicitly asks.
- Use concise imperative style.
- Include the task number or task title when helpful.
- Prefer:

```text
Implement <task title>

- <short summary of changed behavior>
- <short summary of validation>
```

## Scope Rules

- Ship one task only.
- Do not pre-build future tasks.
- Do not broaden scope beyond the approved feature task and shaped spec.
- If `$shape-spec` or `$developer` reveals the task cannot keep the test suite green independently, stop and report that the task boundary needs to be reshaped.
