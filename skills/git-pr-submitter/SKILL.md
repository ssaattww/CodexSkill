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

## Inputs

Before running this skill, gather:

- task or issue scope
- relevant commits and branch
- review evidence and validation evidence
- report references needed in the PR body

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

## Outputs

After this skill runs, the current task has a PR that another reviewer can understand and evaluate.

## Completion condition

This skill is complete only when a reviewable PR exists with the necessary context and evidence.
