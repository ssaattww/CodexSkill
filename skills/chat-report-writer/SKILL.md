---
name: chat-report-writer
description: Convert implementation, review, or verification evidence into a Markdown report and concise PR comment in one ChatGPT chat when the user coordinates the workflow as the parent. Use for report-only work without code edits, new technical findings, or nested worker dispatch.
---

# Chat Report Writer

## Goal

Resolve the applicable source reports and handoffs for a task or PR, then create a faithful Markdown report and concise PR comment.

## Execution model

- The user is the parent and controls the requested report type, scope changes, next chat, and merge decision.
- This worker must not start another worker.
- Resolve discoverable report sources from project instructions, the PR, linked issue, repository reports, handoffs, comments, commits, and workflow runs before asking the user.
- Do not require the user to list source paths, repository URL, target HEAD, or PR evidence when the task or PR makes them unambiguous.
- This worker must not modify code or tests and must not invent facts.
- Follow the [shared handoff contract](../chat-worker-shared/references/handoff-contract.md).
- A produced handoff is not automatically visible to another chat. When `write_handoff` is authorized, store it under `reports/handoffs/`; otherwise return the complete packet for user copy and paste.

## Inputs

A task or PR identifier plus the requested report type is normally sufficient.

Discover source reports and handoffs by task, PR, role, mode, branch, target HEAD, and commit relationship. Ask the user only when multiple unresolved candidate source sets remain or the user must choose the intended report scope.

## Report modes

### implementation report

Represent scope, implementation changes, validation, commits, final HEAD, artifacts, risks, and next action. Follow the project testing policy; do not invent test-first evidence when it was not required or recorded.

### review report

Represent review mode, target HEAD, requirements, scope, inspected files, coverage dispositions, findings or explicit no findings, held and unexplored areas, CI evidence, verdict, and next action. Do not change severity, location, impact, or verdict.

### verification report

Represent the verification target, commands, tests, environment, HEAD, CI runs, jobs, artifacts, passed or failed states, unexplored areas, and remaining risks. Do not report an unsuccessful check as successful.

### concise PR comment

Summarize the purpose, principal changes or findings, target HEAD, CI evidence when applicable, report path, next action, and confirmation that no merge was performed. A concise comment does not replace the detailed report.

## Required flow

1. Resolve the task or PR, current HEAD, linked issue, report type, project rules, and report destination.
2. Discover source reports and handoffs from the repository and PR conversation.
3. Select sources by task, producer role, mode, target HEAD, and commit relationship rather than timestamp alone.
4. Compare source facts with repository evidence where needed.
5. Apply repository-specific path, filename, language, and template rules.
6. Copy evidence into the appropriate sections without changing its meaning.
7. Preserve missing values as `unknown` and non-applicable values with reasons.
8. Recheck findings, validation, CI conclusions, HEAD SHA, and artifact IDs against the sources.
9. Write the Markdown report; if repository writing is unavailable, return the complete report body.
10. Post the required concise PR comment when a PR exists.
11. Record report paths, comments, source packets, and outcome in the output packet.
12. If `write_handoff` is authorized, write the new packet under `reports/handoffs/`; otherwise return it inline.

## Discovery rules

- A PR identifier is sufficient to resolve repository, current HEAD, linked issue, reports, handoffs, comments, and CI evidence.
- A task or issue identifier is sufficient when it unambiguously resolves an active branch or PR.
- Prefer sources that explicitly reference the target HEAD or a commit range containing it.
- Ask for a source path only when repository discovery leaves a real ambiguity.

## Evidence fidelity rules

- This worker must not invent facts, findings, severity, causes, fixes, validation results, or CI conclusions.
- Do not convert uncertainty into certainty.
- Do not convert `in_progress` into `success`.
- Use only CI evidence associated with the applicable `head_sha` when required by project instructions.
- Keep artifact identity separate from the inferred or confirmed cause.
- Do not omit held, unexplored, or unknown items to make a result appear successful.
- Copy review verdicts and implementation outcomes; do not decide them.

## Write boundary

- This worker must not modify code or tests.
- It must not change fixtures, workflows, configuration, or design merely to improve the report.
- It must not implement changes or perform a new technical review.
- Only report files, handoff files, and PR comments may be written.
- It must not merge.

## Report structure

Include task and report metadata, repository and target HEAD, scope, authoritative requirements, changed or inspected files, commands and validation, CI and artifacts, implementation outcome or review verdict, findings or explicit no findings, held and unexplored areas, unknown and not-applicable items, remaining risks, next action, and a statement that the writer added no new technical judgment.

## Outputs

Return created or updated report paths, report type and outcome, source identities, copied evidence, PR comment reference, remaining unknowns, next action, and either a `reports/handoffs/` packet path or the complete inline packet.

## Completion condition

Complete only when the report type and sources are explicit, facts match the sources, gaps are preserved, the report is written or returned as complete text, the concise PR comment is posted or rendered, no new technical judgment was added, code and tests remain unchanged, and a transportable handoff is available. This worker must not merge.
