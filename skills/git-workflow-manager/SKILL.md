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
- verification capability and the separate commit, push, and CI-wait states

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
- Default to `1 task -> 1 implementation commit`.
- Allow multiple implementation commits only when the task clearly contains independently reviewable sub-units or when the user explicitly wants a split history. Lifecycle commits with purpose `review_target`, `normal_report`, or the one allowed `report_attestation` are explicit exceptions and do not change task scope.
- Treat commit-count policy as owned here; `git-commit-manager` should follow this skill's decision instead of inventing a separate default.
- Keep commits understandable and scoped.
- Require a committed review target before review, but do not make each normal
  review or finding-closure commit an automatic push.
- For `local_execution_available`, allow converged local review commits to be
  pushed together only after validation relevant to the pushed changes; require
  the repository-defined full local gate before final push.
- Keep CI waiting separate from publication. After attestation, wait once only
  for exact-head required `pull_request` CI unless repository policy explicitly
  requires a `push` run. For `remote_ci_only`, matching current-HEAD CI after
  authorized push is formal verification evidence.
- Make PRs carry enough evidence to review and merge safely.
- Do not open or update a PR without linking the relevant issue in the PR body.
- If the current commit closes or hands off a skill/process improvement loop that came from `feedback-points`, make sure the corresponding issue has been created or confirmed through `feedback-points-manager` before treating the loop as handed off.
- At commit timing, expect active `feedback-points.md` to be empty again; do not leave commit-ready skill/process follow-up in the active FP ledger.

## Outputs

After this skill runs, the current task should have:

- the right branch context
- a commit plan that is coherent for the current task, defaulting to one commit
- a reviewable PR or an explicit reason why submission cannot proceed yet

## Completion condition

This skill is done for the current task only when the relevant branch, commit, and PR actions are complete, the commit shape for the task has been decided, and commit-ready feedback-point follow-up has been cleared from the active FP ledger.

## Cross-cutting rule

If repeated Git mistakes or submission friction appear, call `feedback-points-manager`.
