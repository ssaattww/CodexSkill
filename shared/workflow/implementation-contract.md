# Implementation Contract

## Purpose

This file defines implementation semantics shared by Codex implementation executors and ChatGPT implementation workers.

Use it together with [Common Work Contract](common-work-contract.md). Runtime adapters own execution placement, delegation, repository tooling, report persistence, and handoff transport.

## Inputs

Before implementation, establish:

- accepted scope and non-goals,
- authoritative requirements and design,
- target repository, branch, base ref, and current HEAD,
- target files and direct contract dependencies,
- target-project development and testing policy,
- validation targets and required failure diagnostics,
- allowed and forbidden writes,
- applicable previous findings for review follow-up.

## Modes

### Initial implementation

- Read the task, design, relevant code, tests, configuration, and validation wiring before editing.
- Implement the smallest coherent change that satisfies the accepted scope.
- Follow the target project's required implementation and testing order.
- Do not redesign the whole task or add unrelated improvements.

### Review follow-up

- Resolve the applicable findings by finding identity and reviewed HEAD.
- Inspect the fix boundary, direct causes, affected contracts, and sibling cases of the same defect class.
- Preserve existing regression evidence and strengthen it only when required by the finding or target-project policy.
- Do not use review follow-up as permission for unrelated cleanup.

## Required flow

1. Confirm scope, non-goals, requirements, write boundary, branch, and current HEAD.
2. Read target files, direct dependencies, tests, validation wiring, and relevant CI entry points.
3. Confirm that required failure diagnostics can be preserved before running applicable validation.
4. Apply the smallest coherent implementation for the selected mode.
5. Keep code, tests, documentation, configuration, and workflow changes aligned with the accepted requirement.
6. Run focused validation, then relevant broader validation required by the target project.
7. For failures, preserve or inspect the required logs, test results, standard output, standard error, and artifacts.
8. Record changed files, intentionally untouched areas, commands, results, commits, final HEAD, matching CI evidence, unknowns, and remaining risks.
9. Produce the implementation evidence required by the runtime adapter.

## Testing and validation rules

- The target project owns whether implementation is TDD, test-after, validation-only, or another method.
- Do not claim Red/Green evidence unless it was required and actually observed.
- Do not add a test solely to manufacture process evidence when the target project does not require it.
- When executable regression proof is required, keep the proof aligned with the behavior being changed.
- A failing or unavailable check must remain failing or unavailable in the report.

## Scope and review boundary

- Implementation may change only paths and operations inside the accepted write boundary.
- Implementation must not issue an independent review verdict for its own changes.
- Review findings may be reported as inputs and addressed outcomes, but final review ownership remains with the review runtime.
- Implementation does not merge.

## Required implementation evidence

Record at least:

- implementation mode,
- accepted scope and non-goals,
- requirements and design references,
- changed files and purpose,
- intentionally untouched areas,
- validation commands and results,
- failure diagnostics and artifacts when applicable,
- commit identities,
- final HEAD SHA,
- matching CI run or explicit absence,
- blocked items, unknowns, and remaining risks,
- next required action.

## Completion condition

Implementation is complete only when the accepted scope is implemented or explicitly blocked, target-project validation is recorded accurately, the final HEAD is explicit, required implementation evidence is available to the runtime adapter, no independent review verdict was issued, and no merge was performed.