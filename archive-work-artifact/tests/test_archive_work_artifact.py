from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "archive_work_artifact.py"


class ArchiveWorkArtifactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def create_feature(self, path: Path) -> None:
        path.mkdir(parents=True)
        (path / "feature.md").write_text("# Feature\n", encoding="utf-8")
        (path / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
        (path / "tasks").mkdir()

    def run_archive(self, path: Path) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(path),
                "--repo-root",
                str(self.repo_root),
                "--confirm-feature-complete",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        output = result.stdout if result.returncode == 0 else result.stderr
        return result, json.loads(output)

    def test_grouped_feature_under_epics_does_not_move_active_epic_and_is_idempotent(self) -> None:
        epic_root = self.repo_root / "ai" / "features" / "epics" / "platform"
        first_feature = epic_root / "first-feature"
        second_feature = epic_root / "second-feature"
        self.create_feature(first_feature)
        self.create_feature(second_feature)
        (epic_root / "epic.md").write_text(
            "# Platform\n\nStatus: Active\n\n## Features\n\n"
            "- [ ] first-feature\n"
            "- [ ] second-feature\n",
            encoding="utf-8",
        )

        first_result, first_payload = self.run_archive(first_feature)

        self.assertEqual(0, first_result.returncode, first_result.stderr)
        self.assertEqual("updated_no_move", first_payload["status"])
        self.assertTrue(epic_root.is_dir())
        self.assertFalse(
            (self.repo_root / "ai" / "archive" / "features" / "epics" / "platform").exists()
        )
        self.assertIn("- [x] first-feature", (epic_root / "epic.md").read_text(encoding="utf-8"))

        second_result, second_payload = self.run_archive(first_feature)

        self.assertEqual(0, second_result.returncode, second_result.stderr)
        self.assertEqual("no_move", second_payload["status"])
        self.assertEqual(["second-feature"], second_payload["unchecked_features"])

    def test_grouped_feature_under_epics_archives_complete_epic(self) -> None:
        epic_root = self.repo_root / "ai" / "features" / "epics" / "platform"
        first_feature = epic_root / "first-feature"
        last_feature = epic_root / "last-feature"
        self.create_feature(first_feature)
        self.create_feature(last_feature)
        task_path = last_feature / "tasks" / "001-finish"
        task_path.mkdir()
        (task_path / "brief.md").write_text("# Finish\n", encoding="utf-8")
        (epic_root / "epic.md").write_text(
            "# Platform\n\nStatus: Active\n\n## Features\n\n"
            "- [x] first-feature\n"
            "- [ ] last-feature\n",
            encoding="utf-8",
        )

        result, payload = self.run_archive(task_path)

        target = self.repo_root / "ai" / "archive" / "features" / "epics" / "platform"
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("moved", payload["status"])
        self.assertEqual("ai/archive/features/epics/platform", payload["target"])
        self.assertFalse(epic_root.exists())
        self.assertTrue((target / "first-feature").is_dir())
        self.assertTrue((target / "last-feature").is_dir())
        epic_text = (target / "epic.md").read_text(encoding="utf-8")
        self.assertIn("Status: Complete", epic_text)
        self.assertIn("- [x] last-feature", epic_text)

    def test_legacy_shallow_epic_still_archives_to_shallow_target(self) -> None:
        epic_root = self.repo_root / "ai" / "features" / "legacy-platform"
        feature = epic_root / "only-feature"
        self.create_feature(feature)
        (epic_root / "epic.md").write_text(
            "# Legacy Platform\n\n## Features\n\n- [ ] only-feature\n",
            encoding="utf-8",
        )

        result, payload = self.run_archive(feature)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("ai/archive/features/legacy-platform", payload["target"])
        self.assertTrue(
            (self.repo_root / "ai" / "archive" / "features" / "legacy-platform").is_dir()
        )

    def test_archived_standalone_spec_reports_already_archived(self) -> None:
        spec_root = self.repo_root / "ai" / "archive" / "specs" / "completed-spec"
        spec_root.mkdir(parents=True)

        result, payload = self.run_archive(spec_root)

        self.assertEqual(2, result.returncode)
        self.assertEqual("error", payload["status"])
        self.assertIn("already under ai/archive", payload["message"])


if __name__ == "__main__":
    unittest.main()
