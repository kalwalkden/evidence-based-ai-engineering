# Design Principles

This toolkit is built around a simple premise: AI-assisted engineering becomes more trustworthy
when the work leaves behind evidence that another person or model can inspect. The skills separate
planning, shaping, implementation, and review because each stage answers a different question and
should produce a durable handoff to the next one.

These principles explain why the workflow is structured this way. The individual `SKILL.md` files
remain the authority for exact behavior and operating details.

## Evidence before inference

An agent should inspect the real repository before deciding how it works. Names, common framework
patterns, and previous experience are useful leads, but they are not proof.

The toolkit treats evidence in this order:

1. Approved product, scope, and architecture decisions define what the work is meant to accomplish.
2. Enforceable repository configuration and tests define constraints the implementation must obey.
3. Source code, call sites, Git history, and observed conventions provide supporting evidence.
4. External guidance is optional reference material, not repository policy, unless it is explicitly
   selected for the task.

This is why discovery reads manifests and representative code, shaping verifies likely landmarks
against the current tree, and review examines the actual diff. Static-analysis output and familiar
patterns can direct investigation, but consequential conclusions still need verification.

## Durable artifacts over conversation history

Conversation context is temporary. Repository artifacts survive a closed session, a different
model, a handoff to another engineer, and the passage of time.

Important decisions therefore belong in the repository beside the code they affect. Feature plans
capture scope and tradeoffs. Task briefs define boundaries. Task specs record the current-tree
implementation map and its evidence. Validation and review report what was actually checked.

The artifacts are not administrative residue. They are the interface between stages and the answer
to later questions such as:

- Why was this approach chosen?
- Which alternatives were rejected or deferred?
- What evidence supported the implementation plan?
- What was intentionally left unchanged?
- Which checks ran before the work was considered ready?

The workflow should not depend on a later agent inheriting the original conversation or
reconstructing unstated decisions.

## Separate skills for separate kinds of reasoning

The skills are deliberately narrow. A feature architect, task shaper, implementer, and reviewer do
related work, but they do not have the same objective:

| Stage | Primary question | Durable result |
| --- | --- | --- |
| Discovery | What system already exists? | Repository map and evidence-backed hotspots |
| Feature architecture | What should change, and in what order? | Approved scope, decisions, and task briefs |
| Task shaping | How should this task change the current tree? | Focused implementation plan and references |
| Implementation | What is the smallest correct change? | Code, tests, and validation evidence |
| Review | Does the actual change satisfy its contract safely? | Verified findings or a readiness verdict |
| Archival | How should completed reasoning remain available? | Preserved, recoverable work artifacts |

Keeping these responsibilities separate reduces goal conflict. Planning is not pressured to start
coding early. Implementation does not get to redefine its own scope. Review does not repair the
work it is judging. Each stage can be used independently, while orchestration skills compose them
for one-task or whole-feature delivery.

## Progressive commitment

The workflow adds detail only when that detail becomes useful.

Feature planning identifies scope, sequencing, likely code landmarks, and change boundaries. It
does not freeze a line-by-line edit plan while later tasks or the repository itself may still
change. Immediately before implementation, task shaping verifies those landmarks against the
current tree and produces a code-specific handoff.

This avoids two common failures:

- Planning too vaguely, leaving the implementer to rediscover product and architecture decisions.
- Planning too precisely, producing a brittle specification that is stale by the time its task
  starts.

The feature brief says what must remain true. The task spec says how the next bounded change can
make it true in the repository as it exists now.

## Small changes with explicit boundaries

Task boundaries exist to make changes understandable and attributable, not merely to create a
checklist. A useful task has a coherent outcome, names what is in scope, states what remains
unchanged, and can leave the project in a valid state.

The workflow avoids decompositions that knowingly create broken intermediate commits. If a change
cannot be split without temporarily violating a contract or breaking the test suite, it should land
atomically. Small is valuable only when it remains correct.

This boundary also gives review a meaningful unit. The reviewer can compare one written contract
with one resolved diff instead of guessing which changes belong together in a dirty worktree or a
long-running branch.

## Verification should match the claim

No single check proves that software is correct. The validation performed should be proportional to
the claim being made.

