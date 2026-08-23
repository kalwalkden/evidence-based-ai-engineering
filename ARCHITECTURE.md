# Architecture

## Detected stack

- Markdown skill definitions are the primary product surface. Each top-level skill directory owns a
  `SKILL.md` and an `agents/openai.yaml` interface manifest (`scripts/validate_skills.py`).
- Python 3.9+ supports skill validation and the archive utility; Ruff and pytest configuration lives
  in `pyproject.toml` (`pyproject.toml`, `archive-work-artifact/`).
- POSIX shell implements installation and the canonical local check runner
  (`sync-installable-skills.sh`, `scripts/check.sh`).
- GitHub Actions runs the same lint, prose, validation, and Python test classes as the local runner
  (`.github/workflows/ci.yml`, `scripts/tool-versions.env`).

## Conventions

- Skills are self-contained top-level directories. Frontmatter names must match their directory,
  every skill needs `agents/openai.yaml`, and `installable-skills.txt` lists every skill exactly once
  (`scripts/validate_skills.py`).
- Skill behavior is expressed as concise Markdown instructions. The repository prefers durable,
  evidence-backed artifacts and separates discovery, planning, shaping, implementation, review, and
  archival responsibilities (`docs/design-principles.md`).
- Markdown structure, spelling, Python style, YAML, and shell are checked with pinned tools
  (`.markdownlint-cli2.jsonc`, `cspell.json`, `pyproject.toml`, `.yamllint.yaml`,
  `scripts/tool-versions.env`).
- Python tests use pytest and currently concentrate on the archival script
  (`archive-work-artifact/tests/test_archive_work_artifact.py`).

## Linting and testing commands

- All checks: `scripts/check.sh` (`scripts/check.sh`).
- Focused groups: `scripts/check.sh lint`, `scripts/check.sh prose`,
  `scripts/check.sh validate`, and `scripts/check.sh test` (`scripts/check.sh`).
- The all-checks command requires `uv` and `npx`; it obtains pinned tools on demand
  (`scripts/check.sh`, `scripts/tool-versions.env`).

## Project structure hotspots

- Skill contract boundary: each `<skill>/SKILL.md` defines agent behavior while
  `<skill>/agents/openai.yaml` exposes the runtime-facing name and default prompt
  (`scripts/validate_skills.py`).
- Workflow boundary: `discover-architecture/SKILL.md` creates repository orientation consumed by
  `architect-feature/SKILL.md`, while `trace-domain-flow/SKILL.md` deepens one selected path.
- Installation boundary: `installable-skills.txt` is the source list consumed by
  `sync-installable-skills.sh`; structural validation keeps that list aligned with skill directories
  (`scripts/validate_skills.py`).
- Validation boundary: `scripts/check.sh` is the canonical aggregator mirrored by
  `.github/workflows/ci.yml`, with versions centralized in `scripts/tool-versions.env`.
- Recent Git history is concentrated in `README.md`, CI, installer, and orchestration skills. This is
  maintenance activity, not evidence that those files are defective.

## Analysis coverage and limitations

- Covered all top-level skill definitions, manifests, repository configuration, validation scripts,
  tests, CI, and root documentation by direct inspection.
- Reveal 0.122.0 was present. Its local agent help contributed capability orientation only; no
  structural adapter output was used as a report finding because this repository is predominantly
  Markdown and its small Python and shell surfaces were directly reviewable.
- Git activity was sampled from 2025-08-23 through 2026-08-23. Counts identify frequently touched
  files only and were not combined with a comparable complexity metric.
- No runtime execution graph was inferred. Prompt-level skill behavior depends on the consuming
  agent and cannot be proven by static analysis alone.

## Do and don't patterns

- Do keep each skill narrow and hand off through repository artifacts
  (`docs/design-principles.md`, `architect-feature/SKILL.md`, `shape-spec/SKILL.md`).
- Do preserve a green boundary between planned tasks and validate with the canonical runner
  (`architect-feature/SKILL.md`, `developer/SKILL.md`, `scripts/check.sh`).
- Do keep tool and CI versions in one source of truth
  (`scripts/tool-versions.env`, `.github/workflows/ci.yml`).
- Do not treat static-analysis leads as proof; verify material claims against repository evidence
  (`discover-architecture/SKILL.md`, `docs/design-principles.md`).
- Do not let implementation certify its own readiness
  (`task-reviewer/SKILL.md`, `feature-reviewer/SKILL.md`, `docs/design-principles.md`).

## Open questions

- None.

## Deep-dive references

- No domain-flow deep dives exist yet. Useful future traces are the skill installation lifecycle,
  one-task shipping lifecycle, and feature completion/archive lifecycle.
