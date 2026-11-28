---
name: git-pr-submitter
description: Draft or revise an Issue or PR body, or submit a pull request after the required verification and review. Use when preparing review context, validation evidence, and related links for an Issue or PR.
---

# Git PR Submitter

Turn task work into a reviewable PR.

## Goal

Write a concise Issue or PR body, or submit a completed task as a reviewable PR. Select the mode from the request:

- **Body only:** Draft or revise the Issue or PR text using the matching template. Gather the scope and known facts; a branch, commit, or review result is not required. Finish when the requested text is ready, or when an explicitly requested and authorized body edit has been verified. Missing evidence stays unconfirmed.
- **PR submission:** Use the PR creation steps below only when the request and existing permissions cover submission. Keep the required implementation, verification, review, commit, and branch prerequisites.

Creating or publishing an Issue or PR, editing its published body, or changing its state requires permission for that operation. A request to draft or format text does not authorize any of those operations.

## Execution owner

Run this skill as: `parent`

- PR creation publishes the parent-owned outcome and should stay with the parent.
- For large PR context, the parent may request a draft summary and evidence collection pass from a `sub-agent`, but the actual PR creation remains parent work.

## PR submission inputs

Before submitting a PR, gather:

- task or issue scope
- relevant commits and branch
- linked issue identifier(s) for the task or an explicit reason why no issue exists
- review evidence and validation evidence
- report references needed in the PR body

## Body templates

- Use the [Issue body template](references/issue-body-template.md) when drafting or editing an Issue. Start with the intended outcome, then state the problem, scope, and observable completion conditions. Keep a suspected cause separate from a confirmed one.
- Use the [PR body template](references/pull-request-body-template.md) when drafting or editing a PR. Put the review decision and its effect first; distinguish changes, scope exclusions, verified evidence, and remaining work. Link directly to the relevant file lines, review, or CI result.
- Use a short example, a table, or a diagram when it explains a rule better than a long paragraph. Do not copy placeholder instructions or invent evidence.

## Required PR contents

Include as relevant:

- task or issue scope
- explicit linked issue reference in the PR body
- summary of changes
- test or validation evidence
- report references
- notable risks or follow-ups

## PR submission rules

- Keep PR scope aligned with the task.
- Always link the relevant issue in the PR body. Prefer closing keywords such as `Closes #123` when the PR resolves that issue; otherwise add an explicit non-closing reference.
- Do not hide unresolved findings.
- Do not create a PR with missing review evidence when the workflow requires review first.
- If no issue exists yet for a process/skill loop that must be handed off, create or confirm that issue before opening the PR.

## PR submission completion condition

A reviewable PR exists with the necessary context and evidence.

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
