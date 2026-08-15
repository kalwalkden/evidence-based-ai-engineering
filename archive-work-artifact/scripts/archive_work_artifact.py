#!/usr/bin/env python3
"""Archive completed Codex planning artifacts without clobbering targets."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

FEATURE_ENTRY_RE = re.compile(r"^(\s*-\s+\[)([ xX])(\]\s+`?)([A-Za-z0-9][A-Za-z0-9._-]*)(`?.*)$")


class ArchiveError(Exception):
    pass


@dataclass
class ChecklistEntry:
    slug: str
    checked: bool
    line_index: int


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)


def find_repo_root(start: Path) -> Path:
    probe = start if start.is_dir() else start.parent
    result = run(["git", "rev-parse", "--show-toplevel"], probe)
    if result.returncode == 0:
        return Path(result.stdout.strip()).resolve()
    return Path.cwd().resolve()


def inside(path: Path, ancestor: Path) -> bool:
    try:
        path.relative_to(ancestor)
        return True
    except ValueError:
        return False


def rel_to_repo(path: Path, repo_root: Path) -> Path:
    try:
        return path.relative_to(repo_root)
    except ValueError as exc:
        raise ArchiveError(f"Path is outside repo root: {path}") from exc


def feature_layout(path: Path, repo_root: Path) -> tuple[str, str] | None:
    """Return (state, layout) for supported feature-root locations."""
    parts = rel_to_repo(path, repo_root).parts
    if parts[:2] == ("ai", "features"):
        state = "active"
        tail = parts[2:]
    elif parts[:3] == ("ai", "archive", "features"):
        state = "archived"
        tail = parts[3:]
    else:
        return None

    if len(tail) == 1 and tail[0] != "epics":
        return state, "ungrouped"
    if len(tail) == 3 and tail[0] == "epics":
        return state, "grouped"
    if len(tail) == 2 and tail[0] != "epics":
        return state, "legacy_grouped"
    return None


def valid_feature_root(path: Path, repo_root: Path) -> bool:
    if not path.is_dir():
        return False
    if not (path / "feature.md").is_file():
        return False
    if not (path / "tasks.md").is_file():
        return False
    if not (path / "tasks").is_dir():
        return False

    return feature_layout(path, repo_root) is not None


def find_feature_root(path: Path, repo_root: Path) -> Path | None:
    current = path if path.is_dir() else path.parent
    while inside(current, repo_root):
        if valid_feature_root(current, repo_root):
            return current
        if current == repo_root:
            break
        current = current.parent
    return None


def find_standalone_spec_root(path: Path, repo_root: Path) -> Path | None:
    current = path if path.is_dir() else path.parent
    specs_roots = {
        repo_root / "ai" / "specs",
        repo_root / "ai" / "archive" / "specs",
    }
    while inside(current, repo_root):
        if current.parent in specs_roots and current.is_dir():
            return current
        if current == repo_root:
            break
        current = current.parent
    return None


def ensure_active(path: Path, repo_root: Path) -> None:
    rel = rel_to_repo(path, repo_root)
    if rel.parts[:3] == ("ai", "archive", "features") or rel.parts[:3] == (
        "ai",
        "archive",
        "specs",
    ):
        raise ArchiveError(f"Artifact is already under ai/archive: {rel}")


def parse_feature_checklist(epic_md: Path) -> tuple[list[str], list[ChecklistEntry]]:
    lines = epic_md.read_text(encoding="utf-8").splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if line.strip().lower() == "## features"]
    if len(starts) != 1:
        raise ArchiveError("Epic must contain exactly one '## Features' checklist section.")

    start = starts[0] + 1
    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break

    entries: list[ChecklistEntry] = []
    seen: set[str] = set()
    for index in range(start, end):
        match = FEATURE_ENTRY_RE.match(lines[index].rstrip("\n"))
        if not match:
            continue
        slug = match.group(4)
        if slug in seen:
            raise ArchiveError(f"Epic checklist contains duplicate feature entry: {slug}")
        seen.add(slug)
        entries.append(
            ChecklistEntry(slug=slug, checked=match.group(2).lower() == "x", line_index=index)
        )

    if not entries:
        raise ArchiveError("Epic '## Features' section has no checkbox feature entries.")
    return lines, entries


def write_checked_entry(epic_md: Path, slug: str, dry_run: bool) -> bool:
    lines, entries = parse_feature_checklist(epic_md)
    by_slug = {entry.slug: entry for entry in entries}
    if slug not in by_slug:
        raise ArchiveError(f"Epic checklist does not contain completed feature slug: {slug}")

    entry = by_slug[slug]
    if entry.checked:
        return False

    lines[entry.line_index] = FEATURE_ENTRY_RE.sub(r"\1x\3\4\5", lines[entry.line_index])
    if not dry_run:
        epic_md.write_text("".join(lines), encoding="utf-8")
    return True


def epic_ready_to_archive(
    epic_root: Path, repo_root: Path, assume_checked: str | None = None
) -> tuple[bool, list[str], list[str]]:
    _, entries = parse_feature_checklist(epic_root / "epic.md")
    if assume_checked:
        for entry in entries:
            if entry.slug == assume_checked:
                entry.checked = True
    entry_slugs = sorted(entry.slug for entry in entries)
    unchecked = sorted(entry.slug for entry in entries if not entry.checked)
    feature_dirs = sorted(
        child.name for child in epic_root.iterdir() if valid_feature_root(child, repo_root)
    )

    if entry_slugs != feature_dirs:
        missing_dirs = sorted(set(entry_slugs) - set(feature_dirs))
        missing_entries = sorted(set(feature_dirs) - set(entry_slugs))
        details = []
        if missing_dirs:
            details.append(f"checklist entries without feature dirs: {', '.join(missing_dirs)}")
        if missing_entries:
            details.append(f"feature dirs without checklist entries: {', '.join(missing_entries)}")
        raise ArchiveError(
            "Epic checklist does not match feature directories (" + "; ".join(details) + ")."
        )

    return not unchecked, unchecked, feature_dirs


def mark_epic_complete(epic_md: Path, dry_run: bool) -> None:
    lines = epic_md.read_text(encoding="utf-8").splitlines(keepends=True)
    for index, line in enumerate(lines):
        if line.lower().startswith("status:"):
            lines[index] = "Status: Complete\n"
            if not dry_run:
                epic_md.write_text("".join(lines), encoding="utf-8")
            return

    insert_at = 0
    if lines and lines[0].startswith("#"):
        insert_at = 1
        if insert_at < len(lines) and lines[insert_at].strip() == "":
            insert_at += 1
    lines.insert(insert_at, "Status: Complete\n")
    if insert_at < len(lines) - 1 and lines[insert_at + 1].strip() != "":
        lines.insert(insert_at + 1, "\n")
    if not dry_run:
        epic_md.write_text("".join(lines), encoding="utf-8")


def move_artifact(source: Path, target: Path, repo_root: Path, dry_run: bool) -> str:
    if target.exists():
        raise ArchiveError(f"Archive target already exists: {rel_to_repo(target, repo_root)}")
    if dry_run:
        return "dry_run"

    target.parent.mkdir(parents=True, exist_ok=True)
    git_check = run(["git", "rev-parse", "--is-inside-work-tree"], repo_root)
    if git_check.returncode == 0:
        result = run(["git", "mv", str(source), str(target)], repo_root)
        if result.returncode != 0:
            raise ArchiveError(result.stderr.strip() or result.stdout.strip() or "git mv failed")
        return "git mv"

    shutil.move(str(source), str(target))
    return "mv"


def archive_standalone(spec_root: Path, repo_root: Path, dry_run: bool) -> dict[str, object]:
    ensure_active(spec_root, repo_root)
    target = repo_root / "ai" / "archive" / "specs" / spec_root.name
    method = move_artifact(spec_root, target, repo_root, dry_run)
    return {
        "status": "moved" if not dry_run else "would_move",
        "kind": "standalone_spec",
        "source": str(rel_to_repo(spec_root, repo_root)),
        "target": str(rel_to_repo(target, repo_root)),
        "method": method,
    }


def archive_feature(
    feature_root: Path, repo_root: Path, confirm: bool, dry_run: bool
) -> dict[str, object]:
    ensure_active(feature_root, repo_root)
    if not confirm:
        raise ArchiveError("Feature artifacts require --confirm-feature-complete.")

    features_root = repo_root / "ai" / "features"
    archive_features_root = repo_root / "ai" / "archive" / "features"
    location = feature_layout(feature_root, repo_root)
    if location == ("active", "ungrouped"):
        target = archive_features_root / feature_root.name
        method = move_artifact(feature_root, target, repo_root, dry_run)
        return {
            "status": "moved" if not dry_run else "would_move",
            "kind": "ungrouped_feature",
            "source": str(rel_to_repo(feature_root, repo_root)),
            "target": str(rel_to_repo(target, repo_root)),
            "method": method,
        }

    if location == ("active", "grouped"):
        expected_epics_root = features_root / "epics"
        archive_epics_root = archive_features_root / "epics"
    elif location == ("active", "legacy_grouped"):
        expected_epics_root = features_root
        archive_epics_root = archive_features_root
    else:
        raise ArchiveError(
            f"Unsupported active feature layout: {rel_to_repo(feature_root, repo_root)}"
        )

    epic_root = feature_root.parent
    if epic_root.parent != expected_epics_root or not (epic_root / "epic.md").is_file():
        raise ArchiveError(
            "Feature root is not directly under ai/features/, "
            "ai/features/epics/<epic>/, or a valid legacy epic: "
            f"{rel_to_repo(feature_root, repo_root)}"
        )

    checklist_changed = write_checked_entry(epic_root / "epic.md", feature_root.name, dry_run)
    ready, unchecked, feature_dirs = epic_ready_to_archive(
        epic_root, repo_root, assume_checked=feature_root.name if dry_run else None
    )
    if not ready:
        return {
            "status": "updated_no_move" if checklist_changed else "no_move",
            "kind": "grouped_feature",
            "feature": str(rel_to_repo(feature_root, repo_root)),
            "epic": str(rel_to_repo(epic_root, repo_root)),
            "unchecked_features": unchecked,
            "feature_dirs": feature_dirs,
        }

    mark_epic_complete(epic_root / "epic.md", dry_run)
    target = archive_epics_root / epic_root.name
    method = move_artifact(epic_root, target, repo_root, dry_run)
    return {
        "status": "moved" if not dry_run else "would_move",
        "kind": "epic",
        "source": str(rel_to_repo(epic_root, repo_root)),
        "target": str(rel_to_repo(target, repo_root)),
        "method": method,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_path", help="Completed feature task/root or standalone spec path")
    parser.add_argument(
        "--repo-root", help="Repository root. Defaults to git root or current directory."
    )
    parser.add_argument(
        "--confirm-feature-complete",
        action="store_true",
        help="Required before archiving a feature artifact.",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Report the intended action without moving files."
    )
    args = parser.parse_args()

    input_path = Path(args.artifact_path).expanduser()
    if not input_path.is_absolute():
        input_path = Path.cwd() / input_path
    input_path = input_path.resolve()

    repo_root = (
        Path(args.repo_root).expanduser().resolve()
        if args.repo_root
        else find_repo_root(input_path)
    )
    try:
        if not input_path.exists():
            raise ArchiveError(f"Path does not exist: {input_path}")

        feature_root = find_feature_root(input_path, repo_root)
        if feature_root:
            result = archive_feature(
                feature_root, repo_root, args.confirm_feature_complete, args.dry_run
            )
        else:
            spec_root = find_standalone_spec_root(input_path, repo_root)
            if not spec_root:
                raise ArchiveError(
                    "Path is neither a valid feature artifact nor a standalone spec under ai/specs/."
                )
            result = archive_standalone(spec_root, repo_root, args.dry_run)

        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except ArchiveError as exc:
        print(
            json.dumps({"status": "error", "message": str(exc)}, indent=2, sort_keys=True),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
