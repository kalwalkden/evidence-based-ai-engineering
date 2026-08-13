---
name: feature-reviewer
description: Run an independent, adversarial, read-only feature-level readiness review after all tasks are implemented. Use for a valid feature root under ai/features or ai/archive/features; run in a fresh context and preferably with a different capable model from implementation, review the feature plan, visuals, every task package, and cumulative diff directly, and return findings plus a Ready or Not ready verdict without changing status or archiving artifacts.
---

# Feature Reviewer

Review one assembled feature before completion or archive. Treat `feature.md`, feature visuals, and
the full set of task packages as intended behavior. Treat the cumulative feature diff as implemented
behavior. Keep the entire skill read-only: do not modify implementation code or planning artifacts,
change status, append orchestration logs, move files, invoke archival, commit, push, or post review
comments. The calling workflow owns every state transition after it receives the verdict.

## Preserve Adversarial Independence

Run this skill in a fresh thread or agent that did not implement or materially direct the feature.
Prefer a different capable model or model family from implementation when the runtime permits model
selection. A different model strengthens the adversarial pass; a fresh context is the minimum
independence requirement.

If an implementation context invokes this skill, do not automatically spawn another reviewer.
Stop with the feature active and report that `$feature-reviewer` must be run separately. Do not
issue a ready verdict, change feature status, or archive the feature from that implementation
context. A user request to continue does not make the inherited context independent; start a fresh
reviewer or leave the handoff pending.

Work from the raw feature artifacts, cumulative diff, surrounding code, and validation evidence.
Do not substitute the implementation agent's summary or reasoning for direct inspection.

A `ship-log.md` in the feature root is an orchestration record, not review input. It reports what a
prior run believed it did. Do not read it before forming findings, do not treat its recorded
validation results as this context's validation evidence, and never let it narrow the review scope.
Consult it only after the verdict, and only to reconcile a discrepancy worth reporting.
Reconstruct intent from source artifacts, challenge implementation assumptions, and actively seek
counterexamples and cross-task failures.

## Gate

Require an explicit feature root under `ai/features/` or `ai/archive/features/`, either directly or
inside an epic. A valid feature root contains `feature.md`, `tasks.md`, and `tasks/`. Do not infer the
feature from the branch, recent conversation, or nearby files. Do not use this skill to review an
epic.

Require every feature task to be complete before a readiness review. If any task is incomplete,
stop and list it unless the user explicitly requests a partial feature review. A partial review
cannot produce a ready verdict.

## Read the Feature Package

Read before reviewing code:

- Applicable `AGENTS.md` and `CLAUDE.md` instructions
- `feature.md`, `tasks.md`, and feature-level `visuals/` when present
- Every task's `brief.md`
- Every task's `plan.md` or `spec/plan.md`
- Every task's `references.md` or `spec/references.md`
- Task-level `visuals/` or `spec/visuals/` when present
- Repository architecture documentation when it exists

Confirm that task directories and `tasks.md` entries agree. Treat a missing task package or a task
listed as complete without its required spec files as a readiness blocker unless the user explicitly
authorizes review against partial inputs.

## Resolve the Cumulative Change

Identify the repository root, current feature branch, and exact comparison target. Prefer a
user-specified base branch or commit. Otherwise resolve the repository's remote default branch and
state the assumption; stop if the comparison target is ambiguous.

Review what the feature branch would actually merge:

1. Resolve `git merge-base HEAD <comparison-ref>`.
2. Inspect the complete cumulative diff from that merge base through the working tree.
3. Inspect repository status, staged and unstaged changes, and the complete contents of every
   untracked file.
4. Enumerate the full changed-path set in the review inputs.

Do not review only the last task, only the latest commit, a diff summary, or a direct comparison to
a moving branch tip. If the feature implementation is not represented by the resolved target, stop
and ask for the correct base, commit range, or branch.

## Build a Structural Dossier with Reveal

Use Reveal as an optional, preferred enrichment after resolving the complete cumulative target:

1. Locate the `reveal` executable with the platform's command lookup. The package name is
   `reveal-cli`, but the executable is `reveal`.
2. If present, record `reveal --version` and inspect `reveal --agent-help`, falling back to
   `reveal --help`. Use only commands, flags, and URI adapters advertised by that installed binary.
   Do not assume that capabilities described by newer documentation are installed locally.
