# Cursor installation implementation map

## Primary edit targets

| Path | Symbol or section | Intended change |
| --- | --- | --- |
| `sync-installable-skills.sh` | `destinations`, `usage`, header | Add Cursor to the existing shared lifecycle and describe all destinations |
| `README.md` | Runtime badge, See it in 60 seconds, Installation details, Installer safety | Describe installation and discovery for three runtimes |
| `scripts/validate_skills.py` | Module docstring | Correct the runtime list; validation contract remains unchanged |
| `ARCHITECTURE.md` | Detected stack, conventions, installation boundary | Update only facts affected by implementation and tests |

Proposed new file: `scripts/tests/test_sync_installable_skills.py`. Neither this test file nor
`scripts/tests/` exists yet. There is no existing installer behavior test to extend.

## Entry point and call path

`./sync-installable-skills.sh [--dry-run]` → parse arguments → resolve `script_dir` and state paths →
validate `installable-skills.txt` into `skills`/`sources` → create/preflight each destination →
`load_manifest` → `sync_skill` for each skill/destination → `prune_retired_symlinks` per destination →
`write_manifest` → completion output.

`run` suppresses mutations in dry-run mode; `write_manifest` has its own dry-run guard.
`sync_skill` returns 3 for a foreign link, which the loop counts and excludes from installed entries.
Other failures stop execution. Preflight may create destination directories but precedes link edits.

## Contracts, state, and invariants

- `installable-skills.txt`: ten unique names, each matching a top-level skill directory.
- `scripts/validate_skills.py`: `discover_skills`, `check_skill`, and `check_skill_list` enforce
  frontmatter, `agents/openai.yaml`, and list coverage. Cursor does not justify relaxing these rules.
- `path_digest`, `state_dir`, `manifest_file`: one manifest keyed by physical checkout path under
  `${XDG_STATE_HOME:-$HOME/.local/state}/sync-installable-skills`.
- `manifest_entries` / `installed_entries`: destination root plus skill name, separated by a tab.
- `links_into_repo`: literal absolute target prefix test, not filesystem resolution. This permits
  recognition of dangling retired links and does not claim ownership of foreign relative links.
- `ensure_no_managed_name_collisions`: reject non-symlinks at desired names before synchronization.
- `prune_retired_symlinks`: preserve desired names and foreign links; prune owned obsolete links
  even without a previous manifest entry.

## Patterns to reuse

Use the existing destination array and shared helpers, not a separate Cursor installer.
`archive-work-artifact/tests/test_archive_work_artifact.py` demonstrates temporary filesystem
fixtures and subprocess assertions. Adapt the testing style, not its archive-specific inputs.
`pyproject.toml` discovers `test_*.py` throughout the repository with pytest.

`ship-feature/SKILL.md` requires fresh workers and explicit model selection; its
`references/model-routing.md` supports unlisted runtimes through advertised capabilities. Those
existing rules are the reason installation must not promise unconditional orchestration parity.

## Tests and fixtures

Build temporary checkouts containing the copied installer, a small skill list, and real skill
directories with `SKILL.md`. Supply child-process-only home and state paths. Assert actual link
targets, manifest content, exit status, retained collision contents, and unchanged dry-run trees.
Include spaces in temporary checkout paths to protect quoting at the new destination boundary.

The current CI dry run does not prove link creation, ownership safety, or Cursor discovery.
The archived feature/spec packages contain no installer task contract to inherit; the current
installer and user decisions are the governing inputs.

## Expected unchanged boundaries

All top-level skill instructions and `agents/openai.yaml` files; skill membership; archive utility;
model-routing policy; manifest format; Codex and Claude destination paths; existing command options;
`.github/workflows/ci.yml`, `scripts/check.sh`, and pinned tool versions unless a demonstrated test
integration issue requires a narrowly justified change.

## Validation commands

| Command | Authority and purpose |
| --- | --- |
| `scripts/check.sh lint prose` | `AGENTS.md`, `scripts/check.sh`: shell/Python/YAML checks and Markdown/spelling |
| `scripts/check.sh validate test` | `AGENTS.md`, `scripts/check.sh`: skill validator, dry run, Python test matrix |
| `scripts/check.sh` | `ARCHITECTURE.md`, `scripts/check.sh`: equivalent full aggregate |
| `./sync-installable-skills.sh --dry-run` | Installer `usage`, check runner and CI: read-only destination preview |

Versions come from `scripts/tool-versions.env`. Tests run under Python 3.10–3.13 by default.
`uv` and `npx` are required by the runner. There is no configured static type checker.

## Selected external evidence

The shaper selected official Cursor documentation solely to verify the target runtime's discovery
contract. This section vendors concise factual notes as observed on 2026-10-26; the website exposes
no immutable revision here. Do not treat later website changes or unrelated guidance as policy.

- Origin: [Cursor skills documentation](https://cursor.com/docs/skills) and
  [Cursor skills help](https://cursor.com/help/customization/skills).
- Vendored factual notes: Cursor supports local personal skills under `~/.cursor/skills`, with
  each skill in a directory containing `SKILL.md`. It also reads Codex and Claude skill locations.
  This task supplies an explicit Cursor destination rather than relying on compatibility discovery.
- Applicability: destination and format only. These pages do not establish that this installer's
  symlink layout works, how duplicate names appear, or that every workflow can run.
- Attribution: retain the source links when reusing these notes. No source code or documentation
  passages are copied, and no third-party implementation is incorporated.

## Uncertainties to verify

Cursor symlink discovery and duplicate presentation need runtime evidence. No `cursor` executable
was found on PATH during shaping; this does not establish whether the desktop app is installed.
Use an isolated profile for discovery if available; otherwise report the missing check. Do not
enable cloud synchronization or install into the user's actual skill directories as an incidental
test. Revisit scope if copying or runtime-specific skill adaptations prove necessary.
