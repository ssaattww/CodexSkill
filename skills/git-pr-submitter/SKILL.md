---
name: git-pr-submitter
description: Create a pull request that packages the current task with sufficient context, validation evidence, and report references. Use when writing an Issue body or preparing a pull request for integration after the required verification and review.
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
- linked issue identifier(s) for the task or an explicit reason why no issue exists
- review evidence and validation evidence
- report references needed in the PR body

## Body templates

- Use the [Issue body template](references/issue-body-template.md) when drafting or editing an Issue. Start with the intended outcome, then state the problem, scope, and observable completion conditions. Keep a suspected cause separate from a confirmed one.
- Use the [PR body template](references/pull-request-body-template.md) when drafting or editing a PR. Put the review decision and its effect first; distinguish changes, scope exclusions, verified evidence, and remaining work. Link directly to the relevant file lines, review, or CI result.
- Use a short example, a table, or a diagram when it explains a rule better than a long paragraph. Do not copy placeholder instructions or invent evidence. Formatting an Issue or PR does not grant permission to publish it or change its state.

## Required PR contents

Include as relevant:

- task or issue scope
- explicit linked issue reference in the PR body
- summary of changes
- test or validation evidence
- report references
- notable risks or follow-ups

## Rules

- Keep PR scope aligned with the task.
- Always link the relevant issue in the PR body. Prefer closing keywords such as `Closes #123` when the PR resolves that issue; otherwise add an explicit non-closing reference.
- Do not hide unresolved findings.
- Do not create a PR with missing review evidence when the workflow requires review first.
- If no issue exists yet for a process/skill loop that must be handed off, create or confirm that issue before opening the PR.

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
