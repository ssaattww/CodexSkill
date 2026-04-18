---
name: implementation-executor
description: Execute concrete implementation work in code and tests after task scope has been decided. Use when code authoring, test authoring, or bounded fix work must be carried out as implementation work.
---

# Implementation Executor

Perform the actual code and test changes.

## Goal

Turn an already-scoped task into concrete code and test updates without re-planning the workflow.

## Execution owner

Run this skill as: `parent`

- This skill describes the execution work for code and test authoring.
- `codex-delegation-executor` may assign that editing work to the parent or a `sub-agent`.

## Use this skill when

- task scope and exit criteria are already known
- code files must be changed
- tests must be added or updated
- review follow-up requires concrete implementation edits

## Required inputs

Before running this skill, make sure the parent has already decided:

- task scope and non-goals
- target files or affected modules
- validation target or expected proof

## Required flow

1. read the relevant code and tests
2. make the smallest changes that satisfy the scoped task
3. update or add tests when the task requires executable proof
4. keep unrelated changes untouched
5. report changed files, validation run, and any remaining risks

## Rules

- Do not re-plan the task; `task-breakdown-planner`, `task-consistency-manager`, and `tdd-executor` own that planning work.
- Do not broaden scope beyond the assigned task.
- Prefer the narrowest implementation that satisfies the required behavior.
- Keep code and tests aligned; do not leave test expectations implicit when a task depends on them.

## Output expectations

After this skill runs, the scoped code/test changes are in place and ready for validation or review.
