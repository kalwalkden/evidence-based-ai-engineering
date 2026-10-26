# Filesystem archival

## Context

The archive utility selects git mv inside worktrees, which stages moves and fails on untracked artifacts.

## Objective

Move artifacts through the filesystem regardless of Git tracking state, leaving Git handling to the user.

## Scope

Remove Git-based move selection, update the archive skill behavior description, and validate the Git index remains unchanged for tracked and untracked source content. Preserve existing lifecycle protections.

## Non-goals / Later

Do not remove Git-based repository-root discovery or redesign archive layouts, checklist rules, collision handling, or dry runs.

## Constraints / Caveats

Use the approved decisions and testing policy in `../../feature.md`. This toolkit is under
development; breaking workflow changes are acceptable. No visual design is needed. Keep this task
green without relying on a later task to repair a contradictory handoff.

## Dependent Tasks or Work

002-brief-task-review.

## Likely Starting Points

Recheck these landmarks against the current tree during shaping:

- `archive-work-artifact/scripts/archive_work_artifact.py` — move_artifact and find_repo_root.
- `archive-work-artifact/tests/test_archive_work_artifact.py` — existing subprocess-based lifecycle tests.
- `archive-work-artifact/SKILL.md` — archival behavior contract.

## Expected Change Surface

Archive move implementation, behavior documentation, and focused lifecycle/boundary tests. Preserve source/target layout and JSON report structure.

## Open Questions

None.
