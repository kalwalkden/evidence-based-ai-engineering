# Compare inspection tools in Claude Desktop

Use one local **Code tab** session per codebase to prepare and coordinate the experiment.
Copy [Prompt 1](CLAUDE_DESKTOP_PROMPTS.md) into that session, review the plan, then paste Prompt 2 to run it.
Bring the resulting `reports/results.json` back for evaluation.

The experiment compares **baseline, Reveal, and ast-grep** with your existing installed skills:

| Stage | Skills | Result |
| --- | --- | --- |
| Build | `developer` and `task-reviewer` | Implementation, normal tests, review, and handoffs |
| Flow | `trace-domain-flow` | Flow document and cross-links |
| Architecture | `discover-architecture` | Architecture report and managed instructions |

There are 18 measured workers: three configurations, three stages, and two modes, once each.
Independent tasks start from the original commit. Chained tasks inherit the previous stage's code
and documents, with a fresh worker for each stage. Task review stays inside the build worker.
Coordinator and preparation work add overhead, recorded separately from those 18 tasks.

All model runs use Desktop's native agents. Normal development tools still run through the skills.
The [Desktop protocol](DESKTOP.md) defines isolation, evidence, and the portable results contract.
Claude prepares the native workflow in the target project using its available authoring reference.

The [evidence collector](collect_desktop_evidence.py) can recover saved native worker transcripts,
tool results, request usage, and model/effort records by exact worker ID. It embeds local artifacts
into a separate portable snapshot without modifying the running experiment or starting agents.
See [collection instructions](DESKTOP.md#recover-evidence-from-local-desktop-transcripts).

Anthropic documents native workflows in Desktop and per-agent token displays. The exact usage
export available in your installed version must be checked during setup. Missing cost or detailed
token fields stay unknown. The headless runner's automatic accounting and spending caps do not
carry over to Desktop. [Workflow documentation](https://code.claude.com/docs/en/workflows)

This Desktop workflow has not been executed against a real codebase here. The existing Python
tests cover the earlier headless runner, not Desktop execution. Setup checks the actual Desktop
capabilities before measured runs; no model calls are launched here.

The earlier [headless runner](HEADLESS.md) and [headless prompts](HEADLESS_PROMPTS.md) remain available
as a separate mode. Do not mix their accounting with Desktop results or run the headless commands
for a Desktop experiment.
