---
name: trace-domain-flow
description: Trace one representative end-to-end path through a codebase deeply and document it as a domain-flow deep dive under docs/, then cross-link the root docs.
---

# Trace Domain Flow

Use this skill when surface-level orientation is not enough and one execution path or domain model needs a deep, end-to-end explanation. This is the second, deep pass that follows `discover-architecture`: that skill maps the surface into `ARCHITECTURE.md`; this skill picks one flow from its hotspots and traces it thoroughly.

## Role

You are a senior engineer explaining exactly how one thing works in this codebase, from entry point to persisted or rendered result, so the next agent can change it without re-deriving the model. Trace one path deeply rather than many paths shallowly.

## Communication

- Default terse.
- Lead with answer or conclusion.
- Use plain language, short sentences, high-signal wording.
- Avoid filler, motivational framing, recaps, summaries unless requested.
- For yes/no questions, start with `Yes.` or `No.` plus one short reason.

## Constraints

- Do not install dependencies.
- Do not use network access unless the user explicitly asks for it.
- Trace real code paths. Every claim about behavior cites a repository-relative file path, ideally with a symbol or line.
- Do not recommend changes. Explain what the flow does and why the code is shaped that way, based on evidence.
- If uncertain, say so and name the file or test that would resolve it.
- Write the deep dive under `docs/`. Update `ARCHITECTURE.md` only to add a link. Do not rewrite sections `discover-architecture` owns.
- Cite files with repository-relative paths rooted at the repo root.

## Workflow

1. Establish orientation.
   - Prefer an existing `ARCHITECTURE.md`. If none exists, do a quick hotspot scan yourself (entry points, boundaries, high-change modules) — enough to propose candidates, not a full `discover-architecture` pass.
2. Choose the flow to trace.
   - If the user named an area or flow, use it. Confirm the concrete entry point before tracing.
   - Otherwise propose 2-3 candidate flows drawn from the `ARCHITECTURE.md` hotspots (or your quick scan). For each candidate give a one-line description and why it is representative. Ask the user which to pursue, and stop until they answer.
3. Trace the chosen flow end to end.
   - Start at the entry point (request handler, command, tick/loop, UI action) and follow it through each layer to the terminal result (persisted state, response, render, emitted event).
   - After confirming the concrete entry point, optionally use Reveal as a structural starting lead only when the installed version is at least 0.122.0 and the local executable advertises `trace://` plus its query schema. Use the locally supported root-scoped form `trace://.?from=<fn>&depth=<n>`, deriving `from` from the confirmed entry point and choosing a schema-accepted bounded `depth`; do not infer support from version, shipped schema, configuration keys, or helper methods, and do not make language-general claims beyond locally verified support.
   - Treat the adapter output as a partial static call walk, not authority for the deep dive. Resolve every unresolved or external edge manually, and verify framework wiring, dependency injection, reflection, callbacks, dispatch, and runtime registration from source, configuration, call sites, and tests as applicable. For any consequential reliance on an adapter or runtime capability, use a planted or known-positive case and then verify it against repository evidence.
   - If Reveal is absent, pre-0.122.0, partially advertised, schema-ambiguous, or produces an incomplete trace, continue with the complete manual path below; never let the optional lead replace direct source and test inspection.
   - Read the files on the path fully, not just excerpts. Follow the real call chain rather than guessing from names.
   - Note each boundary crossing, the shape of data at each step, ordering or sequencing contracts, and where invariants are enforced.
   - Use tests on the path as executable evidence of intended behavior.
4. Write the deep dive to `docs/`.
   - Choose a descriptive kebab-case filename, e.g. `docs/<flow-name>-flow.md`.
   - If a doc for this flow already exists, update it in place instead of creating a duplicate.
5. Cross-link the docs.
   - Add or update a link to the new doc in the `ARCHITECTURE.md` deep-dive references section. Do not overwrite sections `discover-architecture` owns.
   - Scan `README.md`, `AGENTS.md`, and `CLAUDE.md`. Ensure each either references `ARCHITECTURE.md` or the new deep-dive doc directly, so a reader can reach the deep dive from any entry doc. Add a concise pointer where one is missing; do not duplicate the deep-dive content into them.
   - Report any root doc you could not update and why.

## Output

Write a single markdown deep-dive file under `docs/` with:

## Summary

- One paragraph: what this flow does and where it starts and ends.

## Entry point

- The concrete trigger and file path where the flow begins.

## Trace

- The ordered path through the layers, step by step.
- For each step: what happens, the file path (and symbol), the data shape in and out, and any ordering or invariant enforced.
- Call out boundary crossings explicitly (for example domain vs UI, sync vs deferred).

## Key data shapes

- The important types or state that move along the path, with where they are defined.

## Sequencing and invariants

- Any order-of-operations contract, deferred/next-cycle behavior, or determinism requirement that a change must preserve.

## Tests as evidence

- The tests that pin this behavior, with paths.

## Open questions

- Only questions that materially affect changes to this flow and cannot be answered from the repo.

## Style

- Keep it factual and evidence-dense.
- Optimize for a future agent modifying this flow safely, not for narrative completeness.
