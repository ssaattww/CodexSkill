---
name: git-review-followup-manager
description: Manage review feedback on an existing PR by converting findings into tracked work, applying fixes, and resubmitting for review. Use when PR comments arrive, when Codex review produces follow-up actions, or when a task must loop through another review cycle before it can be considered complete.
---

# Git Review Follow-up Manager

Close the loop on review feedback.

## Goal

Convert review feedback into tracked, verifiable, and reviewable follow-up work.

## Execution owner

Run this skill as: `parent`

- Parent owns task routing, follow-up scope, and PR state updates.
- Implementation work inside this skill may still be delegated through `codex-delegation-executor`.

## Required flow

1. read the feedback
2. decide whether the fix belongs to the current task or a new task
3. call `task-consistency-manager` if tracking changes are needed
4. implement the fix through the normal workflow, using `codex-delegation-executor` to decide whether the main agent or a sub-agent owns the fix work and making the executor read `implementation-executor`
5. update reports and progress
6. refresh the PR state

When creating a new follow-up report file, call `report-output-manager`.

## Rules

- Do not apply review feedback as invisible side work.
- Track meaningful fixes explicitly.
- Re-review when the fix changes behavior or closes a substantive finding.
