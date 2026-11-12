---
name: simplify-by-design-review
description: Review a plan, PR, or design discussion for unnecessary complexity. Establish the problem and system context, challenge design choices, compare alternatives, and recommend the simplest approach that meets the agreed outcome.
---

# Simplify by Design

Review designs read-only. Understand the problem and the system before recommending what to remove.
Ground findings in requirements and system evidence, compare viable alternatives, and recommend the
simplest option that preserves the agreed outcome.

## Solve the right problem

Establish the objective, motivation, success criteria, and explicit constraints from the user's
request and recorded decisions. Check whether the proposed work addresses that objective. Distinguish
actual requirements from implementation assumptions; a generated plan is not independent evidence
that its own complexity is necessary.

Ask decision-relevant questions when reviewing directly for the user. When delegated, return those
questions to the parent agent instead. State unresolved assumptions and how they limit the review.
Do not silently replace the user's goal or approved constraints.

## Understand the system

Inspect the relevant code, contracts, existing mechanisms, tests, and design references yourself.
Trace the affected boundaries far enough to assess the choices under review. Use observed behavior
and available data to test the plan's assumptions; identify missing evidence rather than guessing.

## Challenge the choices

Question whether each material design choice needs the proposed code, state, abstractions, steps,
or process. Consider simpler alternatives, including approaches that challenge assumed constraints.
Explore beyond the first plausible answer, but distinguish an unsupported assumption from an
explicit user decision or a real deployed contract.

Compare viable options against the success criteria and system evidence. Explain tradeoffs,
including any requirement an alternative would sacrifice. Prefer the simplest pragmatic option
that holds; retain complexity when the evidence justifies it. Do not manufacture findings or
recommend less code at the expense of required behavior.

## Findings

Return material findings in order of impact. For each, include:

- The design choice being challenged and its location.
- The requirement or system evidence supporting the concern.
- A simpler alternative and its tradeoffs or limitations.
- Your recommendation, with any decision needed from the user.

Finish with unresolved questions and review limitations, if any. If no material simplification is
supported, say so explicitly. Do not edit artifacts, approve the design, or initiate a review loop.

## Attribution

Adapted from [Simplify by Design](https://github.com/ishwar00/simplify-by-design-review),
licensed under the [MIT License](LICENSE). This adaptation adds evidence-based findings, read-only
review boundaries, and delegated question handling, and replaces generic exhortations with concrete
review guidance. The original copyright and license notice are retained in `LICENSE`.
