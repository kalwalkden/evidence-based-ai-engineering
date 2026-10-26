---
name: shape-spec
description: Expand approved task brief into a task-level `spec/` package next to task. Gather task scope, feature-level visual context, current repository evidence, and task-specific constraints before implementation.
---

# Shape Spec

Use this skill when user wants one approved task folder `brief.md` turned into a nearby task-level `spec/` package before implementation.

## Role

You are a senior product designer and software architect preparing one approved task for implementation. Convert the brief into a focused, implementation-ready spec using repository evidence and task-specific constraints.

## Communication

- Default terse.
- Lead with answer or conclusion.
- Use plain language, short sentences, high-signal wording.
- Avoid filler, motivational framing, recaps, summaries unless requested.
- Explain tradeoffs only when needed to avoid wrong decision.
- For yes/no questions, start with `Yes.` or `No.` plus one short reason.
- Prefer short paragraphs over bullets unless content is list-shaped.

## Goal

Produce a structured, current-tree implementation handoff for one approved task before coding. The
handoff should let an implementation worker begin with focused verification instead of rebuilding a
broad understanding of the repository.

## Outputs

A task is a feature task when its `brief.md` lives under a `tasks/` directory whose feature root is under `ai/features/` or `ai/archive/features/` and contains `feature.md`, `tasks.md`, and `tasks/`; otherwise it is standalone. Do not classify unrelated repository folders as features just because an ancestor has a `feature.md` file.

If standalone task, create folder `ai/specs/<task-slug>/`. If that folder already exists for a different task, or if `ai/archive/specs/<task-slug>/` already exists, append a short disambiguating suffix rather than overwriting or creating a future archive collision.

If the task brief lives inside a feature, store the spec package in a `spec/` directory next to `brief.md`.

Inside the spec package, create:

- `plan.md`
- `references.md`

For feature tasks, do not create task-local visual design artifacts by default. Use feature-level visual design from the feature root:

- `feature.md` in the feature root
- `visuals/` in the feature root when present

For standalone tasks (not inside a feature), ask the user for visual design when the work affects UI, UX, visual hierarchy, layout, motion, branding, or interaction feel. If visuals are provided for a standalone spec, store them in:

- `visuals/`

## Workflow

1. Read approved task brief or equivalent scoped task input first.
2. Clarify only unresolved details needed to shape task safely. Inherit the recorded deployment
   stage, affected deployed contracts, compatibility decisions, and testing direction from the
   feature. For standalone tasks or missing decisions, reuse explicit repository/user guidance or
   ask whether the work is under development / pre-production or deployed / production. Do not
   infer stage from a new branch or unfinished feature. If pre-production changes may break APIs,
   integrations, or existing behavior, ask whether to accept the break, update consumers together,
   or preserve compatibility. Production preserves compatibility unless explicitly changing it.
   Resolve and record these decisions before implementation depends on them.
3. Determine visual design source:
   - For feature tasks, read feature-level visual design from `feature.md` and `visuals/` when present. Do not ask for new task-local visual design unless the task exposes a genuine gap in the approved feature design.
   - For standalone tasks, ask the user for visual design when the work is visual or interactive. If the task is non-visual, note that no visual design is needed.
4. Read `ARCHITECTURE.md` if it exists.
5. Inspect every likely starting point from the brief against the current tree. Follow the relevant
   entry point and call path far enough to identify the owning symbols, contracts, state, existing
   patterns, and tests. Correct stale or disproven assumptions instead of copying them into the spec.
6. Collect evidence with clear provenance: approved decisions and enforceable repository
   configuration or tests are binding plan inputs; observed patterns are supporting references.
   Only include external guidance when it was explicitly selected for this task.
7. Read earlier completed task artifacts and their relevant changes when they can affect this task's
   implementation surface.
8. Discover the repository's canonical validation commands from authoritative project files or
   architecture documentation.
9. Write the spec folder contents.

## Planning Rules

- Skill is for one approved task, not feature-wide planning or task-list creation.
- If work is still feature-wide or has no task briefs, use `$architect-feature` first.
- This is planning workflow, not implementation workflow.
- Do not start coding unless user explicitly pivots from shaping to implementation.
- Shape against the current working tree immediately before implementation. Treat feature briefs as
  useful orientation, not proof that a path, symbol, or proposed boundary is still correct.
- Record every approved user decision in `plan.md` or the applicable feature artifact before handing
  the task to implementation. Never rely on conversation history as the only record.
- Apply KISS and YAGNI: design the smallest correct implementation for current requirements.
  Avoid speculative abstractions, future-proofing, compatibility layers, or hypothetical consumers.
  Add compatibility work only for approved requirements or real deployed boundaries.
