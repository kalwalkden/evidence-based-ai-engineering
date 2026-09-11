# Test this repository's skills in Claude Code

The question is specific: **which inspection tool helps these skills work best on your codebases?**

Use one Claude project per codebase. Copy the [experiment prompts](PROMPTS.md) into that project,
run the experiment there, and bring `reports/results.json` back here for evaluation.
Claude already has the skills installed. The harness records headless runs using those installed
skills; it does not supply replacement workflows or install another skill library.

| Stage | Installed skill | Expected work |
| --- | --- | --- |
| Build | `developer` + `task-reviewer` | Implement an approved task/spec, validate, review in the same context, and complete normal handoffs |
| Flow | `trace-domain-flow` | Trace the named flow, write the document, and cross-link the root docs |
| Architecture | `discover-architecture` | Write `ARCHITECTURE.md` and update its managed `AGENTS.md` block |

The three configurations are baseline, Reveal, and ast-grep. Baseline uses ordinary file reading
and search without Reveal or ast-grep, including in skill handoffs. Reveal uses the skills' existing
optional enrichment instructions. The ast-grep configuration substitutes ast-grep where useful,
preserving the skills' evidence requirements.
That small tool override is part of the experiment; the skill files themselves are unchanged.

## Run from Claude

Use the setup and execution prompts in [PROMPTS.md](PROMPTS.md). Keep the normal Claude
login, settings, installed skills, and repository instructions. There is no bare mode, isolated
login directory, empty settings selection, or replacement system prompt.

The runner needs Python 3.10+, Git, Claude Code, and both inspection CLIs on macOS or Linux.
It inherits authentication from the environment and normal Claude login. An API key is not required
by the harness. USD values are Claude's reported estimates, including when using a subscription;
they must not be described as additional subscription charges or actual invoice totals.

The existing commands are:

```bash
python3 benchmarks/agent_tools/harness.py plan /path/to/experiment.json --output /path/to/campaign
python3 benchmarks/agent_tools/harness.py run /path/to/campaign
python3 benchmarks/agent_tools/harness.py report /path/to/campaign
```

Planning and reporting make no model calls. Running starts headless Claude sessions. If the Claude
session hosting the experiment cannot launch nested sessions, run the same command from a separate
terminal; do not change the skills to work around the host restriction.

## Prepare the cases

Claude uses [example.json](example.json) to prepare the configuration for the repository open in
the current session, resolving its root automatically. It derives the starting revision from the
current HEAD and infers the implementation languages from the source and project configuration, recording both without manual input.
Required spec and source changes must be committed so they appear in the experiment checkouts.
The configuration also holds optional preparation commands and three prompt files. The build
prompt must identify an approved task/spec package already present in the chosen commit. The flow prompt must name the
flow to trace. The architecture prompt can simply request the installed discovery skill.

Use the installed `task-reviewer` skill as the build review gate within the normal `developer`
workflow. It reviews the full task/spec and exact diff in the same build context, with the assigned
inspection tool. Its review pass stays read-only; fixes follow the developer repair loop. Keep normal
tests and validation. No acceptance script or separate reviewer session is required.

Leave task `checks` empty for this experiment. Optional external commands remain supported for
existing configurations; if supplied, their failures also block the build. Commands use argument
arrays, not shell text. Optional `evaluation_files` are hashed for reproducibility. Preparation runs
outside model timing and must not change source files that Git would track.

The example defaults to Sonnet 4.6, high effort, one repetition, USD 2 per session, and a USD 50
campaign budget. These are editable starting settings. A complete pass with both modes is 18
sessions per codebase: three tool configurations, three stages, two modes. Five codebases mean 90
sessions before repetitions. Start with one codebase and adjust limits after the pilot.

## Independent and chained runs

- **Independent:** each skill starts in a separate checkout of the same original commit.
- **Chained:** build, then flow, then architecture. Each starts a fresh conversation and inherits the
  preceding stage's code and documentation, including the flow report and its cross-links.

A failed build, a blocked or missing reported task review, or failed optional external checks block
the chained follow-ups; a failed flow blocks architecture. Keep those outcomes in the results. Independent results compare equivalent starting inputs. Chained results
measure your full workflow, including differences introduced by earlier stages.

