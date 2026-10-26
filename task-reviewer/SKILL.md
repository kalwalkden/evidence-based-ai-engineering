---
name: task-reviewer
description: Run a brief, read-only local check of one task against its approved scope and exact diff. Use after implementation or for a requested task review; check correctness and directly affected boundaries, and report blocking findings separately from advisory documentation-only P3 issues.
---

# Task Reviewer

Review exactly one spec-driven implementation before merge. Treat the task package as the source
of intended behavior and the actual diff as the source of implemented behavior. Coordinate the
review; do not modify files, create commits, push branches, or post review comments.

## Resolve the Task

Accept one of these entry points:

- `ai/features/<feature-slug>/tasks/<NNN>-<task-title>/brief.md`
- `ai/features/<feature-slug>/tasks/<NNN>-<task-title>/`
- `ai/specs/<task-slug>/`
- The equivalent archived path under `ai/archive/`

Classify an entry as a feature task only when it is under a feature root containing `feature.md`,
`tasks.md`, and `tasks/`. Otherwise require a standalone spec root. Do not infer feature status from
unrelated ancestor files.

Read the brief and plan once as the task contract. Consult other artifacts only as needed to
resolve affected decisions or evidence:

- Applicable `AGENTS.md` and `CLAUDE.md` instructions
- `brief.md` when present
- Feature-level `feature.md` and `visuals/` when present
- `plan.md` or `spec/plan.md`
- `references.md` or `spec/references.md`
- Task-level `visuals/` or `spec/visuals/` when present

Use `brief.md` as the scope guard. If a required plan or references file is missing,
stop and ask whether to use `$shape-spec` unless the user explicitly authorizes a partial-input
review. Note missing optional artifacts without stopping.

## Resolve the Change

Identify the repository root and the exact review target. Honor a user-specified uncommitted diff,
base branch, commit, or custom target. Inspect the complete task diff and only the surrounding
code, tests, and call sites needed to check its directly affected behavior and boundaries.

For an uncommitted review, inspect repository status, the staged diff, the unstaged diff, and the
complete contents of every untracked file. Enumerate that full path set in the review inputs; plain
`git diff` does not include staged or untracked changes.

For a tree-to-tree review, the caller supplies two git tree SHAs bracketing one task's work — the
form `$developer` and `$ship-feature` produce when earlier uncommitted changes must stay out of the
verdict. The caller also supplies the temporary `GIT_DIR`, real repository Git directory, cleanup
root, and cleanup marker needed to resolve those trees without writing into the real Git metadata.
Run `git diff-tree -r -p <before-sha> <after-sha>` with that temporary `GIT_DIR`, the real
repository's `objects` path as `GIT_ALTERNATE_OBJECT_DIRECTORIES`, and system/global Git config
disabled through the supplied empty config exactly as in `$developer`. Keep the verified cleanup
root until review finishes.
That target already includes tracked and untracked additions, modifications, and deletions, so do
not widen it with `git status` or a working-tree scan; changes outside it belong to another task or
to the user. Read surrounding code, call sites, and tests freely — the boundary limits what you
judge, not what you read. If either SHA, Git-directory path, cleanup root, or marker is missing or
unresolvable, stop and ask rather than substituting an uncommitted review or guessing a cleanup
target.

For a base-branch review, inspect what would actually merge:

1. Prefer the branch's upstream when it exists and is ahead of the local branch; otherwise use the
   local branch.
2. Resolve `git merge-base HEAD <comparison-ref>`.
3. Review `git diff <merge-base-sha>`.

Do not rely on a diff summary or compare directly with a moving branch tip.

## Enrich with Reveal When Available

Use Reveal optionally when a concrete review concern would benefit from structural evidence, such
as an unclear dependency, changed symbol, or affected call boundary. Availability alone is not a
reason to run it; skip routine discovery and blanket analysis on every task.

- When useful, locate the `reveal` executable and inspect its installed version and help as needed.
  Use only commands and options advertised by that binary.
- Target the relevant supported files or symbols and stop when the concern is resolved. Keep the
  exact task diff as the review boundary.
- Treat output as investigation leads; verify findings against source, call sites, tests, or
  behavior. If Reveal is absent, unsupported, or fails, continue with normal repository tools.
  Do not install it or block task review because it is unavailable.

## Run the Review Pass

Perform the defect-first review in the current context by default. This is the routine, low-overhead
quality gate used inside `$developer` and `$ship-task`; it does not require an independent context.
Do not create a new thread, agent, or subagent solely for task review.

Use an in-process native review mode when the runtime exposes one without creating another worker.
Otherwise apply the review contract below directly. Invoke a separate built-in reviewer, subagent,
hosted PR review, or external review service only when the user explicitly requests that additional
review.

Keep the pass brief and read-only. Compare the exact diff with approved scope, acceptance criteria,
and directly affected contracts; check for concrete local correctness defects and scope drift.
Reuse still-valid validation evidence. Run another check only when a specific gap or suspected
failure warrants it. Use targeted Reveal checks only as described above; skip routine tool discovery
and blanket structural analysis. Do not run a repository survey or cumulative feature review.
Reserve cross-task integration and assembled-feature
readiness for `$feature-reviewer`; still flag a concrete boundary defect visible in this task.
Do not rely solely on implementation memory or the author's summary.

## Review Contract

Inspect the entire target and continue after finding the first issue. Flag a finding only when it
is:

- Meaningful to correctness, security, performance, maintainability, task scope, or acceptance
  criteria
- Discrete and actionable
- Introduced by the reviewed change
- Demonstrable from the code, affected call path, spec, or test behavior
- Something the author would probably fix before merge

Reject speculative concerns, pre-existing problems, intentional in-scope behavior changes, and
style nits. Check for scope drift, unnecessary complexity, violated task constraints or approved decisions, boundary
regressions, and missing tests only where they materially reduce confidence.

Verify every finding against the diff and task package before reporting it.

## Report

Present verified findings first, ordered by severity. Use one entry per issue:

`[P1] Imperative finding title — path/to/file.ext:line`

Follow with one short paragraph stating the affected scenario, why it is wrong, and the relevant
task constraint when applicable. Cite a tight repository-relative location that overlaps the diff.

- `P0`: universal release blocker or critical failure
- `P1`: urgent defect that should be fixed next
- `P2`: ordinary defect that should be fixed
- `P3`: low-impact issue that is still worth fixing

Treat documentation-only P3 findings as advisory: report them separately and do not require a
repair to pass. This means an explanatory/editorial issue with no effect on behavior, contracts,
or safe operation. A defect in operative skill instructions is not documentation-only merely
because its file is Markdown. All other qualifying findings remain blocking.

If no issue qualifies, say `No findings.` Do not invent feedback. End with exactly one task verdict:

- `Task review: Pass` when no unresolved blocking finding remains, including when advisory
  documentation-only P3 findings remain.
- `Task review: Needs fixes` when any blocking finding remains or required inputs are incomplete.

Report unresolved blocking and advisory counts separately. Mention only material validation gaps
or residual risks. This verdict is local task checking, not independent feature readiness.
