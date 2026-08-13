---
name: task-reviewer
description: Run a read-only, spec-aware review of one approved feature task or standalone spec before merge. Use after implementation or when the user asks to review a task-driven change; load the full task package, resolve the exact diff, review in the current context by default, and return verified, actionable findings.
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

Read the complete package before reviewing code:

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
base branch, commit, or custom target. Always inspect the complete diff and enough surrounding code,
tests, and call sites to understand every changed path.

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

After resolving the complete target, use Reveal as an optional structural evidence layer:

1. Locate the `reveal` executable with the platform's command lookup. The package name is
   `reveal-cli`, but the executable is `reveal`.
2. If present, record `reveal --version` and inspect `reveal --agent-help`, falling back to
   `reveal --help`. Use only commands and URI adapters advertised by that installed binary; do not
   infer capabilities from remote documentation or the version number alone.
3. Filter the changed-path set to existing code files supported by `reveal --list-supported`.
   Continue to inspect deleted, binary, and unsupported files through the diff and normal tools.
4. Run a lightweight structural pass over supported changed files, starting with
   `reveal --stdin --outline`. Drill into risky files with `reveal <file> --typed`,
   `reveal <file> <changed-symbol>`, or `reveal <file> --check --select B,S,C,E` when the local help
   confirms those options.
5. Use a concise summary of relevant symbols, containment, imports, complexity signals, and
   detector results during the review. Do not let unfiltered Reveal output crowd out the task
   package, diff, or source evidence.

Treat Reveal output as investigation leads, not findings. Verify every consequential signal against
the source, diff, call sites, tests, or runtime behavior. If Reveal is unavailable, unsupported for
the changed language, or fails, continue the full review with normal repository tools. Do not
install it, block the review, or lower the review standard.

## Run the Review Pass

Perform the defect-first review in the current context by default. This is the routine, low-overhead
quality gate used inside `$developer` and `$ship-task`; it does not require an independent context.
Do not create a new thread, agent, or subagent solely for task review.

Use an in-process native review mode when the runtime exposes one without creating another worker.
Otherwise apply the review contract below directly. Invoke a separate built-in reviewer, subagent,
hosted PR review, or external review service only when the user explicitly requests that additional
review.

Keep the pass read-only even when it runs in the implementation context. Inspect the complete target
and use the task package as an adversarial checklist rather than relying on implementation memory or
the author's summary.

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

If no issue qualifies, say `No findings.` Do not invent feedback. End with a brief overall
assessment and only material test gaps or residual risks.