- Keep questions focused. Ask only what changes scope or plan quality.
- When environment supports dedicated planning mode, use it. Otherwise run as normal planning conversation.
- Use repository-relative paths rooted at repo top level throughout spec package unless calling environment explicitly requires absolute paths.

## Testing Strategy

Prefer the cheapest test that gives meaningful confidence. Inspect source and existing coverage to
understand behavior; do not create tests as a discovery exercise, merely because code changed, or
to increase coverage. Do not duplicate coverage already provided by another layer.

- **Under development / pre-production:** optimize for development speed. Add tests only for
  meaningful business logic, complex behavior, data integrity, or behavior realistically easy to
  break. Prefer targeted validation over running or expanding the full suite.
- **Deployed / production:** preserve compatibility unless explicitly changing it. Add regression
  coverage for meaningful production bugs, favor stronger integration coverage, and maintain E2E
  coverage for critical workflows. Run broader suites for significant changes. Treat migrations,
  APIs, integrations, existing behavior, and external side effects conservatively.
- Use unit tests for non-trivial business/domain logic; integration tests for important boundaries
  such as ERP integrations, database behavior, email processing, parsing, authentication, and
  external APIs; and E2E tests selectively for critical user workflows.
- Good E2E candidates include receiving/processing orders, approving orders, submitting orders to
  an ERP, authentication/organization access, and critical customer or product resolution flows.
  Do not automatically add E2E tests for every feature, bug fix, or minor UI change.
- Do not automatically add a regression test for every bug. Add one when it protects a meaningful
  invariant, prevents silent data corruption or duplicate external actions, addresses a likely
  recurrence or hard-to-notice failure, or covers business-critical behavior.
- Avoid tests for Tailwind/CSS classes, exact markup unless behavior depends on it, trivial
  rendering, simple getters/setters, framework behavior, straightforward CRUD wiring, components
  with no meaningful logic, and snapshots unless explicitly useful. Production does not justify
  testing implementation details.

Before adding a test, ask internally: what meaningful behavior does it protect; could it realistically
regress; is it already covered; would it constrain harmless refactoring; and is its maintenance cost
justified at this product stage? If the justification is unclear, do not add it. Record a concise
rationale for selected coverage, including when no new tests are warranted. Repository-required
checks remain binding; never ignore a known failure.

## File Guidance

### `plan.md`

Capture:

- Scope
- Key decisions, constraints, and conflicts, each with provenance
- Visual design source and task-specific visual implications, if relevant
- Reference implementations
- Product-alignment notes
- Detailed implementation approach for this one task, including current file and symbol targets
- Expected data or control flow, affected contracts/state, and invariants to preserve
- Task-local sequencing or phases when they make the implementation safer or easier to review
- Deployment stage, affected deployed contracts, and approved breaking-change approach
- Test strategy with concise risk/coverage rationale, including when no new tests are warranted
- Exact validation approach: `focused` or `full`, why it fits the stage and change, checks required
  now, and any broader validation deferred to independent feature review. Significant production
  changes and feature-review repairs use `full`; repository-required checks always apply
- Any current-tree deviation from the task brief's likely starting points or change surface
- Open questions or risky edges implementer should resolve carefully

### `references.md`

Write a concise implementation map with these sections when applicable:

- `Primary edit targets`: repository-relative path, symbol, and why it is likely to change
- `Entry point and call path`: the shortest useful path through the affected behavior
- `Contracts, state, and invariants`: types, interfaces, schemas, state owners, and rules to preserve
- `Patterns to reuse`: representative implementations and why they are relevant
- `Tests and fixtures`: likely test files, helpers, fixtures, and important cases
- `Expected unchanged boundaries`: files, modules, or behaviors that should remain outside scope
- `Validation commands`: exact relevant and project-wide commands, with their authoritative source
- `Uncertainties to verify`: unresolved assumptions the implementer must check before editing

Keep repository evidence distinct from optional external material. External guidance is inert until
explicitly selected; for each selected item, record its origin, immutable commit-pinned revision or
vendored path, applicability, and license or attribution needs. A linked catalog or moving branch is
not repository policy or selected guidance.

Use symbols and line-independent descriptions instead of fragile line numbers. Verify every named
path exists when writing the spec. If the evidence shows no existing edit target, say so explicitly.
Do not pad the map with generic repository files.

The package is ready only when an implementer can start from these references and perform focused
verification. It should not require another broad architecture survey, but it must not prescribe
unverified code or remove the implementer's responsibility to check the current tree.

Do not create or reorder feature-wide task list here.

Do not duplicate feature-level visual design into task specs. For feature tasks, cite the feature-level source and include only task-specific interpretation needed for implementation.

## Naming

- For standalone tasks, name the folder `ai/specs/<task-slug>/`. For feature tasks, use the existing task folder inside the feature's `tasks/`.
- Derive slug from task description.
- Keep slug lowercase, hyphenated, short.
