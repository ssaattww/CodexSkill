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
- For large PR context, the parent may request a draft summary and evidence collection pass from a `sub-agent`, but the actual PR creation remains parent work.

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

## Large-scope delegation

If PR context is large enough that assembling summary, validation evidence, and report references would be noisy, the parent may:

1. use `sub-agent-task-manager`
2. ask a `sub-agent` for a bounded PR-draft preparation pass
3. require a report under `reports/`
4. create or update the actual PR in the parent

Use these provisional thresholds as the default trigger:

- report references to collect are 3 or more
- distinct validation commands or evidence items to summarize are 3 or more
- changed-file groups that need separate summary bullets are 4 or more
- the PR body would likely need 4 or more top-level bullets or sections to stay readable
