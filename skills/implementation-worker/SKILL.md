---
name: implementation-worker
description: Perform initial implementation or review follow-up from a resolved work context without depending on a Codex parent or ChatGPT chat runtime.
---

# Implementation Worker

## Goal

Implement one accepted scope and return implementation evidence to the caller.

## Required input

Use the output of `work-context-manager`. Do not infer runtime permissions, persistence, delegation, or merge authority.

Required context includes scope, non-goals, requirements, target identity,
`verification_capability`, write boundary, development policy, validation
targets, and applicable findings.

## Modes

### Initial implementation

- Read the task, design, relevant code, tests, configuration, and validation wiring before editing.
- Implement the smallest coherent change satisfying the accepted scope.
- Follow the target project's required implementation and testing order.
- Do not add unrelated improvements.

### Review follow-up

- Resolve findings by identity and reviewed HEAD.
- Inspect the direct cause, affected contracts, fix boundary, and sibling cases of the same defect class.
- Preserve existing regression evidence.
- Do not use review follow-up for unrelated cleanup.

## Required flow

1. Validate that the supplied work context is sufficient and current.
2. Read target files, direct dependencies, tests, configuration, and CI entry points.
3. Confirm required failure diagnostics can be preserved.
4. Apply the smallest coherent change.
5. Keep code, tests, documentation, configuration, and workflows aligned with the requirement.
6. Run focused validation for the inner loop. Record broader validation separately from the repository-defined full local equivalence gate; the latter is executed once for the final publication candidate HEAD after normal convergence, unless a content delta invalidates that exact-HEAD evidence.
7. Preserve or inspect logs, test results, standard output, standard error, and artifacts for failures.
8. Return changed files, intentionally untouched areas, commands, results, commits, final HEAD, matching CI evidence, unknowns, and risks.

Keep validation, review-target commit, push, and CI evidence or wait state
separate. Record the evidence supplied by the caller, but do not define or
perform runtime-specific push or CI-wait routing in this runtime-neutral Skill.

## Testing policy

The target repository determines whether work is TDD, test-after, validation-only, or another method. Do not manufacture Red/Green evidence. CodexSkill repository maintenance is non-TDD unless the user explicitly changes that policy.

## Boundaries

- Stay inside the supplied write boundary.
- Do not issue an independent review verdict for your own changes.
- Do not perform runtime-specific report persistence or handoff transport.
- Do not merge.

## Output contract

Return:

- mode,
- accepted scope and non-goals,
- requirements and design references,
- changed files and purpose,
- intentionally untouched areas,
- validation commands and results,
- failure diagnostics and artifacts,
- verification capability and validation evidence,
- review-target commit identity or explicit pending state,
- push state and matching CI evidence or explicit absence,
- final technical HEAD SHA and administrative parent when applicable,
- blocked items, unknowns, and remaining risks,
- next required action.

## Completion condition

Complete when the accepted scope is implemented or explicitly blocked, validation is recorded accurately, final HEAD is explicit, implementation evidence is complete, no independent review verdict was issued, and no merge was performed.
