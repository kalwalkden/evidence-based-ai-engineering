# Complexity must earn its place

## Scope and provenance

Shape one standalone task from the user's explicit request: add a concrete complexity decision
rule to `architect-feature`, `shape-spec`, and `developer`, and a necessity check to
`feature-reviewer`. This package is a planning handoff; skill edits are not implemented here.

The user identified the failure: a conceivable lost Google response became an automatic recovery
requirement, then the generated spec was treated as justification for that complexity. The main
correction belongs in planning and shaping. More implementation testing would not prevent it.

The existing KISS/YAGNI guidance supports the change. The requested text is the scope authority;
this generated plan supplies placement and validation guidance, not new product requirements.

This is non-visual skill instruction maintenance; no visual design is needed. Earlier archived
task 001 of `toolkit-simplicity-and-validation` records the toolkit as under development and permits
workflow changes. This task adds an explicitly requested decision rule without changing deployed
APIs, installer behavior, file formats, or compatibility mechanisms.

## Requested wording

Add the following text to each of the three planning/implementation skills, preserving its wording
(Markdown heading and line wrapping may follow local style):

> Complexity must earn its place.
>
> Implement the requested workflow using the simplest existing mechanisms.
>
> Do not introduce persistent state, ownership markers, recovery protocols, speculative abstractions, or additional reasons to refuse an operation merely because a failure is conceivable.
>
> Add such machinery only when an explicit requirement or demonstrated current problem makes the simpler approach insufficient. Otherwise, report the failure clearly and allow ordinary manual correction.
>
> Do not turn implementation assumptions into user requirements by recording them in a plan or spec. A generated spec is not independent evidence that added complexity is necessary.
>
> Apply this internally; do not introduce extra approval rounds or justification documents.

Add the following text to `feature-reviewer`:

> Review necessity as well as correctness. Flag unrequested persistent state, blocking prerequisites, and recovery machinery even when they faithfully implement the generated spec.

## Implementation approach

1. Recheck the four current skill files against `references.md`.
2. Add the common rule as a prominent section adjacent to `architect-feature`'s Priorities,
   `shape-spec`'s Planning Rules, and `developer`'s Core Rules. Keep the existing KISS/YAGNI guidance
   and stage responsibilities; this rule makes their application concrete.
3. Add the reviewer wording in Review the Assembled Feature, where the assembled feature checks
   live. It must apply even when implementation matches the generated spec.
4. Read the resulting instructions together. The spec remains the implementation handoff, but
   its existence cannot independently establish that added complexity is necessary. Make only
   narrowly necessary wording adjustments if existing instructions would contradict that rule.

Acceptance: all three skills carry the full common rule, and feature-reviewer carries the full
necessity check. Planning and shaping must reject invented requirements before they become a
handoff. Implementation and review provide further checks without adding process ceremony.

No new state, artifacts required of skill consumers, approval rounds, justification documents,
testing policy, or automated tests are part of the change. Do not retrofit the unrelated Google
workflow or change orchestration, manifests, installer behavior, archived plans, or other skills.

## Validation needs

The affected behavior is prose interpreted by agents. Existing structural validation checks skill
frontmatter, manifests, and membership; it cannot prove that agents follow the necessity rule.
Use direct inspection of the four-file diff to verify wording, placement, scope, and consistency.
As a review scenario, a conceivable lost response alone must not justify automatic recovery;
an explicit requirement or demonstrated current problem may justify it when simpler mechanisms
are insufficient. This is an internal check, not a new required artifact or approval gate.

No new automated tests are warranted for this instruction-only change. Preserve repository-required
checks from `AGENTS.md` and `scripts/check.sh`:

```bash
scripts/check.sh lint prose
scripts/check.sh validate test
git diff --check
```

No validation mode was selected by the user. Focused validation is appropriate to the small prose
change, with the canonical repository checks above still binding. No independent feature review
or deferred feature checks apply to this standalone task. Report unavailable tools or failed checks
accurately. There is no configured static type checker.

## Open questions

None.

## Implementation record — 2026-10-30

Complete. Added the full common rule beside the existing simplicity guidance in architect-feature,
shape-spec, and developer, and the necessity check in feature-reviewer. Heading punctuation follows
repository lint rules. Added `unrequested` to `cspell.json` after the spelling check flagged the
user's requested wording; no other configuration changes were needed.

Validation mode: focused, with all repository-required canonical checks completed. No new tests:
these are instruction changes, and wording-matching tests would not establish behavioral quality.

- `scripts/check.sh lint prose validate test`: initial run exited 1; lint and structural validation
  passed, while prose checks identified heading punctuation and a missing dictionary word, and
  Python 3.10–3.12 were unavailable. Corrected the prose issues and installed temporary interpreters.
- `scripts/check.sh prose test`: exit 0 after corrections; prose checks and the existing test suite
  passed on Python 3.10, 3.11, 3.12, and 3.13. Earlier lint/validate results remain applicable.
- Skill-creator's `quick_validate.py`: exit 0 for each of the four changed skills.
- Exact task tree diff whitespace check: exit 0.

The initial sandbox-only attempt could not fetch tools or write their default cache. Successful
checks used network-enabled execution with caches, tools, and downloaded interpreters under `/tmp`.
No full-suite checks were deferred. Static checks cannot prove that agents follow the new rule.

Task review: Pass. No findings; zero blocking and zero advisory findings. The current-context,
read-only task-reviewer pass inspected the complete tree-to-tree delta from the pre-implementation
baseline: four skill files and the necessary dictionary entry. Earlier untracked files were outside
that delta. The user wording and all scope constraints are satisfied; generated specs remain
handoffs without independently justifying complexity. No new approval or justification steps were
introduced. Implementation, validation, and review are complete; archive this standalone package.
