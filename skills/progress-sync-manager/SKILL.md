---
name: progress-sync-manager
description: Synchronize canonical task and phase tracking, report references, and related progress records with actual work results. Use after planning changes, after review, after commit/PR creation, or whenever tracking no longer matches the real state of the work.
---

# Progress Sync Manager

Keep canonical tracking truthful and current.

## Goal

Make recorded project status reflect actual execution state without delay.

## Execution owner

Run this Skill in the caller that owns authorized canonical tracking writes.

- In the Codex standard flow, that owner is normally the parent.
- In a ChatGPT worker flow, the current chat may execute this Skill directly when the wrapper has write authorization.
- This Skill does not require or start a sub-agent.

## Inputs

Before running this Skill, gather:

- latest task, review, verification, commit, or PR outcome,
- structured context from `work-context-manager`, including `tracking.task_path` and `tracking.phase_path`,
- current content of the resolved canonical tracking files,
- relevant report references to sync.

Do not hardcode `tasks-status.md` or `phases-status.md`. Use the resolved repository-relative paths exactly. If `tracking.task_path` is unknown, stop as blocked instead of guessing. If `tracking.phase_path` is null, do not create a phase file unless an authoritative project rule requires one. If it is unknown and phase tracking is required, stop as blocked.

## Update targets

Update as relevant at the resolved canonical paths:

- task tracking,
- phase tracking when configured,
- progress summary sections,
- overall progress sections,
- report references,
- PR references if tracked.

If a canonical tracking file must be created according to authoritative project rules, include a top-of-file rule stating that the file may be updated only through `task-breakdown-planner`, `task-consistency-manager`, or `progress-sync-manager`.

## Required timing

Run this Skill:

- after tasks are added or split,
- after significant implementation milestones,
- after review,
- after commit and PR creation,
- after blocked state changes,
- whenever tracking is discovered to be stale.

## Rules for canonical task tracking

Ensure it reflects:

- current active task,
- completed tasks,
- new tasks from review or discoveries,
- dependencies,
- exit criteria,
- PR/commit completion if part of done.

## Rules for canonical phase tracking

When a separate phase tracking path is configured, ensure it reflects:

- current phase position,
- remaining phase count,
- changed exit criteria,
- completed milestones,
- honest remaining estimates.

## Strong rule

Do not leave tracking updates as optional end-of-day cleanup. Update close to the work that changed the state.

## Outputs

After this Skill runs, return:

- canonical task tracking path,
- canonical phase tracking path or null,
- current task state,
- current phase when applicable,
- dependencies and exit criteria,
- latest report and PR references when applicable,
- latest validation state,
- blockers,
- next pending tracking action,
- real completion status of recent work.

## Completion condition

This Skill is complete only when canonical tracking matches the actual execution state and no guessed tracking path was used.

## Cross-cutting rule

If stale tracking is a recurring problem, call `feedback-points-manager` when that Skill is available in the current runtime.
