# Prompts for Codex

Open the target codebase in Codex on the machine that will run the experiment.
Replace the three task/location inputs. Repository, revision, and languages are discovered locally.

## 1. Prepare and preflight

```text
Prepare a native Codex experiment using the protocol at:
[toolkit checkout]/benchmarks/agent_tools/CODEX.md

Approved task/spec: [repository-relative path]
Flow to trace: [concrete existing flow and entry point]

Compare baseline, Reveal, and ast-grep using my already installed skills, preserving their full
workflows. Use developer plus task-reviewer in the same build worker; trace-domain-flow for flow;
discover-architecture for architecture. Keep both independent tasks and the build → flow →
architecture sequence: 18 measured workers, serially, one repetition.

Use this open repository. Discover local paths, commit, languages, and installed skill sources.
Choose a new results directory outside the target source repository. Do not reuse Claude results.
Follow CODEX.md to freeze tasks, exact tool commands and versions, skills, and the run order.
Use the project-locked Reveal version when present, never silently use the global executable.
Resolve tool commands separately in each isolated checkout. Preserve the assigned inspection tool
throughout skill handoffs and review, including overrides of conflicting repository tool guidance.

Run the local preflight and one small fresh native subagent smoke test. I authorize that setup
worker; do not launch any measured trials yet. Verify checkout access, installed skills, fresh
context, exact worker identity, and recovery of its local token/tool evidence. Account for this
as overhead. Native workers must not inherit coordinator history or see other answers.
Do not invoke Codex/Claude CLI model processes, SDK runners, or external model APIs.

Record actual capabilities and unresolved blockers, including required browser/test access.
Do not install or rewrite my skills. Do not change the original source checkout. Show the prepared
plan, accounting coverage, and any destination-specific setup still needed, then stop.
```

## 2. Run the prepared experiment

```text
Run the prepared native Codex experiment following CODEX.md at the toolkit location already given.
Use its saved plan and recheck the destination machine preflight. Run serially, using a fresh native
subagent with no inherited conversation for every measured task. I authorize those workers.
Use separate checkouts; keep all development tools and browser servers on the assigned checkout.
Inherit one consistent coordinator model/effort configuration and record observed worker settings.

Independent tasks start at the frozen commit. Chained stages inherit only the previous stage's
code and documents in a fresh checkout. Keep task-reviewer in the build worker, read-only during
review. Required validation failures, incomplete browser checks, and unresolved findings block
success even if the worker prints a passed marker. Do not advance a blocked chain.

Collect each exact worker's saved token and tool evidence, review report, validation results,
patch, and skill documents before launching the next worker. Stop if promised isolation or
accounting fails. Preserve failed attempts; no silent retries. Keep setup/coordinator usage
separate. Do not infer cost from account percentages or invent missing fields.

Produce the self-contained reports/results.json required by CODEX.md. Include all planned cases,
including blocked and not-run cases, with quality pending. Give me its full path for evaluation.
```
