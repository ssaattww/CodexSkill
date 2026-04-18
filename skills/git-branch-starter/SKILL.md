---
name: git-branch-starter
description: Start work on an appropriate branch for the current task or issue. Use when beginning implementation, when resuming work that should not happen on the default branch, or when preparing to isolate a task into a reviewable submission unit.
---

# Git Branch Starter

Create a safe branch boundary for the current work.

## Goal

Ensure task work is isolated on a branch before meaningful changes accumulate.

## Execution owner

Run this skill as: `parent`

- Branch creation changes the active Git context and should stay under parent control.

## Inputs

Before running this skill, identify:

- current task or issue scope
- current branch state
- desired branch naming basis

## Rules

- Use a branch name tied to the issue or task scope.
- Keep the branch purpose narrow enough to produce a reviewable PR.
- Avoid direct work on the default branch unless explicitly intended.

## Outputs

After this skill runs, the current task has a clear branch context for future commit and PR steps.

## Completion condition

This skill is complete only when the active work is isolated on the intended branch.
