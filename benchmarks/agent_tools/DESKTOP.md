# Desktop experiment protocol

This contract supports the [copyable prompts](PROMPTS.md). Claude prepares the native workflow
using the authoring reference available in the target Desktop session. All model work uses native
agents, with no Claude CLI or Agent SDK subprocesses. Git, inspection tools, and test runners
remain part of normal skill work.

## Freeze and isolate

- Resolve the current repository, commit, languages, and approved spec. Required uncommitted spec
  or source changes are blockers. Keep the original checkout untouched.
- Record installed skill paths, source texts and hashes, tool versions, model, effort, Desktop
  version when available, and relevant settings. Exclude secrets.
- Verify native workers can load the installed skills, use an assigned checkout, and start without
  coordinator history. If not, return a setup blocker instead of changing the experiment.
- Freeze the three task prompts, three tool assignments, and a recorded order balanced across
  configurations. Preserve chained stage order. Run serially. Create all 18 case records first.
- Give each worker only its frozen inputs and assigned checkout. Never forward another worker's
  answer or coordinator history. Independent tasks start at the original commit; chained stages
  inherit only the previous stage's complete output tree, including documents, in a new checkout.
- Record actual worker IDs, model/effort, work directories, and input/output tree identifiers.
  Verify the work directory before running a skill. Preserve committed changes, staged/unstaged
  edits, and untracked files not ignored by Git in patches. Keep experiment evidence outside code.
- Keep task-reviewer read-only within the build worker; repairs use the normal developer loop.
  Save findings, final assessment, validation output, and material test gaps. A blocked or missing
  review, failed validation, or incomplete build blocks its chained follow-ups. Failed flow blocks
  chained architecture. Independent cases can continue.
- Keep completed records immutable. Do not automatically relaunch after an interruption: reconcile
  completed and still-running workers first. Each retry needs a new attempt record and usage.
- Record coordinator, setup, and collection work separately. Show supported accounting and actual
  enforceable limits before the user launches. Do not claim the old CLI caps apply to Desktop.

## Native usage evidence

For each attempt, save native usage tied to the worker ID, with its source and measurement scope.
Record input, cache creation, cache reads, output, total tokens, reported USD, and elapsed time
where available. Unknown values are JSON `null` with reasons. Do not have agents estimate their own
usage. A native total is useful even without its breakdown, provided its meaning is recorded.

Never sum cumulative snapshots, add child totals to a parent total that already includes them, or
split shared usage evenly between cases. Include delegated work only when the source establishes
its scope. Keep coordinator/preparation/collection overhead separately identified; otherwise flag
attribution as incomplete. Collection usage may remain partial until the coordinating turn ends.

Desktop's usage ring shows context occupancy and shared plan usage, not per-attempt accounting.
The workflow view exposes per-agent token totals, but setup must verify how the installed version
can export or capture them. Record manual capture if required. Missing USD remains unknown; any
later pricing calculation must be labeled an estimate with its own dated source.
[Desktop usage](https://code.claude.com/docs/en/desktop#check-usage),
[workflow usage](https://code.claude.com/docs/en/workflows#cost).

If collection becomes unavailable after launch, retain partial evidence and stop before another
measured worker starts. Missing accounting cannot establish savings or enforcement of a cost cap.

## Recover evidence from local Desktop transcripts

Check the local transcript store before declaring raw evidence unavailable. In the inspected
Desktop run, native workers saved `agent-<worker-id>.jsonl` under the project's session directory
in `~/.claude/projects/`, even though the Agent tool returned only a final answer and usage summary.
Match exact recorded worker IDs; do not assume another session's files belong to this experiment.

The coordinator or evaluator can run this evidence-only helper. It starts no Claude processes,
makes no model calls, and never writes to trial checkouts, native transcripts, or live results:

```bash
python3 /path/to/toolkit/benchmarks/agent_tools/collect_desktop_evidence.py \
  --experiment /path/to/desktop-experiment \
  --transcripts /path/to/matching/native/session/subagents \
  --output /path/to/desktop-experiment/reports/new-evidence-snapshot/results.json
```

Choose a new output path each time. The helper refuses to overwrite an existing file. It embeds
prompts, reports, patches, verified skill source texts, preparation logs, and changed Markdown
documents read from recorded output trees. Saved native tool calls and results retain the actual
test output and review activity. No tests are rerun to manufacture missing evidence.

The bundle preserves original usage and adds `recovered_request_usage`, deduplicated by request
and message ID across streaming blocks. These request counters include repeated cache reads and
must not be combined with, or substituted silently for, the Agent tool's `subagent_tokens` total.
Regressing, missing, or malformed usage remains unknown. USD costs are not estimated. Observed
model and effort values come from transcript events, separate from the requested settings.

Native workers whose prompts identify a planned checkout but which lack a linked result attempt
are preserved under `unlinked_worker_evidence`. They may be active or discarded; reconcile their
status and usage before final evaluation. Do not silently omit them or add their usage twice.
The collector saves all locally available evidence at that moment; it does not certify runtime
completeness. Later work requires another snapshot. Existing quality verdicts are not changed.

## One portable result

Write `reports/results.json` using the following structure. Populate all 18 planned case records,
including failed, blocked, interrupted, invalid, and not_run cases, with reasons. Completion means
execution finished; it does not establish quality. Keep scores pending for the later evaluation.

```json
{
  "format": "evidence-based-ai-engineering-desktop-experiment",
  "schema_version": 1,
  "execution_surface": "claude-desktop-native",
  "review_status": "pending",
  "plan": {},
  "skill_references": {},
  "workflow_source": "",
  "accounting_capabilities": {},
  "overhead": [],
  "runs": [
    {
      "run_id": "independent-baseline-build-1",
      "repository": "",
      "languages": [],
      "arm": "baseline",
      "stage": "build",
      "mode": "independent",
      "repetition": 1,
      "status": "not_run",
      "attempts": [],
      "quality": null
    }
  ],
  "limitations": []
}
```

Populate `plan` with frozen inputs, order, prompts, versions, model/effort, supported limits, and
accounting coverage. `skill_references` maps installed reference paths to captured skill source
text. Include the saved native workflow source for reproducibility.

Each attempt contains:

- Attempt ID, native worker ID, status, actual model/effort, measurable start/end times,
  input/output trees, and agent-reported task-review status for builds.
- `usage`: available token/cache/cost/time values, evidence source, measurement scope, and explicit
  missing-data reasons. Unknown numeric fields are `null`.
- `files`: artifact names mapped to contents: prompt, answer, review, validation output, patch,
  generated documents, and native usage evidence. Include contents, not only local file paths.
- `transcript_coverage`: complete, partial, or unavailable, with reasons. Include available raw
  evidence; do not invent a transcript or present a worker summary as a full record.

The distinct format separates Desktop and headless measurements. Do not feed this bundle to the
headless `report.py`; bring it back to the experiment-design conversation for evaluation.
Compare quality by stage, language, and mode before efficiency. Missing usage or source evidence
limits the corresponding conclusions; retain those limits in later blog posts.
