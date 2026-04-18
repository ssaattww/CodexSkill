---
name: task-breakdown-planner
description: Break an issue, request, or large work item into concrete tasks and phases with dependencies and exit criteria. Use when starting a new issue, when an existing task is too large, when planning remaining work to completion, or when rescoping after new requirements appear.
---

# Task Breakdown Planner

Translate large work into executable tracked units.

## Goal

Create a task structure that allows one-task-at-a-time execution without hidden work.

## Execution owner

Run this skill as: `parent`

- Task and phase design set the execution contract and should stay under parent control.
- For large or noisy scope, the parent may request a bounded planning draft from a `sub-agent`, but final task/phase adoption remains parent work.

## Inputs

Before running this skill, gather:

- issue or request scope
- known constraints and dependencies
- current `tasks-status.md` and `phases-status.md` when they already exist

## Outputs

Produce or revise:

- phase entries in `phases-status.md`
- task entries in `tasks-status.md`
- dependencies
- exit criteria
- size estimates

If `tasks-status.md` or `phases-status.md` must be created from scratch, write a top-of-file rule stating that the file may be updated only through `task-breakdown-planner`, `task-consistency-manager`, or `progress-sync-manager`.

## Completion condition

This skill is complete only when:

- task and phase breakdown is explicit
- dependencies and exit criteria are recorded
- another agent could execute the next task without guessing

## Large-scope delegation

If the issue or remaining work is large enough that a first-pass breakdown would be expensive to do inline, the parent may:

1. use `sub-agent-task-manager`
2. ask a `sub-agent` for a bounded draft of tasks, phases, dependencies, and exit criteria
3. require a report under `reports/`
4. review and finalize the adopted breakdown in the parent

Do not let the `sub-agent` become the final owner of task structure.

Use these provisional thresholds as the default trigger:

- expected task candidates are 5 or more
- expected phases are 3 or more
- explicit dependency edges to reason about are 4 or more
- the parent would otherwise need to read 4 or more source documents before drafting the breakdown

## Breakdown rules

Prefer tasks that can move all the way to commit and PR.

Split by workflow boundaries such as:

- investigation
- design update
- failing tests
- implementation
- review fixes
- integration or E2E verification
- documentation or tracking sync

Do not create tasks that are so broad that they hide multiple implementation cycles.

## Quality bar

A task is acceptable only if another agent could execute it without guessing:

- what to change
- how to prove it works
- when to stop

## Phase rules

Create or update phases when the work introduces a meaningful milestone or exit checkpoint.

Keep remaining phases truthful. Do not leave stale estimates or completed work in remaining sections.
