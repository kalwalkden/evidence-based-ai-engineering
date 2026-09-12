# Local Codex preflight — 2026-09-11

The native execution and evidence path passed a small local smoke test. No measured feature,
flow, or architecture trial was launched. This checks the mechanism, not the quality of any tool.

## Verified here

- Target: queen-formica, clean commit `f05d03c18ad05d8d85466fd5df5b077b06f8d738`.
- Created a disposable checkout with its own Git directory and no remote; left source unchanged.
- Prepared that checkout's Python tools from its frozen lock file.
- Its own `.venv/bin/reveal` reported **0.127.0**; ast-grep reported **0.45.3**.
  Both help commands worked. Reveal outlined a TypeScript flow implementation and ast-grep
  matched return statements in the same file. This does not establish every optional capability.
- The global Reveal executable reported **0.122.0**. This confirms why each prepared checkout's
  exact invocation must be tested, rather than checking only the machine's global command.
- One native worker launched with no inherited conversation. Its visible tool calls used the
  assigned checkout and confirmed access to all five required installed skills. It performed no
  implementation, review, or skill workflow. Initial native context still pointed at the parent
  directory; explicit command working directories were therefore necessary.
- Exact parent/task metadata resolved the child rollout. The collector recovered its final answer,
  tool call/results, observed `gpt-6-astra` model with high effort, and two response usage records.
  Root session ID and child thread ID differ; attribution correctly uses the child thread ID.
- Setup worker usage: **56,549 input tokens**, of which **46,720 cached**; **746 output tokens**,
  of which **178 reasoning**; **57,295 total**. Cache and reasoning are subdivisions, not extra
  tokens. This is setup overhead, not an experimental result. Billed USD was unavailable.
- All **48 experiment-helper tests** passed on Python 3.13. The **11 new native tests** also passed
  on Python 3.10. Skill validation and installation dry run passed. Python lint/format and scoped
  documentation checks passed after correcting minor spelling flags.

Local detailed evidence is under the ignored `test_output/codex-preflight/` directory. Keep it
local; the branch contains the reusable source, tests, instructions, and this summary.

## Repeat on the destination

Install the repository's skills through its normal setup and prepare the target project's locked
dependencies. Resolve local tool/skill paths; use [codex-tools.example.json](codex-tools.example.json)
as a starting point. Run [Prompt 1](PROMPTS.md) in a Codex task on the target codebase. It explicitly
permits one setup worker and stops before measured trials.

Previously selected queen-formica inputs remain:

- Approved spec: `ai/specs/homepage-pin-gate/`.
- Flow: performance → loyalty → audit → tile reclamation, starting at
  `resolveTileLoyaltyTransition` in `packages/game-core/src/shift/loyalty-transition.ts`.

Confirm the spec is still approved and unimplemented at the destination's frozen revision. Discover
its current line numbers and languages locally. Do not copy the earlier Claude campaign's revision,
paths, model settings, outputs, or worker results into the new plan.

Required project tests, interactive browser verification, full skill execution, chained artifact
handoff with real model changes, and the other machine's native tools/log format have **not** been
certified by this smoke test. The complete experiment remains pending. The setup protocol must
resolve those prerequisites before the first measured trial, and record blockers honestly.