The source checkout stays untouched. Runs use separate clones; patches include tracked and new
files not excluded by Git. Modified Markdown documents are also saved under each run's `documents/`.
Analysis stages may change the documentation their skills own; changes to application source
invalidate those runs. Review still needs to check section ownership and link correctness.

## What is recorded

- Starting commits, task prompts, tool versions, and repository skill files saved for reference.
- The requested skill and observed Skill-tool calls, reported task-review status and findings in
  the answer/transcript, changed documents, binary patch, and validation logs.
- Ordinary input, cache creation, cache reads, output tokens, reported USD, time, and tool-call count.
- Failed, blocked, interrupted, and not-run sessions. Missing usage stays missing, never zero.

The skill reference copy is evidence only: it is not loaded into Claude. Keep the installed skills
pointing at this repository and leave the Claude environment unchanged between configurations.
Normal hooks, memory, plugins, and repository instructions remain active. Results therefore describe
this skill set in your Claude environment, rather than a claim about all agents or all tool setups.

The collector uses final per-model accounting when available, avoiding repeated cumulative events.
It preserves spend on failures and stops further calls if cost is unknown. The campaign budget
reserves a full session cap before each call; an API response may cross Claude's cap. Completed runs
are not retried. Investigate interrupted runs before starting another campaign.

Tool selection is a prompt instruction, not an OS sandbox. Check the transcript for compliance,
including handoffs. Bash and skill tools are permitted for headless work; normal Claude settings
and managed restrictions still apply. Nothing is published automatically.

## Quality first, then efficiency

Leave quality forms pending during the Claude run. Bring `reports/results.json` back to the
experiment-design conversation, where we can evaluate the skill artifacts, source evidence,
task-reviewer findings, normal validation, and review transcript together. Score correctness,
completeness, and evidence from 0 to 4: 0 is unusable,
2 requires substantive repair, 3 meets the important requirements, and 4 covers the checked scope
including edge cases. Record critical errors, tool-policy compliance, whether the skill's full
workflow was followed, and whether the assigned inspection tool was actually used.

An acceptable run needs all three scores at least 3, zero critical errors, both compliance checks,
a completed session, a reported passing task review for builds, and no failed optional checks.
Review `developer`'s tests, review, and archival; review the actual flow/architecture files and their cross-links, not just the final
chat summary. The recorded review status is the agent's report, not independent verification or an
experiment quality score. Verify it against the transcript during our later evaluation. A missing
review marker stays missing and blocks chained follow-ups. Score before looking at cost where
practical. Blank quality forms remain pending.

Reports group by repository, language, skill, and mode:

- **`results.json`: the single file to bring back**, including the plan, skill references, per-run
  records, transcripts, code patches, changed documents, and validation output. It includes code
  and local paths and is intended for private evaluation, not direct blog publication.
- `runs.csv`: every planned session and its measurements.
- `summary.csv` and `results.md`: quality counts followed by usage and known-cost totals.
- `paired.csv`: candidate-minus-baseline deltas for Reveal and ast-grep within matched cases; deltas stay blank until both
  results pass quality review and both measurements exist.

For the later blog posts, retain prompts, skill references, results, failures, and review notes.
Separate independent and chained conclusions, report sample sizes, and explain which tool earned
its place in each skill/language combination. Review private code and transcripts before sharing.

## Offline smoke test

```bash
python3 benchmarks/agent_tools/harness.py demo --output /tmp/tool-comparison-demo
```

This creates a small Python repository with an approved standalone spec, normal tests, and a
configuration using task-reviewer within the build workflow. It does not call Claude. Automated
tests use a fake Claude process and real temporary Git repositories; they verify orchestration and accounting, not actual
skill execution quality. A live pilot in your Claude environment is still required.

References: [Claude headless mode](https://code.claude.com/docs/en/headless),
[CLI flags](https://code.claude.com/docs/en/cli-reference), and
[usage accounting](https://code.claude.com/docs/en/agent-sdk/cost-tracking).
