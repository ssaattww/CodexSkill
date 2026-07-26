---
name: chat-report-writer
description: Convert implementation, review, or verification evidence into a Markdown report and concise PR comment in one ChatGPT chat when the user coordinates the workflow as the parent. Use for report-only work without code edits, new technical findings, or nested worker dispatch.
---

# Chat Report Writer

## Goal

Resolve the authoritative evidence for one task or PR, create the requested report without changing its meaning, post or render the concise PR comment, and leave a transportable handoff.

## Shared contracts

Follow these canonical contracts instead of redefining their rules here:

- [Common Work Contract](../../shared/workflow/common-work-contract.md)
- [Report Contract](../../shared/workflow/report-contract.md)
- [Chat Worker Handoff Contract](../../shared/chat-worker/handoff-contract.md)

The GitHub Release builder rewrites these repository links and includes the referenced files inside the installable Skill.

## Execution owner

Run this Skill directly in the current ChatGPT chat.

- The user is the parent and chooses the report type, permissions, next chat, and merge action.
- This worker must not start another worker or sub-agent.
- Resolve source reports, handoffs, repository evidence, comments, commits, current HEAD, and matching CI evidence through the available connector before asking the user.
- This is report-only work. Do not perform a new implementation or technical review.

## Inputs

A task, Issue, or PR identifier plus the requested report mode is normally sufficient.

Supported modes follow the shared Report Contract:

- implementation report,
- review report,
- verification report,
- consolidated report,
- concise PR comment.

Ask the user only when multiple unresolved source sets remain or a product decision is required to define the report scope.

## Runtime flow

1. Resolve the target task or PR, report mode, current HEAD, project rules, destination, and write boundary.
2. Discover source reports, handoffs, comments, commits, validation, CI runs, and artifacts.
3. Select sources by identity and commit relationship, not timestamp alone.
4. Execute the shared Report Contract directly and preserve all unknown, held, and unexplored items.
5. Write the detailed report under the repository's path and naming rules. If writing is unavailable, return the complete report body.
6. Post the required concise PR comment when a PR exists. If commenting is unavailable, return the complete comment body.
7. Create a handoff packet using the Chat Worker Handoff Contract and persist it under `reports/handoffs/` when authorized; otherwise return it in full.

## Runtime-specific boundaries

- Do not modify code, tests, fixtures, workflows, configuration, or design.
- Do not create new technical findings or change a supplied verdict.
- Do not convert missing or unsuccessful evidence into success.
- Do not exceed the current chat's explicit permissions.
- Do not merge.

## Outputs

Return or persist:

- report mode, target identity, and authoritative source identities,
- created or updated report paths or complete bodies,
- copied evidence and preserved uncertainty,
- PR comment reference or complete body,
- handoff path or complete packet,
- remaining unknowns, risks, and next action.

## Completion condition

This Skill is complete only when the shared Common Work and Report contracts are satisfied, the requested report and PR outputs are available, no new technical judgment was invented, the write boundary is preserved, a transportable handoff exists, and no merge was performed.
