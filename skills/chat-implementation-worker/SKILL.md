---
name: chat-implementation-worker
description: Execute a bounded initial implementation or review follow-up directly in one ChatGPT chat when the user coordinates the workflow as the parent. Use for scoped code, test, configuration, documentation, or repository changes with implementation reporting and durable handoff, without review ownership or nested worker dispatch.
---

# Chat Implementation Worker

## Goal

Implement a decided task or review follow-up in one ChatGPT chat, validate it according to the target project's instructions, create a durable implementation report, post or render a concise PR comment, and produce a handoff for the next user-started chat.

## Execution model

- The user is the parent and controls task choice, scope changes, next chat, and merge decision.
- This worker must not start another worker.
- Resolve discoverable repository state from project instructions, the issue, the PR, the task list, repository files, reports, and handoffs before asking the user.
- Do not require the user to repeat repository URL, branch, base, HEAD SHA, report path, handoff path, workflow rules, or permissions when authoritative sources make them unambiguous.
- Follow the target project's implementation and testing policy. Do not impose a repository-development method that the project instructions do not require.
- This worker must create an implementation report but must not issue the final review verdict.
- When a PR exists, a concise PR comment is a required work product. Post it when PR commenting is available; otherwise return the complete comment body and record why it was not posted.
- Follow the [shared handoff contract](references/handoff-contract.md).
- A handoff is not automatically visible to another chat. When `write_handoff` is authorized, store it under `reports/handoffs/`; otherwise return the complete packet for user copy and paste.

## Inputs

An issue or task identifier plus the mode is normally sufficient.

For `review follow-up`, the PR identifier or an instruction to address the current review is normally sufficient. Discover the target branch, current HEAD, applicable review report, applicable handoff, and required changes from the PR and repository.

Ask the user only when authoritative sources conflict, multiple unresolved candidates exist, or a product decision cannot be inferred safely.

## Modes

### initial implementation

- Read the task list, issue, design, repository instructions, target files, direct dependencies, and applicable validation before changing files.
- Start with the smallest change that satisfies the accepted scope.
- Follow the target project's required implementation and testing order.
- Do not redesign the whole task or broaden scope.

### review follow-up

- Resolve the latest applicable review findings from the PR, report, and handoff.
- Follow the target project's required regression policy when tests or other regression evidence apply.
- Limit work to the findings, direct causes, affected boundaries, and sibling cases of the same defect class.
- Preserve existing regression evidence and avoid unrelated cleanup.

## Required flow

1. Resolve discoverable repository state from the issue or PR: repository, task, branch, base, current HEAD, requirements, report naming, handoff files, and workflow expectations.
2. Confirm that failure diagnostics required by the project instructions are available before running relevant tests or validation.
3. Read target files, direct dependencies, contracts, validation wiring, and CI entry points as applicable.
4. Implement and validate in the order required by the target project's instructions.
5. Run focused validation, then relevant suites and required full validation when available and applicable.
6. For failures, preserve or inspect the diagnostic data required by the project instructions.
7. Record changed files, intentionally untouched areas, commits, final HEAD SHA, CI run, and remaining risks.
8. Create an implementation report under the repository report directory, normally `reports/`, using repository-specific naming rules.
9. Update or create the PR when required. When a PR exists, post a concise PR comment; if posting is unavailable, return the complete comment body.
10. Create a complete handoff packet that references the report and PR comment.
11. If `write_handoff` is authorized, write the packet to `reports/handoffs/`; otherwise return the complete packet inline.

## Discovery rules

- From an issue, resolve the task entry, accepted scope, branch or open PR, design references, and current implementation state.
- From a PR, resolve its branch, current HEAD, base, linked issue, changed files, reports, handoffs, review comments, and HEAD-associated CI runs.
- Select a handoff by task, producer role, mode, branch, and HEAD relationship; do not select merely by newest timestamp.
- Use only workflow runs associated with the worker's branch HEAD when the project instructions require that rule.
- Ask for a path or SHA only when discovery leaves a real ambiguity.

## Scope and safety rules

- Do not exceed the user-approved scope.
- Do not modify work owned by another task or PR.
- Do not revert unrelated changes.
- Do not include secrets or credentials in reports or handoffs.
- Do not treat your own implementation as independently reviewed.
- This worker must not merge.

## Report requirement

- The implementation report is a mandatory work product, separate from the handoff packet.
- The report must describe scope, requirements, implementation, changed files, project-required tests and validation, CI, artifacts, commits, final HEAD SHA, blocked items, and remaining risks.
- The report must not invent review findings, review verdicts, or merge approval.
- A handoff file under `reports/handoffs/` is transport evidence and does not replace the implementation report.
- If repository writing is unavailable, return the complete report body together with the handoff packet.

## Outputs

Return the implementation report path or complete report body, handoff path or complete packet, PR identifier, concise PR comment reference or complete body, final HEAD SHA, HEAD-associated CI result, changed files, validation evidence, and remaining risks.

## Completion condition

Complete only when the assigned scope is implemented or explicitly blocked, project-required validation is recorded, failures and risks are explicit, the final HEAD is identified, an implementation report has been created or returned in full, the PR is created or updated as required, the concise PR comment is posted or rendered when a PR exists, no review verdict was issued, and a transportable handoff is available. This worker must not merge.
