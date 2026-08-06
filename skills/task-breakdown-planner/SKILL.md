---
name: task-breakdown-planner
description: Break an issue, request, or large work item into concrete tasks and phases with dependencies and exit criteria using the target project's canonical tracking paths. Use when starting a new issue, when an existing task is too large, when planning remaining work to completion, or when rescoping after new requirements appear.
---

# Task Breakdown Planner

Translate large work into executable tracked units.

## Goal

Create a task structure that allows one-task-at-a-time execution without hidden work.

## Execution owner

Run this Skill in the caller that owns authorized canonical tracking writes.

- In the Codex standard flow, that owner is normally the parent.
- In a ChatGPT worker flow, the current chat may execute this Skill directly when the wrapper has write authorization.
- This Skill does not require or start a sub-agent.
- A caller with its own delegation capability may obtain a bounded planning draft separately, but final task and phase adoption remains with the authorized caller and delegation is never required by this Skill.

## Inputs

Before running this Skill, gather:

- issue or request scope,
- known constraints and dependencies,
- structured context from `work-context-manager`, including `tracking.task_path` and `tracking.phase_path`,
- current content of the resolved canonical tracking files when they already exist.

Do not hardcode `tasks-status.md` or `phases-status.md`. Use the resolved repository-relative paths exactly. If `tracking.task_path` is unknown, stop as blocked instead of guessing. If `tracking.phase_path` is null, do not invent a separate phase file. If it is unknown and phase tracking is required by the project, stop as blocked.

## Outputs

Produce or revise at the resolved canonical paths:

- task entries,
- phase entries when the project uses a separate phase tracking file,
- dependencies,
- exit criteria,
- size estimates.

Return the canonical task tracking path, canonical phase tracking path or null, created or revised task identities, phases when applicable, dependencies, exit criteria, estimates, and next executable task.

If a canonical tracking file must be created according to authoritative project rules, write a top-of-file rule stating that the file may be updated only through `task-breakdown-planner`, `task-consistency-manager`, or `progress-sync-manager`.

## Completion condition

This Skill is complete only when:

- task and phase breakdown is explicit,
- dependencies and exit criteria are recorded,
- another agent or chat could execute the next task without guessing,
- no guessed tracking path was used.

## Breakdown rules

Prefer tasks that can move all the way to commit and PR.

Split by workflow boundaries such as:

- investigation,
- design update,
- failing tests when the target project requires them,
- implementation,
- review fixes,
- integration or E2E verification,
- documentation or tracking sync.

Do not create tasks that are so broad that they hide multiple implementation cycles.

## Quality bar

A task is acceptable only if another agent could execute it without guessing:

- what to change,
- how to prove it works,
- when to stop.

## Phase rules

Create or update phases only when the target project uses phases and the work introduces a meaningful milestone or exit checkpoint.

Keep remaining phases truthful. Do not leave stale estimates or completed work in remaining sections.
