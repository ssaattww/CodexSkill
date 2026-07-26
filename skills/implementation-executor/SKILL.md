---
name: implementation-executor
description: Execute concrete implementation work after task scope has been decided. Use when bounded code, test, documentation, configuration, workflow, or review-follow-up edits must be performed under the target project's development policy.
---

# Implementation Executor

## Goal

Execute an already-scoped implementation through the Codex runtime without redefining cross-runtime implementation rules.

## Shared contracts

Follow:

- [Common Work Contract](../../shared/workflow/common-work-contract.md)
- [Implementation Contract](../../shared/workflow/implementation-contract.md)

These files are the canonical implementation semantics shared with ChatGPT workers. This Skill contains only the Codex execution adapter.

## Execution owner

Run this Skill as: `parent`.

- The parent owns scope, write boundary, and completion integration.
- `codex-delegation-executor` may assign the actual editing work to the parent or an implementation sub-agent.
- A delegated executor reads this Skill and the shared contracts before editing.

## Inputs

Before running this Skill, the parent must establish:

- implementation mode: initial implementation or review follow-up,
- accepted scope and non-goals,
- target files or affected modules,
- authoritative requirements and design,
- target-project development and testing policy,
- validation target and expected proof,
- allowed and forbidden writes.

## Required flow

1. Select the executor through `codex-delegation-executor`.
2. Give the executor the accepted scope, write boundary, target identity, relevant files, validation policy, and shared-contract paths.
3. Execute the shared Implementation Contract.
4. Return changed files, validation evidence, commit-relevant summary, unknowns, and remaining risks to the parent.
5. Leave report persistence, review, progress sync, commit, push, PR, and handoff orchestration to their owning parent Skills.

## Codex adapter rules

- Do not re-plan the task; planning belongs to `task-breakdown-planner`, `task-consistency-manager`, and the parent workflow.
- Do not decide TDD applicability here. The target project and caller own that policy.
- Do not broaden scope beyond the assigned task.
- Do not let the implementation executor review its own work.
- For executor selection, follow `codex-delegation-executor`; do not invent a separate dispatch policy here.
- Do not merge.

## Outputs

After this Skill runs, the parent receives:

- applied scoped changes,
- changed and intentionally untouched files,
- focused and broader validation evidence required by the target project,
- failure diagnostics when applicable,
- unknowns, blocked items, and remaining risks,
- a result ready for report generation and review.

## Completion condition

This Skill is complete only when the shared Common Work and Implementation contracts are satisfied for the assigned scope, the parent has the evidence required for the next workflow stage, no review verdict was issued by the executor, and no merge was performed.