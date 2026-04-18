---
name: progress-sync-manager
description: Synchronize tasks-status.md, phases-status.md, reports references, and related progress records with actual work results. Use after planning changes, after review, after commit/PR creation, or whenever tracking no longer matches the real state of the work.
---

# Progress Sync Manager

Keep tracking files truthful and current.

## Goal

Make recorded project status reflect actual execution state without delay.

## Execution owner

Run this skill as: `parent`

- This skill updates canonical tracking files and should remain under parent control.

## Inputs

Before running this skill, gather:

- latest task, review, verification, commit, or PR outcome
- current `tasks-status.md` and `phases-status.md`
- relevant `reports/` references to sync

## Update targets

Update as relevant:

- `tasks-status.md`
- `phases-status.md`
- progress summary sections
- overall progress sections
- report references
- PR references if tracked

## Required timing

Run this skill:

- after tasks are added or split
- after significant implementation milestones
- after review
- after commit and PR creation
- whenever tracking is discovered to be stale

## Rules for tasks-status.md

Ensure it reflects:

- current active task
- completed tasks
- new tasks from review or discoveries
- dependencies
- exit criteria
- PR/commit completion if part of done

## Rules for phases-status.md

Ensure it reflects:

- current phase position
- remaining phase count
- changed exit criteria
- completed milestones
- honest remaining estimates

## Strong rule

Do not leave tracking updates as optional end-of-day cleanup. Update close to the work that changed the state.

## Outputs

After this skill runs, tracking should reflect:

- the current task and phase state
- latest report and PR references when applicable
- the real completion status of recent work

## Completion condition

This skill is complete only when canonical tracking matches the actual execution state.

## Cross-cutting rule

If stale tracking is a recurring problem, call `feedback-points-manager`.
