# Complexity decision rule implementation map

## Primary edit targets

| Path | Section | Intended change |
| --- | --- | --- |
| `architect-feature/SKILL.md` | Priorities / Rules | Place the full common rule near KISS/YAGNI so feature plans do not invent requirements |
| `shape-spec/SKILL.md` | Planning Rules | Place the full common rule near KISS/YAGNI and decision provenance guidance |
| `developer/SKILL.md` | Core Rules | Place the full common rule near the simplest-correct-implementation guidance |
| `feature-reviewer/SKILL.md` | Review the Assembled Feature | Add the requested necessity check even for faithful spec implementations |

## Entry point and instruction flow

`architect-feature` records feature decisions and task briefs. `shape-spec` verifies one task against
the current tree and writes its plan and references. `developer` uses that package as its primary
implementation source. `feature-reviewer` compares the assembled implementation with feature and
task artifacts in an independent context.

These are prompt-level handoffs, not an executable call graph. The common rule must act at the
first two stages, before speculative complexity becomes a written requirement. Later stages must
not treat that written requirement as independent evidence of necessity.

## Contracts, state, and invariants

- `architect-feature` already prioritizes KISS/YAGNI and limits speculative scope.
- `shape-spec` already requires decision provenance and separates binding inputs from observed
  patterns. Its Planning Rules already reject speculative abstractions and hypothetical consumers.
- `developer` calls the full spec its primary source of truth. Preserve its handoff role while
  applying the user's explicit rule that generated specs do not independently justify complexity.
- `feature-reviewer` treats feature/task artifacts as intended behavior and rejects speculative
  findings. The new check must allow demonstrable unnecessary machinery to be flagged even when
  it appears in those generated artifacts. Preserve read-only review and existing severity rules.
- No runtime state or data contract changes are needed.

## Supporting repository evidence

- `docs/design-principles.md`: existing KISS/YAGNI, proportional verification, distinct stage roles,
  and reuse of recorded decisions without redundant confirmation.
- `ai/archive/features/toolkit-simplicity-and-validation/tasks/001-stage-aware-planning-and-testing/spec/plan.md`:
  historical provenance for the toolkit's under-development stage and earlier simplicity/testing
  work. Supporting context, not authority for new requirements.
- `scripts/validate_skills.py`: `check_skill`, `check_skill_list`, and `main` validate skill structure
  and membership; they do not validate the behavioral meaning of prose instructions.

## Tests and validation commands

No existing automated test exercises agents' interpretation of these four skill instructions.
Do not add tests that merely match their wording. Inspect the final diff against the user's text
in `plan.md`, including its no-extra-ceremony constraint.

| Command | Authority and purpose |
| --- | --- |
| `scripts/check.sh lint prose` | `AGENTS.md`, `scripts/check.sh`: code/config lint and Markdown/spelling checks |
| `scripts/check.sh validate test` | `AGENTS.md`, `scripts/check.sh`: skill structure, installer dry run, existing Python test matrix |
| `git diff --check` | Focused whitespace check |

The canonical runner requires `uv` and `npx`; pinned versions live in `scripts/tool-versions.env`.

## Expected unchanged boundaries and uncertainties

Keep skill frontmatter and manifests, installation, orchestration, review independence, validation
policy, and archived artifacts unchanged. Leave the pre-existing untracked `.claude/` directory
untouched. All four requested targets exist; no stale target assumptions or unresolved product
decisions were found. No external guidance was selected.
