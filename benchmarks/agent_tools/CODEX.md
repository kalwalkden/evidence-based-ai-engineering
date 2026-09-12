# Native Codex experiment protocol

This is a coordinator-driven experiment for this repository's installed skills, not a model runner.
Use the actual native subagent tools exposed in the session. Python helpers only check local state
and collect evidence. Never substitute external model processes if native capabilities are absent.

## Freeze inputs and preflight

1. Discover the target repository root, clean current commit, implementation languages, approved
   spec, and concrete flow. Require all task inputs to exist in that commit. Read the spec to
   identify normal automated tests and other prerequisites. Interactive browser verification is
   excluded from this experiment by the user's instruction below; do not preflight browser access.
   Do not invent acceptance scripts or silently waive other required validation. Resolve required
   toolchain checks and existing user-approved waivers before reporting setup blockers.
2. Resolve installed skill files and supporting resources. Save their content and hashes for
   evidence, but workers must use the installed originals. Do not replace or edit skills. Keep
   the same versions for every arm. Follow the spec's normal developer/review/archival workflow.
3. Create a NEW campaign directory outside the target source checkout. Freeze task text, tool
   assignments, validation policy, skills, source commit, run order, and session model/effort policy
   in `plan.json`. Include the applicable validation policy in every fresh worker's prompt.
   Discover paths locally; never copy machine-specific paths from old results. Preserve previous
   campaigns. Do not import Claude attempts into the Codex campaign.
4. Inspect project tool locks and installed versions. Write `tools.json` containing exactly
   `reveal` and `ast-grep`, each with an `argv` array and an exact `version` string. For example:

   ```json
   {
     "reveal": {"argv": [".venv/bin/reveal"], "version": "0.127.0"},
     "ast-grep": {"argv": ["ast-grep"], "version": "0.45.3"}
   }
   ```

   These are the locally verified versions, not universal latest-version recommendations. Prefer
   the project's locked Reveal version. If using a launcher such as uv, include its full prefix
   in `argv` and verify that exact invocation. The assigned command overrides conflicting tool
   invocation guidance in repository instructions and skills for this experiment only. A matching
   global binary does not prove a project launcher uses that version.
5. Run `codex_native.py preflight --repo TARGET --tools TOOLS_JSON --output NEW_PREFLIGHT_JSON`.
   Optionally supply `--skills-dir`. The helper is read-only apart from writing the new report;
   supplied tool commands must themselves be read-only. It checks clean Git inputs, installed
   skill fingerprints, and exact version/help commands. It does not install dependencies or
   establish task readiness. Missing versions/skills and mismatched commands are blockers.
6. Create a throwaway checkout at the frozen commit with a separate Git directory, no remote,
   and hooks disabled. Ordinary Git operations or `harness.checkout` may prepare it; never invoke
   `harness.py run`. Prepare dependencies from the project's lock files inside that checkout.
   Do not share writable dependency directories between trials. Record preparation commands and
   any resulting tracked changes; unexplained source changes block launch.
7. Run one small native smoke worker before any measured trials. In this environment use
   `collaboration.spawn_agent` with `fork_turns="none"`, a unique task name, and no model/effort
   overrides. Give only its assignment, checkout, and installed skill paths. Ask it to read its
   Git identity and skill frontmatter, and report access without implementing the feature.
   Verify its visible tool calls used the assigned checkout. Record its usage as setup overhead.
8. Locate and collect the smoke worker's saved evidence as below. Check its final answer and
   completion against the collected messages. Verify observed model/effort and per-response
   usage. Stop if fresh contexts, checkout access, installed skills, exact tool routing, or
   accounting cannot be established. A fresh worker still receives platform instructions and
   skill listings; it does not start with zero input tokens. Recheck on the destination machine.

## Required toolchain checks and validation waivers

**Interactive browser verification is excluded by default for all arms and stages.** The user
explicitly directed: "We don't need the browser test." Record this in
`plan.validation_policy.waivers` with ID `interactive-browser-verification`, status `waived`,
scope `all arms and stages`, and this protocol section as the approval source. Do not launch a
browser verification session, require browser tooling, ask for this waiver again, or block a
worker, review, archival handoff, or chained stage because interactive verification was not run.
Pass this experiment override to developer and task-reviewer, even when the original spec or
skill calls for an interactive check. Keep normal automated tests, lint/type checks, builds, and
review. Report the omitted interactive coverage honestly. The user can explicitly opt it back
into a later campaign; otherwise this default continues to apply.

The arm assignment controls **code inspection**. It does not prohibit a tool's narrowly scoped,
required toolchain checks. In every arm, allow version/help checks and checks explicitly required
by the frozen spec to verify installation or toolchain operation. This protocol authorizes that
exception: record it during preflight and continue without asking for approval again. A general
repository preference to explore code with Reveal is not a required toolchain check.

