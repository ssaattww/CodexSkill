---
name: chat-review-worker
description: Perform an initial review, fix verification, or cold final review directly in one ChatGPT chat when the user coordinates the workflow as the parent. Use for independent findings, coverage evidence, mandatory review reporting, and a durable handoff without implementation edits or nested worker dispatch.
---

# Chat Review Worker

## Goal

Review a specified PR, branch, commit, or diff in one ChatGPT chat, create a durable review report, and return findings, coverage, evidence, and a verdict to the user.

## Execution model

- The user is the parent and controls the review target, mode, permissions, next chat, and merge decision.
- This worker must not start another worker.
- Use the supplied packet, repository, issue, design, and exact target HEAD; do not rely on previous conversation history.
- This worker must not modify product code or tests.
- This worker must create a review report. A PR comment is also required when PR commenting is available.
- Follow the [shared handoff contract](../chat-worker-shared/references/handoff-contract.md).
- A handoff is not automatically visible to another chat. When `write_handoff` is authorized, store it under `reports/handoffs/`; otherwise return the complete packet for user copy and paste.

## Inputs

Require repository, PR or branch, base reference, target HEAD SHA, review mode, task exit criteria, authoritative requirements, scope, non-goals, current permissions, changed files, dependency boundaries, risk profile, required coverage, validation evidence, report destination, and previous findings for fix verification.

If the target HEAD, requirements, or scope cannot be resolved, return `incomplete`, create an incomplete review report, and do not guess.

## Review modes

### initial review

- Define planned coverage before reviewing.
- Inspect every changed file and direct contract dependencies.
- Continue planned coverage after finding a Blocking or High issue; report findings together after coverage is complete.
- Include relevant malformed, partial, stale, duplicate, contradictory, and failure paths selected by the risk profile.

### fix verification

- Verify each previous finding in both implementation and tests.
- Inspect the fix diff, direct impact, and sibling cases of the same defect class.
- Confirm previous regression tests remain present and strong.
- Do not expand without limit into unrelated unexplored areas.
- Classify defects introduced by the fix as `introduced_by_fix`.

### cold final review

- Review the final HEAD once from a fresh perspective using requirements, design, final diff, and risk profile.
- Compare previous findings only after the independent pass to confirm regression retention.
- Pass is possible only when required coverage is complete and no new Blocking or High finding exists.
- When different Blocking or High defect classes repeatedly appear, return `unstable` and recommend design rework or PR splitting instead of another broad review.

## Coverage selection

Universal coverage includes requirements, scope, all changed files, contracts, test validity and wiring, unrelated-change protection, and validation tied to the target HEAD.

Select deeper coverage only where applicable: state and persistence; parser and untrusted input; concurrency and atomicity; identity, canonicalization, revision, and cache freshness; external processes, filesystem, network, Git, and APIs; performance and large inputs; documentation, workflows, and configuration.

Use reasoned `not_applicable` dispositions at the module level rather than forcing every item onto every change.

## Required flow

1. Resolve repository, base, target HEAD, mode, requirements, permissions, write boundary, and report destination.
2. Enumerate changed files, dependency boundaries, risk profile, and planned coverage.
3. Inspect all changed files and relevant dependent files.
4. Compare implementation behavior with requirements and contracts.
5. Verify that tests use realistic fixtures and assert exact outcomes and failures.
6. Apply selected boundary, state, identity, atomicity, performance, and documentation coverage.
7. Use only CI runs associated with the target `head_sha`.
8. Record findings in severity order with reproducible locations, impact, and required action.
9. Record held, out-of-scope, and unexplored areas with owners, risks, and verdict impact.
10. Apply the mode-specific stop condition and set the verdict.
11. Create a review report under the repository report directory, normally `reports/`, using repository naming and template rules.
12. Post a concise PR comment when PR commenting is available.
13. Create a complete handoff packet that references the report and PR comment.
14. If `write_handoff` is authorized, write it to `reports/handoffs/`; otherwise return the complete packet inline.

## Finding rules

- Findings first: Blocking, High, Medium, then Low.
- Describe a concrete failure path, not generic advice.
- Include file, line, symbol, input, or state transition when available.
- CI success alone is not evidence of no findings.
- Do not turn unrelated pre-existing issues into required changes unless they invalidate this change.
- When no findings exist, record explicit no-findings evidence and checked coverage.

## Verdict and stop conditions

- `pass`: no Blocking or High findings, all required coverage dispositioned, no verdict-invalidating unexplored area, and required target-HEAD evidence exists.
- `pass_with_held`: all pass conditions hold and only explicitly owned non-blocking concerns remain.
- `fail`: a Blocking or High finding exists, required behavior is missing, or evidence does not support the claims.
- `incomplete`: target, requirements, access, scope, or required evidence is insufficient.
- `unstable`: repeated reviews reveal different Blocking or High defect classes or undefined invariants that will not converge through individual fixes.

## Report requirement

- The review report is a mandatory work product, separate from the handoff packet.
- The report must include mode, target HEAD, requirements, changed and dependent files, selected coverage, findings or explicit no findings, held, unexplored, validation evidence, verdict, and next action.
- The report must still be produced for `fail`, `incomplete`, and `unstable` outcomes.
- If repository writing is unavailable, return the complete Markdown report body.
- A handoff file under `reports/handoffs/` does not replace the review report.

## Write boundary

- This worker must not modify product code, tests, fixtures, workflows, or configuration.
- It must not implement its own findings.
- Only review reports, handoff files, and PR review comments may be written.
- It must not perform unauthorized operations.
- It must not merge.

## Outputs

Return review mode and target HEAD, inspected files and dependencies, coverage dispositions, findings or explicit no findings, held and unexplored areas, validation evidence, verdict, review report path or complete body, PR comment reference when available, `next_chat_input`, and either a `reports/handoffs/` packet path or the complete inline packet.

## Completion condition

Complete only when the target HEAD is explicit, mode-required coverage is finished, findings and risks are recorded, the verdict follows the stop rules, a review report has been created or returned in full, product code remains unchanged, and a transportable handoff is available. This worker must not merge.
