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

Reveal is available throughout Reveal runs; ast-grep is available throughout ast-grep runs.
Baseline uses ordinary reading/search. Each tool arm also retains ordinary reading/search.
Restrict only cross-arm code inspection. Follow CODEX.md's required-toolchain-check exception:
freeze exact commands, requirement sources, and stages; apply the same checks across arms.
Version/help and required installation/toolchain checks may use Reveal or ast-grep in any arm
without another approval. Do not extend this to outlines, searches, traces, or code review.
Include this policy in every worker prompt and preserve invocation evidence for evaluation.

Exclude interactive browser verification in all arms and stages, as already authorized in CODEX.md.
Do not require browser access, run interactive browser checks, or ask for that waiver again.
Keep normal automated tests, lint/type checks, builds, and task-reviewer. Record browser coverage
as waived, not passed, and pass this override to every worker and skill handoff. Carry forward
other explicit waivers approved for this campaign with their scope and approval evidence.
Freeze validation_policy in the plan before measured work.

Run the local preflight and one small fresh native subagent smoke test. I authorize that setup
worker; do not launch any measured trials yet. Verify checkout access, installed skills, fresh
context, exact worker identity, and recovery of its local token/tool evidence. Account for this
as overhead. Native workers must not inherit coordinator history or see other answers.
Do not invoke Codex/Claude CLI model processes, SDK runners, or external model APIs.

Record actual capabilities and unresolved blockers, including required automated test access.
Do not install or rewrite my skills. Do not change the original source checkout. Show the prepared
plan, accounting coverage, and any destination-specific setup still needed, then stop.
```

## 2. Run the prepared experiment

```text
Run the prepared native Codex experiment following CODEX.md at the toolkit location already given.
Use its saved plan and recheck the destination machine preflight. Run serially, using a fresh native
subagent with no inherited conversation for every measured task. I authorize those workers.
Use separate checkouts; keep all development tools and test commands on the assigned checkout.
Inherit one consistent coordinator model/effort configuration and record observed worker settings.

Independent tasks start at the frozen commit. Chained stages inherit only the previous stage's
code and documents in a fresh checkout. Keep task-reviewer in the build worker, read-only during
review. Pass the frozen validation_policy to every worker and review. Allow its exact required
toolchain checks across all arms while keeping inspection restricted to the assigned tool.
Use the authorized default excluding interactive browser verification across all arms and stages;
do not ask again or block a review, handoff, or chain for that omitted check. Keep automated validation.
Validation failures and incomplete required checks without an applicable waiver, plus unresolved
findings, block success even if the worker prints a passed marker. Preserve approved waivers as waived, not passed; do
not ask again for the same approval. A chain may advance when remaining validation and review
pass under that policy. Do not advance a blocked chain or claim full validation when checks were waived.

Collect each exact worker's saved token and tool evidence, review report, validation results,
patch, and skill documents before launching the next worker. Stop if promised isolation or
accounting fails. Preserve failed attempts; no silent retries. Keep setup/coordinator usage
separate. Do not infer cost from account percentages or invent missing fields.

Produce the self-contained reports/results.json required by CODEX.md. Include all planned cases,
including blocked and not-run cases, with quality pending. Embed scoped toolchain-check evidence,
the validation policy used by each attempt, and waiver limitations so evaluation can distinguish
allowed checks from prohibited inspection. Give me its full path for evaluation.
```