Before launch, freeze `plan.validation_policy.toolchain_checks`. Each entry must include a stable
ID, the exact command argument array, checkout-relative working directory, the requirement's
source path and text, purpose, applicable stages, and expected output. Apply the same checks to
all arms at the same stage, using the pinned tool versions. Record whether each check runs during
coordinator preparation or inside the worker. Keep coordinator preparation as overhead; checks
inside a measured worker remain in its usage. Never subtract guessed per-command token costs.

This exception is not permission to explore source with an otherwise prohibited tool. Outlines,
symbol searches, call graphs, architecture discovery, and code-review findings remain inspection,
even when a command is called a validation check. Inspect wrappers and scripts as necessary to
classify what they actually do. Do not widen an allowed command with extra targets or flags.
If a mandatory check necessarily exposes code-inspection results to a prohibited arm, record the
specific conflict and seek a concrete protocol decision before measured work. Do not hide that
exposure, automatically waive the check, or label an inspection command as toolchain validation.

Record every allowed invocation in the attempt's `toolchain_check_results`, with its policy ID,
actual command, exit status, and output evidence. Audit tool-policy compliance against this frozen
list, not a blanket search for the word Reveal. Allowed toolchain checks do not contaminate an
inspection comparison; use outside their documented scope does. Describe the baseline accurately
as ordinary inspection with the same required toolchain validation as the other arms.

Preserve explicit user-approved waivers in `plan.validation_policy.waivers`, each with the exact
requirement, applicable stages/arms, reason, and approval text/source. An existing approval for
this campaign is sufficient; do not ask again in each worker or review. Beyond the explicit browser
exclusion above, do not infer waivers from missing access or copy an unrelated campaign's waiver. Apply
the same validation conditions to comparable arms and pass them to task-reviewer as experiment
overrides without editing the installed skill or original spec.

A waived check has status `waived`, never `passed`. If all remaining required validation and
review pass, the coordinator may advance the chain under the recorded waiver, while retaining
that limitation in the result and handoff. It must not claim full original-spec validation.
A waiver of browser verification does not waive automated tests, review findings, or other checks.
Preserve any earlier failures even if a later approval waives rerunning a check; an observed product
defect remains a finding. If policy changes after measured work starts, keep the original policy
with each attempt and separate differently governed results during evaluation.

## Prepare and run the 18 cases

Use baseline, Reveal, and ast-grep across build, flow, and architecture in independent and chained
modes, once each. Save a reproducible shuffled arm/block order and seed; keep chain stages ordered.
Record all 18 cases before starting. One repetition is exploratory, not a statistical verdict.

Tool assignments apply throughout implementation, documentation, handoffs, and review:

| Arm | Available code-inspection tools |
| --- | --- |
| Baseline | Ordinary file reading and search |
| Reveal | Reveal plus ordinary file reading and search |
| ast-grep | ast-grep plus ordinary file reading and search |

Workers should use their assigned inspection tool where useful throughout the skill workflow.
Reveal is allowed in Reveal runs; ast-grep is allowed in ast-grep runs. Preserve local capability
checks, source verification, and fallbacks. Only cross-arm inspection is restricted: the baseline
does not inspect code with either tool, and each tool arm does not inspect code with the other.
All arms retain the required-toolchain-check exception above. Do not turn these comparison
boundaries into a blanket tool ban or ask whether a worker may use its assigned tool.

Each measured stage uses a new native worker with `fork_turns="none"`; never resume a previous
worker. Run serially. Inherit one unchanged coordinator model/effort configuration and record
observed values from every worker; an unexpected change blocks further comparable trials.
Keep task-reviewer inside the build worker with its normal read-only review and developer repair
loop. Do not spawn extra reviewers or nested model workers for this experiment.

Native workers share the host filesystem and may inherit the coordinator's initial working
directory. Separate contexts/checkouts are NOT operating-system sandboxes. Every worker prompt
must give its explicit checkout and require that working directory for commands, development servers,
and tests. Allow reading installed skills, supporting references, and ordinary tool dependencies;
allow writing only its checkout and assigned output directory. Forbid reading the original source,
other trial outputs, or evaluator materials. Audit tool evidence for violations; mark contaminated
attempts ineligible instead of claiming enforcement that the runtime does not provide.

Independent tasks start from the same frozen commit in separate checkouts. Chained build starts
there too; flow and architecture each start in a new checkout from the predecessor's captured
output tree, including normal generated documents and archived artifacts. No conversation or
answers carry forward. Capture each worker's entire diff against its recorded input commit,
including staged/untracked files and agent-created commits; `harness.snapshot` supports this.
Commit captured code/documents in the isolated checkout to provide the next stage's input. Verify
that its tree matches the captured output tree. Do not carry dependency caches or result bundles.

