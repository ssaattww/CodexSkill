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

## Inputs

Before running this skill, gather:

- current task completion state
- branch context
- commit readiness
- PR readiness including review and validation evidence

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
- Default to `1 task -> 1 commit`.
- Allow multiple commits for one task only when the task clearly contains independently reviewable sub-units or when the user explicitly wants a split history.
- Treat commit-count policy as owned here; `git-commit-manager` should follow this skill's decision instead of inventing a separate default.
- Keep commits understandable and scoped.
- Make PRs carry enough evidence to review and merge safely.

## Outputs

After this skill runs, the current task should have:

- the right branch context
- a commit plan that is coherent for the current task, defaulting to one commit
- a reviewable PR or an explicit reason why submission cannot proceed yet

## Completion condition

This skill is done for the current task only when the relevant branch, commit, and PR actions are complete and the commit shape for the task has been decided.

## Cross-cutting rule

If repeated Git mistakes or submission friction appear, call `feedback-points-manager`.
