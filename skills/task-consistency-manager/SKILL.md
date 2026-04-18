---
name: task-consistency-manager
description: Validate that intended work is explicitly represented in tasks-status.md and phases-status.md before and during implementation. Use when starting a task, when implementation reveals missing scope, dependencies, or exit criteria, or when review uncovers new work that must be tracked before proceeding.
---

# Task Consistency Manager

Ensure that no meaningful work proceeds unless it exists in task tracking.

## Goal

Keep `tasks-status.md` and `phases-status.md` aligned with actual implementation scope.

## Execution owner

Run this skill as: `parent`

- This skill updates canonical task tracking and should remain parent-owned.
- For large tracking diffs or many discoveries, the parent may request a consistency audit from a `sub-agent`, but final tracking updates remain parent work.

## Inputs

Before running this skill, gather:

- current intended work item
- `tasks-status.md`
- `phases-status.md`
- any newly discovered scope from implementation or review

## Run this skill

Run this skill:

- before starting any task
- when implementation reveals missing work
- when a task is too large or vague
- when review creates follow-up work
- when phase scope or exit criteria have changed

## Required checks

Check whether the current work item has:

- a task entry
- a phase assignment
- dependencies
- exit criteria
- an estimate or expected size
- wording precise enough to decide done vs not done

## Required actions

If the task is missing, add or revise tracking before implementation continues.

If the task is too large, split it into smaller tasks.

If the task implies additional work not yet tracked, add the missing tasks first.

If the task changes phase scope, update `phases-status.md` as well.

If `tasks-status.md` or `phases-status.md` does not exist yet and must be created, include a top-of-file rule stating that the file may be updated only through `task-breakdown-planner`, `task-consistency-manager`, or `progress-sync-manager`.

## Strong rule

Do not implement significant work that is not represented in `tasks-status.md`.

Allow exceptions only for tiny corrections such as obvious typos or purely mechanical renames with no behavior or contract impact.

## Outputs

After this skill runs, tracking must make the next step unambiguous:

- which task is active
- what blocks it
- what exits it
- whether additional tasks were added

## Completion condition

This skill is complete only when:

- tracking reflects the real current scope
- any missing or split tasks are recorded
- the next implementation step is unambiguous from tracking

## Large-scope delegation

If tracking review would span many tasks, many review findings, or a noisy mismatch between execution and tracking, the parent may:

1. use `sub-agent-task-manager`
2. ask a `sub-agent` for a bounded audit of missing tasks, stale entries, and ambiguous wording
3. require a report under `reports/`
4. apply and confirm the final tracking changes in the parent

Do not let the `sub-agent` silently rewrite canonical tracking without parent review.

Use these provisional thresholds as the default trigger:

- suspected stale or missing tracking points are 3 or more
- affected task rows are 5 or more
- review findings or implementation discoveries to reconcile are 3 or more
- `tasks-status.md` and `phases-status.md` both need coordinated edits across 2 or more sections each
