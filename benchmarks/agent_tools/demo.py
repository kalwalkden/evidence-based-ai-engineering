"""Create an offline fixture; this command never invokes Claude."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent


def make_demo(output: Path):
    output.mkdir(parents=True, exist_ok=False)
    repo = output / "repository"
    repo.mkdir()
    (repo / ".gitignore").write_text("__pycache__/\n")
    (repo / "checkout.py").write_text(
        '"""Calculate a basket total in integer cents."""\n\n'
        "def total(prices):\n"
        "    return sum(prices)\n"
    )
    (repo / "test_checkout.py").write_text(
        "import unittest\nfrom checkout import total\n\n"
        "class CheckoutTests(unittest.TestCase):\n"
        "    def test_total(self):\n"
        "        self.assertEqual(total([100, 250]), 350)\n"
        "    def test_empty(self):\n"
        "        self.assertEqual(total([]), 0)\n"
    )
    (repo / "README.md").write_text(
        "# Basket totals\n\nThe checkout module computes integer-cent totals.\n\n"
        "Run tests with `python3 -m unittest discover`.\n"
    )
    spec = repo / "ai" / "specs" / "basket-discount"
    spec.mkdir(parents=True)
    (spec / "plan.md").write_text(
        "# Basket discount\n\nStatus: approved for implementation.\n\n"
        "Extend checkout.total(prices, discount_percent=0) with an optional integer discount "
        "from 0 to 100 inclusive. Apply it to the basket sum and round down to integer cents. "
        "Preserve calls without a discount. Reject non-integers, including bool, with TypeError; "
        "reject values outside the range with ValueError. Do not mutate prices. Prices are "
        "nonnegative integer cents.\n\nImplement only this change and focused tests. Run the full "
        "unittest suite, complete the developer skill's review loop, and archive this standalone "
        "spec through archive-work-artifact after completion. No visual design applies.\n"
    )
    (spec / "references.md").write_text(
        "# Repository evidence\n\n"
        "- checkout.py: total currently sums integer-cent prices.\n"
        "- test_checkout.py: standard-library unittest coverage for sums and empty baskets.\n"
        "- README.md: canonical command is python3 -m unittest discover.\n"
        "- No runtime dependencies or external API calls are needed.\n"
    )
    subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
    for key, value in (
        ("user.name", "Experiment Fixture"),
        ("user.email", "fixture@localhost"),
        ("core.hooksPath", "/dev/null"),
    ):
        subprocess.run(["git", "-C", str(repo), "config", key, value], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "--quiet", "-m", "Initial fixture"], check=True
    )
    tasks = output / "tasks"
    tasks.mkdir()
    (tasks / "build.md").write_text(
        "Implement the approved standalone spec at ai/specs/basket-discount/ using developer, "
        "including its validation, task-reviewer review, and archival workflow.\n"
    )
    (tasks / "flow.md").write_text(
        "Trace a call to checkout.total from its public arguments to its returned value. "
        "Explain validation, arithmetic, rounding, and errors actually present in this revision. "
        "Do not assume discount support exists.\n"
    )
    (tasks / "architecture.md").write_text(
        "Discover this repository's architecture, public interface, tests, dependencies, and "
        "validation commands. Distinguish observed structure from unsupported speculation.\n"
    )
    config = json.loads((HERE / "example.json").read_text())
    repo_config = config["repositories"][0]
    repo_config.update(
        id="basket",
        path=str(repo),
        context="Python standard library only. Run local tests with python3 -m unittest discover.",
    )
    (output / "experiment.json").write_text(json.dumps(config, indent=2) + "\n")
    print(output / "experiment.json")
