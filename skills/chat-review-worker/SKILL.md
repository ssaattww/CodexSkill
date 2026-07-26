---
name: chat-review-worker
description: Perform an initial review, fix verification, or independent final review directly in one ChatGPT chat when the user coordinates the workflow as the parent. Use for findings, coverage evidence, mandatory review reporting, and durable handoff without implementation edits or nested worker dispatch.
---

# Chat Review Worker

## Goal

Review one PR and target HEAD directly in the current ChatGPT chat, persist accurate review evidence, post or render the concise PR comment, and leave a transportable handoff.

## Shared contracts

Follow these canonical contracts instead of redefining their rules here:

- [Common Work Contract](../../shared/workflow/common-work-contract.md)
- [Review Contract](../../shared/workflow/review-contract.md)
- [Report Contract](../../shared/workflow/report-contract.md)
- [Chat Worker Handoff Contract](../../shared/chat-worker/handoff-contract.md)

The GitHub Release builder rewrites these repository links and includes the referenced files inside the installable Skill.

## Execution owner

Run this Skill directly in the current ChatGPT chat.

- The user is the parent and chooses the review mode, permissions, next chat, and merge action.
- This worker must not start another worker or sub-agent.
- Resolve the PR, current HEAD, requirements, changed files, reports, comments, handoffs, and matching CI evidence through the available connector before asking the user.
- This worker must not modify product code, tests, fixtures, workflows, configuration, or implementation documentation.

## Inputs

A PR identifier plus the review mode is normally sufficient.

Supported user-facing modes are:

- `initial review`
- `fix verification`
- `independent final review` or `cold final review`

The handoff and report use the canonical mode value `independent_final_review`.

## Chat continuity rules

### Normal review cycle

Use one review chat for the initial review and later fix verification when that chat remains available. This preserves finding identity, selected criteria, and reviewed-HEAD history.

If the original review chat is unavailable, a different non-implementing chat may become the normal reviewer, but it must reconstruct the previous finding set and record the continuity change.

### Independent final review

Use a newly started chat that:

- did not implement the PR,
- did not implement review fixes,
- was not the normal review chat,
- performs its independent pass before relying on earlier review conclusions.

A review performed in an implementation or normal-review chat must not be labeled as the independent final review.

## Runtime flow

1. Resolve the PR, linked Issue or task, base, current HEAD, requirements, design, changed files, direct dependencies, previous reports, handoffs, comments, and current-HEAD CI evidence.
2. Validate the selected mode and this chat's reviewer independence.
3. Execute the shared Review Contract directly for the selected mode.
4. Create the detailed review report under the repository's report rules. If writing is unavailable, return the complete report body.
5. Post a concise PR review comment derived from the report. If commenting is unavailable, return the complete comment body.
6. Create a handoff packet using the Chat Worker Handoff Contract and persist it under `reports/handoffs/` when authorized; otherwise return it in full.

## Runtime-specific boundaries

- Do not implement findings in the review chat.
- Do not exceed the current chat's explicit permissions.
- Do not call CI success a review result.
- Do not reuse an independent final review after the HEAD changes.
- Do not merge.

## Outputs

Return or persist:

- review mode, target HEAD, and reviewer continuity or independence evidence,
- inspected files, dependencies, risk profile, and coverage dispositions,
- findings or explicit no findings,
- held, unexplored, unknown, and not-applicable items,
- validation and current-HEAD CI evidence,
- verdict and next action,
- review report path or complete body,
- PR comment reference or complete body,
- handoff path or complete packet.

## Completion condition

This Skill is complete only when the shared Common Work and Review contracts are satisfied for the selected mode, the write boundary is preserved, required report and PR outputs are available, a transportable handoff exists, and no merge was performed.