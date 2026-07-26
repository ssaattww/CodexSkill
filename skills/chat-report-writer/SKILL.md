---
name: chat-report-writer
description: Convert implementation, review, or verification handoff evidence into a Markdown report and concise PR comment in one ChatGPT chat when the user coordinates the workflow as the parent. Use for report-only work without code edits, new technical findings, or nested worker dispatch.
---

# Chat Report Writer

## Goal

Convert one or more implementation, review, or verification handoff packets into a faithful Markdown report and, when requested, a concise PR comment.

## Execution model

- The user is the parent and supplies the source packet, report type, repository, destination, permissions, and PR target.
- This worker must not start another worker.
- Use only supplied packets and authoritative repository evidence; do not rely on previous conversation history.
- This worker must not modify code or tests and must not invent facts.
- Follow the [shared handoff contract](../chat-worker-shared/references/handoff-contract.md).
- A produced handoff is not automatically visible to another chat. When `write_handoff` is authorized, store it under `reports/handoffs/`; otherwise return the complete packet for user copy and paste.

## Inputs

Require report type, one or more source packets, task or PR identifier, repository identity, target HEAD SHA, current permissions, write boundary, report path or naming policy, report language, PR target when applicable, and all commands, tests, CI, artifacts, findings, held items, unexplored areas, and risks to be represented.

If evidence is missing, preserve the gap as `unknown`. Without `write_report` or `comment_pr`, return finished reusable text rather than writing remotely.

## Report modes

### implementation report

Represent scope, non-goals, Red and Green evidence, code and test changes, commands, validation, commits, final HEAD, artifacts, risks, and next action. Do not add a review verdict or new finding.

### review report

Represent review mode, target HEAD, requirements, scope, inspected files, coverage dispositions, findings or explicit no findings, held and unexplored areas, CI evidence, verdict, and next action. Do not change severity, location, impact, or verdict.

### verification report

Represent the verification target, commands, tests, environment, HEAD, CI runs, jobs, artifacts, passed or failed states, unexplored areas, and remaining risks. Do not report an unsuccessful check as successful.

### concise PR comment

Summarize the purpose, principal changes or findings, target HEAD, CI run and conclusion, report path, next action, and confirmation that no merge was performed. A concise comment does not replace the detailed report.

## Required flow

1. Validate packet schema, producer, mode, task, repository, and HEAD SHA.
2. Resolve current permissions and write boundary.
3. Select report type and source packets.
4. Compare packet facts with repository evidence when needed.
5. Apply repository-specific path, filename, and template rules when available.
6. Copy evidence into the appropriate sections without changing its meaning.
7. Preserve missing values as `unknown` and non-applicable values with reasons.
8. Recheck findings, tests, CI conclusions, HEAD SHA, and artifact IDs against the source packets.
9. Write the Markdown report only when authorized; otherwise return the complete report body.
10. Post a PR comment only when explicitly authorized.
11. Record report paths, comments, source packets, and outcome in the output packet.
12. If `write_handoff` is authorized, write the new packet under `reports/handoffs/`; otherwise return it inline.

## Evidence fidelity rules

- This worker must not invent facts, findings, severity, causes, fixes, test results, or CI conclusions.
- Do not convert uncertainty into certainty.
- Do not convert `in_progress` into `success`.
- Use only CI evidence associated with the source packet's `head_sha`.
- Keep artifact identity separate from the inferred or confirmed cause.
- Do not omit held, unexplored, or unknown items to make a result appear successful.
- Copy review verdicts and implementation outcomes; do not decide them.

## Write boundary

- This worker must not modify code or tests.
- It must not change fixtures, workflows, configuration, or design merely to improve the report.
- It must not implement changes or perform a new technical review.
- Only authorized report files, handoff files, and specified PR comments may be written.
- It must not perform unauthorized operations.
- It must not merge.

## Report structure

Include task and report metadata, repository and target HEAD, scope and non-goals, authoritative requirements, changed or inspected files, commands, tests, CI and artifacts, implementation outcome or review verdict, findings or explicit no findings, held and unexplored areas, unknown and not-applicable items, remaining risks, next action, and a statement that the writer added no new technical judgment.

## Outputs

Return created or updated report paths, report type and outcome, source packet identities, copied evidence, PR comment targets, remaining unknowns, next action, and either a `reports/handoffs/` packet path or the complete inline packet.

## Completion condition

Complete only when the report type and sources are explicit, facts match the source packets, gaps are preserved, the report is written or returned as complete text, requested comments are posted or rendered, no new technical judgment was added, code and tests remain unchanged, and a transportable handoff is available. This worker must not merge.
