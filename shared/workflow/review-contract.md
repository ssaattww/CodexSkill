# Review Contract

## Purpose

This file defines review semantics shared by Codex review orchestration and ChatGPT review workers.

Use it together with [Common Work Contract](common-work-contract.md). Runtime adapters own reviewer execution, identity enforcement, report persistence, and handoff transport.

## Review lifecycle

A complete lifecycle has two stages:

1. a normal review cycle containing initial review and any required fix verification,
2. an independent final review of the final current HEAD.

Preserve reviewer continuity during the normal cycle when the runtime supports it. The independent final review must use a different reviewer and a fresh context that did not implement the change or its review fixes.

A final review is invalidated when the target HEAD changes.

## Inputs

Before review, establish:

- review mode,
- repository, PR, base ref, and target HEAD,
- linked Issue, task, requirements, and design,
- complete changed-file set and direct contract dependencies,
- risk profile and planned coverage,
- target-HEAD validation and CI evidence,
- previous findings, reviewed HEAD, and fix evidence when applicable,
- reviewer identity and independence evidence required by the runtime,
- allowed and forbidden writes.

## Review modes

### Initial review

- Define planned coverage before drawing conclusions.
- Inspect every changed file and relevant direct contract dependency.
- Compare behavior with requirements, design, public contracts, failure behavior, and delivery wiring.
- Continue planned coverage after finding a Blocking or High issue.
- Select malformed, partial, stale, duplicate, contradictory, concurrency, identity, boundary, and failure paths according to the actual risk profile.

### Fix verification

- Verify each applicable previous finding by identity and reviewed HEAD.
- Inspect the fix diff, direct impact, affected contracts, and sibling cases of the same defect class.
- Confirm required regression tests or equivalent evidence remain present and strong.
- Classify a defect introduced by the fix as `introduced_by_fix`.
- Do not expand without limit into unrelated areas; record newly noticed unrelated areas as held, out of scope, or unexplored as appropriate.

### Independent final review

- Use a reviewer and context independent from implementation, review-fix implementation, and the normal reviewer.
- Target the final current HEAD once the normal review cycle has completed.
- Read requirements, design, final diff, changed files, direct dependencies, and target-HEAD evidence.
- Perform an independent pass before consulting earlier review conclusions.
- Compare earlier findings only after the independent pass.
- If a required finding causes a fix and the HEAD changes, return to fix verification and run another independent final review against the new HEAD.

A ChatGPT adapter may call this mode `cold final review`; the canonical mode value is `independent_final_review`.

## Required flow

1. Resolve the PR, linked task, requirements, base, target HEAD, changed files, reports, comments, and matching CI evidence.
2. Validate that the selected mode and reviewer identity are allowed by the runtime adapter.
3. Enumerate changed files, dependency boundaries, risk modules, and planned coverage.
4. Inspect all required files and relevant dependent behavior.
5. Compare implementation with requirements, design, contracts, and delivery behavior.
6. Verify that target-project validation and current-HEAD evidence support the claimed result.
7. Record findings in severity order with reproducible locations, impact, and required action.
8. Record checked coverage, held items, out-of-scope items, unexplored areas, unknowns, and verdict impact.
9. Apply the mode-specific stop condition and set the verdict.
10. Produce the review evidence required by the runtime adapter.

## Finding contract

Each finding records:

- stable finding identity,
- severity: `blocking`, `high`, `medium`, or `low`,
- origin: `introduced_by_change`, `introduced_by_fix`, `pre_existing`, `coverage_miss`, `out_of_scope`, or `unknown`,
- concrete location or state transition,
- failure path,
- impact,
- required action,
- evidence.

Findings must describe a concrete defect or unsupported claim, not generic advice.

Do not turn unrelated pre-existing issues into required changes unless they invalidate the changed behavior.

When no findings exist, record explicit no-findings evidence and checked coverage.

## Coverage dispositions

Use these values for required coverage:

- `checked_no_finding`
- `checked_finding`
- `held`
- `not_applicable`
- `unexplored`

Do not omit unexplored or held areas to make the verdict appear stronger.

## Verdicts

- `pass`: no Blocking or High finding remains, all required coverage is dispositioned, no verdict-invalidating unexplored area remains, and required target-HEAD evidence exists.
- `pass_with_held`: all pass conditions hold and only explicitly owned non-blocking concerns remain.
- `fail`: a Blocking or High finding exists, required behavior is missing, or evidence does not support the claimed result.
- `incomplete`: target, requirements, access, scope, reviewer independence, or required evidence is insufficient.
- `unstable`: repeated review rounds reveal different Blocking or High defect classes, undefined invariants, or a scope that will not converge through bounded fixes.

CI success alone is never a review verdict.

## Write boundary

Review must not modify product code, tests, fixtures, workflows, configuration, or implementation documentation.

Review may write only review reports, handoff artifacts allowed by the runtime, and PR review comments. A reviewer must not implement its own findings or merge.

## Required review evidence

Record at least:

- review mode and target HEAD,
- reviewer identity and independence evidence,
- requirements and design references,
- changed and dependent files,
- selected risk profile and coverage dispositions,
- findings or explicit no findings,
- held, out-of-scope, unexplored, unknown, and not-applicable items,
- validation and current-HEAD CI evidence,
- previous finding disposition for fix verification,
- verdict and next action.

## Completion condition

A review round is complete only when the target HEAD and reviewer identity are explicit, mode-required coverage is finished, findings and uncertainty are recorded, the verdict follows this contract, required review evidence is available to the runtime adapter, the write boundary was preserved, and no merge was performed.

The overall review lifecycle is complete only when the normal cycle has converged and a different fresh reviewer has passed an independent final review of the unchanged final current HEAD.