3. Filter the cumulative changed-path set to existing code files supported by
   `reveal --list-supported`. Keep deleted, binary, generated, and unsupported paths in the normal
   diff review even though Reveal cannot inspect them.
4. Outline all supported changed files with `reveal --stdin --outline`. Use
   `reveal <file> --typed` and `reveal <file> <changed-symbol>` to inspect containment and exact
   changed units. Run `reveal <file> --check --select B,S,C,E` on risk-bearing files when supported.
5. Use locally advertised structural adapters such as `ast://` and `imports://` to examine
   complexity, imports, and cross-task boundaries. Use richer facilities such as `calls://`,
   `diff://`, `reveal review`, or `reveal pack` only when the installed help explicitly exposes and
   documents them.
6. Build a concise dossier of changed symbols, callers or dependencies when available, containment,
   complexity deltas or hotspots, external boundaries, and detector results. Use that dossier with
   the raw target and feature constraints during the review pass.

Reveal provides structural evidence, not proof. Confirm every consequential signal by inspecting
the source, cumulative diff, affected call paths, tests, and runtime behavior. If Reveal is absent,
unsupported for the repository's languages, or fails, continue the complete feature review with
normal repository tools. Do not install it, block readiness solely because it is missing, or reduce
the review standard.

## Run the Defect Pass

Perform the complete defect-first pass directly in the fresh feature-reviewer context. Treat the
feature root, repository root, comparison ref, merge-base SHA, full changed-path set, material
feature constraints, and structural dossier as the review inputs.

Do not create another thread, agent, or subagent solely for the review pass. Use an in-process native
review mode when available, otherwise inspect the target directly. Do not trigger a hosted PR
review, publish comments, or contact an external service unless the user explicitly requests it.

## Review the Assembled Feature

In addition to native defect findings, verify:

- Every feature-level requirement is implemented, tested where risk warrants it, or explicitly a
  non-goal
- Task outputs integrate correctly across shared boundaries and end-to-end flows
- Later tasks did not invalidate assumptions, tests, or behavior established by earlier tasks
- UI behavior and visual results match feature-level direction when relevant
- Migrations, configuration, documentation, compatibility, and operational concerns required by
  the feature are complete
- No temporary scaffolding, disconnected paths, or partially implemented states remain
- Final project-wide validation evidence covers the assembled feature, not only isolated tasks

Run the repository's canonical full validation in this fresh feature-review context before issuing
`Feature readiness: Ready`. Record the commands and exit statuses in the report. Do not rely on a
parent or implementation agent's conversational validation summary, because that evidence is not
part of this independent context. If the repository has no full validation command, state that
explicitly and run the closest available project-wide checks. Treat a failing or materially
incomplete final validation as a readiness blocker.

Flag only discrete, actionable issues that are demonstrable from the code, feature package, call
paths, visuals, or test behavior. Reject speculative concerns, pre-existing problems, intentional
in-scope changes, and low-value style nits. Verify every candidate finding before reporting it.

## Report

Present verified findings first, ordered by severity:

`[P1] Imperative finding title — path/to/file.ext:line`

Follow with one short paragraph explaining the affected scenario, why it violates feature intent,
and what must change. Cite changed code for implementation defects. For an entirely missing
requirement, cite the feature or task artifact that defines the unmet behavior.

- `P0`: universal release blocker or critical failure
- `P1`: urgent defect that should be fixed next
- `P2`: ordinary defect that should be fixed
- `P3`: low-impact issue that is still worth fixing

If no issue qualifies, say `No findings.` Do not invent feedback. Determine one verdict:

- `Feature readiness: Ready` only when all tasks and required implementation are complete, no
  finding remains, and material final validation evidence exists
- `Feature readiness: Not ready` when any finding remains, inputs are partial, or final validation
  evidence is materially insufficient

Mention only material residual risks.

Include the final validation commands and exit statuses with the verdict.

## Return a Read-Only Handoff

Return the exact reviewed feature path, comparison target, merge-base SHA, findings, final validation
commands and exit statuses, and readiness verdict to the caller. Do not make a Ready verdict
conditional on being allowed to update status or archive; those operations are deliberately outside
this skill.

For either verdict, leave `feature.md`, `tasks.md`, `ship-log.md`, the feature directory, and archive
directories untouched. On `Feature readiness: Ready`, the calling orchestrator may record the
verdict, mark the feature complete, and invoke `$archive-work-artifact`. On `Feature readiness: Not
ready`, the calling orchestrator must leave the feature active and route the findings for repair.
