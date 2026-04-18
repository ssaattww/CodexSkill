---
name: git-workflow-manager
description: Standardize branch, commit, and pull-request workflow for development tasks. Use when starting task-based work on a branch, preparing commits, creating PRs, addressing review comments, or ensuring that a task reaches a submit-ready state rather than stopping at local implementation.
---

# Git Workflow Manager

Drive work through branch, commit, and PR completion.

## Goal

Ensure every implementation task reaches a clean Git submission state.

## Execution owner

Run this skill as: `parent`

- This skill coordinates branch, commit, and PR lifecycle across child skills.

## Workflow stages

Use these sub-skills as needed:

- `git-branch-starter`
- `git-commit-manager`
- `git-pr-submitter`
- `git-review-followup-manager`

## Strong rules

- Do not treat local implementation as the endpoint.
- Prefer branch-based work.
- Prefer PR-based submission.
- Keep commits understandable and scoped.
- Make PRs carry enough evidence to review and merge safely.

## Required completion condition

This skill is done for the current task only when the relevant branch, commit, and PR actions are complete.

## Cross-cutting rule

If repeated Git mistakes or submission friction appear, call `feedback-points-manager`.
