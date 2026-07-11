---
name: git-pr-submitter
description: Create a pull request that packages the current task with sufficient context, validation evidence, routine evidence, skill/tool decisions, and report references. Use when a task has passed implementation, verification, review, reflection, feedback disposition, progress synchronization, and commit stages and is ready to be submitted for integration.
---

# Git PR Submitter

Turn task work into a reviewable PR.

## Goal

Submit each completed task as a PR with enough context and evidence for efficient review.

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
- active task-routine evidence for completed or skipped steps
- skill reflection decision, target, and evidence
- tool reflection decision, target, and evidence
- report references needed in the PR body

## Required PR contents

Every PR body must contain the following exact headings with non-placeholder evidence:

```markdown
## Task routine evidence

## Skill action

## Tool action
```

Record the following under those headings:

- `Task routine evidence`: verification, review, feedback disposition, progress synchronization, and Git submission readiness
- `Skill action`: `none`, `update-existing`, or `propose-new`, including the reason and target when applicable
- `Tool action`: `none`, `update-existing`, `create-internal`, or `propose-external`, including the reason and target when applicable

Also include as relevant:

- task or issue scope
- explicit linked issue reference in the PR body
- summary of changes
- test or validation evidence
- report references
- notable risks or follow-ups

## Rules

- Keep PR scope aligned with the task.
- Always link the relevant issue in the PR body. Prefer closing keywords such as `Closes #123` when the PR resolves that issue; otherwise add an explicit non-closing reference.
- Do not use empty headings, `TODO`, `TBD`, `none` without rationale, `N/A`, `未記入`, or equivalent placeholders as evidence.
- Do not hide unresolved findings.
- Do not create a PR with missing review evidence when the workflow requires review first.
- Do not create a PR until the task routine has evidence for both reflections, feedback disposition, and progress synchronization.
- If no issue exists yet for a process/skill/tool loop that must be handed off, create or confirm that issue before opening the PR.
- When the task-routine `PreToolUse` hook is active, treat a missing required PR-body section as a blocking gate rather than adding it after PR creation.

## Outputs

After this skill runs, the current task has a PR that another reviewer can understand and evaluate, including explicit task-routine, skill-action, and tool-action evidence.

## Completion condition

This skill is complete only when a reviewable PR exists with the necessary context, validation and review evidence, exact required routine headings, and linked tracking records.

## Large-scope delegation

If PR context is large enough that assembling summary, validation evidence, routine evidence, and report references would be noisy, the parent may:

1. use `sub-agent-task-manager`
2. ask a `sub-agent` for a bounded PR-draft preparation pass
3. require a report under `reports/`
4. create or update the actual PR in the parent

Use these provisional thresholds as the default trigger:

- report references to collect are 3 or more
- distinct validation commands or evidence items to summarize are 3 or more
- changed-file groups that need separate summary bullets are 4 or more
- the PR body would likely need 4 or more top-level bullets or sections to stay readable
