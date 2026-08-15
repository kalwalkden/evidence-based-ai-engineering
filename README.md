<p align="center">
  <img src="assets/banner.svg" alt="Evidence-Based AI Engineering Toolkit" width="100%">
</p>

<p align="center">
  <strong>A delivery system for AI-assisted engineering that leaves an evidence trail you can defend — in code review, in a client meeting, or six months later.</strong>
</p>

<p align="center">
  <img alt="License: Apache-2.0" src="https://img.shields.io/badge/license-Apache--2.0-8a6d3b.svg?labelColor=050806">
  <img alt="10 skills" src="https://img.shields.io/badge/skills-10-8a6d3b.svg?labelColor=050806">
  <img alt="Runtimes: Codex and Claude Code" src="https://img.shields.io/badge/runtimes-Codex%20%7C%20Claude%20Code-8a6d3b.svg?labelColor=050806">
  <img alt="Requires bash 3.2+" src="https://img.shields.io/badge/requires-bash%203.2%2B-8a6d3b.svg?labelColor=050806">
</p>

---

We all know AI/LLMs can make an already capable engineer faster. It can also make a less experienced engineer confidently wrong — faster. The problem only magnifies when work starts from incomplete context, vague requirements, or an unfamiliar codebase.

This toolkit gives AI-assisted delivery a durable operating model: **inspect the real system, make the
decision trail explicit, shape a narrow plan, validate the result, and review it independently before
calling it done.**

## See it in 60 seconds

Install the skills. The installer tells you explicitly what it will do before it does anything:

```bash
./sync-installable-skills.sh --dry-run
```

```text
Linking: ~/.codex/skills/architect-feature -> evidence-based-ai-engineering/architect-feature
Linking: ~/.codex/skills/discover-architecture -> evidence-based-ai-engineering/discover-architecture
Linking: ~/.codex/skills/ship-task -> evidence-based-ai-engineering/ship-task
...
Would record 20 managed link(s) in ~/.local/state/sync-installable-skills/...
Dry run complete. No changes were made.
```

Then drive a feature through the loop. Each step hands the next one evidence rather than vibes:

```text
you ▸ Use discover-architecture on this repo.
      → docs/architecture.md — stack, conventions, hotspots, and the canonical
        lint/type-check/test commands, all read from the repo rather than assumed.

you ▸ Use architect-feature for per-org rate limiting.
      → ai/features/rate-limiting/feature.md   the plan and its tradeoffs
        ai/features/rate-limiting/tasks.md     an ordered, human-reviewable task list
        ai/features/rate-limiting/tasks/…      one brief per task
      ⏸  Stops for your approval before writing briefs.

you ▸ Ship the next task.
      → tasks/01-token-bucket/spec/     scope, call paths, constraints, what stays unchanged
        a small diff + tests, validated with the commands discovery found

you ▸ Review the feature.
      → an independent, read-only pass in a fresh context — reads the real diff,
        returns findings and a Ready / Not ready verdict it cannot grant itself.
```

The artifacts are noisy, but they are the point. When someone asks *why is this code like this*, the answer is in the
repository, next to the code, not lost.

## Three problems it solves

**1. The agent changed more than you asked, and you cannot tell what or why.**
Work is shaped into one task at a time against a written spec that names the files in scope *and the
boundaries that stay unchanged*. The review step resolves the exact diff for that task. The delta
is attributable instead of tangled with unrelated edits.

**2. "Done" means the model said it was done.**
Implementation never self-certifies. The feature review runs read-only in a fresh context  - ideally
on a different model. It returns a verdict against the actual git diff. An agent cannot mark its own
work done and cannot quietly fudge "tests didn't run" into "ready!"

**3. The reasoning evaporates when the conversation ends.**
Plans, specs, decisions, tradeoffs, and validation evidence are written to `ai/` beside the code and
archived on completion. The next engineer, or you in six months, inherits the decision
trail.

## Quick start

The smallest safe path is three commands. Nothing is installed until you've seen the plan.

```bash
git clone https://github.com/kalwalkden/evidence-based-ai-engineering.git && cd evidence-based-ai-engineering
```

**1. Preview.** Don't skip this, it shows every link that would change.

```bash
./sync-installable-skills.sh --dry-run
```

**2. Install.** Creates symlinks in `~/.codex/skills` and `~/.claude/skills`.

```bash
./sync-installable-skills.sh
```

**3. Start small.** In your own repo, run discovery first. It is read-only and produces a report you
can judge the toolkit by before trusting it with a change:

```text
Use discover-architecture on this repository.
```