Implementation uses the repository's canonical lint, type-check, and test commands and adds focused
tests where they provide meaningful coverage. Task review checks one implementation against its
specification and exact change set. Feature review examines the cumulative result and its
interactions before the feature is declared ready.

Missing or failed checks remain visible. They are not translated into success because a command was
unavailable or because the implementation looks plausible.

## Implementation does not self-certify

An implementer carries assumptions from the choices it made. Asking the same context to declare its
own work ready provides useful checking, but limited independence.

The toolkit therefore uses two review levels with different costs and purposes:

- Task review is a fast, spec-aware quality pass inside the implementation loop. It catches local
  defects while context is fresh and repair is cheap.
- Feature review is a separate adversarial readiness gate over the assembled change. It runs in a
  fresh context and, when practical, on a different capable model so it is less likely to inherit
  the implementation's blind spots.

Reviewers remain read-only. They report verified findings and, at feature level, a readiness
verdict. The calling workflow owns repair, completion, and archival. This prevents the reviewer from
quietly changing the object it is judging or granting readiness to a different diff.

Independence improves confidence; it does not create proof. A Ready verdict is still a second
opinion, not a guarantee of correctness.

## Model cost follows task risk

The planner-executor split is intended to spend model capability where the uncertainty is highest.
A stronger model can resolve ambiguity, architecture, and risky tradeoffs, then capture that work in
a durable spec. A less expensive capable model may execute a well-specified task when the remaining
work is genuinely straightforward.

This is not a rule that planning is hard and implementation is cheap. If shaping reveals difficult
reasoning, unfamiliar behavior, or high-impact risk, implementation stays on the stronger model.
The saving comes from removing ambiguity before execution, not from assigning risky work to a model
that cannot handle it safely.

Durable handoffs make this routing possible. Without a precise, evidence-backed task package, a new
worker would have to repeat the expensive reasoning or act on an incomplete summary.

This planner-executor approach is influenced by [The Cheapest Way to Cut Your AI Bill Is a More
Expensive Model](https://medium.com/ai-all-in/the-cheapest-way-to-cut-your-ai-bill-is-a-more-expensive-model-250fd7040ff5).

## Parallelize investigation, serialize mutation

Independent, read-only investigation can often happen in parallel. Multiple workers can inspect
different evidence without changing what the others observe.

Write-capable stages share a worktree and therefore remain sequential. Each task shapes against the
result of the tasks before it, implements one bounded change, and validates that new state before
the next task begins. This keeps specifications current and avoids overlapping edits, inconsistent
baselines, and ambiguous ownership of failures.

## Humans decide; agents verify facts

The workflow distinguishes user-owned decisions from discoverable facts.

Agents should resolve repository facts through read-only inspection: which framework is installed,
where a call path leads, which command the project uses, or whether a named symbol still exists.
They should not silently choose product scope, architecture policy, risk tolerance, or among
meaningfully different user experiences.

Feature approval and preflight checks exist to surface those decisions before implementation. Once
the decision record is complete, automation should continue without asking for redundant
confirmation at every mechanical step. Human attention is reserved for choices that materially
change the result.

## Active work and historical evidence are different states

Planning artifacts live under `ai/` so they travel with the repository and remain available to each
stage. Active features and specs are separated from completed artifacts so the next worker can tell
what still requires action without losing the record of earlier decisions.

Archival is explicit, conservative, and reversible. A feature is archived only after its tasks are
complete and the required readiness gate has passed. Grouped features stay with their epic until
the epic is complete, preserving the context in which their sequencing and tradeoffs were chosen.

The archive is a decision trail, not a second source tree. Current code and tests remain the
authority for current behavior.

## Strong defaults, not enforcement

These skills provide an operating model, not a security boundary or CI gate. They can make good
practice repeatable, but they cannot prevent an agent or person from ignoring the instructions.

The workflow intentionally carries overhead: more artifacts, more model calls, and more elapsed
time. That cost is justified for changes where scope, correctness, reviewability, or future
explanation matter. It is unnecessary for every typo or trivial edit.

The design should therefore remain adaptable. Teams can change artifact locations, validation
commands, review policies, and routing choices to fit their environment while preserving the core
ideas: inspect before assuming, record decisions, keep changes bounded, validate real behavior, and
separate implementation from the final readiness judgment.
