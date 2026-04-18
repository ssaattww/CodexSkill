---
name: review-enforcer
description: Require a dedicated review step for every task before the task is treated as complete. Use when implementation appears done, before final progress updates, before commit/PR closure, or whenever a review result must be captured and addressed task by task.
---

# Review Enforcer

Prevent completion without review.

## Goal

Make task completion impossible until review has run and its outcome is recorded.

## Execution owner

Run this skill as: `parent`

- Parent owns completion gating and finding disposition.
- The actual review work inside this skill remains mandatory sub-agent work.

## Inputs

Before running this skill, gather:

- task-scoped diff or changed-file set
- relevant validation context and reports
- current task identifier and review scope

## Required flow

1. Prepare a task-scoped diff.
2. Run review for that task only as a `sub-agent` task through `sub-agent-task-manager`.
3. Instruct the review `sub-agent` to use the built-in review behavior: findings first, severity-ordered, with file/line references when available.
4. Materialize the built-in review result into the pre-created report file under `reports/`.
5. If the review `sub-agent` does not write the report file directly, have the parent write it immediately from the returned review findings.
6. Address findings if any.
7. Re-run review if required.
8. Only then allow progress sync and Git submission.

When creating a new review report file, call `report-output-manager`.

## Rules

- Review one task at a time.
- Do not batch multiple unrelated tasks into one review.
- Do not mark a task complete without recorded review evidence.
- Distinguish between “no findings” and “review not run”.
- Review is mandatory sub-agent work.
- Reviewer assignment is never switchable to the parent.
- Review requests should explicitly ask for a code review, not a generic diff summary.
- Built-in review output alone is not sufficient; it must also exist in the report file.

## Required report contents

Include:

- task identifier
- scope reviewed
- reviewer or sub-agent used
- findings summary
- file/line references for findings when available
- explicit `no findings` statement when applicable
- disposition of findings
- final outcome

## Outputs

After this skill runs, there should be:

- a review report in `reports/`
- explicit findings or explicit `no findings`
- a clear disposition for whether follow-up work is required

## Completion condition

This skill is complete only when:

- review has run for the current task
- findings are materialized in the report file
- required follow-up has been addressed or explicitly left open

## Cross-cutting rule

If a repeated review-related instruction appears, call `feedback-points-manager`.
