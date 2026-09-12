# Compare inspection tools in Codex

Run this experiment in a Codex task opened on the target codebase, using your installed skills.
Start with the [setup prompt](PROMPTS.md), then run the prepared plan when ready.
The [native protocol](CODEX.md) explains preparation, workers, evidence, and migration to another machine.

Compare baseline (ordinary reading/search), Reveal, and ast-grep. Test each with:

| Stage | Installed skills |
| --- | --- |
| Build | developer, task-reviewer in the same worker, normal validation and archival |
| Flow | trace-domain-flow |
| Architecture | discover-architecture |

Keep both independent tasks and a build → flow → architecture sequence. Three tools, three stages,
and two modes give **18 measured workers**, run serially with fresh contexts. Chained stages inherit
code and documents only. Preserve the skills' workflows; change only the inspection-tool assignment.

The coordinator uses native Codex subagents. Python helpers prepare/check local inputs and collect
saved evidence; they never launch model processes. [codex_native.py](codex_native.py) checks exact
executable versions and installed skill fingerprints, and exports per-worker token records and
filtered text/tool evidence. Cost stays unknown when no verified billed amount is available.
Account-wide subscription usage is not per-worker cost, and API price estimates are not charges.

Quality is evaluated first, by skill and implementation language. Keep failed/blocked attempts and
all their usage. Do not rank tools from one repetition alone or infer quality from token savings.
Bring the self-contained `reports/results.json` back for evaluation and later blog writing.
Review project-sensitive evidence before publishing it.

## Move to another machine

Check in this directory and the root README changes. Include the newly added Python files,
protocol, tests, and preserved historical guides. Do not check in local experiment results,
checkouts, dependencies, or Codex session logs. Paths and installed environments do not transfer.

On the other machine, check out the branch and install this repository's skills using the root
README's normal setup. Open the target codebase in Codex and paste Prompt 1. Setup resolves local
paths, checks the exact tool versions, and repeats the native worker smoke test before any trials.
The target feature spec and required source changes must also be committed in that codebase.

`codex_native.py` requires Python 3.10+ and Git; it uses only the Python standard library.
Run its tests with the repository's pinned pytest environment. The smoke test and preflight are
setup overhead; they are not any of the 18 measured trials. Native tools and local log schemas
can differ between machines, so a successful local check does not certify the destination.

## Historical Claude experiments

The [Claude Desktop prompts](CLAUDE_DESKTOP_PROMPTS.md), [guide](CLAUDE_DESKTOP_README.md),
[protocol](DESKTOP.md), and [collector](collect_desktop_evidence.py) remain available for historical
results. The [headless runner](HEADLESS.md) is also retained. Their formats and accounting are
separate; do not use `harness.py run` for a native Codex experiment or merge old attempts into it.