Before starting a worker, re-run exact version/help checks inside its PREPARED checkout and verify
skill hashes, task inputs, and source tree. In particular, `.venv/bin/reveal` must be that checkout's
prepared executable. An original repository's virtual environment is not a portable trial setup.

After each worker, save the final answer, full change patch, skill documents, normal automated test
results, review report, and local worker evidence. The coordinator must inspect actual validation
and review results against the frozen validation policy: any unresolved finding, required
check not performed or failed without an applicable waiver, or explicit unresolved blocker
overrides a `passed` marker. Record
approved waivers separately; they permit only their documented exceptions. A completed model turn
is not task success. Record
review and validation separately. Block remaining chained stages after a blocked/failed predecessor.
Use task-reviewer instead of adding custom acceptance scripts. Leave later comparative quality
scores pending. Never silently retry; every retry has a separate ID and full usage.

## Recover native worker evidence

When the native tool returns a task name rather than a UUID, resolve the exact saved child from
its parent thread ID and canonical task path. The local parent ID is available as `CODEX_THREAD_ID`.
The sessions root defaults to `CODEX_HOME/sessions`, or `~/.codex/sessions` when unset:

```text
python3 codex_native.py locate --parent-id PARENT_UUID --agent-path /root/UNIQUE_TASK
python3 codex_native.py collect --rollout EXACT_FILE --worker-id WORKER_UUID --output NEW_FILE
```

Use the returned worker ID and rollout together. Do not guess by newest filename or combine all
children of a parent. On another runtime, inspect actual tools and metadata; do not invent fields.
`locate` rejects ambiguous matches. `collect` never overwrites files. Collect after completion;
if disk flushing lags, retry collection into a new file without rerunning the worker.

The collector sums `token_usage_record.payload.usage` once per response ID for the exact worker
thread. Native child token records may retain the ROOT `session_id`; their `thread_id` identifies
the worker. Do not add cumulative turn/thread totals. Cached input is a subset of input; reasoning
output is a subset of output. Preserve both subdivisions, but do not add them a second time.
Missing, malformed, foreign, or conflicting records leave trustworthy totals unknown, with reasons.
The collector exports text messages, tool calls/results, and observed model/effort; it excludes
internal reasoning, system/developer messages, session instructions, and image/audio bytes.
This is filtered evidence, not a full raw transcript or a guaranteed complete execution trace.
Match the final answer and tool returns against native completion before marking coverage complete.

Store `reported_cost_usd: null` unless verified per-worker billed cost is exposed. Subscription
limits and plan charges cannot be divided into measured task costs. No automatic dollar cap is
enforced by this protocol. If publishing estimated API-equivalent costs later, label them as
estimates, cite dated rates, and keep them separate from measured usage and actual charges.

## Portable results contract

The coordinator assembles `reports/results.json` with format
`evidence-based-ai-engineering-codex-experiment`, schema version 1, and these fields:

- `plan`: frozen commit/languages, task text/hashes, exact tool commands/versions, installed skill
  contents/hashes, seeded order, model/effort policy, preparation and preflight reports. Include
  `validation_policy` with scoped `toolchain_checks` and explicit user-approved `waivers`.
- `runs`: every planned case, its ID, arm, mode, stage, status, and `quality: null`.
- Each run's `attempts`: unique attempt/native worker IDs, input/output commits and trees, frozen
  prompt, final answer, start/end times, patch and changed documents inline, review findings,
  normal validation evidence, `toolchain_check_results`, checks with status `waived` and their
  approval references, unresolved blockers, and separate workflow/tool-policy verdicts. Include
  the exact validation policy used by the attempt, even if the campaign policy later changes.
  Embed the collector result under `worker_evidence`, with missing-data and coverage reasons.
- `overhead`: setup smoke evidence and separately identifiable coordinator/preparation/collection
  work. If coordinator token boundaries are unavailable, say so; do not charge them to a worker.
- `limitations`: missing cost/usage/visual evidence, policy violations, unavailable checks, and
  comparison constraints. Failed attempts keep their usage; blocked/not-run cases remain present.

File paths alone are insufficient: embed readable review/test/document/prompt/patch evidence and
skill references so the bundle can be evaluated on another machine. Reference hashes preserve
provenance. Preserve source logs locally; do not check them into the branch or publish private
project data without review. The new Codex format is not input to the historical Claude report
parser. Evaluate quality first using these artifacts, then compare efficiency within each skill,
language, and execution mode; distinguish independent evidence from effects of earlier chain work.
Evaluate allowed toolchain checks against their recorded scope before flagging prohibited tool use.
Waived validation is an evidence limitation, not proof of correctness or an automatic policy failure.
Keep comparisons with materially different validation policies separate and disclose waivers in
recommendations and blog claims.
