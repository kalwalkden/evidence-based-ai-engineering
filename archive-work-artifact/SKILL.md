---
name: archive-work-artifact
description: Archive completed agent planning artifacts under `ai/archive/`. Use when a feature task or standalone spec has already been implemented, validated, reviewed, and marked complete, and the agent needs to move the completed feature, completed epic, or standalone spec without overwriting existing artifacts.
---

# Archive Work Artifact

Use this skill after completion/status updates are done. Do not use it to decide whether implementation is complete.

## Inputs

Accept one path:

- A completed standalone spec under `ai/specs/<task-slug>/`
- A completed feature task path under a valid feature root's `tasks/`
- A completed feature root under `ai/features/<feature-slug>/` or `ai/features/epics/<epic-slug>/<feature-slug>/`
- A completed feature root in the supported legacy layout `ai/features/<epic-slug>/<feature-slug>/`

A valid feature root contains `feature.md`, `tasks.md`, and `tasks/`.

## Workflow

1. Confirm implementation, validation, review, and status updates already happened.
2. Run the bundled `scripts/archive_work_artifact.py` from this skill folder.
3. For feature artifacts, pass `--confirm-feature-complete` only when the feature itself is complete.
4. If the script reports a conflict, malformed artifact, incomplete epic checklist, or existing target, stop and surface the message. Do not hand-move the files.
5. Report the archived path when the script moves something. If a grouped feature is complete but its epic is not, report that the epic checklist was updated and no directory moved.

## Script

```bash
python3 scripts/archive_work_artifact.py <artifact-path> --confirm-feature-complete
```

For standalone specs, omit `--confirm-feature-complete`:

```bash
python3 scripts/archive_work_artifact.py ai/specs/<task-slug>
```

If your shell is not currently in this skill folder, use the path to `scripts/archive_work_artifact.py` next to the `SKILL.md` file you loaded.

Use `--dry-run` when checking what would happen before allowing a move.

## Behavior

- Creates only archive container directories such as `ai/archive/features/` or `ai/archive/specs/`.
- Never pre-creates the final target directory.
- Never overwrites an existing final target.
- Uses `git mv` inside a git worktree, otherwise plain filesystem move.
- Treats `ai/features/epics/<epic-slug>/` as the canonical epic location while accepting the legacy shallow epic location under `ai/features/`.
- For grouped features, checks the epic's `## Features` checklist against immediate feature-root subdirectories before archiving the whole epic.
- Archives canonical epics under `ai/archive/features/epics/<epic-slug>/`; legacy shallow epics retain their shallow archive layout.
