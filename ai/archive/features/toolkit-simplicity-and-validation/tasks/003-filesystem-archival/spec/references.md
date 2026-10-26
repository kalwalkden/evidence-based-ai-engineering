# Implementation References

## Primary Edit Targets

- archive-work-artifact/scripts/archive_work_artifact.py — move_artifact selects git mv today;
  archive_standalone and archive_feature consume its method result. find_repo_root independently
  uses Git and remains unchanged.
- archive-work-artifact/tests/test_archive_work_artifact.py — ArchiveWorkArtifactTests creates
  temporary roots and invokes the CLI with --repo-root via run_archive. Reuse these fixtures.
- archive-work-artifact/SKILL.md — Behavior describes move selection.

## Contracts and Flow

CLI resolves input -> archive_standalone/archive_feature -> move_artifact. A filesystem move must
preserve content without changing the Git index. The existing shutil.move path returns mv; dry-run
returns dry_run. Existing JSON keys and completion/collision safeguards remain unchanged.

## Tests and Validation Commands

`python -m unittest discover -s archive-work-artifact/tests -v` gives focused behavioral confidence.
`scripts/check.sh lint prose validate test` is canonical assembled validation from AGENTS.md and
scripts/check.sh. New Git-boundary test is justified by prior untracked failures and unwanted
staging, not coverage percentage. No external guidance is selected.

## Uncertainties to Verify

Confirm the Git index stays unchanged for tracked and untracked artifacts, and the new boundary
test fails against the original implementation. Preserve dry-run and existing-target behavior.
