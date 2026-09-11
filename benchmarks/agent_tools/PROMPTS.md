# Prompts to paste into Claude Code

Use one Claude project per codebase. Paste these prompts there, where your skills are already
installed. Replace bracketed values. The toolkit directory is the checkout containing this harness.
After the run, bring `reports/results.json` back to the conversation where we designed the
experiment. We will evaluate that file and compare the codebases there.

## 1. Set up the experiment

```text
Set up a pilot experiment using the existing harness at:
[toolkit checkout]/benchmarks/agent_tools/

This tests MY installed evidence-based-ai-engineering skills:
- developer: implement the approved task, including its normal validation and handoffs.
- task-reviewer: review that implementation against its full task/spec and exact diff within
  the build session, following its read-only review contract and normal developer repair loop.
- trace-domain-flow: trace the named flow and write/cross-link its normal documents.
- discover-architecture: produce its normal ARCHITECTURE.md and AGENTS.md updates.

Approved task/spec: [repository-relative path]
Flow to trace: [concrete flow and entry point]
Experiment files and results: [directory outside the codebase]

Use the repository open in this Claude session as the codebase and resolve its root automatically.
Derive the starting revision from its current HEAD and infer its implementation
languages from the source and project configuration. Record both in the experiment configuration
and freeze the resolved commit in the plan. Flag any required spec or source changes that are
uncommitted, since the experiment checkouts use committed files.

Use the installed task-reviewer skill as the build review gate, not a separately supplied acceptance
script. Keep the developer skill's normal tests and validation. Leave external checks empty in the
configuration. Preserve review findings, the final assessment, and material test gaps in the output.
Review in the current build context; do not add a separate reviewer session or subagent.

Compare baseline, reveal-cli, and ast-grep. Baseline uses ordinary file reading and search without
reveal or ast-grep, including in skill handoffs. Keep the installed skills and my normal Claude
setup. Do not use bare mode, replace the skill workflows, or build a new testing system.
Only vary the optional inspection tool. Apply that choice to skill handoffs too.

Configure both independent runs and a build → flow → architecture sequence, with one repetition.
Use the harness defaults for model and limits for the pilot unless they are unsupported here.
Read its README, create the three task prompt files and configuration, verify prerequisites,
and generate the plan. Keep quality scoring separate from token and reported-cost accounting.

Do not launch the experiment yet. Show the planned cases, session count, cost caps, and any
missing input needed to run the actual skills. Do not invent missing spec decisions or answer keys.
```

## 2. Run the prepared experiment

```text
Run the prepared experiment at [campaign directory] using the existing harness in
[toolkit checkout]/benchmarks/agent_tools/.

Use normal headless Claude Code and the skills already installed here. Do not use bare mode,
replace the skill instructions, or switch to a different agent. Keep the configuration's tool
assignment in effect through the skills' handoffs.

Execute the frozen plan. Preserve the transcript, skill artifacts, patches, validation results,
tokens, and reported costs for every attempt. Keep independent and chained runs separate.
Respect the configured caps and report failures or missing accounting without silently retrying.

If this Claude session cannot launch the headless child sessions, give me the exact existing
harness command to run in a separate terminal. Do not redesign the experiment.

When execution ends, run the existing report command to generate reports/results.json.
Give me that single file and its full path so I can bring it back for evaluation. It must include
the recorded tokens, costs, test output, documents, patches, and failures. Leave quality scores
pending: we will evaluate them in the other conversation. Do not declare a winning tool.
```
