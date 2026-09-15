# Implementation map

## Primary edit targets

- `developer/SKILL.md`: `Role`, `Core Rules`, `Validation`, `Review Loop`, and `Completion Report`.
  Owns the repeated full-suite mandate, repair validation, and task completion contract.
- `ship-feature/SKILL.md`: `Ship Every Task Sequentially` owns selection and both worker prompts;
  `Keep a Durable Run Log` owns evidence and counts; `Launch the Independent Feature Review` and
  `Repair Within Three Review Attempts` own final and repair gates.
- `docs/design-principles.md`: `Verification should match the claim` explains the validation
  distinction while preserving correct intermediate states.

## Entry point and call path

`$ship-feature` preflight and branch gate → read current `tasks.md` → shape one task → inspect its
spec → dispatch `$developer` → required validation → local `$task-reviewer` and repair loop →
record task completion/evidence → next task → fresh `$feature-reviewer` full validation/verdict →
bounded repairs and fresh review when needed → completion and archive.

The policy travels from the parent into shaping artifacts and the implementation prompt. The
developer validates eligibility against disk. Independent review keeps its own full validation.

## Contracts, state, and invariants

- `tasks.md` is the durable source for task ordering and completion. The selected task is final
  when no other incomplete task remains, not necessarily when its directory sorts last.
- Task specs define intended checks; actual changed behavior determines whether more are needed.
- The temporary Git baseline and reviewed after-tree isolate each task from earlier uncommitted
  changes. Preserve this mechanism unchanged.
- `ship-log.md` stores command results, review evidence, and canonical full-validation counts.
  Deferral is not success and a focused run is not a full-validation execution.
- Local task review stays mandatory. Independent feature review stays read-only and fresh.
- Hosted-session persistence uses the same task validation policy; no new commit authority.

## Patterns to reuse

- `developer/SKILL.md`, `Completion Update`: an existing explicit parent-owned feature-review
  handoff already changes behavior under `$ship-feature` without a duplicate developer skill.
- `ship-feature/SKILL.md`, worker prompts and result checks: pass explicit context, write durable
  artifacts, then inspect results before continuing.
- `feature-reviewer/SKILL.md`, `Review the Assembled Feature`: canonical full validation belongs to
  the fresh reviewer and failures block readiness. Preserve this policy.

## Tests and fixtures

- No automated skill-behavior test currently covers this prompt-level workflow. Use the scenario
  table and acceptance cases in `plan.md` for semantic verification.
- `scripts/validate_skills.py`: `discover_skills`, `check_skill`, and `check_skill_list` validate
  frontmatter, interface manifests, and installation registration, not execution behavior.
- `archive-work-artifact/tests/test_archive_work_artifact.py` and
  `benchmarks/agent_tools/tests/` are existing regression suites run by the canonical test group;
  neither is an edit target for this task.

## Expected unchanged boundaries

- `feature-reviewer/SKILL.md`: fresh review and full project validation.
- `task-reviewer/SKILL.md`: exact change target and local defect-first review.
- `ship-task/SKILL.md`: full-suite validation through the default developer policy.
- `architect-feature/SKILL.md`: tasks must preserve correct intermediate states.
- `shape-spec/SKILL.md`: generic shaping remains unchanged; caller supplies validation context.
- `developer/agents/openai.yaml`, `ship-feature/agents/openai.yaml`, and
  `installable-skills.txt`: no new skill or invocation surface.
- `scripts/check.sh`, `scripts/tool-versions.env`, and `pyproject.toml`: validation tooling and
  discovery remain unchanged.

## Validation commands

| Command | Purpose | Authority |
| --- | --- | --- |
| `scripts/check.sh prose` | Markdown structure and spelling | `scripts/check.sh`, `ARCHITECTURE.md` |
| `scripts/check.sh lint prose` | Required lint/format and prose checks | `AGENTS.md` |
| `scripts/check.sh validate test` | Skill structure, installer dry run, complete pytest matrix | `AGENTS.md`, `scripts/check.sh` |
| `scripts/check.sh` | All canonical groups | `scripts/check.sh`, `ARCHITECTURE.md` |

The runner requires `uv` and `npx`, with tool versions in `scripts/tool-versions.env`. Tests run
under Python 3.10, 3.11, 3.12, and 3.13 by default. No static type checker is configured.

## Uncertainties to verify

- Recheck all unconditional full-suite wording during editing, especially the developer role,
  core rules, repair loop, and embedded ship-feature implementation prompt.
- No active feature fixture exists for this change. Archived feature artifacts illustrate the
  artifact structure but must not be edited or used as a live shipping target.
- Architecture documentation describes tests mainly in the archive utility; current pytest
  discovery also includes benchmark tests. Use the actual canonical runner for complete coverage.
- Static checks cannot establish how an agent will follow the new policy. Report semantic review
  separately from executed automated checks; do not claim an end-to-end agent run without one.

All references above are current repository evidence. No external material was selected.
