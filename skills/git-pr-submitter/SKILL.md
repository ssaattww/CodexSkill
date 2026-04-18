---
name: git-pr-submitter
description: Create a pull request that packages the current task with sufficient context, validation evidence, and report references. Use when a task has passed implementation, verification, review, and commit stages and is ready to be submitted for integration.
---

# Git PR Submitter

Turn task work into a reviewable PR.

## Goal

Submit each completed task as a PR with enough context for efficient review.

## Execution owner

Run this skill as: `parent`

- PR creation publishes the parent-owned outcome and should stay with the parent.

## Required PR contents

Include as relevant:

- task or issue scope
- summary of changes
- test or validation evidence
- report references
- notable risks or follow-ups

## Rules

- Keep PR scope aligned with the task.
- Do not hide unresolved findings.
- Do not create a PR with missing review evidence when the workflow requires review first.

## Output expectations

After this skill runs, the current task has a PR that another reviewer can understand and evaluate.
