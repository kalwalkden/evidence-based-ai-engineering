# Prompts to paste into Claude Desktop

Open the codebase in Claude Desktop's **Code tab**, using a local session with your installed
skills. Replace the bracketed values below. All model work stays in Desktop's native agents.
The skills still use normal development tools, including Git, tests, Reveal, and ast-grep.

## 1. Set up the experiment

```text
Prepare this experiment in Claude Desktop using native dynamic workflows and fresh subagents.
Do not launch the Claude CLI, headless Claude processes, or an Agent SDK runner.

Read CLAUDE_DESKTOP_README.md and DESKTOP.md at:
[toolkit checkout]/benchmarks/agent_tools/

Approved task/spec: [repository-relative path]
Flow to trace: [concrete existing flow and entry point]
Experiment files and results: [directory outside the codebase]

Use the repository open in this session. Resolve its root, current commit, and implementation
languages automatically. Required spec and source changes must be committed before freezing
inputs. Keep the original checkout untouched; prepare isolated trial checkouts.

Compare baseline, reveal-cli, and ast-grep using MY existing installed skills:
- Build: developer, including normal tests, task-reviewer in the same worker context, repairs,
  and normal completion/archival requirements.
- Flow: trace-domain-flow and its normal documents and cross-links.
- Architecture: discover-architecture and its normal ARCHITECTURE.md and AGENTS.md updates.

Baseline uses ordinary reading/search without Reveal or ast-grep. Reveal follows the skills'
existing optional enrichment guidance. ast-grep substitutes only that optional inspection layer.
Keep evidence verification and fallback requirements. Apply the assigned tool to handoffs and
review too. Do not replace or install skills, or add a separate acceptance-check script.

Prepare independent tasks and a build → flow → architecture sequence, one repetition:
3 configurations × 3 stages × 2 modes = 18 measured workers, run serially. Keep preparation and
collection overhead separate. Each worker gets only its frozen task, tool assignment, repository
instructions, and assigned checkout, not other workers' answers or coordinator history.

Use the available native workflow-authoring reference to prepare the workflow and prompts;
do not invent Workflow API fields. Follow DESKTOP.md. Do not execute harness.py run or reuse its
CLI accounting parser. Use one fixed model and effort for all measured workers and record them.

Verify native workflows are available and workers can use my installed skills and their own
checkout. Check which native per-worker token/cost evidence can actually be collected. Record
unsupported fields as null with reasons. Do not estimate tokens or claim CLI spending caps apply.
If required isolation or skills cannot be preserved, stop and identify the missing capability.

Save the frozen plan, native workflow, versions, prompts, and results template outside the codebase.
Show the cases, accounting coverage, and limits Desktop can actually enforce. Do not start measured
workers yet. Disclose missing per-worker tokens or costs before I decide to run the experiment.
```

## 2. Run the prepared Desktop experiment

```text
Run the prepared Desktop experiment at [experiment directory] using its frozen native workflow.
Keep all Claude model work in Desktop; do not launch a CLI or Agent SDK runner.

Follow DESKTOP.md from the toolkit. Run each measured task in a fresh native worker and its assigned
checkout, serially. Preserve my installed skills and the assigned inspection tool throughout.
Keep task-reviewer inside the build worker. Do not use side chats or resume a prior task's worker.

Independent tasks start at the frozen original commit. Chained stages inherit only the previous
stage's code and documents in a new checkout and fresh context. Do not advance after a failed or
blocked build/review/validation, or failed flow. Preserve failures and unattempted cases.

Save each worker's artifacts and native accounting as it finishes. Keep usage from failed attempts
and coordinator/preparation/collection work separately identifiable. Never rerun a worker silently;
any retry needs its own attempt record and usage. Respect the limits recorded in the plan.
Look for the saved local transcript matching each exact native worker ID; a limited Agent-tool
return does not mean the transcript is unavailable. Use collect_desktop_evidence.py as described
in DESKTOP.md to create a separate evidence snapshot, without overwriting live results. This helper
only reads evidence and writes a bundle; it does not launch any Claude model process.
If usage evidence cannot be collected as planned, save partial results and stop before another
measured worker starts. Do not derive tokens from context percentages or shared plan usage.

Collect one self-contained reports/results.json following DESKTOP.md, including every planned
case, native usage evidence, missing-data reasons, review reports, tests, documents, patches,
and transcript coverage. Leave quality scores pending and do not declare a winning tool.
Give me the file and its full path so I can bring it back for evaluation.
```
