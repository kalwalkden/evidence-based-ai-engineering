#!/usr/bin/env python3
"""Validate the structural contract every skill in this kit has to satisfy.

A skill is any top-level directory holding a SKILL.md. Each one must carry
YAML frontmatter naming itself, ship an agents/openai.yaml interface block,
and be listed exactly once in installable-skills.txt, which is what
sync-installable-skills.sh reads when it links skills into Codex and Claude.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_LIST = REPO_ROOT / "installable-skills.txt"
REQUIRED_FRONTMATTER = ("name", "description")
REQUIRED_INTERFACE = ("display_name", "short_description", "default_prompt")


def parse_frontmatter(skill_md: Path) -> dict[str, object]:
    """Return the YAML frontmatter block, or raise ValueError if malformed."""
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing opening '---' frontmatter fence on line 1")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError("missing closing '---' frontmatter fence")
    data = yaml.safe_load(text[4:end])
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a YAML mapping")
    return data


def discover_skills() -> list[Path]:
    return sorted(
        child
        for child in REPO_ROOT.iterdir()
        if child.is_dir() and not child.name.startswith(".") and (child / "SKILL.md").is_file()
    )


def check_skill(skill_dir: Path, errors: list[str]) -> None:
    name = skill_dir.name

    try:
        frontmatter = parse_frontmatter(skill_dir / "SKILL.md")
    except (ValueError, yaml.YAMLError) as exc:
        errors.append(f"{name}/SKILL.md: {exc}")
        return

    for key in REQUIRED_FRONTMATTER:
        value = frontmatter.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{name}/SKILL.md: frontmatter '{key}' is missing or empty")

    declared = frontmatter.get("name")
    if isinstance(declared, str) and declared.strip() != name:
        errors.append(
            f"{name}/SKILL.md: frontmatter name '{declared.strip()}' does not match directory '{name}'"
        )

    manifest = skill_dir / "agents" / "openai.yaml"
    if not manifest.is_file():
        errors.append(f"{name}: missing agents/openai.yaml")
        return

    try:
        loaded = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        errors.append(f"{name}/agents/openai.yaml: invalid YAML ({exc})")
        return

    interface = (loaded or {}).get("interface") if isinstance(loaded, dict) else None
    if not isinstance(interface, dict):
        errors.append(f"{name}/agents/openai.yaml: missing top-level 'interface' mapping")
        return

    for key in REQUIRED_INTERFACE:
        value = interface.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{name}/agents/openai.yaml: interface '{key}' is missing or empty")


def check_skill_list(skill_names: set[str], errors: list[str]) -> None:
    if not SKILL_LIST.is_file():
        errors.append("installable-skills.txt: file is missing")
        return

    listed: list[str] = []
    for lineno, raw in enumerate(SKILL_LIST.read_text(encoding="utf-8").splitlines(), start=1):
        entry = raw.strip()
        if not entry or entry.startswith("#"):
            continue
        if entry != raw:
            errors.append(f"installable-skills.txt:{lineno}: '{raw}' has surrounding whitespace")
        listed.append(entry)

    for entry in sorted({e for e in listed if listed.count(e) > 1}):
        errors.append(f"installable-skills.txt: '{entry}' is listed more than once")

    for entry in sorted(set(listed) - skill_names):
        errors.append(f"installable-skills.txt: '{entry}' has no matching skill directory")

    for missing in sorted(skill_names - set(listed)):
        errors.append(f"installable-skills.txt: skill '{missing}' exists but is not listed")


def main() -> int:
    skills = discover_skills()
    if not skills:
        print("error: no skill directories found (expected top-level dirs with SKILL.md)")
        return 1

    errors: list[str] = []
    for skill_dir in skills:
        check_skill(skill_dir, errors)
    check_skill_list({s.name for s in skills}, errors)

    if errors:
        print(f"Found {len(errors)} problem(s) across {len(skills)} skill(s):\n")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"OK: {len(skills)} skills validated, all listed in installable-skills.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
