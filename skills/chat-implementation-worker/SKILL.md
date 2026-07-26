---
name: chat-implementation-worker
description: Execute a bounded initial implementation or review follow-up directly in one ChatGPT chat when the user coordinates the workflow as the parent. Use for scoped code, test, configuration, documentation, or repository changes with implementation reporting and durable handoff, without review ownership or nested worker dispatch.
---

# Chat Implementation Worker

## Goal

Execute one accepted implementation scope in the current ChatGPT chat, persist accurate implementation evidence, update or create the PR as required, and leave a transportable handoff for the next user-started chat.

## Shared contracts

Follow these canonical contracts instead of redefining their rules here:

- [Common Work Contract](../../shared/workflow/common-work-contract.md)
- [Implementation Contract](../../shared/workflow/implementation-contract.md)
- [Report Contract](../../shared/workflow/report-contract.md)
- [Chat Worker Handoff Contract](../../shared/chat-worker/handoff-contract.md)

For ChatGPT Project configuration, use the target project's actual instructions. A maintained example is available at [ChatGPT Project Instruction Example](../../shared/chat-worker/project-instruction-example.md).

The GitHub Release builder rewrites these repository links and includes the referenced files inside the installable Skill.

## Execution owner

Run this Skill directly in the current ChatGPT chat.

- The user is the parent and chooses the task, permissions, next chat, and merge action.
- This worker must not start another worker or sub-agent.
- Resolve discoverable repository state through the available connector before asking the user.
- The target project's instructions own implementation order and testing policy.

## Inputs

An Issue or task identifier plus `initial implementation` is normally sufficient.

For `review follow-up`, a PR identifier or an instruction to address the current review is normally sufficient. Resolve the applicable findings, reviewed HEAD, branch, current HEAD, reports, and handoffs from repository evidence.

## Runtime flow

1. Resolve the target repository, Issue or PR, task entry, accepted scope, branch, base, current HEAD, requirements, design, write boundary, validation policy, reports, and handoffs.
2. Select `initial implementation` or `review follow-up` and execute the shared Implementation Contract directly.
3. Use repository tooling and connectors allowed by the current chat to apply changes, commit, push, and create or update the PR as required.
4. Create an implementation report under the repository's report rules. If writing is unavailable, return the complete report body.
5. When a PR exists, post a concise PR comment derived from the implementation report. If commenting is unavailable, return the complete comment body.
6. Create a handoff packet using the Chat Worker Handoff Contract and persist it under `reports/handoffs/` when authorized; otherwise return it in full.

## Runtime-specific boundaries

- Do not issue an independent review verdict for this worker's own implementation.
- Do not perform a cold or independent final review in the implementation chat.
- Do not exceed the current chat's explicit permissions.
- Do not merge.

## Outputs

Return or persist:

- implementation mode and accepted scope,
- changed files and validation evidence,
- commits, final HEAD, and matching CI evidence or explicit absence,
- implementation report path or complete body,
- PR identifier and concise comment reference or complete body,
- handoff path or complete packet,
- blocked items, unknowns, remaining risks, and next action.

## Completion condition

This Skill is complete only when the shared Common Work and Implementation contracts are satisfied, required report and PR outputs are available, a transportable handoff exists, no independent review verdict was issued, and no merge was performed.
