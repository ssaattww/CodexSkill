---
name: chat-implementation-worker
description: Execute a bounded initial implementation or review follow-up directly in one ChatGPT chat when the user coordinates the workflow as the parent. Use for test-first code and test changes, implementation reporting, and durable handoff without review ownership or nested worker dispatch.
---

# Chat Implementation Worker

## Goal

Implement a decided task or review follow-up in one ChatGPT chat, validate it, create a durable implementation report, and produce a handoff for the next user-started chat.

## Execution model

- The user is the parent and controls the repository, branch, task order, permissions, next chat, and merge decision.
- This worker must not start another worker.
- Use only the supplied task packet and authoritative repository sources; do not rely on previous conversation history.
- This worker must create an implementation report but must not issue the final review verdict.
- Follow the [shared handoff contract](../chat-worker-shared/references/handoff-contract.md).
- A handoff is not automatically visible to another chat. When `write_handoff` is authorized, store it under `reports/handoffs/`; otherwise return the complete packet for user copy and paste.

## Inputs

Require:

- task, issue, or PR identifier
- repository, branch, base reference, and current HEAD SHA
- mode: `initial implementation` or `review follow-up`
- scope, non-goals, and authoritative requirements
- target files and relevant dependency boundaries
- current `authorized_actions` and `write_boundary`
- behavior to prove test-first
- focused and full validation expectations
- report path or repository report naming policy
- previous findings and required regressions for review follow-up

If required information is missing, do not guess. Record it under `unknown`, mark the implementation `blocked`, create a report describing the blocked state when reporting is authorized, and return control to the user.

## Modes

### initial implementation

- Start with the smallest testable behavior.
- Inspect existing contracts before introducing a new model.
- Do not redesign the whole task or broaden scope.

### review follow-up

- Add or strengthen a failing regression before the fix.
- Limit work to the finding, its direct cause, affected boundary, and sibling cases of the same defect class.
- Preserve all earlier regression tests.
- Do not mix unrelated cleanup into the fix.

## Required flow

1. Resolve repository, branch, base, HEAD, scope, permissions, write boundaries, and report destination.
2. Read target files, direct dependencies, existing contracts, test wiring, and CI entry points.
3. Add or identify a failing test or contract check before implementation.
4. Record the Red command, exit code, failure, HEAD SHA, and diagnostic artifact when available.
5. Implement the smallest change that satisfies the requirement.
6. Run focused validation, then relevant suites and required full validation.
7. Record build, lint, unit, integration, host, packaging, and environment evidence that applies.
8. For failures, preserve or inspect stdout, stderr, environment, source, tests, configuration, generated output, and test results needed for diagnosis.
9. Record changed files, intentionally untouched areas, commits, final HEAD SHA, and remaining risks.
10. Create an implementation report under the repository report directory, normally `reports/`, using the repository naming and template rules.
11. Create a complete handoff packet that references the report path.
12. If `write_handoff` is authorized, write the packet to `reports/handoffs/` and return its path. Otherwise return the complete packet inline for copy and paste.

## Test-first rules

- Executable behavior changes are test-first by default.
- An existing test may serve as Red evidence only when it already proves the exact failure.
- Documentation-only or externally blocked work may use `not_applicable` with a concrete reason.
- Do not weaken tests to match the implementation.
- Assert exact values, state, identity, side effects, and failure behavior rather than success or throw alone.
- Fixtures must be producible by the real protocol, parser, API, or tool.

## Scope and safety rules

- Do not exceed the user-approved scope.
- Do not perform actions absent from `authorized_actions`.
- Do not write outside `write_boundary`.
- Do not modify work owned by another task, PR, or worker.
- Do not revert unrelated changes.
- Do not include secrets or credentials in reports or handoffs.
- Do not treat your own implementation as independently reviewed.
- This worker must not merge.

## Report requirement

- The implementation report is a mandatory work product, separate from the handoff packet.
- The report must describe scope, non-goals, authoritative requirements, Red and Green evidence, changed files, commands, tests, CI, artifacts, commits, final HEAD SHA, blocked items, and remaining risks.
- The report must not invent review findings, review verdicts, or merge approval.
- The report may state that independent review has not yet occurred.
- A handoff file under `reports/handoffs/` is transport evidence and does not replace the implementation report.
- If repository writing is unavailable, return the complete report body together with the handoff packet so the user can persist it.

## Outputs

Return:

- scoped code and test changes
- Red and Green evidence
- changed and intentionally untouched files
- commands, tests, CI, and artifacts
- commits and final HEAD SHA
- implementation outcome and remaining risks
- implementation report path or complete report body
- `next_chat_input`
- a packet conforming to the shared contract
- either a `reports/handoffs/` packet path or the complete inline packet

## Completion condition

Complete only when the assigned scope is implemented or explicitly blocked, test-first evidence or an exemption is recorded, required validation is recorded, failures and risks are explicit, the final HEAD is identified, an implementation report has been created or returned in full, no review verdict was issued, and a transportable handoff is available. This worker must not merge.
