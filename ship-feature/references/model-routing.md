# Model Routing

Per-runtime mapping for the capability tiers named in `SKILL.md`. Read this when selecting a model
for a spawn. The tiers in `SKILL.md` are the decision; this file is only the lookup.

Never invent an identifier from this file. Confirm the model is one the runtime actually advertises
before spawning, and prefer an explicit user choice over anything here. These are routing
preferences, not unconditional pins.

## Tiers

| Tier | Meaning |
| --- | --- |
| Strongest capable | Ambiguous architecture, security analysis, migrations, concurrency, cross-cutting reasoning, difficult product decisions, adversarial review |
| General workhorse | Ordinary implementation, integration, tests, repository-aware changes, straightforward shaping |
| Fastest efficient | Clear, repetitive, low-risk execution against a precise spec |

## Runtime mapping

| Tier | Codex (GPT-5.6) | Claude Code |
| --- | --- | --- |
| Strongest capable | `gpt-5.6-sol` | `opus` |
| General workhorse | `gpt-5.6-terra` | `sonnet` |
| Fastest efficient | `gpt-5.6-luna` | `haiku` |

## Reasoning effort

Codex accepts a reasoning effort per spawn: use `high` or `xhigh` for difficult shaping and
adversarial review, `high` for straightforward shaping, `medium` for ordinary implementation.

Claude Code supports `effort` in subagent definitions and session-scoped `--agents` definitions, but
the active invocation surface may expose only `model`. Feature-detect effort support before the
first spawn:

1. Inspect the active Agent tool schema and the selected subagent definition capabilities.
2. If the invocation accepts effort, pass the selected value explicitly.
3. Otherwise, if an already-available session, project, user, or plugin subagent definition exposes
   an appropriate `effort`, use that configured definition and record the applied value. Do not edit
   persistent runtime configuration solely to force an effort level.
4. If neither route exposes effort, record `effort: unavailable`, treat the guidance as advisory,
   and continue. Model selection without effort control is not a blocker.

Do not assume all Claude Code versions or Agent surfaces have the same schema. Prefer the active
runtime's advertised capability over this reference. Current field definitions are documented in
the [Claude Code subagent documentation](https://code.claude.com/docs/en/sub-agents) and
[plugin reference](https://code.claude.com/docs/en/plugins-reference).

## Applied routing

Shaping, chosen before the spec exists:

- Straightforward shaping with a clear code surface → general workhorse
- Ambiguous or high-risk shaping → strongest capable

Implementation, chosen from the completed spec:

- Clear, repetitive, low-risk execution with precise references → fastest efficient
- Ordinary implementation → general workhorse (default)
- Spec still exposes difficult or high-risk reasoning → strongest capable

Do not force a cheaper model when the task exceeds its likely capability. The point of shaping is to
make execution cheap where that is genuinely safe, not to push risk onto a smaller model.

Feature review, chosen after seeing which models implemented the feature:

- Prefer a different capable model from the primary implementation model
- Prefer strongest capable for broad or risky features
- If no different model is available, use the strongest available in a fresh context and disclose
  that model diversity was unavailable

A parent and subagent running the same inherited model are not a different model. Fresh context is
mandatory; a different model is preferred.

## Runtime notes

Explicit model values passed at spawn time override general subagent defaults in both runtimes. Do
not change the user's persistent Codex or Claude Code configuration as part of this skill.

When a runtime is not listed here, map its advertised models onto the three tiers by capability and
cost, state the mapping once before the first spawn, and proceed.
