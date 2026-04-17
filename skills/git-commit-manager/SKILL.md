---
name: git-commit-manager
description: Prepare and create commits with appropriate scope, evidence, and cleanliness for the current task. Use after reviewable changes are ready, after verification has completed, or when a task needs to be checkpointed in a way that preserves clear history and supports PR creation.
---

# Git Commit Manager

Create clean, scoped commits.

## Goal

Produce commits that map cleanly to the current task and can be reviewed without guesswork.

## Rules

- Keep commit scope aligned to the current task.
- Avoid mixing unrelated work.
- Make sure verification and review results exist before final task commit.
- Stage intentionally; do not include noise or irrelevant generated files.

## Pre-commit checks

Confirm:

- task scope is correct
- tests or validation have run as required
- review outcome exists
- tracking updates are included if they are part of the task

## Output expectations

After this skill runs, the task has one or more coherent commits suitable for PR submission.