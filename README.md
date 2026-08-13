# Evidence-Based AI Engineering Toolkit

> A practical system of Codex skills for taking software work from discovery to a reviewed, shippable result — with evidence at every handoff.

AI can make a capable engineering team faster. It can also make a team confidently wrong, especially
when the work starts with incomplete context, vague requirements, or an unfamiliar codebase.

The Evidence-Based AI Engineering Toolkit gives AI-assisted software delivery a durable operating
model: inspect the real system, make the decision trail explicit, shape a narrow implementation
plan, validate the result, and review the change independently before calling it done.

## What it is for

This toolkit is for engineers, technical leaders, and Fractional CTOs who want AI agents to
accelerate delivery without replacing engineering judgment. It is designed for real repositories
with existing conventions, incomplete documentation, and work that needs to be explainable after
the chat is over.

```text
Discover the system
        ↓
Shape a feature or task
        ↓
Implement a small, explicit change
        ↓
Validate and review the exact diff
        ↓
Archive the decision trail
```

## The approach: evidence first

Every workflow starts from the repository, not from assumptions. The toolkit favors:

- **Observed architecture** — identify the stack, conventions, dependencies, hotspots, and
  verification commands before proposing changes.
- **Explicit scope** — turn a feature into human-reviewable tasks and task-level specifications
  before code is written.
- **Small, attributable changes** — preserve the user’s existing work and review the precise delta
  created for a task.
- **Validation as evidence** — record the commands run, their results, and the constraints that
  were checked.
- **Independent review** — separate implementation from the final readiness review so a feature
  is not declared ready merely because its author believes it is.
- **Durable artifacts** — retain plans, references, decisions, and completion history alongside the
  work they describe.

## Core workflow

| Stage | Outcome |
| --- | --- |
| **Discover** | A concise architecture report grounded in the current repository, including conventions, hotspots, and canonical validation commands. |
| **Architect** | A feature plan with a visual design, human-reviewable task list, and concise task briefs. |
| **Shape** | A task-level specification that names relevant files, call paths, constraints, tests, and unchanged boundaries. |
| **Develop** | One bounded task implemented against the approved specification, with focused validation and diff-aware review. |
| **Review** | A defect-first task or feature review that verifies what actually changed against the stated intent. |
| **Ship and archive** | A complete feature run with durable timing and validation evidence, then archive the completed planning artifacts. |

## Why this is different

Most agent workflows optimize for producing code. This one optimizes for producing **defensible
engineering outcomes**.

That means an agent should be able to answer:

- What did we observe in the codebase before deciding what to change?
- What is in scope, and what was deliberately left unchanged?
- Which checks passed, and what do those checks prove?
- Was the final result reviewed independently of its implementation?
- Where can the next engineer find the decisions that led here?

Those answers matter when you are working in a mature product, guiding a mixed seniority team, or
communicating technical confidence to a client, board, or future maintainer.

## Designed for humans in the loop

This is not an attempt to automate away technical leadership. It is a set of operating constraints
that makes AI collaboration more useful:

- Humans approve meaningful product and architectural decisions.
- Agents gather evidence, draft artifacts, implement bounded work, and surface uncertainty.
- Review and validation provide a checkpoint before claims of completion.
- The repository remains the source of truth.

## Getting started

1. Review the available skills and choose the smallest workflow that fits the work.
2. Start with architecture discovery when a repository or domain is unfamiliar.
3. Use feature planning for multi-step work; use a standalone specification for a single bounded
   change.
4. Implement against the approved specification, then validate and review the exact change.

Begin with the skills that match your environment and adapt the language, commands, and quality
gates to your team’s engineering practice.

## Intended skill set

The toolkit is organized around a complete delivery loop:

```text
discover-architecture → architect-feature → shape-spec → developer → task-reviewer
                                                    ↓
                                             ship-feature
                                                    ↓
                                        feature-reviewer → archive-work-artifact
```

Each skill has a narrow responsibility. That separation is intentional: discovery should not be
silently treated as design, implementation should not self-certify final readiness, and completed
artifacts should not disappear when the conversation ends.

## Principles

1. **Inspect before inference.** Prefer repository evidence over generic conventions or model memory.
2. **Make decisions reviewable.** Capture material choices where the next person can find them.
3. **Keep work narrow.** A small, verified change is usually more valuable than a broad, impressive-looking one.
4. **Separate creation from verification.** Independent review catches the blind spots of an implementation pass.
5. **Preserve attribution.** Do not blur agent work with unrelated local changes.
6. **Earn confidence.** “Done” means the agreed evidence exists — not simply that code was generated.

## Who it helps

- Engineering leaders establishing a practical AI-assisted delivery practice
- Fractional CTOs who need repeatable, transparent technical execution across clients
- Product teams working in inherited or lightly documented codebases
- Senior engineers who want agents to reduce setup and research work without lowering standards
- Teams that want a useful audit trail without introducing heavyweight process

## Status

This is an evolving open-source toolkit. The workflows are intentionally opinionated, but they are
meant to be adapted: use the parts that improve your team’s clarity and delivery confidence, then
contribute what you learn.

## Contributing

Contributions that improve evidence quality, clarity, safety, validation, and developer experience
are welcome. Please keep additions focused, explain the problem they solve, and preserve the core
idea: AI assistance should make engineering work more understandable and trustworthy.

---

Built for teams that want to move quickly **and** be able to explain why they trust what shipped.
