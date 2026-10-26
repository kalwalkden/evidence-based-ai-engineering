from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "sync-installable-skills.sh"


class SyncInstallableSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name).resolve()
        self.checkout = self.root / "toolkit checkout"
        self.checkout.mkdir()
        self.script = self.checkout / SCRIPT.name
        shutil.copy2(SCRIPT, self.script)
        self.home = self.root / "test home"
        self.state = self.root / "test state"
        self.destinations = [
            self.home / runtime / "skills" for runtime in (".codex", ".claude", ".cursor")
        ]
        self.env = {**os.environ, "HOME": str(self.home), "XDG_STATE_HOME": str(self.state)}
        self.names = ("alpha", "beta")
        (self.checkout / "installable-skills.txt").write_text("alpha\nbeta\n")
        for name in self.names:
            source = self.checkout / name
            source.mkdir()
            (source / "SKILL.md").write_text(f"# {name}\n")

    def sync(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["bash", str(self.script), *args],
            env=self.env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        return result

    def manifest(self) -> Path:
        paths = list(self.state.rglob("*.manifest"))
        self.assertEqual(1, len(paths))
        return paths[0]

    def entries(self) -> set[str]:
        return {
            line
            for line in self.manifest().read_text().splitlines()
            if line and not line.startswith("#")
        }

    def snapshot(self) -> dict[str, tuple[str, bytes | str]]:
        result = {}
        for path in self.root.rglob("*"):
            key = str(path.relative_to(self.root))
            if path.is_symlink():
                result[key] = ("link", os.readlink(path))
            elif path.is_dir():
                result[key] = ("directory", "")
            else:
                result[key] = ("file", path.read_bytes())
        return result

    def test_install_and_repeat_record_all_destinations(self) -> None:
        self.sync()
        for destination in self.destinations:
            for name in self.names:
                link = destination / name
                self.assertTrue(link.is_symlink())
                self.assertEqual(str(self.checkout / name), os.readlink(link))
                self.assertEqual(f"# {name}\n", (link / "SKILL.md").read_text())
        self.assertEqual(
            {f"{destination}\t{name}" for destination in self.destinations for name in self.names},
            self.entries(),
        )
        before = self.snapshot()
        self.sync()
        self.assertEqual(before, self.snapshot())

    def test_upgrade_preserves_existing_links_and_manifest_path(self) -> None:
        self.sync()
        manifest = self.manifest()
        old_entries = {entry for entry in self.entries() if ".cursor/" not in entry}
        manifest.write_text("\n".join(sorted(old_entries)) + "\n")
        shutil.rmtree(self.home / ".cursor")
        old_links = {
            path: path.lstat().st_ino for dest in self.destinations[:2] for path in dest.iterdir()
        }
        self.sync()
        self.assertEqual(manifest, self.manifest())
        self.assertTrue(old_entries < self.entries())
        for path, inode in old_links.items():
            self.assertEqual(inode, path.lstat().st_ino)
        for name in self.names:
            self.assertEqual(str(self.checkout / name), os.readlink(self.destinations[2] / name))

    def test_dry_run_changes_neither_absent_nor_existing_trees(self) -> None:
        before = self.snapshot()
        result = self.sync("--dry-run")
        self.assertIn(".cursor/skills", result.stdout)
        self.assertEqual(before, self.snapshot())
        self.sync()
        cursor = self.destinations[2]
        (cursor / "alpha").unlink()
        (cursor / "alpha").symlink_to(self.checkout / "wrong")
        (cursor / "retired").symlink_to(self.checkout / "deleted")
        before = self.snapshot()
        self.sync("--dry-run")
        self.assertEqual(before, self.snapshot())

    def test_foreign_links_are_preserved_and_not_recorded(self) -> None:
        cursor = self.destinations[2]
        cursor.mkdir(parents=True)
        foreign = self.root / "other project"
        (cursor / "alpha").symlink_to(foreign)
        (cursor / "retired").symlink_to(foreign)
        result = self.sync()
        self.assertIn("owned by another project", result.stderr)
        self.assertEqual(str(foreign), os.readlink(cursor / "alpha"))
        self.assertEqual(str(foreign), os.readlink(cursor / "retired"))
        self.assertNotIn(f"{cursor}\talpha", self.entries())
        self.assertEqual(5, len(self.entries()))

    def test_cursor_file_and_directory_collisions_prevent_link_edits(self) -> None:
        cursor = self.destinations[2]
        cursor.mkdir(parents=True)
        collision = cursor / "alpha"
        for kind in ("file", "directory"):
            with self.subTest(kind=kind):
                if kind == "file":
                    collision.write_text("keep")
                    content = collision
                else:
                    collision.mkdir()
                    content = collision / "keep.txt"
                    content.write_text("keep")
                self.sync(expected=1)
                self.assertEqual("keep", content.read_text())
                self.assertFalse(self.state.exists())
                for destination in self.destinations[:2]:
                    self.assertEqual([], list(destination.iterdir()))
                self.assertFalse((cursor / "beta").exists())
                content.unlink()
                if kind == "directory":
                    collision.rmdir()

    def test_repairs_owned_links_and_prunes_recorded_and_unrecorded_links(self) -> None:
        self.sync()
        (self.checkout / "installable-skills.txt").write_text("alpha\n")
        shutil.rmtree(self.checkout / "beta")
        for destination in self.destinations:
            (destination / "alpha").unlink()
            (destination / "alpha").symlink_to(self.checkout / "wrong")
            (destination / "unrecorded").symlink_to(self.checkout / "missing")
        self.sync()
        for destination in self.destinations:
            self.assertEqual(str(self.checkout / "alpha"), os.readlink(destination / "alpha"))
            self.assertFalse((destination / "beta").is_symlink())
            self.assertFalse((destination / "unrecorded").is_symlink())
        self.assertEqual(
            {f"{destination}\talpha" for destination in self.destinations}, self.entries()
        )
