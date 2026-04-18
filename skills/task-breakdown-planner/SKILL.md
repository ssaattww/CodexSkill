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