The installer only manages its own links. It records what it installed, removes only those links when
a skill is later dropped from the list, and never touches real files, real directories, or symlinks
belonging to another project — if another project already owns a skill name, it skips that name with a
warning instead of taking it over. See [Installer safety](#installer-safety).

## Choose your workflow

Pick the smallest one that fits.

### Discovery only — unfamiliar codebase, no code changes yet

Read-only: Produces an architecture report or a traced end-to-end path. Use before estimating,
onboarding, or inheriting a system.

| Skill | Produces |
| --- | --- |
| `discover-architecture` | Stack, conventions, classified hotspots, and canonical validation commands |
| `trace-domain-flow` | One representative end-to-end path, documented under `docs/` and cross-linked |

### One task — a fix or a small change

Skip feature planning. Shape a spec and implement against it. Then, review the exact diff.

Run the three skills yourself, stopping between each:

| Skill | Role |
| --- | --- |
| `shape-spec` | Expands a brief into a task-level `spec/` package grounded in current repo evidence |
| `developer` | Implements one task, adds high-ROI tests, validates before reporting |
| `task-reviewer` | Spec-aware, read-only review of the resolved diff before merge |

**OR** hand the whole task to one skill:

| Skill | Role |
| --- | --- |
| `ship-task` | Runs shape + developer for exactly one task, then **stops** |

### A whole feature — multi-step work

Plan it, break it into reviewable tasks, then run to completion with an independent readiness gate.

| Skill | Role |
| --- | --- |
| `architect-feature` | Feature plan, visual design, `tasks.md`, and task briefs — pauses for approval |
| `ship-feature` | Runs every remaining task, then up to three independent reviews |

```text
discover-architecture → architect-feature → shape-spec → developer → task-reviewer
                        ↓       OR       ↓
                    ship-feature      ship-task (repeat until tasks are done)
```

## How this compares

| | Ad-hoc prompting | `AGENTS.md` / `CLAUDE.md` conventions | Heavyweight process (RFCs, gated boards) | **This toolkit** |
| --- | --- | --- | --- | --- |
| Setup cost | None | Low | High | Low — clone and symlink |
| Scales past one session | ✗ | Partial — conventions persist, decisions don't | ✓ | ✓ — artifacts live in the repo |
| Scope is written down before code | ✗ | ✗ | ✓ | ✓ — spec names what stays unchanged |
| Independent verification | ✗ | ✗ | ✓ — human reviewers | ✓ — separate context, ideally another model |
| Validation recorded as evidence | ✗ | ✗ | ✓ | ✓ |
| Overhead on a one-line fix | None | None | Severe | Moderate — skip to `ship-feature`\ `ship-task`, or don't use it |
| Enforced by tooling | ✗ | ✗ | ✓ — CI/approvals | ✗ — conventions, not gates |

### Honest tradeoffs

Worth knowing before you adopt it:

- **It costs more per change.** Discovery, specs, and an independent review mean more model calls and
  more wall-clock time. On a typo fix that overhead is pure waste, just edit the file yourself.
- **It is opinionated about layout.** Feature artifacts live under `ai/features/`, archives under
  `ai/archive/`. If that conflicts with your repo conventions, you can change the skills to fit your workflow.
- **Nothing is enforced.** These are agent instructions, not CI gates. An agent can ignore them and
  nothing here blocks a merge. Treat it as a strong default, not a control.
- **The review is a second opinion not a proof.** An independent adversarial pass on the real diff
  catches meaningfully more than self-review. It still misses things and a "Ready" verdict is not a
  guarantee of correctness.
- **It adds files to your repo.** Some teams want the decision trail in the repository; others will
  find `ai/` noisy. If you want plans in Linear or Notion instead you can modify the skills do that, but it is going to be a bit fussy.
- **Best results need model diversity.** The strongest guarantee is review by a different capable model.

## Installer safety

`sync-installable-skills.sh` links every skill named in `installable-skills.txt` into `~/.codex/skills`
and `~/.claude/skills`. It manages symlinks only that it owns:

- **It records what it installed** in a manifest under `${XDG_STATE_HOME:-~/.local/state}/`, keyed by
  repository path. The two checkouts never clobber each other's record.
- **It never takes over a name another project owns.** A link pointing elsewhere is skipped with a
  warning naming the owner not repointed.
- **It removes only its own retired links** and deleted only when this kit installed it.
- **It never touches real files or directories.** It only touches symlinks.
- **`--dry-run` writes nothing**.

## Compatibility

| | |
| --- | --- |
| **Runtimes** | OpenAI Codex (`agents/openai.yaml`) and Claude Code (`SKILL.md`) |
| **OS** | macOS and Linux |
| **Shell** | `bash` 3.2+ — the installer avoids bash 4 features, so stock macOS `/bin/bash` works |
| **Python** | 3.9+, and only for `archive-work-artifact`; the rest is prompt-level guidance |
| **Windows** | Not tested. The installer relies on POSIX symlinks |

Skills are plain Markdown with a small YAML block on top. Adapting the language, commands, and
quality gates to your team's practice is expected.

## Contributing

Contributions that improve evidence quality, clarity, safety, validation, and developer experience are
welcome! Keep additions focused, explain the problem they solve, and preserve the core idea: AI/LLM
assistance should make engineering work more understandable and trustworthy.

If you are changing the installer run the dry-run against a scratch `HOME` before opening a PR.

Contributions are accepted under the project's license, per Apache-2.0 section 5.

## Support

Questions, bug reports, and workflow experience reports go to [issues](../../issues). Adoption reports
are genuinely useful - especially the ones where the toolkit got in the way.

## License

Licensed under the Apache License, Version 2.0 — see [LICENSE](LICENSE).

Copyright 2026 Kal Walkden.

Apache-2.0 permits commercial and private use, modification, and redistribution, provided the license
and copyright notice are retained and changed files are marked. It also includes an express patent
grant from contributors.

## Created by

**Kal Walkden**, Fractional CTO. I build and lead engineering teams. This toolkit is the operating
model I use so AI-assisted delivery stays explainable to the people who have to trust it:
clients, boards, and the engineers who inherit the code.

[wtwentyseven.com](https://www.wtwentyseven.com)
