---
name: task-consistency-manager
description: Validate that intended work is explicitly represented in canonical task and phase tracking before and during implementation. Use when starting a task, when implementation reveals missing scope, dependencies, or exit criteria, or when review uncovers new work that must be tracked before proceeding.
---

# Task Consistency Manager

Ensure that no meaningful work proceeds unless it exists in canonical task tracking.

## Goal

Keep the configured canonical task and phase tracking aligned with actual implementation scope.

## Execution owner

Run this Skill in the caller that owns authorized canonical tracking writes.

- In the Codex standard flow, that owner is normally the parent.
- In a ChatGPT worker flow, the current chat may execute this Skill directly when the wrapper has write authorization.
- This Skill does not require or start a sub-agent.
- A caller with its own delegation capability may obtain a bounded audit separately, but final canonical tracking writes remain with the authorized caller and delegation is never required by this Skill.

## Inputs

Before running this Skill, gather:

- current intended work item,
- structured context from `work-context-manager`, including `tracking.task_path` and `tracking.phase_path`,
- current content of the resolved canonical tracking files,
- any newly discovered scope from implementation or review.

Do not hardcode `tasks-status.md` or `phases-status.md`. Use the resolved repository-relative paths exactly. If `tracking.task_path` is unknown, stop as blocked instead of guessing. If `tracking.phase_path` is null, do not create a phase file unless an authoritative project rule requires one. If it is unknown and phase tracking is required, stop as blocked.

## Run this Skill

Run this Skill:

- before starting any task,
- when implementation reveals missing work,
- when a task is too large or vague,
- when review creates follow-up work,
- when phase scope or exit criteria have changed.

## Required checks

Check whether the current work item has:

- a task entry,
- a phase assignment when the project uses phases,
- dependencies,
- exit criteria,
- an estimate or expected size,
- wording precise enough to decide done vs not done.

## Required actions

If the task is missing, add or revise canonical tracking before implementation continues.

If the task is too large, invoke `task-breakdown-planner` using the same resolved tracking paths.

If the task implies additional work not yet tracked, add the missing tasks first.

If the task changes phase scope and a canonical phase tracking file exists, update that resolved phase path as well.

If a canonical tracking file must be created according to authoritative project rules, include a top-of-file rule stating that the file may be updated only through `task-breakdown-planner`, `task-consistency-manager`, or `progress-sync-manager`.

## Strong rule

Do not implement significant work that is not represented in the resolved canonical task tracking file.

Allow exceptions only for tiny corrections such as obvious typos or purely mechanical renames with no behavior or contract impact.

## Outputs

After this Skill runs, return:

- canonical task tracking path,
- canonical phase tracking path or null,
- active task identity,
- current tracking state,
- phase when applicable,
- dependencies,
- exit criteria,
- blockers,
- whether additional tasks were added or split,
- next pending tracking action.

## Completion condition

This Skill is complete only when:

- tracking reflects the real current scope,
- any missing or split tasks are recorded,
- the next implementation step is unambiguous from canonical tracking,
- no guessed tracking path was used.
