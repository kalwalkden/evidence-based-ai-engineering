# Filesystem Archival

## Scope and Decisions

Implement approved task 003 after tasks 001 and 002. The user explicitly requested filesystem moves
and will handle Git behavior. This toolkit is pre-production and permits breaking workflow changes.
No visual work is needed.

## Approach

- Remove Git worktree detection and git mv from move_artifact; always use the existing shutil.move
  path after collision/dry-run checks. Keep method reporting as mv and retain repository discovery.
- Update archive-work-artifact/SKILL.md to promise filesystem moves with no staging/index mutation.
- Add one subprocess regression test covering fully untracked and mixed tracked/untracked artifacts
  inside a real Git repository. Verify all content moves and the pre-existing index remains byte
  identical, including unrelated staged content. This protects the meaningful Git ownership boundary
  and reproduces the old failure; do not add tests for implementation calls.
- Exercise existing archive lifecycle tests. Check dry-run and collision behavior with temporary
  artifacts instead of expanding tests for unchanged behavior.

## Contracts and Unchanged Boundaries

Archive target and JSON report shapes, dry-run behavior, no-overwrite checks, feature completion,
epic checklists, and legacy layout support stay unchanged. Git remains a read-only root-discovery
mechanism. The real repository index must remain untouched by archival.

## Validation

Run the new test against the previous implementation to establish it detects the defect, then run
`python -m unittest discover -s archive-work-artifact/tests -v` after the fix. Run canonical
`scripts/check.sh lint prose validate test` for the assembled feature (AGENTS.md/scripts/check.sh).
Use the existing supported Python matrix; obtain missing pinned tools in temporary caches when
needed. The independent feature reviewer must run canonical full validation in its own context.

## Open Questions

None.
